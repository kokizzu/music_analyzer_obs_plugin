#include "analyzer.hpp"

#include <obs-module.h>
#include <obs-source.h>
#include <obs.h>
#include <media-io/audio-io.h>

#include <algorithm>
#include <atomic>
#include <array>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

OBS_DECLARE_MODULE()

namespace {

constexpr const char *kFilterId = "music_analyzer_filter";
constexpr const char *kVisualizerId = "music_analyzer_overlay";
constexpr uint32_t kDefaultWidth = 960;
constexpr uint32_t kDefaultHeight = 360;
static_assert((mao::kAnalysisWindow & (mao::kAnalysisWindow - 1)) == 0, "analysis window must be a power of two");

std::mutex g_snapshot_mutex;
mao::AnalysisSnapshot g_snapshot;
uint64_t g_snapshot_sequence = 0;

void copy_text(char *dst, std::size_t dst_size, const char *src)
{
	if (!dst || dst_size == 0)
		return;
	std::snprintf(dst, dst_size, "%s", src ? src : "");
}

void publish_snapshot(mao::AnalysisSnapshot snapshot)
{
	std::lock_guard<std::mutex> lock(g_snapshot_mutex);
	snapshot.sequence = ++g_snapshot_sequence;
	g_snapshot = snapshot;
}

mao::AnalysisSnapshot read_snapshot()
{
	std::lock_guard<std::mutex> lock(g_snapshot_mutex);
	return g_snapshot;
}

struct FilterData {
	obs_source_t *source = nullptr;
	std::array<float, mao::kAnalysisWindow> ring = {};
	std::array<float, mao::kAnalysisWindow> pending_window = {};
	std::size_t write_pos = 0;
	std::atomic<uint32_t> sample_rate{48000};
	std::atomic<uint32_t> channels{2};
	std::atomic<uint32_t> hop_samples{2400};
	std::atomic<uint32_t> sensitivity_percent{100};
	std::atomic<bool> parent_name_resolved{false};
	std::atomic<uint64_t> direct_audio_frames_seen{0};
	uint32_t samples_until_analysis = 2400;
	char source_name[64] = {};
	char pending_source_name[64] = {};
	uint64_t dropped_windows = 0;
	uint64_t audio_frames_seen = 0;
	uint64_t analyzed_windows = 0;
	uint64_t pending_audio_frames = 0;
	uint64_t pending_analyzed_windows = 0;
	uint64_t master_last_direct_frames = 0;
	uint32_t master_callbacks_since_direct = 0;
	audio_t *master_audio = nullptr;
	bool master_audio_connected = false;

