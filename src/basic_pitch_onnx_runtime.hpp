#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace mao {

struct BasicPitchOnnxOutput {
	static constexpr std::size_t kFrames = 172;
	static constexpr std::size_t kNoteBins = 88;
	static constexpr std::size_t kContourBins = 264;

	std::vector<float> note;
	std::vector<float> onset;
	std::vector<float> contour;
};

// A deliberately isolated runtime primitive.  The analyzer does not depend on
// it yet: an eventual caller must own this object on a worker thread and feed
// it a causal, resampled two-second PCM window.
class BasicPitchOnnxRuntime {
public:
	static constexpr std::size_t kInputSamples = 43844;

	BasicPitchOnnxRuntime() = default;
	~BasicPitchOnnxRuntime();
	BasicPitchOnnxRuntime(const BasicPitchOnnxRuntime &) = delete;
	BasicPitchOnnxRuntime &operator=(const BasicPitchOnnxRuntime &) = delete;

	bool load(const char *runtime_library_path, const char *model_path);
	bool infer(const float *waveform, std::size_t count, BasicPitchOnnxOutput &output);
	bool ready() const { return session_ != nullptr; }
	const std::string &last_error() const { return last_error_; }

private:
	void reset();
	bool check_status(void *status, const char *operation);

	void *library_ = nullptr;
	const void *api_ = nullptr;
	void *environment_ = nullptr;
	void *session_options_ = nullptr;
	void *session_ = nullptr;
	std::string last_error_;
};

} // namespace mao
