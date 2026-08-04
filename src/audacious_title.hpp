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

inline std::string trim_audacious_field(std::string value)
{
	std::size_t begin = 0;
	while (begin < value.size() && std::isspace(static_cast<unsigned char>(value[begin])))
		++begin;
	std::size_t end = value.size();
	while (end > begin && std::isspace(static_cast<unsigned char>(value[end - 1])))
		--end;
	return value.substr(begin, end - begin);
}

inline std::string normalize_audacious_qualifier(const std::string &value)
{
	std::string normalized;
	bool pending_space = false;
	for (const unsigned char c : value) {
		if (c < 0x80 && std::isalnum(c)) {
			if (pending_space && !normalized.empty())
				normalized.push_back(' ');
			normalized.push_back(static_cast<char>(std::tolower(c)));
			pending_space = false;
		} else if (!normalized.empty()) {
			pending_space = true;
		}
	}
	return normalized;
}

inline bool is_removable_audacious_qualifier(const std::string &value)
{
	const std::string qualifier = normalize_audacious_qualifier(value);
	return qualifier == "live" || qualifier == "live video" || qualifier == "live performance" ||
	       qualifier == "music video" || qualifier == "lyric video" || qualifier == "lyrics video" ||
	       qualifier == "official video" || qualifier == "official music video" ||
	       qualifier == "official lyric video" || qualifier == "official lyrics video" ||
	       qualifier == "official audio" || qualifier == "official visualizer" || qualifier == "official mv" ||
	       qualifier == "official live" || qualifier == "official live video" ||
	       qualifier == "official performance" || qualifier == "official live performance";
}

inline std::string strip_audacious_presentation_qualifiers(std::string title)
{
	for (std::size_t pos = 0; pos < title.size();) {
		const char open = title[pos];
		const char close = open == '(' ? ')' : open == '[' ? ']' : '\0';
		if (!close) {
			++pos;
			continue;
		}

		const std::size_t end = title.find(close, pos + 1);
		if (end == std::string::npos) {
			++pos;
			continue;
		}
		if (!is_removable_audacious_qualifier(title.substr(pos + 1, end - pos - 1))) {
			pos = end + 1;
			continue;
		}

		std::size_t erase_begin = pos;
		if (erase_begin > 0 && title[erase_begin - 1] == ' ')
			--erase_begin;
		title.erase(erase_begin, end - erase_begin + 1);
		pos = erase_begin;
	}
	return trim_audacious_field(title);
}

inline std::string format_audacious_artist_title(std::string artist, std::string title)
{
	artist = trim_audacious_field(artist);
	title = strip_audacious_presentation_qualifiers(trim_audacious_field(title));
	if (artist == "(null)" || artist == "null")
		artist.clear();
	if (title == "(null)" || title == "null")
		title.clear();

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