	std::mutex audio_mutex;
	std::mutex worker_mutex;
	std::condition_variable worker_cv;
	std::thread worker;
	bool stop_worker = false;
	bool pending = false;
	mao::AnalysisSettings pending_settings;
	mao::AnalysisEngine engine;
};

void master_audio_callback(void *param, size_t, struct audio_data *audio);

void copy_ring_to_pending(FilterData *filter, const char *source_label)
{
	std::unique_lock<std::mutex> lock(filter->worker_mutex);
	if (filter->pending) {
		++filter->dropped_windows;
		return;
	}

	for (std::size_t i = 0; i < mao::kAnalysisWindow; ++i) {
		const std::size_t idx = (filter->write_pos + i) & (mao::kAnalysisWindow - 1);
		filter->pending_window[i] = filter->ring[idx];
	}
	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const uint32_t hop_samples = std::max<uint32_t>(1, filter->hop_samples.load(std::memory_order_relaxed));
	filter->pending_settings.sample_rate = sample_rate;
	filter->pending_settings.sensitivity =
		static_cast<float>(filter->sensitivity_percent.load(std::memory_order_relaxed)) / 100.0f;
	filter->pending_settings.analysis_interval_seconds =
		static_cast<float>(hop_samples) / static_cast<float>(std::max<uint32_t>(1, sample_rate));
	copy_text(filter->pending_source_name, sizeof(filter->pending_source_name),
		  source_label && *source_label ? source_label : filter->source_name);
	filter->pending_audio_frames = filter->audio_frames_seen;
	filter->pending_analyzed_windows = ++filter->analyzed_windows;
	filter->pending = true;
	lock.unlock();
	filter->worker_cv.notify_one();
}

bool refresh_source_name(FilterData *filter)
{
	obs_source_t *parent = obs_filter_get_parent(filter->source);
	const char *name = parent ? obs_source_get_name(parent) : obs_source_get_name(filter->source);
	std::lock_guard<std::mutex> lock(filter->worker_mutex);
	copy_text(filter->source_name, sizeof(filter->source_name), name);
	return parent != nullptr;
}

void publish_filter_ready(FilterData *filter)
{
	mao::AnalysisSettings settings;
	mao::AnalysisEngine status_engine;
	char source_name[64] = {};
	uint64_t dropped_windows = 0;

	settings.sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	settings.sensitivity = static_cast<float>(filter->sensitivity_percent.load(std::memory_order_relaxed)) / 100.0f;
	settings.analysis_interval_seconds =
		static_cast<float>(std::max<uint32_t>(1, filter->hop_samples.load(std::memory_order_relaxed))) /
		static_cast<float>(std::max<uint32_t>(1, settings.sample_rate));

	{
		std::lock_guard<std::mutex> lock(filter->worker_mutex);
		copy_text(source_name, sizeof(source_name), filter->source_name);
		dropped_windows = filter->dropped_windows;
	}

	auto snapshot = status_engine.analyze(nullptr, 0, settings, source_name, dropped_windows);
	snapshot.audio_seen = false;
	publish_snapshot(snapshot);
}

void connect_master_audio(FilterData *filter)
{
	audio_t *audio = obs_get_audio();
	if (!audio)
		return;

	audio_convert_info conversion = {};
	conversion.samples_per_sec = filter->sample_rate.load(std::memory_order_relaxed);
	conversion.format = AUDIO_FORMAT_FLOAT_PLANAR;
	conversion.speakers = SPEAKERS_STEREO;
	conversion.allow_clipping = false;

	filter->master_audio_connected = audio_output_connect(audio, 0, &conversion, master_audio_callback, filter);
	if (filter->master_audio_connected)
		filter->master_audio = audio;
}

void disconnect_master_audio(FilterData *filter)
{
	if (!filter->master_audio_connected || !filter->master_audio)
		return;

	audio_output_disconnect(filter->master_audio, 0, master_audio_callback, filter);
	filter->master_audio_connected = false;
	filter->master_audio = nullptr;
}

void process_audio_planes(FilterData *filter, const float *const *planes, uint32_t channels, uint32_t frames,
			  const char *source_label)
{
	if (!planes || channels == 0 || frames == 0)
		return;

	std::lock_guard<std::mutex> audio_lock(filter->audio_mutex);

	for (uint32_t frame = 0; frame < frames; ++frame) {
		float mixed = 0.0f;
		uint32_t valid_planes = 0;

		for (uint32_t ch = 0; ch < channels; ++ch) {
			if (!planes[ch])
				continue;
			mixed += planes[ch][frame];
			++valid_planes;
		}

		if (valid_planes == 0)
			continue;

		mixed /= static_cast<float>(valid_planes);
		filter->ring[filter->write_pos] = std::clamp(mixed, -2.0f, 2.0f);
		filter->write_pos = (filter->write_pos + 1) & (mao::kAnalysisWindow - 1);
		++filter->audio_frames_seen;

		if (--filter->samples_until_analysis == 0) {
			filter->samples_until_analysis =
				std::max<uint32_t>(1, filter->hop_samples.load(std::memory_order_relaxed));
			copy_ring_to_pending(filter, source_label);
		}
	}
}

void master_audio_callback(void *param, size_t, struct audio_data *audio)
{
	auto *filter = static_cast<FilterData *>(param);
	if (!filter || !audio)
		return;

	const uint64_t direct_frames = filter->direct_audio_frames_seen.load(std::memory_order_relaxed);
	if (direct_frames != filter->master_last_direct_frames) {
		filter->master_last_direct_frames = direct_frames;
		filter->master_callbacks_since_direct = 0;
		return;
	}
	if (direct_frames > 0 && filter->master_callbacks_since_direct++ < 30)
		return;

	std::array<const float *, 2> planes = {
		reinterpret_cast<const float *>(audio->data[0]),
		reinterpret_cast<const float *>(audio->data[1]),
	};
	process_audio_planes(filter, planes.data(), static_cast<uint32_t>(planes.size()), audio->frames, "OBS MIX");
}

void analyzer_worker(FilterData *filter)
{
	std::array<float, mao::kAnalysisWindow> local_window = {};

	for (;;) {
		mao::AnalysisSettings settings;
		char source_name[64] = {};
		uint64_t dropped = 0;
		uint64_t audio_frames = 0;
		uint64_t analyzed_windows = 0;

		{
			std::unique_lock<std::mutex> lock(filter->worker_mutex);
			filter->worker_cv.wait(lock, [&]() { return filter->stop_worker || filter->pending; });
			if (filter->stop_worker)
				return;

			local_window = filter->pending_window;
			settings = filter->pending_settings;
			copy_text(source_name, sizeof(source_name), filter->pending_source_name);
			dropped = filter->dropped_windows;
			audio_frames = filter->pending_audio_frames;
			analyzed_windows = filter->pending_analyzed_windows;
			filter->pending = false;
		}

		auto snapshot = filter->engine.analyze(local_window.data(), local_window.size(), settings, source_name, dropped);
		snapshot.audio_seen = true;
		snapshot.audio_frames = audio_frames;
		snapshot.analyzed_windows = analyzed_windows;
		publish_snapshot(snapshot);
	}
}

void refresh_audio_config(FilterData *filter)
{
	obs_audio_info info = {};
	if (obs_get_audio_info(&info)) {
		filter->sample_rate = info.samples_per_sec ? info.samples_per_sec : 48000;
		const uint32_t channels = get_audio_channels(info.speakers);
		filter->channels.store(channels ? channels : 2, std::memory_order_relaxed);
	}
}

void *filter_create(obs_data_t *settings, obs_source_t *source)
{
	auto *filter = new FilterData();
	filter->source = source;
	filter->parent_name_resolved.store(refresh_source_name(filter), std::memory_order_relaxed);
	refresh_audio_config(filter);

	const long long update_ms = obs_data_get_int(settings, "update_ms");
	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const uint32_t hop =
		std::max<uint32_t>(1, sample_rate * static_cast<uint32_t>(std::max<long long>(20, update_ms)) / 1000);
	filter->hop_samples.store(hop, std::memory_order_relaxed);
	filter->samples_until_analysis = hop;
	filter->sensitivity_percent.store(static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "sensitivity"), 50, 200)),
					  std::memory_order_relaxed);

	publish_filter_ready(filter);
	connect_master_audio(filter);
	filter->worker = std::thread(analyzer_worker, filter);
	return filter;
}

