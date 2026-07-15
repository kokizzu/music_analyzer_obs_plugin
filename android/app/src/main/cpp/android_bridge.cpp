#include "analyzer.hpp"
#include "visualizer_renderer.hpp"

#include <android/bitmap.h>
#include <android/log.h>
#include <jni.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <vector>

namespace {

constexpr const char *kLogTag = "MusicAnalyzer";

struct AndroidAnalyzer {
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings;
	mao::VisualizerRenderer renderer;
	mao::AnalysisSnapshot snapshot;
	std::vector<float> samples;
	std::vector<float> input_buffer;
	std::mutex mutex;
	uint64_t sequence = 0;
	uint64_t audio_frames = 0;
	std::size_t samples_since_analysis = 0;
	float cpu_percent = -1.0f;
	float free_memory_percent = -1.0f;
	bool rendered_once = false;
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

bool analyze_if_ready(AndroidAnalyzer *state)
{
	const std::size_t window = window_samples(state->settings);
	const std::size_t interval = interval_samples(state->settings);
	if (state->samples.size() < window || state->samples_since_analysis < interval)
		return false;

	const float *window_start = state->samples.data() + state->samples.size() - window;
	state->snapshot =
		state->engine.analyze(window_start, window, state->settings, "ANDROID", state->snapshot.dropped_windows);
	state->snapshot.sequence = ++state->sequence;
	state->snapshot.audio_seen = state->audio_frames > 0;
	state->snapshot.audio_frames = state->audio_frames;
	state->snapshot.analyzed_windows = state->sequence;
	state->snapshot.cpu_percent = state->cpu_percent;
	state->snapshot.free_memory_percent = state->free_memory_percent;
	state->samples_since_analysis = 0;
	mao::append_visualizer_drum_hits(&state->renderer, state->snapshot);
	return true;
}

void trim_samples(AndroidAnalyzer *state)
{
	const std::size_t keep = window_samples(state->settings) + interval_samples(state->settings) * 2;
	if (state->samples.size() <= keep)
		return;
	const std::size_t extra = state->samples.size() - keep;
	std::memmove(state->samples.data(), state->samples.data() + extra, keep * sizeof(float));
	state->samples.resize(keep);
}

} // namespace

extern "C" JNIEXPORT jlong JNICALL
Java_dev_kyz_musicanalyzer_MusicAnalyzerNative_nativeCreate(JNIEnv *, jclass, jint sample_rate, jint width, jint height,
							    jboolean bass_guitar)
{
	auto *state = new AndroidAnalyzer();
	state->settings.sample_rate = static_cast<uint32_t>(std::max(8000, static_cast<int>(sample_rate)));
	state->settings.input_mode = mao::AnalysisInputMode::FullMix;
	state->settings.analysis_interval_seconds = 0.05f;
	state->settings.analysis_window_seconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;
	state->renderer.layout_mode =
		bass_guitar ? mao::VisualizerLayoutMode::BassGuitar : mao::VisualizerLayoutMode::Complete;
	const uint32_t render_width =
		width > 0 ? static_cast<uint32_t>(width) :
			    (bass_guitar ? mao::kBassGuitarVisualizerWidth : mao::kDefaultVisualizerWidth);
	const uint32_t render_height =
		height > 0 ? static_cast<uint32_t>(height) :
			     (bass_guitar ? mao::kBassGuitarVisualizerHeight : mao::kDefaultVisualizerHeight);
	mao::resize_visualizer(&state->renderer, render_width, render_height);
	state->samples.reserve(window_samples(state->settings) + interval_samples(state->settings) * 3);
	state->input_buffer.reserve(interval_samples(state->settings));
	mao::render_visualizer(&state->renderer, state->snapshot, 0.0f);
	state->rendered_once = true;
	return static_cast<jlong>(reinterpret_cast<intptr_t>(state));
}

extern "C" JNIEXPORT void JNICALL
Java_dev_kyz_musicanalyzer_MusicAnalyzerNative_nativeDestroy(JNIEnv *, jclass, jlong handle)
{
	delete from_handle(handle);
}

extern "C" JNIEXPORT jboolean JNICALL
Java_dev_kyz_musicanalyzer_MusicAnalyzerNative_nativePushSamples(JNIEnv *env, jclass, jlong handle, jfloatArray input,
								 jint length)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state || !input || length <= 0)
		return JNI_FALSE;

	const jsize array_len = env->GetArrayLength(input);
	const jsize read_len = std::min<jsize>(array_len, length);
	if (state->input_buffer.size() < static_cast<std::size_t>(read_len))
		state->input_buffer.resize(static_cast<std::size_t>(read_len));
	env->GetFloatArrayRegion(input, 0, read_len, state->input_buffer.data());

	std::lock_guard<std::mutex> lock(state->mutex);
	state->samples.insert(state->samples.end(), state->input_buffer.begin(),
			      state->input_buffer.begin() + read_len);
	state->audio_frames += static_cast<uint64_t>(read_len);
	state->samples_since_analysis += static_cast<std::size_t>(read_len);
	trim_samples(state);

	return analyze_if_ready(state) ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT void JNICALL
Java_dev_kyz_musicanalyzer_MusicAnalyzerNative_nativeSetRuntimeMetrics(JNIEnv *, jclass, jlong handle,
									jfloat cpu_percent,
									jfloat free_memory_percent)
{
	AndroidAnalyzer *state = from_handle(handle);
	if (!state)
		return;

	std::lock_guard<std::mutex> lock(state->mutex);
	state->cpu_percent = cpu_percent;
	state->free_memory_percent = free_memory_percent;
	state->snapshot.cpu_percent = cpu_percent;
	state->snapshot.free_memory_percent = free_memory_percent;
}

extern "C" JNIEXPORT void JNICALL
Java_dev_kyz_musicanalyzer_MusicAnalyzerNative_nativeRender(JNIEnv *env, jclass, jlong handle, jobject bitmap,
							    jfloat elapsed_seconds, jfloat snapshot_age_seconds)
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

	{
		std::lock_guard<std::mutex> lock(state->mutex);
		mao::advance_visualizer_drum_history(&state->renderer, std::max(0.0f, elapsed_seconds));
		mao::render_visualizer(&state->renderer, state->snapshot, std::max(0.0f, snapshot_age_seconds));
		const std::size_t row_bytes = static_cast<std::size_t>(state->renderer.width) * 4;
		const std::size_t copy_h = std::min<std::size_t>(state->renderer.height, info.height);
		const std::size_t copy_w_bytes = std::min<std::size_t>(row_bytes, static_cast<std::size_t>(info.width) * 4);
		auto *dst = static_cast<uint8_t *>(pixels);
		for (std::size_t y = 0; y < copy_h; ++y) {
			std::memcpy(dst + y * info.stride, state->renderer.pixels.data() + y * row_bytes, copy_w_bytes);
		}
	}

	AndroidBitmap_unlockPixels(env, bitmap);
}
