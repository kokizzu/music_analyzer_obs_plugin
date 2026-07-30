#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cctype>
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

struct SourceStats {
	std::array<int, mao::kDrumCount> total = {};
	std::array<int, mao::kDrumCount> hits = {};
	std::array<int, mao::kDrumCount> primary_hits = {};
};

struct DrumSampleAnalysis {
	mao::AnalysisSnapshot snapshot = {};
	mao::AnalysisSnapshot merged_expected_snapshot = {};
	bool merged_expected_from_later_frame = false;
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

std::vector<std::string> split_path_components(const std::string &path)
{
	std::vector<std::string> parts;
	std::string part;
	for (char c : path) {
		if (c == '/' || c == '\\') {
			if (!part.empty()) {
				parts.push_back(part);
				part.clear();
			}
			continue;
		}
		part.push_back(c);
	}
	if (!part.empty())
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

std::string drum_source_bucket(const std::vector<std::string> &fields)
{
	std::string source = fields.size() >= 4 ? fields[3] : fields.size() >= 2 ? fields[1] : "unknown";
	const std::size_t archive_separator = source.find('!');
	if (archive_separator != std::string::npos) {
		const std::string archive = source.substr(0, archive_separator);
		const std::string member = source.substr(archive_separator + 1);
		const std::vector<std::string> archive_parts = split_path_components(archive);
		std::string archive_label = archive_parts.empty() ? "archive" : archive_parts.back();
		const std::size_t extension = archive_label.find_last_of('.');
		if (extension != std::string::npos)
			archive_label.resize(extension);

		const std::vector<std::string> member_parts = split_path_components(member);
		if (!member_parts.empty()) {
			std::size_t category = 0;
			if (member_parts.size() >= 2 && !category_index(member_parts[0], category)) {
				if (member_parts[0] == archive_label) {
					if (member_parts.size() >= 3 && !category_index(member_parts[1], category))
						return archive_label + "/" + member_parts[1];
					return archive_label;
				}
				return archive_label + "/" + member_parts[0];
			}
		}
		return archive_label;
	}
	const std::vector<std::string> parts = split_path_components(source);
	if (parts.empty())
		return "unknown";
	for (std::size_t i = 0; i + 1 < parts.size(); ++i) {
		if (parts[i] == "Drum Samples")
			return parts[i + 1];
	}
	if (parts.size() >= 2)
		return parts[parts.size() - 2];
	return parts[0];
}

struct SourceSummaryRow {
	std::string source;
	std::size_t category = 0;
	int total = 0;
	int hits = 0;
	int misses = 0;
};

std::string source_summary_text(const std::map<std::string, SourceStats> &stats, bool primary, int max_entries)
{
	std::vector<SourceSummaryRow> rows;
	for (const auto &entry : stats) {
		for (std::size_t category = 0; category < mao::kDrumCount; ++category) {
			const int total = entry.second.total[category];
			if (total <= 0)
				continue;
			const int hits = primary ? entry.second.primary_hits[category] : entry.second.hits[category];
			const int misses = total - hits;
			if (misses <= 0)
				continue;
			rows.push_back({entry.first, category, total, hits, misses});
		}
	}
	std::sort(rows.begin(), rows.end(), [](const SourceSummaryRow &lhs, const SourceSummaryRow &rhs) {
		if (lhs.misses != rhs.misses)
			return lhs.misses > rhs.misses;
		if (lhs.total != rhs.total)
			return lhs.total > rhs.total;
		if (lhs.category != rhs.category)
			return lhs.category < rhs.category;
		return lhs.source < rhs.source;
	});
	if (rows.empty())
		return "";

	std::string text = primary ? " source primary misses" : " source misses";
	const int count = std::min<int>(max_entries, static_cast<int>(rows.size()));
	for (int i = 0; i < count; ++i) {
		text += " ";
		text += category_name(rows[i].category);
		text += "/";
		text += rows[i].source;
		text += "=";
		text += std::to_string(rows[i].hits);
		text += "/";
		text += std::to_string(rows[i].total);
	}
	if (static_cast<int>(rows.size()) > count)
		text += " ...";
	return text;
}

std::string normalized_token(const std::string &text)
{
	std::string normalized;
	for (unsigned char c : text) {
		if (std::isalnum(c))
			normalized.push_back(static_cast<char>(std::tolower(c)));
	}
	return normalized;
}

bool category_token_index(const std::string &category, std::size_t &index)
{
	const std::string normalized = normalized_token(category);
	if (normalized == "bd" || normalized == "bassdrum" || normalized == "kickdrum") {
		index = 0;
		return true;
	}
	if (normalized == "hat" || normalized == "closedhat" || normalized == "openhihat") {
		index = 2;
		return true;
	}
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (normalized == normalized_token(category_name(i))) {
			index = i;
			return true;
		}
	}
	return false;
}

std::array<bool, mao::kDrumCount> required_categories_from_env()
{
	std::array<bool, mao::kDrumCount> required = {};
	const char *env = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES");
	if (!env || !*env) {
		required.fill(true);
		return required;
	}

	std::istringstream input(env);
	std::string token;
	int accepted = 0;
	while (std::getline(input, token, ',')) {
		const std::string normalized = normalized_token(token);
		if (normalized.empty())
			continue;
		if (normalized == "all") {
			required.fill(true);
			return required;
		}
		std::size_t index = 0;
		if (!category_token_index(token, index)) {
			std::fprintf(stderr,
				     "analyzer_drum_samples: ignoring unknown required category `%s`\n",
				     token.c_str());
			continue;
		}
		required[index] = true;
		++accepted;
	}
	if (accepted == 0) {
		std::fprintf(stderr,
			     "analyzer_drum_samples: no valid MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES; using all\n");
		required.fill(true);
	}
	return required;
}

int primary_drum_index(const mao::AnalysisSnapshot &snapshot, std::size_t expected = mao::kDrumCount,
		       bool merged_expected_from_later_frame = false)
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

