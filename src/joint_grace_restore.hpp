#pragma once
#include "analyzer.hpp"

namespace mao::joint {
inline float visible_level(const NoteCell &cell) { return cell.active ? (cell.visual_level < 0 ? cell.level : cell.visual_level) : 0; }
inline bool restore_erased_note(NoteGrid &target, const NoteGrid &original, int midi)
{
	if (midi < kFirstAnalyzedMidi || midi > kLastAnalyzedMidi) return false;
	const std::size_t pc = static_cast<std::size_t>(midi % 12);
	const NoteCell *source = nullptr;
	NoteCell *destination = nullptr;
	for (auto &row : target.rows) {
		if (row[pc].midi == midi && visible_level(row[pc]) > 0) return false;
		if (row[pc].active && row[pc].midi == midi) destination = &row[pc];
	}
	for (const auto &row : original.rows)
		if (row[pc].midi == midi && visible_level(row[pc]) > 0 && (!source || visible_level(row[pc]) > visible_level(*source))) source = &row[pc];
	if (!source) return false;
	if (!destination) for (auto &row : target.rows) if (visible_level(row[pc]) <= 0) { destination = &row[pc]; break; }
	if (!destination) return false;
	*destination = *source;
	target.cells[pc] = {};
	for (const auto &row : target.rows)
		if (visible_level(row[pc]) > 0 && (!target.cells[pc].active || row[pc].level > target.cells[pc].level)) target.cells[pc] = row[pc];
	return true;
}
}
