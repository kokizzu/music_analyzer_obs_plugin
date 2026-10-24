#pragma once
#include "pcm_tempo_evidence.hpp"

namespace mao {
namespace pcm_tempo {
// Experimental port of the measured correction. Does not change ownership,
// confidence or tracker state; live integration remains separately gated.
inline double upward_energy_candidate(double actual, const BandTempos &energy,
				      const std::array<double, 3> &native)
{
	if (!std::isfinite(actual) || actual <= 0) return actual;
	const auto limits = std::minmax_element(energy.begin(), energy.end());
	if (*limits.first <= 0 || *limits.second > 220 || *limits.second - *limits.first > 4) return actual;
	int sum = 0;
	for (int value : energy) sum += value;
	int candidate = sum / 4;
	const int remainder = sum % 4;
	// The Python reference rounds exact half-integer means to the even value.
	if (remainder > 2 || (remainder == 2 && candidate % 2)) ++candidate;
	if (candidate <= actual || std::abs(candidate - actual * 2) > 4) return actual;
	for (double hint : native) if (hint > 0 && std::abs(hint - actual) <= 4) return actual;
	return candidate;
}

inline double select_upward(double actual, const BandTempos &energy,
			    const std::array<double, 3> &native, const BandTempos &spectral)
{
	const double candidate = upward_energy_candidate(actual, energy, native);
	if (candidate == actual) return actual;
	if (spectral[0] <= 0 || spectral[1] <= 0 ||
	    std::abs(spectral[0] - candidate) > 4 || std::abs(spectral[1] - candidate) > 4) return actual;
	return candidate;
}
} // namespace pcm_tempo
} // namespace mao
