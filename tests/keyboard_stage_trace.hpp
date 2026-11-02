#pragma once
#include "analyzer.hpp"
#include <algorithm>
#include <array>
#include <vector>

// Diagnostic-only observer injected into a primary source export. It reads
// grids and buffers events; it performs no live file I/O or detector writes.
namespace mao_stage_trace {
using Levels = std::array<float, mao::kNoteProbeCount>;
inline Levels levels(const mao::NoteGrid &grid)
{
	Levels result{};
	for (const auto &row : grid.rows) for (const auto &cell : row) {
		if (!cell.active || cell.midi < mao::kFirstAnalyzedMidi || cell.midi > mao::kLastAnalyzedMidi) continue;
		auto &value = result[static_cast<std::size_t>(cell.midi - mao::kFirstAnalyzedMidi)];
		value = std::max(value, cell.visual_level < 0 ? cell.level : cell.visual_level);
	}
	return result;
}
struct Event { const char *stage; int midi; float before, after; bool between; };
struct LowEvidence {
	float direct = 0, adjacent = 0, strongest = 0, harmonic = 0;
	int partials = 0;
	bool considered = false;
};
struct State {
	const mao::NoteGrid *watched = nullptr;
	Levels initial{}, last{};
	std::vector<Event> events;
	std::array<LowEvidence, mao::kNoteProbeCount> low{};
	unsigned depth = 0;
	bool started = false;
	void compare(const Levels &next, const char *stage, bool between)
	{
		for (std::size_t i = 0; i < next.size(); ++i)
			if ((last[i] > 0) != (next[i] > 0)) events.push_back({stage, static_cast<int>(i) + mao::kFirstAnalyzedMidi, last[i], next[i], between});
		last = next;
	}
	void start(const mao::NoteGrid &grid)
	{
		watched = &grid;
		initial = last = levels(grid);
		events.clear();
		low = {};
		depth = 0;
		started = true;
	}
	void finish(const mao::NoteGrid &grid)
	{
		compare(levels(grid), "after_analyze", true);
		watched = nullptr;
	}
};
inline thread_local State state;
class Scope {
	const mao::NoteGrid *grid_ = nullptr;
	const char *stage_;
	bool outer_ = false;
public:
	Scope(const mao::NoteGrid &grid, const char *stage) : stage_(stage)
	{
		if (&grid != state.watched) return;
		grid_ = &grid;
		outer_ = state.depth++ == 0;
		if (outer_) state.compare(levels(grid), stage_, true);
	}
	~Scope()
	{
		if (!grid_) return;
		--state.depth;
		if (outer_) state.compare(levels(*grid_), stage_, false);
	}
};
}
