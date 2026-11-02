#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

namespace mao::joint {
template<std::size_t Size> class OriginalDisplayHistory {
	std::array<unsigned char, Size> counts_{};
	uint64_t drops_ = 0;
	bool have_drops_ = false, pending_ = false;
public:
	using Mask = std::array<bool, Size>;
	void reset() { counts_ = {}; have_drops_ = pending_ = false; }
	void begin(uint64_t drops)
	{
		if (pending_ || (have_drops_ && drops != drops_)) counts_ = {};
		drops_ = drops; have_drops_ = pending_ = true;
	}
	bool preceded(std::size_t index) const { return pending_ && index < Size && counts_[index] >= 3; }
	void finish(const Mask &original)
	{
		if (!pending_) return;
		for (std::size_t i = 0; i < Size; ++i) counts_[i] = original[i] ? (counts_[i] < 3 ? counts_[i] + 1 : 3) : 0;
		pending_ = false;
	}
};
}
