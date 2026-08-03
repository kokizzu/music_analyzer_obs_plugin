#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cctype>
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
#include <sys/stat.h>
#include <vector>

namespace {

struct Runner {
	int checks = 0;
	int failures = 0;
	int reported_failures = 0;
	int max_reported_failures = 80;

	void expect(bool ok, const std::string &message)
	{
		++checks;
		if (!ok) {
			++failures;
			if (reported_failures < max_reported_failures) {
				std::fprintf(stderr, "%s\n", message.c_str());
			} else if (reported_failures == max_reported_failures) {
				std::fprintf(stderr, "further analyzer_guitarset failures suppressed\n");
			}
			++reported_failures;
		}
	}
};

bool file_exists(const std::string &path)
{
	struct stat st = {};
	return ::stat(path.c_str(), &st) == 0 && S_ISREG(st.st_mode);
}

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

bool read_wav_window(const std::string &path, uint64_t center_sample, mao_test::Buffer &buffer,
		     uint32_t &sample_rate, std::string &error)
{
	WavFormat format;
	if (!read_wav_format(path, format, error))
		return false;

	const uint16_t bytes_per_sample = static_cast<uint16_t>(format.bits_per_sample / 8);
	if (bytes_per_sample == 0 || format.block_align < bytes_per_sample * format.channels) {
		error = "invalid block alignment";
		return false;
	}
	if (format.frame_count < buffer.size()) {
		error = "audio shorter than analyzer window";
		return false;
	}

	int64_t start_frame = static_cast<int64_t>(center_sample) - static_cast<int64_t>(buffer.size() / 2);
	start_frame = std::max<int64_t>(0, start_frame);
	if (static_cast<uint64_t>(start_frame) + buffer.size() > format.frame_count)
		start_frame = static_cast<int64_t>(format.frame_count - buffer.size());

	std::ifstream file(path, std::ios::binary);
	if (!file) {
		error = "open failed";
		return false;
	}
	file.seekg(static_cast<std::streamoff>(format.data_offset + static_cast<uint64_t>(start_frame) *
							       format.block_align));

	std::vector<unsigned char> bytes(static_cast<std::size_t>(format.block_align) * buffer.size());
	file.read(reinterpret_cast<char *>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
	if (file.gcount() != static_cast<std::streamsize>(bytes.size())) {
		error = "short read";
		return false;
	}

	for (std::size_t frame = 0; frame < buffer.size(); ++frame) {
		const unsigned char *frame_bytes = bytes.data() + frame * format.block_align;
		float sum = 0.0f;
		for (uint16_t channel = 0; channel < format.channels; ++channel)
			sum += decode_pcm_sample(frame_bytes + channel * bytes_per_sample, format.bits_per_sample,
						 format.audio_format);
		buffer[frame] = sum / static_cast<float>(format.channels);
	}

	sample_rate = format.sample_rate;
	return true;
}

std::vector<std::string> split_tab(const std::string &line)
{
	std::vector<std::string> fields;
	std::string field;
	for (char ch : line) {
		if (ch == '\t') {
			fields.push_back(field);
			field.clear();
		} else {
			field.push_back(ch);
		}
	}
	fields.push_back(field);
	return fields;
}

int resolve_positive_int_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;

	const int parsed = std::atoi(value);
	return parsed > 0 ? parsed : fallback;
}

int resolve_nonnegative_int_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;

	const int parsed = std::atoi(value);
	return parsed >= 0 ? parsed : fallback;
}

int resolve_percent_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;

	const int parsed = std::atoi(value);
	return parsed >= 0 && parsed <= 100 ? parsed : fallback;
}

bool env_truthy(const char *name)
{
	const char *value = std::getenv(name);
	return value && *value && std::strcmp(value, "0") != 0 && std::strcmp(value, "false") != 0 &&
	       std::strcmp(value, "FALSE") != 0;
}

struct NoteAnnotation {
	double start_seconds = 0.0;
	double end_seconds = 0.0;
	int midi = 0;
};

struct Recording {
	std::string id;
	std::string audio_path;
	std::vector<NoteAnnotation> notes;
};

bool read_manifest(const std::string &path, std::vector<Recording> &recordings, std::string &error)
{
	std::ifstream file(path);
	if (!file) {
		error = "open failed";
		return false;
	}

	std::map<std::string, Recording> by_id;
	std::string line;
	while (std::getline(file, line)) {
		if (line.empty() || line[0] == '#')
			continue;
		const std::vector<std::string> fields = split_tab(line);
		if (fields.empty())
			continue;

		if (fields[0] == "AUDIO" && fields.size() >= 3) {
			Recording &recording = by_id[fields[1]];
			recording.id = fields[1];
			recording.audio_path = fields[2];
		} else if (fields[0] == "NOTE" && fields.size() >= 5) {
			Recording &recording = by_id[fields[1]];
			recording.id = fields[1];
			NoteAnnotation note;
			note.start_seconds = std::atof(fields[2].c_str());
			note.end_seconds = std::atof(fields[3].c_str());
			note.midi = std::atoi(fields[4].c_str());
			if (note.end_seconds > note.start_seconds && note.midi > 0)
				recording.notes.push_back(note);
		}
	}

	for (auto &item : by_id) {
		Recording &recording = item.second;
		if (recording.audio_path.empty() || recording.notes.empty())
			continue;
		std::sort(recording.notes.begin(), recording.notes.end(),
			  [](const NoteAnnotation &a, const NoteAnnotation &b) {
				  if (a.start_seconds != b.start_seconds)
					  return a.start_seconds < b.start_seconds;
				  return a.midi < b.midi;
			  });
		recordings.push_back(recording);
	}

	std::sort(recordings.begin(), recordings.end(), [](const Recording &a, const Recording &b) {
		return a.id < b.id;
	});
	return true;
}

bool has_pitch_class(const std::array<bool, 12> &pitch_classes, int pitch_class)
{
	return pitch_classes[((pitch_class % 12) + 12) % 12];
}

int pitch_class_count(const std::array<bool, 12> &pitch_classes)
{
	int count = 0;
	for (bool active : pitch_classes) {
		if (active)
			++count;
	}
	return count;
}

bool grid_has_pitch_class(const mao::NoteGrid &grid, int pitch_class)
{
	if (grid.cells[pitch_class].active)
		return true;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return true;
	}
	return false;
}

void add_detected_pitch_classes(const mao::NoteGrid &grid, std::array<bool, 12> &pitch_classes)
{
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (grid_has_pitch_class(grid, pitch_class))
			pitch_classes[pitch_class] = true;
	}
}

std::array<bool, 12> detected_pitch_classes(const mao::AnalysisSnapshot &snapshot)
{
	std::array<bool, 12> pitch_classes = {};
	add_detected_pitch_classes(snapshot.bass_notes, pitch_classes);
	add_detected_pitch_classes(snapshot.keyboard_notes, pitch_classes);
	add_detected_pitch_classes(snapshot.guitar_notes, pitch_classes);
	add_detected_pitch_classes(snapshot.vocal_notes, pitch_classes);
	add_detected_pitch_classes(snapshot.other_notes, pitch_classes);
	add_detected_pitch_classes(snapshot.ambiguous_notes, pitch_classes);
	return pitch_classes;
}

bool has_chord_label(const char *actual, const std::string &expected)
{
	if (!actual)
		return false;
	const char *cursor = actual;
	while (*cursor) {
		const char *end = cursor;
		while (*end && *end != '=')
			++end;
		if (static_cast<std::size_t>(end - cursor) == expected.size() &&
		    std::strncmp(cursor, expected.c_str(), expected.size()) == 0)
			return true;
		cursor = *end == '=' ? end + 1 : end;
	}
	return false;
}

bool snapshot_has_chord_label(const mao::AnalysisSnapshot &snapshot, const std::string &label)
{
	return has_chord_label(snapshot.global_chord.label, label) ||
	       has_chord_label(snapshot.keyboard_chord.label, label) ||
	       has_chord_label(snapshot.guitar_chord.label, label) || has_chord_label(snapshot.other_chord.label, label);
}

