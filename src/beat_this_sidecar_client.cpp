#include "beat_this_sidecar_client.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace mao {
namespace {

constexpr std::array<uint8_t, 8> kMagic = {'M', 'A', 'O', 'B', 'T', '1', 0, 0};
constexpr const char *kProtocol = "mao-beat-this-v1";

void append_u32_le(std::vector<uint8_t> *output, uint32_t value)
{
	for (int shift = 0; shift < 32; shift += 8)
		output->push_back(static_cast<uint8_t>((value >> shift) & 0xffU));
}

bool parse_u32_field(const std::string &line, const char *name, uint32_t *value)
{
	if (!name || !value)
		return false;
	const std::string marker = std::string{"\""} + name + "\":";
	const std::size_t start = line.find(marker);
	if (start == std::string::npos)
		return false;
	const std::size_t digits = start + marker.size();
	if (digits >= line.size() || line[digits] < '0' || line[digits] > '9')
		return false;
	uint64_t parsed = 0;
	std::size_t end = digits;
	while (end < line.size() && line[end] >= '0' && line[end] <= '9') {
		parsed = parsed * 10U + static_cast<uint64_t>(line[end] - '0');
		if (parsed > UINT32_MAX)
			return false;
		++end;
	}
	*value = static_cast<uint32_t>(parsed);
	return true;
}

bool parse_float_field(const std::string &line, const char *name, float *value)
{
	if (!name || !value)
		return false;
	const std::string marker = std::string{"\""} + name + "\":";
	const std::size_t start = line.find(marker);
	if (start == std::string::npos)
		return false;
	const char *begin = line.c_str() + start + marker.size();
	char *end = nullptr;
	errno = 0;
	const float parsed = std::strtof(begin, &end);
	if (errno != 0 || end == begin || !std::isfinite(parsed))
		return false;
	*value = parsed;
	return true;
}

bool has_string_field(const std::string &line, const char *name, const char *expected)
{
	return line.find(std::string{"\""} + name + "\":\"" + expected + "\"") != std::string::npos;
}

bool write_float32_le(std::vector<uint8_t> *output, float value)
{
	if (!std::isfinite(value))
		return false;
	uint32_t bits = 0;
	static_assert(sizeof(bits) == sizeof(value), "float32 protocol requires 32-bit float");
	std::memcpy(&bits, &value, sizeof(bits));
	append_u32_le(output, bits);
	return true;
}

} // namespace

BeatThisSidecarClient::~BeatThisSidecarClient()
{
	stop();
}

bool BeatThisSidecarClient::valid_config(const BeatThisSidecarConfig &config)
{
	return !config.python_command.empty() && !config.runner_path.empty() && !config.runtime_root.empty() &&
	       !config.model_cache_root.empty() && !config.checkpoint.empty() &&
	       config.checkpoint.find('/') == std::string::npos && config.checkpoint.find('\\') == std::string::npos &&
	       config.response_timeout_ms > 0;
}

bool BeatThisSidecarClient::valid_packet_shape(uint32_t sample_rate, std::size_t sample_count)
{
	return sample_rate >= kBeatThisMinSampleRate && sample_rate <= kBeatThisMaxSampleRate &&
	       sample_count == static_cast<std::size_t>(sample_rate) * kBeatThisWindowSeconds;
}

bool BeatThisSidecarClient::parse_reply(const std::string &line, uint32_t expected_sample_rate,
					std::size_t expected_sample_count, BeatThisSidecarReply *reply)
{
	if (!reply || !valid_packet_shape(expected_sample_rate, expected_sample_count) ||
	    !has_string_field(line, "protocol", kProtocol))
		return false;

	uint32_t sample_rate = 0;
	uint32_t samples = 0;
	uint32_t intervals = 0;
	float bpm = 0.0f;
	if (!parse_u32_field(line, "sample_rate", &sample_rate) || !parse_u32_field(line, "samples", &samples) ||
	    !parse_u32_field(line, "intervals", &intervals) || !parse_float_field(line, "bpm", &bpm) ||
	    sample_rate != expected_sample_rate || samples != expected_sample_count)
		return false;

	if (has_string_field(line, "status", "gated")) {
		if (bpm != 0.0f)
			return false;
		*reply = {};
		return true;
	}
	if (!has_string_field(line, "status", "ready") || intervals < kBeatThisMinIntervals || bpm <= 0.0f)
		return false;
	*reply = {true, bpm, intervals};
	return true;
}

bool BeatThisSidecarClient::start(const BeatThisSidecarConfig &config)
{
	if (!valid_config(config))
		return false;
	stop();

	int stdin_pipe[2] = {-1, -1};
	int stdout_pipe[2] = {-1, -1};
	if (pipe(stdin_pipe) != 0 || pipe(stdout_pipe) != 0) {
		if (stdin_pipe[0] >= 0) {
			close(stdin_pipe[0]);
			close(stdin_pipe[1]);
		}
		if (stdout_pipe[0] >= 0) {
			close(stdout_pipe[0]);
			close(stdout_pipe[1]);
		}
		return false;
	}

	const pid_t child = fork();
	if (child < 0) {
		close(stdin_pipe[0]);
		close(stdin_pipe[1]);
		close(stdout_pipe[0]);
		close(stdout_pipe[1]);
		return false;
	}
	if (child == 0) {
		(void)dup2(stdin_pipe[0], STDIN_FILENO);
		(void)dup2(stdout_pipe[1], STDOUT_FILENO);
		close(stdin_pipe[0]);
		close(stdin_pipe[1]);
		close(stdout_pipe[0]);
		close(stdout_pipe[1]);
		const std::array<const char *, 11> args = {
			config.python_command.c_str(), config.runner_path.c_str(), "--runtime-root", config.runtime_root.c_str(),
			"--model-cache-root", config.model_cache_root.c_str(), "--checkpoint", config.checkpoint.c_str(),
			"--device", "cpu", nullptr,
		};
		execvp(args[0], const_cast<char *const *>(args.data()));
		_exit(127);
	}

	close(stdin_pipe[0]);
	close(stdout_pipe[1]);
	stdin_fd_ = stdin_pipe[1];
	stdout_fd_ = stdout_pipe[0];
	pid_ = static_cast<int>(child);
	config_ = config;
	const int flags = fcntl(stdin_fd_, F_GETFL, 0);
	if (flags < 0 || fcntl(stdin_fd_, F_SETFL, flags | O_NONBLOCK) != 0) {
		stop();
		return false;
	}
	read_buffer_.clear();
	return true;
}

