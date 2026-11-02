#include "basic_pitch_pcm_history.hpp"
#include "basic_pitch_pcm_history_primary.hpp"
#include <array>
#include <cmath>
#include <iostream>
#include <vector>

int main()
{
	for (unsigned rate : {16000U, 44100U, 48000U}) {
		mao::BasicPitchPcmHistory dense;
		mao::PrimaryPitchPcmHistory primary;
		std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> a{}, b{};
		const auto hop = std::size_t(std::lround(rate * .05));
		std::vector<float> fresh(hop);
		unsigned regular = 0, frequent = 0;
		for (unsigned frame = 0; frame < 60; ++frame) {
			for (std::size_t i = 0; i < hop; ++i) {
				const auto t = (frame * hop + i) / double(rate);
				fresh[i] = float(.3 * std::sin(2 * 3.14159265358979323846 * 73.4 * t) + .1 * std::sin(2 * 3.14159265358979323846 * 997 * t));
			}
			const bool d = dense.push(fresh.data(), fresh.size(), rate, a);
			const bool p = primary.push(fresh.data(), fresh.size(), rate, b);
			frequent += d; regular += p;
			if (p && (!d || a != b)) return 1;
		}
		if (regular != 3 || frequent != 21) return 2;
	}
	std::cout << "Original and dense snapshots are bit-identical at every shared endpoint, all three rates\n";
}
