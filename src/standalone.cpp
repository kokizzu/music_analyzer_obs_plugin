#include "analyzer.hpp"
#include "visualizer_renderer.hpp"

#ifndef MAO_STANDALONE_WITH_SDL
#define MAO_STANDALONE_WITH_SDL 0
#endif

#ifndef MAO_STANDALONE_VERSION
#define MAO_STANDALONE_VERSION "unknown"
#endif

#if MAO_STANDALONE_WITH_SDL
#ifndef SDL_MAIN_HANDLED
#define SDL_MAIN_HANDLED
#endif
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wold-style-cast"
#endif
#include <SDL.h>
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
#else
#error "music-analyzer-standalone requires MAO_STANDALONE_WITH_SDL=1 and SDL2 development headers"
#endif

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <poll.h>
#include <csignal>
#include <string>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

namespace {

constexpr float kPi = 3.14159265358979323846f;
constexpr const char *kFfmpegLogLevel = "quiet";
constexpr float kStandaloneSilenceRms = 0.0025f;
constexpr float kStandaloneSilenceDrainSeconds = 2.2f;
constexpr float kStandaloneIdleAnalysisSeconds = 1.0f;
constexpr float kStandaloneIdleFrameSeconds = 0.5f;

struct Options {
	std::string input_path;
	std::string raw_f32le_path;
	std::string source_name = "STANDALONE";
	std::string device_name;
	uint32_t sample_rate = 48000;
	uint32_t width = mao::kDefaultVisualizerWidth;
	uint32_t height = mao::kDefaultVisualizerHeight;
	uint32_t update_ms = 50;
	uint32_t fps = 30;
	float sensitivity = 1.0f;
	bool hold_on_eof = false;
	bool list_devices = false;
	bool self_test = false;
	bool show_version = false;
	bool prefer_output_monitor = true;
};

struct AspectViewport {
	int x = 0;
	int y = 0;
	int w = 1;
	int h = 1;
};

struct AspectSize {
	int w = 1;
	int h = 1;
};

struct AspectPlacement {
	int x = 0;
	int y = 0;
	int w = 1;
	int h = 1;
};

AspectViewport aspect_fit_viewport(int window_w, int window_h, int aspect_w, int aspect_h)
{
	window_w = std::max(1, window_w);
	window_h = std::max(1, window_h);
	aspect_w = std::max(1, aspect_w);
	aspect_h = std::max(1, aspect_h);

	const int fitted_h_from_w = std::max(1, window_w * aspect_h / aspect_w);
	if (fitted_h_from_w <= window_h) {
		return AspectViewport{0, (window_h - fitted_h_from_w) / 2, window_w, fitted_h_from_w};
	}

	const int fitted_w_from_h = std::max(1, window_h * aspect_w / aspect_h);
	return AspectViewport{(window_w - fitted_w_from_h) / 2, 0, fitted_w_from_h, window_h};
}

AspectSize aspect_preserved_window_size(int window_w, int window_h, int aspect_w, int aspect_h)
{
	window_w = std::max(1, window_w);
	window_h = std::max(1, window_h);
	aspect_w = std::max(1, aspect_w);
	aspect_h = std::max(1, aspect_h);

	const int height_from_width =
		std::max(1, static_cast<int>((static_cast<int64_t>(window_w) * aspect_h + aspect_w / 2) / aspect_w));
	const int width_from_height =
		std::max(1, static_cast<int>((static_cast<int64_t>(window_h) * aspect_w + aspect_h / 2) / aspect_h));
	const int width_driven_delta = std::abs(height_from_width - window_h);
	const int height_driven_delta = std::abs(width_from_height - window_w);
	if (width_driven_delta <= height_driven_delta)
		return AspectSize{window_w, height_from_width};
	return AspectSize{width_from_height, window_h};
}

AspectSize minimum_aspect_window_size(int aspect_w, int aspect_h)
{
	aspect_w = std::max(1, aspect_w);
	aspect_h = std::max(1, aspect_h);
	const int h_from_min_w =
		std::max(1, static_cast<int>((static_cast<int64_t>(640) * aspect_h + aspect_w / 2) / aspect_w));
	if (h_from_min_w >= 360)
		return AspectSize{640, h_from_min_w};
	const int w_from_min_h =
		std::max(1, static_cast<int>((static_cast<int64_t>(360) * aspect_w + aspect_h / 2) / aspect_h));
	return AspectSize{w_from_min_h, 360};
}

AspectPlacement top_aligned_aspect_placement(int bounds_x, int bounds_y, int bounds_w, int bounds_h,
					     int aspect_w, int aspect_h)
{
	const AspectViewport fit = aspect_fit_viewport(bounds_w, bounds_h, aspect_w, aspect_h);
	return AspectPlacement{bounds_x + fit.x, bounds_y, fit.w, fit.h};
}

void print_usage(const char *argv0)
{
	std::fprintf(stderr,
		     "Usage: %s [--input audio-file] [--raw-f32le file|-] [--device name]\n"
		     "       [--source name] [--width px] [--height px] [--update-ms ms]\n"
		     "       [--fps fps] [--sample-rate hz] [--sensitivity percent]\n"
		     "       [--list-devices] [--default-input] [--hold] [--version] [--self-test]\n\n"
		     "No input option prefers an SDL output monitor/loopback device, then falls back to default input.\n",
		     argv0);
}

bool parse_uint(const char *text, uint32_t min_value, uint32_t max_value, uint32_t *out)
{
	if (!text || !*text || !out)
		return false;
	char *end = nullptr;
	const unsigned long value = std::strtoul(text, &end, 10);
	if (!end || *end != '\0' || value < min_value || value > max_value)
		return false;
	*out = static_cast<uint32_t>(value);
	return true;
}

bool parse_options(int argc, char **argv, Options *options)
{
	if (!options)
		return false;

	for (int i = 1; i < argc; ++i) {
		const std::string arg = argv[i];
		auto need_value = [&](const char *name) -> const char * {
			if (i + 1 >= argc) {
				std::fprintf(stderr, "%s requires a value\n", name);
				return nullptr;
			}
			return argv[++i];
		};

		if (arg == "--help" || arg == "-h") {
			print_usage(argv[0]);
			std::exit(0);
		} else if (arg == "--version") {
			options->show_version = true;
		} else if (arg == "--input") {
			const char *value = need_value("--input");
			if (!value)
				return false;
			options->input_path = value;
		} else if (arg == "--raw-f32le") {
			const char *value = need_value("--raw-f32le");
			if (!value)
				return false;
			options->raw_f32le_path = value;
		} else if (arg == "--device") {
			const char *value = need_value("--device");
			if (!value)
				return false;
			options->device_name = value;
		} else if (arg == "--source") {
			const char *value = need_value("--source");
			if (!value)
				return false;
			options->source_name = value;
		} else if (arg == "--width") {
			const char *value = need_value("--width");
			if (!value || !parse_uint(value, 320, 3840, &options->width))
				return false;
		} else if (arg == "--height") {
			const char *value = need_value("--height");
			if (!value || !parse_uint(value, 520, 2160, &options->height))
				return false;
		} else if (arg == "--update-ms") {
			const char *value = need_value("--update-ms");
			if (!value || !parse_uint(value, 20, 250, &options->update_ms))
				return false;
		} else if (arg == "--fps") {
			const char *value = need_value("--fps");
			if (!value || !parse_uint(value, 1, 60, &options->fps))
				return false;
		} else if (arg == "--sample-rate") {
			const char *value = need_value("--sample-rate");
			if (!value || !parse_uint(value, 8000, 192000, &options->sample_rate))
				return false;
		} else if (arg == "--sensitivity") {
			uint32_t percent = 0;
			const char *value = need_value("--sensitivity");
			if (!value || !parse_uint(value, 25, 400, &percent))
				return false;
			options->sensitivity = static_cast<float>(percent) / 100.0f;
		} else if (arg == "--list-devices") {
			options->list_devices = true;
		} else if (arg == "--default-input") {
			options->prefer_output_monitor = false;
		} else if (arg == "--hold") {
			options->hold_on_eof = true;
		} else if (arg == "--self-test") {
			options->self_test = true;
		} else {
			std::fprintf(stderr, "unknown option: %s\n", arg.c_str());
			return false;
		}
	}

	if (!options->input_path.empty() && !options->raw_f32le_path.empty()) {
		std::fprintf(stderr, "--input and --raw-f32le are mutually exclusive\n");
		return false;
	}
	if (!options->device_name.empty() && (!options->input_path.empty() || !options->raw_f32le_path.empty())) {
		std::fprintf(stderr, "--device is only valid for live SDL capture\n");
		return false;
	}

	return true;
}

bool key_requests_exit(SDL_Keycode key)
{
	return key == SDLK_ESCAPE || key == SDLK_q;
}

std::string lowercase_ascii(const std::string &text)
{
	std::string out;
	out.reserve(text.size());
	for (unsigned char c : text)
		out.push_back(static_cast<char>(std::tolower(c)));
	return out;
}

bool contains_wordish(const std::string &haystack, const char *needle)
{
	return haystack.find(needle) != std::string::npos;
}

bool looks_like_output_monitor_device(const std::string &name)
{
	const std::string lower = lowercase_ascii(name);
	if (contains_wordish(lower, "monitor"))
		return true;
	if (contains_wordish(lower, "loopback"))
		return true;
	if (contains_wordish(lower, "what u hear") || contains_wordish(lower, "stereo mix"))
		return true;
	if (contains_wordish(lower, "output") && contains_wordish(lower, "capture"))
		return true;
	return false;
}

std::string choose_capture_device_name(const std::vector<std::string> &devices, const Options &options)
{
	if (!options.device_name.empty())
		return options.device_name;
	if (!options.prefer_output_monitor)
		return "";

	for (const std::string &device : devices) {
		if (looks_like_output_monitor_device(device))
			return device;
	}
	return "";
}

float midi_frequency(int midi)
{
	return 440.0f * std::pow(2.0f, (static_cast<float>(midi) - 69.0f) / 12.0f);
}

void add_midi_note(std::array<float, mao::kAnalysisWindow> *buffer, int midi, float amp, uint32_t sample_rate)
{
	const float frequency = midi_frequency(midi);
	for (std::size_t i = 0; i < buffer->size(); ++i) {
		(*buffer)[i] +=
			amp * std::sin(2.0f * kPi * frequency * static_cast<float>(i) / static_cast<float>(sample_rate));
	}
}

bool run_idle_throttle_self_test();

bool run_self_test()
{
	mao::AnalysisSettings settings;
	settings.sample_rate = 48000;
	settings.sensitivity = 1.0f;
	settings.analysis_interval_seconds = 0.05f;
	settings.input_mode = mao::AnalysisInputMode::IsolatedKeyboard;

	mao::AnalysisEngine engine;
	mao::AnalysisSnapshot snapshot;
	std::array<float, mao::kAnalysisWindow> buffer = {};
	for (int frame = 0; frame < 5; ++frame) {
		buffer.fill(0.0f);
		add_midi_note(&buffer, 60, 0.22f, settings.sample_rate);
		add_midi_note(&buffer, 64, 0.20f, settings.sample_rate);
		add_midi_note(&buffer, 67, 0.18f, settings.sample_rate);
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		snapshot.sequence = static_cast<uint64_t>(frame + 1);
		snapshot.audio_seen = true;
		snapshot.audio_frames = static_cast<uint64_t>(frame + 1) * mao::kAnalysisWindow;
		snapshot.analyzed_windows = static_cast<uint64_t>(frame + 1);
	}

	mao::VisualizerRenderer renderer;
	mao::resize_visualizer(&renderer, 960, 540);
	mao::append_visualizer_drum_hits(&renderer, snapshot);
	mao::render_visualizer(&renderer, snapshot, 0.0f);

	std::size_t bright_pixels = 0;
	for (std::size_t i = 0; i + 3 < renderer.pixels.size(); i += 4) {
		if (renderer.pixels[i] > 24 || renderer.pixels[i + 1] > 30 || renderer.pixels[i + 2] > 38)
			++bright_pixels;
	}

	if (renderer.pixels.size() != static_cast<std::size_t>(960 * 540 * 4) || bright_pixels < 1000) {
		std::fprintf(stderr, "standalone self-test: renderer produced too few visible pixels\n");
		return false;
	}
	{
		mao::AnalysisSnapshot status_snapshot = {};
		status_snapshot.rms = 0.12f;
		status_snapshot.low_energy = 0.25f;
		status_snapshot.mid_energy = 0.50f;
		status_snapshot.high_energy = 0.25f;
		status_snapshot.dropped_windows = 7;
		char status_line[128] = {};
		mao::format_visualizer_status_line(status_line, sizeof(status_line), status_snapshot, 1.6f);
		const char *age = std::strstr(status_line, "AGE ");
		const char *drop = std::strstr(status_line, "DROP ");
		const char *expected = "RMS 0.12 LOW 25% MID 50% HIGH 25% AGE 1.6S DROP 7";
		if (std::strstr(status_line, "FRAMES") || std::strstr(status_line, "UPD") || !age || !drop ||
		    age > drop || std::strcmp(status_line, expected) != 0) {
			std::fprintf(stderr, "standalone self-test: unexpected status line '%s'\n", status_line);
			return false;
		}
	}
	{
		mao::VisualizerRenderer bpm_renderer;
		mao::resize_visualizer(&bpm_renderer, 960, 540);
		mao::AnalysisSnapshot bpm_snapshot = {};
		bpm_snapshot.audio_seen = true;
		bpm_snapshot.sequence = 42;
		bpm_snapshot.estimated_bpm = 128.0f;
		bpm_snapshot.bpm_confidence = 0.82f;
		std::snprintf(bpm_snapshot.root_candidates, sizeof(bpm_snapshot.root_candidates), "-- 0%%");
		mao::render_visualizer(&bpm_renderer, bpm_snapshot, 0.0f);

		std::size_t bpm_pixels = 0;
		for (int y = 520; y < 540; ++y) {
			for (int x = 760; x < 940; ++x) {
				const std::size_t offset = static_cast<std::size_t>((y * 960 + x) * 4);
				if (offset + 2 < bpm_renderer.pixels.size() && bpm_renderer.pixels[offset] > 220 &&
				    bpm_renderer.pixels[offset + 1] > 220 && bpm_renderer.pixels[offset + 2] > 220)
					++bpm_pixels;
			}
		}
		if (bpm_pixels < 20) {
			std::fprintf(stderr, "standalone self-test: expected BPM text at bottom right\n");
			return false;
		}
	}
	if (std::strstr(snapshot.keyboard_chord.label, "C") == nullptr) {
		std::fprintf(stderr, "standalone self-test: expected keyboard C chord, got '%s'\n",
			     snapshot.keyboard_chord.label);
		return false;
	}
	if (std::strstr(renderer.stable_labels[3].label, "C") == nullptr) {
		std::fprintf(stderr, "standalone self-test: expected stable keyboard label, got '%s'\n",
			     renderer.stable_labels[3].label);
		return false;
	}
	{
		mao::VisualizerRenderer stable_renderer;
		mao::resize_visualizer(&stable_renderer, 960, 540);
		mao::AnalysisSnapshot stable_snapshot;
		stable_snapshot.audio_seen = true;
		stable_snapshot.rms = 0.10f;
		stable_snapshot.sequence = 1;
		stable_snapshot.bass_notes.rows[0][0].active = true;
		stable_snapshot.bass_notes.rows[0][0].midi = 48;
		stable_snapshot.bass_notes.rows[0][0].level = 0.90f;
		std::snprintf(stable_snapshot.bass_notes.rows[0][0].label,
			      sizeof(stable_snapshot.bass_notes.rows[0][0].label), "3");
		mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		if (std::strcmp(stable_renderer.stable_labels[0].label, "C") != 0) {
			std::fprintf(stderr, "standalone self-test: expected bass stable label C, got '%s'\n",
				     stable_renderer.stable_labels[0].label);
			return false;
		}

		for (uint64_t sequence = 2; sequence <= 4; ++sequence) {
			stable_snapshot = {};
			stable_snapshot.audio_seen = true;
			stable_snapshot.rms = 0.10f;
			stable_snapshot.sequence = sequence;
			stable_snapshot.bass_notes.rows[0][0].active = true;
			stable_snapshot.bass_notes.rows[0][0].midi = 48;
			stable_snapshot.bass_notes.rows[0][0].level = 0.62f;
			std::snprintf(stable_snapshot.bass_notes.rows[0][0].label,
				      sizeof(stable_snapshot.bass_notes.rows[0][0].label), "3");
			mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		}
		stable_snapshot = {};
		stable_snapshot.audio_seen = true;
		stable_snapshot.rms = 0.10f;
		stable_snapshot.sequence = 5;
		stable_snapshot.bass_notes.rows[0][0].active = true;
		stable_snapshot.bass_notes.rows[0][0].midi = 50;
		stable_snapshot.bass_notes.rows[0][0].level = 1.00f;
		std::snprintf(stable_snapshot.bass_notes.rows[0][0].label,
			      sizeof(stable_snapshot.bass_notes.rows[0][0].label), "3");
		mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		if (std::strcmp(stable_renderer.stable_labels[0].label, "C") != 0) {
			std::fprintf(stderr,
				     "standalone self-test: one-frame louder bass note replaced frequent label with '%s'\n",
				     stable_renderer.stable_labels[0].label);
			return false;
		}

		for (uint64_t sequence = 6; sequence <= 9; ++sequence) {
			stable_snapshot = {};
			stable_snapshot.audio_seen = true;
			stable_snapshot.rms = 0.10f;
			stable_snapshot.sequence = sequence;
			stable_snapshot.vocal_notes.rows[0][0].active = true;
			stable_snapshot.vocal_notes.rows[0][0].midi = 69;
			stable_snapshot.vocal_notes.rows[0][0].level = 0.58f;
			std::snprintf(stable_snapshot.vocal_notes.rows[0][0].label,
				      sizeof(stable_snapshot.vocal_notes.rows[0][0].label), "4");
			mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		}
		stable_snapshot = {};
		stable_snapshot.audio_seen = true;
		stable_snapshot.rms = 0.10f;
		stable_snapshot.sequence = 10;
		stable_snapshot.vocal_notes.rows[0][0].active = true;
		stable_snapshot.vocal_notes.rows[0][0].midi = 71;
		stable_snapshot.vocal_notes.rows[0][0].level = 1.00f;
		std::snprintf(stable_snapshot.vocal_notes.rows[0][0].label,
			      sizeof(stable_snapshot.vocal_notes.rows[0][0].label), "4");
		mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		if (std::strcmp(stable_renderer.stable_labels[1].label, "A") != 0) {
			std::fprintf(stderr,
				     "standalone self-test: one-frame louder vocal note replaced frequent label with '%s'\n",
				     stable_renderer.stable_labels[1].label);
			return false;
		}

		for (uint64_t sequence = 11; sequence <= 14; ++sequence) {
			stable_snapshot = {};
			stable_snapshot.audio_seen = true;
			stable_snapshot.rms = 0.10f;
			stable_snapshot.sequence = sequence;
			std::snprintf(stable_snapshot.keyboard_chord.label, sizeof(stable_snapshot.keyboard_chord.label),
				      "Cmaj7");
			stable_snapshot.keyboard_chord.confidence = 0.82f;
			mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		}
		if (std::strcmp(stable_renderer.stable_labels[3].label, "C") != 0) {
			std::fprintf(stderr, "standalone self-test: expected Cmaj7 sustain to simplify to C, got '%s'\n",
				     stable_renderer.stable_labels[3].label);
			return false;
		}
		stable_snapshot = {};
		stable_snapshot.audio_seen = true;
		stable_snapshot.rms = 0.10f;
		stable_snapshot.sequence = 15;
		std::snprintf(stable_snapshot.keyboard_chord.label, sizeof(stable_snapshot.keyboard_chord.label), "G");
		stable_snapshot.keyboard_chord.confidence = 0.98f;
		mao::render_visualizer(&stable_renderer, stable_snapshot, 0.0f);
		if (std::strcmp(stable_renderer.stable_labels[3].label, "C") != 0) {
			std::fprintf(stderr, "standalone self-test: one-frame chord spike replaced stable label with '%s'\n",
				     stable_renderer.stable_labels[3].label);
			return false;
		}

		mao::VisualizerRenderer power_renderer;
		mao::resize_visualizer(&power_renderer, 960, 540);
		stable_snapshot = {};
		stable_snapshot.audio_seen = true;
		stable_snapshot.rms = 0.10f;
		stable_snapshot.sequence = 1;
		std::snprintf(stable_snapshot.keyboard_chord.label, sizeof(stable_snapshot.keyboard_chord.label),
			      "Cpow");
		stable_snapshot.keyboard_chord.confidence = 0.99f;
		mao::render_visualizer(&power_renderer, stable_snapshot, 0.0f);
		if (power_renderer.stable_labels[3].label[0]) {
			std::fprintf(stderr, "standalone self-test: power chord populated sustain as '%s'\n",
				     power_renderer.stable_labels[3].label);
			return false;
		}
	}
	{
		if (std::strcmp(kFfmpegLogLevel, "quiet") != 0) {
			std::fprintf(stderr,
				     "standalone self-test: ffmpeg loglevel should silence broken-pipe exit noise\n");
			return false;
		}
	}
	{
		Options options;
		const std::vector<std::string> devices = {"Built-in Microphone", "Monitor of Built-in Audio Analog Stereo"};
		const std::string chosen = choose_capture_device_name(devices, options);
		if (chosen != "Monitor of Built-in Audio Analog Stereo") {
			std::fprintf(stderr, "standalone self-test: expected monitor device, got '%s'\n",
				     chosen.c_str());
			return false;
		}
		options.prefer_output_monitor = false;
		if (!choose_capture_device_name(devices, options).empty()) {
			std::fprintf(stderr, "standalone self-test: default-input should not auto-select monitor\n");
			return false;
		}
		options.device_name = "Built-in Microphone";
		if (choose_capture_device_name(devices, options) != "Built-in Microphone") {
			std::fprintf(stderr, "standalone self-test: explicit device was not preserved\n");
			return false;
		}
	}
	{
		const AspectViewport wide = aspect_fit_viewport(1920, 1200, 16, 9);
		if (wide.x != 0 || wide.y != 60 || wide.w != 1920 || wide.h != 1080) {
			std::fprintf(stderr, "standalone self-test: bad wide aspect viewport\n");
			return false;
		}
		const AspectViewport tall = aspect_fit_viewport(1000, 1000, 16, 9);
		if (tall.x != 0 || tall.y != 219 || tall.w != 1000 || tall.h != 562) {
			std::fprintf(stderr, "standalone self-test: bad tall aspect viewport\n");
			return false;
		}
		const AspectViewport exact = aspect_fit_viewport(1920, 1080, 16, 9);
		if (exact.x != 0 || exact.y != 0 || exact.w != 1920 || exact.h != 1080) {
			std::fprintf(stderr, "standalone self-test: bad exact aspect viewport\n");
			return false;
		}
		const AspectSize wide_size = aspect_preserved_window_size(1920, 1200, 16, 9);
		if (wide_size.w != 1920 || wide_size.h != 1080) {
			std::fprintf(stderr, "standalone self-test: bad wide aspect window size\n");
			return false;
		}
		const AspectSize tall_size = aspect_preserved_window_size(1000, 1000, 16, 9);
		if (tall_size.w != 1000 || tall_size.h != 563) {
			std::fprintf(stderr, "standalone self-test: bad tall aspect window size\n");
			return false;
		}
		const AspectSize minimum_size = minimum_aspect_window_size(16, 9);
		if (minimum_size.w != 640 || minimum_size.h != 360) {
			std::fprintf(stderr, "standalone self-test: bad minimum aspect window size\n");
			return false;
		}
		const AspectPlacement top_wide = top_aligned_aspect_placement(0, 0, 1920, 1200, 16, 9);
		if (top_wide.x != 0 || top_wide.y != 0 || top_wide.w != 1920 || top_wide.h != 1080) {
			std::fprintf(stderr, "standalone self-test: bad top wide aspect placement\n");
			return false;
		}
		const AspectPlacement top_short = top_aligned_aspect_placement(10, 20, 1000, 300, 16, 9);
		if (top_short.x != 243 || top_short.y != 20 || top_short.w != 533 || top_short.h != 300) {
			std::fprintf(stderr, "standalone self-test: bad top short aspect placement\n");
			return false;
		}
	}
	if (key_requests_exit(SDLK_SPACE) || !key_requests_exit(SDLK_ESCAPE) || !key_requests_exit(SDLK_q)) {
		std::fprintf(stderr, "standalone self-test: bad quit key mapping\n");
		return false;
	}
	if (!run_idle_throttle_self_test())
		return false;

	std::puts("standalone self-test: ok");
	return true;
}

struct ChildProcess {
	pid_t pid = -1;
	int read_fd = -1;

