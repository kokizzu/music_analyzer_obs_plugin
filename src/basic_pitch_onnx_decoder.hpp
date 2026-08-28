#pragma once

#include "basic_pitch_onnx_runtime.hpp"

#include <array>

namespace mao {

struct BasicPitchCausalNotes {
	std::array<float, BasicPitchOnnxOutput::kNoteBins> confidence = {};
};

// Converts a two-second Basic Pitch output tensor into the note state near the
// live edge.  The selected frame leaves 250 ms of lookahead, matching the
// causal benchmark.  This has no ownership or UI policy: callers must fuse it
// through independently validated detector gates.
class BasicPitchOnnxDecoder {
public:
	static constexpr int kMidiOffset = 21;
	static constexpr std::size_t kLookaheadFrames = 22;
	static constexpr std::size_t kCausalFrame = BasicPitchOnnxOutput::kFrames - kLookaheadFrames;
	static constexpr float kFrameThreshold = 0.30f;
	static constexpr std::size_t kMinimumStableFrames = 7;

	BasicPitchCausalNotes decode(const BasicPitchOnnxOutput &output) const;
};

} // namespace mao