std::string chord_root(const std::string &label)
{
	if (label.empty())
		return "";
	std::size_t suffix = 1;
	if (suffix < label.size() && label[suffix] == '#')
		++suffix;
	return label.substr(0, suffix);
}

std::string chord_quality(const std::string &label)
{
	if (label.empty())
		return "";
	std::size_t suffix = 1;
	if (suffix < label.size() && label[suffix] == '#')
		++suffix;
	return label.substr(suffix);
}

std::string simplified_chord_label(const std::string &label)
{
	const std::string root = chord_root(label);
	const std::string quality = chord_quality(label);
	if (root.empty())
		return label;
	if (quality.empty() || quality == "6" || quality == "7" || quality == "9" || quality == "add9" ||
	    quality == "maj7" || quality == "maj9")
		return root;
	if (quality == "m" || quality == "m6" || quality == "m7" || quality == "m9")
		return root + "m";
	return label;
}

struct ChordTemplate {
	const char *suffix = "";
	std::vector<int> intervals;
};

const std::vector<ChordTemplate> &common_chord_templates()
{
	static const std::vector<ChordTemplate> kTemplates = {
		{"9", {0, 2, 4, 7, 10}},   {"maj9", {0, 2, 4, 7, 11}},
		{"m9", {0, 2, 3, 7, 10}},  {"dim7", {0, 3, 6, 9}},
		{"m7b5", {0, 3, 6, 10}},   {"7", {0, 4, 7, 10}},
		{"maj7", {0, 4, 7, 11}},   {"m7", {0, 3, 7, 10}},
		{"6", {0, 4, 7, 9}},       {"m6", {0, 3, 7, 9}},
		{"add9", {0, 2, 4, 7}},    {"", {0, 4, 7}},
		{"m", {0, 3, 7}},          {"dim", {0, 3, 6}},
		{"aug", {0, 4, 8}},        {"sus2", {0, 2, 7}},
		{"sus4", {0, 5, 7}},       {"pow", {0, 7}},
	};
	return kTemplates;
}

bool template_matches_pitch_classes(const std::array<bool, 12> &pitch_classes, int root,
				    const ChordTemplate &chord_template)
{
	for (int interval : chord_template.intervals) {
		if (!has_pitch_class(pitch_classes, root + interval))
			return false;
	}

	if (std::strcmp(chord_template.suffix, "pow") == 0) {
		static constexpr int kNonPowerIntervals[] = {2, 3, 4, 5, 6, 8, 9, 10, 11};
		for (int interval : kNonPowerIntervals) {
			if (has_pitch_class(pitch_classes, root + interval))
				return false;
		}
	}

	return true;
}

std::vector<std::string> expected_common_chord_labels(const std::array<bool, 12> &pitch_classes,
						      int &best_tone_count)
{
	std::vector<std::string> labels;
	best_tone_count = 0;

	for (int root = 0; root < 12; ++root) {
		if (!has_pitch_class(pitch_classes, root))
			continue;
		for (const ChordTemplate &chord_template : common_chord_templates()) {
			if (!template_matches_pitch_classes(pitch_classes, root, chord_template))
				continue;
			const int tone_count = static_cast<int>(chord_template.intervals.size());
			if (tone_count < best_tone_count)
				continue;
			const std::string label = std::string(mao_test::note_name(root)) + chord_template.suffix;
			if (tone_count > best_tone_count) {
				best_tone_count = tone_count;
				labels.clear();
			}
			if (std::find(labels.begin(), labels.end(), label) == labels.end())
				labels.push_back(label);
		}
	}

	return labels;
}

std::string join_labels(const std::vector<std::string> &labels)
{
	std::string joined;
	for (const std::string &label : labels) {
		if (!joined.empty())
			joined += "/";
		joined += label;
	}
	return joined;
}

struct CandidateWindow {
	uint64_t center_sample = 0;
	double center_seconds = 0.0;
	std::vector<int> active_midis;
	std::array<bool, 12> pitch_classes = {};
	std::vector<std::string> chord_labels;
	int chord_tone_count = 0;
	double score = 0.0;
};

CandidateWindow candidate_window_at(const Recording &recording, double time_seconds, uint32_t sample_rate)
{
	CandidateWindow candidate;
	candidate.center_seconds = time_seconds;
	candidate.center_sample = static_cast<uint64_t>(std::llround(time_seconds * sample_rate));

	for (const NoteAnnotation &note : recording.notes) {
		const double duration = note.end_seconds - note.start_seconds;
		const double edge = std::min(0.035, duration / 5.0);
		const double start = note.start_seconds + edge;
		const double end = note.end_seconds - edge;
		if (time_seconds < start || time_seconds > end)
			continue;
		candidate.active_midis.push_back(note.midi);
		candidate.pitch_classes[((note.midi % 12) + 12) % 12] = true;
	}

	if (candidate.active_midis.size() < 2)
		return candidate;

	candidate.chord_labels = expected_common_chord_labels(candidate.pitch_classes, candidate.chord_tone_count);
	candidate.score = static_cast<double>(candidate.active_midis.size()) * 100.0 +
			  static_cast<double>(pitch_class_count(candidate.pitch_classes)) * 30.0 +
			  static_cast<double>(candidate.chord_tone_count) * 30.0 +
			  (candidate.chord_labels.empty() ? 0.0 : 60.0);
	return candidate;
}

std::vector<CandidateWindow> select_candidate_windows(const Recording &recording, uint32_t sample_rate,
						      int max_windows, int min_active_notes,
						      int min_pitch_classes)
{
	std::vector<CandidateWindow> candidates;
	for (const NoteAnnotation &note : recording.notes) {
		const double center = note.start_seconds + (note.end_seconds - note.start_seconds) * 0.5;
		CandidateWindow candidate = candidate_window_at(recording, center, sample_rate);
		if (static_cast<int>(candidate.active_midis.size()) < min_active_notes)
			continue;
		if (pitch_class_count(candidate.pitch_classes) < min_pitch_classes)
			continue;
		candidates.push_back(candidate);
	}

	std::sort(candidates.begin(), candidates.end(), [](const CandidateWindow &a, const CandidateWindow &b) {
		if (a.score != b.score)
			return a.score > b.score;
		return a.center_sample < b.center_sample;
	});

	std::vector<CandidateWindow> selected;
	for (const CandidateWindow &candidate : candidates) {
		bool duplicate = false;
		for (const CandidateWindow &existing : selected) {
			const uint64_t distance = candidate.center_sample > existing.center_sample
							  ? candidate.center_sample - existing.center_sample
							  : existing.center_sample - candidate.center_sample;
			if (distance < static_cast<uint64_t>(sample_rate / 5)) {
				duplicate = true;
				break;
			}
		}
		if (duplicate)
			continue;
		selected.push_back(candidate);
		if (static_cast<int>(selected.size()) >= max_windows)
			break;
	}

	std::sort(selected.begin(), selected.end(), [](const CandidateWindow &a, const CandidateWindow &b) {
		return a.center_sample < b.center_sample;
	});
	return selected;
}

mao::AnalysisSnapshot analyze_confirmed_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;
	settings.input_mode = mao::AnalysisInputMode::IsolatedGuitar;

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "GuitarSet guitar", 0);
	return snapshot;
}

struct RecallStats {
	int hits = 0;
	int expected = 0;
	int chord_hits = 0;
	int chord_checks = 0;
	int simple_chord_hits = 0;
	int major_minor_chord_hits = 0;
	int major_minor_chord_checks = 0;
	int simple_major_minor_chord_hits = 0;
	int other_chord_hits = 0;
	int other_chord_checks = 0;
	int simple_other_chord_hits = 0;
	struct ChordQualityStats {
		int hits = 0;
		int simple_hits = 0;
		int checks = 0;
	};
	std::map<std::string, ChordQualityStats> chord_quality;
};

std::array<bool, 12> grid_pitch_classes(const mao::NoteGrid &grid)
{
	std::array<bool, 12> pitch_classes = {};
	add_detected_pitch_classes(grid, pitch_classes);
	return pitch_classes;
}

