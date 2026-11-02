#include "low_keyboard_coherence.hpp"
#include <cmath>
#include <iostream>
#include <vector>

int main()
{
	using Evidence = mao::duration::LowKeyboardCoherence;
	constexpr unsigned rate = 16000;
	constexpr double pi = 3.14159265358979323846;
	auto audio = [&](double frequency, double amplitude) {
		std::vector<float> values(rate);
		for (std::size_t i = 0; i < values.size(); ++i)
			values[i] = float(.3 * std::sin(2 * pi * 1000 * i / rate) + amplitude * std::sin(2 * pi * frequency * i / rate));
		return values;
	};
	auto unsupported = audio(1000, 0);
	Evidence state;
	Evidence::Mask displayed{};
	displayed[15] = true; // C2, MIDI 36.
	for (std::size_t endpoint = rate / 10; endpoint <= rate; endpoint += rate / 20) {
		if (!state.feed(unsupported.data() + endpoint - rate / 10, rate / 10, rate, 0)) return 1;
		const auto rejected = state.finish(displayed);
		if (endpoint < rate * .4 && rejected[15]) return 2;
		if (endpoint >= rate / 2 && !rejected[15]) {
			std::cerr << "Persistent low conjecture without coherent fundamental/third remained visible\n";
			return 3;
		}
	}
	state.reset();
	auto real = audio(65.406391325, .03);
	for (std::size_t endpoint = rate / 10; endpoint <= rate; endpoint += rate / 20) {
		state.feed(real.data() + endpoint - rate / 10, rate / 10, rate, 0);
		if (state.finish(displayed)[15]) return 4;
	}
	// Real evidence stays latched through a continuously displayed decay.
	for (unsigned i = 0; i < 12; ++i) {
		state.feed(unsupported.data(), rate / 10, rate, 0);
		// This intentionally discontinuous buffer must reset the latch.
		if (i == 0 && state.finish(displayed)[15]) return 5;
		else if (i != 0) state.finish(displayed);
	}
	state.reset();
	state.feed(nullptr, 0, rate, 0);
	if (state.finish(displayed)[15]) return 6;
	std::cout << "Coherence: causal warmup, unsupported conjecture, real fundamental and reset passed\n";
}
