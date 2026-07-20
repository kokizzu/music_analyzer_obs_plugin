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
				std::fprintf(stderr, "further analyzer_real_note_samples failures suppressed\n");
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
	std::string nsynth_family;
	std::string source;
	int midi = 0;
	std::string note;
	std::string path;
};

struct SourceStats {
	int total = 0;
	int hits = 0;
	int any_hits = 0;
};

constexpr int kFamilyCount = 5;
constexpr int kObservedRowCount = 7;
constexpr int kObservedBass = 0;
constexpr int kObservedGuitar = 1;
constexpr int kObservedPiano = 2;
constexpr int kObservedVocals = 3;
constexpr int kObservedOther = 4;
constexpr int kObservedAmbiguous = 5;
constexpr int kObservedNone = 6;
static constexpr const char *kFamilyNames[kFamilyCount] = {"bass", "guitar", "piano", "vocals", "other"};
static constexpr const char *kObservedRowNames[kObservedRowCount] = {"bass", "guitar", "piano",
								    "vocals", "other", "amb", "none"};

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
		row.nsynth_family = fields[2];
		row.source = fields[3];
		row.midi = std::atoi(fields[4].c_str());
		row.note = fields[5];
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

	const float gain = std::min(24.0f, target_peak / window_peak);
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
	static constexpr double kOffsetsSeconds[] = {0.025, 0.080, 0.180, 0.320, 0.520, 0.820, 1.200};
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

bool grid_has_pitch_class(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return true;
	}
	return grid.cells[pitch_class].active;
}

float grid_pitch_class_level(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	float level = 0.0f;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max(level, row[pitch_class].level);
	}
	if (grid.cells[pitch_class].active)
		level = std::max(level, grid.cells[pitch_class].level);
	return level;
}

int strongest_pitch_class_row(const mao::AnalysisSnapshot &snapshot, int midi)
{
	std::array<float, kObservedRowCount> levels = {};
	levels[kObservedBass] = grid_pitch_class_level(snapshot.bass_notes, midi);
	levels[kObservedGuitar] = grid_pitch_class_level(snapshot.guitar_notes, midi);
	levels[kObservedPiano] = grid_pitch_class_level(snapshot.keyboard_notes, midi);
	levels[kObservedVocals] = grid_pitch_class_level(snapshot.vocal_notes, midi);
	levels[kObservedOther] = grid_pitch_class_level(snapshot.other_notes, midi);
	levels[kObservedAmbiguous] = grid_pitch_class_level(snapshot.ambiguous_notes, midi);

	int best = kObservedNone;
	float best_level = 0.0f;
	for (int i = 0; i < kObservedNone; ++i) {
		if (levels[static_cast<std::size_t>(i)] > best_level) {
			best = i;
			best_level = levels[static_cast<std::size_t>(i)];
		}
	}
	return best;
}

bool snapshot_has_pitch_class(const mao::AnalysisSnapshot &snapshot, int midi)
{
	return grid_has_pitch_class(snapshot.ambiguous_notes, midi) ||
	       grid_has_pitch_class(snapshot.bass_notes, midi) ||
	       grid_has_pitch_class(snapshot.keyboard_notes, midi) ||
	       grid_has_pitch_class(snapshot.guitar_notes, midi) ||
	       grid_has_pitch_class(snapshot.vocal_notes, midi) ||
	       grid_has_pitch_class(snapshot.other_notes, midi);
}

const mao::InstrumentState &family_state(const mao::AnalysisSnapshot &snapshot, const std::string &family)
{
	if (family == "bass")
		return snapshot.bass;
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
	if (family == "bass")
		return snapshot.bass_notes;
	if (family == "guitar")
		return snapshot.guitar_notes;
	if (family == "piano")
		return snapshot.keyboard_notes;
	if (family == "vocals")
		return snapshot.vocal_notes;
	return snapshot.other_notes;
}

std::string debug_note_label(int midi)
{
	if (midi < mao::kFirstAnalyzedMidi || midi > mao::kLastAnalyzedMidi)
		return "--";
	return mao_test::note_label(midi);
}

std::string grid_debug_label(const mao::NoteGrid &grid)
{
	std::string text;
	auto append_cell = [&](const mao::NoteCell &cell) {
		if (!cell.active || cell.midi < mao::kFirstAnalyzedMidi || cell.midi > mao::kLastAnalyzedMidi)
			return;
		char part[48] = {};
		std::snprintf(part, sizeof(part), "%s%s:%.2f", text.empty() ? "" : ",",
			      debug_note_label(cell.midi).c_str(), cell.level);
		text += part;
	};

	for (const mao::NoteCell &cell : grid.cells)
		append_cell(cell);
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row)
			append_cell(cell);
	}
	return text.empty() ? "--" : text;
}

