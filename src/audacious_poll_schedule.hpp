#pragma once

#include <chrono>

namespace mao {

constexpr std::chrono::milliseconds kAudaciousTitlePollInterval{1000};

// Polls are scheduled from their start time. A slow probe must never add a
// second of idle time before the next attempt.
constexpr std::chrono::milliseconds audacious_title_poll_wait(std::chrono::milliseconds elapsed)
{
	return elapsed >= kAudaciousTitlePollInterval ? std::chrono::milliseconds{0}
							 : kAudaciousTitlePollInterval - elapsed;
}

} // namespace mao
