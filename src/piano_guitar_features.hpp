#pragma once
#include "analyzer.hpp"
#include "native_timbre_features.hpp"
#include "piano_guitar_verifier.hpp"

namespace mao { namespace piano_guitar_model {
inline Features candidate_features(const FullMixDebugCandidate &c, const timbre::Cepstra &cepstra,
                                  const std::array<FullMixDebugCandidate, kFullMixDebugCandidateCount> &candidates,
                                  std::size_t candidate_count)
{
	Features raw = {c.ownership_confidence, c.onset_strength, c.decay_rate, c.pitch_stability,
		c.simultaneous_onset, c.bass_score, c.keyboard_score, c.guitar_score, c.vocal_score, c.other_score,
		c.spectral_level, c.pitch_confidence, c.periodicity, c.harmonicity, c.harmonic_fit_error,
		c.spectral_centroid, c.spectral_slope, c.local_noise_level, c.lower_octave_ratio, c.harmonic_product_score,
		c.lower_subharmonic_product_ratio, c.adjacent_lower_ratio, c.adjacent_upper_ratio, c.third_octave_ratio,
		c.harmonic_ratios[0], c.harmonic_ratios[1], c.harmonic_ratios[2], c.harmonic_ratios[3], c.harmonic_ratios[4]};
	std::copy(cepstra.begin(), cepstra.end(), raw.begin() + 29);
	const std::size_t limit = std::min(candidate_count, candidates.size());
	std::size_t count = 0, profiles = 0;
	int lowest = 128, highest = -1;
	for (std::size_t i = 0; i < limit; ++i) {
		const auto &candidate = candidates[i];
		if (candidate.midi < 0) continue;
		const int owner = static_cast<int>(candidate.owner);
		if (owner < 0 || owner >= 6 || candidate.midi > 127) return {};
		raw[53 + static_cast<std::size_t>(owner)] += 1.;
		profiles += candidate.vocal_tone_profile_supported ? 1 : 0;
		lowest = std::min(lowest, candidate.midi);
		highest = std::max(highest, candidate.midi);
		++count;
	}
	if (count) {
		for (std::size_t i = 53; i < 59; ++i) raw[i] /= count;
		raw[59] = double(profiles) / count;
		raw[60] = std::min(double(count) / 64., 1.);
		raw[61] = double(highest - lowest) / 127.;
	}
	return raw;
}
}} // namespace mao::piano_guitar_model