std::string snapshot_note_debug_line(const mao::AnalysisSnapshot &snapshot)
{
	std::ostringstream line;
	line << "amb=" << grid_debug_label(snapshot.ambiguous_notes)
	     << " bass=" << snapshot.bass.label << "[" << grid_debug_label(snapshot.bass_notes) << "]"
	     << " keys=" << snapshot.keyboard.label << "[" << grid_debug_label(snapshot.keyboard_notes) << "]"
	     << " guitar=" << snapshot.guitar.label << "[" << grid_debug_label(snapshot.guitar_notes) << "]"
	     << " vocal=" << snapshot.vocal.label << "[" << grid_debug_label(snapshot.vocal_notes) << "]"
	     << " other=" << snapshot.other.label << "[" << grid_debug_label(snapshot.other_notes) << "]"
	     << " rms=" << snapshot.rms << " low=" << snapshot.low_energy << " mid=" << snapshot.mid_energy
	     << " high=" << snapshot.high_energy;
	return line.str();
}

const char *drum_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								"tom", "ride", "rim"};
	return index < mao::kDrumCount ? kNames[index] : "unknown";
}

std::string drum_debug_line(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
		char part[192] = {};
		std::snprintf(part, sizeof(part), "%s%s=%.2f%s score=%.2f thr=%.2f band=%.2f seg=%.2f",
			      text.empty() ? "" : " | ", drum_name(i), snapshot.drums[i].level,
			      snapshot.drums[i].active ? "*" : "",
			      snapshot.drum_debug_trigger_scores[i],
			      snapshot.drum_debug_trigger_thresholds[i], snapshot.drum_debug_bands[i],
			      snapshot.drum_debug_segment_bands[i]);
		text += part;
	}
	char part[256] = {};
	std::snprintf(part, sizeof(part),
		      " | rms=%.4f low=%.2f mid=%.2f high=%.2f transient=%.2f onset=%.2f body=%.2f/%.2f/%.2f crack=%.2f shape=%d",
		      snapshot.rms, snapshot.low_energy, snapshot.mid_energy, snapshot.high_energy,
		      snapshot.drum_debug_transient_ratio, snapshot.drum_debug_onset,
		      snapshot.drum_debug_kick_body, snapshot.drum_debug_snare_body,
		      snapshot.drum_debug_tom_body, snapshot.drum_debug_snare_crack,
		      snapshot.drum_debug_body_shape);
	text += part;
	return text;
}

mao::AnalysisInputMode family_mode(const std::string &family)
{
	if (family == "bass")
		return mao::AnalysisInputMode::IsolatedBass;
	if (family == "guitar")
		return mao::AnalysisInputMode::IsolatedGuitar;
	if (family == "piano")
		return mao::AnalysisInputMode::IsolatedKeyboard;
	if (family == "vocals")
		return mao::AnalysisInputMode::IsolatedVocal;
	return mao::AnalysisInputMode::IsolatedOther;
}

int family_index(const std::string &family)
{
	if (family == "bass")
		return kObservedBass;
	if (family == "guitar")
		return kObservedGuitar;
	if (family == "piano")
		return kObservedPiano;
	if (family == "vocals")
		return kObservedVocals;
	return kObservedOther;
}

std::string source_summary_key(const SampleRow &row)
{
	if (!row.source.empty())
		return row.family + "/" + row.source;
	if (!row.nsynth_family.empty())
		return row.family + "/" + row.nsynth_family;
	return row.family + "/unknown";
}

