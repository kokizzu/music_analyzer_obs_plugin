#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace mao {

constexpr uint32_t kBeatThisWindowSeconds = 20;
constexpr uint32_t kBeatThisMinSampleRate = 8000;
constexpr uint32_t kBeatThisMaxSampleRate = 192000;
constexpr uint32_t kBeatThisMinIntervals = 44;

struct BeatThisSidecarConfig {
	std::string python_command;
	std::string runner_path;
	std::string runtime_root;
	std::string model_cache_root;
	std::string checkpoint = "final0";
	uint32_t response_timeout_ms = 4000;
};

struct BeatThisSidecarReply {
	bool ready = false;
	float bpm = 0.0f;
	uint32_t intervals = 0;
};

// This client is owned exclusively by the optional sidecar worker.  It has no
// OBS dependency and never falls back to a shell, a model download, or an
// in-process model implementation.
class BeatThisSidecarClient {
public:
	BeatThisSidecarClient() = default;
	~BeatThisSidecarClient();
	BeatThisSidecarClient(const BeatThisSidecarClient &) = delete;
	BeatThisSidecarClient &operator=(const BeatThisSidecarClient &) = delete;

	bool request(const BeatThisSidecarConfig &config, const float *samples, std::size_t sample_count,
		     uint32_t sample_rate, BeatThisSidecarReply *reply);
	// Start the persistent child early, while the sidecar worker is idle.  This
	// deliberately does not send audio or wait for model output.
	bool warm(const BeatThisSidecarConfig &config);
	void stop();

	static bool valid_config(const BeatThisSidecarConfig &config);
	static bool valid_packet_shape(uint32_t sample_rate, std::size_t sample_count);
	static bool parse_reply(const std::string &line, uint32_t expected_sample_rate,
				std::size_t expected_sample_count, BeatThisSidecarReply *reply);

private:
	bool start(const BeatThisSidecarConfig &config);
	bool write_all(const void *data, std::size_t length, uint32_t timeout_ms);
	bool read_line(uint32_t timeout_ms, std::string *line);

	int stdin_fd_ = -1;
	int stdout_fd_ = -1;
	int pid_ = -1;
	BeatThisSidecarConfig config_;
	std::string read_buffer_;
};

} // namespace mao