std::string pitch_class_list(const std::array<bool, 12> &pitch_classes)
{
	std::string text;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!pitch_classes[pitch_class])
			continue;
		if (!text.empty())
			text += ",";
		text += mao_test::note_name(pitch_class);
	}
	return text.empty() ? "--" : text;
}

std::string grid_cell_list(const mao::NoteGrid &grid)
{
	std::string text;
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0)
				continue;
			char item[32] = {};
			std::snprintf(item, sizeof(item), "%s%d:%.2f", mao_test::note_name(cell.midi % 12),
				      cell.midi / 12 - 1, cell.level);
			if (!text.empty())
				text += ",";
			text += item;
		}
	}
	return text.empty() ? "--" : text;
}

float raw_goertzel_magnitude(const mao_test::Buffer &buffer, uint32_t sample_rate, int midi)
{
	if (sample_rate == 0 || buffer.size() < 2)
		return 0.0f;

	double sum = 0.0;
	for (float sample : buffer)
		sum += sample;
	const float mean = static_cast<float>(sum / static_cast<double>(buffer.size()));
	const float frequency = mao_test::midi_frequency(midi);
	const float coeff = 2.0f * std::cos(2.0f * mao_test::kPi * frequency / static_cast<float>(sample_rate));

	float s1 = 0.0f;
	float s2 = 0.0f;
	for (std::size_t i = 0; i < buffer.size(); ++i) {
		const float phase =
			2.0f * mao_test::kPi * static_cast<float>(i) / static_cast<float>(buffer.size() - 1);
		const float window = 0.5f - 0.5f * std::cos(phase);
		const float x = (buffer[i] - mean) * window;
		const float s0 = x + coeff * s1 - s2;
		s2 = s1;
		s1 = s0;
	}

	return std::sqrt(std::max(0.0f, s1 * s1 + s2 * s2 - coeff * s1 * s2));
}

float strongest_expected_raw_magnitude(const CandidateWindow &candidate, const mao_test::Buffer &buffer,
				       uint32_t sample_rate)
{
	float strongest = 0.0f;
	for (int midi : candidate.active_midis)
		strongest = std::max(strongest, raw_goertzel_magnitude(buffer, sample_rate, midi));
	return strongest;
}

std::string expected_raw_cell_list(const CandidateWindow &candidate, const mao_test::Buffer &buffer,
				   uint32_t sample_rate, float strongest)
{
	if (strongest <= 1.0e-9f)
		return "--";

	std::vector<int> midis = candidate.active_midis;
	std::sort(midis.begin(), midis.end());
	midis.erase(std::unique(midis.begin(), midis.end()), midis.end());

	std::string text;
	for (int midi : midis) {
		const float level =
			std::clamp(raw_goertzel_magnitude(buffer, sample_rate, midi) / strongest, 0.0f, 1.0f);
		char item[32] = {};
		std::snprintf(item, sizeof(item), "%s%d:%.3f", mao_test::note_name(midi % 12),
			      midi / 12 - 1, level);
		if (!text.empty())
			text += ",";
		text += item;
	}
	return text.empty() ? "--" : text;
}

std::array<float, 12> raw_pitch_class_profile(const mao_test::Buffer &buffer, uint32_t sample_rate,
					      int min_midi, int max_midi)
{
	std::array<float, 12> profile = {};
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const int pitch_class = ((midi % 12) + 12) % 12;
		profile[pitch_class] =
			std::max(profile[pitch_class], raw_goertzel_magnitude(buffer, sample_rate, midi));
	}
	return profile;
}

std::string raw_pitch_class_level_list(const std::array<float, 12> &profile)
{
	const float strongest = *std::max_element(profile.begin(), profile.end());
	if (strongest <= 1.0e-9f)
		return "--";

	std::string text;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		const float level = std::clamp(profile[pitch_class] / strongest, 0.0f, 1.0f);
		char item[32] = {};
		std::snprintf(item, sizeof(item), "%s:%.3f", mao_test::note_name(pitch_class), level);
		if (!text.empty())
			text += ",";
		text += item;
	}
	return text;
}

int root_from_chord_label(const std::string &label)
{
	if (label.empty())
		return -1;

	for (int preferred_len : {2, 1}) {
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			const char *name = mao_test::note_name(pitch_class);
			const std::size_t len = std::strlen(name);
			if (len != static_cast<std::size_t>(preferred_len))
				continue;
			if (label.size() >= len && label.compare(0, len, name) == 0)
				return pitch_class;
		}
	}
	return -1;
}

float normalized_raw_pitch_class_level(const std::array<float, 12> &profile, int pitch_class)
{
	const float strongest = *std::max_element(profile.begin(), profile.end());
	if (strongest <= 1.0e-9f)
		return 0.0f;
	pitch_class = ((pitch_class % 12) + 12) % 12;
	return std::clamp(profile[pitch_class] / strongest, 0.0f, 1.0f);
}

std::string expected_quality_raw_profile(const CandidateWindow &candidate,
					 const std::array<float, 12> &raw_profile)
{
	if (candidate.chord_labels.empty())
		return "--";

	std::string text;
	for (const std::string &label : candidate.chord_labels) {
		const int root = root_from_chord_label(label);
		if (root < 0)
			continue;
		const float root_level = normalized_raw_pitch_class_level(raw_profile, root);
		const float minor_third = normalized_raw_pitch_class_level(raw_profile, root + 3);
		const float major_third = normalized_raw_pitch_class_level(raw_profile, root + 4);
		const float fifth = normalized_raw_pitch_class_level(raw_profile, root + 7);
		char item[96] = {};
		std::snprintf(item, sizeof(item), "%s:r%.3f,m3%.3f,M3%.3f,5%.3f", label.c_str(),
			      root_level, minor_third, major_third, fifth);
		if (!text.empty())
			text += ";";
		text += item;
	}
	return text.empty() ? "--" : text;
}

bool grid_has_any_active_pitch_class(const mao::NoteGrid &grid)
{
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (grid_has_pitch_class(grid, pitch_class))
			return true;
	}
	return false;
}

struct GuitarPrecisionStats {
	int windows = 0;
	int expected_pitch_classes = 0;
	int true_positives = 0;
	int false_positives = 0;
	int false_negatives = 0;
	int contaminated_pitch_classes = 0;
	int bass_contamination = 0;
	int keyboard_contamination = 0;
	int vocal_contamination = 0;
	int other_contamination = 0;
	int ambiguous_pitch_classes = 0;
	int false_vocal_windows = 0;
};

struct ChordPrecisionStats {
	int expected_windows = 0;
	int predicted_windows = 0;
	int true_positives = 0;
	int false_positives = 0;
	int false_negatives = 0;
};

std::vector<std::string> split_chord_labels(const char *label)
{
	std::vector<std::string> labels;
	if (!label || !*label || std::strcmp(label, "--") == 0)
		return labels;

	const char *cursor = label;
	while (*cursor) {
		const char *end = cursor;
		while (*end && *end != '=')
			++end;
		if (end > cursor) {
			const std::string component(cursor, static_cast<std::size_t>(end - cursor));
			if (component != "--")
				labels.push_back(component);
		}
		cursor = *end == '=' ? end + 1 : end;
	}

	return labels;
}

std::vector<std::string> snapshot_chord_labels(const mao::AnalysisSnapshot &snapshot)
{
	std::vector<std::string> labels;
	for (const char *label : {snapshot.global_chord.label, snapshot.keyboard_chord.label,
				  snapshot.guitar_chord.label, snapshot.other_chord.label}) {
		std::vector<std::string> part = split_chord_labels(label);
		labels.insert(labels.end(), part.begin(), part.end());
	}
	return labels;
}

bool snapshot_has_simplified_chord_label(const mao::AnalysisSnapshot &snapshot, const std::string &label)
{
	const std::string expected = simplified_chord_label(label);
	for (const std::string &actual : snapshot_chord_labels(snapshot)) {
		if (simplified_chord_label(actual) == expected)
			return true;
	}
	return false;
}

