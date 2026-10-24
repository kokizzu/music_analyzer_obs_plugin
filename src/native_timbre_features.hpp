#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao { namespace timbre {
using Cepstra = std::array<double, 24>;

// Rate-dependent FFT/filter geometry is reused; audio history and predictions
// are not retained. Each call uses at most the last 100 ms of supplied PCM.
class CepstralExtractor {
	struct Bin { int a = -1, b = -1; double wa = 0., wb = 0.; };
	uint32_t rate_ = 0;
	std::size_t size_ = 0;
	std::vector<double> window_;
	std::vector<std::complex<double>> spectrum_;
	std::vector<std::size_t> reversed_;
	std::vector<std::vector<std::complex<double>>> twiddles_;
	std::vector<Bin> bins_;
	std::array<double, 26> weight_sums_{};
	std::array<std::array<double, 26>, 12> dct_{};
	void configure(uint32_t rate)
	{
		if (rate_ == rate) return;
		rate_ = rate;
		size_ = 1;
		while (size_ < static_cast<std::size_t>(std::lround(rate * .032))) size_ *= 2;
		constexpr double pi = 3.14159265358979323846;
		window_.resize(size_);
		spectrum_.resize(size_);
		reversed_.assign(size_, 0);
		for (std::size_t i = 0; i < size_; ++i) window_[i] = .5 - .5 * std::cos(2 * pi * i / (size_ - 1));
		for (std::size_t i = 1, j = 0; i < size_; ++i) {
			std::size_t bit = size_ >> 1;
			for (; j & bit; bit >>= 1) j ^= bit;
			j ^= bit;
			reversed_[i] = j;
		}
		twiddles_.clear();
		for (std::size_t length = 2; length <= size_; length *= 2) {
			std::vector<std::complex<double>> stage(length / 2);
			const auto rotation = std::polar(1., -2 * pi / length);
			std::complex<double> phase = 1.;
			for (auto &value : stage) { value = phase; phase *= rotation; }
			twiddles_.push_back(std::move(stage));
		}
		std::array<double, 28> edges{};
		const auto mel = [](double hz) { return 2595 * std::log10(1 + hz / 700); };
		const double low = mel(20), high = mel(std::min(8000., rate * .49));
		for (std::size_t i = 0; i < edges.size(); ++i)
			edges[i] = 700 * (std::pow(10., (low + (high - low) * i / 27.) / 2595) - 1);
		bins_.assign(size_ / 2 + 1, {});
		weight_sums_.fill(0);
		std::size_t segment = 0;
		for (std::size_t bin = 0; bin < bins_.size(); ++bin) {
			const double frequency = double(bin) * rate / size_;
			if (frequency < edges.front() || frequency > edges.back()) continue;
			while (segment < 26 && frequency >= edges[segment + 1]) ++segment;
			const double fraction = (frequency - edges[segment]) / (edges[segment + 1] - edges[segment]);
			auto &weights = bins_[bin];
			if (segment > 0) { weights.a = int(segment) - 1; weights.wa = 1 - fraction; weight_sums_[weights.a] += weights.wa; }
			if (segment < 26) { weights.b = int(segment); weights.wb = fraction; weight_sums_[weights.b] += weights.wb; }
		}
		for (std::size_t c = 0; c < dct_.size(); ++c)
			for (std::size_t m = 0; m < 26; ++m)
				dct_[c][m] = std::sqrt(2. / 26) * std::cos(pi * (m + .5) * (c + 1) / 26);
	}

public:
	bool extract(const float *samples, std::size_t count, uint32_t rate, Cepstra &output)
	{
		output.fill(0);
		if (!samples || rate < 8000 || rate > 192000) return false;
		const std::size_t used = std::min(count, static_cast<std::size_t>(std::lround(rate * .1)));
		if (!used) return false;
		samples += count - used;
		double maximum = 0;
		for (std::size_t i = 0; i < used; ++i) {
			if (!std::isfinite(samples[i])) return false;
			maximum = std::max(maximum, std::abs(double(samples[i])));
		}
		if (maximum < 1e-7) return false;
		configure(rate);
		if (used < size_) return false;
		std::array<std::size_t, 3> starts = {0, (used - size_) / 2, used - size_};
		std::array<double, 12> first{}, last{}, accumulated{};
		int frames = 0;
		std::size_t previous = used + 1;
		for (std::size_t start : starts) {
			if (start == previous) continue;
			previous = start;
			double mean = 0;
			for (std::size_t i = 0; i < size_; ++i) mean += samples[start + i];
			mean /= size_;
			for (std::size_t i = 0; i < size_; ++i) spectrum_[i] = (double(samples[start + i]) - mean) * window_[i];
			for (std::size_t i = 1; i < size_; ++i) if (i < reversed_[i]) std::swap(spectrum_[i], spectrum_[reversed_[i]]);
			std::size_t stage = 0;
			for (std::size_t length = 2; length <= size_; length *= 2, ++stage)
				for (std::size_t base = 0; base < size_; base += length)
					for (std::size_t j = 0; j < length / 2; ++j) {
						const auto even = spectrum_[base + j];
						const auto odd = spectrum_[base + j + length / 2] * twiddles_[stage][j];
						spectrum_[base + j] = even + odd;
						spectrum_[base + j + length / 2] = even - odd;
					}
			std::array<double, 26> energies{};
			for (std::size_t bin = 0; bin < bins_.size(); ++bin) {
				const double power = std::norm(spectrum_[bin]);
				const auto &weights = bins_[bin];
				if (weights.a >= 0) energies[weights.a] += weights.wa * power;
				if (weights.b >= 0) energies[weights.b] += weights.wb * power;
			}
			double total = 0;
			for (std::size_t m = 0; m < energies.size(); ++m) {
				energies[m] /= std::max(weight_sums_[m], 1e-12);
				total += energies[m];
			}
			if (total < 1e-20) continue;
			for (auto &value : energies) value = std::log(std::max(value / total, 1e-8));
			std::array<double, 12> cepstrum{};
			for (std::size_t c = 0; c < 12; ++c) {
				for (std::size_t m = 0; m < 26; ++m) cepstrum[c] += energies[m] * dct_[c][m];
				accumulated[c] += cepstrum[c];
			}
			if (!frames) first = cepstrum;
			last = cepstrum;
			++frames;
		}
		if (!frames) return false;
		for (std::size_t c = 0; c < 12; ++c) { output[c] = accumulated[c] / frames; output[c + 12] = last[c] - first[c]; }
		return true;
	}
};
}} // namespace mao::timbre
