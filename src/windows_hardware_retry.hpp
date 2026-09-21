#pragma once

#include <algorithm>
#include <chrono>

namespace mao {

// Shared by the Windows workers and the fake-backend tests so retry timing is
// exercised without requiring a Windows device.
class HardwareRetryState {
public:
	using clock = std::chrono::steady_clock;
	using time_point = clock::time_point;
	using duration = std::chrono::seconds;

	static constexpr duration initial_delay{2};
	static constexpr duration maximum_delay{30};

	bool ready(time_point now) const
	{
		return now >= next_attempt_;
	}

	void force(time_point now)
	{
		next_attempt_ = now;
	}

	void succeeded(time_point now)
	{
		delay_ = initial_delay;
		next_attempt_ = now + delay_;
	}

	void failed(time_point now)
	{
		next_attempt_ = now + delay_;
		delay_ = std::min(delay_ + delay_, maximum_delay);
	}

	duration delay() const
	{
		return delay_;
	}

	time_point next_attempt() const
	{
		return next_attempt_;
	}

private:
	time_point next_attempt_ = time_point::min();
	duration delay_ = initial_delay;
};

} // namespace mao
