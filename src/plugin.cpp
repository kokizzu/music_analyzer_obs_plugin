#include "analyzer.hpp"
#include "visualizer_renderer.hpp"

#include <obs-module.h>
#include <obs-source.h>
#include <obs.h>
#include <media-io/audio-io.h>

#include <algorithm>
#include <atomic>
#include <array>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/resource.h>
#include <unistd.h>
#endif

OBS_DECLARE_MODULE()

namespace {

constexpr const char *kFilterId = "music_analyzer_filter";
constexpr const char *kVisualizerId = "music_analyzer_overlay";
static_assert((mao::kAnalysisWindow & (mao::kAnalysisWindow - 1)) == 0, "analysis window must be a power of two");

std::mutex g_snapshot_mutex;
mao::AnalysisSnapshot g_snapshot;
uint64_t g_snapshot_sequence = 0;

struct ProcessMetricsState {
	std::chrono::steady_clock::time_point last_wall = std::chrono::steady_clock::now();
	double last_cpu_seconds = -1.0;
	float cpu_percent = -1.0f;
	float ram_mb = -1.0f;
	bool initialized = false;
};

ProcessMetricsState g_process_metrics;

double process_cpu_seconds()
{
#if defined(__unix__) || defined(__APPLE__)
	rusage usage = {};
	if (getrusage(RUSAGE_SELF, &usage) != 0)
		return -1.0;
	const double user = static_cast<double>(usage.ru_utime.tv_sec) +
			    static_cast<double>(usage.ru_utime.tv_usec) / 1000000.0;
	const double system = static_cast<double>(usage.ru_stime.tv_sec) +
			      static_cast<double>(usage.ru_stime.tv_usec) / 1000000.0;
	return user + system;
#else
	return -1.0;
#endif
}

float process_ram_mb()
{
#if defined(__linux__)
	FILE *file = std::fopen("/proc/self/statm", "r");
	if (file) {
		unsigned long size_pages = 0;
		unsigned long resident_pages = 0;
		const int parsed = std::fscanf(file, "%lu %lu", &size_pages, &resident_pages);
		std::fclose(file);
		const long page_size = sysconf(_SC_PAGESIZE);
		if (parsed == 2 && page_size > 0) {
			return static_cast<float>(static_cast<double>(resident_pages) *
						  static_cast<double>(page_size) / (1024.0 * 1024.0));
		}
	}
#endif
#if defined(__unix__) || defined(__APPLE__)
	rusage usage = {};
	if (getrusage(RUSAGE_SELF, &usage) != 0)
		return -1.0f;
#if defined(__APPLE__)
	return static_cast<float>(usage.ru_maxrss) / (1024.0f * 1024.0f);
#else
	return static_cast<float>(usage.ru_maxrss) / 1024.0f;
#endif
#else
	return -1.0f;
#endif
}

void apply_process_metrics(mao::AnalysisSnapshot *snapshot)
{
	if (!snapshot)
		return;

	constexpr float kMetricsIntervalSeconds = 1.0f;
	const auto now = std::chrono::steady_clock::now();
	if (!g_process_metrics.initialized) {
		g_process_metrics.last_wall = now;
		g_process_metrics.last_cpu_seconds = process_cpu_seconds();
		g_process_metrics.cpu_percent = g_process_metrics.last_cpu_seconds >= 0.0 ? 0.0f : -1.0f;
		g_process_metrics.ram_mb = process_ram_mb();
		g_process_metrics.initialized = true;
	} else {
		const float elapsed = std::chrono::duration<float>(now - g_process_metrics.last_wall).count();
		if (elapsed >= kMetricsIntervalSeconds) {
			const double cpu_seconds = process_cpu_seconds();
			if (cpu_seconds >= 0.0 && g_process_metrics.last_cpu_seconds >= 0.0 && elapsed > 0.0f) {
				g_process_metrics.cpu_percent =
					static_cast<float>((cpu_seconds - g_process_metrics.last_cpu_seconds) *
							   100.0 / static_cast<double>(elapsed));
			}
			g_process_metrics.ram_mb = process_ram_mb();
			g_process_metrics.last_wall = now;
			g_process_metrics.last_cpu_seconds = cpu_seconds;
		}
	}

	snapshot->cpu_percent = g_process_metrics.cpu_percent;
	snapshot->ram_mb = g_process_metrics.ram_mb;
}

void copy_text(char *dst, std::size_t dst_size, const char *src)
{
	if (!dst || dst_size == 0)
		return;
	std::snprintf(dst, dst_size, "%s", src ? src : "");
}

void publish_snapshot(mao::AnalysisSnapshot snapshot)
{
	std::lock_guard<std::mutex> lock(g_snapshot_mutex);
	apply_process_metrics(&snapshot);
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
	std::atomic<uint32_t> window_ms{mao::kDefaultAnalysisWindowMs};
	std::atomic<bool> legacy_window{false};
	std::atomic<uint32_t> sensitivity_percent{100};
	std::atomic<bool> parent_name_resolved{false};
	std::atomic<uint64_t> direct_audio_frames_seen{0};
	uint32_t samples_until_analysis = 2400;
	char source_name[64] = {};
	char pending_source_name[64] = {};
	std::size_t pending_window_samples = mao::kLegacyAnalysisWindow;
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

	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const uint32_t hop_samples = std::max<uint32_t>(1, filter->hop_samples.load(std::memory_order_relaxed));
	filter->pending_settings.sample_rate = sample_rate;
	filter->pending_settings.sensitivity =
		static_cast<float>(filter->sensitivity_percent.load(std::memory_order_relaxed)) / 100.0f;
	filter->pending_settings.analysis_interval_seconds =
		static_cast<float>(hop_samples) / static_cast<float>(std::max<uint32_t>(1, sample_rate));
	filter->pending_settings.analysis_window_seconds =
		static_cast<float>(std::max<uint32_t>(20, filter->window_ms.load(std::memory_order_relaxed))) /
		1000.0f;
	filter->pending_settings.analysis_window_samples =
		filter->legacy_window.load(std::memory_order_relaxed) ?
			static_cast<uint32_t>(mao::kLegacyAnalysisWindow) :
			0;
	filter->pending_settings.input_mode = mao::AnalysisInputMode::FullMix;
	const std::size_t window_samples = mao::resolve_analysis_window_samples(filter->pending_settings);
	copy_text(filter->pending_source_name, sizeof(filter->pending_source_name),
		  source_label && *source_label ? source_label : filter->source_name);
	filter->pending_window_samples = window_samples;
	filter->pending_audio_frames = filter->audio_frames_seen;
	filter->pending_analyzed_windows = ++filter->analyzed_windows;
	for (std::size_t i = 0; i < window_samples; ++i) {
		const std::size_t idx = (filter->write_pos + mao::kAnalysisWindow - window_samples + i) &
					(mao::kAnalysisWindow - 1);
		filter->pending_window[i] = filter->ring[idx];
	}
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
	settings.analysis_window_seconds =
		static_cast<float>(std::max<uint32_t>(20, filter->window_ms.load(std::memory_order_relaxed))) /
		1000.0f;
	settings.analysis_window_samples =
		filter->legacy_window.load(std::memory_order_relaxed) ?
			static_cast<uint32_t>(mao::kLegacyAnalysisWindow) :
			0;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

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
		float mixed_sum = 0.0f;
		float square_sum = 0.0f;
		float strongest_sample = 0.0f;
		float strongest_abs = 0.0f;
		uint32_t valid_planes = 0;

		for (uint32_t ch = 0; ch < channels; ++ch) {
			if (!planes[ch])
				continue;
			const float sample = planes[ch][frame];
			const float abs_sample = std::abs(sample);
			mixed_sum += sample;
			square_sum += sample * sample;
			if (abs_sample > strongest_abs) {
				strongest_abs = abs_sample;
				strongest_sample = sample;
			}
			++valid_planes;
		}

		if (valid_planes == 0)
			continue;

		float mixed = mixed_sum / static_cast<float>(valid_planes);
		if (valid_planes > 1) {
			const float channel_rms = std::sqrt(square_sum / static_cast<float>(valid_planes));
			if (channel_rms > 1.0e-8f && std::abs(mixed) < channel_rms * 0.75f)
				mixed = std::copysign(channel_rms, strongest_sample);
		}
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
		std::size_t window_samples = mao::kLegacyAnalysisWindow;

		{
			std::unique_lock<std::mutex> lock(filter->worker_mutex);
			filter->worker_cv.wait(lock, [&]() { return filter->stop_worker || filter->pending; });
			if (filter->stop_worker)
				return;

			local_window = filter->pending_window;
			settings = filter->pending_settings;
			copy_text(source_name, sizeof(source_name), filter->pending_source_name);
			window_samples = filter->pending_window_samples;
			dropped = filter->dropped_windows;
			audio_frames = filter->pending_audio_frames;
			analyzed_windows = filter->pending_analyzed_windows;
			filter->pending = false;
		}

		auto snapshot = filter->engine.analyze(local_window.data(), window_samples, settings, source_name, dropped);
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
	const long long configured_window_ms = obs_data_get_int(settings, "window_ms");
	const long long window_ms = configured_window_ms > 0 ? configured_window_ms : mao::kDefaultAnalysisWindowMs;
	const uint32_t sample_rate = filter->sample_rate.load(std::memory_order_relaxed);
	const uint32_t hop =
		std::max<uint32_t>(1, sample_rate * static_cast<uint32_t>(std::max<long long>(20, update_ms)) / 1000);
	filter->hop_samples.store(hop, std::memory_order_relaxed);
	filter->samples_until_analysis = hop;
	filter->window_ms.store(static_cast<uint32_t>(std::clamp<long long>(window_ms, 20, 170)),
				std::memory_order_relaxed);
	filter->legacy_window.store(obs_data_get_bool(settings, "legacy_window"), std::memory_order_relaxed);
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
	obs_data_set_default_int(settings, "window_ms", mao::kDefaultAnalysisWindowMs);
	obs_data_set_default_bool(settings, "legacy_window", false);
	obs_data_set_default_int(settings, "sensitivity", 100);
}

obs_properties_t *filter_properties(void *)
{
	obs_properties_t *props = obs_properties_create();
	obs_properties_add_int_slider(props, "update_ms", "Analyzer interval (ms)", 20, 250, 5);
	obs_properties_add_int_slider(props, "window_ms", "Analysis window (ms)", 20, 170, 5);
	obs_properties_add_bool(props, "legacy_window", "Use legacy 4096-sample analysis window");
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
	const long long configured_window_ms = obs_data_get_int(settings, "window_ms");
	const long long window_ms = std::clamp<long long>(
		configured_window_ms > 0 ? configured_window_ms : mao::kDefaultAnalysisWindowMs, 20, 170);
	filter->hop_samples.store(std::max<uint32_t>(1, sample_rate * static_cast<uint32_t>(update_ms) / 1000),
				  std::memory_order_relaxed);
	filter->window_ms.store(static_cast<uint32_t>(window_ms), std::memory_order_relaxed);
	filter->legacy_window.store(obs_data_get_bool(settings, "legacy_window"), std::memory_order_relaxed);
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

struct VisualizerData {
	mutable std::mutex mutex;
	mao::VisualizerRenderer renderer;
	uint32_t update_fps = 10;
	float elapsed = 1.0f;
	float snapshot_age = 0.0f;
	float stale_status_elapsed = 0.0f;
	uint64_t rendered_sequence = 0;
	bool dirty = true;
	bool texture_size_dirty = true;
	gs_texture_t *texture = nullptr;
};

void *visualizer_create(obs_data_t *settings, obs_source_t *)
{
	auto *visualizer = new VisualizerData();
	const uint32_t width = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "width"), 320, 1920));
	const uint32_t height = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "height"), 520, 1080));
	visualizer->update_fps = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "update_fps"), 1, 30));
	mao::resize_visualizer(&visualizer->renderer, width, height);
	mao::render_visualizer(&visualizer->renderer, read_snapshot(), 0.0f);
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
	obs_data_set_default_int(settings, "width", mao::kDefaultVisualizerWidth);
	obs_data_set_default_int(settings, "height", mao::kDefaultVisualizerHeight);
	obs_data_set_default_int(settings, "update_fps", 10);
}

