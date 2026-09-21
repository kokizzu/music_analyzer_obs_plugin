#include "../src/windows_hardware_write.hpp"

#include <vector>

int main()
{
	std::vector<int> writes;
	unsigned long revision = 7;
	const auto is_current = [&]() { return revision == 7; };

	if (mao::hardware_write_if_current(is_current, [&]() {
		writes.push_back(1);
		revision = 8;
		return true;
	}) != mao::HardwareWriteResult::Succeeded)
		return 1;

	if (mao::hardware_write_if_current(is_current, [&]() {
		writes.push_back(2);
		return true;
	}) != mao::HardwareWriteResult::Stale)
		return 2;
	if (writes != std::vector<int>{1})
		return 3;

	revision = 7;
	if (mao::hardware_write_if_current(is_current, [&]() {
		return false;
	}) != mao::HardwareWriteResult::Failed)
		return 4;
	return 0;
}