void filter_destroy(void *data)
{
	auto *filter = static_cast<FilterData *>(data);
	if (!filter)
		return;

	disconnect_master_audio(filter);

	{
		std::lock_guard<std::mutex> lock(filter->worker_mutex);
		filter->stop_worker = true;
	}
	filter->worker_cv.notify_one();
	if (filter->worker.joinable())
		filter->worker.join();

	delete filter;
}

void filter_defaults(obs_data_t *settings)
{
	obs_data_set_default_int(settings, "update_ms", 50);
	obs_data_set_default_int(settings, "sensitivity", 100);
}

obs_properties_t *filter_properties(void *)
{
	obs_properties_t *props = obs_properties_create();
	obs_properties_add_int_slider(props, "update_ms", "Analyzer interval (ms)", 20, 250, 5);
	obs_properties_add_int_slider(props, "sensitivity", "Drum sensitivity (%)", 50, 200, 5);
	return props;
}

void filter_update(void *data, obs_data_t *settings)
{
	auto *filter = static_cast<FilterData *>(data);
	if (!filter)
		return;

	refresh_audio_config(filter);
	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const long long update_ms = std::clamp<long long>(obs_data_get_int(settings, "update_ms"), 20, 250);
	filter->hop_samples.store(std::max<uint32_t>(1, sample_rate * static_cast<uint32_t>(update_ms) / 1000),
				  std::memory_order_relaxed);
	filter->sensitivity_percent.store(static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "sensitivity"), 50, 200)),
					  std::memory_order_relaxed);
	filter->parent_name_resolved.store(refresh_source_name(filter), std::memory_order_relaxed);
	publish_filter_ready(filter);
}

obs_audio_data *filter_audio(void *data, obs_audio_data *audio)
{
	auto *filter = static_cast<FilterData *>(data);
	if (!filter || !audio || audio->frames == 0)
		return audio;

	if (!filter->parent_name_resolved.load(std::memory_order_relaxed))
		filter->parent_name_resolved.store(refresh_source_name(filter), std::memory_order_relaxed);

	const uint32_t channels =
		std::clamp<uint32_t>(filter->channels.load(std::memory_order_relaxed), 1, MAX_AUDIO_CHANNELS);
	std::array<const float *, MAX_AUDIO_CHANNELS> planes = {};
	uint32_t valid_planes = 0;
	for (uint32_t ch = 0; ch < channels; ++ch) {
		planes[ch] = reinterpret_cast<const float *>(audio->data[ch]);
		if (planes[ch])
			++valid_planes;
	}

	if (valid_planes == 0)
		return audio;

	filter->direct_audio_frames_seen.fetch_add(audio->frames, std::memory_order_relaxed);
	process_audio_planes(filter, planes.data(), channels, audio->frames, nullptr);

	return audio;
}

const char *filter_name(void *)
{
	return "Music Analyzer Filter";
}

