#include "native_timbre_features.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <vector>

int main()
{
	mao::timbre::CepstralExtractor cached;
	int cases = 0;
	for (unsigned rate : {16000u, 44100u, 48000u, 44100u}) {
		std::vector<float> audio(static_cast<std::size_t>(std::lround(rate * .1)));
		for (int seed = 0; seed < 8; ++seed) {
			for (std::size_t i = 0; i < audio.size(); ++i)
				audio[i] = static_cast<float>(.5 * std::sin((i + seed * 37) * (100. + seed * 91.) / rate * 6.283185307179586));
			mao::timbre::Cepstra warm{}, cold{};
			mao::timbre::CepstralExtractor fresh;
			assert(cached.extract(audio.data(), audio.size(), rate, warm));
			assert(fresh.extract(audio.data(), audio.size(), rate, cold));
			assert(warm == cold); // Exact values: no audio or prediction history.
			++cases;
		}
	}
	std::vector<float> invalid(4800, std::numeric_limits<float>::quiet_NaN());
	mao::timbre::Cepstra values;
	values.fill(42.);
	assert(!cached.extract(invalid.data(), invalid.size(), 48000, values));
	for (double value : values) assert(value == 0.);
	std::cout << "Cepstral cache: " << cases << " exact warm/cold parity cases, rate changes and invalid input passed\n";
}
