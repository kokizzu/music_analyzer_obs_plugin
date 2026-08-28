#pragma once

#include "basic_pitch_onnx_decoder.hpp"
#include "basic_pitch_onnx_runtime.hpp"

#include <array>
#include <condition_variable>
#include <cstdint>
#include <mutex>
#include <string>
#include <thread>

namespace mao {

// Own this independently from the audio callback.  submit() only replaces a
// bounded pending window; inference and model loading happen exclusively on
// worker_.  A later analyzer integration is responsible for resampling and
// choosing causal two-second windows before submission.
class BasicPitchOnnxWorker {
public:
	BasicPitchOnnxWorker(std::string runtime_library_path, std::string model_path);
	~BasicPitchOnnxWorker();
	BasicPitchOnnxWorker(const BasicPitchOnnxWorker &) = delete;
	BasicPitchOnnxWorker &operator=(const BasicPitchOnnxWorker &) = delete;

	bool start();
	void stop();
	bool submit(const float *waveform, std::size_t count, uint64_t *sequence = nullptr);
	bool wait_for_result(uint32_t timeout_ms);
	bool wait_for_result(uint64_t sequence, uint32_t timeout_ms);
	bool copy_latest(BasicPitchCausalNotes &notes, uint64_t *sequence = nullptr) const;
	std::string last_error() const;

private:
	void run();

	const std::string runtime_library_path_;
	const std::string model_path_;
	mutable std::mutex mutex_;
	std::condition_variable condition_;
	std::thread worker_;
	std::array<float, BasicPitchOnnxRuntime::kInputSamples> pending_ = {};
	BasicPitchCausalNotes latest_ = {};
	uint64_t pending_sequence_ = 0;
	uint64_t processed_sequence_ = 0;
	uint64_t result_sequence_ = 0;
	bool running_ = false;
	bool stop_requested_ = false;
	bool startup_complete_ = false;
	std::string last_error_;
};

} // namespace mao
