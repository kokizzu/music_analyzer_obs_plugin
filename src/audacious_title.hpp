#pragma once

#include <cctype>
#include <cstddef>
#include <string>

namespace mao {

struct AudaciousNowPlaying {
	bool running = false;
	std::string window_title;
	std::string song_title;
};

inline std::string format_audacious_artist_title(std::string artist, std::string title)
{
	const auto trim_field = [](std::string value) {
		std::size_t begin = 0;
		while (begin < value.size() && std::isspace(static_cast<unsigned char>(value[begin])))
			++begin;
		std::size_t end = value.size();
		while (end > begin && std::isspace(static_cast<unsigned char>(value[end - 1])))
			--end;
		return value.substr(begin, end - begin);
	};

	artist = trim_field(artist);
	title = trim_field(title);
	if (artist == "(null)" || artist == "null")
		artist.clear();
	if (title == "(null)" || title == "null")
		title.clear();

	const std::size_t parenthetical = title.find(" (");
	if (parenthetical != std::string::npos)
		title = trim_field(title.substr(0, parenthetical));

	if (artist.empty())
		return title;
	if (title.empty())
		return artist;
	return artist + " - " + title;
}

std::string find_audacious_window_title(const std::string &wmctrl_output);
std::string extract_audacious_song_title(const std::string &titlebar);
std::string make_scrolling_title(const std::string &title, std::size_t width, std::size_t offset);
AudaciousNowPlaying read_audacious_now_playing();

} // namespace mao
