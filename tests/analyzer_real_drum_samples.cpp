#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

namespace {

constexpr const char *kDefaultRoot = "/media/kyz/sshflashtor/InstrumentSamples/idmt_drums_samples";
constexpr std::array<const char *, 3> kCategories = {"kick", "snare", "hihat"};
constexpr std::array<std::size_t, 3> kDrumIndexes = {0, 1, 2};
constexpr int kMaximumSamplesPerCategory = 128;

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

struct DrumRow {
	std::string category;
	std::string path;
	std::string source;
};

uint16_t read_u16(std::ifstream &file)
{
	unsigned char bytes[2] = {};
	file.read(reinterpret_cast<char *>(bytes), sizeof(bytes));
	return static_cast<uint16_t>(bytes[0]) | static_cast<uint16_t>(bytes[1] << 8);
}

uint32_t read_u32(std::ifstream &file)
{
	unsigned char bytes[4] = {};
	file.read(reinterpret_cast<char *>(bytes), sizeof(bytes));
	return static_cast<uint32_t>(bytes[0]) | (static_cast<uint32_t>(bytes[1]) << 8) |
	       (static_cast<uint32_t>(bytes[2]) << 16) | (static_cast<uint32_t>(bytes[3]) << 24);
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
		const int32_t value = static_cast<int32_t>(bytes[0]) | (static_cast<int32_t>(bytes[1]) << 8) |
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

std::size_t first_audible_sample(const std::vector<float> &samples, float peak)
{
	const float threshold = std::max(peak * 0.020f, 0.0008f);
	for (std::size_t i = 0; i < samples.size(); ++i) {
		if (std::abs(samples[i]) >= threshold)
			return i;
	}
	return 0;
}

bool make_sample_buffer_at(const std::vector<float> &samples, std::size_t start, mao_test::Buffer &buffer)
{
	buffer.fill(0.0f);
	if (samples.empty() || start >= samples.size())
		return false;
	const std::size_t count = std::min<std::size_t>(buffer.size(), samples.size() - start);
	float peak = 0.0f;
	for (std::size_t i = 0; i < count; ++i)
		peak = std::max(peak, std::abs(samples[start + i]));
	if (peak < 1.0e-5f)
		return false;
	const float gain = std::min(24.0f, 0.62f / peak);
	for (std::size_t i = 0; i < count; ++i)
		buffer[i] = std::clamp(samples[start + i] * gain, -1.0f, 1.0f);
	return true;
}

std::vector<mao_test::Buffer> make_sample_buffers(const std::vector<float> &samples, uint32_t sample_rate)
{
	std::vector<mao_test::Buffer> buffers;
	if (samples.empty() || sample_rate == 0)
		return buffers;
	float peak = 0.0f;
	for (float sample : samples)
		peak = std::max(peak, std::abs(sample));
	if (peak < 1.0e-5f)
		return buffers;
	const std::size_t onset = first_audible_sample(samples, peak);
	static constexpr double kOffsetsSeconds[] = {0.000, 0.005, 0.015, 0.035};
	std::size_t previous_start = samples.size();
	for (double offset_seconds : kOffsetsSeconds) {
		const std::size_t offset = static_cast<std::size_t>(sample_rate * offset_seconds);
		const std::size_t start = std::min(samples.size() - 1, onset + offset);
		if (start == previous_start)
			continue;
		previous_start = start;
		mao_test::Buffer buffer = {};
		if (make_sample_buffer_at(samples, start, buffer))
			buffers.push_back(buffer);
	}
	return buffers;
}

mao::AnalysisSnapshot analyze_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate, const char *source)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	mao_test::Buffer silence = {};
	engine.analyze(silence.data(), silence.size(), settings, source, 0);
	return engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
}

std::vector<std::string> split_tab(const std::string &line)
{
	std::vector<std::string> fields;
	std::string field;
	std::istringstream input(line);
	while (std::getline(input, field, '\t'))
		fields.push_back(field);
	return fields;
}

bool read_manifest(const std::string &path, std::vector<DrumRow> &rows)
{
	std::ifstream file(path);
	if (!file)
		return false;
	std::string header;
	if (!std::getline(file, header))
		return false;
	const std::vector<std::string> columns = split_tab(header);
	std::map<std::string, std::size_t> index;
	for (std::size_t i = 0; i < columns.size(); ++i)
		index[columns[i]] = i;
	if (index.count("category") == 0 || index.count("path") == 0 || index.count("source") == 0)
		return false;
	std::string line;
	while (std::getline(file, line)) {
		const std::vector<std::string> fields = split_tab(line);
		if (fields.size() != columns.size())
			continue;
		rows.push_back({fields[index["category"]], fields[index["path"]], fields[index["source"]]});
	}
	return !rows.empty();
}

