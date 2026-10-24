#pragma once
#include "keyboard_voice_model_data.hpp"
#include <algorithm>
#include <array>
#include <cmath>

namespace mao {
namespace keyboard_voice_model {
using Features = std::array<double, 14>;

inline bool has_local_keyboard_triad(int target, const int *midis, std::size_t count)
{
	for (std::size_t a = 0; a < count; ++a) for (std::size_t b = a + 1; b < count; ++b) {
		const std::array<int, 3> notes = {target, midis[a], midis[b]};
		const auto bounds = std::minmax_element(notes.begin(), notes.end());
		if (*bounds.second - *bounds.first > 12) continue;
		for (int root : notes) {
			std::array<int, 3> intervals{};
			for (std::size_t i = 0; i < notes.size(); ++i) intervals[i] = (notes[i] - root + 120) % 12;
			std::sort(intervals.begin(), intervals.end());
			if (intervals == std::array<int, 3>{0, 4, 7} || intervals == std::array<int, 3>{0, 3, 7} ||
			    intervals == std::array<int, 3>{0, 3, 6} || intervals == std::array<int, 3>{0, 4, 8}) return true;
		}
	}
	return false;
}

// Input captures use six significant decimal digits. Return the lowest
// probability over both branches near a rounding boundary: native full-precision
// features must never make suppression more aggressive than calibration.
inline double tree_lower_probability(const Features &values, int index)
{
	if (index < 0 || index >= static_cast<int>(nodes.size())) return 0.;
	const auto &node = nodes[static_cast<std::size_t>(index)];
	if (node.feature < 0) return node.probability;
	if (node.feature >= static_cast<int>(values.size())) return 0.;
	const double value = values[static_cast<std::size_t>(node.feature)];
	const double uncertainty = std::abs(value) * 1e-5;
	if (value + uncertainty <= node.threshold) return tree_lower_probability(values, node.left);
	if (value - uncertainty > node.threshold) return tree_lower_probability(values, node.right);
	return std::min(tree_lower_probability(values, node.left), tree_lower_probability(values, node.right));
}

inline double lower_probability(const Features &raw)
{
	Features values{};
	for (std::size_t i = 0; i < values.size(); ++i) {
		if (!std::isfinite(raw[i])) return 0.;
		values[i] = std::copysign(std::log1p(std::abs(raw[i])), raw[i]);
	}
	double total = 0.;
	for (int root : roots) total += tree_lower_probability(values, root);
	return total / roots.size();
}

inline bool should_suppress(const Features &values, bool keyboard_owner, double keys,
                           double guitar, double voice, bool voice_profile)
{
	if (!keyboard_owner || voice_profile || !std::isfinite(keys) || !std::isfinite(guitar) ||
	    !std::isfinite(voice) || keys < .9 || keys > 1. || guitar < 0. || guitar > .05 || voice < 0. || voice > .05 ||
	    !(values[4] >= .7) || !(values[5] >= .5)) return false;
	return lower_probability(values) >= threshold;
}
} // namespace keyboard_voice_model
} // namespace mao
