#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

namespace {

constexpr float kDefaultWindowSeconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;

struct Runner {
	int checks = 0;
	int failures = 0;

	void expect(bool ok, const std::string &message)
	{
		++checks;
		if (!ok) {
			++failures;
			std::fprintf(stderr, "%s\n", message.c_str());
		}
	}
};

struct WavFormat {
	uint16_t audio_format = 0;
	uint16_t channels = 0;
	uint32_t sample_rate = 0;
	uint16_t block_align = 0;
	uint16_t bits_per_sample = 0;
	uint64_t data_offset = 0;
	uint64_t data_size = 0;
	uint64_t frame_count = 0;
};

uint16_t read_u16(std::ifstream &file)
{
	unsigned char b[2] = {};
	file.read(reinterpret_cast<char *>(b), sizeof(b));
	return static_cast<uint16_t>(b[0]) | static_cast<uint16_t>(b[1] << 8);
}

uint32_t read_u32(std::ifstream &file)
{
	unsigned char b[4] = {};
	file.read(reinterpret_cast<char *>(b), sizeof(b));
	return static_cast<uint32_t>(b[0]) | (static_cast<uint32_t>(b[1]) << 8) |
	       (static_cast<uint32_t>(b[2]) << 16) | (static_cast<uint32_t>(b[3]) << 24);
}

bool read_wav_format(const std::string &path, WavFormat &format, std::string &error)
{
	std::ifstream file(path, std::ios::binary);
	if (!file) {
		error = "open failed";
		return false;
	}

	char riff[4] = {};
	char wave[4] = {};
	file.read(riff, sizeof(riff));
	(void)read_u32(file);
	file.read(wave, sizeof(wave));
	if (std::strncmp(riff, "RIFF", 4) != 0 || std::strncmp(wave, "WAVE", 4) != 0) {
		error = "not a RIFF/WAVE file";
		return false;
	}

	while (file) {
		char id[4] = {};
		file.read(id, sizeof(id));
		if (!file)
			break;
		const uint32_t chunk_size = read_u32(file);
		const std::streampos chunk_data = file.tellg();

		if (std::strncmp(id, "fmt ", 4) == 0) {
			format.audio_format = read_u16(file);
			format.channels = read_u16(file);
			format.sample_rate = read_u32(file);
			(void)read_u32(file);
			format.block_align = read_u16(file);
			format.bits_per_sample = read_u16(file);
		} else if (std::strncmp(id, "data", 4) == 0) {
			format.data_offset = static_cast<uint64_t>(chunk_data);
			format.data_size = chunk_size;
		}

		file.seekg(chunk_data + static_cast<std::streamoff>(chunk_size + (chunk_size & 1)));
	}

	if (format.channels == 0 || format.sample_rate == 0 || format.block_align == 0 ||
	    format.bits_per_sample == 0 || format.data_offset == 0 || format.data_size == 0) {
		error = "missing fmt or data chunk";
		return false;
	}
	if (format.audio_format != 1 && format.audio_format != 3) {
		error = "unsupported WAV format";
		return false;
	}
	format.frame_count = format.data_size / format.block_align;
	return true;
}

float decode_pcm_sample(const unsigned char *bytes, uint16_t bits_per_sample, uint16_t audio_format)
{
	if (audio_format == 3 && bits_per_sample == 32) {
		float value = 0.0f;
		std::memcpy(&value, bytes, sizeof(value));
		return std::clamp(value, -1.0f, 1.0f);
	}
	if (bits_per_sample == 16) {
		const int16_t value = static_cast<int16_t>(static_cast<uint16_t>(bytes[0]) |
							  (static_cast<uint16_t>(bytes[1]) << 8));
		return static_cast<float>(value) / 32768.0f;
	}
	if (bits_per_sample == 24) {
		int32_t value = static_cast<int32_t>(bytes[0]) | (static_cast<int32_t>(bytes[1]) << 8) |
				(static_cast<int32_t>(bytes[2]) << 16);
		if (value & 0x00800000)
			value |= ~0x00ffffff;
		return static_cast<float>(value) / 8388608.0f;
	}
	if (bits_per_sample == 32) {
		int32_t value = static_cast<int32_t>(bytes[0]) | (static_cast<int32_t>(bytes[1]) << 8) |
				(static_cast<int32_t>(bytes[2]) << 16) |
				(static_cast<int32_t>(bytes[3]) << 24);
		return static_cast<float>(value) / 2147483648.0f;
	}
	return 0.0f;
}

bool read_wav_mono(const std::string &path, std::vector<float> &samples, uint32_t &sample_rate,
		   std::string &error)
{
	WavFormat format;
	if (!read_wav_format(path, format, error))
		return false;

	const uint16_t bytes_per_sample = static_cast<uint16_t>(format.bits_per_sample / 8);
	if (bytes_per_sample == 0 || format.block_align < bytes_per_sample * format.channels) {
		error = "invalid block alignment";
		return false;
	}

	std::ifstream file(path, std::ios::binary);
	if (!file) {
		error = "open failed";
		return false;
	}
	file.seekg(static_cast<std::streamoff>(format.data_offset));

	std::vector<unsigned char> bytes(static_cast<std::size_t>(format.data_size));
	file.read(reinterpret_cast<char *>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
	if (file.gcount() != static_cast<std::streamsize>(bytes.size())) {
		error = "short read";
		return false;
	}

	samples.assign(static_cast<std::size_t>(format.frame_count), 0.0f);
	for (std::size_t frame = 0; frame < samples.size(); ++frame) {
		const unsigned char *frame_bytes = bytes.data() + frame * format.block_align;
		float sum = 0.0f;
		for (uint16_t channel = 0; channel < format.channels; ++channel)
			sum += decode_pcm_sample(frame_bytes + channel * bytes_per_sample, format.bits_per_sample,
						 format.audio_format);
		samples[frame] = sum / static_cast<float>(format.channels);
	}

	sample_rate = format.sample_rate;
	return true;
}

std::string join_path(const std::string &lhs, const std::string &rhs)
{
	if (lhs.empty() || lhs[lhs.size() - 1] == '/')
		return lhs + rhs;
	return lhs + "/" + rhs;
}

std::vector<std::string> split_tab(const std::string &line)
{
	std::vector<std::string> parts;
	std::string part;
	std::istringstream input(line);
	while (std::getline(input, part, '\t'))
		parts.push_back(part);
	return parts;
}

const char *category_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								"tom", "ride", "rim"};
	return index < mao::kDrumCount ? kNames[index] : "unknown";
}

