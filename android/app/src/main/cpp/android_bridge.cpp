#include "analyzer.hpp"
#include "visualizer_renderer.hpp"

#include <android/bitmap.h>
#include <android/log.h>
#include <jni.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <vector>

namespace {

constexpr const char *kLogTag = "MusicAnalyzer";
constexpr float kAndroidSilenceRms = 0.0025f;
constexpr float kAndroidSilenceDrainSeconds = 2.2f;
constexpr float kAndroidIdleAnalysisSeconds = 1.0f;

struct AndroidAnalyzer {
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings;
	mao::VisualizerRenderer renderer;
	mao::AnalysisSnapshot snapshot;
	std::array<float, mao::kAnalysisWindow> ring = {};
	std::vector<float> input_buffer;
	std::vector<float> decimated_buffer;
	std::vector<float> analysis_window;
	std::mutex snapshot_mutex;
	char source_name[64] = "ANDROID";
	uint64_t sequence = 0;
	uint64_t audio_frames = 0;
	uint32_t input_sample_rate = 48000;
	uint32_t decimation_factor = 1;
	uint32_t decimation_count = 0;
	std::size_t ring_write_pos = 0;
	std::size_t buffered_samples = 0;
	std::size_t samples_since_analysis = 0;
	float decimation_sum = 0.0f;
	uint32_t silence_drain_windows = 44;
	uint32_t idle_analysis_windows = 20;
	uint32_t consecutive_silent_windows = 0;
	uint32_t silent_skip_windows = 0;
	std::atomic<float> cpu_percent{-1.0f};
	std::atomic<float> ram_mb{-1.0f};
	bool seen_nonsilent_audio = false;
};

AndroidAnalyzer *from_handle(jlong handle)
{
	return reinterpret_cast<AndroidAnalyzer *>(static_cast<intptr_t>(handle));
}

std::size_t interval_samples(const mao::AnalysisSettings &settings)
{
	const float interval = std::max(0.01f, settings.analysis_interval_seconds);
	return std::max<std::size_t>(1, static_cast<std::size_t>(interval * static_cast<float>(settings.sample_rate)));
}

std::size_t window_samples(const mao::AnalysisSettings &settings)
{
	return std::max<std::size_t>(1, mao::resolve_analysis_window_samples(settings));
}

void push_audio_samples(AndroidAnalyzer *state, const float *samples, std::size_t count)
{
	for (std::size_t i = 0; i < count; ++i) {
		state->ring[state->ring_write_pos] = samples[i];
		state->ring_write_pos = (state->ring_write_pos + 1) % state->ring.size();
	}
	state->buffered_samples = std::min<std::size_t>(state->buffered_samples + count, state->ring.size());
	state->samples_since_analysis += count;
}

void push_input_samples(AndroidAnalyzer *state, const float *samples, std::size_t count)
{
	state->audio_frames += static_cast<uint64_t>(count);
	if (state->decimation_factor <= 1) {
		push_audio_samples(state, samples, count);
		return;
	}

	const std::size_t max_decimated = count / state->decimation_factor + 1;
	if (state->decimated_buffer.size() < max_decimated)
		state->decimated_buffer.resize(max_decimated);

	std::size_t out_count = 0;
	for (std::size_t i = 0; i < count; ++i) {
		state->decimation_sum += samples[i];
		++state->decimation_count;
		if (state->decimation_count < state->decimation_factor)
			continue;
		state->decimated_buffer[out_count++] =
			state->decimation_sum / static_cast<float>(state->decimation_factor);
		state->decimation_sum = 0.0f;
		state->decimation_count = 0;
	}
	if (out_count > 0)
		push_audio_samples(state, state->decimated_buffer.data(), out_count);
}

float ring_window_rms(const AndroidAnalyzer *state, std::size_t window)
{
	const std::size_t start = (state->ring_write_pos + state->ring.size() - window) % state->ring.size();
	double square_sum = 0.0;
	for (std::size_t i = 0; i < window; ++i) {
		const float sample = state->ring[(start + i) % state->ring.size()];
		square_sum += static_cast<double>(sample) * static_cast<double>(sample);
	}
	return std::sqrt(static_cast<float>(square_sum / static_cast<double>(std::max<std::size_t>(1, window))));
}

bool should_skip_silent_analysis(AndroidAnalyzer *state)
{
	const bool draining_previous_audio =
		state->seen_nonsilent_audio && state->consecutive_silent_windows <= state->silence_drain_windows;
	if (draining_previous_audio)
		return false;
	if (state->sequence == 0)
		return false;

	++state->silent_skip_windows;
	return state->silent_skip_windows < state->idle_analysis_windows;
}

void copy_ring_window(AndroidAnalyzer *state, std::size_t window)
{
	if (state->analysis_window.size() != window)
		state->analysis_window.resize(window);
	const std::size_t start = (state->ring_write_pos + state->ring.size() - window) % state->ring.size();
	for (std::size_t i = 0; i < window; ++i)
		state->analysis_window[i] = state->ring[(start + i) % state->ring.size()];
}

bool analyze_if_ready(AndroidAnalyzer *state)
{
	const std::size_t window = window_samples(state->settings);
	const std::size_t interval = interval_samples(state->settings);
	if (state->buffered_samples < window || state->samples_since_analysis < interval)
		return false;

	state->samples_since_analysis = 0;
	const float window_rms = ring_window_rms(state, window);
	const bool silent_window = window_rms < kAndroidSilenceRms;
	if (silent_window) {
		state->consecutive_silent_windows = std::min<uint32_t>(state->consecutive_silent_windows + 1, 1000000);
	} else {
		state->consecutive_silent_windows = 0;
		state->silent_skip_windows = 0;
		state->seen_nonsilent_audio = true;
	}

	if (silent_window && should_skip_silent_analysis(state))
		return false;

	copy_ring_window(state, window);

	char source_name[64] = {};
	{
		std::lock_guard<std::mutex> lock(state->snapshot_mutex);
		std::snprintf(source_name, sizeof(source_name), "%s", state->source_name);
	}

	mao::AnalysisSnapshot snapshot =
		state->engine.analyze(state->analysis_window.data(), window, state->settings, source_name, 0);
	snapshot.sequence = ++state->sequence;
	snapshot.audio_seen = state->audio_frames > 0;
	snapshot.audio_frames = state->audio_frames;
	snapshot.analyzed_windows = state->sequence;
	snapshot.cpu_percent = state->cpu_percent.load(std::memory_order_relaxed);
	snapshot.ram_mb = state->ram_mb.load(std::memory_order_relaxed);
	if (silent_window)
		state->silent_skip_windows = 0;

	{
		std::lock_guard<std::mutex> lock(state->snapshot_mutex);
		state->snapshot = snapshot;
	}
	return true;
}

} // namespace

