#pragma once
#ifdef _WIN32
#include "windows_loopback.hpp"
#include "capture_queue.hpp"
#include <atomic>
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
	std::vector<float> queue_;
public:
	~WindowsInputCapture() { close(); }
	void close()
	{
		stop_ = true;
		if (worker_.joinable()) worker_.join();
		queue_.clear();
	}
	bool open(const std::string &name, uint32_t &rate, bool diagnostics)
	{
		close();
		stop_ = false;
		failed_ = false;
		std::promise<uint32_t> opened;
		auto result = opened.get_future();
		worker_ = std::thread([this, name, diagnostics, start = std::move(opened)]() mutable {
			try {
				WindowsLoopback endpoint;
				uint32_t sample_rate = 48000;
				if (!endpoint.open(sample_rate, name.c_str())) { start.set_value(0); return; }
				endpoint.set_diagnostics(diagnostics);
				std::size_t capacity = std::max<uint32_t>(1, sample_rate / 4);
				queue_.reserve(capacity);
				start.set_value(sample_rate);
				std::vector<float> block;
				block.reserve(sample_rate);
				auto reopen = [&]() {
					constexpr auto kInitialDelay = std::chrono::milliseconds(250);
					constexpr auto kMaximumDelay = std::chrono::milliseconds(2000);
					auto delay = kInitialDelay;
					for (;;) {
						if (stop_)
							return false;
						if (endpoint.open(sample_rate, name.c_str())) {
							endpoint.set_diagnostics(diagnostics);
							capacity = std::max<uint32_t>(1, sample_rate / 4);
							{
								std::lock_guard<std::mutex> lock(mutex_);
								queue_.reserve(capacity);
							}
							std::fprintf(stderr, "WASAPI capture recovered: source=%s rate=%u\n",
								     name.c_str(), sample_rate);
							return true;
						}
						std::fprintf(stderr, "WASAPI capture reopen pending: source=%s retry_ms=%lld\n",
							     name.c_str(), static_cast<long long>(delay.count()));
						std::this_thread::sleep_for(delay);
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
						const auto excess = mao::append_capture_samples(queue_, block, capacity);
						if (excess) {
							std::fprintf(stderr, "WASAPI queue overrun: t=%lu dropped_frames=%zu limit_ms=250\n", static_cast<unsigned long>(GetTickCount()), excess);
						}
					}
				}
			} catch (const std::exception &error) {
				std::fprintf(stderr, "WASAPI capture thread exception: %s\n", error.what());
				failed_ = true;
				try { start.set_value(0); } catch (const std::future_error &) {}
			}
		});
		const uint32_t opened_rate = result.get();
		if (!opened_rate) { close(); return false; }
		rate = opened_rate;
		return true;
	}
	bool failed() const { return failed_; }
	void drain(std::vector<float> &samples)
	{
		std::lock_guard<std::mutex> lock(mutex_);
		samples.assign(queue_.begin(), queue_.end());
		queue_.clear();
	}
};
#endif
