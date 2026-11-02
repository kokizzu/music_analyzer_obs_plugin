#include "multiscale_low_keyboard.hpp"
#include "low_keyboard_coherence.hpp"
#include <cmath>
#include <iostream>
#include <vector>

int main()
{
	for (unsigned rate : {16000U, 44100U, 48000U}) {
		std::vector<float> audio(rate);
		for (std::size_t i = 0; i < audio.size(); ++i)
			audio[i] = float(.3 * std::sin(2 * 3.14159265358979323846 * 1000 * i / rate) +
				(i < rate * .15 ? .006 * std::sin(2 * 3.14159265358979323846 * 65.406391325 * i / rate) : 0));
		mao::duration::MultiScaleLowKeyboard candidate;
		mao::duration::LowKeyboardCoherence long_only;
		mao::duration::MultiScaleLowKeyboard::Mask visible{}; visible[15] = true;
		bool old_rejected = false;
		const auto hop = std::size_t(std::lround(rate * .05));
		const auto count = std::size_t(std::lround(rate * .1));
		for (std::size_t end = count; end <= audio.size(); end += hop) {
			if (!candidate.feed(audio.data() + end - count, count, rate, 0)) return 1;
			long_only.feed(audio.data() + end - count, count, rate, 0);
			if (candidate.finish(visible)[15]) return 2;
			old_rejected |= long_only.finish(visible)[15];
		}
		if (!old_rejected) return 3; // This fixture must expose the long-window blind spot.
	}
	std::cout << "Short-window evidence protects a brief note through continuous decay at all three rates\n";
}
