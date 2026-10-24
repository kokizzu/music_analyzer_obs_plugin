#pragma once

#include <array>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao {
namespace pcm_tempo {
using BandTempos = std::array<int, 4>;

struct Peak {
	double time;
	double strength;
};

// All PCM novelty peaks use the reference scorer's drum/body mask and quality.
inline int estimate_tempo(const std::vector<Peak> &peaks)
{
	if (peaks.size() < 3 || peaks.back().time - peaks.front().time < .45) return 0;
	double total = 0, best = 0;
	std::vector<double> roots(peaks.size());
	for (std::size_t i = 0; i < peaks.size(); ++i) {
		roots[i] = std::sqrt(std::max(peaks[i].strength, 0.0));
		total += roots[i];
	}
	// Peak strengths do not depend on the BPM hypothesis. Cache their exact
	// original arithmetic once, preserving summation order and tie behavior.
	// Real three-second novelty streams contain fewer than 20 peaks; bound the
	// quadratic cache and retain the on-demand path for arbitrary caller input.
	const bool cache_pairs = peaks.size() <= 64;
	std::vector<double> pair_weights(cache_pairs ? peaks.size() * peaks.size() : 0);
	if (cache_pairs) for (std::size_t a = 0; a < peaks.size(); ++a)
		for (std::size_t b = a + 1; b < peaks.size(); ++b)
			pair_weights[a * peaks.size() + b] = std::pow(peaks[a].strength * peaks[b].strength, .5);
	int winner = 0;
	std::vector<double> phase(peaks.size());
	for (int bpm = 50; bpm <= 220; ++bpm) {
		const double period = 60.0 / bpm;
		const double tolerance = std::clamp(period * .12, .035, .085);
		double score = 0;
		std::copy(roots.begin(), roots.end(), phase.begin());
		for (std::size_t older = 0; older < peaks.size(); ++older) {
			for (std::size_t newer = older + 1; newer < peaks.size(); ++newer) {
				const auto &a = peaks[older];
				const auto &b = peaks[newer];
				const double delta = b.time - a.time;
				const int beats = static_cast<int>(std::floor(delta / period + .5));
				if (beats < 1 || beats > 8) continue;
				const double error = std::abs(delta - beats * period);
				if (error > tolerance) continue;
				const double match = 1 - error / tolerance;
				const double weight = cache_pairs ? pair_weights[older * peaks.size() + newer] : std::pow(a.strength * b.strength, .5);
				score += weight * (beats == 1 ? 1 : .18) * match * match;
				phase[older] += roots[newer] * match;
				phase[newer] += roots[older] * match;
			}
		}
		if (peaks.size() >= 4 && score > 0 && total > 1e-6)
			score *= .45 + .55 * std::clamp(*std::max_element(phase.begin(), phase.end()) / total, 0.0, 1.0);
		if (score > best) { best = score; winner = bpm; }
	}
	return winner;
}

inline int novelty_tempo(const std::vector<double> &values, double interval)
{
	const double maximum = values.empty() ? 0 : *std::max_element(values.begin(), values.end());
	std::vector<Peak> peaks;
	if (maximum > 1e-6) for (std::size_t i = 1; i + 1 < values.size(); ++i) {
		const double strength = values[i] / maximum;
		if (strength < .20 || values[i] < values[i - 1] || values[i] < values[i + 1]) continue;
		const Peak peak{(i + 1) * interval, strength};
		if (!peaks.empty() && peak.time - peaks.back().time < .16) {
			if (peak.strength > peaks.back().strength) peaks.back() = peak;
		} else peaks.push_back(peak);
	}
	return estimate_tempo(peaks);
}

// Experimental native port. Inputs must contain at most three causal seconds.
inline BandTempos energy_tempos(const float *samples, std::size_t count, uint32_t rate)
{
	if (!samples || rate < 8000 || rate > 192000 || count > static_cast<std::size_t>(rate) * 3) return {};
	const std::size_t hop = static_cast<std::size_t>(std::floor(rate * .01 + .5));
	const double interval = static_cast<double>(hop) / rate;
	constexpr double pi = 3.14159265358979323846;
	const double alpha_low = 1 - std::exp(-2 * pi * 200 / rate);
	const double alpha_mid = 1 - std::exp(-2 * pi * 2000 / rate);
	double low = 0, mid = 0;
	std::array<double, 4> energy = {};
	std::array<std::vector<double>, 4> envelopes;
	for (auto &envelope : envelopes) envelope.reserve(count / hop);
	for (std::size_t i = 0; i < count; ++i) {
		const double sample = samples[i];
		if (!std::isfinite(sample)) return {};
		low += alpha_low * (sample - low);
		mid += alpha_mid * (sample - mid);
		const std::array<double, 4> bands = {sample, low, mid - low, sample - mid};
		for (std::size_t b = 0; b < 4; ++b) energy[b] += bands[b] * bands[b];
		if ((i + 1) % hop == 0) {
			for (std::size_t b = 0; b < 4; ++b) envelopes[b].push_back(std::log1p(std::sqrt(energy[b] / hop) * 100));
			energy.fill(0);
		}
	}
	BandTempos result = {};
	for (std::size_t b = 0; b < 4; ++b) {
		const auto &envelope = envelopes[b];
		std::vector<double> novelty(envelope.size(), 0);
		for (std::size_t i = 1; i < envelope.size(); ++i) {
			const std::size_t n = std::min<std::size_t>(i, 5);
			std::array<double, 5> prior = {};
			std::copy(envelope.begin() + i - n, envelope.begin() + i, prior.begin());
			std::sort(prior.begin(), prior.begin() + n);
			const double median = n % 2 ? prior[n / 2] : (prior[n / 2 - 1] + prior[n / 2]) / 2;
			novelty[i] = std::max(0.0, envelope[i] - median);
		}
		result[b] = novelty_tempo(novelty, interval);
	}
	return result;
}
} // namespace pcm_tempo
} // namespace mao
