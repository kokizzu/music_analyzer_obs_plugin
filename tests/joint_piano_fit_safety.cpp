#include "joint_piano_fit.hpp"
#include <iostream>
#include <limits>
#include <memory>

int main()
{
	auto fitter = std::make_unique<mao::joint::PianoFitter>();
	mao::joint::FitOutput result;
	std::vector<float> audio(4800, 0);
	if (fitter->extract(audio.data(), 1600, 16000, result)) return 1;
	std::vector<double> dictionary(mao::joint::kPitches * mao::joint::kBins, 0);
	for (std::size_t i = 0; i < mao::joint::kPitches; ++i) dictionary[i * mao::joint::kBins + i] = 1;
	if (!fitter->configure(dictionary)) return 2;
	for (unsigned rate : {16000U, 44100U, 48000U}) {
		if (!fitter->extract(audio.data(), std::lround(rate * .1), rate, result)) return 3;
		for (double value : result.relative) if (value != 0) return 4;
	}
	if (fitter->extract(nullptr, 1600, 16000, result) || fitter->extract(audio.data(), 1599, 16000, result) ||
	    fitter->extract(audio.data(), 3200, 32000, result)) return 5;
	audio[0] = std::numeric_limits<float>::quiet_NaN();
	if (fitter->extract(audio.data(), 1600, 16000, result)) return 6;
	audio[0] = 0;
	if (fitter->configure({})) return 7;
	if (fitter->extract(audio.data(), 1600, 16000, result)) {
		std::cerr << "Rejected dictionary left stale model active\n"; return 8;
	}
	dictionary[0] = -1;
	if (fitter->configure(dictionary)) return 9;
	dictionary[0] = std::numeric_limits<double>::infinity();
	if (fitter->configure(dictionary)) return 10;
	dictionary[0] = .5;
	if (fitter->configure(dictionary)) return 11;
	std::cout << "Joint fitter safety: unconfigured, silence, rate switches, invalid audio and rejected dictionary passed\n";
}
