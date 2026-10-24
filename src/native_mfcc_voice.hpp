#pragma once
#include "keyboard_voice_classifier.hpp"
#include "native_mfcc_voice_model_data.hpp"
#include "native_timbre_features.hpp"
#include <string_view>

namespace mao { namespace native_mfcc_voice {
using Features = std::array<double, 38>;
static_assert(std::string_view(parent_sha256) == std::string_view(keyboard_voice_model::model_sha256),
              "Spectral verifier requires its frozen parent proposal model");

inline double tree_lower_probability(const Features &values, int index)
{
	if (index < 0 || index >= static_cast<int>(nodes.size())) return 0.;
	const auto &node = nodes[static_cast<std::size_t>(index)];
	if (node.feature < 0) return node.probability;
	if (node.feature >= static_cast<int>(values.size())) return 0.;
	const double value = values[static_cast<std::size_t>(node.feature)];
	const double epsilon = node.feature < 14 ? std::abs(value) * 1e-5 : (1. + std::abs(value)) * 1e-7;
	if (value + epsilon <= node.threshold) return tree_lower_probability(values, node.left);
	if (value - epsilon > node.threshold) return tree_lower_probability(values, node.right);
	return std::min(tree_lower_probability(values, node.left), tree_lower_probability(values, node.right));
}

inline double lower_probability(const keyboard_voice_model::Features &raw, const timbre::Cepstra &cepstra)
{
	Features values{};
	for (std::size_t i = 0; i < raw.size(); ++i) {
		if (!std::isfinite(raw[i])) return 0.;
		values[i] = std::copysign(std::log1p(std::abs(raw[i])), raw[i]);
	}
	for (std::size_t i = 0; i < cepstra.size(); ++i) {
		if (!std::isfinite(cepstra[i])) return 0.;
		values[i + raw.size()] = cepstra[i];
	}
	double total = 0.;
	for (int root : roots) total += tree_lower_probability(values, root);
	return total / roots.size();
}
}} // namespace mao::native_mfcc_voice