struct Color {
	uint8_t r = 255;
	uint8_t g = 255;
	uint8_t b = 255;
	uint8_t a = 255;
};

struct DrumBar {
	float age = 0.0f;
	float level = 0.0f;
};

struct VisualizerData {
	mutable std::mutex mutex;
	uint32_t width = kDefaultWidth;
	uint32_t height = kDefaultHeight;
	uint32_t update_fps = 10;
	float elapsed = 1.0f;
	float snapshot_age = 0.0f;
	uint64_t rendered_sequence = 0;
	bool dirty = true;
	bool texture_size_dirty = true;
	uint64_t drum_history_sequence = 0;
	std::array<std::vector<DrumBar>, mao::kDrumCount> drum_history = {};
	std::vector<uint8_t> pixels;
	gs_texture_t *texture = nullptr;
};

const std::array<const char *, 7> glyph_rows(char c)
{
	switch (c) {
	case 'a':
		return {"00000", "00000", "01110", "00001", "01111", "10001", "01111"};
	case 'j':
		return {"00010", "00000", "00110", "00010", "00010", "10010", "01100"};
	case 'm':
		return {"00000", "00000", "11010", "10101", "10101", "10101", "10101"};
	case 's':
		return {"00000", "00000", "01111", "10000", "01110", "00001", "11110"};
	case 'u':
		return {"00000", "00000", "10001", "10001", "10001", "10011", "01101"};
	case 'A':
		return {"01110", "10001", "10001", "11111", "10001", "10001", "10001"};
	case 'B':
		return {"11110", "10001", "10001", "11110", "10001", "10001", "11110"};
	case 'C':
		return {"01111", "10000", "10000", "10000", "10000", "10000", "01111"};
	case 'D':
		return {"11110", "10001", "10001", "10001", "10001", "10001", "11110"};
	case 'E':
		return {"11111", "10000", "10000", "11110", "10000", "10000", "11111"};
	case 'F':
		return {"11111", "10000", "10000", "11110", "10000", "10000", "10000"};
	case 'G':
		return {"01111", "10000", "10000", "10011", "10001", "10001", "01111"};
	case 'H':
		return {"10001", "10001", "10001", "11111", "10001", "10001", "10001"};
	case 'I':
		return {"11111", "00100", "00100", "00100", "00100", "00100", "11111"};
	case 'J':
		return {"00111", "00010", "00010", "00010", "00010", "10010", "01100"};
	case 'K':
		return {"10001", "10010", "10100", "11000", "10100", "10010", "10001"};
	case 'L':
		return {"10000", "10000", "10000", "10000", "10000", "10000", "11111"};
	case 'M':
		return {"10001", "11011", "10101", "10101", "10001", "10001", "10001"};
	case 'N':
		return {"10001", "11001", "10101", "10011", "10001", "10001", "10001"};
	case 'O':
		return {"01110", "10001", "10001", "10001", "10001", "10001", "01110"};
	case 'P':
		return {"11110", "10001", "10001", "11110", "10000", "10000", "10000"};
	case 'Q':
		return {"01110", "10001", "10001", "10001", "10101", "10010", "01101"};
	case 'R':
		return {"11110", "10001", "10001", "11110", "10100", "10010", "10001"};
	case 'S':
		return {"01111", "10000", "10000", "01110", "00001", "00001", "11110"};
	case 'T':
		return {"11111", "00100", "00100", "00100", "00100", "00100", "00100"};
	case 'U':
		return {"10001", "10001", "10001", "10001", "10001", "10001", "01110"};
	case 'V':
		return {"10001", "10001", "10001", "10001", "10001", "01010", "00100"};
	case 'W':
		return {"10001", "10001", "10001", "10101", "10101", "10101", "01010"};
	case 'X':
		return {"10001", "10001", "01010", "00100", "01010", "10001", "10001"};
	case 'Y':
		return {"10001", "10001", "01010", "00100", "00100", "00100", "00100"};
	case 'Z':
		return {"11111", "00001", "00010", "00100", "01000", "10000", "11111"};
	case '0':
		return {"01110", "10001", "10011", "10101", "11001", "10001", "01110"};
	case '1':
		return {"00100", "01100", "00100", "00100", "00100", "00100", "01110"};
	case '2':
		return {"01110", "10001", "00001", "00010", "00100", "01000", "11111"};
	case '3':
		return {"11110", "00001", "00001", "01110", "00001", "00001", "11110"};
	case '4':
		return {"00010", "00110", "01010", "10010", "11111", "00010", "00010"};
	case '5':
		return {"11111", "10000", "10000", "11110", "00001", "00001", "11110"};
	case '6':
		return {"01111", "10000", "10000", "11110", "10001", "10001", "01110"};
	case '7':
		return {"11111", "00001", "00010", "00100", "01000", "01000", "01000"};
	case '8':
		return {"01110", "10001", "10001", "01110", "10001", "10001", "01110"};
	case '9':
		return {"01110", "10001", "10001", "01111", "00001", "00001", "11110"};
	case '#':
		return {"01010", "01010", "11111", "01010", "11111", "01010", "01010"};
	case '-':
		return {"00000", "00000", "00000", "11111", "00000", "00000", "00000"};
	case '.':
		return {"00000", "00000", "00000", "00000", "00000", "01100", "01100"};
	case ':':
		return {"00000", "01100", "01100", "00000", "01100", "01100", "00000"};
	case '%':
		return {"11001", "11010", "00100", "01000", "10110", "00110", "00000"};
	case '/':
		return {"00001", "00010", "00010", "00100", "01000", "01000", "10000"};
	case ' ':
		return {"00000", "00000", "00000", "00000", "00000", "00000", "00000"};
	default:
		return {"11111", "00001", "00010", "00100", "00100", "00000", "00100"};
	}
}

