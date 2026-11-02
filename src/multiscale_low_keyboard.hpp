#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao::duration {
// Experimental: short-window support protects brief notes before the longer
// measurement is ready. Decisions use only original display history.
class MultiScaleLowKeyboard {
	struct Geometry { std::vector<double> hann; };
	unsigned rate_ = 0;
	uint64_t drops_ = 0;
	std::size_t elapsed_ = 0;
	bool pending_ = false;
	std::vector<float> previous_, history_;
	std::array<Geometry, 2> geometry_{};
	std::array<unsigned, 19> stable_{};
public:
	using Mask = std::array<bool, 19>;
private:
	Mask latched_{};
	double amplitude(int midi, int harmonic, const std::vector<double> &centered,
			 const std::vector<double> &hann, double denominator) const
	{
		const double frequency = 440 * std::pow(2., (midi - 69) / 12.) * harmonic;
		const double coefficient = 2 * std::cos(2 * 3.14159265358979323846 * frequency / rate_);
		double first = 0, second = 0;
		for (std::size_t i = 0; i < centered.size(); ++i) {
			const double next = centered[i] * hann[i] + coefficient * first - second;
			second = first; first = next;
		}
		return std::sqrt(std::max(0., first * first + second * second - coefficient * first * second)) * 2 / denominator;
	}
public:
	void reset()
	{
		rate_ = 0; drops_ = 0; elapsed_ = 0; pending_ = false;
		previous_.clear(); history_.clear(); geometry_ = {};
		stable_ = {}; latched_ = {};
	}
	bool feed(const float *samples, std::size_t count, unsigned rate, uint64_t drops)
	{
		if (!samples || (rate != 16000 && rate != 44100 && rate != 48000) ||
		    count != std::size_t(std::lround(rate * .1))) { reset(); return false; }
		for (std::size_t i = 0; i < count; ++i)
			if (!std::isfinite(samples[i])) { reset(); return false; }
		const std::size_t hop = std::size_t(std::lround(rate * .05));
		bool continuous = rate_ == rate && !pending_ && drops_ == drops && previous_.size() == count;
		if (continuous) continuous = std::equal(previous_.begin() + hop, previous_.end(), samples);
		if (!continuous) {
			reset(); rate_ = rate; history_.assign(samples, samples + count);
		} else history_.insert(history_.end(), samples + count - hop, samples + count);
		drops_ = drops; previous_.assign(samples, samples + count);
		const std::size_t length = std::size_t(std::lround(rate * .4));
		if (history_.size() > length) history_.erase(history_.begin(), history_.end() - length);
		elapsed_ = std::min(length, elapsed_ + hop);
		pending_ = true;
		return true;
	}
	Mask finish(const Mask &displayed)
	{
		Mask rejected{};
		if (!pending_) return rejected;
		pending_ = false;
		for (std::size_t i = 0; i < displayed.size(); ++i)
			if (!displayed[i]) { stable_[i] = 0; latched_[i] = false; }
		for (unsigned scale = 0; scale < 2; ++scale) {
			const std::size_t length = std::size_t(std::lround(rate_ * (scale ? .4 : .1)));
			if (elapsed_ < length || history_.size() < length) continue;
			bool needed = false;
			for (std::size_t i = 0; i < displayed.size(); ++i) needed |= displayed[i] && !latched_[i];
			if (!needed) break;
			auto &hann = geometry_[scale].hann;
			if (hann.size() != length) {
				hann.resize(length);
				for (std::size_t i = 0; i < length; ++i)
					hann[i] = .5 - .5 * std::cos(2 * 3.14159265358979323846 * i / (length - 1));
			}
			const auto offset = history_.size() - length;
			double weight = 0, mean = 0, square = 0;
			for (std::size_t i = 0; i < length; ++i) { weight += hann[i]; mean += hann[i] * history_[offset + i]; }
			mean /= weight;
			std::vector<double> centered(length);
			for (std::size_t i = 0; i < length; ++i) {
				centered[i] = history_[offset + i] - mean;
				square += hann[i] * centered[i] * centered[i];
			}
			const double denominator = weight * std::max(1e-12, std::sqrt(2 * square / weight));
			for (std::size_t i = 0; i < displayed.size(); ++i) {
				if (!displayed[i] || latched_[i]) continue;
				latched_[i] = amplitude(int(i) + 21, 1, centered, hann, denominator) >= .01 ||
					amplitude(int(i) + 21, 3, centered, hann, denominator) >= .01;
			}
		}
		const bool ready = elapsed_ == std::size_t(std::lround(rate_ * .4));
		for (std::size_t i = 0; i < displayed.size(); ++i) {
			if (!displayed[i]) continue;
			rejected[i] = ready && stable_[i] >= 3 && !latched_[i];
			stable_[i] = std::min(3U, stable_[i] + 1);
		}
		return rejected;
	}
};
}