	~ChildProcess()
	{
		close_process();
	}

	bool start(const std::vector<std::string> &args)
	{
		int pipe_fds[2] = {-1, -1};
		if (pipe(pipe_fds) != 0) {
			std::fprintf(stderr, "pipe failed: %s\n", std::strerror(errno));
			return false;
		}

		pid = fork();
		if (pid < 0) {
			std::fprintf(stderr, "fork failed: %s\n", std::strerror(errno));
			close(pipe_fds[0]);
			close(pipe_fds[1]);
			return false;
		}

		if (pid == 0) {
			dup2(pipe_fds[1], STDOUT_FILENO);
			close(pipe_fds[0]);
			close(pipe_fds[1]);

			std::vector<char *> child_argv;
			child_argv.reserve(args.size() + 1);
			for (const std::string &arg : args)
				child_argv.push_back(const_cast<char *>(arg.c_str()));
			child_argv.push_back(nullptr);
			execvp(child_argv[0], child_argv.data());
			_exit(127);
		}

		close(pipe_fds[1]);
		read_fd = pipe_fds[0];
		return true;
	}

	void drain_available_stdout()
	{
		if (read_fd < 0)
			return;

		for (int attempt = 0; attempt < 32; ++attempt) {
			pollfd pfd = {read_fd, POLLIN, 0};
			const int poll_result = poll(&pfd, 1, 0);
			if (poll_result <= 0 || !(pfd.revents & POLLIN))
				return;

			std::array<uint8_t, 4096> buffer = {};
			const ssize_t n = read(read_fd, buffer.data(), buffer.size());
			if (n <= 0)
				return;
		}
	}

