#include "joint_piano_fit.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>

int main(int argc, char **argv)
{
	if (argc != 5) return 2;
	std::ifstream model(argv[1], std::ios::binary), input(argv[2], std::ios::binary);
	std::ofstream output(argv[4], std::ios::binary);
	const unsigned rate = std::stoul(argv[3]);
	if (!model || !input || !output || (rate != 16000 && rate != 44100 && rate != 48000)) return 2;
	std::vector<double> dictionary(mao::joint::kPitches * mao::joint::kBins);
	if (!model.read(reinterpret_cast<char *>(dictionary.data()), dictionary.size() * sizeof(double))) return 3;
	auto fitter = std::make_unique<mao::joint::PianoFitter>();
	if (!fitter->configure(dictionary)) return 4;
	const std::size_t hop = std::lround(rate * .05), count = std::lround(rate * .1);
	std::vector<float> fresh(hop), window(count, 0);
	std::size_t frames = 0;
	double maximum_ms = 0, total_ms = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		mao::joint::FitOutput values;
		const auto begin = std::chrono::steady_clock::now();
		if (!fitter->extract(window.data(), window.size(), rate, values)) return 5;
		const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - begin).count();
		maximum_ms = std::max(maximum_ms, ms); total_ms += ms;
		for (const auto *array : {&values.activation, &values.projection, &values.relative, &values.explained})
			output.write(reinterpret_cast<const char *>(array->data()), array->size() * sizeof(double));
		++frames;
	}
	if (!frames || !input.eof() || !output) return 6;
	std::cout << std::setprecision(9) << frames << " frames, mean " << total_ms / frames << " ms, max " << maximum_ms << " ms\n";
}
