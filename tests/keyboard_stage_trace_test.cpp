#include "keyboard_stage_trace.hpp"
#include <cassert>
#include <iostream>

int main()
{
	mao::NoteGrid grid{};
	auto &cell = grid.rows[0][0];
	cell.active = true; cell.midi = 60; cell.level = .5f;
	auto &state = mao_stage_trace::state;
	state.start(grid);
	{
		mao_stage_trace::Scope outer(grid, "outer");
		{ mao_stage_trace::Scope inner(grid, "inner"); cell.visual_level = 0; }
	}
	assert(state.events.size() == 1 && std::string(state.events[0].stage) == "outer");
	cell.visual_level = .3f;
	{
		mao_stage_trace::Scope next(grid, "next");
		cell.visual_level = 0;
	}
	assert(state.events.size() == 3 && state.events[1].between && !state.events[2].between);
	state.finish(grid);
	assert(state.depth == 0 && state.watched == nullptr);
	std::cout << "Stage observer: nested attribution, unobserved changes and final-state reconciliation passed\n";
}
