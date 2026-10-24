#include "tempo_candidate_gate.hpp"
#include "pcm_tempo_selection.hpp"
#include <cstdio>
#include <random>

int main()
{
	using namespace mao::pcm_tempo;
	std::mt19937 generator(20261024);
	std::uniform_int_distribution<int> tempo(0, 240);
	int checked = 0, skipped = 0;
	for (int index = 0; index < 250000; ++index) {
		const double actual = tempo(generator) / 2.;
		BandTempos energy{}, spectral{};
		const int around = static_cast<int>(actual * 2);
		for (auto &value : energy) value = std::max(0, around + tempo(generator) % 11 - 5);
		for (auto &value : spectral) value = tempo(generator);
		if (index % 3 == 0) spectral[0] = spectral[1] = around;
		std::array<double, 3> native{double(tempo(generator)), double(tempo(generator)), double(tempo(generator))};
		if (index % 4 == 0) native[0] = actual;
		const double original = select_upward(actual, energy, native, spectral);
		const bool possible = upward_pcm_support_possible(actual, native, spectral);
		const double optimized = possible ? original : actual;
		if (actual <= 112 && original != optimized) {
			std::fprintf(stderr, "unsafe early veto at %.2f\n", actual);
			return 1;
		}
		skipped += !possible;
		++checked;
	}
	if (upward_pcm_support_possible(100, {0, 0, 0}, {0, 200, 0, 0}) ||
	    !upward_pcm_support_possible(100, {0, 0, 0}, {192, 200, 0, 0}) ||
	    upward_pcm_support_possible(100, {104, 0, 0}, {200, 200, 0, 0})) return 1;
	std::printf("tempo candidate gate: %d paired cases, %d safely skipped\n", checked, skipped);
}
