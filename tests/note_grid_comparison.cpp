#include "note_grid_comparison.hpp"
#include <iostream>
#include <utility>

int main()
{
	mao::NoteGrid grid{};
	for (std::size_t row = 0; row < 2; ++row) {
		auto &cell = grid.rows[row][0];
		cell.active = true; cell.midi = 60; cell.level = row ? .2f : .8f;
	}
	if (mao_test::surviving_grid_cells_changed(grid, grid)) {
		std::cerr << "Identical duplicate-MIDI cells were falsely reported as changed\n";
		return 1;
	}
	auto moved = grid;
	std::swap(moved.rows[0], moved.rows[1]);
	if (mao_test::surviving_grid_cells_changed(grid, moved)) return 2;
	moved.rows[0][0].level = .3f;
	if (!mao_test::surviving_grid_cells_changed(grid, moved)) return 3;
	moved = grid;
	moved.rows[1][0] = {};
	if (!mao_test::surviving_grid_cells_changed(grid, moved)) return 5;
	moved.rows[0][0] = {};
	moved.rows[1][0] = {};
	if (mao_test::surviving_grid_cells_changed(grid, moved)) return 4;
	std::cout << "Surviving cells: duplicate identity, row permutation, changed value and removed pitch passed\n";
}
