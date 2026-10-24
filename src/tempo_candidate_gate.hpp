#pragma once
#include <array>
#include <cmath>

namespace mao {
namespace pcm_tempo {
// Necessary conditions for the existing upward-only PCM correction. Checking
// these before scanning three seconds of PCM cannot introduce a new estimate.
inline bool upward_pcm_support_possible(double actual, const std::array<double, 3> &native,
                                        const std::array<int, 4> &spectral)
{
	if (!std::isfinite(actual) || actual <= 0 || actual > 112) return false;
	for (double hint : native)
		if (hint > 0 && std::abs(hint - actual) <= 4) return false;
	if (spectral[0] <= 0 || spectral[1] <= 0) return false;
	// Energy candidate is within four BPM of twice the source; both spectral
	// votes must be within four BPM of that same candidate.
	return std::abs(spectral[0] - actual * 2) <= 8 &&
	       std::abs(spectral[1] - actual * 2) <= 8 &&
	       std::abs(spectral[0] - spectral[1]) <= 8;
}
} // namespace pcm_tempo
} // namespace mao
