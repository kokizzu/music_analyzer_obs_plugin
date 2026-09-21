#include "../src/windows_hardware_retry.hpp"

#include <chrono>

int main()
{
	using Retry = mao::HardwareRetryState;
	const Retry::time_point start{};
	Retry retry;
	if (!retry.ready(start))
		return 1;

	retry.failed(start);
	if (retry.ready(start + std::chrono::seconds(1)))
		return 2;
	if (retry.delay() != std::chrono::seconds(4))
		return 3;

	const auto second_attempt = start + std::chrono::seconds(2);
	retry.failed(second_attempt);
	if (retry.ready(second_attempt + std::chrono::seconds(3)))
		return 4;
	if (retry.delay() != std::chrono::seconds(8))
		return 5;

	const auto successful_attempt = second_attempt + std::chrono::seconds(4);
	retry.succeeded(successful_attempt);
	if (retry.ready(successful_attempt + std::chrono::seconds(1)))
		return 6;
	if (retry.delay() != std::chrono::seconds(2))
		return 7;

	retry.force(successful_attempt + std::chrono::seconds(1));
	if (!retry.ready(successful_attempt + std::chrono::seconds(1)))
		return 8;
	return 0;
}
