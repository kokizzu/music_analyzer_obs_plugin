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
	uint32_t samples_until_analysis = 2400;
	char source_name[64] = {};
	uint64_t dropped_windows = 0;

	std::mutex worker_mutex;
	std::condition_variable worker_cv;
	std::thread worker;
	bool stop_worker = false;
	bool pending = false;
	mao::AnalysisSettings pending_settings;
	mao::AnalysisEngine engine;
};

void copy_ring_to_pending(FilterData *filter)
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
	filter->pending_settings.sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	filter->pending_settings.sensitivity =
		static_cast<float>(filter->sensitivity_percent.load(std::memory_order_relaxed)) / 100.0f;
	filter->pending = true;
	lock.unlock();
	filter->worker_cv.notify_one();
}

void refresh_source_name(FilterData *filter)
{
	obs_source_t *parent = obs_filter_get_parent(filter->source);
	const char *name = parent ? obs_source_get_name(parent) : obs_source_get_name(filter->source);
	std::lock_guard<std::mutex> lock(filter->worker_mutex);
	copy_text(filter->source_name, sizeof(filter->source_name), name);
}

void analyzer_worker(FilterData *filter)
{
	std::array<float, mao::kAnalysisWindow> local_window = {};

	for (;;) {
		mao::AnalysisSettings settings;
		char source_name[64] = {};
		uint64_t dropped = 0;

		{
			std::unique_lock<std::mutex> lock(filter->worker_mutex);
			filter->worker_cv.wait(lock, [&]() { return filter->stop_worker || filter->pending; });
			if (filter->stop_worker)
				return;

			local_window = filter->pending_window;
			settings = filter->pending_settings;
			copy_text(source_name, sizeof(source_name), filter->source_name);
			dropped = filter->dropped_windows;
			filter->pending = false;
		}

		auto snapshot = filter->engine.analyze(local_window.data(), local_window.size(), settings, source_name, dropped);
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
	refresh_source_name(filter);
	refresh_audio_config(filter);

	const long long update_ms = obs_data_get_int(settings, "update_ms");
	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const uint32_t hop =
		std::max<uint32_t>(1, sample_rate * static_cast<uint32_t>(std::max<long long>(20, update_ms)) / 1000);
	filter->hop_samples.store(hop, std::memory_order_relaxed);
	filter->samples_until_analysis = hop;
	filter->sensitivity_percent.store(static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "sensitivity"), 50, 200)),
					  std::memory_order_relaxed);

	filter->worker = std::thread(analyzer_worker, filter);
	return filter;
}

void filter_destroy(void *data)
{
	auto *filter = static_cast<FilterData *>(data);
	if (!filter)
		return;

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
	refresh_source_name(filter);
}

