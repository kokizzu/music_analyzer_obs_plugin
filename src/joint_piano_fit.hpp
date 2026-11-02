#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao::joint {
constexpr std::size_t kPitches = 88, kBins = 2049, kFft = 4096, kSamples = 1600;
struct FitOutput {
	std::array<double, kPitches> activation{}, projection{}, relative{}, explained{};
};

// Experimental current-window-only implementation of joint_pitch_reference.py.
// Dictionary columns are pitch-major and normalized by the reference producer.
class PianoFitter {
	std::vector<double> dictionary_;
	std::array<std::array<double, kPitches>, kPitches> gram_{};
	std::array<double, kSamples> hann_{};
	std::array<std::size_t, kFft> reversed_{};
	std::vector<std::vector<std::complex<double>>> twiddles_;
	std::array<std::complex<double>, kFft> fft_{};
public:
	bool configure(const std::vector<double> &columns)
	{
		dictionary_.clear();
		if (columns.size() != kPitches * kBins) return false;
		for (double value : columns) if (!std::isfinite(value) || value < 0) return false;
		for (std::size_t pitch = 0; pitch < kPitches; ++pitch) {
			double norm = 0;
			for (std::size_t i = 0; i < kBins; ++i) norm += columns[pitch * kBins + i] * columns[pitch * kBins + i];
			if (!std::isfinite(norm) || std::abs(norm - 1) > 1e-6) return false;
		}
		dictionary_ = columns;
		for (std::size_t a = 0; a < kPitches; ++a)
			for (std::size_t b = 0; b <= a; ++b) {
				double sum = 0;
				for (std::size_t i = 0; i < kBins; ++i) sum += columns[a * kBins + i] * columns[b * kBins + i];
				gram_[a][b] = gram_[b][a] = sum;
			}
		constexpr double pi = 3.14159265358979323846;
		for (std::size_t i = 0; i < kSamples; ++i) hann_[i] = .5 - .5 * std::cos(2 * pi * i / (kSamples - 1));
		for (std::size_t i = 1, j = 0; i < kFft; ++i) {
			std::size_t bit = kFft >> 1;
			for (; j & bit; bit >>= 1) j ^= bit;
			j ^= bit;
			reversed_[i] = j;
		}
		twiddles_.clear();
		for (std::size_t length = 2; length <= kFft; length *= 2) {
			std::vector<std::complex<double>> stage(length / 2);
			for (std::size_t j = 0; j < stage.size(); ++j) stage[j] = std::polar(1., -2 * pi * j / length);
			twiddles_.push_back(std::move(stage));
		}
		return true;
	}
	bool extract(const float *samples, std::size_t count, uint32_t rate, FitOutput &output)
	{
		output = {};
		if (dictionary_.empty() || !samples || (rate != 16000 && rate != 44100 && rate != 48000) ||
		    count != static_cast<std::size_t>(std::lround(rate * .1))) return false;
		for (std::size_t i = 0; i < count; ++i) if (!std::isfinite(samples[i])) return false;
		std::array<double, kSamples> resampled{};
		double mean = 0;
		for (std::size_t i = 0; i < kSamples; ++i) {
			const double position = double(i) * rate / 16000;
			const std::size_t a = static_cast<std::size_t>(position), b = std::min(a + 1, count - 1);
			resampled[i] = double(samples[a]) + (double(samples[b]) - samples[a]) * (position - a);
			mean += resampled[i];
		}
		mean /= kSamples;
		fft_.fill(0);
		for (std::size_t i = 0; i < kSamples; ++i) fft_[i] = (resampled[i] - mean) * hann_[i];
		for (std::size_t i = 1; i < kFft; ++i) if (i < reversed_[i]) std::swap(fft_[i], fft_[reversed_[i]]);
		std::size_t stage = 0;
		for (std::size_t length = 2; length <= kFft; length *= 2, ++stage)
			for (std::size_t base = 0; base < kFft; base += length)
				for (std::size_t j = 0; j < length / 2; ++j) {
					const auto even = fft_[base + j], odd = fft_[base + j + length / 2] * twiddles_[stage][j];
					fft_[base + j] = even + odd;
					fft_[base + j + length / 2] = even - odd;
				}
		std::array<double, kBins> magnitude{}, observed{};
		for (std::size_t i = 0; i < kBins; ++i) magnitude[i] = std::abs(fft_[i]);
		double norm = 0;
		for (std::size_t i = 0; i < kBins; ++i) {
			observed[i] = ((i ? magnitude[i-1] : 0) + 2 * magnitude[i] + (i + 1 < kBins ? magnitude[i+1] : 0)) / 4;
			norm += observed[i] * observed[i];
		}
		norm = std::max(std::sqrt(norm), 1e-12);
		for (auto &value : observed) value /= norm;
		for (std::size_t pitch = 0; pitch < kPitches; ++pitch) {
			for (std::size_t i = 0; i < kBins; ++i) output.projection[pitch] += dictionary_[pitch * kBins + i] * observed[i];
			output.activation[pitch] = std::max(output.projection[pitch], 1e-12);
		}
		for (unsigned iteration = 0; iteration < 80; ++iteration) {
			std::array<double, kPitches> next{};
			for (std::size_t a = 0; a < kPitches; ++a) {
				double denominator = 0;
				for (std::size_t b = 0; b < kPitches; ++b) denominator += gram_[a][b] * output.activation[b];
				next[a] = output.activation[a] * output.projection[a] / std::max(denominator, 1e-12);
			}
			output.activation = next;
		}
		const double maximum = std::max(*std::max_element(output.activation.begin(), output.activation.end()), 1e-12);
		for (std::size_t i = 0; i < kPitches; ++i) {
			output.relative[i] = output.activation[i] / maximum;
			output.explained[i] = output.activation[i] / std::max(output.projection[i], 1e-12);
		}
		return true;
	}
};
}
