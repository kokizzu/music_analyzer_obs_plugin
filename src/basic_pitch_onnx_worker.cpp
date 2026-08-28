#include "basic_pitch_onnx_worker.hpp"

#include <algorithm>
#include <chrono>

namespace mao {

BasicPitchOnnxWorker::BasicPitchOnnxWorker(std::string runtime_library_path, std::string model_path)
	: runtime_library_path_(std::move(runtime_library_path)), model_path_(std::move(model_path))
{
}

BasicPitchOnnxWorker::~BasicPitchOnnxWorker()
{
	stop();
}

bool BasicPitchOnnxWorker::start()
{
	std::lock_guard<std::mutex> lock(mutex_);
	if (running_)
		return true;
	if (runtime_library_path_.empty() || model_path_.empty()) {
		last_error_ = "runtime library and model paths are required";
		return false;
	}
	stop_requested_ = false;
	startup_complete_ = false;
	last_error_.clear();
	running_ = true;
	worker_ = std::thread(&BasicPitchOnnxWorker::run, this);
	return true;
}

void BasicPitchOnnxWorker::stop()
{
	{
		std::lock_guard<std::mutex> lock(mutex_);
		if (!running_)
			return;
		stop_requested_ = true;
	}
	condition_.notify_all();
	if (worker_.joinable())
		worker_.join();
	std::lock_guard<std::mutex> lock(mutex_);
	running_ = false;
}

bool BasicPitchOnnxWorker::submit(const float *waveform, std::size_t count, uint64_t *sequence)
{
	if (!waveform || count != BasicPitchOnnxRuntime::kInputSamples)
		return false;
	{
		std::lock_guard<std::mutex> lock(mutex_);
		if (!running_ || stop_requested_)
			return false;
		std::copy(waveform, waveform + count, pending_.begin());
		++pending_sequence_;
		if (sequence)
			*sequence = pending_sequence_;
	}
	condition_.notify_one();
	return true;
}

bool BasicPitchOnnxWorker::wait_for_result(uint32_t timeout_ms)
{
	std::unique_lock<std::mutex> lock(mutex_);
	const uint64_t sequence = pending_sequence_;
	return condition_.wait_for(lock, std::chrono::milliseconds(timeout_ms), [this, sequence] {
		return result_sequence_ >= sequence || (startup_complete_ && !last_error_.empty()) || !running_;
	});
}

bool BasicPitchOnnxWorker::wait_for_result(uint64_t sequence, uint32_t timeout_ms)
{
	std::unique_lock<std::mutex> lock(mutex_);
	return condition_.wait_for(lock, std::chrono::milliseconds(timeout_ms), [this, sequence] {
		return result_sequence_ >= sequence || (startup_complete_ && !last_error_.empty()) || !running_;
	});
}

bool BasicPitchOnnxWorker::copy_latest(BasicPitchCausalNotes &notes, uint64_t *sequence) const
{
	std::lock_guard<std::mutex> lock(mutex_);
	if (result_sequence_ == 0)
		return false;
	notes = latest_;
	if (sequence)
		*sequence = result_sequence_;
	return true;
}

std::string BasicPitchOnnxWorker::last_error() const
{
	std::lock_guard<std::mutex> lock(mutex_);
	return last_error_;
}

void BasicPitchOnnxWorker::run()
{
	BasicPitchOnnxRuntime runtime;
	if (!runtime.load(runtime_library_path_.c_str(), model_path_.c_str())) {
		std::lock_guard<std::mutex> lock(mutex_);
		last_error_ = runtime.last_error();
		startup_complete_ = true;
		condition_.notify_all();
		return;
	}
	{
		std::lock_guard<std::mutex> lock(mutex_);
		startup_complete_ = true;
	}
	condition_.notify_all();

	BasicPitchOnnxDecoder decoder;
	for (;;) {
		std::array<float, BasicPitchOnnxRuntime::kInputSamples> waveform = {};
		uint64_t sequence = 0;
		{
			std::unique_lock<std::mutex> lock(mutex_);
			condition_.wait(lock, [this] { return stop_requested_ || pending_sequence_ > processed_sequence_; });
			if (stop_requested_)
				break;
			waveform = pending_;
			sequence = pending_sequence_;
		}
		BasicPitchOnnxOutput output;
		if (!runtime.infer(waveform.data(), waveform.size(), output)) {
			std::lock_guard<std::mutex> lock(mutex_);
			last_error_ = runtime.last_error();
			processed_sequence_ = sequence;
			condition_.notify_all();
			continue;
		}
		const BasicPitchCausalNotes notes = decoder.decode(output);
		{
			std::lock_guard<std::mutex> lock(mutex_);
			latest_ = notes;
			processed_sequence_ = sequence;
			result_sequence_ = sequence;
		}
		condition_.notify_all();
	}
}

} // namespace mao
