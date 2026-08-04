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

inline std::string collapse_audacious_spaces(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	bool pending_space = false;
	for (const unsigned char c : value) {
		if (c < 0x80 && std::isspace(c)) {
			pending_space = !output.empty();
			continue;
		}
		if (pending_space)
			output.push_back(' ');
		output.push_back(static_cast<char>(c));
		pending_space = false;
	}
	return trim_audacious_field(output);
}

inline std::string lower_audacious_ascii(std::string value)
{
	for (char &c : value) {
		const unsigned char byte = static_cast<unsigned char>(c);
		if (byte < 0x80)
			c = static_cast<char>(std::tolower(byte));
	}
	return value;
}

inline bool ends_with_audacious_ascii(const std::string &value, const std::string &suffix)
{
	if (suffix.size() > value.size())
		return false;
	return lower_audacious_ascii(value.substr(value.size() - suffix.size())) ==
	       lower_audacious_ascii(suffix);
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

inline bool audacious_qualifier_has_word(const std::string &qualifier, const std::string &word)
{
	std::size_t start = 0;
	while (start < qualifier.size()) {
		const std::size_t end = qualifier.find(' ', start);
		const std::size_t length = end == std::string::npos ? qualifier.size() - start : end - start;
		if (qualifier.compare(start, length, word) == 0)
			return true;
		if (end == std::string::npos)
			break;
		start = end + 1;
	}
	return false;
}

inline bool is_removable_audacious_qualifier(const std::string &value)
{
	const std::string qualifier = normalize_audacious_qualifier(value);
	if (qualifier.empty())
		return false;
	if (qualifier == "live" || qualifier == "live video" || qualifier == "live performance" ||
	    qualifier == "music video" || qualifier == "video music" || qualifier == "lyric video" ||
	    qualifier == "lyrics video")
		return true;

	const bool official = audacious_qualifier_has_word(qualifier, "official");
	const bool presentation = audacious_qualifier_has_word(qualifier, "video") ||
				  audacious_qualifier_has_word(qualifier, "audio") ||
				  audacious_qualifier_has_word(qualifier, "visualizer") ||
				  audacious_qualifier_has_word(qualifier, "mv") ||
				  audacious_qualifier_has_word(qualifier, "live") ||
				  audacious_qualifier_has_word(qualifier, "performance") ||
				  audacious_qualifier_has_word(qualifier, "lyric") ||
				  audacious_qualifier_has_word(qualifier, "lyrics") ||
				  audacious_qualifier_has_word(qualifier, "music");
	if (official && presentation)
		return true;

	const bool lyric_video = (audacious_qualifier_has_word(qualifier, "lyric") ||
				  audacious_qualifier_has_word(qualifier, "lyrics")) &&
				 audacious_qualifier_has_word(qualifier, "video");
	return lyric_video;
}

inline std::string strip_audacious_transport_suffixes(std::string title)
{
	title = trim_audacious_field(title);
	static constexpr const char *kSuffixes[] = {
		" - music-yt",
		" .music-yt",
		"_music-yt",
		".music-yt",
		" music-yt",
		"-music-yt",
	};

	bool removed = true;
	while (removed && !title.empty()) {
		removed = false;
		for (const char *suffix : kSuffixes) {
			const std::string suffix_text(suffix);
			if (!ends_with_audacious_ascii(title, suffix_text))
				continue;
			title.resize(title.size() - suffix_text.size());
			title = trim_audacious_field(title);
			removed = true;
			break;
		}
	}
	return title;
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
	return strip_audacious_transport_suffixes(collapse_audacious_spaces(title));
}

inline std::string clean_audacious_title(std::string title)
{
	title = strip_audacious_presentation_qualifiers(collapse_audacious_spaces(title));
	if (title == "(null)" || title == "null")
		title.clear();
	return title;
}

std::string find_audacious_window_title(const std::string &wmctrl_output);
std::string extract_audacious_song_title(const std::string &titlebar);
std::string make_scrolling_title(const std::string &title, std::size_t width, std::size_t offset);
AudaciousNowPlaying read_audacious_now_playing();

} // namespace mao