void put_pixel(VisualizerData *visualizer, int x, int y, Color color)
{
	if (x < 0 || y < 0 || x >= static_cast<int>(visualizer->width) || y >= static_cast<int>(visualizer->height))
		return;

	const std::size_t offset = (static_cast<std::size_t>(y) * visualizer->width + static_cast<std::size_t>(x)) * 4;
	visualizer->pixels[offset + 0] = color.r;
	visualizer->pixels[offset + 1] = color.g;
	visualizer->pixels[offset + 2] = color.b;
	visualizer->pixels[offset + 3] = color.a;
}

void fill_rect(VisualizerData *visualizer, int x, int y, int w, int h, Color color)
{
	const int x0 = std::max(0, x);
	const int y0 = std::max(0, y);
	const int x1 = std::min(static_cast<int>(visualizer->width), x + w);
	const int y1 = std::min(static_cast<int>(visualizer->height), y + h);

	for (int yy = y0; yy < y1; ++yy) {
		for (int xx = x0; xx < x1; ++xx)
			put_pixel(visualizer, xx, yy, color);
	}
}

void draw_text_impl(VisualizerData *visualizer, int x, int y, const char *text, uint32_t scale, Color color,
		    bool preserve_chord_lowercase)
{
	if (!text)
		return;

	int cursor = x;
	for (const char *p = text; *p; ++p) {
		char c = *p;
		const bool chord_lowercase = c == 'a' || c == 'j' || c == 'm' || c == 's' || c == 'u';
		if (c >= 'a' && c <= 'z' && (!preserve_chord_lowercase || !chord_lowercase))
			c = static_cast<char>(c - 'a' + 'A');

		const auto rows = glyph_rows(c);
		for (int row = 0; row < 7; ++row) {
			for (int col = 0; col < 5; ++col) {
				if (rows[row][col] != '1')
					continue;
				fill_rect(visualizer, cursor + col * static_cast<int>(scale),
					  y + row * static_cast<int>(scale), static_cast<int>(scale),
					  static_cast<int>(scale), color);
			}
		}
		cursor += static_cast<int>(scale) * 6;
	}
}

void draw_text(VisualizerData *visualizer, int x, int y, const char *text, uint32_t scale, Color color)
{
	draw_text_impl(visualizer, x, y, text, scale, color, false);
}

void draw_chord_text(VisualizerData *visualizer, int x, int y, const char *text, uint32_t scale, Color color)
{
	draw_text_impl(visualizer, x, y, text, scale, color, true);
}

void draw_drum_chart(VisualizerData *visualizer, int x, int y, int w, const mao::DrumState &drum,
		     const std::vector<DrumBar> &history)
{
	const int label_h = 18;
	const int chart_y = y + label_h + 4;
	const int chart_h = 28;
	const Color bg{24, 30, 38, 210};
	const Color active_bg{242, 149, 40, 235};
	const Color border{86, 96, 111, 230};
	const Color text{240, 244, 248, 255};
	const Color dark_text{24, 26, 30, 255};
	const bool active = drum.level > 0.30f;

	fill_rect(visualizer, x, y, w, label_h, active ? active_bg : bg);
	fill_rect(visualizer, x, y, w, 1, border);
	fill_rect(visualizer, x, y + label_h - 1, w, 1, border);
	draw_text(visualizer, x + 5, y + 3, drum.label, 2, active ? dark_text : text);

	fill_rect(visualizer, x, chart_y, w, chart_h, bg);
	fill_rect(visualizer, x, chart_y, w, 1, border);
	fill_rect(visualizer, x, chart_y + chart_h - 1, w, 1, border);

	for (const DrumBar &bar : history) {
		if (bar.age < 0.0f || bar.age > 1.0f || bar.level <= 0.0f)
			continue;
		const int bar_x = x + std::clamp(static_cast<int>((1.0f - bar.age) * static_cast<float>(w - 4)), 0, w - 4);
		const int bar_h = std::clamp(static_cast<int>(bar.level * static_cast<float>(chart_h - 4)), 2, chart_h - 4);
		fill_rect(visualizer, bar_x, chart_y + chart_h - 2 - bar_h, 3, bar_h, active_bg);
	}
}

