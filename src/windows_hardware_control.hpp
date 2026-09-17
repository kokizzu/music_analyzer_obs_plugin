#pragma once

#include "fret_control.hpp"

#include <cstdint>
#include <cstdio>
#include <memory>
#include <string>

namespace mao {

inline bool windows_ascii_case_equal(char left, char right)
{
	if (left >= 'A' && left <= 'Z')
		left = static_cast<char>(left - 'A' + 'a');
	if (right >= 'A' && right <= 'Z')
		right = static_cast<char>(right - 'A' + 'a');
	return left == right;
}

inline bool windows_ascii_contains(const std::string &value, const char *needle)
{
	if (!needle || !*needle)
		return true;
	for (std::size_t start = 0; start + std::char_traits<char>::length(needle) <= value.size(); ++start) {
		std::size_t offset = 0;
		for (; needle[offset] && windows_ascii_case_equal(value[start + offset], needle[offset]); ++offset)
			;
		if (!needle[offset])
			return true;
	}
	return false;
}

inline bool windows_midi_output_name_matches(const std::string &name, const std::string &preferred)
{
	if (!preferred.empty()) {
		if (preferred.size() > name.size())
			return false;
		for (std::size_t start = 0; start + preferred.size() <= name.size(); ++start) {
			std::size_t offset = 0;
			for (; offset < preferred.size() &&
				       windows_ascii_case_equal(name[start + offset], preferred[offset]); ++offset)
				;
			if (offset == preferred.size())
				return true;
		}
		return false;
	}

	if (windows_ascii_contains(name, "apc mini") || windows_ascii_contains(name, "apcmini"))
		return true;
	const bool akai_family = windows_ascii_contains(name, "akai") ||
					 windows_ascii_contains(name, "mpc") ||
					 windows_ascii_contains(name, "mpd");
	return akai_family && (windows_ascii_contains(name, "apc") ||
				      windows_ascii_contains(name, "mpc") ||
				      windows_ascii_contains(name, "mpd") ||
				      windows_ascii_contains(name, "pad"));
}

inline bool windows_litejam_name_matches(const std::string &name, const std::string &preferred)
{
	if (!preferred.empty())
		return windows_ascii_contains(name, preferred.c_str());
	return windows_ascii_contains(name, "litejam") || windows_ascii_contains(name, "lite jam");
}

inline std::uint32_t pack_windows_midi_short_message(std::uint8_t status, std::uint8_t data1,
								      std::uint8_t data2)
{
	return static_cast<std::uint32_t>(status) |
		(static_cast<std::uint32_t>(data1) << 8) |
		(static_cast<std::uint32_t>(data2) << 16);
}

struct WindowsHardwareOptions {
	bool enabled = true;
	std::string midi_output;
	std::string litejam_device;
	std::string fret_zealot_device;
};

class WindowsHardwareController {
public:
	explicit WindowsHardwareController(const WindowsHardwareOptions &options);
#if defined(_WIN32)
	~WindowsHardwareController();
#else
	~WindowsHardwareController() = default;
#endif

	void start();
	void update(int root_pitch_class, RootControlMode mode);
	void stop();

	static void print_midi_devices();
	static void print_litejam_devices();
	static void print_fret_zealot_devices();

#if defined(_WIN32)
private:
	struct Impl;
	std::unique_ptr<Impl> impl_;
#endif
};

#if !defined(_WIN32)
inline WindowsHardwareController::WindowsHardwareController(const WindowsHardwareOptions &)
{
}

inline void WindowsHardwareController::start()
{
}

inline void WindowsHardwareController::update(int, RootControlMode)
{
}

inline void WindowsHardwareController::stop()
{
}

inline void WindowsHardwareController::print_midi_devices()
{
	std::fprintf(stderr, "Windows hardware control is available only in the Windows standalone build\n");
}

inline void WindowsHardwareController::print_litejam_devices()
{
}

inline void WindowsHardwareController::print_fret_zealot_devices()
{
}
#endif

} // namespace mao