extern "C" JNIEXPORT jlong JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativeCreate(JNIEnv *, jclass, jint sample_rate, jint width,
							       jint height, jboolean bass_guitar)
{
	auto *state = new AndroidAnalyzer();
	state->settings.sample_rate = static_cast<uint32_t>(std::max(8000, static_cast<int>(sample_rate)));
	state->input_sample_rate = state->settings.sample_rate;
	if (state->input_sample_rate >= 44100) {
		state->decimation_factor = 2;
		state->settings.sample_rate = state->input_sample_rate / state->decimation_factor;
	}
	state->settings.input_mode = mao::AnalysisInputMode::FullMix;
	state->settings.analysis_interval_seconds = 0.10f;
	state->settings.analysis_window_seconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;
	const float interval_seconds = std::max(0.001f, state->settings.analysis_interval_seconds);
	state->silence_drain_windows =
		std::max<uint32_t>(1, static_cast<uint32_t>(std::ceil(kAndroidSilenceDrainSeconds / interval_seconds)));
	state->idle_analysis_windows =
		std::max<uint32_t>(1, static_cast<uint32_t>(std::ceil(kAndroidIdleAnalysisSeconds / interval_seconds)));
	state->renderer.layout_mode =
		bass_guitar ? mao::VisualizerLayoutMode::BassGuitar : mao::VisualizerLayoutMode::Complete;
	const uint32_t render_width =
		width > 0 ? static_cast<uint32_t>(width) :
			    (bass_guitar ? mao::kBassGuitarVisualizerWidth : mao::kDefaultVisualizerWidth);
	const uint32_t render_height =
		height > 0 ? static_cast<uint32_t>(height) :
			     (bass_guitar ? mao::kBassGuitarVisualizerHeight : mao::kDefaultVisualizerHeight);
	mao::resize_visualizer(&state->renderer, render_width, render_height);
	state->analysis_window.resize(window_samples(state->settings));
	state->input_buffer.resize(std::max<std::size_t>(4096, interval_samples(state->settings) * 4));
	state->decimated_buffer.resize(state->input_buffer.size() / std::max<uint32_t>(1, state->decimation_factor) + 1);
	mao::render_visualizer(&state->renderer, state->snapshot, 0.0f);
	return static_cast<jlong>(reinterpret_cast<intptr_t>(state));
}

