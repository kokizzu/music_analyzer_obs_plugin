#include "fret_control.hpp"
#include "windows_hardware_control.hpp"

#include <cstdio>
#include <vector>

namespace {

bool expect(bool condition, const char *message)
{
	if (!condition)
		std::fprintf(stderr, "windows_midi_protocol: %s\n", message);
	return condition;
}

} // namespace

int main()
{
	bool ok = expect(mao::windows_midi_uses_pad_note_feedback("Akai MPC", "auto"),
			 "auto must select note feedback for MPC");
	ok = expect(!mao::windows_midi_uses_pad_note_feedback("APC Mini", "auto"),
		     "auto must keep APC grid feedback for APC Mini") && ok;
	ok = expect(!mao::windows_midi_uses_pad_note_feedback("Akai MPC", "apc"),
		     "explicit APC protocol must override device-name detection") && ok;
	ok = expect(mao::windows_midi_uses_pad_note_feedback("Akai MPC", "mpc-notes"),
		     "explicit MPC protocol must select note feedback") && ok;
	const std::vector<uint8_t> messages = mao::build_mpc_pad_note_messages(0);
	ok = expect(messages.size() == 16 * 3, "MPC packet must contain 16 three-byte messages") && ok;
	for (int pad = 0; pad < 16 && ok; ++pad) {
		const std::size_t offset = static_cast<std::size_t>(pad) * 3;
		ok = expect(messages[offset] == 0x99, "MPC packet must use MIDI channel 10 note-on") &&
			expect(messages[offset + 1] == static_cast<uint8_t>(36 + pad),
			       "MPC packet must use classic pad note numbering");
	}
	if (ok)
		ok = expect(messages[2] != 0, "C-root pad must be lit") &&
			expect(messages[8] != 0, "D-scale pad must be lit") &&
			expect(messages[14] != 0, "E-scale pad must be lit");
	if (ok)
		std::puts("windows_midi_protocol: ok");
	return ok ? 0 : 1;
}
