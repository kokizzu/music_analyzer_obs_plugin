#pragma once
#ifdef _WIN32
#include "windows_loopback.hpp"
#include "capture_queue.hpp"
#include <atomic>
#include <condition_variable>
#include <future>
#include <mutex>
#include <thread>
#include <chrono>

// COM and the endpoint stay on the capture thread. DSP/rendering only consume
// copies, so neither a slow analysis pass nor vsync can hold a WASAPI buffer.
class WindowsInputCapture {
	std::thread worker_;
	std::atomic<bool> stop_{false};
	std::atomic<bool> failed_{false};
	std::mutex mutex_;
	mao::CaptureRingBuffer queue_;
	std::mutex wake_mutex_;
	std::condition_variable wake_condition_;
	std::atomic<std::uint64_t> dropped_samples_{0};
public:
	~WindowsInputCapture() { close(); }
	void close()
	{
		stop_ = true;
		wake_condition_.notify_all();
		if (worker_.joinable()) worker_.join();
		std::lock_guard<std::mutex> lock(mutex_);
		queue_.clear();
	}
	bool open(const std::string &name, uint32_t &rate, bool diagnostics)
	{
		close();
		stop_ = false;
		failed_ = false;
		dropped_samples_ = 0;
		std::promise<uint32_t> opened;
		auto result = opened.get_future();
		try {
		worker_ = std::thread([this, name, diagnostics, start = std::move(opened)]() mutable {
			try {
				WindowsLoopback endpoint;
				std::wstring endpoint_id;
				uint32_t sample_rate = 48000;
				if (!endpoint.open(sample_rate, name.c_str())) { start.set_value(0); return; }
				endpoint_id = endpoint.device_id();
				endpoint.set_diagnostics(diagnostics);
				std::size_t capacity = std::max<uint32_t>(1, sample_rate / 4);
				{
					std::lock_guard<std::mutex> lock(mutex_);
					queue_.reset(capacity);
				}
				start.set_value(sample_rate);
				std::vector<float> block;
				block.reserve(sample_rate);
				auto last_overrun_log = std::chrono::steady_clock::time_point{};
				auto reopen = [&]() {
					constexpr auto kInitialDelay = std::chrono::milliseconds(250);
					constexpr auto kMaximumDelay = std::chrono::milliseconds(2000);
					auto delay = kInitialDelay;
					{
						std::lock_guard<std::mutex> lock(mutex_);
						queue_.clear();
					}
					for (;;) {
						if (stop_)
							return false;
						if (endpoint.open(sample_rate, name.c_str(), endpoint_id.c_str())) {
							endpoint_id = endpoint.device_id();
							endpoint.set_diagnostics(diagnostics);
							capacity = std::max<uint32_t>(1, sample_rate / 4);
							{
								std::lock_guard<std::mutex> lock(mutex_);
								queue_.reset(capacity);
							}
							std::fprintf(stderr, "WASAPI capture recovered: source=%s rate=%u\n",
								     name.c_str(), sample_rate);
							return true;
						}
						std::fprintf(stderr, "WASAPI capture reopen pending: source=%s retry_ms=%lld\n",
							     name.c_str(), static_cast<long long>(delay.count()));
						std::unique_lock<std::mutex> wake_lock(wake_mutex_);
						wake_condition_.wait_for(wake_lock, delay, [this]() { return stop_.load(); });
						delay = std::min(delay + delay, kMaximumDelay);
					}
				};
				while (!stop_) {
					if (endpoint.endpoint_changed() && !reopen())
						break;
					block.clear();
					if (!endpoint.wait_input() || !endpoint.pump([&](float sample) { block.push_back(sample); })) {
						std::fprintf(stderr, "WASAPI native input failed: t=%lu source=%s\n", static_cast<unsigned long>(GetTickCount()), name.c_str());
						if (!reopen())
							break;
						continue;
					}
					endpoint.maybe_log_diagnostics();
					if (!block.empty()) {
						std::lock_guard<std::mutex> lock(mutex_);
						const auto excess = queue_.append(block);
						if (excess)
							dropped_samples_.fetch_add(excess, std::memory_order_relaxed);
						if (excess) {
							const auto now = std::chrono::steady_clock::now();
							if (last_overrun_log == std::chrono::steady_clock::time_point{} ||
							    now - last_overrun_log >= std::chrono::seconds(1)) {
								last_overrun_log = now;
								std::fprintf(stderr, "WASAPI queue overrun: t=%lu dropped_frames=%llu limit_ms=250\n",
									     static_cast<unsigned long>(GetTickCount()),
									     static_cast<unsigned long long>(dropped_samples_.load(std::memory_order_relaxed)));
							}
						}
					}
				}
			} catch (const std::exception &error) {
				std::fprintf(stderr, "WASAPI capture thread exception: %s\n", error.what());
				failed_ = true;
				try { start.set_value(0); } catch (const std::future_error &) {}
			} catch (...) {
				std::fprintf(stderr, "WASAPI capture thread exception: unknown\n");
				failed_ = true;
				try { start.set_value(0); } catch (const std::future_error &) {}
			}
		});
		} catch (const std::exception &error) {
			std::fprintf(stderr, "WASAPI capture thread startup failed: %s\n", error.what());
			failed_ = true;
			stop_ = true;
			return false;
		} catch (...) {
			std::fprintf(stderr, "WASAPI capture thread startup failed: unknown\n");
			failed_ = true;
			stop_ = true;
			return false;
		}
		constexpr auto kStartupTimeout = std::chrono::seconds(5);
		if (result.wait_for(kStartupTimeout) != std::future_status::ready) {
			std::fprintf(stderr, "WASAPI capture startup timed out: source=%s\n", name.c_str());
			failed_ = true;
			close();
			return false;
		}
		const uint32_t opened_rate = result.get();
		if (!opened_rate) { close(); return false; }
		rate = opened_rate;
		return true;
	}
	bool failed() const { return failed_; }
	std::uint64_t dropped_samples() const { return dropped_samples_.load(std::memory_order_relaxed); }
	void drain(std::vector<float> &samples)
	{
		std::lock_guard<std::mutex> lock(mutex_);
		queue_.drain(samples);
	}
};
#endif