void add_guitar_precision_metrics(GuitarPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
				  const CandidateWindow &candidate)
{
	++stats.windows;
	const std::array<bool, 12> guitar = grid_pitch_classes(snapshot.guitar_notes);
	const std::array<bool, 12> bass = grid_pitch_classes(snapshot.bass_notes);
	const std::array<bool, 12> keyboard = grid_pitch_classes(snapshot.keyboard_notes);
	const std::array<bool, 12> vocal = grid_pitch_classes(snapshot.vocal_notes);
	const std::array<bool, 12> other = grid_pitch_classes(snapshot.other_notes);
	const std::array<bool, 12> ambiguous = grid_pitch_classes(snapshot.ambiguous_notes);

	if (grid_has_any_active_pitch_class(snapshot.vocal_notes))
		++stats.false_vocal_windows;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		const bool expected = candidate.pitch_classes[pitch_class];
		if (expected) {
			++stats.expected_pitch_classes;
			if (guitar[pitch_class])
				++stats.true_positives;
			else
				++stats.false_negatives;

			bool contaminated = false;
			if (bass[pitch_class]) {
				++stats.bass_contamination;
				contaminated = true;
			}
			if (keyboard[pitch_class]) {
				++stats.keyboard_contamination;
				contaminated = true;
			}
			if (vocal[pitch_class]) {
				++stats.vocal_contamination;
				contaminated = true;
			}
			if (other[pitch_class]) {
				++stats.other_contamination;
				contaminated = true;
			}
			if (contaminated)
				++stats.contaminated_pitch_classes;
			if (ambiguous[pitch_class])
				++stats.ambiguous_pitch_classes;
		} else if (guitar[pitch_class]) {
			++stats.false_positives;
		}
	}
}

void debug_guitar_window(const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate,
			 const std::string &context)
{
	if (!env_truthy("MUSIC_ANALYZER_GUITARSET_DEBUG_WINDOWS"))
		return;

	const std::array<bool, 12> guitar = grid_pitch_classes(snapshot.guitar_notes);
	const std::array<bool, 12> guitar_analysis = grid_pitch_classes(snapshot.guitar_chord_analysis_notes);
	const std::array<bool, 12> guitar_smoothed = grid_pitch_classes(snapshot.guitar_chord_smoothed_notes);
	std::fprintf(stderr,
		     "%s: expected pc `%s`, guitar pc `%s`, guitar cells `%s`, global `%s`, key `%s`, "
		     "guitar `%s`, other `%s`, guitar analysis pc `%s`, guitar analysis cells `%s`, "
		     "guitar smooth pc `%s`, guitar smooth cells `%s`\n",
		     context.c_str(), pitch_class_list(candidate.pitch_classes).c_str(),
		     pitch_class_list(guitar).c_str(), grid_cell_list(snapshot.guitar_notes).c_str(),
		     snapshot.global_chord.label, snapshot.keyboard_chord.label, snapshot.guitar_chord.label,
		     snapshot.other_chord.label, pitch_class_list(guitar_analysis).c_str(),
		     grid_cell_list(snapshot.guitar_chord_analysis_notes).c_str(),
		     pitch_class_list(guitar_smoothed).c_str(),
		     grid_cell_list(snapshot.guitar_chord_smoothed_notes).c_str());
}

void add_guitar_chord_precision_metrics(ChordPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
					const CandidateWindow &candidate)
{
	const bool expected = !candidate.chord_labels.empty();
	const std::vector<std::string> predicted = split_chord_labels(snapshot.guitar_chord.label);
	const bool predicted_any = !predicted.empty();
	bool matched = false;
	for (const std::string &label : predicted) {
		if (std::find(candidate.chord_labels.begin(), candidate.chord_labels.end(), label) !=
		    candidate.chord_labels.end()) {
			matched = true;
			break;
		}
	}

	if (expected)
		++stats.expected_windows;
	if (predicted_any)
		++stats.predicted_windows;
	if (matched) {
		++stats.true_positives;
		return;
	}
	if (predicted_any)
		++stats.false_positives;
	if (expected)
		++stats.false_negatives;
}

int percentage_floor(int numerator, int denominator)
{
	return denominator > 0 ? numerator * 100 / denominator : 0;
}

std::string percent_string(int numerator, int denominator)
{
	char buffer[32] = {};
	std::snprintf(buffer, sizeof(buffer), "%.2f%%",
		      denominator > 0 ? static_cast<double>(numerator) * 100.0 / static_cast<double>(denominator) :
				       0.0);
	return buffer;
}

std::string f1_string(int true_positives, int false_positives, int false_negatives)
{
	const int denominator = 2 * true_positives + false_positives + false_negatives;
	char buffer[32] = {};
	std::snprintf(buffer, sizeof(buffer), "%.2f%%",
		      denominator > 0 ?
			      static_cast<double>(2 * true_positives) * 100.0 / static_cast<double>(denominator) :
			      0.0);
	return buffer;
}

std::string guitar_precision_summary(const GuitarPrecisionStats &stats)
{
	return "guitar precision " + percent_string(stats.true_positives,
						    stats.true_positives + stats.false_positives) +
	       ", guitar recall " + percent_string(stats.true_positives,
						    stats.true_positives + stats.false_negatives) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", contamination " + percent_string(stats.contaminated_pitch_classes, stats.expected_pitch_classes) +
	       ", false vocal windows " + percent_string(stats.false_vocal_windows, stats.windows) +
	       ", ambiguous " + std::to_string(stats.ambiguous_pitch_classes) + "/" +
	       std::to_string(stats.expected_pitch_classes) + ", row leaks bass/keys/vocal/other " +
	       std::to_string(stats.bass_contamination) + "/" + std::to_string(stats.keyboard_contamination) +
	       "/" + std::to_string(stats.vocal_contamination) + "/" +
	       std::to_string(stats.other_contamination) + ", tp/fp/fn " +
	       std::to_string(stats.true_positives) + "/" + std::to_string(stats.false_positives) + "/" +
	       std::to_string(stats.false_negatives);
}

std::string chord_precision_summary(const ChordPrecisionStats &stats)
{
	return "guitar chord precision " + percent_string(stats.true_positives, stats.predicted_windows) +
	       ", guitar chord recall " + percent_string(stats.true_positives, stats.expected_windows) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", tp/fp/fn " + std::to_string(stats.true_positives) + "/" +
	       std::to_string(stats.false_positives) + "/" + std::to_string(stats.false_negatives);
}

bool chord_label_is_plain_major_or_minor(const std::string &label)
{
	if (label.empty())
		return false;
	const char root = label[0];
	if (root < 'A' || root > 'G')
		return false;
	std::size_t suffix = 1;
	if (suffix < label.size() && label[suffix] == '#')
		++suffix;
	const std::string quality = label.substr(suffix);
	return quality.empty() || quality == "m";
}

std::string chord_quality_name(const std::string &label)
{
	if (label.empty())
		return "unknown";
	const std::string quality = chord_quality(label);
	if (quality.empty())
		return "maj";
	if (quality == "m")
		return "min";
	return quality;
}

std::string chord_quality_summary(const RecallStats &stats)
{
	if (stats.chord_quality.empty())
		return "chord quality hits none";

	std::string text = "chord quality hits";
	for (const auto &entry : stats.chord_quality) {
		text += " ";
		text += entry.first;
		text += " ";
		text += std::to_string(entry.second.hits);
		text += "/";
		text += std::to_string(entry.second.checks);
		text += " ";
		text += percent_string(entry.second.hits, entry.second.checks);
		if (entry.second.simple_hits != entry.second.hits) {
			text += " simple ";
			text += std::to_string(entry.second.simple_hits);
			text += "/";
			text += std::to_string(entry.second.checks);
			text += " ";
			text += percent_string(entry.second.simple_hits, entry.second.checks);
		}
	}
	return text;
}

std::string simplified_chord_summary(const RecallStats &stats)
{
	return "simple chord hits " + std::to_string(stats.simple_chord_hits) + "/" +
	       std::to_string(stats.chord_checks) + " " +
	       percent_string(stats.simple_chord_hits, stats.chord_checks) + ", simple major/minor hits " +
	       std::to_string(stats.simple_major_minor_chord_hits) + "/" +
	       std::to_string(stats.major_minor_chord_checks) + " " +
	       percent_string(stats.simple_major_minor_chord_hits, stats.major_minor_chord_checks) +
	       ", simple other hits " + std::to_string(stats.simple_other_chord_hits) + "/" +
	       std::to_string(stats.other_chord_checks) + " " +
	       percent_string(stats.simple_other_chord_hits, stats.other_chord_checks);
}

