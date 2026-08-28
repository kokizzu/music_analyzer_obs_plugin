#include "basic_pitch_onnx_decoder.hpp"

#include <cmath>
#include <cstdio>

namespace {

bool near(float actual, float expected)
{
	return std::abs(actual - expected) < 1.0e-5f;
}

} // namespace

int main()
{
	mao::BasicPitchOnnxOutput output;
	output.note.assign(mao::BasicPitchOnnxOutput::kFrames * mao::BasicPitchOnnxOutput::kNoteBins, 0.0f);
	const std::size_t stable_note = 48; // MIDI 69 (A4)
	for (std::size_t frame = mao::BasicPitchOnnxDecoder::kCausalFrame - 3;
	     frame <= mao::BasicPitchOnnxDecoder::kCausalFrame + 3; ++frame)
		output.note[frame * mao::BasicPitchOnnxOutput::kNoteBins + stable_note] = 0.80f;
	const std::size_t spike_note = 51;
	output.note[mao::BasicPitchOnnxDecoder::kCausalFrame * mao::BasicPitchOnnxOutput::kNoteBins + spike_note] =
		0.95f;

	mao::BasicPitchOnnxDecoder decoder;
	const mao::BasicPitchCausalNotes decoded = decoder.decode(output);
	if (!near(decoded.confidence[stable_note], 0.80f) || decoded.confidence[spike_note] != 0.0f) {
		std::fprintf(stderr, "basic_pitch_onnx_decoder: stability gate failed\n");
		return 1;
	}
	std::printf("basic_pitch_onnx_decoder: midi=%d confidence=%.2f\n",
		    mao::BasicPitchOnnxDecoder::kMidiOffset + static_cast<int>(stable_note), decoded.confidence[stable_note]);
	return 0;
}