bool BeatThisSidecarClient::write_all(const void *data, std::size_t length, uint32_t timeout_ms)
{
	const auto *bytes = static_cast<const uint8_t *>(data);
	while (length > 0) {
		const ssize_t written = write(stdin_fd_, bytes, length);
		if (written <= 0) {
			if (written < 0 && errno == EINTR)
				continue;
			if (written >= 0 || (errno != EAGAIN && errno != EWOULDBLOCK))
				return false;
			pollfd descriptor = {stdin_fd_, POLLOUT, 0};
			if (poll(&descriptor, 1, static_cast<int>(timeout_ms)) <= 0 ||
			    !(descriptor.revents & POLLOUT))
				return false;
			continue;
		}
		bytes += written;
		length -= static_cast<std::size_t>(written);
	}
	return true;
}

bool BeatThisSidecarClient::warm(const BeatThisSidecarConfig &config)
{
	if (pid_ > 0 && config.python_command == config_.python_command && config.runner_path == config_.runner_path &&
	    config.runtime_root == config_.runtime_root && config.model_cache_root == config_.model_cache_root &&
	    config.checkpoint == config_.checkpoint && config.response_timeout_ms == config_.response_timeout_ms)
		return true;
	return start(config);
}

bool BeatThisSidecarClient::read_line(uint32_t timeout_ms, std::string *line)
{
	if (!line || stdout_fd_ < 0)
		return false;
	const auto newline = [&]() { return read_buffer_.find('\n'); };
	for (;;) {
		const std::size_t found = newline();
		if (found != std::string::npos) {
			*line = read_buffer_.substr(0, found);
			read_buffer_.erase(0, found + 1);
			return line->size() <= 1024;
		}
		pollfd descriptor = {stdout_fd_, POLLIN, 0};
		const int result = poll(&descriptor, 1, static_cast<int>(timeout_ms));
		if (result <= 0 || !(descriptor.revents & POLLIN))
			return false;
		std::array<char, 512> buffer = {};
		const ssize_t received = read(stdout_fd_, buffer.data(), buffer.size());
		if (received <= 0)
			return false;
		read_buffer_.append(buffer.data(), static_cast<std::size_t>(received));
		if (read_buffer_.size() > 1024)
			return false;
	}
}

bool BeatThisSidecarClient::request(const BeatThisSidecarConfig &config, const float *samples,
					    std::size_t sample_count, uint32_t sample_rate,
					    BeatThisSidecarReply *reply)
{
	if (!reply || !samples || !valid_packet_shape(sample_rate, sample_count))
		return false;
	if (pid_ <= 0 || config.python_command != config_.python_command || config.runner_path != config_.runner_path ||
	    config.runtime_root != config_.runtime_root || config.model_cache_root != config_.model_cache_root ||
	    config.checkpoint != config_.checkpoint || config.response_timeout_ms != config_.response_timeout_ms) {
		if (!start(config))
			return false;
	}

	std::vector<uint8_t> packet;
	packet.reserve(kMagic.size() + 8 + sample_count * sizeof(float));
	packet.insert(packet.end(), kMagic.begin(), kMagic.end());
	append_u32_le(&packet, sample_rate);
	append_u32_le(&packet, static_cast<uint32_t>(sample_count));
	for (std::size_t i = 0; i < sample_count; ++i) {
		if (!write_float32_le(&packet, samples[i])) {
			stop();
			return false;
		}
	}
	std::string line;
	if (!write_all(packet.data(), packet.size(), config.response_timeout_ms) || !read_line(config.response_timeout_ms, &line) ||
	    !parse_reply(line, sample_rate, sample_count, reply)) {
		stop();
		return false;
	}
	return true;
}

void BeatThisSidecarClient::stop()
{
	if (stdin_fd_ >= 0) {
		close(stdin_fd_);
		stdin_fd_ = -1;
	}
	if (pid_ > 0) {
		int status = 0;
		pid_t result = waitpid(static_cast<pid_t>(pid_), &status, WNOHANG);
		if (result == 0) {
			(void)kill(static_cast<pid_t>(pid_), SIGTERM);
			for (int attempt = 0; attempt < 20 && result == 0; ++attempt) {
				usleep(10000);
				result = waitpid(static_cast<pid_t>(pid_), &status, WNOHANG);
			}
		}
		if (result == 0) {
			(void)kill(static_cast<pid_t>(pid_), SIGKILL);
			(void)waitpid(static_cast<pid_t>(pid_), &status, 0);
		}
	}
	if (stdout_fd_ >= 0) {
		close(stdout_fd_);
		stdout_fd_ = -1;
	}
	pid_ = -1;
	config_ = {};
	read_buffer_.clear();
}

} // namespace mao