void draw_note_cell(VisualizerData *visualizer, int x, int y, int w, int h, const mao::NoteCell &cell, Color accent)
{
	const Color idle_bg{24, 30, 38, 210};
	const Color border{58, 68, 82, 220};
	const Color active_text{13, 17, 23, 255};
	const Color idle_text{91, 106, 124, 255};

	fill_rect(visualizer, x, y, w, h, cell.active ? accent : idle_bg);
	fill_rect(visualizer, x, y, w, 1, border);
	fill_rect(visualizer, x, y + h - 1, w, 1, border);
	fill_rect(visualizer, x, y, 1, h, border);
	fill_rect(visualizer, x + w - 1, y, 1, h, border);
	if (!cell.label[0])
		return;

	const int text_width = static_cast<int>(std::strlen(cell.label)) * 12;
	draw_text(visualizer, x + std::max(2, (w - text_width) / 2), y + 6, cell.label, 2,
		  cell.active ? active_text : idle_text);
}

void draw_instrument_row(VisualizerData *visualizer, int y, const char *name, const mao::NoteGrid &notes,
			 const mao::InstrumentState *chord, Color accent)
{
	const int label_x = 28;
	const int matrix_x = 150;
	const int cell_w = 40;
	const int cell_h = 26;
	const int chord_x = std::max(matrix_x + cell_w * 12 + 24, static_cast<int>(visualizer->width) - 190);
	const Color dim{130, 145, 163, 255};
	const Color chord_text{199, 210, 224, 255};
	const char *chord_label = chord && chord->label[0] ? chord->label : "--";

	draw_text(visualizer, label_x, y, name, 3, dim);
	for (int i = 0; i < 12; ++i)
		draw_note_cell(visualizer, matrix_x + i * cell_w, y, cell_w - 2, cell_h, notes.cells[i], accent);
	draw_chord_text(visualizer, chord_x, y + 2, chord_label, 3, chord_text);
}

