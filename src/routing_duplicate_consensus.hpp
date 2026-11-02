#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

namespace mao::routing {
// Three 100ms windows at a 50ms hop include two nonoverlapping windows.
// Calls which do not finish a valid prediction frame break corroboration.
template <std::size_t N> class DuplicateConsensus {
public:
	using Mask = std::array<bool, N>;
	void reset() { hits_ = {}; pending_ = seen_drop_ = false; dropped_ = 0; }
	void begin_frame(std::uint64_t dropped)
	{
		if (pending_ || (seen_drop_ && dropped_ != dropped)) hits_ = {};
		pending_ = seen_drop_ = true;
		dropped_ = dropped;
	}
	Mask confirm(const Mask &prediction)
	{
		Mask result{};
		for (std::size_t i = 0; i < N; ++i) {
			hits_[i] = prediction[i] ? static_cast<std::uint8_t>(hits_[i] < 3 ? hits_[i] + 1 : 3) : 0;
			result[i] = hits_[i] == 3;
		}
		pending_ = false;
		return result;
	}
private:
	std::array<std::uint8_t, N> hits_{};
	std::uint64_t dropped_ = 0;
	bool pending_ = false, seen_drop_ = false;
};
}