	void close_process()
	{
		if (pid > 0) {
			int status = 0;
			pid_t result = waitpid(pid, &status, WNOHANG);
			if (result == 0) {
				(void)kill(pid, SIGTERM);
				for (int attempt = 0; attempt < 50; ++attempt) {
					drain_available_stdout();
					result = waitpid(pid, &status, WNOHANG);
					if (result != 0)
						break;
					usleep(10000);
				}
			}
			if (result == 0) {
				(void)kill(pid, SIGKILL);
				(void)waitpid(pid, &status, 0);
			}
			drain_available_stdout();
			pid = -1;
		}
		if (read_fd >= 0) {
			close(read_fd);
			read_fd = -1;
		}
	}
};

std::vector<std::string> ffmpeg_args(const Options &options)
{
	return {
		"ffmpeg", "-hide_banner", "-loglevel", kFfmpegLogLevel, "-nostdin", "-re", "-i", options.input_path,
		"-f", "f32le", "-ac", "1", "-ar", std::to_string(options.sample_rate), "-",
	};
}

std::vector<std::string> ffmpeg_pulse_monitor_args(const Options &options)
{
	return {
		"ffmpeg", "-hide_banner", "-loglevel", kFfmpegLogLevel, "-nostdin", "-f", "pulse", "-i",
		"@DEFAULT_MONITOR@", "-f", "f32le", "-ac", "1", "-ar", std::to_string(options.sample_rate), "-",
	};
}

struct FileAudioInput {
	ChildProcess child;
	int fd = -1;

