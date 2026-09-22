#include "src/windows_hardware_worker.hpp"

#include <atomic>
#include <cassert>
#include <chrono>
#include <thread>

int main()
{
	mao::WindowsHardwareWorkerState state;
	state.update(7, mao::RootControlMode::Auto);

	std::uint64_t attempted_revision = 0;
	std::uint64_t seen_device_generation = 0;
	mao::HardwareWorkerCommand command;
	assert(state.wait(attempted_revision, seen_device_generation, command));
	assert(command.root == 7);
	assert(command.revision == 1);
	assert(state.current(command.revision));

	state.update(2, mao::RootControlMode::Manual);
	assert(!state.current(command.revision));
	assert(state.wait(attempted_revision, seen_device_generation, command));
	assert(command.root == 2);
	assert(command.mode == mao::RootControlMode::Manual);

	const auto revision = command.revision;
	state.notify_device_change();
	assert(state.wait(attempted_revision, seen_device_generation, command));
	assert(command.revision == revision);
	assert(command.device_generation == 1);

	std::atomic<bool> stopped{false};
	std::thread waiter([&]() {
		mao::HardwareWorkerCommand ignored;
		std::uint64_t revision_to_wait = attempted_revision;
		std::uint64_t generation_to_wait = seen_device_generation;
		stopped = !state.wait(revision_to_wait, generation_to_wait, ignored);
	});
	std::this_thread::sleep_for(std::chrono::milliseconds(20));
	state.request_stop();
	waiter.join();
	assert(stopped.load());
	return 0;
}
