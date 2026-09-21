#include "fret_control.hpp"

#include <array>
#include <cstdint>
#include <cstdio>
#include <vector>

int main()
{
	const std::vector<std::uint8_t> packet = mao::build_fret_zealot_major_scale_packet(0);
	if (packet.size() < 8 || packet[0] != 0x40 || packet[1] != 0x00 || packet[2] != 0x00 || packet[3] != 0x00) {
		std::fprintf(stderr, "fret_zealot_protocol: missing clear prefix\n");
		return 1;
	}

	if ((packet.size() - 4) % 4 != 0) {
		std::fprintf(stderr, "fret_zealot_protocol: command alignment is invalid\n");
		return 1;
	}

	const std::array<std::uint8_t, 6> expected_masks = {0x40, 0x20, 0x10, 0x08, 0x04, 0x02};
	std::array<bool, 6> mask_found = {};
	for (std::size_t offset = 4; offset + 3 < packet.size(); offset += 4) {
		for (std::size_t index = 0; index < expected_masks.size(); ++index)
			mask_found[index] = mask_found[index] || packet[offset + 3] == expected_masks[index];
	}
	for (std::size_t index = 0; index < mask_found.size(); ++index) {
		if (!mask_found[index]) {
			std::fprintf(stderr, "fret_zealot_protocol: missing reversed string mask 0x%02x\n",
				     expected_masks[index]);
			return 1;
		}
	}

	std::puts("fret_zealot_protocol: ok");
	return 0;
}