	~FileAudioInput()
	{
		if (fd >= 0 && fd == child.read_fd) {
			child.close_process();
			fd = -1;
		} else if (fd >= 0 && fd != STDIN_FILENO) {
			close(fd);
			fd = -1;
		}
	}

	bool open_input(const Options &options)
	{
		if (!options.raw_f32le_path.empty()) {
			if (options.raw_f32le_path == "-") {
				fd = STDIN_FILENO;
				return true;
			}
			fd = open(options.raw_f32le_path.c_str(), O_RDONLY);
			if (fd < 0) {
				std::fprintf(stderr, "open %s failed: %s\n", options.raw_f32le_path.c_str(),
					     std::strerror(errno));
				return false;
			}
			return true;
		}

		if (!child.start(ffmpeg_args(options)))
			return false;
		fd = child.read_fd;
		return true;
	}

	bool open_pulse_monitor(const Options &options)
	{
		if (!child.start(ffmpeg_pulse_monitor_args(options)))
			return false;
		fd = child.read_fd;
		std::fprintf(stderr, "capturing speaker output through ffmpeg Pulse/PipeWire monitor\n");
		return true;
	}
};

class StandaloneAnalyzer {
public:
	explicit StandaloneAnalyzer(const Options &options)
	{
		settings_.sample_rate = options.sample_rate;
		settings_.sensitivity = options.sensitivity;
		settings_.analysis_interval_seconds = static_cast<float>(options.update_ms) / 1000.0f;
		settings_.root_window_seconds = 15.0f;
		settings_.input_mode = mao::AnalysisInputMode::FullMix;
		hop_samples_ = std::max<uint32_t>(1, options.sample_rate * options.update_ms / 1000);
		samples_until_analysis_ = hop_samples_;
		const float interval_seconds = std::max(0.001f, settings_.analysis_interval_seconds);
		silence_drain_windows_ =
			std::max<uint32_t>(1, static_cast<uint32_t>(std::ceil(kStandaloneSilenceDrainSeconds /
									     interval_seconds)));
		idle_analysis_windows_ =
			std::max<uint32_t>(1, static_cast<uint32_t>(std::ceil(kStandaloneIdleAnalysisSeconds /
									     interval_seconds)));
		source_name_ = options.source_name;
		snapshot_ = engine_.analyze(nullptr, 0, settings_, source_name_.c_str(), 0);
		snapshot_.audio_seen = false;
	}

