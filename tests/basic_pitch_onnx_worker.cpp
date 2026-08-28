#include "basic_pitch_onnx_worker.hpp"

#include <cstdio>
#include <vector>

int main(int argc, char **argv)
{
	if (argc != 3) {
		std::fprintf(stderr, "usage: basic_pitch_onnx_worker_tests ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL\n");
		return 2;
	}
	mao::BasicPitchOnnxWorker worker(argv[1], argv[2]);
	if (!worker.start()) {
		std::fprintf(stderr, "worker start failed: %s\n", worker.last_error().c_str());
		return 1;
	}
	std::vector<float> waveform(mao::BasicPitchOnnxRuntime::kInputSamples, 0.0f);
	uint64_t first_sequence = 0;
	if (!worker.submit(waveform.data(), waveform.size(), &first_sequence) ||
	    !worker.wait_for_result(first_sequence, 5000)) {
		std::fprintf(stderr, "worker did not publish an inference result: %s\n", worker.last_error().c_str());
		return 1;
	}
	mao::BasicPitchCausalNotes notes;
	uint64_t sequence = 0;
	if (!worker.copy_latest(notes, &sequence) || sequence != first_sequence) {
		std::fprintf(stderr, "worker result sequence is invalid\n");
		return 1;
	}
	float peak = 0.0f;
	for (float confidence : notes.confidence)
		peak = confidence > peak ? confidence : peak;
	if (peak > 1.0e-6f) {
		std::fprintf(stderr, "zero waveform produced a causal note confidence\n");
		return 1;
	}
	uint64_t second_sequence = 0;
	if (!worker.submit(waveform.data(), waveform.size(), &second_sequence) ||
	    second_sequence <= first_sequence || !worker.wait_for_result(second_sequence, 5000) ||
	    !worker.copy_latest(notes, &sequence) || sequence < second_sequence) {
		std::fprintf(stderr, "worker returned a stale result for a later request: %s\n", worker.last_error().c_str());
		return 1;
	}
	worker.stop();
	std::printf("basic_pitch_onnx_worker: sequence=%llu peak=%.2f\n",
		    static_cast<unsigned long long>(sequence), peak);
	return 0;
}
