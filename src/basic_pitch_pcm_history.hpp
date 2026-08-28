#pragma once

#include "basic_pitch_onnx_runtime.hpp"

#include <array>
#include <cstddef>
#include <cstdint>

namespace mao {

// Causal linear-resampling history for the eventual ONNX worker.  It never
// allocates while pushing PCM and returns a snapshot no more than twice per
// second after the two-second model window is full.
class BasicPitchPcmHistory {
public:
	static constexpr uint32_t kTargetSampleRate = 22050;
	static constexpr std::size_t kSnapshotStride = kTargetSampleRate / 2;

	bool push(const float *samples, std::size_t count, uint32_t sample_rate,
		  std::array<float, BasicPitchOnnxRuntime::kInputSamples> &snapshot);
	void reset();

private:
	void append(float sample);

	std::array<float, BasicPitchOnnxRuntime::kInputSamples> ring_ = {};
	std::size_t write_index_ = 0;
	std::size_t available_ = 0;
	std::size_t since_snapshot_ = 0;
	uint32_t source_sample_rate_ = 0;
	uint64_t source_index_ = 0;
	double next_output_source_index_ = 0.0;
	float previous_sample_ = 0.0f;
	bool has_previous_sample_ = false;
};

} // namespace mao
