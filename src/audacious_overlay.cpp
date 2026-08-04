#include "audacious_overlay.hpp"
#include "audacious_title.hpp"
#include "visualizer_renderer.hpp"

#include <obs-module.h>
#include <obs.h>
#include <graphics/graphics.h>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

namespace mao {
namespace {

constexpr auto kAudaciousPollInterval = std::chrono::seconds(1);
constexpr float kTitleStartX = 316.0f;
constexpr float kTitleTopY = 12.0f;
constexpr float kTitleTargetHeight = 24.0f;
constexpr float kTitleRightMargin = 28.0f;
constexpr float kTitleScrollPixelsPerSecond = 52.0f;
constexpr float kTitleScrollGap = 80.0f;

std::string sanitize_audacious_tuple_text(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	bool pending_space = false;
	for (const unsigned char c : value) {
		if (c < 0x80 && std::isspace(c)) {
			pending_space = !output.empty();
			continue;
		}
		if (c < 0x20 || c == 0x7f)
			continue;
		if (pending_space)
			output.push_back(' ');
		output.push_back(static_cast<char>(c));
		pending_space = false;
	}

	while (!output.empty() && output.back() == ' ')
		output.pop_back();
	if (output == "(null)" || output == "null")
		return {};
	return output;
}

std::string read_command_text(const char *command)
{
#if defined(__linux__)
	FILE *pipe = popen(command, "r");
	if (!pipe)
		return {};

	std::string output;
	char buffer[512] = {};
	while (std::fgets(buffer, sizeof(buffer), pipe)) {
		if (output.size() >= 4096)
			break;
		output += buffer;
	}
	pclose(pipe);
	return sanitize_audacious_tuple_text(output);
#else
	(void)command;
	return {};
#endif
}

std::string read_audacious_tuple_field(const char *field)
{
	char command[160] = {};
	std::snprintf(command, sizeof(command), "audtool current-song-tuple-data %s 2>/dev/null", field);
	std::string value = read_command_text(command);
	if (!value.empty())
		return value;

	std::snprintf(command, sizeof(command), "audtool --current-song-tuple-data %s 2>/dev/null", field);
	return read_command_text(command);
}

std::string resolve_unicode_font_face()
{
#if defined(__linux__)
	std::string face = read_command_text("fc-match -f '%{family[0]}' 'sans-serif:lang=ja' 2>/dev/null");
	const std::size_t comma = face.find(',');
	if (comma != std::string::npos)
		face.resize(comma);
	face = trim_audacious_field(face);
	if (!face.empty())
		return face;
#endif
	return "Sans Serif";
}

struct AudaciousDisplaySnapshot {
	std::string text;
	std::chrono::steady_clock::time_point started = std::chrono::steady_clock::now();
};

class AudaciousOverlayPoller {
public:
	AudaciousOverlayPoller() : worker_(&AudaciousOverlayPoller::worker_loop, this) {}

	~AudaciousOverlayPoller()
	{
		{
			std::lock_guard<std::mutex> lock(mutex_);
			stop_ = true;
		}
		wake_.notify_one();
		if (worker_.joinable())
			worker_.join();
	}

	AudaciousDisplaySnapshot display_snapshot() const
	{
		std::lock_guard<std::mutex> lock(mutex_);
		AudaciousDisplaySnapshot snapshot;
		snapshot.started = title_started_;
		if (!initialized_)
			snapshot.text = "AUDACIOUS CHECKING";
		else if (!now_playing_.running)
			snapshot.text = "AUDACIOUS NOT RUNNING";
		else if (now_playing_.song_title.empty())
			snapshot.text = "AUDACIOUS TITLE UNAVAILABLE";
		else
			snapshot.text = now_playing_.song_title;
		return snapshot;
	}

private:
	void worker_loop()
	{
		for (;;) {
			AudaciousNowPlaying next;
			const std::string tuple_title = read_audacious_tuple_field("title");
			if (!tuple_title.empty()) {
				const std::string tuple_artist = read_audacious_tuple_field("artist");
				next.running = true;
				next.song_title = format_audacious_artist_title(tuple_artist, tuple_title);
			} else {
				next = read_audacious_now_playing();
				next.song_title = format_audacious_artist_title({}, next.song_title);
			}

			{
				std::lock_guard<std::mutex> lock(mutex_);
				if (next.song_title != now_playing_.song_title || next.running != now_playing_.running)
					title_started_ = std::chrono::steady_clock::now();
				now_playing_ = next;
				initialized_ = true;
			}

			std::unique_lock<std::mutex> lock(mutex_);
			if (wake_.wait_for(lock, kAudaciousPollInterval, [&]() { return stop_; }))
				return;
		}
	}

