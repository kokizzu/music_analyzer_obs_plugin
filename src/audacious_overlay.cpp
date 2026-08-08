#include "audacious_overlay.hpp"
#include "audacious_poll_schedule.hpp"
#include "audacious_title.hpp"
#include "unicode_title_renderer.hpp"
#include "visualizer_renderer.hpp"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

namespace mao {
namespace {

constexpr auto kBitmapScrollInterval = std::chrono::milliseconds(250);
constexpr int kTitleStartX = 316;
constexpr int kTitleHeight = 26;
constexpr int kSilentIndicatorSize = 34;
constexpr int kSilentIndicatorRightMargin = 18;
constexpr int kTitleToSilentIndicatorGap = 8;
constexpr int kSilentIndicatorReserve =
	kSilentIndicatorSize + kSilentIndicatorRightMargin + kTitleToSilentIndicatorGap;
constexpr int kBitmapCharacterWidth = 18; // scale 3: 6 pixels per glyph column.

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

std::string bitmap_ascii_fallback(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	for (std::size_t i = 0; i < value.size();) {
		const unsigned char c = static_cast<unsigned char>(value[i]);
		if (c < 0x80) {
			output.push_back(c >= 0x20 && c != 0x7f ? static_cast<char>(c) : ' ');
			++i;
			continue;
		}

		output.push_back('?');
		++i;
		while (i < value.size() && (static_cast<unsigned char>(value[i]) & 0xc0) == 0x80)
			++i;
	}
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

std::string read_audacious_title_tuple()
{
	std::string value = read_command_text("audtool current-song-tuple-data title 2>/dev/null");
	if (!value.empty())
		return value;
	return read_command_text("audtool --current-song-tuple-data title 2>/dev/null");
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
			const auto poll_started = std::chrono::steady_clock::now();
			AudaciousNowPlaying next;
			const std::string tuple_title = read_audacious_title_tuple();
			if (!tuple_title.empty()) {
				// The Title tuple already contains the complete user-facing
				// value. Artist/Album may be transport labels such as
				// "music-yt" and "flac_output", so never prepend them.
				next.running = true;
				next.song_title = clean_audacious_title(tuple_title);
			} else {
				// Window-title fallback accepts:
				// Artist - Album - Title (presentation tag) [youtubeID]
				// and extracts only Title [youtubeID].
				next = read_audacious_now_playing();
				next.song_title = clean_audacious_title(next.song_title);
			}

			{
				std::lock_guard<std::mutex> lock(mutex_);
				if (next.song_title != now_playing_.song_title || next.running != now_playing_.running)
					title_started_ = std::chrono::steady_clock::now();
				now_playing_ = next;
				initialized_ = true;
			}

			const auto poll_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
				std::chrono::steady_clock::now() - poll_started);
			std::unique_lock<std::mutex> lock(mutex_);
			if (wake_.wait_for(lock, audacious_title_poll_wait(poll_elapsed), [&]() { return stop_; }))
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

AudaciousDisplaySnapshot audacious_overlay_snapshot()
{
	static AudaciousOverlayPoller poller;
	return poller.display_snapshot();
}

} // namespace

void render_visualizer_with_audacious(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot,
				      float snapshot_age)
{
#if defined(__linux__)
	const AudaciousDisplaySnapshot title_snapshot = audacious_overlay_snapshot();

	AnalysisSnapshot display_snapshot = snapshot;
	display_snapshot.source[0] = ' ';
	display_snapshot.source[1] = '\0';
	render_visualizer(visualizer, display_snapshot, snapshot_age);

	const int title_y = visualizer->layout_mode == VisualizerLayoutMode::BassGuitar ? 14 : 12;
	const int available_width =
		static_cast<int>(visualizer->width) - kTitleStartX - kSilentIndicatorReserve;
	const float elapsed_seconds = std::max(
		0.0f, std::chrono::duration<float>(std::chrono::steady_clock::now() - title_snapshot.started).count());

	if (available_width > 0 &&
	    render_unicode_header_title(visualizer, title_snapshot.text, kTitleStartX, title_y, available_width,
					kTitleHeight, elapsed_seconds))
		return;

	// Runtime Pango/Cairo is optional. If unavailable, rerender the unchanged
	// analyzer with a bitmap marquee sized to the exact available header width.
	display_snapshot = snapshot;
	const std::size_t fallback_width = static_cast<std::size_t>(
		std::max(1, available_width > 0 ? available_width / kBitmapCharacterWidth : 1));
	const auto elapsed = std::chrono::steady_clock::now() - title_snapshot.started;
	const auto step_count =
		std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count() /
		kBitmapScrollInterval.count();
	const std::string fallback_window =
		make_scrolling_title(title_snapshot.text, fallback_width,
				     static_cast<std::size_t>(std::max<int64_t>(0, step_count)));
	const std::string fallback = bitmap_ascii_fallback(fallback_window);
	std::snprintf(display_snapshot.source, sizeof(display_snapshot.source), "%s", fallback.c_str());
	render_visualizer(visualizer, display_snapshot, snapshot_age);
#else
	render_visualizer(visualizer, snapshot, snapshot_age);
#endif
}

} // namespace mao
