#include "fret_control.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>

namespace {

uint8_t apc_color(const std::vector<uint8_t> &messages, int note)
{
	assert(messages.size() == 64 * 3);
	assert(messages[static_cast<std::size_t>(note) * 3] == 0x96);
	assert(messages[static_cast<std::size_t>(note) * 3 + 1] == note);
	return messages[static_cast<std::size_t>(note) * 3 + 2];
}

void test_root_state()
{
	mao::FretControlState state;
	assert(state.mode() == mao::RootControlMode::Auto);
	assert(state.manual_root() == 0);
	assert(state.effective_root() == 0);
	assert(state.set_detected_root_label("F# major"));
	assert(state.detected_root() == 6);
	assert(state.effective_root() == 6);
	assert(state.toggle_mode());
	assert(state.effective_root() == 0);
	assert(state.shift_manual_root(-1));
	assert(state.manual_root() == 11);
	assert(state.set_manual_root(19));
	assert(state.manual_root() == 7);
	assert(state.toggle_mode());
	assert(state.effective_root() == 6);
	assert(mao::pitch_class_from_root_label("Db") == 1);
	assert(mao::pitch_class_from_root_label("--") == -1);
	const uint64_t revision = state.revision();
	assert(state.set_device_state(mao::ExternalDevice::LiteJam, mao::DeviceConnectionState::Connected));
	assert(state.revision() == revision + 1);
	assert(state.display().visible);
	assert(state.display().devices[0] == mao::DeviceConnectionState::Connected);
}

void test_controller_actions()
{
	assert(mao::apc_action_for_pad(56).value == 0);
	assert(mao::apc_action_for_pad(57).value == 0);
	assert(mao::apc_action_for_pad(49).value == 0);
	assert(mao::apc_action_for_pad(58).value == 1);
	assert(mao::apc_action_for_pad(40).value == 4);
	assert(mao::apc_action_for_pad(22).value == 11);
	assert(mao::apc_action_for_pad(0).value == -1);
	assert(mao::apc_action_for_pad(3).kind == mao::ControlActionKind::ToggleMode);
	assert(mao::apc_action_for_pad(7).value == 1);
	assert(mao::mvave_action_for_switch(0, false).value == -1);
	assert(mao::mvave_action_for_switch(0, true).value == -2);
	assert(mao::mvave_action_for_switch(1, true).value == 2);
	assert(mao::mvave_action_for_switch(2, false).kind == mao::ControlActionKind::ToggleManualRootCG);
	assert(mao::mvave_action_for_switch(2, true).kind == mao::ControlActionKind::ToggleManualRootCG);
	assert(mao::mvave_action_for_switch(3, false).kind == mao::ControlActionKind::ToggleMode);

	mao::FretControlState state;
	assert(state.apply(mao::mvave_action_for_switch(2, false)));
	assert(state.manual_root() == 7);
	assert(state.apply(mao::mvave_action_for_switch(2, false)));
	assert(state.manual_root() == 0);
	assert(state.set_manual_root(4));
	assert(state.apply(mao::mvave_action_for_switch(2, false)));
	assert(state.manual_root() == 7);
}

void test_apc_display()
{
	const auto natural = mao::build_apc_led_messages(0, mao::RootControlMode::Manual);
	assert(apc_color(natural, 56) == 5);
	assert(apc_color(natural, 57) == 3);
	assert(apc_color(natural, 8) == 2);
	assert(apc_color(natural, 9) == 3);
	assert(apc_color(natural, 3) == 1);
	assert(apc_color(natural, 5) == 2);

	const auto palette = mao::build_apc_led_messages(0, mao::RootControlMode::Auto);
	assert(apc_color(palette, 49) == 5);
	assert(apc_color(palette, 51) == 9);
	assert(apc_color(palette, 53) == 96);
	assert(apc_color(palette, 55) == 109);
	assert(apc_color(palette, 33) == 13);
	assert(apc_color(palette, 35) == 21);
	assert(apc_color(palette, 37) == 90);
	assert(apc_color(palette, 39) == 37);
	assert(apc_color(palette, 17) == 40);
	assert(apc_color(palette, 19) == 49);
	assert(apc_color(palette, 21) == 94);
	assert(apc_color(palette, 23) == 57);
	assert(apc_color(palette, 0) == 1);
	assert(apc_color(palette, 3) == 2);
	assert(apc_color(palette, 5) == 1);

	const auto g_palette = mao::build_apc_led_messages(7, mao::RootControlMode::Auto);
	assert(apc_color(g_palette, 39) == 5);
	assert(apc_color(g_palette, 49) == 21);

	const auto automatic = mao::build_apc_led_messages(1, mao::RootControlMode::Auto);
	assert(apc_color(automatic, 61) == 0);
	assert(apc_color(automatic, 63) == 0);
	assert(apc_color(automatic, 45) == 0);
	assert(apc_color(automatic, 47) == 0);
	const auto manual_sharp = mao::build_apc_led_messages(1, mao::RootControlMode::Manual);
	assert(apc_color(manual_sharp, 61) == 3);
	assert(apc_color(manual_sharp, 63) == 3);
	assert(apc_color(manual_sharp, 45) == 3);
	assert(apc_color(manual_sharp, 47) == 3);
}

void test_litejam_packet()
{
	const auto packet = mao::build_litejam_major_scale_packet(0);
	assert(packet.size() < 245);
	for (int root = 0; root < 12; ++root)
		assert(mao::build_litejam_major_scale_packet(root).size() < 245);
	assert(packet.front() == 7);
	assert(packet[packet.size() - 3] == 'E');
	assert(packet[packet.size() - 2] == 'N');
	assert(packet[packet.size() - 1] == 'D');
	std::size_t offset = 1;
	for (int degree = 0; degree < 7; ++degree) {
		const uint8_t fret_count = packet[offset++];
		assert(fret_count > 0);
		bool found_expected_open_pair = false;
		for (int fret_index = 0; fret_index < fret_count; ++fret_index) {
			assert(packet[offset] <= 24);
			assert(packet[offset + 1] > 0 && packet[offset + 1] <= 0x3f);
			if ((degree == 0 && packet[offset] == 8 && packet[offset + 1] == 0x21) ||
			    (degree == 2 && packet[offset] == 0 && packet[offset + 1] == 0x21))
				found_expected_open_pair = true;
			offset += 2;
		}
		if (degree == 0 || degree == 2)
			assert(found_expected_open_pair);
		const mao::RgbColor expected = mao::major_scale_colors()[static_cast<std::size_t>(degree)];
		assert(packet[offset++] == expected.red);
		assert(packet[offset++] == expected.green);
		assert(packet[offset++] == expected.blue);
	}
	assert(offset + 3 == packet.size());
}

void test_fret_zealot_packet()
{
	const auto packet = mao::build_fret_zealot_major_scale_packet(0);
	for (int root = 0; root < 12; ++root) {
		const auto root_packet = mao::build_fret_zealot_major_scale_packet(root);
		assert(root_packet.size() <= 4 + 6 * 15 * 4);
	}
	assert(packet.size() > 4 && packet.size() % 4 == 0);
	assert(packet[0] == 0x40 && packet[1] == 0 && packet[2] == 0 && packet[3] == 0);
	assert(packet[4] == 0x00);
	assert(packet[5] == 0x00);
	assert(packet[6] == 0xf0);
	assert(packet[7] == 0x02);
	for (std::size_t offset = 4; offset < packet.size(); offset += 4) {
		assert(packet[offset] == 0x00);
		assert((packet[offset + 1] >> 4) <= 14);
		assert(packet[offset + 3] == 2 || packet[offset + 3] == 4 || packet[offset + 3] == 8 ||
		       packet[offset + 3] == 16 || packet[offset + 3] == 32 || packet[offset + 3] == 64);
	}
	bool found_orange = false;
	for (std::size_t offset = 4; offset < packet.size(); offset += 4) {
		if ((packet[offset + 1] & 0x0f) == 15 && packet[offset + 2] == 0x60) {
			found_orange = true;
			break;
		}
	}
	assert(found_orange);
}

} // namespace

int main()
{
	test_root_state();
	test_controller_actions();
	test_apc_display();
	test_litejam_packet();
	test_fret_zealot_packet();
	std::cout << "fret_control: ok\n";
	return 0;
}