	mutable std::mutex mutex_;
	std::condition_variable wake_;
	std::thread worker_;
	AudaciousNowPlaying now_playing_;
	std::chrono::steady_clock::time_point title_started_ = std::chrono::steady_clock::now();
	bool initialized_ = false;
	bool stop_ = false;
};

AudaciousOverlayPoller &audacious_poller()
{
	static AudaciousOverlayPoller poller;
	return poller;
}

obs_source_t *create_unicode_text_source()
{
	obs_data_t *settings = obs_data_create();
	obs_data_t *font = obs_data_create();
	const std::string face = resolve_unicode_font_face();
	obs_data_set_string(font, "face", face.c_str());
	obs_data_set_string(font, "style", "");
	obs_data_set_int(font, "size", 32);
	obs_data_set_int(font, "flags", 0);
	obs_data_set_obj(settings, "font", font);
	obs_data_set_string(settings, "text", "AUDACIOUS CHECKING");
	obs_data_set_bool(settings, "from_file", false);
	obs_data_set_bool(settings, "antialiasing", true);
	obs_data_set_bool(settings, "word_wrap", false);
	obs_data_set_bool(settings, "outline", false);
	obs_data_set_bool(settings, "drop_shadow", false);
	obs_data_set_int(settings, "custom_width", 0);
	obs_data_set_int(settings, "color1", 0xffffffff);
	obs_data_set_int(settings, "color2", 0xffffffff);

	obs_source_t *source = obs_source_create_private("text_ft2_source", nullptr, settings);
	obs_data_release(font);
	obs_data_release(settings);
	if (!source)
		blog(LOG_WARNING, "Music Analyzer: OBS FreeType text source is unavailable; Unicode song title is disabled");
	return source;
}

void draw_text_source(obs_source_t *source, float x, float y, float scale)
{
	gs_matrix_push();
	gs_matrix_translate3f(x, y, 0.0f);
	gs_matrix_scale3f(scale, scale, 1.0f);
	obs_source_video_render(source);
	gs_matrix_pop();
}

} // namespace

struct AudaciousUnicodeOverlay {
	obs_source_t *text_source = nullptr;
	std::string text;
	std::chrono::steady_clock::time_point started = std::chrono::steady_clock::now();
};

namespace {

struct GlobalOverlayHolder {
	AudaciousUnicodeOverlay *overlay = create_audacious_unicode_overlay(nullptr);
	~GlobalOverlayHolder() { destroy_audacious_unicode_overlay(overlay); }
};

AudaciousUnicodeOverlay *global_audacious_unicode_overlay()
{
	static GlobalOverlayHolder holder;
	return holder.overlay;
}

} // namespace

void render_visualizer_with_audacious(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot,
				      float snapshot_age)
{
#if defined(__linux__)
	tick_audacious_unicode_overlay(global_audacious_unicode_overlay());
	AnalysisSnapshot display_snapshot = snapshot;
	display_snapshot.source[0] = ' ';
	display_snapshot.source[1] = '\0';
	render_visualizer(visualizer, display_snapshot, snapshot_age);
#else
	render_visualizer(visualizer, snapshot, snapshot_age);
#endif
}

AudaciousUnicodeOverlay *create_audacious_unicode_overlay(obs_source_t *)
{
#if defined(__linux__)
	auto *overlay = new AudaciousUnicodeOverlay();
	overlay->text_source = create_unicode_text_source();
	tick_audacious_unicode_overlay(overlay);
	return overlay;
#else
	return nullptr;
#endif
}

void destroy_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay)
{
	if (!overlay)
		return;
	if (overlay->text_source)
		obs_source_release(overlay->text_source);
	delete overlay;
}

void tick_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay)
{
	if (!overlay || !overlay->text_source)
		return;
	const AudaciousDisplaySnapshot snapshot = audacious_poller().display_snapshot();
	if (snapshot.text == overlay->text)
		return;

	overlay->text = snapshot.text;
	overlay->started = snapshot.started;
	obs_data_t *settings = obs_source_get_settings(overlay->text_source);
	obs_data_set_string(settings, "text", overlay->text.c_str());
	obs_source_update(overlay->text_source, settings);
	obs_data_release(settings);
}

void render_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay, uint32_t width, uint32_t)
{
	if (!overlay || !overlay->text_source || width <= static_cast<uint32_t>(kTitleStartX + kTitleRightMargin))
		return;

	const uint32_t source_width = obs_source_get_width(overlay->text_source);
	const uint32_t source_height = obs_source_get_height(overlay->text_source);
	if (source_width == 0 || source_height == 0)
		return;

	const float scale = kTitleTargetHeight / static_cast<float>(source_height);
	const float scaled_width = static_cast<float>(source_width) * scale;
	const float available_width = static_cast<float>(width) - kTitleStartX - kTitleRightMargin;
	const gs_rect clip = {static_cast<int>(kTitleStartX), 8, static_cast<int>(available_width), 34};
	gs_set_scissor_rect(&clip);

	if (scaled_width > available_width) {
		const float elapsed = std::chrono::duration<float>(std::chrono::steady_clock::now() - overlay->started).count();
		const float cycle_width = scaled_width + kTitleScrollGap;
		const float offset =
			std::fmod(std::max(0.0f, elapsed) * kTitleScrollPixelsPerSecond, cycle_width);
		draw_text_source(overlay->text_source, kTitleStartX - offset, kTitleTopY, scale);
		draw_text_source(overlay->text_source, kTitleStartX - offset + cycle_width, kTitleTopY, scale);
	} else {
		draw_text_source(overlay->text_source, kTitleStartX, kTitleTopY, scale);
	}

	gs_set_scissor_rect(nullptr);
}

void audacious_obs_source_draw(gs_texture_t *texture, uint32_t x, uint32_t y, uint32_t width, uint32_t height,
			      bool flip)
{
	::obs_source_draw(texture, x, y, width, height, flip);
#if defined(__linux__)
	render_audacious_unicode_overlay(global_audacious_unicode_overlay(), width, height);
#endif
}

} // namespace mao