std::string source_summary_text(const std::map<std::string, SourceStats> &stats, int max_entries)
{
	struct Row {
		std::string source;
		int total = 0;
		int hits = 0;
		int misses = 0;
	};
	std::vector<Row> rows;
	for (const auto &entry : stats) {
		const int misses = entry.second.total - entry.second.hits;
		if (misses <= 0)
			continue;
		rows.push_back({entry.first, entry.second.total, entry.second.hits, misses});
	}
	std::sort(rows.begin(), rows.end(), [](const Row &lhs, const Row &rhs) {
		if (lhs.misses != rhs.misses)
			return lhs.misses > rhs.misses;
		if (lhs.total != rhs.total)
			return lhs.total > rhs.total;
		return lhs.source < rhs.source;
	});
	if (rows.empty())
		return "";

	std::string text = " source misses";
	const int count = std::min<int>(max_entries, static_cast<int>(rows.size()));
	for (int i = 0; i < count; ++i) {
		text += " ";
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

std::string source_any_summary_text(const std::map<std::string, SourceStats> &stats, int max_entries)
{
	struct Row {
		std::string source;
		int total = 0;
		int hits = 0;
		int misses = 0;
	};
	std::vector<Row> rows;
	for (const auto &entry : stats) {
		const int misses = entry.second.total - entry.second.any_hits;
		if (misses <= 0)
			continue;
		rows.push_back({entry.first, entry.second.total, entry.second.any_hits, misses});
	}
	std::sort(rows.begin(), rows.end(), [](const Row &lhs, const Row &rhs) {
		if (lhs.misses != rhs.misses)
			return lhs.misses > rhs.misses;
		if (lhs.total != rhs.total)
			return lhs.total > rhs.total;
		return lhs.source < rhs.source;
	});
	if (rows.empty())
		return "";

	std::string text = " source any-row misses";
	const int count = std::min<int>(max_entries, static_cast<int>(rows.size()));
	for (int i = 0; i < count; ++i) {
		text += " ";
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

void print_row_confusion(FILE *out,
			 const std::array<std::array<int, kObservedRowCount>, kFamilyCount> &row_confusion)
{
	std::fprintf(out, "analyzer_real_note_samples full-mix row-confusion:");
	for (int family = 0; family < kFamilyCount; ++family) {
		std::fprintf(out, " %s[", kFamilyNames[family]);
		for (int row = 0; row < kObservedRowCount; ++row) {
			std::fprintf(out, "%s%s=%d", row == 0 ? "" : ",", kObservedRowNames[row],
				     row_confusion[static_cast<std::size_t>(family)]
						  [static_cast<std::size_t>(row)]);
		}
		std::fprintf(out, "]");
	}
	std::fprintf(out, "\n");
}

mao::AnalysisSnapshot analyze_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate,
				     mao::AnalysisInputMode mode, const char *source, int frames = 4)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = kDefaultWindowSeconds;
	settings.input_mode = mode;

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < frames; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
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

} // namespace

int main()
{
	const char *root_env = std::getenv("MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT");
	const std::string root = root_env && *root_env ? root_env : "build/real_note_samples";
	const bool required = std::getenv("MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED") != nullptr;
	const bool verbose_misses = std::getenv("MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES") != nullptr;
	const bool verbose_drums = std::getenv("MUSIC_ANALYZER_REAL_NOTE_VERBOSE_DRUMS") != nullptr;
	const int required_samples = positive_int_env("MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES", 1000);
	const int max_failures = nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES", 0);
	const bool full_mix = std::getenv("MUSIC_ANALYZER_REAL_NOTE_FULL_MIX") != nullptr;
	const int min_any_hit_percent =
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT",
					       full_mix ? 80 : 0),
			   0, 100);
	const int min_expected_row_percent =
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT", 0),
			   0, 100);
	const std::array<int, kFamilyCount> min_family_expected_row_percent = {
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT", 0),
			   0, 100),
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT", 0),
			   0, 100),
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT", 0),
			   0, 100),
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT", 0),
			   0, 100),
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT", 0),
			   0, 100),
	};
	const int max_drum_active_percent =
		std::clamp(nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT",
					       full_mix ? 100 : 100),
			   0, 100);

	std::vector<SampleRow> rows;
	const std::string manifest_path = join_path(root, "manifest.tsv");
	if (!read_manifest(manifest_path, rows)) {
		if (required) {
			std::fprintf(stderr, "analyzer_real_note_samples: missing manifest %s\n",
				     manifest_path.c_str());
			return 1;
		}
		std::printf("analyzer_real_note_samples: skipped; no generated manifest at %s\n",
			    manifest_path.c_str());
		return 0;
	}

	Runner runner;
	runner.max_reported_failures = positive_int_env("MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES", 40);
	runner.expect(static_cast<int>(rows.size()) >= required_samples,
		      "expected at least " + std::to_string(required_samples) +
			      " real note samples, got " + std::to_string(rows.size()));

	std::array<int, kFamilyCount> family_counts = {};
	std::array<int, kFamilyCount> family_hits = {};
	std::array<int, kFamilyCount> family_any_hits = {};
	std::array<int, kFamilyCount> family_row_hits = {};
	std::array<std::array<int, kObservedRowCount>, kFamilyCount> row_confusion = {};
	std::map<std::string, SourceStats> source_stats;
	int any_hits = 0;
	int row_hits = 0;
	int active_drum_windows = 0;
	std::array<int, mao::kDrumCount> active_drum_by_class = {};
	int analyzed_windows = 0;
	int verbose_drum_lines = 0;
	const int verbose_drum_limit = positive_int_env("MUSIC_ANALYZER_REAL_NOTE_VERBOSE_DRUM_LIMIT", 24);
	int usable = 0;
	for (const SampleRow &row : rows) {
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

		const std::string expected = mao_test::note_label(row.midi);
		bool detected = false;
		bool detected_anywhere = false;
		bool detected_expected_row = false;
		int first_detected_row = kObservedNone;
		std::string last_label = "--";
		std::vector<std::string> debug_lines;
		int buffer_index = 0;
		const char *analysis_source =
			full_mix ? "Speaker Monitor" :
				   row.family == "bass" && !row.source.empty() ? row.source.c_str() :
										 row.family.c_str();
		for (const mao_test::Buffer &buffer : buffers) {
			const mao::AnalysisSnapshot snapshot =
				analyze_buffer(buffer, sample_rate,
					       full_mix ? mao::AnalysisInputMode::FullMix : family_mode(row.family),
					       analysis_source);
			last_label = family_state(snapshot, row.family).label;
			const bool label_ok = mao_test::has_note_token(family_state(snapshot, row.family).label,
								       expected.c_str()) ||
					      std::strcmp(family_state(snapshot, row.family).label,
							  expected.c_str()) == 0;
			const bool grid_ok = grid_has_pitch_class(family_grid(snapshot, row.family), row.midi);
			const bool any_grid_ok = snapshot_has_pitch_class(snapshot, row.midi);
			for (const mao::DrumState &drum : snapshot.drums) {
				if (drum.active) {
					++active_drum_windows;
					break;
				}
			}
			bool any_drum_active = false;
			for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
				if (snapshot.drums[i].active) {
					++active_drum_by_class[i];
					any_drum_active = true;
				}
			}
			if (full_mix && verbose_drums && any_drum_active && verbose_drum_lines < verbose_drum_limit) {
				std::fprintf(stderr, "%s %s/%s %s buffer %d false-drum: %s\n", row.id.c_str(),
					     row.family.c_str(), row.source.c_str(), expected.c_str(), buffer_index,
					     drum_debug_line(snapshot).c_str());
				++verbose_drum_lines;
			}
			++analyzed_windows;
			if (label_ok || grid_ok)
				detected_expected_row = true;
			if (any_grid_ok) {
				detected_anywhere = true;
				if (first_detected_row == kObservedNone)
					first_detected_row = strongest_pitch_class_row(snapshot, row.midi);
			}
			if ((!full_mix && (label_ok || grid_ok)) ||
			    (full_mix && detected_expected_row)) {
				detected = true;
				break;
			}
			if (full_mix && any_grid_ok)
				detected = true;
			if (verbose_misses) {
				std::ostringstream line;
				line << "  buffer " << buffer_index << " expected=" << expected
				     << " row_label=" << family_state(snapshot, row.family).label
				     << " row_conf=" << family_state(snapshot, row.family).confidence
				     << " row_grid=" << (grid_ok ? "yes" : "no")
				     << " any_grid=" << (any_grid_ok ? "yes" : "no") << " "
				     << snapshot_note_debug_line(snapshot);
				if (row.family == "bass") {
					line << " spectral=" << debug_note_label(snapshot.bass_debug_spectral_midi) << "/"
					     << snapshot.bass_debug_spectral_confidence << "/"
					     << snapshot.bass_debug_spectral_score
					     << " periodic=" << debug_note_label(snapshot.bass_debug_periodic_midi) << "/"
					     << snapshot.bass_debug_periodic_confidence << "/"
					     << snapshot.bass_debug_periodic_score
					     << " displayed=" << debug_note_label(snapshot.bass_debug_displayed_midi) << "/"
					     << snapshot.bass_debug_displayed_confidence << "/"
					     << snapshot.bass_debug_displayed_score;
				}
				debug_lines.push_back(line.str());
			}
			++buffer_index;
		}
		const bool ownership_miss = full_mix && detected_anywhere && !detected_expected_row;
		if ((!detected || ownership_miss) && verbose_misses) {
			for (const std::string &line : debug_lines)
				std::fprintf(stderr, "%s\n", line.c_str());
			if (ownership_miss) {
				std::fprintf(stderr,
					     "%s %s/%s %s: expected-row ownership missing first-row=%s row-label=`%s`\n",
					     row.id.c_str(), row.family.c_str(), row.source.c_str(),
					     expected.c_str(), kObservedRowNames[first_detected_row],
					     last_label.c_str());
			}
		}
		runner.expect(detected,
			      row.id + " " + row.nsynth_family + "/" + row.source + " " + expected +
				      ": expected detected note, got label `" + last_label + "`");
		++usable;

		const int index = family_index(row.family);
		++family_counts[index];
		SourceStats &source_stat = source_stats[source_summary_key(row)];
		++source_stat.total;
		if (detected) {
			++family_hits[index];
			++source_stat.hits;
		}
		if (detected_anywhere) {
			++family_any_hits[index];
			++source_stat.any_hits;
			++any_hits;
		}
		if (detected_expected_row) {
			++family_row_hits[index];
			++row_hits;
		}
		if (full_mix) {
			++row_confusion[static_cast<std::size_t>(index)]
					[static_cast<std::size_t>(first_detected_row)];
		}
	}

	const std::array<int, kFamilyCount> minimum_family_counts = {
		nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_BASS", 0),
		nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR", 0),
		nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO", 0),
		nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS", 0),
		nonnegative_int_env("MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER", 0),
	};
	for (std::size_t i = 0; i < minimum_family_counts.size(); ++i) {
		runner.expect(family_counts[i] >= minimum_family_counts[i],
			      std::string("expected at least ") + std::to_string(minimum_family_counts[i]) +
				      " " + kFamilyNames[i] + " real note samples, got " +
				      std::to_string(family_counts[i]));
	}
	if (full_mix && usable > 0) {
		const int any_hit_percent = any_hits * 100 / usable;
		runner.expect(any_hit_percent >= min_any_hit_percent,
			      "expected at least " + std::to_string(min_any_hit_percent) +
				      "% full-mix any-row note recall, got " + std::to_string(any_hits) +
				      "/" + std::to_string(usable));
		const int expected_row_percent = row_hits * 100 / usable;
		runner.expect(expected_row_percent >= min_expected_row_percent,
			      "expected at least " + std::to_string(min_expected_row_percent) +
				      "% full-mix expected-row note recall, got " +
				      std::to_string(row_hits) + "/" + std::to_string(usable));
		for (std::size_t i = 0; i < min_family_expected_row_percent.size(); ++i) {
			if (min_family_expected_row_percent[i] <= 0 || family_counts[i] <= 0)
				continue;
			const int family_expected_row_percent = family_row_hits[i] * 100 / family_counts[i];
			runner.expect(family_expected_row_percent >= min_family_expected_row_percent[i],
				      "expected at least " +
					      std::to_string(min_family_expected_row_percent[i]) +
					      "% full-mix " + kFamilyNames[i] +
					      " expected-row note recall, got " +
					      std::to_string(family_row_hits[i]) + "/" +
					      std::to_string(family_counts[i]));
		}
		if (analyzed_windows > 0) {
			const int drum_active_percent = active_drum_windows * 100 / analyzed_windows;
			runner.expect(drum_active_percent <= max_drum_active_percent,
				      "expected at most " + std::to_string(max_drum_active_percent) +
					      "% full-mix melodic drum-active windows, got " +
					      std::to_string(active_drum_windows) + "/" +
					      std::to_string(analyzed_windows));
		}
	}

	if (runner.failures) {
		const std::string source_summary = source_summary_text(source_stats, 12);
		if (!source_summary.empty())
			std::fprintf(stderr, "analyzer_real_note_samples:%s\n", source_summary.c_str());
		if (full_mix) {
			const std::string any_summary = source_any_summary_text(source_stats, 12);
			if (!any_summary.empty())
				std::fprintf(stderr, "analyzer_real_note_samples:%s\n", any_summary.c_str());
		}
		std::fprintf(stderr,
			     "analyzer_real_note_samples%s: %d/%d checks failed (usable %d, bass %d/%d, guitar "
			     "%d/%d, piano %d/%d, vocals %d/%d, other %d/%d",
			     full_mix ? " full-mix" : "",
			     runner.failures, runner.checks, usable, family_hits[0], family_counts[0],
			     family_hits[1], family_counts[1], family_hits[2], family_counts[2],
			     family_hits[3], family_counts[3], family_hits[4], family_counts[4]);
		if (full_mix) {
			std::fprintf(stderr,
				     "; any-row %d/%d, expected-row %d/%d, drum-active-windows %d/%d",
				     any_hits, usable, row_hits, usable, active_drum_windows, analyzed_windows);
			std::fprintf(stderr,
				     ", expected-row-by-family bass=%d/%d guitar=%d/%d piano=%d/%d vocals=%d/%d other=%d/%d",
				     family_row_hits[0], family_counts[0], family_row_hits[1],
				     family_counts[1], family_row_hits[2], family_counts[2],
				     family_row_hits[3], family_counts[3], family_row_hits[4],
				     family_counts[4]);
			std::fprintf(stderr,
				     ", drums kick=%d snare=%d hihat=%d crash=%d tom=%d ride=%d rim=%d",
				     active_drum_by_class[0], active_drum_by_class[1],
				     active_drum_by_class[2], active_drum_by_class[3],
				     active_drum_by_class[4], active_drum_by_class[5],
				     active_drum_by_class[6]);
		}
		std::fprintf(stderr, ")\n");
		if (full_mix)
			print_row_confusion(stderr, row_confusion);
		if (runner.failures > max_failures)
			return 1;
		std::printf(
			"analyzer_real_note_samples%s: %d tolerated failures within limit %d (usable %d, bass "
			"%d/%d, guitar %d/%d, piano %d/%d, vocals %d/%d, other %d/%d",
			full_mix ? " full-mix" : "",
			runner.failures, max_failures, usable, family_hits[0], family_counts[0],
			family_hits[1], family_counts[1], family_hits[2], family_counts[2],
			family_hits[3], family_counts[3], family_hits[4], family_counts[4]);
		if (full_mix) {
			std::printf("; any-row %d/%d, expected-row %d/%d, drum-active-windows %d/%d",
				    any_hits, usable, row_hits, usable, active_drum_windows, analyzed_windows);
			std::printf(
				", expected-row-by-family bass=%d/%d guitar=%d/%d piano=%d/%d vocals=%d/%d other=%d/%d",
				family_row_hits[0], family_counts[0], family_row_hits[1], family_counts[1],
				family_row_hits[2], family_counts[2], family_row_hits[3], family_counts[3],
				family_row_hits[4], family_counts[4]);
			std::printf(", drums kick=%d snare=%d hihat=%d crash=%d tom=%d ride=%d rim=%d",
				    active_drum_by_class[0], active_drum_by_class[1],
				    active_drum_by_class[2], active_drum_by_class[3],
				    active_drum_by_class[4], active_drum_by_class[5],
				    active_drum_by_class[6]);
		}
		std::printf(")\n");
		if (full_mix)
			print_row_confusion(stdout, row_confusion);
		return 0;
	}

	std::printf(
		"analyzer_real_note_samples%s: %d checks passed (usable %d, bass %d/%d, guitar %d/%d, piano "
		"%d/%d, vocals %d/%d, other %d/%d",
		full_mix ? " full-mix" : "",
		runner.checks, usable, family_hits[0], family_counts[0], family_hits[1], family_counts[1],
		family_hits[2], family_counts[2], family_hits[3], family_counts[3], family_hits[4],
		family_counts[4]);
	if (full_mix) {
		std::printf("; any-row %d/%d, expected-row %d/%d, drum-active-windows %d/%d",
			    any_hits, usable, row_hits, usable, active_drum_windows, analyzed_windows);
		std::printf(
			", expected-row-by-family bass=%d/%d guitar=%d/%d piano=%d/%d vocals=%d/%d other=%d/%d",
			family_row_hits[0], family_counts[0], family_row_hits[1], family_counts[1],
			family_row_hits[2], family_counts[2], family_row_hits[3], family_counts[3],
			family_row_hits[4], family_counts[4]);
		std::printf(", drums kick=%d snare=%d hihat=%d crash=%d tom=%d ride=%d rim=%d",
			    active_drum_by_class[0], active_drum_by_class[1], active_drum_by_class[2],
			    active_drum_by_class[3], active_drum_by_class[4], active_drum_by_class[5],
			    active_drum_by_class[6]);
	}
	std::printf(")\n");
	if (full_mix)
		print_row_confusion(stdout, row_confusion);
	return 0;
}
