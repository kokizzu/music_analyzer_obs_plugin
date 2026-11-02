#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao::duration {
// Experimental: short-window amplitude must also have phase-derived pitch
// within 25 cents. Original-display latches and long-window evidence are retained.
class PhaseLowKeyboard {
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
	struct Window {
		std::vector<double> centered;
		const std::vector<double> *hann;
		double denominator;
	};
	Window window(std::size_t length, std::size_t end, unsigned scale)
	{
		auto &hann = geometry_[scale].hann;
		if (hann.size() != length) {
			hann.resize(length);
			for (std::size_t i = 0; i < length; ++i)
				hann[i] = .5 - .5 * std::cos(2 * 3.14159265358979323846 * i / (length - 1));
		}
		const auto offset = end - length;
		double weight = 0, mean = 0, square = 0;
		for (std::size_t i = 0; i < length; ++i) { weight += hann[i]; mean += hann[i] * history_[offset + i]; }
		mean /= weight;
		Window result{std::vector<double>(length), &hann, 1};
		for (std::size_t i = 0; i < length; ++i) {
			result.centered[i] = history_[offset + i] - mean;
			square += hann[i] * result.centered[i] * result.centered[i];
		}
		result.denominator = weight * std::max(1e-12, std::sqrt(2 * square / weight));
		return result;
	}
	std::complex<double> projection(int midi, int harmonic, const Window &input) const
	{
		const double frequency = 440 * std::pow(2., (midi - 69) / 12.) * harmonic;
		const double omega = 2 * 3.14159265358979323846 * frequency / rate_;
		const double cosine = std::cos(omega), sine = std::sin(omega);
		double first = 0, second = 0;
		for (std::size_t i = 0; i < input.centered.size(); ++i) {
			const double next = input.centered[i] * (*input.hann)[i] + 2 * cosine * first - second;
			second = first; first = next;
		}
		return std::polar(1., -omega * (input.centered.size() - 1)) *
			std::complex<double>(first - cosine * second, sine * second) * (2 / input.denominator);
	}
	bool short_support(int midi, int harmonic, const Window &current, const Window &previous) const
	{
		const auto now = projection(midi, harmonic, current);
		if (std::abs(now) < .01) return false;
		const auto before = projection(midi, harmonic, previous);
		if (std::abs(before) < .01) return false;
		const double frequency = 440 * std::pow(2., (midi - 69) / 12.) * harmonic;
		const double hop_seconds = std::lround(rate_ * .05) / double(rate_);
		const double step = 2 * 3.14159265358979323846 * hop_seconds;
		const double residual = std::arg(now * std::conj(before) * std::polar(1., -frequency * step));
		const double cents = 1200 * std::log2((frequency + residual / step) / frequency);
		return std::isfinite(cents) && std::abs(cents) <= 25;
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
		bool needed = false;
		for (std::size_t i = 0; i < displayed.size(); ++i) needed |= displayed[i] && !latched_[i];
		const std::size_t short_length = std::size_t(std::lround(rate_ * .1));
		const std::size_t hop = std::size_t(std::lround(rate_ * .05));
		if (needed && elapsed_ >= short_length + hop && history_.size() >= short_length + hop) {
			const auto current = window(short_length, history_.size(), 0);
			const auto previous = window(short_length, history_.size() - hop, 0);
			for (std::size_t i = 0; i < displayed.size(); ++i) {
				if (!displayed[i] || latched_[i]) continue;
				latched_[i] = short_support(int(i) + 21, 1, current, previous) ||
					short_support(int(i) + 21, 3, current, previous);
			}
		}
		needed = false;
		for (std::size_t i = 0; i < displayed.size(); ++i) needed |= displayed[i] && !latched_[i];
		const std::size_t long_length = std::size_t(std::lround(rate_ * .4));
		if (needed && elapsed_ >= long_length && history_.size() >= long_length) {
			const auto current = window(long_length, history_.size(), 1);
			for (std::size_t i = 0; i < displayed.size(); ++i) {
				if (!displayed[i] || latched_[i]) continue;
				latched_[i] = std::abs(projection(int(i) + 21, 1, current)) >= .01 ||
					std::abs(projection(int(i) + 21, 3, current)) >= .01;
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
