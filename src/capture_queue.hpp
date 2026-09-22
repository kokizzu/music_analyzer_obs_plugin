#pragma once
#include <algorithm>
#include <cstddef>
#include <vector>

namespace mao {
// Retain the newest audio when the consumer falls behind. Return the exact
// number of discarded samples so diagnostic logs account for discontinuities.
inline std::size_t append_capture_samples(std::vector<float> &queue,
	const std::vector<float> &block, std::size_t capacity)
{
	const auto total = queue.size() + block.size();
	const auto excess = total > capacity ? total - capacity : 0;
	const auto drop = std::min(excess, queue.size());
	queue.erase(queue.begin(), queue.begin() + drop);
	const auto keep = std::min(capacity, block.size());
	queue.insert(queue.end(), block.end() - keep, block.end());
	return excess;
}

// Keep the newest samples without moving the existing queue contents. The
// storage is resized only when the capture format changes or a stream opens.
class CaptureRingBuffer {
public:
	void reset(std::size_t capacity)
	{
		if (storage_.size() != capacity)
			storage_.assign(capacity, 0.0f);
		clear();
	}

	void clear() noexcept
	{
		head_ = 0;
		size_ = 0;
	}

	std::size_t append(const std::vector<float> &block) noexcept
	{
		return append(block.data(), block.size());
	}

	std::size_t append(const float *samples, std::size_t count) noexcept
	{
		if (!samples || count == 0)
			return 0;
		if (storage_.empty())
			return count;

		const std::size_t capacity = storage_.size();
		const std::size_t total = size_ + count;
		const std::size_t discarded = total > capacity ? total - capacity : 0;
		if (count >= capacity) {
			samples += count - capacity;
			count = capacity;
			head_ = 0;
			size_ = 0;
		} else if (discarded != 0) {
			head_ = (head_ + discarded) % capacity;
			size_ -= discarded;
		}

		for (std::size_t index = 0; index < count; ++index)
			storage_[(head_ + size_ + index) % capacity] = samples[index];
		size_ += count;
		return discarded;
	}

	void drain(std::vector<float> &samples)
	{
		samples.resize(size_);
		if (!storage_.empty()) {
			for (std::size_t index = 0; index < size_; ++index)
				samples[index] = storage_[(head_ + index) % storage_.size()];
		}
		clear();
	}

	std::size_t size() const noexcept { return size_; }
	std::size_t capacity() const noexcept { return storage_.size(); }

private:
	std::vector<float> storage_;
	std::size_t head_ = 0;
	std::size_t size_ = 0;
};
}
