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
#include <sstream>
#include <string>
#include <vector>

namespace {

constexpr float kDefaultWindowSeconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;

struct Runner {
	int checks = 0;
	int failures = 0;
	int reported_failures = 0;
	int max_reported_failures = 40;

	void expect(bool ok, const std::string &message)
	{
		++checks;
		if (!ok) {
			++failures;
			if (reported_failures < max_reported_failures) {
				std::fprintf(stderr, "%s\n", message.c_str());
			} else if (reported_failures == max_reported_failures) {
				std::fprintf(stderr, "further analyzer_instrument_family_samples failures suppressed\n");
			}
			++reported_failures;
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

struct SampleRow {
	std::string id;
	std::string family;
	std::string instrument;
	std::string subset;
	std::string path;
};

struct FamilyStats {
	int total = 0;
	int hits = 0;
	std::array<int, 4> cross = {};
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

bool read_manifest(const std::string &path, std::vector<SampleRow> &rows)
{
	std::ifstream manifest(path);
	if (!manifest)
		return false;

	std::string line;
	bool header = true;
	while (std::getline(manifest, line)) {
		// Python's csv writer emits CRLF by default.  Strip the retained CR so
		// relative audio paths resolve identically on every host.
		if (!line.empty() && line.back() == '\r')
			line.pop_back();
		if (header) {
			header = false;
			continue;
		}
		if (line.empty())
			continue;
		const std::vector<std::string> fields = split_tab(line);
		if (fields.size() < 7)
			continue;
		SampleRow row;
		row.id = fields[0];
		row.family = fields[1];
		row.instrument = fields[2];
		row.subset = fields[3];
		row.path = fields[6];
		rows.push_back(row);
	}
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

bool make_sample_buffer_at(const std::vector<float> &samples, std::size_t start, mao_test::Buffer &buffer,
			   float target_peak)
{
	buffer.fill(0.0f);
	if (samples.empty() || start >= samples.size())
		return false;

	const std::size_t count = std::min<std::size_t>(buffer.size(), samples.size() - start);
	if (count == 0)
		return false;

	float window_peak = 0.0f;
	for (std::size_t i = 0; i < count; ++i)
		window_peak = std::max(window_peak, std::abs(samples[start + i]));
	if (window_peak < 1.0e-5f)
		return false;

	const float gain = std::min(18.0f, target_peak / window_peak);
	for (std::size_t i = 0; i < count; ++i)
		buffer[i] = std::clamp(samples[start + i] * gain, -1.0f, 1.0f);
	return true;
}

std::vector<mao_test::Buffer> make_sample_buffers(const std::vector<float> &samples, uint32_t sample_rate,
						  float target_peak)
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
	static constexpr double kOffsetsSeconds[] = {0.080, 0.180, 0.320, 0.520, 0.820, 1.200, 1.800, 2.300};
	std::size_t previous_start = samples.size();
	for (double offset_seconds : kOffsetsSeconds) {
		const std::size_t offset =
			static_cast<std::size_t>(static_cast<double>(sample_rate) * offset_seconds);
		const std::size_t start = std::min(samples.size() - 1, onset + offset);
		if (start == previous_start)
			continue;
		previous_start = start;

		mao_test::Buffer buffer = {};
		if (make_sample_buffer_at(samples, start, buffer, target_peak))
			buffers.push_back(buffer);
	}
	return buffers;
}

bool grid_has_any_active(const mao::NoteGrid &grid)
{
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active)
				return true;
		}
	}
	for (const mao::NoteCell &cell : grid.cells) {
		if (cell.active)
			return true;
	}
	return false;
}

const mao::InstrumentState &family_state(const mao::AnalysisSnapshot &snapshot, const std::string &family)
{
	if (family == "guitar")
		return snapshot.guitar;
	if (family == "piano")
		return snapshot.keyboard;
	if (family == "vocals")
		return snapshot.vocal;
	return snapshot.other;
}

const mao::NoteGrid &family_grid(const mao::AnalysisSnapshot &snapshot, const std::string &family)
{
	if (family == "guitar")
		return snapshot.guitar_notes;
	if (family == "piano")
		return snapshot.keyboard_notes;
	if (family == "vocals")
		return snapshot.vocal_notes;
	return snapshot.other_notes;
}

bool family_detected(const mao::AnalysisSnapshot &snapshot, const std::string &family)
{
	return family_state(snapshot, family).confidence > 0.0f || grid_has_any_active(family_grid(snapshot, family));
}

void print_attribute_header(std::ostream &out)
{
	out << "sample_id\tfamily\tinstrument\tsubset\tbuffer_index\texpected_row_hit"

	       "\tguitar_active\tpiano_active\tvocals_active\tother_active"

	       "\tguitar_confidence\tpiano_confidence\tvocals_confidence\tother_confidence"

	       "\tguitar_label\tpiano_label\tvocals_label\tother_label\n";
}

void append_attribute_row(std::ostream &out, const SampleRow &row, std::size_t buffer_index,
			  const mao::AnalysisSnapshot &snapshot)
{
	const std::array<const char *, 4> families = {"guitar", "piano", "vocals", "other"};
	out << row.id << '\t' << row.family << '\t' << row.instrument << '\t' << row.subset << '\t'
	    << buffer_index << '\t' << (family_detected(snapshot, row.family) ? 1 : 0);
	for (const char *family : families)
		out << '\t' << (family_detected(snapshot, family) ? 1 : 0);
	for (const char *family : families)
		out << '\t' << family_state(snapshot, family).confidence;
	for (const char *family : families)
		out << '\t' << family_state(snapshot, family).label;
	out << '\n';
}

int family_index(const std::string &family)
{
	if (family == "guitar")
		return 0;
	if (family == "piano")
		return 1;
	if (family == "vocals")
		return 2;
	return 3;
}

const char *family_name(int index)
{
	static constexpr const char *kNames[4] = {"guitar", "piano", "vocals", "other"};
	return index >= 0 && index < 4 ? kNames[index] : "unknown";
}

const char *instrument_name(mao::InstrumentKind instrument)
{
	switch (instrument) {
	case mao::InstrumentKind::Bass:
		return "bass";
	case mao::InstrumentKind::Guitar:
		return "guitar";
	case mao::InstrumentKind::Keyboard:
		return "piano";
	case mao::InstrumentKind::Vocal:
		return "vocals";
	case mao::InstrumentKind::Other:
		return "other";
	case mao::InstrumentKind::Ambiguous:
		return "ambiguous";
	}
	return "unknown";
}

void print_full_mix_debug(const SampleRow &row, std::size_t buffer_index,
			  const mao::AnalysisSnapshot &snapshot)
{
	std::fprintf(stderr,
		     "instrument_family_debug sample=%s expected=%s/%s buffer=%zu rows="
		     "guitar:%s piano:%s vocals:%s other:%s candidates=%zu\n",
		     row.id.c_str(), row.family.c_str(), row.instrument.c_str(), buffer_index,
		     snapshot.guitar.label, snapshot.keyboard.label, snapshot.vocal.label,
		     snapshot.other.label, snapshot.full_mix_debug_candidate_count);
	const std::size_t count = std::min(snapshot.full_mix_debug_candidate_count,
					   snapshot.full_mix_debug_candidates.size());
	for (std::size_t index = 0; index < count; ++index) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[index];
		std::fprintf(stderr,
			     "  candidate midi=%d owner=%s own=%.3f scores=k%.3f g%.3f v%.3f o%.3f "
			     "level=%.3f pitch=%.3f periodic=%.3f harmonicity=%.3f fit=%.3f noise=%.3f "
			     "centroid=%.3f slope=%.3f "
			     "harmonics=%.3f,%.3f,%.3f,%.3f\n",
			     debug.midi, instrument_name(debug.owner), debug.ownership_confidence,
			     debug.keyboard_score, debug.guitar_score, debug.vocal_score, debug.other_score,
			     debug.spectral_level, debug.pitch_confidence, debug.periodicity,
			     debug.harmonicity, debug.harmonic_fit_error, debug.local_noise_level,
			     debug.spectral_centroid, debug.spectral_slope,
			     debug.harmonic_ratios[1], debug.harmonic_ratios[2], debug.harmonic_ratios[3],
			     debug.harmonic_ratios[4]);
	}
}

mao::AnalysisSnapshot analyze_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate, int frames = 4)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = kDefaultWindowSeconds;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < frames; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Medley Solos", 0);
	return snapshot;
}