extern "C" JNIEXPORT void JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativeDestroy(JNIEnv *, jclass, jlong handle)
{
	delete from_handle(handle);
}

extern "C" JNIEXPORT void JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativeSetSourceName(JNIEnv *env, jclass, jlong handle,
								      jstring source_name)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state)
		return;

	const char *text = source_name ? env->GetStringUTFChars(source_name, nullptr) : nullptr;
	{
		std::lock_guard<std::mutex> lock(state->snapshot_mutex);
		std::snprintf(state->source_name, sizeof(state->source_name), "%s", text && text[0] ? text : "ANDROID");
		std::snprintf(state->snapshot.source, sizeof(state->snapshot.source), "%s", state->source_name);
	}
	if (text)
		env->ReleaseStringUTFChars(source_name, text);
}

extern "C" JNIEXPORT jboolean JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativePushSamples(JNIEnv *env, jclass, jlong handle,
								    jfloatArray input, jint length)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state || !input || length <= 0)
		return JNI_FALSE;

	const jsize array_len = env->GetArrayLength(input);
	const jsize read_len = std::min<jsize>(array_len, length);
	if (state->input_buffer.size() < static_cast<std::size_t>(read_len))
		state->input_buffer.resize(static_cast<std::size_t>(read_len));
	env->GetFloatArrayRegion(input, 0, read_len, state->input_buffer.data());

	push_input_samples(state, state->input_buffer.data(), static_cast<std::size_t>(read_len));
	return analyze_if_ready(state) ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT void JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativeSetRuntimeMetrics(JNIEnv *, jclass, jlong handle,
									  jfloat cpu_percent,
									  jfloat ram_mb)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state)
		return;

	state->cpu_percent.store(cpu_percent, std::memory_order_relaxed);
	state->ram_mb.store(ram_mb, std::memory_order_relaxed);
	std::lock_guard<std::mutex> lock(state->snapshot_mutex);
	state->snapshot.cpu_percent = cpu_percent;
	state->snapshot.ram_mb = ram_mb;
}

extern "C" JNIEXPORT void JNICALL
Java_dev_benalu_musicanalyzer_MusicAnalyzerNative_nativeRender(JNIEnv *env, jclass, jlong handle, jobject bitmap,
							       jfloat elapsed_seconds,
							       jfloat snapshot_age_seconds)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state || !bitmap)
		return;

	AndroidBitmapInfo info = {};
	if (AndroidBitmap_getInfo(env, bitmap, &info) != ANDROID_BITMAP_RESULT_SUCCESS)
		return;
	if (info.format != ANDROID_BITMAP_FORMAT_RGBA_8888) {
		__android_log_print(ANDROID_LOG_WARN, kLogTag, "bitmap must be RGBA_8888");
		return;
	}

	void *pixels = nullptr;
	if (AndroidBitmap_lockPixels(env, bitmap, &pixels) != ANDROID_BITMAP_RESULT_SUCCESS || !pixels)
		return;

	mao::AnalysisSnapshot snapshot;
	{
		std::lock_guard<std::mutex> lock(state->snapshot_mutex);
		snapshot = state->snapshot;
	}

	mao::advance_visualizer_drum_history(&state->renderer, std::max(0.0f, elapsed_seconds));
	mao::append_visualizer_drum_hits(&state->renderer, snapshot);
	mao::render_visualizer(&state->renderer, snapshot, std::max(0.0f, snapshot_age_seconds));
	const std::size_t row_bytes = static_cast<std::size_t>(state->renderer.width) * 4;
	const std::size_t copy_h = std::min<std::size_t>(state->renderer.height, info.height);
	const std::size_t copy_w_bytes = std::min<std::size_t>(row_bytes, static_cast<std::size_t>(info.width) * 4);
	auto *dst = static_cast<uint8_t *>(pixels);
	for (std::size_t y = 0; y < copy_h; ++y) {
		std::memcpy(dst + y * info.stride, state->renderer.pixels.data() + y * row_bytes, copy_w_bytes);
	}

	AndroidBitmap_unlockPixels(env, bitmap);
}