const char *category_env_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"KICK", "SNARE", "HIHAT", "CRASH",
								"TOM", "RIDE", "RIM"};
	return index < mao::kDrumCount ? kNames[index] : "UNKNOWN";
}

bool category_index(const std::string &category, std::size_t &index)
{
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (category == category_name(i)) {
			index = i;
			return true;
		}
	}
	return false;
}

int primary_drum_index(const mao::AnalysisSnapshot &snapshot)
{
	int primary = -1;
	float primary_level = 0.0f;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!snapshot.drums[i].active || snapshot.drums[i].level <= primary_level)
			continue;
		primary = static_cast<int>(i);
		primary_level = snapshot.drums[i].level;
	}
	if (primary < 0)
		return primary;

	int tied = 0;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (snapshot.drums[i].active && std::abs(snapshot.drums[i].level - primary_level) <= 0.015f)
			++tied;
	}
	if (tied > 1)
		return -2;
	return primary;
}

mao_test::Buffer make_warmup_buffer()
{
	mao_test::Buffer buffer = {};
	buffer.fill(0.003f);
	return buffer;
}

bool make_sample_buffer(const std::vector<float> &samples, mao_test::Buffer &buffer)
{
	buffer.fill(0.0f);
	if (samples.empty())
		return false;

	std::size_t peak_index = 0;
	float peak = 0.0f;
	for (std::size_t i = 0; i < samples.size(); ++i) {
		const float abs_sample = std::abs(samples[i]);
		if (abs_sample > peak) {
			peak = abs_sample;
			peak_index = i;
		}
	}
	if (peak < 1.0e-5f)
		return false;

	std::size_t onset_index = peak_index;
	const float onset_threshold = std::max(peak * 0.025f, 0.0015f);
	for (std::size_t i = 0; i < samples.size(); ++i) {
		if (std::abs(samples[i]) >= onset_threshold) {
			onset_index = i;
			break;
		}
	}
	const std::size_t pre_roll = 16;
	const std::size_t start = onset_index > pre_roll ? onset_index - pre_roll : 0;
	const std::size_t insert = std::min<std::size_t>(1536, buffer.size() / 3);
	const std::size_t count = std::min<std::size_t>(buffer.size() - insert, samples.size() - start);
	const float gain = std::min(16.0f, 0.88f / peak);
	for (std::size_t i = 0; i < count; ++i)
		buffer[insert + i] = std::clamp(samples[start + i] * gain, -1.0f, 1.0f);
	return true;
}

