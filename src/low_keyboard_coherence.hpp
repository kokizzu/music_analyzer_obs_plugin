#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <algorithm>
#include <cmath>
#include <vector>

namespace mao::duration {
// Experimental causal evidence, independent of detector envelopes.
class LowKeyboardCoherence {
	unsigned rate_ = 0;
	uint64_t drops_ = 0;
	std::size_t elapsed_ = 0;
	bool pending_ = false, valid_ = false;
	std::vector<float> previous_, history_;
	std::vector<double> hann_;
	std::array<unsigned, 19> stable_{};
public:
	using Mask = std::array<bool, 19>;
private:
	Mask latched_{};
	double amplitude(int midi, int harmonic, const std::vector<double> &centered, double denominator) const
	{
		const double frequency = 440 * std::pow(2., (midi - 69) / 12.) * harmonic;
		const double coefficient = 2 * std::cos(2 * 3.14159265358979323846 * frequency / rate_);
		double first = 0, second = 0;
		for (std::size_t i = 0; i < centered.size(); ++i) {
			const double next = centered[i] * hann_[i] + coefficient * first - second;
			second = first;
			first = next;
		}
		return std::sqrt(std::max(0., first * first + second * second - coefficient * first * second)) * 2 / denominator;
	}
public:
	void reset()
	{
		rate_ = 0; elapsed_ = 0; pending_ = valid_ = false;
		previous_.clear(); history_.clear(); hann_.clear();
		stable_ = {}; latched_ = {};
	}
	bool feed(const float *samples, std::size_t count, unsigned rate, uint64_t drops)
	{
		if (!samples || (rate != 16000 && rate != 44100 && rate != 48000) || count != std::size_t(std::lround(rate * .1))) {
			reset(); return false;
		}
		for (std::size_t i = 0; i < count; ++i) if (!std::isfinite(samples[i])) { reset(); return false; }
		const std::size_t hop = std::size_t(std::lround(rate * .05));
		bool continuous = rate_ == rate && !pending_ && drops_ == drops && previous_.size() == count;
		if (continuous)
			continuous = std::equal(previous_.begin() + hop, previous_.end(), samples);
		if (!continuous) {
			reset(); rate_ = rate;
			history_.assign(samples, samples + count);
		} else {
			history_.insert(history_.end(), samples + count - hop, samples + count);
		}
		drops_ = drops;
		previous_.assign(samples, samples + count);
		const std::size_t length = std::size_t(std::lround(rate * .4));
		if (history_.size() > length) history_.erase(history_.begin(), history_.end() - length);
		elapsed_ = std::min(length, elapsed_ + hop);
		valid_ = elapsed_ == length && history_.size() == length;
		pending_ = true;
		return true;
	}
	Mask finish(const Mask &displayed)
	{
		Mask rejected{};
		if (!pending_) return rejected;
		pending_ = false;
		std::vector<double> centered;
		double denominator = 1;
		if (valid_) {
			const std::size_t length = history_.size();
			if (hann_.size() != length) {
				hann_.resize(length);
				for (std::size_t i = 0; i < length; ++i) hann_[i] = .5 - .5 * std::cos(2 * 3.14159265358979323846 * i / (length - 1));
			}
			double weight = 0, mean = 0, square = 0;
			for (std::size_t i = 0; i < length; ++i) { weight += hann_[i]; mean += hann_[i] * history_[i]; }
			mean /= weight;
			centered.resize(length);
			for (std::size_t i = 0; i < length; ++i) { centered[i] = history_[i] - mean; square += hann_[i] * centered[i] * centered[i]; }
			denominator = weight * std::max(1e-12, std::sqrt(2 * square / weight));
		}
		for (std::size_t i = 0; i < displayed.size(); ++i) {
			if (!displayed[i]) { stable_[i] = 0; latched_[i] = false; continue; }
			if (valid_ && !latched_[i])
				latched_[i] = amplitude(int(i) + 21, 1, centered, denominator) >= .01 || amplitude(int(i) + 21, 3, centered, denominator) >= .01;
			rejected[i] = valid_ && stable_[i] >= 3 && !latched_[i];
			stable_[i] = std::min(3U, stable_[i] + 1);
		}
		return rejected;
	}
};
}
