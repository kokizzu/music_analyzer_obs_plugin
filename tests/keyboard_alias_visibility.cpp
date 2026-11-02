#include "analyzer.cpp"
#include <iostream>

namespace mao {
static bool visible(const NoteGrid &grid, int midi)
{
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi == midi && note_cell_effective_visual_level(cell) > 0) return true;
	return false;
}
static NoteGrid source(float visibility)
{
	NoteGrid grid{};
	write_note_grid_cell(grid, NoteCandidate{60, .8f}, 1.f, 1.f);
	for (auto &cell : grid.cells) if (cell.active) cell.visual_level = visibility;
	for (auto &row : grid.rows) for (auto &cell : row) if (cell.active) cell.visual_level = visibility;
	return grid;
}
int alias_visibility_test()
{
	FullMixOwnership ownership{};
	ownership.debug_candidate_count = 1;
	auto &candidate = ownership.debug_candidates[0];
	candidate.midi = 48;
	candidate.owner = InstrumentKind::Keyboard;
	candidate.keyboard_score = .99f;
	candidate.ownership_confidence = .99f;
	candidate.spectral_level = .8f;
	candidate.other_score = .12f;
	candidate.harmonic_ratios[2] = .01f;
	ownership.global_note_levels[48 - kFirstMidi] = .8f;
	InstrumentState state{};
	auto hidden = source(0.f);
	prefer_exact_debug_keyboard_lower_octave_primary(hidden, state, ownership, -1);
	if (visible(hidden, 48)) {
		std::cerr << "Invisible Keyboard source resurrected as a visible octave alias\n";
		return 1;
	}
	auto shown = source(.4f);
	prefer_exact_debug_keyboard_lower_octave_primary(shown, state, ownership, -1);
	if (!visible(shown, 48) || !visible(shown, 60)) {
		std::cerr << "Visible source or supported visible alias was lost\n";
		return 1;
	}
	std::cout << "Keyboard alias visibility: invisible source blocked; visible source and supported promotion preserved\n";
	return 0;
}
}
int main() { return mao::alias_visibility_test(); }