obs_audio_data *filter_audio(void *data, obs_audio_data *audio)
{
	auto *filter = static_cast<FilterData *>(data);
	if (!filter || !audio || audio->frames == 0)
		return audio;

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

	for (uint32_t frame = 0; frame < audio->frames; ++frame) {
		float mixed = 0.0f;
		for (uint32_t ch = 0; ch < channels; ++ch) {
			if (planes[ch])
				mixed += planes[ch][frame];
		}
		mixed /= static_cast<float>(valid_planes);

		filter->ring[filter->write_pos] = std::clamp(mixed, -2.0f, 2.0f);
		filter->write_pos = (filter->write_pos + 1) & (mao::kAnalysisWindow - 1);

		if (--filter->samples_until_analysis == 0) {
			filter->samples_until_analysis =
				std::max<uint32_t>(1, filter->hop_samples.load(std::memory_order_relaxed));
			copy_ring_to_pending(filter);
		}
	}

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

struct VisualizerData {
	mutable std::mutex mutex;
	uint32_t width = kDefaultWidth;
	uint32_t height = kDefaultHeight;
	uint32_t update_fps = 10;
	float elapsed = 1.0f;
	uint64_t rendered_sequence = 0;
	bool dirty = true;
	bool texture_size_dirty = true;
	std::vector<uint8_t> pixels;
	gs_texture_t *texture = nullptr;
};

const std::array<const char *, 7> glyph_rows(char c)
{
	switch (c) {
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

void draw_text(VisualizerData *visualizer, int x, int y, const char *text, uint32_t scale, Color color)
{
	if (!text)
		return;

	int cursor = x;
	for (const char *p = text; *p; ++p) {
		char c = *p;
		if (c >= 'a' && c <= 'z')
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

void draw_tag(VisualizerData *visualizer, int x, int y, int w, const char *label, float level)
{
	const Color idle_bg{34, 41, 50, 210};
	const Color active_bg{242, 149, 40, 235};
	const Color border{86, 96, 111, 230};
	const Color text{240, 244, 248, 255};
	const Color dark_text{24, 26, 30, 255};
	const bool active = level > 0.30f;

	fill_rect(visualizer, x, y, w, 30, active ? active_bg : idle_bg);
	fill_rect(visualizer, x, y, w, 2, border);
	fill_rect(visualizer, x, y + 28, w, 2, border);
	draw_text(visualizer, x + 8, y + 7, label, 2, active ? dark_text : text);

	if (active) {
		const int meter = std::clamp(static_cast<int>(level * static_cast<float>(w - 4)), 0, w - 4);
		fill_rect(visualizer, x + 2, y + 25, meter, 3, Color{255, 238, 167, 255});
	}
}

void draw_instrument_row(VisualizerData *visualizer, int y, const char *name, const mao::InstrumentState &state,
			 Color accent)
{
	const int label_x = 28;
	const int value_x = 230;
	const int meter_x = 520;
	const int meter_w = std::max(80, static_cast<int>(visualizer->width) - meter_x - 36);
	const Color text{232, 237, 243, 255};
	const Color dim{130, 145, 163, 255};
	const Color meter_bg{39, 47, 57, 220};

	draw_text(visualizer, label_x, y, name, 3, dim);
	draw_text(visualizer, value_x, y, state.label, 3, text);
	fill_rect(visualizer, meter_x, y + 6, meter_w, 14, meter_bg);
	fill_rect(visualizer, meter_x, y + 6, std::clamp(static_cast<int>(state.confidence * meter_w), 0, meter_w), 14,
		  accent);
}

void render_pixels(VisualizerData *visualizer, const mao::AnalysisSnapshot &snapshot)
{
	visualizer->pixels.assign(static_cast<std::size_t>(visualizer->width) * visualizer->height * 4, 0);

	fill_rect(visualizer, 0, 0, visualizer->width, visualizer->height, Color{12, 16, 22, 205});
	fill_rect(visualizer, 0, 0, visualizer->width, 8, Color{59, 130, 246, 240});

	char title[128];
	std::snprintf(title, sizeof(title), "MUSIC ANALYZER  %s", snapshot.source[0] ? snapshot.source : "WAITING");
	draw_text(visualizer, 28, 24, title, 3, Color{246, 248, 251, 255});

	char level[96];
	std::snprintf(level, sizeof(level), "RMS %.2f  LOW %.0f%% MID %.0f%% HIGH %.0f%%", snapshot.rms,
		      snapshot.low_energy * 100.0f, snapshot.mid_energy * 100.0f, snapshot.high_energy * 100.0f);
	draw_text(visualizer, 28, 58, level, 2, Color{148, 163, 184, 255});

	draw_text(visualizer, 28, 96, "DRUMS", 3, Color{148, 163, 184, 255});
	int tag_x = 150;
	for (const auto &drum : snapshot.drums) {
		draw_tag(visualizer, tag_x, 88, 118, drum.label, drum.level);
		tag_x += 126;
	}

	draw_instrument_row(visualizer, 145, "BASS", snapshot.bass, Color{35, 197, 94, 245});
	draw_instrument_row(visualizer, 185, "GUITAR", snapshot.guitar, Color{249, 115, 22, 245});
	draw_instrument_row(visualizer, 225, "KEYS", snapshot.keyboard, Color{56, 189, 248, 245});
	draw_instrument_row(visualizer, 265, "VOCAL", snapshot.vocal, Color{244, 114, 182, 245});
	draw_instrument_row(visualizer, 305, "OTHERS", snapshot.other, Color{168, 85, 247, 245});

	if (snapshot.sequence == 0)
		draw_text(visualizer, 230, 145, "ADD MUSIC ANALYZER FILTER TO AN AUDIO SOURCE", 2,
			  Color{248, 250, 252, 255});
}

void *visualizer_create(obs_data_t *settings, obs_source_t *)
{
	auto *visualizer = new VisualizerData();
	visualizer->width = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "width"), 320, 1920));
	visualizer->height = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "height"), 160, 1080));
	visualizer->update_fps = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "update_fps"), 1, 30));
	visualizer->pixels.resize(static_cast<std::size_t>(visualizer->width) * visualizer->height * 4);
	render_pixels(visualizer, read_snapshot());
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
	const float interval = 1.0f / static_cast<float>(std::max<uint32_t>(1, visualizer->update_fps));
	if (visualizer->elapsed < interval && !visualizer->dirty)
		return;
	visualizer->elapsed = 0.0f;

	const auto snapshot = read_snapshot();
	if (snapshot.sequence != visualizer->rendered_sequence || visualizer->dirty) {
		render_pixels(visualizer, snapshot);
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
		visualizer->texture = gs_texture_create(visualizer->width, visualizer->height, GS_RGBA, 1, &data_ptr, 0);
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