void render_pixels(VisualizerData *visualizer, const mao::AnalysisSnapshot &snapshot, float snapshot_age)
{
	visualizer->pixels.assign(static_cast<std::size_t>(visualizer->width) * visualizer->height * 4, 0);

	fill_rect(visualizer, 0, 0, visualizer->width, visualizer->height, Color{12, 16, 22, 205});
	fill_rect(visualizer, 0, 0, visualizer->width, 8, Color{59, 130, 246, 240});

	char title[128];
	std::snprintf(title, sizeof(title), "MUSIC ANALYZER  %s", snapshot.source[0] ? snapshot.source : "WAITING");
	draw_text(visualizer, 28, 24, title, 3, Color{246, 248, 251, 255});

	char level[128];
	std::snprintf(level, sizeof(level), "RMS %.2f LOW %.0f%% MID %.0f%% HIGH %.0f%% UPD %llu DROP %llu",
		      snapshot.rms, snapshot.low_energy * 100.0f, snapshot.mid_energy * 100.0f,
		      snapshot.high_energy * 100.0f, static_cast<unsigned long long>(snapshot.analyzed_windows),
		      static_cast<unsigned long long>(snapshot.dropped_windows));
	draw_text(visualizer, 28, 58, level, 2, Color{148, 163, 184, 255});

	char debug[96];
	std::snprintf(debug, sizeof(debug), "FRAMES %llu AGE %.1FS",
		      static_cast<unsigned long long>(snapshot.audio_frames), snapshot_age);
	draw_text(visualizer, 28, 78, debug, 1, Color{148, 163, 184, 255});

	draw_text(visualizer, 28, 96, "DRUMS", 3, Color{148, 163, 184, 255});
	int tag_x = 150;
	for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
		draw_drum_chart(visualizer, tag_x, 88, 118, snapshot.drums[i], visualizer->drum_history[i]);
		tag_x += 126;
	}

	static constexpr const char *kNoteNames[12] = {"C", "C#", "D", "D#", "E", "F",
						       "F#", "G", "G#", "A", "A#", "B"};
	const int matrix_x = 150;
	const int cell_w = 40;
	const int chord_x = std::max(matrix_x + cell_w * 12 + 24, static_cast<int>(visualizer->width) - 190);
	for (int i = 0; i < 12; ++i)
		draw_text(visualizer, matrix_x + i * cell_w + 7, 150, kNoteNames[i], 2,
			  Color{148, 163, 184, 255});
	draw_text(visualizer, chord_x, 150, "CHORD", 2, Color{148, 163, 184, 255});
	draw_instrument_row(visualizer, 174, "BASS", snapshot.bass_notes, nullptr, Color{35, 197, 94, 245});
	draw_instrument_row(visualizer, 204, "GUITAR", snapshot.guitar_notes, &snapshot.guitar_chord,
			    Color{249, 115, 22, 245});
	draw_instrument_row(visualizer, 234, "KEYS", snapshot.keyboard_notes, &snapshot.keyboard_chord,
			    Color{56, 189, 248, 245});
	draw_instrument_row(visualizer, 264, "VOCAL", snapshot.vocal_notes, nullptr, Color{244, 114, 182, 245});
	draw_instrument_row(visualizer, 294, "OTHERS", snapshot.other_notes, &snapshot.other_chord,
			    Color{168, 85, 247, 245});

	char root_label[96];
	std::snprintf(root_label, sizeof(root_label), "ROOT %s",
		      snapshot.root_candidates[0] ? snapshot.root_candidates : "-- 0%");
	draw_text(visualizer, 28, std::max(132, static_cast<int>(visualizer->height) - 28), root_label, 3,
		  Color{199, 210, 224, 255});

	if (snapshot.sequence == 0)
		draw_text(visualizer, 230, 145, "ADD MUSIC ANALYZER FILTER TO AN AUDIO SOURCE", 2,
			  Color{248, 250, 252, 255});
	else if (!snapshot.audio_seen)
		draw_text(visualizer, 230, 145, "FILTER READY - WAITING FOR AUDIO", 2, Color{248, 250, 252, 255});
	else if (snapshot_age > 1.5f) {
		char stale[96];
		std::snprintf(stale, sizeof(stale), "STALE %.1FS - FILTER NOT RECEIVING AUDIO", snapshot_age);
		draw_text(visualizer, 230, 145, stale, 2, Color{248, 250, 252, 255});
	}
}

bool advance_drum_history(VisualizerData *visualizer, float seconds)
{
	bool has_history = false;
	for (auto &history : visualizer->drum_history) {
		for (DrumBar &bar : history)
			bar.age += seconds;
		history.erase(std::remove_if(history.begin(), history.end(),
					     [](const DrumBar &bar) { return bar.age > 1.0f; }),
			      history.end());
		has_history = has_history || !history.empty();
	}
	return has_history;
}

bool append_drum_hits(VisualizerData *visualizer, const mao::AnalysisSnapshot &snapshot)
{
	if (snapshot.sequence == 0 || snapshot.sequence == visualizer->drum_history_sequence)
		return false;

	visualizer->drum_history_sequence = snapshot.sequence;
	bool appended = false;
	for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
		const mao::DrumState &drum = snapshot.drums[i];
		if (drum.level <= 0.30f)
			continue;

		auto &history = visualizer->drum_history[i];
		history.push_back(DrumBar{0.0f, std::clamp(drum.level, 0.0f, 1.0f)});
		if (history.size() > 64)
			history.erase(history.begin());
		appended = true;
	}
	return appended;
}

void *visualizer_create(obs_data_t *settings, obs_source_t *)
{
	auto *visualizer = new VisualizerData();
	visualizer->width = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "width"), 320, 1920));
	visualizer->height = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "height"), 160, 1080));
	visualizer->update_fps = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "update_fps"), 1, 30));
	visualizer->pixels.resize(static_cast<std::size_t>(visualizer->width) * visualizer->height * 4);
	render_pixels(visualizer, read_snapshot(), 0.0f);
	return visualizer;
}

void visualizer_destroy(void *data)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return;

	{
		std::lock_guard<std::mutex> lock(visualizer->mutex);
		if (visualizer->texture) {
			obs_enter_graphics();
			gs_texture_destroy(visualizer->texture);
			obs_leave_graphics();
			visualizer->texture = nullptr;
		}
	}

	delete visualizer;
}

void visualizer_defaults(obs_data_t *settings)
{
	obs_data_set_default_int(settings, "width", kDefaultWidth);
	obs_data_set_default_int(settings, "height", kDefaultHeight);
	obs_data_set_default_int(settings, "update_fps", 10);
}

