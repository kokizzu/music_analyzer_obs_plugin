#include "basic_pitch_pcm_history.hpp"

#include <array>
#include <cmath>
#include <cstdio>
#include <vector>

int main()
{
	mao::BasicPitchPcmHistory history;
	std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> snapshot = {};
	std::vector<float> constant(48000 * 3, 0.25f);
	if (!history.push(constant.data(), constant.size(), 48000, snapshot)) {
		std::fprintf(stderr, "basic_pitch_pcm_history: expected first complete snapshot\n");
		return 1;
	}
	for (float sample : snapshot) {
		if (std::abs(sample - 0.25f) > 0.002f) {
			std::fprintf(stderr, "basic_pitch_pcm_history: resampling drifted from the constant input\n");
			return 1;
		}
	}
	const std::vector<float> half_second(24000, -0.5f);
	if (!history.push(half_second.data(), half_second.size(), 48000, snapshot)) {
		std::fprintf(stderr, "basic_pitch_pcm_history: expected cadence snapshot\n");
		return 1;
	}
	history.reset();
	if (history.push(nullptr, 0, 48000, snapshot)) {
		std::fprintf(stderr, "basic_pitch_pcm_history: accepted an empty input\n");
		return 1;
	}
	std::printf("basic_pitch_pcm_history: samples=%zu stride=%zu\n", snapshot.size(),
		    mao::BasicPitchPcmHistory::kSnapshotStride);
	return 0;
}
