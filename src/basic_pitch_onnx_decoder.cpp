#include "basic_pitch_onnx_decoder.hpp"

#include <algorithm>
#include <cmath>

namespace mao {

BasicPitchCausalNotes BasicPitchOnnxDecoder::decode(const BasicPitchOnnxOutput &output) const
{
	BasicPitchCausalNotes decoded;
	if (output.note.size() != BasicPitchOnnxOutput::kFrames * BasicPitchOnnxOutput::kNoteBins)
		return decoded;

	for (std::size_t note = 0; note < BasicPitchOnnxOutput::kNoteBins; ++note) {
		const auto at = [&](std::size_t frame) {
			return std::clamp(output.note[frame * BasicPitchOnnxOutput::kNoteBins + note], 0.0f, 1.0f);
		};
		if (at(kCausalFrame) < kFrameThreshold)
			continue;

		std::size_t first = kCausalFrame;
		while (first > 0 && at(first - 1) >= kFrameThreshold)
			--first;
		std::size_t last = kCausalFrame;
		while (last + 1 < BasicPitchOnnxOutput::kFrames && at(last + 1) >= kFrameThreshold)
			++last;
		if (last - first + 1 < kMinimumStableFrames)
			continue;

		const std::size_t local_first = kCausalFrame > 2 ? kCausalFrame - 2 : 0;
		const std::size_t local_last = std::min(BasicPitchOnnxOutput::kFrames - 1, kCausalFrame + 2);
		float sum = 0.0f;
		for (std::size_t frame = local_first; frame <= local_last; ++frame)
			sum += at(frame);
		decoded.confidence[note] = sum / static_cast<float>(local_last - local_first + 1);
	}
	return decoded;
}

} // namespace mao