void check_recall(Runner &runner, const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate,
		  const std::string &context, RecallStats &stats, int min_recall_percent)
{
	const std::array<bool, 12> detected = detected_pitch_classes(snapshot);
	int expected = 0;
	int hits = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!candidate.pitch_classes[pitch_class])
			continue;
		++expected;
		if (detected[pitch_class])
			++hits;
	}

	stats.hits += hits;
	stats.expected += expected;
	runner.expect(expected > 0 && hits * 100 >= expected * min_recall_percent,
		      context + ": expected at least " + std::to_string(min_recall_percent) +
			      "% pitch-class recall, got " + std::to_string(hits) + "/" +
			      std::to_string(expected));

	if (!candidate.chord_labels.empty()) {
		++stats.chord_checks;
		const bool major_minor_opportunity =
			std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
				    chord_label_is_plain_major_or_minor);
		const bool chord_hit =
			std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
				    [&](const std::string &label) { return snapshot_has_chord_label(snapshot, label); });
		const bool simple_chord_hit =
			std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
				    [&](const std::string &label) {
					    return snapshot_has_simplified_chord_label(snapshot, label);
				    });
		if (chord_hit) {
			++stats.chord_hits;
		} else if (env_truthy("MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES")) {
			const std::array<bool, 12> guitar = grid_pitch_classes(snapshot.guitar_notes);
			const std::array<bool, 12> guitar_analysis =
				grid_pitch_classes(snapshot.guitar_chord_analysis_notes);
			const std::array<bool, 12> guitar_smoothed =
				grid_pitch_classes(snapshot.guitar_chord_smoothed_notes);
			std::fprintf(stderr,
				     "%s: chord opportunity `%s`, detected global `%s`, key `%s`, guitar `%s`, "
				     "other `%s`, expected pc `%s`, guitar pc `%s`, guitar cells `%s`, "
				     "guitar analysis pc `%s`, guitar analysis cells `%s`, guitar smooth pc `%s`, "
				     "guitar smooth cells `%s`\n",
				     context.c_str(), join_labels(candidate.chord_labels).c_str(),
				     snapshot.global_chord.label, snapshot.keyboard_chord.label,
				     snapshot.guitar_chord.label, snapshot.other_chord.label,
				     pitch_class_list(candidate.pitch_classes).c_str(), pitch_class_list(guitar).c_str(),
				     grid_cell_list(snapshot.guitar_notes).c_str(),
				     pitch_class_list(guitar_analysis).c_str(),
				     grid_cell_list(snapshot.guitar_chord_analysis_notes).c_str(),
				     pitch_class_list(guitar_smoothed).c_str(),
				     grid_cell_list(snapshot.guitar_chord_smoothed_notes).c_str());
		}
		if (simple_chord_hit)
			++stats.simple_chord_hits;
		if (major_minor_opportunity) {
			++stats.major_minor_chord_checks;
			if (chord_hit)
				++stats.major_minor_chord_hits;
			if (simple_chord_hit)
				++stats.simple_major_minor_chord_hits;
		} else {
			++stats.other_chord_checks;
			if (chord_hit)
				++stats.other_chord_hits;
			if (simple_chord_hit)
				++stats.simple_other_chord_hits;
		}
		for (const std::string &label : candidate.chord_labels) {
			RecallStats::ChordQualityStats &quality_stats =
				stats.chord_quality[chord_quality_name(label)];
			++quality_stats.checks;
			if (snapshot_has_chord_label(snapshot, label))
				++quality_stats.hits;
			if (snapshot_has_simplified_chord_label(snapshot, label))
				++quality_stats.simple_hits;
		}
	}
}

struct CompositionStats {
	int windows = 0;
	int active_note_sum = 0;
	int pitch_class_sum = 0;
	int min_active_notes = 0;
	int max_active_notes = 0;
	int min_pitch_classes = 0;
	int max_pitch_classes = 0;
};

void add_composition(CompositionStats &stats, const CandidateWindow &candidate)
{
	const int active_notes = static_cast<int>(candidate.active_midis.size());
	const int pitch_classes = pitch_class_count(candidate.pitch_classes);

	++stats.windows;
	stats.active_note_sum += active_notes;
	stats.pitch_class_sum += pitch_classes;
	if (stats.windows == 1) {
		stats.min_active_notes = active_notes;
		stats.max_active_notes = active_notes;
		stats.min_pitch_classes = pitch_classes;
		stats.max_pitch_classes = pitch_classes;
		return;
	}

	stats.min_active_notes = std::min(stats.min_active_notes, active_notes);
	stats.max_active_notes = std::max(stats.max_active_notes, active_notes);
	stats.min_pitch_classes = std::min(stats.min_pitch_classes, pitch_classes);
	stats.max_pitch_classes = std::max(stats.max_pitch_classes, pitch_classes);
}

std::string average_string(int sum, int count)
{
	char buffer[32] = {};
	std::snprintf(buffer, sizeof(buffer), "%.2f", count > 0 ? static_cast<double>(sum) / count : 0.0);
	return buffer;
}

std::string composition_summary(const CompositionStats &stats)
{
	if (stats.windows == 0)
		return "active notes min/avg/max 0/0.00/0, pitch classes min/avg/max 0/0.00/0";

	return "active notes min/avg/max " + std::to_string(stats.min_active_notes) + "/" +
	       average_string(stats.active_note_sum, stats.windows) + "/" +
	       std::to_string(stats.max_active_notes) + ", pitch classes min/avg/max " +
	       std::to_string(stats.min_pitch_classes) + "/" +
	       average_string(stats.pitch_class_sum, stats.windows) + "/" +
	       std::to_string(stats.max_pitch_classes);
}

std::string tsv_field(std::string value)
{
	for (char &ch : value) {
		if (ch == '\t' || ch == '\n' || ch == '\r')
			ch = ' ';
	}
	return value;
}

void append_tsv(std::ostringstream &line, const std::string &value)
{
	line << '\t' << tsv_field(value);
}

void append_tsv(std::ostringstream &line, const char *value)
{
	append_tsv(line, value ? std::string(value) : std::string());
}

void append_tsv(std::ostringstream &line, int value)
{
	line << '\t' << value;
}

void append_tsv(std::ostringstream &line, double value)
{
	line << '\t' << value;
}

void append_tsv(std::ostringstream &line, float value)
{
	line << '\t' << value;
}

const char *bool_cell(bool value)
{
	return value ? "1" : "0";
}

std::string midi_list(const std::vector<int> &midis)
{
	std::string text;
	for (int midi : midis) {
		char item[16] = {};
		std::snprintf(item, sizeof(item), "%s%d", mao_test::note_name(midi % 12), midi / 12 - 1);
		if (!text.empty())
			text += ",";
		text += item;
	}
	return text.empty() ? "--" : text;
}

std::string chord_quality_list(const std::vector<std::string> &labels)
{
	std::set<std::string> qualities;
	for (const std::string &label : labels)
		qualities.insert(chord_quality_name(label));
	std::string text;
	for (const std::string &quality : qualities) {
		if (!text.empty())
			text += "/";
		text += quality;
	}
	return text.empty() ? "--" : text;
}

int pitch_class_hits(const std::array<bool, 12> &expected, const std::array<bool, 12> &detected)
{
	int hits = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (expected[pitch_class] && detected[pitch_class])
			++hits;
	}
	return hits;
}

int pitch_class_false_positives(const std::array<bool, 12> &expected,
				const std::array<bool, 12> &detected)
{
	int false_positives = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!expected[pitch_class] && detected[pitch_class])
			++false_positives;
	}
	return false_positives;
}

