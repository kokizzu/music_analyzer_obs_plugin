#include "src/capture_queue.hpp"

#include <cassert>
#include <vector>

int main()
{
	mao::CaptureRingBuffer queue;
	queue.reset(4);

	const std::vector<float> first = {1.0f, 2.0f, 3.0f};
	assert(queue.append(first) == 0);
	std::vector<float> drained;
	queue.drain(drained);
	assert((drained == std::vector<float>{1.0f, 2.0f, 3.0f}));

	const std::vector<float> wrapped = {4.0f, 5.0f, 6.0f};
	assert(queue.append(wrapped) == 0);
	const std::vector<float> tail = {7.0f, 8.0f};
	assert(queue.append(tail) == 1);
	queue.drain(drained);
	assert((drained == std::vector<float>{5.0f, 6.0f, 7.0f, 8.0f}));

	const std::vector<float> oversized = {9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f};
	assert(queue.append(oversized) == 2);
	queue.drain(drained);
	assert((drained == std::vector<float>{11.0f, 12.0f, 13.0f, 14.0f}));

	queue.reset(2);
	assert(queue.capacity() == 2);
	assert(queue.size() == 0);
	assert(queue.append(nullptr, 3) == 0);
	assert(queue.size() == 0);
	return 0;
}