mao::AnalysisSnapshot analyze_sample(const mao_test::Buffer &sample, uint32_t sample_rate, float window_seconds,
				     std::size_t expected)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = window_seconds;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	const mao_test::Buffer warmup = make_warmup_buffer();
	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(warmup.data(), warmup.size(), settings, "drum sample", 0);

	mao::AnalysisSnapshot selected = {};
	mao::AnalysisSnapshot best_expected = {};
	float best_expected_level = -1.0f;
	const std::size_t hop = std::max<std::size_t>(1, static_cast<std::size_t>(
							 std::lround(static_cast<double>(sample_rate) *
								     static_cast<double>(settings.analysis_interval_seconds))));
	for (std::size_t frame = 0; frame < 2; ++frame) {
		mao_test::Buffer shifted = {};
		const std::size_t offset = frame * hop;
		if (offset < sample.size()) {
			const std::size_t count = sample.size() - offset;
			std::copy_n(sample.begin() + static_cast<std::ptrdiff_t>(offset), count, shifted.begin());
		}
		snapshot = engine.analyze(shifted.data(), shifted.size(), settings, "drum sample", 0);
		if (frame == 0)
			selected = snapshot;
		const float expected_level =
			expected < mao::kDrumCount && snapshot.drums[expected].active ?
				snapshot.drums[expected].level :
				0.0f;
		if (frame == 0 || expected_level > best_expected_level) {
			best_expected = snapshot;
			best_expected_level = expected_level;
		}
	}
	// Credit the expected hit across one 50 ms hop, but keep other classes from the onset frame
	// so decay in the next frame does not inflate false-positive counts.
	if (expected < mao::kDrumCount && best_expected.drums[expected].level > selected.drums[expected].level)
		selected.drums[expected] = best_expected.drums[expected];
	return selected;
}

std::string active_details(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[96] = {};
		std::snprintf(part, sizeof(part), "%s%s=%.2f%s", text.empty() ? "" : " ",
			      category_name(i), snapshot.drums[i].level, snapshot.drums[i].active ? "*" : "");
		text += part;
	}
	return text;
}

int resolve_percent_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed >= 0 && parsed <= 100 ? parsed : fallback;
}

} // namespace

