#include "src/windows_hardware_worker.hpp"

#include <atomic>
#include <cassert>
#include <chrono>
#include <mutex>
#include <string_view>
#include <thread>
#include <vector>

namespace {

struct FakeBackend {
	std::atomic<bool> present{true};
	std::atomic<bool> succeed{true};
	std::mutex mutex;
	std::vector<int> writes;
	int close_count = 0;

	static bool is_present(void *context)
	{
		return static_cast<FakeBackend *>(context)->present.load(std::memory_order_acquire);
	}

	static bool send(void *context, int root, mao::RootControlMode,
				const mao::HardwareWorkerProbe &probe)
	{
		auto *backend = static_cast<FakeBackend *>(context);
		if (!probe.current())
			return true;
		if (!backend->present.load(std::memory_order_acquire) ||
		    !backend->succeed.load(std::memory_order_acquire))
			return false;
		std::lock_guard<std::mutex> lock(backend->mutex);
		backend->writes.push_back(root);
		return true;
	}

	static void close(void *context)
	{
		auto *backend = static_cast<FakeBackend *>(context);
		std::lock_guard<std::mutex> lock(backend->mutex);
		++backend->close_count;
	}

	std::vector<int> written_roots()
	{
		std::lock_guard<std::mutex> lock(mutex);
		return writes;
	}
};

struct FakeStatus {
	static void publish(const char *, mao::WindowsHardwareStatusState &state, bool connected,
				    const char *reason)
	{
		mao::WindowsHardwareStatusReason code = mao::WindowsHardwareStatusReason::Unknown;
		if (reason && std::string_view(reason) == "device-missing")
			code = mao::WindowsHardwareStatusReason::DeviceMissing;
		else if (reason && std::string_view(reason) == "output-sent")
			code = mao::WindowsHardwareStatusReason::OutputSent;
		else if (reason && std::string_view(reason) == "output-failed")
			code = mao::WindowsHardwareStatusReason::OutputFailed;
		else if (reason && std::string_view(reason) == "worker-exception")
			code = mao::WindowsHardwareStatusReason::WorkerException;
		else if (reason && std::string_view(reason) == "worker-stopped")
			code = mao::WindowsHardwareStatusReason::WorkerStopped;
		state.record(connected, code);
	}
};

bool wait_for_writes(FakeBackend &backend, std::size_t count)
{
	for (int attempt = 0; attempt < 200; ++attempt) {
		if (backend.written_roots().size() >= count)
			return true;
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	return false;
}

bool wait_for_failures(mao::WindowsHardwareStatusState &status, std::uint64_t count)
{
	for (int attempt = 0; attempt < 200; ++attempt) {
		if (status.snapshot().failures >= count)
			return true;
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	return false;
}

void run_fake_backend(const char *device)
{
	mao::WindowsHardwareWorkerState state;
	FakeBackend backend;
	mao::WindowsHardwareStatusState status;
	const mao::HardwareWorkerBackend adapter = {
		&backend, &FakeBackend::is_present, &FakeBackend::send, &FakeBackend::close,
	};
	std::thread worker([&]() {
		mao::run_hardware_worker(state, adapter, device, status, &FakeStatus::publish);
	});

	state.update(7, mao::RootControlMode::Auto);
	assert(wait_for_writes(backend, 1));
	state.update(2, mao::RootControlMode::Manual);
	assert(wait_for_writes(backend, 2));

	backend.present = false;
	state.notify_device_change();
	assert(wait_for_failures(status, 2));
	backend.present = true;
	state.notify_device_change();
	assert(wait_for_writes(backend, 3));
	state.request_stop();
	worker.join();

	const std::vector<int> roots = backend.written_roots();
	assert((roots == std::vector<int>{7, 2, 2}));
	assert(backend.close_count >= 1);
	const auto snapshot = status.snapshot();
	assert(snapshot.connected == false);
	assert(snapshot.reason == mao::WindowsHardwareStatusReason::WorkerStopped);
	assert(snapshot.transitions >= 3);
	assert(snapshot.failures >= 2);
}

} // namespace

int main()
{
	mao::HardwareWorkerLifecycleState lifecycle;
	assert(lifecycle.begin_start());
	assert(!lifecycle.begin_start());
	lifecycle.mark_running();
	assert(lifecycle.begin_stop());
	lifecycle.finish_stop();
	assert(lifecycle.state() == mao::HardwareWorkerLifecycle::Stopped);
	assert(!lifecycle.begin_stop());

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

	run_fake_backend("midi");
	run_fake_backend("litejam");
	run_fake_backend("fret-zealot");
	return 0;
}
