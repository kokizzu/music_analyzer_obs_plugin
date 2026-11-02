#include "routing_duplicate_consensus.hpp"
#include <cassert>
#include <iostream>

int main()
{
	mao::routing::DuplicateConsensus<2> gate;
	const auto step = [&](bool first, bool second, std::uint64_t dropped = 0) {
		gate.begin_frame(dropped);
		return gate.confirm({first, second});
	};
	assert(!step(true, false)[0]);
	assert(!step(true, true)[0]);
	auto result = step(true, true);
	assert(result[0] && !result[1]);
	assert(step(false, true)[1]);
	assert(!step(true, false)[0]);
	gate.reset();
	assert(!step(true, false)[0]);
	assert(!step(true, false)[0]);
	assert(!step(true, false, 1)[0]); // Dropped audio breaks contiguous evidence.
	assert(!step(true, false, 1)[0]);
	assert(step(true, false, 1)[0]);
	gate.begin_frame(1); // Simulate an early-return/silent frame.
	assert(!step(true, false, 1)[0]);
	for (int i = 0; i < 1000; ++i) step(true, false, 1);
	assert(step(true, false, 1)[0]); // Saturates without counter overflow.
	step(false, false, 1);
	assert(!step(true, false, 1)[0]);
	std::cout << "Native duplicate consensus: confirmation, gaps, reset, dropped/unfinished frames and saturation passed\n";
}