int cross_row_expected_hits(const std::array<bool, 12> &expected,
			    const std::array<bool, 12> &bass,
			    const std::array<bool, 12> &keyboard,
			    const std::array<bool, 12> &vocal,
			    const std::array<bool, 12> &other)
{
	int contaminated = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!expected[pitch_class])
			continue;
		if (bass[pitch_class] || keyboard[pitch_class] || vocal[pitch_class] || other[pitch_class])
			++contaminated;
	}
	return contaminated;
}

bool labels_have_exact_chord(const char *actual, const std::vector<std::string> &expected)
{
	return std::any_of(expected.begin(), expected.end(),
			   [&](const std::string &label) { return has_chord_label(actual, label); });
}

bool labels_have_simplified_chord(const mao::AnalysisSnapshot &snapshot,
				  const std::vector<std::string> &expected)
{
	return std::any_of(expected.begin(), expected.end(), [&](const std::string &label) {
		return snapshot_has_simplified_chord_label(snapshot, label);
	});
}

std::string chord_status(const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate)
{
	if (candidate.chord_labels.empty())
		return split_chord_labels(snapshot.guitar_chord.label).empty() ? "no_chord" :
									"single_note_false_chord";
	return std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
			   [&](const std::string &label) { return snapshot_has_chord_label(snapshot, label); }) ?
		       "chord_hit" :
		       "chord_miss";
}

void print_guitarset_attribute_header(std::ostream &out)
{
	out << "status\trecording_id\taudio_path\tcenter_seconds\tsample_rate"
	    << "\tinstrument\texpected_midis\texpected_pitch_classes\texpected_pitch_class_count"
	    << "\texpected_chords\texpected_chord_qualities\texpected_chord_tone_count"
	    << "\tguitar_note_hits\texpected_note_count\tguitar_false_positive_pitch_classes"
	    << "\tcross_row_expected_hits\tchord_hit\tsimple_chord_hit\tguitar_chord_hit"
	    << "\tglobal_chord\tkeyboard_chord\tguitar_chord\tother_chord"
	    << "\tguitar_raw_chord\tguitar_smoothed_chord"
	    << "\tguitar_chord_confidence\tguitar_raw_chord_confidence"
	    << "\tguitar_smoothed_chord_confidence"
	    << "\tguitar_pitch_classes\tguitar_cells\tguitar_analysis_pitch_classes"
	    << "\tguitar_analysis_cells\tguitar_smoothed_pitch_classes\tguitar_smoothed_cells"
	    << "\texpected_raw_peak\texpected_raw_cells\traw_pitch_class_levels"
	    << "\tguitar_probe_pitch_class_levels\tguitar_melodic_probe_pitch_class_levels"
	    << "\texpected_quality_raw_profile"
	    << "\tbass_pitch_classes\tkeyboard_pitch_classes\tvocal_pitch_classes"
	    << "\tother_pitch_classes\tambiguous_pitch_classes"
	    << "\trms\tlow\tmid\thigh\n";
}

void append_guitarset_attribute_row(std::ostream &out, const Recording &recording,
				    const CandidateWindow &candidate,
				    const mao::AnalysisSnapshot &snapshot,
				    const mao_test::Buffer &buffer, uint32_t sample_rate)
{
	const std::array<bool, 12> guitar = grid_pitch_classes(snapshot.guitar_notes);
	const std::array<bool, 12> guitar_analysis =
		grid_pitch_classes(snapshot.guitar_chord_analysis_notes);
	const std::array<bool, 12> guitar_smoothed =
		grid_pitch_classes(snapshot.guitar_chord_smoothed_notes);
	const std::array<bool, 12> bass = grid_pitch_classes(snapshot.bass_notes);
	const std::array<bool, 12> keyboard = grid_pitch_classes(snapshot.keyboard_notes);
	const std::array<bool, 12> vocal = grid_pitch_classes(snapshot.vocal_notes);
	const std::array<bool, 12> other = grid_pitch_classes(snapshot.other_notes);
	const std::array<bool, 12> ambiguous = grid_pitch_classes(snapshot.ambiguous_notes);
	const float raw_peak = strongest_expected_raw_magnitude(candidate, buffer, sample_rate);
	const std::array<float, 12> raw_profile = raw_pitch_class_profile(buffer, sample_rate, 40, 88);

	std::ostringstream line;
	line << chord_status(snapshot, candidate);
	append_tsv(line, recording.id);
	append_tsv(line, recording.audio_path);
	append_tsv(line, candidate.center_seconds);
	append_tsv(line, static_cast<int>(sample_rate));
	append_tsv(line, "guitar");
	append_tsv(line, midi_list(candidate.active_midis));
	append_tsv(line, pitch_class_list(candidate.pitch_classes));
	append_tsv(line, pitch_class_count(candidate.pitch_classes));
	append_tsv(line, join_labels(candidate.chord_labels));
	append_tsv(line, chord_quality_list(candidate.chord_labels));
	append_tsv(line, candidate.chord_tone_count);
	append_tsv(line, pitch_class_hits(candidate.pitch_classes, guitar));
	append_tsv(line, pitch_class_count(candidate.pitch_classes));
	append_tsv(line, pitch_class_false_positives(candidate.pitch_classes, guitar));
	append_tsv(line, cross_row_expected_hits(candidate.pitch_classes, bass, keyboard, vocal, other));
	append_tsv(line, bool_cell(!candidate.chord_labels.empty() &&
				   std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
					       [&](const std::string &label) {
						       return snapshot_has_chord_label(snapshot, label);
					       })));
	append_tsv(line, bool_cell(labels_have_simplified_chord(snapshot, candidate.chord_labels)));
	append_tsv(line, bool_cell(labels_have_exact_chord(snapshot.guitar_chord.label,
							  candidate.chord_labels)));
	append_tsv(line, snapshot.global_chord.label);
	append_tsv(line, snapshot.keyboard_chord.label);
	append_tsv(line, snapshot.guitar_chord.label);
	append_tsv(line, snapshot.other_chord.label);
	append_tsv(line, snapshot.guitar_raw_chord.label);
	append_tsv(line, snapshot.guitar_smoothed_chord.label);
	append_tsv(line, snapshot.guitar_chord.confidence);
	append_tsv(line, snapshot.guitar_raw_chord.confidence);
	append_tsv(line, snapshot.guitar_smoothed_chord.confidence);
	append_tsv(line, pitch_class_list(guitar));
	append_tsv(line, grid_cell_list(snapshot.guitar_notes));
	append_tsv(line, pitch_class_list(guitar_analysis));
	append_tsv(line, grid_cell_list(snapshot.guitar_chord_analysis_notes));
	append_tsv(line, pitch_class_list(guitar_smoothed));
	append_tsv(line, grid_cell_list(snapshot.guitar_chord_smoothed_notes));
	append_tsv(line, raw_peak);
	append_tsv(line, expected_raw_cell_list(candidate, buffer, sample_rate, raw_peak));
	append_tsv(line, raw_pitch_class_level_list(raw_profile));
	append_tsv(line, raw_pitch_class_level_list(snapshot.guitar_chord_debug_probe_levels));
	append_tsv(line, raw_pitch_class_level_list(snapshot.guitar_chord_debug_melodic_probe_levels));
	append_tsv(line, expected_quality_raw_profile(candidate, raw_profile));
	append_tsv(line, pitch_class_list(bass));
	append_tsv(line, pitch_class_list(keyboard));
	append_tsv(line, pitch_class_list(vocal));
	append_tsv(line, pitch_class_list(other));
	append_tsv(line, pitch_class_list(ambiguous));
	append_tsv(line, snapshot.rms);
	append_tsv(line, snapshot.low_energy);
	append_tsv(line, snapshot.mid_energy);
	append_tsv(line, snapshot.high_energy);
	out << line.str() << '\n';
}

void require_recall(Runner &runner, const RecallStats &stats, const char *label, int min_percent)
{
	runner.expect(stats.expected > 0,
		      std::string(label) + ": expected at least one pitch-class check");
	if (stats.expected == 0)
		return;
	runner.expect(stats.hits * 100 >= stats.expected * min_percent,
		      std::string(label) + ": expected aggregate pitch-class recall >=" +
			      std::to_string(min_percent) + "%, got " + std::to_string(stats.hits) +
			      "/" + std::to_string(stats.expected));
}

