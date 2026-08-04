#include "audacious_title.hpp"
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

constexpr std::size_t kOverlayTitleWidth = 34;
constexpr auto kAudaciousPollInterval = std::chrono::seconds(1);
constexpr auto kScrollInterval = std::chrono::milliseconds(250);

std::string sanitize_audacious_tuple_text(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	bool pending_space = false;
	for (std::size_t i = 0; i < value.size();) {
		const unsigned char c = static_cast<unsigned char>(value[i]);
		if (c < 0x80) {
			if (std::isspace(c)) {
				pending_space = !output.empty();
			} else if (c >= 0x20 && c != 0x7f) {
				if (pending_space)
					output.push_back(' ');
				output.push_back(static_cast<char>(c));
				pending_space = false;
			}
			++i;
			continue;
		}

		if (pending_space)
			output.push_back(' ');
		output.push_back('?');
		pending_space = false;
		++i;
		while (i < value.size() && (static_cast<unsigned char>(value[i]) & 0xc0) == 0x80)
			++i;
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

	std::string display_text() const
	{
		AudaciousNowPlaying current;
		std::chrono::steady_clock::time_point title_started;
		bool initialized = false;
		{
			std::lock_guard<std::mutex> lock(mutex_);
			current = now_playing_;
			title_started = title_started_;
			initialized = initialized_;
		}

		if (!initialized)
			return "AUDACIOUS CHECKING";
		if (!current.running)
			return "AUDACIOUS NOT RUNNING";
		if (current.song_title.empty())
			return "AUDACIOUS TITLE UNAVAILABLE";
		if (current.song_title.size() <= kOverlayTitleWidth)
			return current.song_title;

		const auto elapsed = std::chrono::steady_clock::now() - title_started;
		const auto step_count = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count() /
					kScrollInterval.count();
		return make_scrolling_title(current.song_title, kOverlayTitleWidth,
					    static_cast<std::size_t>(std::max<int64_t>(0, step_count)));
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

std::string audacious_overlay_text()
{
	static AudaciousOverlayPoller poller;
	return poller.display_text();
}

} // namespace

void render_visualizer_with_audacious(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot,
				      float snapshot_age)
{
#if defined(__linux__)
	AnalysisSnapshot display_snapshot = snapshot;
	const std::string title = audacious_overlay_text();
	std::snprintf(display_snapshot.source, sizeof(display_snapshot.source), "%s", title.c_str());
	render_visualizer(visualizer, display_snapshot, snapshot_age);
#else
	render_visualizer(visualizer, snapshot, snapshot_age);
#endif
}

} // namespace mao
