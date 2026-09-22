#pragma once

#include "fret_control.hpp"

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

} // namespace mao
