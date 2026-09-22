#include "src/fret_control.hpp"

#include <cassert>

int main()
{
	const std::vector<uint8_t> apc = mao::build_apc_led_clear_messages();
	assert(apc.size() == 64u * 3u);
	for (std::size_t offset = 0; offset < apc.size(); offset += 3) {
		assert(apc[offset] == 0x96);
		assert(apc[offset + 1] == offset / 3);
		assert(apc[offset + 2] == 0);
	}

	const std::vector<uint8_t> mpc = mao::build_mpc_pad_clear_messages();
	assert(mpc.size() == 16u * 3u);
	for (std::size_t offset = 0; offset < mpc.size(); offset += 3) {
		assert(mpc[offset] == 0x99);
		assert(mpc[offset + 1] == 36u + offset / 3);
		assert(mpc[offset + 2] == 0);
	}
	return 0;
}