	if (merged_expected_from_later_frame && expected < mao::kDrumCount &&
	    snapshot.drums[expected].active && snapshot.drums[expected].level >= 0.90f &&
	    snapshot.drums[expected].level + 0.025f >= primary_level)
		return static_cast<int>(expected);

	int tied = 0;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (snapshot.drums[i].active && std::abs(snapshot.drums[i].level - primary_level) <= 0.005f)
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

DrumSampleAnalysis analyze_sample(const mao_test::Buffer &sample, uint32_t sample_rate, float window_seconds,
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
	DrumSampleAnalysis analysis = {};
	analysis.snapshot = selected;
	analysis.merged_expected_snapshot = best_expected;
	if (expected < mao::kDrumCount && best_expected.drums[expected].level > selected.drums[expected].level) {
		analysis.merged_expected_from_later_frame = true;
		selected.drums[expected] = best_expected.drums[expected];
		analysis.snapshot = selected;
	}
	return analysis;
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

std::string debug_details(const mao::AnalysisSnapshot &snapshot, bool merged_expected_from_later_frame)
{
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[224] = {};
		std::snprintf(part, sizeof(part),
			      "%s%s band=%.6f seg=%.6f shape_score=%.6f trigger=%.6f/%.6f shape=%d level=%.6f",
			      text.empty() ? "" : " | ", category_name(i), snapshot.drum_debug_bands[i],
			      snapshot.drum_debug_segment_bands[i], snapshot.drum_debug_shape_scores[i],
			      snapshot.drum_debug_trigger_scores[i],
			      snapshot.drum_debug_trigger_thresholds[i],
			      snapshot.drum_debug_shape_supported[i] ? 1 : 0, snapshot.drums[i].level);
		text += part;
	}
	char part[416] = {};
	std::snprintf(part, sizeof(part),
		      " | transient=%.6f onset=%.6f energy=%.6f/%.6f/%.6f body=%.6f/%.6f/%.6f crack=%.6f upper_tom=%.6f body_shape=%d rule_flags=0x%llx",
		      snapshot.drum_debug_transient_ratio, snapshot.drum_debug_onset,
		      snapshot.low_energy, snapshot.mid_energy, snapshot.high_energy,
		      snapshot.drum_debug_kick_body, snapshot.drum_debug_snare_body,
		      snapshot.drum_debug_tom_body, snapshot.drum_debug_snare_crack,
		      snapshot.drum_debug_upper_tom_body, snapshot.drum_debug_body_shape,
		      static_cast<unsigned long long>(snapshot.drum_debug_rule_flags));
	text += part;
	text += merged_expected_from_later_frame ? " merged_expected=1" : " merged_expected=0";
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

int resolve_non_negative_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed >= 0 ? parsed : fallback;
}

} // namespace

