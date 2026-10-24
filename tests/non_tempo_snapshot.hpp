#pragma once
#include "analyzer.hpp"
#include <cstring>

namespace mao_test {
inline bool same_cell(const mao::NoteCell &a, const mao::NoteCell &b)
{
	return std::strcmp(a.label, b.label) == 0 && a.level == b.level &&
	       a.visual_level == b.visual_level && a.midi == b.midi && a.active == b.active;
}
inline bool same_grid(const mao::NoteGrid &a, const mao::NoteGrid &b)
{
	for (std::size_t i = 0; i < a.cells.size(); ++i) if (!same_cell(a.cells[i], b.cells[i])) return false;
	for (std::size_t row = 0; row < a.rows.size(); ++row)
		for (std::size_t i = 0; i < a.rows[row].size(); ++i)
			if (!same_cell(a.rows[row][i], b.rows[row][i])) return false;
	return true;
}
inline const char *non_tempo_difference(const mao::AnalysisSnapshot &a, const mao::AnalysisSnapshot &b)
{
	struct Grid { const char *name; mao::NoteGrid mao::AnalysisSnapshot::*member; };
	const Grid grids[] = {
		{"ambiguous_notes", &mao::AnalysisSnapshot::ambiguous_notes},
		{"bass_notes", &mao::AnalysisSnapshot::bass_notes},
		{"guitar_notes", &mao::AnalysisSnapshot::guitar_notes},
		{"keyboard_notes", &mao::AnalysisSnapshot::keyboard_notes},
		{"vocal_notes", &mao::AnalysisSnapshot::vocal_notes},
		{"other_notes", &mao::AnalysisSnapshot::other_notes},
		{"guitar_chord_analysis_notes", &mao::AnalysisSnapshot::guitar_chord_analysis_notes},
		{"guitar_chord_smoothed_notes", &mao::AnalysisSnapshot::guitar_chord_smoothed_notes},
		{"keyboard_chord_analysis_notes", &mao::AnalysisSnapshot::keyboard_chord_analysis_notes},
		{"keyboard_chord_smoothed_notes", &mao::AnalysisSnapshot::keyboard_chord_smoothed_notes}};
	for (const auto &grid : grids) if (!same_grid(a.*grid.member, b.*grid.member)) return grid.name;
	struct State { const char *name; mao::InstrumentState mao::AnalysisSnapshot::*member; };
	const State states[] = {
		{"root", &mao::AnalysisSnapshot::root}, {"global_chord", &mao::AnalysisSnapshot::global_chord},
		{"bass", &mao::AnalysisSnapshot::bass}, {"guitar", &mao::AnalysisSnapshot::guitar},
		{"keyboard", &mao::AnalysisSnapshot::keyboard}, {"vocal", &mao::AnalysisSnapshot::vocal},
		{"other", &mao::AnalysisSnapshot::other}, {"guitar_chord", &mao::AnalysisSnapshot::guitar_chord},
		{"guitar_raw_chord", &mao::AnalysisSnapshot::guitar_raw_chord},
		{"guitar_smoothed_chord", &mao::AnalysisSnapshot::guitar_smoothed_chord},
		{"keyboard_chord", &mao::AnalysisSnapshot::keyboard_chord},
		{"other_chord", &mao::AnalysisSnapshot::other_chord}};
	for (const auto &state : states)
		if (std::strcmp((a.*state.member).label, (b.*state.member).label) != 0 ||
		    (a.*state.member).confidence != (b.*state.member).confidence) return state.name;
	if (std::strcmp(a.keyboard_chord_raw_label, b.keyboard_chord_raw_label) != 0 ||
	    a.keyboard_chord_raw_confidence != b.keyboard_chord_raw_confidence) return "keyboard_raw_chord";
	if (std::strcmp(a.keyboard_chord_smoothed_label, b.keyboard_chord_smoothed_label) != 0 ||
	    a.keyboard_chord_smoothed_confidence != b.keyboard_chord_smoothed_confidence) return "keyboard_smoothed_chord";
	for (std::size_t i = 0; i < a.drums.size(); ++i)
		if (std::strcmp(a.drums[i].label, b.drums[i].label) != 0 || a.drums[i].level != b.drums[i].level ||
		    a.drums[i].active != b.drums[i].active) return "drums";
	return nullptr;
}
} // namespace mao_test
