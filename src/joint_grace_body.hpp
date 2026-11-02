#pragma once
#include "analyzer.hpp"
#include <cstddef>

namespace mao::joint {
inline bool stable_body(const FullMixDebugCandidate *candidates, std::size_t count, int midi)
{
	if (!candidates) return false;
	const FullMixDebugCandidate *best = nullptr;
	for (std::size_t i = 0; i < count; ++i) {
		const auto &row = candidates[i];
		if (row.midi != midi) continue;
		if (!best || double(row.keyboard_score) + .01 * row.ownership_confidence >
			double(best->keyboard_score) + .01 * best->ownership_confidence) best = &row;
	}
	return best && !best->vocal_tone_profile_supported && best->pitch_stability >= .75 &&
		best->onset_strength <= .1 && best->decay_rate <= .15;
}
}
