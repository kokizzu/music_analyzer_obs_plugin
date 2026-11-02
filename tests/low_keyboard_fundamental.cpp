#include "analyzer.cpp"
#include <iostream>

namespace mao {
static bool emitted(const NoteCandidateList &candidates, int midi = -1)
{
	NoteGrid grid{};
	const float strongest = strongest_candidate_score(candidates);
	for (const auto &candidate : candidates) write_note_grid_cell(grid, candidate, strongest, 1.f);
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && (midi < 0 || cell.midi == midi) && note_cell_effective_visual_level(cell) > 0) return true;
	return false;
}
int low_fundamental_test()
{
	std::array<float, kNoteProbeCount> powers{};
	powers[60 - kFirstMidi] = 1.f;
	powers[67 - kFirstMidi] = .8f;
	NoteCandidateList harmonic_only;
	append_full_mix_low_keyboard_candidates(harmonic_only, powers, 12);
	if (emitted(harmonic_only)) {
		std::cerr << "Higher C/G notes created a low Keyboard candidate with zero direct fundamental evidence\n";
		return 1;
	}
	// probe_level takes a square root of these powers.
	powers[36 - kFirstMidi] = 1.0e-8f;
	powers[35 - kFirstMidi] = powers[37 - kFirstMidi] = 1.0e-10f;
	NoteCandidateList negligible_fundamental;
	append_full_mix_low_keyboard_candidates(negligible_fundamental, powers, 12);
	if (emitted(negligible_fundamental)) {
		std::cerr << "Negligible direct support bypassed the relative fundamental floor\n";
		return 1;
	}
	powers[36 - kFirstMidi] = 1.0e-6f;
	powers[35 - kFirstMidi] = powers[37 - kFirstMidi] = 1.0e-8f;
	NoteCandidateList weak_fundamental;
	append_full_mix_low_keyboard_candidates(weak_fundamental, powers, 12);
	if (!emitted(weak_fundamental, 36)) {
		std::cerr << "Weak but real supported fundamental was lost\n";
		return 1;
	}
	powers.fill(0.f);
	powers[46 - kFirstMidi] = powers[51 - kFirstMidi] = 1.f;
	powers[55 - kFirstMidi] = powers[58 - kFirstMidi] = .8f;
	powers[39 - kFirstMidi] = 4.0e-6f;
	NoteCandidateList rejected_winner;
	append_full_mix_low_keyboard_candidates(rejected_winner, powers, 12);
	if (emitted(rejected_winner, 39)) {
		std::cerr << "Rejecting a low-note winner promoted an unselected octave runner-up\n";
		return 1;
	}
	std::cout << "Low Keyboard: harmonic-only conjecture rejected; weak supported fundamental retained\n";
	return 0;
}
}
int main() { return mao::low_fundamental_test(); }
