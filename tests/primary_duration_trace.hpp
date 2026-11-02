#pragma once
#include "analyzer.hpp"

// Included only in an exported diagnostic build, never in the production API.
namespace mao_duration_trace {
struct Trace {
	mao::NoteGrid raw_keys{};
	mao::NoteGrid smoothed_keys{};
	std::array<mao::NoteTrackingState, mao::kNoteProbeCount> tracking{};
	bool captured_raw = false;
	bool captured_smoothing = false;
};
inline thread_local Trace state{};
}