	bool process_sample(float sample)
	{
		ring_[write_pos_] = std::clamp(sample, -2.0f, 2.0f);
		write_pos_ = (write_pos_ + 1) & (mao::kAnalysisWindow - 1);
		++audio_frames_;

		if (--samples_until_analysis_ > 0)
			return false;
		samples_until_analysis_ = hop_samples_;

		for (std::size_t i = 0; i < mao::kAnalysisWindow; ++i) {
			const std::size_t idx = (write_pos_ + i) & (mao::kAnalysisWindow - 1);
			window_[i] = ring_[idx];
		}

		double square_sum = 0.0;
		for (float value : window_)
			square_sum += static_cast<double>(value) * static_cast<double>(value);
		const float window_rms = std::sqrt(static_cast<float>(square_sum / window_.size()));
		const bool silent_window = window_rms < kStandaloneSilenceRms;
		if (silent_window) {
			consecutive_silent_windows_ = std::min<uint32_t>(consecutive_silent_windows_ + 1, 1000000);
		} else {
			consecutive_silent_windows_ = 0;
			silent_skip_windows_ = 0;
			seen_nonsilent_audio_ = true;
		}

		if (silent_window && should_skip_silent_analysis())
			return false;

		snapshot_ = engine_.analyze(window_.data(), window_.size(), settings_, source_name_.c_str(), 0);
		snapshot_.sequence = ++sequence_;
		snapshot_.audio_seen = true;
		snapshot_.audio_frames = audio_frames_;
		snapshot_.analyzed_windows = ++analyzed_windows_;
		if (silent_window)
			silent_skip_windows_ = 0;
		return true;
	}

