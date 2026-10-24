#include "native_timbre_features.hpp"
#include <chrono>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <limits>

int main(int argc, char **argv)
{
	mao::timbre::CepstralExtractor extractor;
	mao::timbre::Cepstra features{};
	if (argc == 4) {
		std::ifstream input(argv[1], std::ios::binary | std::ios::ate);
		if (!input) return 2;
		const auto bytes = input.tellg();
		if (bytes <= 0 || bytes % sizeof(float)) return 2;
		std::vector<float> samples(static_cast<std::size_t>(bytes) / sizeof(float));
		input.seekg(0);
		input.read(reinterpret_cast<char *>(samples.data()), bytes);
		std::ofstream output(argv[3]);
		output << std::setprecision(17);
		output << extractor.extract(samples.data(), samples.size(), static_cast<uint32_t>(std::stoul(argv[2])), features);
		for (double value : features) output << '\t' << value;
		output << '\n';
		return 0;
	}
	if (argc != 1) return 2;
	std::vector<float> samples(4800), scaled(4800);
	for (std::size_t i = 0; i < samples.size(); ++i) {
		samples[i] = .6f * std::sin(2 * 3.14159265358979323846 * 440 * i / 48000);
		scaled[i] = samples[i] * .1f;
	}
	mao::timbre::Cepstra quiet{};
	if (!extractor.extract(samples.data(), samples.size(), 48000, features) || !extractor.extract(scaled.data(), scaled.size(), 48000, quiet)) return 1;
	for (std::size_t i = 0; i < features.size(); ++i) if (std::abs(features[i] - quiet[i]) > 1e-5) return 1;
	const auto original = features;
	samples.resize(7200, .9f);
	if (!extractor.extract(samples.data(), 4800, 48000, features) || features != original) return 1;
	samples[0] = std::numeric_limits<float>::quiet_NaN();
	if (extractor.extract(samples.data(), 4800, 48000, features)) return 1;
	if (extractor.extract(nullptr, 0, 48000, features)) return 1;
	const auto start = std::chrono::steady_clock::now();
	for (int i = 0; i < 1000; ++i) extractor.extract(scaled.data(), scaled.size(), 48000, features);
	const double average = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count() / 1000;
	std::printf("Native cepstra: amplitude/causality/invalid-input checks passed; warm 48kHz mean %.4f ms\n", average);
}
