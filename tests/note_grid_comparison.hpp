#pragma once
#include "analyzer.hpp"
#include <array>
#include <cstring>

namespace mao_test {
inline bool surviving_grid_cells_changed(const mao::NoteGrid &before, const mao::NoteGrid &after)
{
	std::array<bool, 128> visited{};
	for (const auto &row : before.rows) for (const auto &cell : row) {
		if (!cell.active || cell.midi < 0 || cell.midi > 127 || visited[cell.midi]) continue;
		visited[cell.midi] = true;
		std::array<const mao::NoteCell *, mao::kNoteRowCount * 12> old_cells{}, new_cells{};
		std::size_t old_count = 0, new_count = 0;
		for (const auto &r : before.rows) for (const auto &c : r)
			if (c.active && c.midi == cell.midi) old_cells[old_count++] = &c;
		for (const auto &r : after.rows) for (const auto &c : r)
			if (c.active && c.midi == cell.midi) new_cells[new_count++] = &c;
		if (!new_count) continue; // Removed notes are scored separately.
		if (old_count != new_count) return true;
		std::array<bool, mao::kNoteRowCount * 12> used{};
		for (std::size_t i = 0; i < old_count; ++i) {
			bool found = false;
			for (std::size_t j = 0; j < new_count; ++j) {
				const auto &a = *old_cells[i], &b = *new_cells[j];
				if (!used[j] && std::strcmp(a.label, b.label) == 0 && a.level == b.level && a.visual_level == b.visual_level) {
					used[j] = found = true;
					break;
				}
			}
			if (!found) return true;
		}
	}
	return false;
}
}