int minimum_percent(const char *name)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return 0;
	return std::clamp(std::atoi(value), 0, 100);
}

} // namespace

int main()
{
	const char *root_env = std::getenv("MUSIC_ANALYZER_REAL_DRUM_ROOT");
	const std::string root = root_env && *root_env ? root_env : kDefaultRoot;
	const char *source_env = std::getenv("MUSIC_ANALYZER_REAL_DRUM_SOURCE");
	const char *source = source_env && *source_env ? source_env : "Speaker Monitor";
	std::vector<DrumRow> manifest;
	if (!read_manifest(root + "/manifest.tsv", manifest)) {
		std::fprintf(stderr, "analyzer_real_drum_samples: missing or invalid manifest under %s\n", root.c_str());
		return 1;
	}

	int failures = 0;
	const bool verbose = std::getenv("MUSIC_ANALYZER_REAL_DRUM_VERBOSE") != nullptr;
	for (std::size_t category_index = 0; category_index < kCategories.size(); ++category_index) {
		const char *category = kCategories[category_index];
		std::set<std::string> sources;
		std::set<std::string> signatures;
		std::vector<DrumRow> selected;
		for (const DrumRow &row : manifest) {
			if (row.category != category)
				continue;
			const bool new_source = sources.insert(row.source).second;
			if (!new_source && !signatures.insert(row.path).second)
				continue;
			signatures.insert(row.path);
			selected.push_back(row);
			if (static_cast<int>(selected.size()) >= kMaximumSamplesPerCategory)
				break;
		}
		int hits = 0;
		int loaded = 0;
		int reported_misses = 0;
		for (const DrumRow &row : selected) {
			std::vector<float> samples;
			uint32_t sample_rate = 0;
			std::string error;
			if (!read_wav_mono(root + "/" + row.path, samples, sample_rate, error)) {
				std::fprintf(stderr, "analyzer_real_drum_samples: load %s failed: %s\n", row.path.c_str(), error.c_str());
				continue;
			}
			++loaded;
			const std::vector<mao_test::Buffer> buffers = make_sample_buffers(samples, sample_rate);
			bool active = false;
			mao::AnalysisSnapshot last_snapshot = {};
			for (const mao_test::Buffer &buffer : buffers) {
				const mao::AnalysisSnapshot snapshot = analyze_buffer(buffer, sample_rate, source);
				last_snapshot = snapshot;
				if (snapshot.drums[kDrumIndexes[category_index]].active) {
					active = true;
					break;
				}
			}
			if (active) {
				++hits;
			} else if (verbose && reported_misses < 16) {
				const std::size_t index = kDrumIndexes[category_index];
				std::fprintf(stderr,
					     "real-drums miss category=%s path=%s level=%.3f score=%.3f threshold=%.3f band=%.3f onset=%.3f transient=%.3f snare-body=%.3f crack=%.3f levels=k%.3f,s%.3f,h%.3f,c%.3f,t%.3f,r%.3f,m%.3f flags=%llu\n",
					     category, row.path.c_str(), last_snapshot.drums[index].level,
					     last_snapshot.drum_debug_trigger_scores[index],
					     last_snapshot.drum_debug_trigger_thresholds[index],
					     last_snapshot.drum_debug_bands[index], last_snapshot.drum_debug_onset,
					     last_snapshot.drum_debug_transient_ratio, last_snapshot.drum_debug_snare_body,
					     last_snapshot.drum_debug_snare_crack, last_snapshot.drums[0].level,
					     last_snapshot.drums[1].level, last_snapshot.drums[2].level,
					     last_snapshot.drums[3].level, last_snapshot.drums[4].level,
					     last_snapshot.drums[5].level, last_snapshot.drums[6].level,
					     static_cast<unsigned long long>(last_snapshot.drum_debug_rule_flags));
				++reported_misses;
			}
		}
		const int percent = loaded > 0 ? hits * 100 / loaded : 0;
		const std::string variable = "MUSIC_ANALYZER_REAL_DRUM_MIN_" + std::string(category == std::string("hihat") ? "HIHAT" : category == std::string("kick") ? "KICK" : "SNARE");
		const int minimum = minimum_percent(variable.c_str());
		std::printf("real-drums source=%s %s=%d/%d (%d%%) minimum=%d%%\n", source, category, hits,
			    loaded, percent, minimum);
		if (loaded == 0 || percent < minimum)
			++failures;
	}
	return failures == 0 ? 0 : 1;
}
