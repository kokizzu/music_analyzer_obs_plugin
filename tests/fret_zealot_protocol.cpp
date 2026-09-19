#include "fret_control.hpp"

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

	bool low_e_mask_found = false;
	bool high_e_mask_found = false;
	for (std::size_t offset = 4; offset + 3 < packet.size(); offset += 4) {
		if ((packet[offset + 1] >> 4) != 0)
			continue;
		low_e_mask_found = low_e_mask_found || packet[offset + 3] == 0x40;
		high_e_mask_found = high_e_mask_found || packet[offset + 3] == 0x02;
	}
	if (!low_e_mask_found || !high_e_mask_found) {
		std::fprintf(stderr, "fret_zealot_protocol: low/high E string masks are not reversed\n");
		return 1;
	}

	std::puts("fret_zealot_protocol: ok");
	return 0;
}
