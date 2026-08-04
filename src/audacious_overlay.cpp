#include "audacious_title.hpp"
#include "visualizer_renderer.hpp"

#include <chrono>
#include <cstdio>
#include <mutex>
#include <string>

namespace mao {
namespace {

constexpr std::size_t kOverlayTitleWidth = 38;
constexpr auto kAudaciousPollInterval = std::chrono::seconds(1);
constexpr auto kScrollInterval = std::chrono::milliseconds(250);

struct AudaciousOverlayState {
	std::mutex mutex;
	std::chrono::steady_clock::time_point last_poll = {};
	std::chrono::steady_clock::time_point last_scroll = {};
	AudaciousNowPlaying now_playing;
	std::string last_song_title;
	std::size_t scroll_offset = 0;
	bool initialized = false;
};

AudaciousOverlayState g_audacious_overlay;

std::string audacious_overlay_text()
{
	std::lock_guard<std::mutex> lock(g_audacious_overlay.mutex);
	const auto now = std::chrono::steady_clock::now();
	if (!g_audacious_overlay.initialized || now - g_audacious_overlay.last_poll >= kAudaciousPollInterval) {
		g_audacious_overlay.now_playing = read_audacious_now_playing();
		g_audacious_overlay.last_poll = now;
		g_audacious_overlay.initialized = true;
		if (g_audacious_overlay.now_playing.song_title != g_audacious_overlay.last_song_title) {
			g_audacious_overlay.last_song_title = g_audacious_overlay.now_playing.song_title;
			g_audacious_overlay.scroll_offset = 0;
			g_audacious_overlay.last_scroll = now;
		}
	}

	if (!g_audacious_overlay.now_playing.running)
		return "AUDACIOUS NOT RUNNING";
	if (g_audacious_overlay.now_playing.song_title.empty())
		return "AUDACIOUS TITLE UNAVAILABLE";

	if (g_audacious_overlay.last_scroll.time_since_epoch().count() == 0)
		g_audacious_overlay.last_scroll = now;
	const auto elapsed = now - g_audacious_overlay.last_scroll;
	const auto steps = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count() /
			   kScrollInterval.count();
	if (steps > 0) {
		g_audacious_overlay.scroll_offset += static_cast<std::size_t>(steps);
		g_audacious_overlay.last_scroll += kScrollInterval * steps;
	}

	return make_scrolling_title(g_audacious_overlay.now_playing.song_title, kOverlayTitleWidth,
				    g_audacious_overlay.scroll_offset);
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