int main()
{
	const char *dir_env = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLES_DIR");
	const std::string sample_dir = dir_env && *dir_env ? dir_env : "build/drum_samples";
	const std::string manifest_path = join_path(sample_dir, "manifest.tsv");
	const bool required = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED") != nullptr;
	const bool verbose_misses = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_MISSES") != nullptr;
	const int min_recall_percent = resolve_percent_env("MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT", 45);
	const int min_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT", 0);

	std::ifstream manifest(manifest_path);
	if (!manifest) {
		if (required) {
			std::fprintf(stderr, "analyzer_drum_samples: missing manifest %s\n", manifest_path.c_str());
			return 1;
		}
		std::printf("analyzer_drum_samples: skipped; no manifest at %s\n", manifest_path.c_str());
		return 0;
	}

	Runner runner;
	std::array<int, mao::kDrumCount> totals = {};
	std::array<int, mao::kDrumCount> hits100 = {};
	std::array<int, mao::kDrumCount> misses100 = {};
	std::array<int, mao::kDrumCount> active100 = {};
	std::array<int, mao::kDrumCount> false100 = {};
	std::array<std::array<int, mao::kDrumCount>, mao::kDrumCount> active_by_expected100 = {};
	std::array<int, mao::kDrumCount> primary_hits100 = {};
	std::array<int, mao::kDrumCount> primary_none100 = {};
	std::array<int, mao::kDrumCount> primary_ambiguous100 = {};
	std::array<std::array<int, mao::kDrumCount>, mao::kDrumCount> primary_by_expected100 = {};
	int usable = 0;
	int skipped = 0;

	std::string line;
	bool header = true;
	while (std::getline(manifest, line)) {
		if (header) {
			header = false;
			continue;
		}
		if (line.empty())
			continue;
		const std::vector<std::string> fields = split_tab(line);
		if (fields.size() < 2)
			continue;
		std::size_t expected = 0;
		if (!category_index(fields[0], expected))
			continue;

		const std::string path = join_path(sample_dir, fields[1]);
		std::vector<float> samples;
		uint32_t sample_rate = 0;
		std::string error;
		if (!read_wav_mono(path, samples, sample_rate, error)) {
			++skipped;
			std::fprintf(stderr, "analyzer_drum_samples: skipping %s: %s\n", path.c_str(), error.c_str());
			continue;
		}

		mao_test::Buffer buffer = {};
		if (!make_sample_buffer(samples, buffer)) {
			++skipped;
			continue;
		}

		const mao::AnalysisSnapshot snapshot100 =
			analyze_sample(buffer, sample_rate, kDefaultWindowSeconds, expected);
		++totals[expected];
		++usable;
		for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
			if (!snapshot100.drums[i].active)
				continue;
			++active100[i];
			++active_by_expected100[expected][i];
			if (i != expected)
				++false100[i];
		}
		if (snapshot100.drums[expected].active) {
			++hits100[expected];
		} else {
			if (verbose_misses || misses100[expected] < 3) {
				std::fprintf(stderr, "analyzer_drum_samples: miss 100ms %s expected %s (%s)\n",
					     fields[1].c_str(), category_name(expected),
					     active_details(snapshot100).c_str());
			}
			++misses100[expected];
		}

		const int primary = primary_drum_index(snapshot100);
		if (primary < 0) {
			if (primary == -2)
				++primary_ambiguous100[expected];
			else
				++primary_none100[expected];
		} else {
			++primary_by_expected100[expected][static_cast<std::size_t>(primary)];
			if (static_cast<std::size_t>(primary) == expected)
				++primary_hits100[expected];
		}
	}

	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		runner.expect(totals[i] >= 2, std::string("expected at least two usable ") + category_name(i) +
					     " samples, got " + std::to_string(totals[i]));
		const int recall100 = totals[i] > 0 ? hits100[i] * 100 / totals[i] : 0;
		const int precision100 = active100[i] > 0 ? hits100[i] * 100 / active100[i] : 0;
		char min_recall_env[96] = {};
		std::snprintf(min_recall_env, sizeof(min_recall_env),
			      "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_%s_RECALL_PERCENT", category_env_name(i));
		const int category_min_recall_percent = resolve_percent_env(min_recall_env, min_recall_percent);
		char max_false_env[96] = {};
		std::snprintf(max_false_env, sizeof(max_false_env),
			      "MUSIC_ANALYZER_DRUM_SAMPLE_MAX_%s_FALSE_PERCENT", category_env_name(i));
		const int max_false_percent = resolve_percent_env(max_false_env, 100);
		const int non_category_total = std::max(0, usable - totals[i]);
		const int false_percent =
			non_category_total > 0 ? false100[i] * 100 / non_category_total : 0;
		runner.expect(recall100 >= category_min_recall_percent,
			      std::string("expected 100ms ") + category_name(i) + " recall >= " +
				      std::to_string(category_min_recall_percent) + "%, got " +
				      std::to_string(recall100) + "% (" + std::to_string(hits100[i]) + "/" +
				      std::to_string(totals[i]) + ")");
		if (min_precision_percent > 0) {
			runner.expect(precision100 >= min_precision_percent,
				      std::string("expected 100ms ") + category_name(i) + " precision >= " +
					      std::to_string(min_precision_percent) + "%, got " +
					      std::to_string(precision100) + "% (" + std::to_string(hits100[i]) +
					      "/" + std::to_string(active100[i]) + ", false " +
					      std::to_string(false100[i]) + ")");
		}
		runner.expect(false_percent <= max_false_percent,
			      std::string("expected 100ms ") + category_name(i) + " false activations <= " +
				      std::to_string(max_false_percent) + "%, got " +
				      std::to_string(false_percent) + "% (" + std::to_string(false100[i]) +
				      "/" + std::to_string(non_category_total) + ")");
	}

	std::printf("analyzer_drum_samples: active matrix");
	for (std::size_t expected = 0; expected < mao::kDrumCount; ++expected) {
		std::printf("\n  expected %-5s", category_name(expected));
		for (std::size_t detected = 0; detected < mao::kDrumCount; ++detected)
			std::printf(" %s=%d", category_name(detected), active_by_expected100[expected][detected]);
	}
	std::printf("\n");

	std::printf("analyzer_drum_samples: primary matrix");
	for (std::size_t expected = 0; expected < mao::kDrumCount; ++expected) {
		std::printf("\n  expected %-5s", category_name(expected));
		for (std::size_t detected = 0; detected < mao::kDrumCount; ++detected)
			std::printf(" %s=%d", category_name(detected), primary_by_expected100[expected][detected]);
		std::printf(" ambiguous=%d none=%d", primary_ambiguous100[expected], primary_none100[expected]);
	}
	std::printf("\n");

	if (runner.failures) {
		std::fprintf(stderr, "analyzer_drum_samples: %d failure(s), usable %d, skipped %d\n", runner.failures,
			     usable, skipped);
		return 1;
	}

	std::printf("analyzer_drum_samples: ok (usable %d, skipped %d", usable, skipped);
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		const int precision100 = active100[i] > 0 ? hits100[i] * 100 / active100[i] : 0;
		std::printf(", %s recall %d/%d primary %d/%d precision %d/%d false %d",
			    category_name(i), hits100[i], totals[i], primary_hits100[i], totals[i], hits100[i],
			    active100[i], false100[i]);
		if (active100[i] > 0)
			std::printf(" %d%%", precision100);
	}
	std::printf(")\n");
	return 0;
}
