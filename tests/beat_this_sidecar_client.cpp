#include "beat_this_sidecar_client.hpp"

#include <cstdio>
#include <string>
#include <vector>

namespace {

bool expect(bool condition, const char *message)
{
	if (condition)
		return true;
	std::fprintf(stderr, "beat_this_sidecar_client: %s\n", message);
	return false;
}

} // namespace

int main(int argc, char **argv)
{
	const std::size_t sample_count = static_cast<std::size_t>(48000) * mao::kBeatThisWindowSeconds;
	if (!expect(mao::BeatThisSidecarClient::valid_packet_shape(48000, sample_count), "valid packet rejected") ||
	    !expect(!mao::BeatThisSidecarClient::valid_packet_shape(48000, sample_count - 1), "short packet accepted") ||
	    !expect(!mao::BeatThisSidecarClient::valid_packet_shape(7000, 140000), "invalid rate accepted"))
		return 1;

	mao::BeatThisSidecarConfig config;
	config.python_command = "python3";
	config.runner_path = "/tmp/runner.py";
	config.runtime_root = "/tmp/runtime";
	config.model_cache_root = "/tmp/cache";
	if (!expect(mao::BeatThisSidecarClient::valid_config(config), "valid explicit config rejected"))
		return 1;
	config.checkpoint = "../final0";
	if (!expect(!mao::BeatThisSidecarClient::valid_config(config), "path-like checkpoint accepted"))
		return 1;

	mao::BeatThisSidecarReply reply;
	const std::string ready =
		"{\"bpm\":128.0,\"intervals\":44,\"protocol\":\"mao-beat-this-v1\",\"sample_rate\":48000,\"samples\":960000,\"status\":\"ready\"}";
	if (!expect(mao::BeatThisSidecarClient::parse_reply(ready, 48000, sample_count, &reply), "ready reply rejected") ||
	    !expect(reply.ready && reply.bpm == 128.0f && reply.intervals == 44, "ready reply changed") ||
	    !expect(mao::BeatThisSidecarClient::parse_reply(
			"{\"bpm\":0.0,\"intervals\":43,\"protocol\":\"mao-beat-this-v1\",\"sample_rate\":48000,\"samples\":960000,\"status\":\"gated\"}",
			48000, sample_count, &reply),
		"gated reply rejected") ||
	    !expect(!reply.ready, "gated reply became ready") ||
	    !expect(!mao::BeatThisSidecarClient::parse_reply(
			"{\"bpm\":128.0,\"intervals\":43,\"protocol\":\"mao-beat-this-v1\",\"sample_rate\":48000,\"samples\":960000,\"status\":\"ready\"}",
			48000, sample_count, &reply),
		"under-gated ready reply accepted") ||
	    !expect(!mao::BeatThisSidecarClient::parse_reply(
			"{\"bpm\":0.0,\"intervals\":44,\"protocol\":\"mao-beat-this-v1\",\"sample_rate\":48000,\"samples\":960000,\"status\":\"ready\"}",
			48000, sample_count, &reply),
		"zero BPM ready reply accepted"))
		return 1;

	if (!expect(argc == 2, "requires a model-free sidecar runner path"))
		return 1;
	config.checkpoint = "final0";
	config.runner_path = argv[1];
	mao::BeatThisSidecarClient client;
	std::vector<float> samples(sample_count, 0.125f);
	if (!expect(client.request(config, samples.data(), samples.size(), 48000, &reply),
		    "first exact packet was not accepted by child") ||
	    !expect(reply.ready && reply.bpm == 128.0f && reply.intervals == 44,
		    "first child reply changed") ||
	    !expect(client.request(config, samples.data(), samples.size(), 48000, &reply),
		    "persistent child did not accept second packet"))
		return 1;
	client.stop();

	std::puts("beat_this_sidecar_client: ok");
	return 0;
}
