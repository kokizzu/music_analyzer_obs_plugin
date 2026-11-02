#include "low_keyboard_coherence.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <vector>

int main()
{
	using Evidence = mao::duration::LowKeyboardCoherence;
	constexpr unsigned rate = 16000, hop = 800, window = 1600;
	constexpr double pi = 3.14159265358979323846;
	std::vector<float> values(rate * 2);
	for (std::size_t i = 0; i < values.size(); ++i)
		values[i] = float(.3 * std::sin(2 * pi * 1000 * i / rate) +
			(i < rate * .6 ? .03 * std::sin(2 * pi * 65.406391325 * i / rate) : 0));
	Evidence::Mask shown{}; shown[15] = true;
	Evidence state;
	for (unsigned end = window; end <= rate * 1.3; end += hop) {
		state.feed(values.data() + end - window, window, rate, 0);
		if (state.finish(shown)[15]) { std::cerr << "Continuous decay lost latched fundamental evidence\n"; return 1; }
	}
	// Absence breaks the latch; the old real note cannot protect a later ghost.
	for (unsigned end = unsigned(rate * 1.35); end <= rate * 1.4; end += hop) {
		state.feed(values.data() + end - window, window, rate, 0);
		state.finish({});
	}
	bool rejected = false;
	for (unsigned end = unsigned(rate * 1.45); end <= rate * 1.8; end += hop) {
		state.feed(values.data() + end - window, window, rate, 0);
		rejected = state.finish(shown)[15];
	}
	if (!rejected) return 2;
	state.feed(values.data() + rate * 2 - window, window, rate, 1);
	if (state.finish(shown)[15]) return 3; // A dropped window breaks prior evidence.
	for (auto &v : values) v = .2f;
	for (unsigned i = 0; i < 12; ++i) {
		state.feed(values.data(), window, rate, 1);
		rejected = state.finish(shown)[15];
	}
	if (!rejected) return 7;
	state.feed(values.data(), window, rate, 2); // Same exact overlap, changed drop count.
	if (state.finish(shown)[15]) return 8;
	state.feed(values.data(), window, rate, 1);
	state.feed(values.data(), window, rate, 1); // Unfinished analysis invalidates history.
	if (state.finish(shown)[15]) return 4;
	values[0] = std::numeric_limits<float>::quiet_NaN();
	if (state.feed(values.data(), window, rate, 1) || state.finish(shown)[15]) return 5;
	for (unsigned changed_rate : {44100U, 48000U}) {
		std::vector<float> steady(changed_rate / 10, .2f);
		state.feed(steady.data(), steady.size(), changed_rate, 1);
		if (state.finish(shown)[15]) return 9;
		for (unsigned i = 0; i < 12; ++i) {
			state.feed(steady.data(), steady.size(), changed_rate, 1);
			rejected = state.finish(shown)[15];
		}
		if (!rejected) return 10;
	}
	state.reset();
	for (std::size_t i = 0; i < values.size(); ++i)
		values[i] = float(.3 * std::sin(2 * pi * 1000 * i / rate) + .03 * std::sin(2 * pi * 3 * 65.406391325 * i / rate));
	for (unsigned end = window; end <= rate; end += hop) {
		state.feed(values.data() + end - window, window, rate, 0);
		if (state.finish(shown)[15]) return 6; // A missing fundamental may have a coherent third.
	}
	std::cout << "Coherence history: continuous decay, absence, drop, unfinished frame, nonfinite input and missing fundamental passed\n";
}
