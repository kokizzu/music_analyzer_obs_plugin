#include "basic_pitch_onnx_runtime.hpp"

#include <cstdio>
#include <vector>

int main(int argc, char **argv)
{
	if (argc != 3) {
		std::fprintf(stderr, "usage: basic_pitch_onnx_runtime_tests ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL\n");
		return 2;
	}
	mao::BasicPitchOnnxRuntime runtime;
	if (!runtime.load(argv[1], argv[2])) {
		std::fprintf(stderr, "load failed: %s\n", runtime.last_error().c_str());
		return 1;
	}
	std::vector<float> waveform(mao::BasicPitchOnnxRuntime::kInputSamples, 0.0f);
	mao::BasicPitchOnnxOutput output;
	if (!runtime.infer(waveform.data(), waveform.size(), output)) {
		std::fprintf(stderr, "infer failed: %s\n", runtime.last_error().c_str());
		return 1;
	}
	if (output.note.size() != mao::BasicPitchOnnxOutput::kFrames * mao::BasicPitchOnnxOutput::kNoteBins ||
	    output.onset.size() != output.note.size() ||
	    output.contour.size() != mao::BasicPitchOnnxOutput::kFrames * mao::BasicPitchOnnxOutput::kContourBins) {
		std::fprintf(stderr, "unexpected ONNX output shape\n");
		return 1;
	}
	std::printf("basic_pitch_onnx_runtime: note=%zu onset=%zu contour=%zu\n", output.note.size(),
		    output.onset.size(), output.contour.size());
	return 0;
}