obs_properties_t *visualizer_properties(void *)
{
	obs_properties_t *props = obs_properties_create();
	obs_properties_add_int(props, "width", "Width", 320, 1920, 10);
	obs_properties_add_int(props, "height", "Height", 520, 1080, 10);
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
	const uint32_t height = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "height"), 520, 1080));
	visualizer->update_fps = static_cast<uint32_t>(std::clamp<long long>(obs_data_get_int(settings, "update_fps"), 1, 30));
	if (width != visualizer->renderer.width || height != visualizer->renderer.height) {
		mao::resize_visualizer(&visualizer->renderer, width, height);
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
	visualizer->stale_status_elapsed += seconds;
	const float interval = 1.0f / static_cast<float>(std::max<uint32_t>(1, visualizer->update_fps));
	const bool interval_ready = visualizer->elapsed >= interval;
	const bool history_active = mao::advance_visualizer_drum_history(&visualizer->renderer, seconds);
	const auto snapshot = read_snapshot();
	const bool stale_status_due =
		snapshot.sequence > 0 && visualizer->snapshot_age > 1.5f && visualizer->stale_status_elapsed >= 1.0f;

	if (mao::append_visualizer_drum_hits(&visualizer->renderer, snapshot))
		visualizer->dirty = true;
	if (history_active && interval_ready)
		visualizer->dirty = true;

	if (!interval_ready && !visualizer->dirty)
		return;
	if (interval_ready)
		visualizer->elapsed = 0.0f;

	if (snapshot.sequence != visualizer->rendered_sequence) {
		if (mao::snapshot_resets_visualizer_age(snapshot)) {
			visualizer->snapshot_age = 0.0f;
			visualizer->stale_status_elapsed = 0.0f;
		}
		mao::render_visualizer(&visualizer->renderer, snapshot, visualizer->snapshot_age);
		visualizer->rendered_sequence = snapshot.sequence;
		visualizer->dirty = true;
	} else if (visualizer->dirty || stale_status_due) {
		visualizer->stale_status_elapsed = 0.0f;
		mao::render_visualizer(&visualizer->renderer, snapshot, visualizer->snapshot_age);
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
		const uint8_t *data_ptr = visualizer->renderer.pixels.data();
		visualizer->texture =
			gs_texture_create(visualizer->renderer.width, visualizer->renderer.height, GS_RGBA, 1, &data_ptr,
					  GS_DYNAMIC);
		visualizer->texture_size_dirty = false;
		visualizer->dirty = false;
	} else if (visualizer->dirty) {
		gs_texture_set_image(visualizer->texture, visualizer->renderer.pixels.data(),
				     visualizer->renderer.width * 4, false);
		visualizer->dirty = false;
	}

	if (visualizer->texture)
		obs_source_draw(visualizer->texture, 0, 0, visualizer->renderer.width, visualizer->renderer.height, false);
}

uint32_t visualizer_width(void *data)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return mao::kDefaultVisualizerWidth;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	return visualizer->renderer.width;
}

uint32_t visualizer_height(void *data)
{
	auto *visualizer = static_cast<VisualizerData *>(data);
	if (!visualizer)
		return mao::kDefaultVisualizerHeight;

	std::lock_guard<std::mutex> lock(visualizer->mutex);
	return visualizer->renderer.height;
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