void require_chord_recall(Runner &runner, const RecallStats &stats, int min_checks, int min_percent)
{
	if (min_checks <= 0)
		return;
	runner.expect(stats.chord_checks >= min_checks,
		      "GuitarSet chord coverage: expected at least " + std::to_string(min_checks) +
			      " chord-checkable windows, got " + std::to_string(stats.chord_checks));
	if (stats.chord_checks < min_checks)
		return;
	runner.expect(stats.chord_hits * 100 >= stats.chord_checks * min_percent,
		      "GuitarSet chord recall: expected >=" + std::to_string(min_percent) +
			      "%, got " + std::to_string(stats.chord_hits) + "/" +
			      std::to_string(stats.chord_checks));
}

void require_chord_hits(Runner &runner, const RecallStats &stats, int min_hits)
{
	if (min_hits <= 0)
		return;
	runner.expect(stats.chord_hits >= min_hits,
		      "GuitarSet chord hits: expected at least " + std::to_string(min_hits) +
			      ", got " + std::to_string(stats.chord_hits) + "/" +
			      std::to_string(stats.chord_checks));
}

void require_chord_bucket_recall(Runner &runner, const char *label, int hits, int checks, int min_percent)
{
	if (min_percent <= 0)
		return;
	runner.expect(checks > 0, std::string(label) + ": expected at least one chord check");
	if (checks == 0)
		return;
	runner.expect(percentage_floor(hits, checks) >= min_percent,
		      std::string(label) + ": expected >=" + std::to_string(min_percent) + "%, got " +
			      percent_string(hits, checks) + " (" + std::to_string(hits) + "/" +
			      std::to_string(checks) + ")");
}

void require_guitar_precision(Runner &runner, const GuitarPrecisionStats &stats, int min_precision_percent,
			      int min_recall_percent, int max_contamination_percent,
			      int max_false_vocal_percent)
{
	runner.expect(stats.expected_pitch_classes > 0,
		      "GuitarSet guitar precision: expected at least one pitch-class check");
	if (stats.expected_pitch_classes == 0)
		return;

	runner.expect(
		percentage_floor(stats.true_positives, stats.true_positives + stats.false_positives) >=
			min_precision_percent,
		"GuitarSet guitar precision: expected >=" + std::to_string(min_precision_percent) +
			"%, got " +
			percent_string(stats.true_positives, stats.true_positives + stats.false_positives) +
			" (" + guitar_precision_summary(stats) + ")");
	runner.expect(
		percentage_floor(stats.true_positives, stats.true_positives + stats.false_negatives) >=
			min_recall_percent,
		"GuitarSet guitar row recall: expected >=" + std::to_string(min_recall_percent) +
			"%, got " +
			percent_string(stats.true_positives, stats.true_positives + stats.false_negatives) +
			" (" + guitar_precision_summary(stats) + ")");
	runner.expect(
		percentage_floor(stats.contaminated_pitch_classes, stats.expected_pitch_classes) <=
			max_contamination_percent,
		"GuitarSet cross-row contamination: expected <=" + std::to_string(max_contamination_percent) +
			"%, got " +
			percent_string(stats.contaminated_pitch_classes, stats.expected_pitch_classes) + " (" +
			guitar_precision_summary(stats) + ")");
	runner.expect(percentage_floor(stats.false_vocal_windows, stats.windows) <= max_false_vocal_percent,
		      "GuitarSet false vocal detection: expected <=" +
			      std::to_string(max_false_vocal_percent) + "% of windows, got " +
			      percent_string(stats.false_vocal_windows, stats.windows) + " (" +
			      guitar_precision_summary(stats) + ")");
}

void require_guitar_chord_precision(Runner &runner, const ChordPrecisionStats &stats, int min_checks,
				    int min_precision_percent)
{
	if (min_checks <= 0)
		return;
	runner.expect(stats.expected_windows >= min_checks,
		      "GuitarSet guitar chord precision coverage: expected at least " +
			      std::to_string(min_checks) + " chord-checkable windows, got " +
			      std::to_string(stats.expected_windows));
	if (stats.expected_windows < min_checks)
		return;
	runner.expect(percentage_floor(stats.true_positives, stats.predicted_windows) >= min_precision_percent,
		      "GuitarSet guitar chord precision: expected >=" +
			      std::to_string(min_precision_percent) + "%, got " +
			      percent_string(stats.true_positives, stats.predicted_windows) + " (" +
			      chord_precision_summary(stats) + ")");
}

void require_single_note_chord_false_rate(Runner &runner, const ChordPrecisionStats &stats, int windows,
					  int max_percent)
{
	if (max_percent < 0 || windows <= 0 || stats.expected_windows > 0)
		return;
	runner.expect(percentage_floor(stats.predicted_windows, windows) <= max_percent,
		      "GuitarSet single-note chord false positives: expected <=" +
			      std::to_string(max_percent) + "%, got " +
			      percent_string(stats.predicted_windows, windows) + " (" +
			      chord_precision_summary(stats) + ")");
}

std::string resolve_manifest_path()
{
	const char *manifest = std::getenv("MUSIC_ANALYZER_GUITARSET_MANIFEST");
	if (manifest && *manifest)
		return manifest;
	return "";
}

} // namespace

