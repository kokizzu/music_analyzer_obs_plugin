#include "basic_pitch_onnx_decoder.hpp"
#include "basic_pitch_onnx_runtime.hpp"

#include <cmath>
#include <cstdio>
#include <vector>

int main(int argc, char **argv)
{
	if (argc != 3) {
		std::fprintf(stderr, "usage: basic_pitch_onnx_signal_tests ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL\n");
		return 2;
	}

	mao::BasicPitchOnnxRuntime runtime;
	if (!runtime.load(argv[1], argv[2])) {
		std::fprintf(stderr, "basic_pitch_onnx_signal: load failed: %s\n", runtime.last_error().c_str());
		return 1;
	}

	constexpr float kA4Hz = 440.0f;
	constexpr float kAmplitude = 0.35f;
	constexpr float kPi = 3.14159265358979323846f;
	std::vector<float> waveform(mao::BasicPitchOnnxRuntime::kInputSamples);
	for (std::size_t sample = 0; sample < waveform.size(); ++sample) {
		const float phase = 2.0f * kPi * kA4Hz * static_cast<float>(sample) / 22050.0f;
		waveform[sample] = kAmplitude * std::sin(phase);
	}

	mao::BasicPitchOnnxOutput output;
	if (!runtime.infer(waveform.data(), waveform.size(), output)) {
		std::fprintf(stderr, "basic_pitch_onnx_signal: infer failed: %s\n", runtime.last_error().c_str());
		return 1;
	}
	const mao::BasicPitchCausalNotes notes = mao::BasicPitchOnnxDecoder().decode(output);
	constexpr int kA4Midi = 69;
	const std::size_t a4 = static_cast<std::size_t>(kA4Midi - mao::BasicPitchOnnxDecoder::kMidiOffset);
	if (notes.confidence[a4] < mao::BasicPitchOnnxDecoder::kFrameThreshold) {
		std::fprintf(stderr,
			     "basic_pitch_onnx_signal: expected stable A4 confidence >= %.2f, got %.3f\n",
			     mao::BasicPitchOnnxDecoder::kFrameThreshold, notes.confidence[a4]);
		return 1;
	}

	std::printf("basic_pitch_onnx_signal: A4 confidence=%.3f\n", notes.confidence[a4]);
	return 0;
}
