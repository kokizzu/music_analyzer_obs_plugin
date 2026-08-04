#pragma once

#include <cstddef>
#include <string>

namespace mao {

struct AudaciousNowPlaying {
	bool running = false;
	std::string window_title;
	std::string song_title;
};

std::string find_audacious_window_title(const std::string &wmctrl_output);
std::string extract_audacious_song_title(const std::string &titlebar);
std::string make_scrolling_title(const std::string &title, std::size_t width, std::size_t offset);
AudaciousNowPlaying read_audacious_now_playing();

} // namespace mao