int positive_int_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed > 0 ? parsed : fallback;
}

int nonnegative_int_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed >= 0 ? parsed : fallback;
}

int percent_env(const char *name, int fallback)
{
	const int value = nonnegative_int_env(name, fallback);
	return std::clamp(value, 0, 100);
}

} // namespace

int main()
{
	const char *root_env = std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT");
	const std::string root = root_env && *root_env ? root_env : "build/medley_solos_samples";
	const bool required = std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED") != nullptr;
	const bool strict_sample_recall =
		std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_STRICT_SAMPLE_RECALL") != nullptr;
	const char *sample_filter = std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ID");
	const char *debug_sample_id = std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_DEBUG_SAMPLE_ID");
	const int required_samples = positive_int_env("MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES", 600);
	const int min_recall_percent = percent_env("MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT", 20);
	const int shard_count = positive_int_env("MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_COUNT", 1);
	const int shard_index = nonnegative_int_env("MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_INDEX", 0);
	const char *attribute_path_env = std::getenv("MUSIC_ANALYZER_INSTRUMENT_FAMILY_ATTRIBUTE_TSV");
	std::ofstream attribute_file;
	if (attribute_path_env && *attribute_path_env) {
		attribute_file.open(attribute_path_env);
		if (!attribute_file) {
			std::fprintf(stderr,
				     "analyzer_instrument_family_samples: failed to open attribute TSV `%s`\n",
				     attribute_path_env);
			return 1;
		}
		print_attribute_header(attribute_file);
	}
	if (shard_index >= shard_count) {
		std::fprintf(stderr,
			     "analyzer_instrument_family_samples: shard index %d outside shard count %d\n",
			     shard_index, shard_count);
		return 1;
	}

	std::vector<SampleRow> rows;
	const std::string manifest_path = join_path(root, "manifest.tsv");
	if (!read_manifest(manifest_path, rows)) {
		if (required) {
			std::fprintf(stderr, "analyzer_instrument_family_samples: missing manifest %s\n",
				     manifest_path.c_str());
			return 1;
		}
		std::printf("analyzer_instrument_family_samples: skipped; no generated manifest at %s\n",
			    manifest_path.c_str());
		return 0;
	}

	Runner runner;
	runner.max_reported_failures = positive_int_env("MUSIC_ANALYZER_INSTRUMENT_FAMILY_MAX_FAILURE_LINES", 40);
	runner.expect(static_cast<int>(rows.size()) >= required_samples,
		      "expected at least " + std::to_string(required_samples) +
			      " real instrument-family samples, got " + std::to_string(rows.size()));

	std::array<FamilyStats, 4> stats = {};
	std::map<std::string, FamilyStats> instrument_stats;
	int usable = 0;
	int selected = 0;
	std::size_t row_ordinal = 0;
	for (const SampleRow &row : rows) {
		const std::size_t current_row_ordinal = row_ordinal++;
		if (shard_count > 1 &&
		    current_row_ordinal % static_cast<std::size_t>(shard_count) !=
			    static_cast<std::size_t>(shard_index))
			continue;
		if (sample_filter && *sample_filter && row.id != sample_filter)
			continue;
		++selected;

		std::vector<float> samples;
		uint32_t sample_rate = 0;
		std::string error;
		const std::string path = join_path(root, row.path);
		if (!read_wav_mono(path, samples, sample_rate, error)) {
			runner.expect(false, "failed to load " + row.id + ": " + error);
			continue;
		}

		const std::vector<mao_test::Buffer> buffers = make_sample_buffers(samples, sample_rate, 0.62f);
		if (buffers.empty()) {
			runner.expect(false, "failed to prepare " + row.id + ": empty or silent sample");
			continue;
		}

		bool detected = false;
		std::array<bool, 4> cross_seen = {};
		for (std::size_t buffer_index = 0; buffer_index < buffers.size(); ++buffer_index) {
			const mao_test::Buffer &buffer = buffers[buffer_index];
			const mao::AnalysisSnapshot snapshot = analyze_buffer(buffer, sample_rate);
			if (debug_sample_id && *debug_sample_id && row.id == debug_sample_id)
				print_full_mix_debug(row, buffer_index, snapshot);
			if (attribute_file)
				append_attribute_row(attribute_file, row, buffer_index, snapshot);
			for (int i = 0; i < 4; ++i) {
				if (family_detected(snapshot, family_name(i)))
					cross_seen[static_cast<std::size_t>(i)] = true;
			}
			if (family_detected(snapshot, row.family))
				detected = true;
		}

		const int index = family_index(row.family);
		++stats[static_cast<std::size_t>(index)].total;
		++instrument_stats[row.instrument].total;
		for (int i = 0; i < 4; ++i) {
			if (i != index && cross_seen[static_cast<std::size_t>(i)]) {
				++stats[static_cast<std::size_t>(index)].cross[static_cast<std::size_t>(i)];
				++instrument_stats[row.instrument].cross[static_cast<std::size_t>(i)];
			}
		}
		if (detected) {
			++stats[static_cast<std::size_t>(index)].hits;
			++instrument_stats[row.instrument].hits;
		}
		++usable;

		if (strict_sample_recall) {
			runner.expect(detected,
			      row.id + " " + row.instrument + "/" + row.subset +
				      ": expected " + row.family + " row activity in full-mix mode");
		}
	}
	runner.expect(selected > 0, "no manifest sample matched MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ID");

	for (int i = 0; i < 4; ++i) {
		const int total = stats[static_cast<std::size_t>(i)].total;
		if (total <= 0)
			continue;
		const int hits = stats[static_cast<std::size_t>(i)].hits;
		const int recall = hits * 100 / total;
		runner.expect(recall >= min_recall_percent,
			      std::string("expected at least ") + std::to_string(min_recall_percent) +
				      "% " + family_name(i) + " recall, got " + std::to_string(hits) +
				      "/" + std::to_string(total));
	}

	if (runner.failures) {
		std::fprintf(stderr,
			     "analyzer_instrument_family_samples: %d/%d checks failed (usable %d, guitar "
			     "%d/%d, piano %d/%d, vocals %d/%d, other %d/%d)\n",
			     runner.failures, runner.checks, usable, stats[0].hits, stats[0].total,
			     stats[1].hits, stats[1].total, stats[2].hits, stats[2].total,
			     stats[3].hits, stats[3].total);
		for (const auto &entry : instrument_stats) {
			std::fprintf(stderr, "  %s %d/%d\n", entry.first.c_str(), entry.second.hits,
				     entry.second.total);
		}
		return 1;
	}

	std::printf(
		"analyzer_instrument_family_samples: %d checks passed (usable %d, guitar %d/%d, piano "
		"%d/%d, vocals %d/%d, other %d/%d; cross rows guitar/piano/vocals/other ",
		runner.checks, usable, stats[0].hits, stats[0].total, stats[1].hits, stats[1].total,
		stats[2].hits, stats[2].total, stats[3].hits, stats[3].total);
	for (int expected = 0; expected < 4; ++expected) {
		if (expected > 0)
			std::printf("; ");
		std::printf("%s", family_name(expected));
		for (int got = 0; got < 4; ++got) {
			if (got == expected)
				continue;
			std::printf(" %s=%d", family_name(got),
				    stats[static_cast<std::size_t>(expected)].cross[static_cast<std::size_t>(got)]);
		}
	}
	std::printf(")\n");
	return 0;
}