	const mao::AnalysisSnapshot &snapshot() const
	{
		return snapshot_;
	}

	bool idle_silence() const
	{
		if (!snapshot_.audio_seen)
			return true;
		if (snapshot_.rms >= kStandaloneSilenceRms)
			return false;
		return !seen_nonsilent_audio_ || consecutive_silent_windows_ > silence_drain_windows_;
	}

private:
	bool should_skip_silent_analysis()
	{
		const bool draining_previous_audio =
			seen_nonsilent_audio_ && consecutive_silent_windows_ <= silence_drain_windows_;
		if (draining_previous_audio)
			return false;
		if (analyzed_windows_ == 0)
			return false;

		++silent_skip_windows_;
		return silent_skip_windows_ < idle_analysis_windows_;
	}

	mao::AnalysisEngine engine_;
	mao::AnalysisSettings settings_;
	std::array<float, mao::kAnalysisWindow> ring_ = {};
	std::array<float, mao::kAnalysisWindow> window_ = {};
	std::size_t write_pos_ = 0;
	uint32_t hop_samples_ = 2400;
	uint32_t samples_until_analysis_ = 2400;
	uint32_t silence_drain_windows_ = 44;
	uint32_t idle_analysis_windows_ = 20;
	uint32_t consecutive_silent_windows_ = 0;
	uint32_t silent_skip_windows_ = 0;
	uint64_t sequence_ = 0;
	uint64_t audio_frames_ = 0;
	uint64_t analyzed_windows_ = 0;
	bool seen_nonsilent_audio_ = false;
	std::string source_name_;
	mao::AnalysisSnapshot snapshot_ = {};
};

bool run_idle_throttle_self_test()
{
	Options options;
	options.sample_rate = 48000;
	options.update_ms = 50;
	options.source_name = "idle self-test";

	StandaloneAnalyzer idle(options);
	const uint32_t hop_samples = std::max<uint32_t>(1, options.sample_rate * options.update_ms / 1000);
	const int silent_windows = 60;
	for (int window = 0; window < silent_windows; ++window) {
		for (uint32_t i = 0; i < hop_samples; ++i)
			(void)idle.process_sample(0.0f);
	}

	if (idle.snapshot().analyzed_windows > 5) {
		std::fprintf(stderr,
			     "standalone self-test: idle silence analyzed too often (%llu windows after %d silent hops)\n",
			     static_cast<unsigned long long>(idle.snapshot().analyzed_windows), silent_windows);
		return false;
	}
	if (!idle.idle_silence()) {
		std::fprintf(stderr, "standalone self-test: idle silence state was not detected\n");
		return false;
	}

	const uint64_t before_sound = idle.snapshot().sequence;
	for (uint32_t i = 0; i < hop_samples; ++i)
		(void)idle.process_sample(i % 2 == 0 ? 0.02f : -0.02f);
	if (idle.snapshot().sequence <= before_sound || idle.idle_silence()) {
		std::fprintf(stderr, "standalone self-test: sound did not wake idle analyzer\n");
		return false;
	}

	return true;
}

bool feed_audio_bytes(StandaloneAnalyzer *analyzer, std::vector<uint8_t> *carry, const uint8_t *data,
		      std::size_t byte_count, bool *snapshot_changed)
{
	carry->insert(carry->end(), data, data + byte_count);
	const std::size_t usable = (carry->size() / sizeof(float)) * sizeof(float);
	for (std::size_t offset = 0; offset < usable; offset += sizeof(float)) {
		float sample = 0.0f;
		std::memcpy(&sample, carry->data() + offset, sizeof(float));
		if (!std::isfinite(sample))
			sample = 0.0f;
		if (analyzer->process_sample(sample))
			*snapshot_changed = true;
	}

	if (usable > 0)
		carry->erase(carry->begin(), carry->begin() + static_cast<std::ptrdiff_t>(usable));
	return true;
}

void print_capture_devices()
{
	const int count = SDL_GetNumAudioDevices(SDL_TRUE);
	if (count < 0) {
		std::fprintf(stderr, "SDL_GetNumAudioDevices failed: %s\n", SDL_GetError());
		return;
	}
	for (int i = 0; i < count; ++i) {
		const char *name = SDL_GetAudioDeviceName(i, SDL_TRUE);
		std::printf("%d\t%s%s\n", i, name ? name : "(unknown)",
			    name && looks_like_output_monitor_device(name) ? "\t(output monitor)" : "");
	}
}

std::vector<std::string> capture_device_names()
{
	std::vector<std::string> devices;
	const int count = SDL_GetNumAudioDevices(SDL_TRUE);
	if (count < 0)
		return devices;
	for (int i = 0; i < count; ++i) {
		const char *name = SDL_GetAudioDeviceName(i, SDL_TRUE);
		if (name && name[0])
			devices.emplace_back(name);
	}
	return devices;
}

SDL_AudioDeviceID open_capture_device(const Options &options, SDL_AudioSpec *obtained, std::string *opened_name)
{
	SDL_AudioSpec desired = {};
	desired.freq = static_cast<int>(options.sample_rate);
	desired.format = AUDIO_F32SYS;
	desired.channels = 1;
	desired.samples = 1024;
	desired.callback = nullptr;

	std::string selected = choose_capture_device_name(capture_device_names(), options);
	const char *device = selected.empty() ? nullptr : selected.c_str();
	const SDL_AudioDeviceID id =
		SDL_OpenAudioDevice(device, SDL_TRUE, &desired, obtained, SDL_AUDIO_ALLOW_FREQUENCY_CHANGE);
	if (id != 0) {
		if (opened_name)
			*opened_name = selected;
		std::fprintf(stderr, "capturing audio from %s\n", selected.empty() ? "default SDL input" : selected.c_str());
		return id;
	}

	if (!selected.empty() && options.device_name.empty()) {
		std::fprintf(stderr, "SDL_OpenAudioDevice failed for '%s': %s; falling back to default SDL input\n",
			     selected.c_str(), SDL_GetError());
		const SDL_AudioDeviceID fallback =
			SDL_OpenAudioDevice(nullptr, SDL_TRUE, &desired, obtained, SDL_AUDIO_ALLOW_FREQUENCY_CHANGE);
		if (fallback != 0) {
			if (opened_name)
				*opened_name = "";
			std::fprintf(stderr, "capturing audio from default SDL input\n");
			return fallback;
		}
	}

	if (id == 0)
		std::fprintf(stderr, "SDL_OpenAudioDevice failed: %s\n", SDL_GetError());
	return 0;
}

struct SdlSession {
	SDL_Window *window = nullptr;
	SDL_Renderer *renderer = nullptr;
	SDL_Texture *texture = nullptr;
	SDL_AudioDeviceID capture = 0;
	int last_aspect_set_w = 0;
	int last_aspect_set_h = 0;