obs_properties_t *visualizer_properties(void *)
{
	obs_properties_t *props = obs_properties_create();
	obs_properties_add_int(props, "width", "Width", 320, 1920, 10);
	obs_properties_add_int(props, "height", "Height", 160, 1080, 10);
	obs_properties_add_int_slider(props, "update_fps", "Visualizer update FPS", 1, 30, 1);
	return props;
}

void visualizer_update(void *data, obs_data_t *settings)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	const uint32_t width = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "width"), 320, 1920));
	const uint32_t height = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "height"), 160, 1080));
	visualizer->update_fps = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "update_fps"), 1, 30));
	if (width != visualizer->width || height != visualizer->height) {
		visualizer->width = width;
		visualizer->height = height;
		visualizer->pixels.resize(static_cast<std::size_t>(width) * height * 4);
		visualizer->texture_size_dirty = true;
	}

	visualizer->dirty = true;
}

void visualizer_tick(void *data, float seconds)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	visualizer->elapsed += seconds;
	visualizer->snapshot_age += seconds;
	const float interval = 1.0f / static_cast<float>(std::max<uint32_t>(1, visualizer->update_fps));
	const bool interval_ready = visualizer->elapsed >= interval;
	const bool history_active = advance_drum_history(visualizer, seconds);
	const auto snapshot = read_snapshot();

	if (append_drum_hits(visualizer, snapshot))
		visualizer->dirty = true;
	if (history_active && interval_ready)
		visualizer->dirty = true;

	if (!interval_ready && !visualizer->dirty)
		return;
	if (interval_ready)
		visualizer->elapsed = 0.0f;

	if (snapshot.sequence != visualizer->rendered_sequence) {
		visualizer->snapshot_age = 0.0f;
		render_pixels(visualizer, snapshot, visualizer->snapshot_age);
		visualizer->rendered_sequence = snapshot.sequence;
		visualizer->dirty = true;
	} else if (visualizer->dirty || (snapshot.sequence > 0 && visualizer->snapshot_age > 1.5f)) {
		render_pixels(visualizer, snapshot, visualizer->snapshot_age);
		visualizer->rendered_sequence = snapshot.sequence;
		visualizer->dirty = true;
	}
}

void visualizer_render(void *data, gs_effect_t *)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	if (visualizer->texture_size_dirty && visualizer->texture) {
		gs_texture_destroy(visualizer->texture);
		visualizer->texture = nullptr;
	}

	if (!visualizer->texture) {
		const uint8_t *data_ptr = visualizer->pixels.data();
		visualizer->texture =
			gs_texture_create(visualizer->width, visualizer->height, GS_RGBA, 1, &data_ptr, GS_DYNAMIC);
		visualizer->texture_size_dirty = false;
		visualizer->dirty = false;
	} else if (visualizer->dirty) {
		gs_texture_set_image(visualizer->texture, visualizer->pixels.data(), visualizer->width * 4, false);
		visualizer->dirty = false;
	}

	if (visualizer->texture)
		obs_source_draw(visualizer->texture, 0, 0, visualizer->width, visualizer->height, false);
}

uint32_t visualizer_width(void *data)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return kDefaultWidth;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	return visualizer->width;
}

uint32_t visualizer_height(void *data)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return kDefaultHeight;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	return visualizer->height;
}

const char *visualizer_name(void *)
{
	return "Music Analyzer Overlay";
}

} // namespace

bool obs_module_load(void)
{
	obs_source_info filter = {};
	filter.id = kFilterId;
	filter.type = OBS_SOURCE_TYPE_FILTER;
	filter.output_flags = OBS_SOURCE_AUDIO;
	filter.get_name = filter_name;
	filter.create = filter_create;
	filter.destroy = filter_destroy;
	filter.get_defaults = filter_defaults;
	filter.get_properties = filter_properties;
	filter.update = filter_update;
	filter.filter_audio = filter_audio;
	obs_register_source(&filter);

	obs_source_info visualizer = {};
	visualizer.id = kVisualizerId;
	visualizer.type = OBS_SOURCE_TYPE_INPUT;
	visualizer.output_flags = OBS_SOURCE_VIDEO;
	visualizer.get_name = visualizer_name;
	visualizer.create = visualizer_create;
	visualizer.destroy = visualizer_destroy;
	visualizer.get_defaults = visualizer_defaults;
	visualizer.get_properties = visualizer_properties;
	visualizer.update = visualizer_update;
	visualizer.video_tick = visualizer_tick;
	visualizer.video_render = visualizer_render;
	visualizer.get_width = visualizer_width;
	visualizer.get_height = visualizer_height;
	obs_register_source(&visualizer);

	return true;
}
