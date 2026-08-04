#include "audacious_title.hpp"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <sstream>
#include <string>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/wait.h>
#endif

namespace mao {
namespace {

struct CommandResult {
	int exit_code = -1;
	std::string output;
};

std::string trim(std::string value)
{
	const auto not_space = [](unsigned char c) { return !std::isspace(c); };
	value.erase(value.begin(), std::find_if(value.begin(), value.end(), not_space));
	value.erase(std::find_if(value.rbegin(), value.rend(), not_space).base(), value.end());
	return value;
}

std::string lower_ascii(std::string value)
{
	for (char &c : value)
		c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
	return value;
}

bool ends_with_case_insensitive(const std::string &value, const std::string &suffix)
{
	if (suffix.size() > value.size())
		return false;
	return lower_ascii(value.substr(value.size() - suffix.size())) == lower_ascii(suffix);
}

std::string collapse_whitespace(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	bool pending_space = false;
	for (unsigned char c : value) {
		if (std::isspace(c)) {
			pending_space = !output.empty();
			continue;
		}
		if (pending_space)
			output.push_back(' ');
		output.push_back(static_cast<char>(c));
		pending_space = false;
	}
	return trim(output);
}

std::string visualizer_safe_ascii(const std::string &value)
{
	std::string output;
	output.reserve(value.size());
	for (std::size_t i = 0; i < value.size();) {
		const unsigned char c = static_cast<unsigned char>(value[i]);
		if (c < 0x80) {
			if (c >= 0x20 && c != 0x7f)
				output.push_back(static_cast<char>(c));
			else if (!output.empty() && output.back() != ' ')
				output.push_back(' ');
			++i;
			continue;
		}

		output.push_back('?');
		++i;
		while (i < value.size() && (static_cast<unsigned char>(value[i]) & 0xc0) == 0x80)
			++i;
	}
	return collapse_whitespace(output);
}

CommandResult run_command(const char *command)
{
	CommandResult result;
#if defined(__unix__) || defined(__APPLE__)
	FILE *pipe = popen(command, "r");
	if (!pipe)
		return result;

	char buffer[512] = {};
	while (std::fgets(buffer, sizeof(buffer), pipe)) {
		if (result.output.size() >= 65536)
			break;
		result.output += buffer;
	}
	const int status = pclose(pipe);
	if (status >= 0 && WIFEXITED(status))
		result.exit_code = WEXITSTATUS(status);
#else
	(void)command;
#endif
	return result;
}

std::string best_audacious_wmctrl_title(const std::string &output)
{
	std::istringstream lines(output);
	std::string line;
	std::string best_title;
	int best_score = -1;

	while (std::getline(lines, line)) {
		std::istringstream fields(line);
		std::string window_id;
		std::string desktop;
		std::string window_class;
		std::string host;
		if (!(fields >> window_id >> desktop >> window_class >> host))
			continue;
		if (lower_ascii(window_class).find("audacious") == std::string::npos)
			continue;

		std::string title;
		std::getline(fields, title);
		title = trim(title);
		if (title.empty())
			continue;

		const std::string lowered = lower_ascii(title);
		int score = 0;
		if (title.find(" - ") != std::string::npos)
			score += 20;
		if (lowered != "audacious")
			score += 10;
		if (lowered.find("preferences") == std::string::npos && lowered.find("equalizer") == std::string::npos &&
		    lowered.find("playlist manager") == std::string::npos)
			score += 5;
		score += static_cast<int>(std::min<std::size_t>(title.size(), 200) / 20);
		if (score > best_score) {
			best_score = score;
			best_title = title;
		}
	}

	return best_title;
}

std::string basename_from_uri_or_path(std::string value)
{
	value = trim(value);
	const std::size_t query = value.find_first_of("?#");
	if (query != std::string::npos)
		value.resize(query);
	const std::size_t slash = value.find_last_of("/\\");
	if (slash != std::string::npos)
		value.erase(0, slash + 1);
	return value;
}

} // namespace

std::string find_audacious_window_title(const std::string &wmctrl_output)
{
	return best_audacious_wmctrl_title(wmctrl_output);
}

std::string extract_audacious_song_title(const std::string &titlebar)
{
	std::string title = collapse_whitespace(titlebar);
	if (title.empty())
		return {};

	static constexpr const char *kSuffixes[] = {" - Audacious", " [Audacious]"};
	for (const char *suffix : kSuffixes) {
		if (ends_with_case_insensitive(title, suffix)) {
			title.resize(title.size() - std::char_traits<char>::length(suffix));
			title = trim(title);
			break;
		}
	}
	if (lower_ascii(title).rfind("audacious - ", 0) == 0)
		title.erase(0, std::char_traits<char>::length("Audacious - "));

	std::vector<std::string> parts;
	std::size_t start = 0;
	while (start <= title.size()) {
		const std::size_t separator = title.find(" - ", start);
		parts.push_back(trim(title.substr(start, separator == std::string::npos ? std::string::npos : separator - start)));
		if (separator == std::string::npos)
			break;
		start = separator + 3;
	}

	std::string song;
	if (parts.size() >= 3) {
		song = parts[2];
		for (std::size_t i = 3; i < parts.size(); ++i) {
			song += " - ";
			song += parts[i];
		}
	} else if (parts.size() == 2) {
		song = parts[1];
	} else {
		song = title;
	}

	return visualizer_safe_ascii(trim(song));
}

std::string make_scrolling_title(const std::string &title, std::size_t width, std::size_t offset)
{
	if (width == 0 || title.empty())
		return {};
	if (title.size() <= width)
		return title;

	const std::string loop = title + "   ---   ";
	offset %= loop.size();
	std::string output;
	output.reserve(width);
	for (std::size_t i = 0; i < width; ++i)
		output.push_back(loop[(offset + i) % loop.size()]);
	return output;
}

AudaciousNowPlaying read_audacious_now_playing()
{
	AudaciousNowPlaying now_playing;
#if defined(__linux__)
	const CommandResult process = run_command("pgrep -x audacious 2>/dev/null");
	now_playing.running = process.exit_code == 0 && !trim(process.output).empty();
	if (!now_playing.running)
		return now_playing;

	const CommandResult windows = run_command("wmctrl -lx 2>/dev/null");
	now_playing.window_title = best_audacious_wmctrl_title(windows.output);

	std::string formatted_title = now_playing.window_title;
	if (formatted_title.empty() || lower_ascii(trim(formatted_title)) == "audacious") {
		const CommandResult audtool_title = run_command("audtool current-song 2>/dev/null");
		if (audtool_title.exit_code == 0)
			formatted_title = trim(audtool_title.output);
	}

	now_playing.song_title = extract_audacious_song_title(formatted_title);
	if (now_playing.song_title.empty()) {
		const CommandResult filename = run_command("audtool current-song-filename 2>/dev/null");
		if (filename.exit_code == 0)
			now_playing.song_title = visualizer_safe_ascii(basename_from_uri_or_path(filename.output));
	}
#else
	now_playing.running = false;
#endif
	return now_playing;
}

} // namespace mao