	~SdlSession()
	{
		if (capture)
			SDL_CloseAudioDevice(capture);
		if (texture)
			SDL_DestroyTexture(texture);
		if (renderer)
			SDL_DestroyRenderer(renderer);
		if (window)
			SDL_DestroyWindow(window);
		SDL_Quit();
	}
};

bool create_window(SdlSession *session, const Options &options)
{
	char title[128] = {};
	std::snprintf(title, sizeof(title), "Music Analyzer Standalone %s", MAO_STANDALONE_VERSION);
	AspectPlacement placement{SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
				  static_cast<int>(options.width), static_cast<int>(options.height)};
	SDL_Rect bounds = {};
	if (SDL_GetDisplayUsableBounds(0, &bounds) == 0 || SDL_GetDisplayBounds(0, &bounds) == 0) {
		placement = top_aligned_aspect_placement(bounds.x, bounds.y, bounds.w, bounds.h,
							 static_cast<int>(options.width),
							 static_cast<int>(options.height));
	}

	session->window = SDL_CreateWindow(title, placement.x, placement.y, placement.w, placement.h,
					   SDL_WINDOW_RESIZABLE);
	if (!session->window) {
		std::fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
		return false;
	}
	session->last_aspect_set_w = placement.w;
	session->last_aspect_set_h = placement.h;

	const AspectSize minimum_size =
		minimum_aspect_window_size(static_cast<int>(options.width), static_cast<int>(options.height));
	SDL_SetWindowMinimumSize(session->window, minimum_size.w, minimum_size.h);

	session->renderer = SDL_CreateRenderer(session->window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
	if (!session->renderer)
		session->renderer = SDL_CreateRenderer(session->window, -1, SDL_RENDERER_SOFTWARE);
	if (!session->renderer) {
		std::fprintf(stderr, "SDL_CreateRenderer failed: %s\n", SDL_GetError());
		return false;
	}
	return true;
}

void preserve_window_aspect(SdlSession *session, int window_w, int window_h, int aspect_w, int aspect_h)
{
	if (!session || !session->window)
		return;

	if (window_w <= 0 || window_h <= 0)
		SDL_GetWindowSize(session->window, &window_w, &window_h);
	const AspectSize corrected = aspect_preserved_window_size(window_w, window_h, aspect_w, aspect_h);
	if (std::abs(corrected.w - window_w) <= 1 && std::abs(corrected.h - window_h) <= 1)
		return;
	if (corrected.w == session->last_aspect_set_w && corrected.h == session->last_aspect_set_h)
		return;

	session->last_aspect_set_w = corrected.w;
	session->last_aspect_set_h = corrected.h;
	SDL_SetWindowSize(session->window, corrected.w, corrected.h);
}

void restore_window_to_display_aspect(SdlSession *session, int aspect_w, int aspect_h)
{
	if (!session || !session->window)
		return;

	SDL_Rect bounds = {};
	const int display_index = std::max(0, SDL_GetWindowDisplayIndex(session->window));
	if (SDL_GetDisplayUsableBounds(display_index, &bounds) != 0 &&
	    SDL_GetDisplayBounds(display_index, &bounds) != 0) {
		SDL_RestoreWindow(session->window);
		preserve_window_aspect(session, 0, 0, aspect_w, aspect_h);
		return;
	}

	const AspectPlacement fit = top_aligned_aspect_placement(bounds.x, bounds.y, bounds.w, bounds.h,
								aspect_w, aspect_h);
	SDL_SetWindowFullscreen(session->window, 0);
	SDL_RestoreWindow(session->window);
	session->last_aspect_set_w = fit.w;
	session->last_aspect_set_h = fit.h;
	SDL_SetWindowSize(session->window, fit.w, fit.h);
	SDL_SetWindowPosition(session->window, fit.x, fit.y);
}

bool ensure_texture(SdlSession *session, const mao::VisualizerRenderer &visualizer)
{
	if (session->texture) {
		uint32_t format = 0;
		int access = 0;
		int width = 0;
		int height = 0;
		SDL_QueryTexture(session->texture, &format, &access, &width, &height);
		if (static_cast<uint32_t>(width) == visualizer.width && static_cast<uint32_t>(height) == visualizer.height)
			return true;
		SDL_DestroyTexture(session->texture);
		session->texture = nullptr;
	}

	session->texture = SDL_CreateTexture(session->renderer, SDL_PIXELFORMAT_RGBA32, SDL_TEXTUREACCESS_STREAMING,
					     static_cast<int>(visualizer.width), static_cast<int>(visualizer.height));
	if (!session->texture)
		std::fprintf(stderr, "SDL_CreateTexture failed: %s\n", SDL_GetError());
	return session->texture != nullptr;
}

void present(SdlSession *session, const mao::VisualizerRenderer &visualizer)
{
	if (!ensure_texture(session, visualizer))
		return;

	SDL_UpdateTexture(session->texture, nullptr, visualizer.pixels.data(), static_cast<int>(visualizer.width * 4));
	int output_w = static_cast<int>(visualizer.width);
	int output_h = static_cast<int>(visualizer.height);
	if (SDL_GetRendererOutputSize(session->renderer, &output_w, &output_h) != 0) {
		output_w = static_cast<int>(visualizer.width);
		output_h = static_cast<int>(visualizer.height);
	}
	const AspectViewport viewport =
		aspect_fit_viewport(output_w, output_h, static_cast<int>(visualizer.width), static_cast<int>(visualizer.height));
	const SDL_Rect destination{viewport.x, viewport.y, viewport.w, viewport.h};
	SDL_SetRenderDrawColor(session->renderer, 0, 0, 0, 255);
	SDL_RenderClear(session->renderer);
	SDL_RenderCopy(session->renderer, session->texture, nullptr, &destination);
	SDL_RenderPresent(session->renderer);
}

} // namespace

int main(int argc, char **argv)
{
	Options options;
	if (!parse_options(argc, argv, &options)) {
		print_usage(argv[0]);
		return 2;
	}
	if (options.show_version) {
		std::puts(MAO_STANDALONE_VERSION);
		return 0;
	}
	if (options.self_test)
		return run_self_test() ? 0 : 1;

	SDL_SetMainReady();
	const uint32_t sdl_init_flags = options.list_devices ? SDL_INIT_AUDIO : (SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_EVENTS);
	if (SDL_Init(sdl_init_flags) != 0) {
		std::fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
		return 1;
	}

	if (options.list_devices) {
		print_capture_devices();
		SDL_Quit();
		return 0;
	}

	SdlSession session;
	FileAudioInput file_input;
	SDL_AudioSpec capture_spec = {};
	const bool file_mode = !options.input_path.empty() || !options.raw_f32le_path.empty();
	bool stream_fd_mode = file_mode;
	if (file_mode) {
		if (!file_input.open_input(options))
			return 1;
		if (options.source_name == "STANDALONE")
			options.source_name = "STANDALONE FILE";
	} else {
		const std::string sdl_monitor = choose_capture_device_name(capture_device_names(), options);
		if (options.prefer_output_monitor && sdl_monitor.empty()) {
			stream_fd_mode = file_input.open_pulse_monitor(options);
			if (stream_fd_mode && options.source_name == "STANDALONE")
				options.source_name = "SPEAKER MONITOR";
		}

		if (!stream_fd_mode) {
			std::string opened_capture_name;
			session.capture = open_capture_device(options, &capture_spec, &opened_capture_name);
			if (!session.capture)
				return 1;
			options.sample_rate = static_cast<uint32_t>(capture_spec.freq);
			if (options.source_name == "STANDALONE")
				options.source_name = opened_capture_name.empty() ? "SDL CAPTURE DEFAULT" : opened_capture_name;
			SDL_PauseAudioDevice(session.capture, 0);
		}
	}

	if (!create_window(&session, options))
		return 1;

	mao::VisualizerRenderer visualizer;
	mao::resize_visualizer(&visualizer, options.width, options.height);

	StandaloneAnalyzer analyzer(options);
	mao::render_visualizer(&visualizer, analyzer.snapshot(), 0.0f);
	present(&session, visualizer);

	bool running = true;
	bool eof = false;
	uint64_t rendered_sequence = analyzer.snapshot().sequence;
	float snapshot_age = 0.0f;
	std::vector<uint8_t> carry;
	auto last_tick = std::chrono::steady_clock::now();
	auto last_present = last_tick;
	const auto frame_interval =
		std::chrono::duration<float>(1.0f / static_cast<float>(std::max<uint32_t>(1, options.fps)));
	const auto idle_frame_interval = std::chrono::duration<float>(kStandaloneIdleFrameSeconds);

	while (running) {
		SDL_Event event;
		bool window_changed = false;
		while (SDL_PollEvent(&event)) {
			if (event.type == SDL_QUIT)
				running = false;
			else if (event.type == SDL_KEYDOWN && key_requests_exit(event.key.keysym.sym))
				running = false;
			else if (event.type == SDL_WINDOWEVENT) {
				switch (event.window.event) {
				case SDL_WINDOWEVENT_MAXIMIZED:
					restore_window_to_display_aspect(&session, static_cast<int>(visualizer.width),
									 static_cast<int>(visualizer.height));
					window_changed = true;
					break;
				case SDL_WINDOWEVENT_RESIZED:
				case SDL_WINDOWEVENT_SIZE_CHANGED:
					if (SDL_GetWindowFlags(session.window) &
					    (SDL_WINDOW_MAXIMIZED | SDL_WINDOW_FULLSCREEN |
					     SDL_WINDOW_FULLSCREEN_DESKTOP)) {
						restore_window_to_display_aspect(&session, static_cast<int>(visualizer.width),
										 static_cast<int>(visualizer.height));
					} else {
						preserve_window_aspect(&session, event.window.data1, event.window.data2,
								       static_cast<int>(visualizer.width),
								       static_cast<int>(visualizer.height));
					}
					window_changed = true;
					break;
				default:
					break;
				}
			}
		}

		const auto now = std::chrono::steady_clock::now();
		const float seconds = std::chrono::duration<float>(now - last_tick).count();
		last_tick = now;
		snapshot_age += seconds;
		const bool history_active = mao::advance_visualizer_drum_history(&visualizer, seconds);

		bool snapshot_changed = false;
		if (stream_fd_mode && !eof) {
			pollfd pfd = {file_input.fd, POLLIN, 0};
			const int poll_result = poll(&pfd, 1, 4);
			if (poll_result > 0 && (pfd.revents & POLLIN)) {
				std::array<uint8_t, 8192> bytes = {};
				const ssize_t n = read(file_input.fd, bytes.data(), bytes.size());
				if (n > 0) {
					feed_audio_bytes(&analyzer, &carry, bytes.data(), static_cast<std::size_t>(n),
							 &snapshot_changed);
				} else if (n == 0) {
					eof = true;
				} else if (errno != EINTR && errno != EAGAIN) {
					std::fprintf(stderr, "audio read failed: %s\n", std::strerror(errno));
					eof = true;
				}
			} else if (poll_result > 0 && (pfd.revents & (POLLHUP | POLLERR | POLLNVAL))) {
				eof = true;
			}
		} else if (!stream_fd_mode && session.capture) {
			const uint32_t queued = SDL_GetQueuedAudioSize(session.capture);
			if (queued >= sizeof(float)) {
				std::vector<uint8_t> bytes(std::min<uint32_t>(queued, 65536));
				const uint32_t got = SDL_DequeueAudio(session.capture, bytes.data(),
								      static_cast<uint32_t>(bytes.size()));
				if (got > 0)
					feed_audio_bytes(&analyzer, &carry, bytes.data(), got, &snapshot_changed);
			}
		}

		bool should_present = window_changed;
		const bool idle_visual = analyzer.idle_silence() && !history_active;
		const auto present_interval = idle_visual ? idle_frame_interval : frame_interval;
		if (snapshot_changed || analyzer.snapshot().sequence != rendered_sequence) {
			snapshot_age = 0.0f;
			mao::append_visualizer_drum_hits(&visualizer, analyzer.snapshot());
			mao::render_visualizer(&visualizer, analyzer.snapshot(), snapshot_age);
			rendered_sequence = analyzer.snapshot().sequence;
			should_present = true;
		} else if (should_present || std::chrono::steady_clock::now() - last_present >= present_interval) {
			mao::render_visualizer(&visualizer, analyzer.snapshot(), snapshot_age);
			should_present = true;
		}

		if (should_present) {
			present(&session, visualizer);
			last_present = std::chrono::steady_clock::now();
		}

		if (eof && !options.hold_on_eof)
			break;
		SDL_Delay(2);
	}

	return 0;
}
