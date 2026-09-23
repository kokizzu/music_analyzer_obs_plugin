#pragma once

#include "fret_control.hpp"
#include "windows_hardware_retry.hpp"
#include "windows_hardware_status.hpp"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <mutex>

namespace mao {

struct HardwareWorkerCommand {
	int root = -1;
	RootControlMode mode = RootControlMode::Auto;
	std::uint64_t revision = 0;
	std::uint64_t device_generation = 0;
};

struct HardwareWorkerProbe {
	const class WindowsHardwareWorkerState *state = nullptr;
	std::uint64_t revision = 0;

	bool current() const;
};

struct HardwareWorkerBackend {
	void *context = nullptr;
	bool (*present)(void *context) = nullptr;
	bool (*send)(void *context, int root, RootControlMode mode,
			 const HardwareWorkerProbe &probe) = nullptr;
	void (*close)(void *context) = nullptr;
};

using HardwareStatusPublisher = void (*)(const char *device, WindowsHardwareStatusState &state,
						 bool connected, const char *reason);

enum class HardwareWorkerLifecycle : std::uint8_t {
	Stopped,
	Starting,
	Running,
	Stopping,
};

class HardwareWorkerLifecycleState {
public:
	bool begin_start()
	{
		std::lock_guard<std::mutex> lock(mutex_);
		if (state_ != HardwareWorkerLifecycle::Stopped)
			return false;
		state_ = HardwareWorkerLifecycle::Starting;
		return true;
	}

	void mark_running()
	{
		{
			std::lock_guard<std::mutex> lock(mutex_);
			state_ = HardwareWorkerLifecycle::Running;
		}
		condition_.notify_all();
	}

	void mark_stopping_after_start_failure()
	{
		{
			std::lock_guard<std::mutex> lock(mutex_);
			state_ = HardwareWorkerLifecycle::Stopping;
		}
		condition_.notify_all();
	}

	bool begin_stop()
	{
		std::unique_lock<std::mutex> lock(mutex_);
		condition_.wait(lock, [this]() {
			return state_ != HardwareWorkerLifecycle::Starting &&
				state_ != HardwareWorkerLifecycle::Stopping;
		});
		if (state_ == HardwareWorkerLifecycle::Stopped)
			return false;
		state_ = HardwareWorkerLifecycle::Stopping;
		return true;
	}

	void finish_stop()
	{
		{
			std::lock_guard<std::mutex> lock(mutex_);
			state_ = HardwareWorkerLifecycle::Stopped;
		}
		condition_.notify_all();
	}

	HardwareWorkerLifecycle state() const
	{
		std::lock_guard<std::mutex> lock(mutex_);
		return state_;
	}

private:
	mutable std::mutex mutex_;
	std::condition_variable condition_;
	HardwareWorkerLifecycle state_ = HardwareWorkerLifecycle::Stopped;
};

// Shared command/reconnect state used by every output worker. The backend is
// deliberately outside this class, so tests can inject fake MIDI/BLE writers.
class WindowsHardwareWorkerState {
public:
	static constexpr auto kRetryInterval = std::chrono::seconds(2);

	void reset_for_start()
	{
		std::lock_guard<std::mutex> lock(mutex_);
		stop_requested_ = false;
	}

	void update(int root, RootControlMode mode)
	{
		std::lock_guard<std::mutex> lock(mutex_);
		if (desired_root_ == root && desired_mode_ == mode)
			return;
		desired_root_ = root;
		desired_mode_ = mode;
		++desired_revision_;
		condition_.notify_all();
	}

	void notify_device_change()
	{
		device_generation_.fetch_add(1, std::memory_order_release);
		condition_.notify_all();
	}

	void request_stop()
	{
		std::lock_guard<std::mutex> lock(mutex_);
		stop_requested_ = true;
		condition_.notify_all();
	}

	bool wait(std::uint64_t &attempted_revision, std::uint64_t &seen_device_generation,
		  HardwareWorkerCommand &command)
	{
		std::unique_lock<std::mutex> lock(mutex_);
		condition_.wait_for(lock, kRetryInterval, [&]() {
			return stop_requested_ || desired_revision_ != attempted_revision ||
				device_generation_.load(std::memory_order_acquire) != seen_device_generation;
		});
		if (stop_requested_)
			return false;
		command.root = desired_root_;
		command.mode = desired_mode_;
		command.revision = desired_revision_;
		command.device_generation = device_generation_.load(std::memory_order_acquire);
		attempted_revision = command.revision;
		seen_device_generation = command.device_generation;
		return true;
	}

	bool current(std::uint64_t revision) const
	{
		std::lock_guard<std::mutex> lock(mutex_);
		return !stop_requested_ && desired_revision_ == revision;
	}

	std::condition_variable &condition() { return condition_; }
	std::atomic<std::uint64_t> &device_generation() { return device_generation_; }

private:
	mutable std::mutex mutex_;
	std::condition_variable condition_;
	std::atomic<std::uint64_t> device_generation_{0};
	bool stop_requested_ = false;
	int desired_root_ = -1;
	RootControlMode desired_mode_ = RootControlMode::Auto;
	std::uint64_t desired_revision_ = 0;
};

inline bool HardwareWorkerProbe::current() const
{
	return state && state->current(revision);
}

inline void run_hardware_worker(WindowsHardwareWorkerState &state,
				       const HardwareWorkerBackend &backend, const char *device,
				       WindowsHardwareStatusState &status, HardwareStatusPublisher publish)
{
	std::uint64_t attempted_revision = 0;
	std::uint64_t seen_device_generation = 0;
	std::uint64_t sent_revision = 0;
	std::uint64_t sent_device_generation = 0;
	std::uint64_t last_revision = 0;
	std::uint64_t last_device_generation = 0;
	HardwareRetryState retry;
	for (;;) {
		HardwareWorkerCommand command;
		if (!state.wait(attempted_revision, seen_device_generation, command))
			break;
		if (command.root < 0)
			continue;

		const auto now = HardwareRetryState::clock::now();
		if (command.revision != last_revision) {
			last_revision = command.revision;
			retry.force(now);
		}
		if (command.device_generation != last_device_generation) {
			last_device_generation = command.device_generation;
			retry.force(now);
		}
		if (!retry.ready(now))
			continue;

		const bool present = backend.present && backend.present(backend.context);
		if (!present && publish)
			publish(device, status, false, "device-missing");
		if (sent_revision != command.revision ||
		    sent_device_generation != command.device_generation || !present) {
			if (!state.current(command.revision))
				continue;
			const HardwareWorkerProbe probe{&state, command.revision};
			const bool write_succeeded = backend.send &&
				backend.send(backend.context, command.root, command.mode, probe);
			if (write_succeeded) {
				const bool current = state.current(command.revision);
				sent_revision = current ? command.revision : 0;
				sent_device_generation = current ? command.device_generation : 0;
				if (publish)
					publish(device, status, true, "output-sent");
				retry.succeeded(HardwareRetryState::clock::now());
			} else {
				if (backend.close)
					backend.close(backend.context);
				sent_revision = 0;
				sent_device_generation = 0;
				if (publish)
					publish(device, status, false, "output-failed");
				retry.failed(HardwareRetryState::clock::now());
			}
		} else {
			retry.succeeded(HardwareRetryState::clock::now());
		}
	}
	if (backend.close)
		backend.close(backend.context);
	if (publish)
		publish(device, status, false, "worker-stopped");
}

} // namespace mao
