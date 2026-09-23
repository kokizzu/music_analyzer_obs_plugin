#pragma once

#include <atomic>
#include <cstdint>

namespace mao {

enum class WindowsHardwareStatusReason : std::uint8_t {
	Unknown,
	DeviceMissing,
	OutputSent,
	OutputFailed,
	WorkerException,
	WorkerStopped,
};

struct WindowsHardwareDeviceStatus {
	bool connected = false;
	WindowsHardwareStatusReason reason = WindowsHardwareStatusReason::Unknown;
	std::uint64_t transitions = 0;
	std::uint64_t failures = 0;
};

struct WindowsHardwareStatusChange {
	bool connection_changed = false;
	bool reason_changed = false;
};

class WindowsHardwareStatusState {
public:
	WindowsHardwareStatusChange record(bool new_connected, WindowsHardwareStatusReason new_reason) noexcept
	{
		const bool previous_connected = connected.exchange(new_connected, std::memory_order_acq_rel);
		const auto previous_reason = reason.exchange(new_reason, std::memory_order_acq_rel);
		const WindowsHardwareStatusChange change{
			previous_connected != new_connected,
			previous_reason != new_reason,
		};
		if (change.connection_changed)
			transitions.fetch_add(1, std::memory_order_relaxed);
		if (new_reason == WindowsHardwareStatusReason::DeviceMissing ||
		    new_reason == WindowsHardwareStatusReason::OutputFailed ||
		    new_reason == WindowsHardwareStatusReason::WorkerException)
			failures.fetch_add(1, std::memory_order_relaxed);
		return change;
	}

	WindowsHardwareDeviceStatus snapshot() const noexcept
	{
		return {
			connected.load(std::memory_order_acquire),
			reason.load(std::memory_order_acquire),
			transitions.load(std::memory_order_acquire),
			failures.load(std::memory_order_acquire),
		};
	}

	std::atomic<bool> connected{false};
	std::atomic<WindowsHardwareStatusReason> reason{WindowsHardwareStatusReason::Unknown};
	std::atomic<std::uint64_t> transitions{0};
	std::atomic<std::uint64_t> failures{0};
};

} // namespace mao
