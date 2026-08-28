#include "basic_pitch_pcm_history.hpp"

#include <algorithm>
#include <cmath>

namespace mao {

void BasicPitchPcmHistory::reset()
{
	write_index_ = 0;
	available_ = 0;
	since_snapshot_ = 0;
	source_sample_rate_ = 0;
	source_index_ = 0;
	next_output_source_index_ = 0.0;
	previous_sample_ = 0.0f;
	has_previous_sample_ = false;
}

void BasicPitchPcmHistory::append(float sample)
{
	ring_[write_index_] = std::clamp(sample, -1.0f, 1.0f);
	write_index_ = (write_index_ + 1) % ring_.size();
	available_ = std::min(available_ + 1, ring_.size());
	++since_snapshot_;
}

bool BasicPitchPcmHistory::push(const float *samples, std::size_t count, uint32_t sample_rate,
				 std::array<float, BasicPitchOnnxRuntime::kInputSamples> &snapshot)
{
	if (!samples || count == 0 || sample_rate == 0)
		return false;
	if (source_sample_rate_ != sample_rate)
		reset();
	source_sample_rate_ = sample_rate;
	const double source_step = static_cast<double>(sample_rate) / static_cast<double>(kTargetSampleRate);
	for (std::size_t offset = 0; offset < count; ++offset, ++source_index_) {
		const float current = std::clamp(samples[offset], -1.0f, 1.0f);
		while (next_output_source_index_ <= static_cast<double>(source_index_)) {
			float output = current;
			if (has_previous_sample_) {
				const double fractional = std::clamp(next_output_source_index_ -
									  static_cast<double>(source_index_ - 1),
									  0.0, 1.0);
				output = previous_sample_ + static_cast<float>(fractional) * (current - previous_sample_);
			}
			append(output);
			next_output_source_index_ += source_step;
		}
		previous_sample_ = current;
		has_previous_sample_ = true;
	}
	if (available_ < ring_.size() || since_snapshot_ < kSnapshotStride)
		return false;
	const std::size_t oldest = write_index_;
	for (std::size_t index = 0; index < ring_.size(); ++index)
		snapshot[index] = ring_[(oldest + index) % ring_.size()];
	since_snapshot_ = 0;
	return true;
}

} // namespace mao
