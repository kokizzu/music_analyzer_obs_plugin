#pragma once
#include "piano_guitar_model_data.hpp"
#include <algorithm>
#include <array>
#include <cmath>

namespace mao { namespace piano_guitar_model {
using Features = std::array<double, 62>;

inline bool eligible_scores(double keyboard, double guitar, double voice, bool vocal_profile)
{
	return !vocal_profile && std::isfinite(keyboard) && std::isfinite(guitar) && std::isfinite(voice) &&
		keyboard >= .9 && keyboard <= 1 && guitar >= 0 && guitar <= .05 && voice >= 0 && voice <= .05;
}

inline double tree_lower_probability(const Features &values, int index)
{
	if (index < 0 || index >= static_cast<int>(nodes.size())) return 0.;
	const auto &node = nodes[static_cast<std::size_t>(index)];
	if (node.feature < 0) return node.probability;
	if (node.feature >= static_cast<int>(values.size())) return 0.;
	const double value = values[static_cast<std::size_t>(node.feature)];
	const double epsilon = (1 + std::abs(value)) * uncertainty;
	if (value + epsilon <= node.threshold) return tree_lower_probability(values, node.left);
	if (value - epsilon > node.threshold) return tree_lower_probability(values, node.right);
	return std::min(tree_lower_probability(values, node.left), tree_lower_probability(values, node.right));
}

inline double lower_probability(const Features &raw)
{
	Features values{};
	for (std::size_t i = 0; i < raw.size(); ++i) {
		if (!std::isfinite(raw[i])) return 0.;
		values[i] = i < 29 ? std::copysign(std::log1p(std::abs(raw[i])), raw[i]) : raw[i];
	}
	double total = 0.;
	for (int root : roots) total += tree_lower_probability(values, root);
	return total / roots.size();
}

inline bool should_remove_duplicate(const Features &raw, bool vocal_profile)
{
	// Caller must first verify this MIDI is currently visible in both Keyboard
	// and Guitar, and must keep the Keyboard cell. This is never a pitch veto.
	return eligible_scores(raw[6], raw[7], raw[8], vocal_profile) && lower_probability(raw) >= threshold;
}
}} // namespace mao::piano_guitar_model