int main()
{
	const char *dir_env = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLES_DIR");
	const std::string sample_dir = dir_env && *dir_env ? dir_env : "build/drum_samples";
	const std::string manifest_path = join_path(sample_dir, "manifest.tsv");
	const bool required = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED") != nullptr;
	const bool verbose_misses = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_MISSES") != nullptr;
	const bool verbose_primary = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY") != nullptr;
	const bool verbose_all = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL") != nullptr;
	const bool verbose_merged_expected =
		std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_MERGED_EXPECTED") != nullptr;
	const bool source_summary = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_SOURCE_SUMMARY") != nullptr;
	const char *filter_category_env = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY");
	const char *filter_source_env = std::getenv("MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_SOURCE");
	const std::string filter_source = filter_source_env && *filter_source_env ? filter_source_env : "";
	std::size_t filter_category = mao::kDrumCount;
	if (filter_category_env && *filter_category_env && !category_token_index(filter_category_env, filter_category)) {
		std::fprintf(stderr, "analyzer_drum_samples: unknown filter category `%s`\n", filter_category_env);
		return 1;
	}
	const int verbose_primary_limit =
		resolve_non_negative_env("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT", 80);
	const int min_recall_percent = resolve_percent_env("MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT", 45);
	const int min_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT", 0);
	const int min_primary_percent =
		resolve_percent_env("MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT", 0);
	const std::array<bool, mao::kDrumCount> required_categories = required_categories_from_env();

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
	std::map<std::string, SourceStats> source_stats;
	int usable = 0;
	int skipped = 0;
	int verbose_all_lines = 0;
	int verbose_primary_lines = 0;

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
		if (filter_category < mao::kDrumCount && expected != filter_category)
			continue;
		const std::string source_bucket = drum_source_bucket(fields);
		if (!filter_source.empty() && source_bucket.find(filter_source) == std::string::npos)
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

		const DrumSampleAnalysis analysis100 =
			analyze_sample(buffer, sample_rate, kDefaultWindowSeconds, expected);
		const mao::AnalysisSnapshot &snapshot100 = analysis100.snapshot;
		if (verbose_all && verbose_all_lines < verbose_primary_limit) {
			++verbose_all_lines;
			std::fprintf(stderr, "analyzer_drum_samples: debug 100ms %s expected %s (%s) [%s]\n",
				     fields[1].c_str(), category_name(expected),
				     active_details(snapshot100).c_str(),
				     debug_details(snapshot100, analysis100.merged_expected_from_later_frame).c_str());
		}
		if (verbose_merged_expected && analysis100.merged_expected_from_later_frame &&
		    verbose_all_lines < verbose_primary_limit) {
			++verbose_all_lines;
			std::fprintf(stderr,
				     "analyzer_drum_samples: merged debug 100ms %s#merged expected %s (%s) [%s]\n",
				     fields[1].c_str(), category_name(expected),
				     active_details(analysis100.merged_expected_snapshot).c_str(),
				     debug_details(analysis100.merged_expected_snapshot, true).c_str());
		}
		++totals[expected];
		++usable;
		SourceStats &source_stat = source_stats[source_bucket];
		++source_stat.total[expected];
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
			++source_stat.hits[expected];
		} else {
			if (verbose_misses || misses100[expected] < 3) {
				std::fprintf(stderr, "analyzer_drum_samples: miss 100ms %s expected %s (%s)\n",
					     fields[1].c_str(), category_name(expected),
					     active_details(snapshot100).c_str());
			}
			++misses100[expected];
		}

		const int primary =
			primary_drum_index(snapshot100, expected, analysis100.merged_expected_from_later_frame);
		if (verbose_primary && primary >= 0 && static_cast<std::size_t>(primary) != expected &&
		    verbose_primary_lines < verbose_primary_limit) {
			++verbose_primary_lines;
			std::fprintf(stderr,
				     "analyzer_drum_samples: primary miss 100ms %s expected %s got %s (%s) [%s]\n",
				     fields[1].c_str(), category_name(expected),
				     category_name(static_cast<std::size_t>(primary)),
				     active_details(snapshot100).c_str(),
				     debug_details(snapshot100, analysis100.merged_expected_from_later_frame).c_str());
		}
		if (primary < 0) {
			if (verbose_primary && verbose_primary_lines < verbose_primary_limit) {
				++verbose_primary_lines;
				std::fprintf(stderr,
					     "analyzer_drum_samples: primary miss 100ms %s expected %s got %s (%s) [%s]\n",
					     fields[1].c_str(), category_name(expected),
					     primary == -2 ? "ambiguous" : "none",
					     active_details(snapshot100).c_str(),
					     debug_details(snapshot100, analysis100.merged_expected_from_later_frame).c_str());
			}
			if (primary == -2)
				++primary_ambiguous100[expected];
			else
				++primary_none100[expected];
		} else {
			++primary_by_expected100[expected][static_cast<std::size_t>(primary)];
			if (static_cast<std::size_t>(primary) == expected) {
				++primary_hits100[expected];
				++source_stat.primary_hits[expected];
			}
		}
	}

	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!required_categories[i] && totals[i] == 0)
			continue;
		if (required_categories[i]) {
			runner.expect(totals[i] >= 2, std::string("expected at least two usable ") +
							     category_name(i) + " samples, got " +
							     std::to_string(totals[i]));
		}
		if (totals[i] == 0)
			continue;
		const int recall100 = totals[i] > 0 ? hits100[i] * 100 / totals[i] : 0;
		const int primary_recall100 = totals[i] > 0 ? primary_hits100[i] * 100 / totals[i] : 0;
		const int precision100 = active100[i] > 0 ? hits100[i] * 100 / active100[i] : 0;
		char min_recall_env[96] = {};
		std::snprintf(min_recall_env, sizeof(min_recall_env),
			      "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_%s_RECALL_PERCENT", category_env_name(i));
		const int category_min_recall_percent = resolve_percent_env(min_recall_env, min_recall_percent);
		char min_primary_env[112] = {};
		std::snprintf(min_primary_env, sizeof(min_primary_env),
			      "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_%s_PRIMARY_RECALL_PERCENT", category_env_name(i));
		const int category_min_primary_percent = resolve_percent_env(min_primary_env, min_primary_percent);
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
		if (category_min_primary_percent > 0) {
			runner.expect(primary_recall100 >= category_min_primary_percent,
				      std::string("expected 100ms ") + category_name(i) +
					      " primary recall >= " +
					      std::to_string(category_min_primary_percent) + "%, got " +
					      std::to_string(primary_recall100) + "% (" +
					      std::to_string(primary_hits100[i]) + "/" +
					      std::to_string(totals[i]) + ")");
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
		const std::string miss_summary = source_summary_text(source_stats, false, 12);
		const std::string primary_summary = source_summary_text(source_stats, true, 12);
		if (!miss_summary.empty())
			std::fprintf(stderr, "analyzer_drum_samples:%s\n", miss_summary.c_str());
		if (!primary_summary.empty())
			std::fprintf(stderr, "analyzer_drum_samples:%s\n", primary_summary.c_str());
		std::fprintf(stderr, "analyzer_drum_samples: %d failure(s), usable %d, skipped %d\n", runner.failures,
			     usable, skipped);
		return 1;
	}

	if (source_summary) {
		const std::string miss_summary = source_summary_text(source_stats, false, 12);
		const std::string primary_summary = source_summary_text(source_stats, true, 12);
		if (!miss_summary.empty())
			std::printf("analyzer_drum_samples:%s\n", miss_summary.c_str());
		if (!primary_summary.empty())
			std::printf("analyzer_drum_samples:%s\n", primary_summary.c_str());
	}

	std::printf("analyzer_drum_samples: ok (usable %d, skipped %d", usable, skipped);
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!required_categories[i] && totals[i] == 0) {
			std::printf(", %s optional absent false %d", category_name(i), false100[i]);
			continue;
		}
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