int main()
{
	const std::string manifest_path = resolve_manifest_path();
	if (manifest_path.empty()) {
		if (env_truthy("MUSIC_ANALYZER_GUITARSET_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_guitarset: real GuitarSet manifest required; run "
				     "tests/prepare_guitarset_manifest.py via the Makefile target\n");
			return 1;
		}
		std::printf("analyzer_guitarset: skipped, set MUSIC_ANALYZER_GUITARSET_MANIFEST\n");
		return 0;
	}
	if (!file_exists(manifest_path)) {
		std::fprintf(stderr, "analyzer_guitarset: `%s` is not a file\n", manifest_path.c_str());
		return 1;
	}

	std::vector<Recording> recordings;
	std::string error;
	if (!read_manifest(manifest_path, recordings, error)) {
		std::fprintf(stderr, "analyzer_guitarset: failed to read `%s`: %s\n", manifest_path.c_str(),
			     error.c_str());
		return 1;
	}

	const int required_recordings = resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS", 20);
	const int max_windows_per_recording =
		resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT", 4);
	const int required_windows = resolve_positive_int_env(
		"MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS", required_recordings * max_windows_per_recording);
	const int min_active_notes = resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES", 3);
	const int min_pitch_classes = resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES", 3);
	const int min_recall_percent = resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT", 45);
	const int min_window_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT", min_recall_percent);
	const int min_guitar_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT", 90);
	const int min_guitar_row_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT", 90);
	const int max_guitar_contamination_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT", 5);
	const int max_false_vocal_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT", 5);
	const int min_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT", 30);
	const int min_chord_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT", 85);
	const int min_major_minor_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT", 0);
	const int min_other_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT", 0);
	const int min_simple_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT", 0);
	const int min_simple_major_minor_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT", 0);
	const int min_simple_other_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT", 0);
	const int min_chord_checks = resolve_nonnegative_int_env("MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS", 5);
	const int min_chord_hits = resolve_nonnegative_int_env("MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS", 0);
	const int max_single_note_chord_false_percent =
		resolve_percent_env("MUSIC_ANALYZER_GUITARSET_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT", -1);
	const int shard_count = resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_SHARD_COUNT", 1);
	const int shard_index = resolve_nonnegative_int_env("MUSIC_ANALYZER_GUITARSET_SHARD_INDEX", 0);
	if (shard_index >= shard_count) {
		std::fprintf(stderr,
			     "analyzer_guitarset: invalid shard index %d for shard count %d\n",
			     shard_index, shard_count);
		return 1;
	}
	const auto shard_required_count = [shard_count](int total) {
		return (total + shard_count - 1) / shard_count;
	};
	const int shard_required_recordings = shard_required_count(required_recordings);
	const int shard_required_windows = shard_required_count(required_windows);
	const int shard_min_chord_checks = shard_required_count(min_chord_checks);
	const int shard_min_chord_hits = shard_required_count(min_chord_hits);
	const bool inspect_only = env_truthy("MUSIC_ANALYZER_GUITARSET_INSPECT_ONLY");
	const bool attribute_only = env_truthy("MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_ONLY");
	const bool use_all_recordings = env_truthy("MUSIC_ANALYZER_GUITARSET_USE_ALL");
	const char *attribute_path_env = std::getenv("MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV");
	std::ofstream attribute_file;
	if (attribute_path_env && *attribute_path_env) {
		attribute_file.open(attribute_path_env);
		if (!attribute_file) {
			std::fprintf(stderr, "analyzer_guitarset: failed to open attribute TSV `%s`\n",
				     attribute_path_env);
			return 1;
		}
		print_guitarset_attribute_header(attribute_file);
	}

	Runner runner;
	runner.max_reported_failures = resolve_positive_int_env("MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES", 80);
	RecallStats recall;
	GuitarPrecisionStats precision;
	ChordPrecisionStats guitar_chord_precision;
	CompositionStats composition;
	int tested_recordings = 0;
	int tested_windows = 0;
	int read_failures = 0;
	int no_candidate_recordings = 0;
	int unusable_recordings = 0;

	int eligible_recording_index = 0;
	for (std::size_t recording_index = 0; recording_index < recordings.size(); ++recording_index) {
		const Recording &recording = recordings[recording_index];
		WavFormat format;
		if (!read_wav_format(recording.audio_path, format, error)) {
			if (shard_count == 1)
				++unusable_recordings;
			continue;
		}
		std::vector<CandidateWindow> candidates =
			select_candidate_windows(recording, format.sample_rate, max_windows_per_recording,
						 min_active_notes, min_pitch_classes);
		if (candidates.empty()) {
			if (shard_count == 1)
				++no_candidate_recordings;
			continue;
		}
		const int shard_for_recording = eligible_recording_index % shard_count;
		++eligible_recording_index;
		if (shard_count > 1 && shard_for_recording != shard_index)
			continue;
		if (!use_all_recordings && tested_recordings >= shard_required_recordings)
			break;

		++tested_recordings;
		for (const CandidateWindow &candidate : candidates) {
			add_composition(composition, candidate);
			if (!inspect_only) {
				mao_test::Buffer buffer = {};
				uint32_t sample_rate = 0;
				if (!read_wav_window(recording.audio_path, candidate.center_sample, buffer, sample_rate,
						     error)) {
					++read_failures;
					continue;
				}
				const mao::AnalysisSnapshot snapshot = analyze_confirmed_buffer(buffer, sample_rate);
				if (attribute_file)
					append_guitarset_attribute_row(attribute_file, recording, candidate,
								      snapshot, buffer, sample_rate);
				check_recall(runner, snapshot, candidate,
					     recording.id + " at " + std::to_string(candidate.center_seconds) + "s",
					     recall, min_window_recall_percent);
				debug_guitar_window(snapshot, candidate,
						    recording.id + " at " +
							    std::to_string(candidate.center_seconds) + "s");
				add_guitar_precision_metrics(precision, snapshot, candidate);
				add_guitar_chord_precision_metrics(guitar_chord_precision, snapshot, candidate);
			}
			++tested_windows;
		}
	}

	if (!attribute_only) {
		runner.expect(tested_recordings >= shard_required_recordings,
			      "GuitarSet coverage: expected at least " +
				      std::to_string(shard_required_recordings) +
				      " usable excerpts, got " + std::to_string(tested_recordings));
		runner.expect(tested_windows >= shard_required_windows,
			      "GuitarSet coverage: expected at least " + std::to_string(shard_required_windows) +
				      " windows, got " + std::to_string(tested_windows));
	}
	runner.expect(read_failures == 0,
		      "GuitarSet audio read failures: expected 0, got " + std::to_string(read_failures));

	if (!inspect_only && !attribute_only) {
		require_recall(runner, recall, "GuitarSet guitar pitch-class recall", min_recall_percent);
		require_guitar_precision(runner, precision, min_guitar_precision_percent,
					 min_guitar_row_recall_percent, max_guitar_contamination_percent,
					 max_false_vocal_percent);
		require_chord_recall(runner, recall, shard_min_chord_checks, min_chord_recall_percent);
		require_chord_hits(runner, recall, shard_min_chord_hits);
		require_chord_bucket_recall(runner, "GuitarSet major/minor chord recall",
					    recall.major_minor_chord_hits,
					    recall.major_minor_chord_checks,
					    min_major_minor_chord_recall_percent);
		require_chord_bucket_recall(runner, "GuitarSet other chord recall",
					    recall.other_chord_hits, recall.other_chord_checks,
					    min_other_chord_recall_percent);
		require_chord_bucket_recall(runner, "GuitarSet simplified chord recall",
					    recall.simple_chord_hits, recall.chord_checks,
					    min_simple_chord_recall_percent);
		require_chord_bucket_recall(runner, "GuitarSet simplified major/minor chord recall",
					    recall.simple_major_minor_chord_hits,
					    recall.major_minor_chord_checks,
					    min_simple_major_minor_chord_recall_percent);
		require_chord_bucket_recall(runner, "GuitarSet simplified other chord recall",
					    recall.simple_other_chord_hits, recall.other_chord_checks,
					    min_simple_other_chord_recall_percent);
		require_guitar_chord_precision(runner, guitar_chord_precision, shard_min_chord_checks,
					       min_chord_precision_percent);
		require_single_note_chord_false_rate(runner, guitar_chord_precision, tested_windows,
						     max_single_note_chord_false_percent);
	}

	if (runner.failures > 0) {
		std::fprintf(stderr,
			     "analyzer_guitarset: %d/%d checks failed (excerpts %d/%d, windows %d/%d, "
			     "read failures %d, no-candidate excerpts %d, unusable %d, note hits %d/%d, "
			     "chord hits %d/%d, major/minor chord hits %d/%d, other chord hits %d/%d, "
			     "%s, %s, %s, %s)\n",
			     runner.failures, runner.checks, tested_recordings, required_recordings,
			     tested_windows, required_windows, read_failures, no_candidate_recordings,
			     unusable_recordings, recall.hits, recall.expected, recall.chord_hits,
			     recall.chord_checks, recall.major_minor_chord_hits,
			     recall.major_minor_chord_checks, recall.other_chord_hits,
			     recall.other_chord_checks, guitar_precision_summary(precision).c_str(),
			     chord_precision_summary(guitar_chord_precision).c_str(),
			     chord_quality_summary(recall).c_str(),
			     (simplified_chord_summary(recall) + ", " + composition_summary(composition)).c_str());
		return 1;
	}

	if (inspect_only) {
		std::printf(
			"analyzer_guitarset: inspect passed (excerpts %d/%d, windows %d, no-candidate excerpts "
			"%d, unusable %d, %s)\n",
			tested_recordings, required_recordings, tested_windows, no_candidate_recordings,
			unusable_recordings, composition_summary(composition).c_str());
	} else {
		std::printf(
			"analyzer_guitarset: %d checks passed (excerpts %d/%d, windows %d, read failures %d, "
			"no-candidate excerpts %d, unusable %d, note hits %d/%d, chord hits %d/%d, %s)\n",
			runner.checks, tested_recordings, required_recordings, tested_windows, read_failures,
			no_candidate_recordings, unusable_recordings, recall.hits, recall.expected,
			recall.chord_hits, recall.chord_checks,
			("major/minor chord hits " + std::to_string(recall.major_minor_chord_hits) + "/" +
			 std::to_string(recall.major_minor_chord_checks) + ", other chord hits " +
			 std::to_string(recall.other_chord_hits) + "/" +
			 std::to_string(recall.other_chord_checks) + ", " +
			 guitar_precision_summary(precision) + ", " +
			 chord_precision_summary(guitar_chord_precision) + ", " +
			 chord_quality_summary(recall) + ", " +
			 simplified_chord_summary(recall) + ", " +
			 composition_summary(composition))
				.c_str());
	}
	return 0;
}
