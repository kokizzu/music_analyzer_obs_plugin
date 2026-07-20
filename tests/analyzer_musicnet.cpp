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
#include <dirent.h>
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <sys/stat.h>
#include <vector>

namespace {

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

struct DirEntry {
	std::string name;
	bool directory = false;
};

bool is_directory(const std::string &path)
{
	struct stat st = {};
	return ::stat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode);
}

std::string join_path(const std::string &lhs, const std::string &rhs)
{
	if (lhs.empty() || lhs[lhs.size() - 1] == '/')
		return lhs + rhs;
	return lhs + "/" + rhs;
}

std::vector<DirEntry> list_dir(const std::string &path)
{
	std::vector<DirEntry> entries;
	DIR *dir = ::opendir(path.c_str());
	if (!dir)
		return entries;

	while (dirent *entry = ::readdir(dir)) {
		if (std::strcmp(entry->d_name, ".") == 0 || std::strcmp(entry->d_name, "..") == 0)
			continue;
		const std::string child = join_path(path, entry->d_name);
		entries.push_back(DirEntry{entry->d_name, is_directory(child)});
	}
	::closedir(dir);

	std::sort(entries.begin(), entries.end(), [](const DirEntry &a, const DirEntry &b) {
		return a.name < b.name;
	});
	return entries;
}

bool ends_with(const std::string &text, const char *suffix)
{
	const std::size_t len = std::strlen(suffix);
	return text.size() >= len && text.compare(text.size() - len, len, suffix) == 0;
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

std::string trim(std::string text)
{
	while (!text.empty() && std::isspace(static_cast<unsigned char>(text.back())))
		text.pop_back();
	std::size_t start = 0;
	while (start < text.size() && std::isspace(static_cast<unsigned char>(text[start])))
		++start;
	return text.substr(start);
}

std::vector<std::string> split_csv_line(const std::string &line)
{
	std::vector<std::string> fields;
	std::string field;
	bool quoted = false;
	for (std::size_t i = 0; i < line.size(); ++i) {
		const char ch = line[i];
		if (ch == '"') {
			if (quoted && i + 1 < line.size() && line[i + 1] == '"') {
				field.push_back('"');
				++i;
			} else {
				quoted = !quoted;
			}
			continue;
		}
		if (ch == ',' && !quoted) {
			fields.push_back(trim(field));
			field.clear();
			continue;
		}
		field.push_back(ch);
	}
	fields.push_back(trim(field));
	return fields;
}

int parse_int(const std::string &text, int fallback)
{
	char *end = nullptr;
	const long value = std::strtol(text.c_str(), &end, 10);
	return end && *end == '\0' ? static_cast<int>(value) : fallback;
}

struct NoteAnnotation {
	int start_sample = 0;
	int end_sample = 0;
	int instrument = 0;
	int midi = 0;
};

bool read_musicnet_labels(const std::string &path, std::vector<NoteAnnotation> &notes, std::string &error)
{
	std::ifstream file(path);
	if (!file) {
		error = "open failed";
		return false;
	}

	std::string line;
	if (!std::getline(file, line)) {
		error = "empty label file";
		return false;
	}
	const std::vector<std::string> header = split_csv_line(line);
	std::map<std::string, int> column;
	for (std::size_t i = 0; i < header.size(); ++i)
		column[header[i]] = static_cast<int>(i);

	for (const char *name : {"start_time", "end_time", "instrument", "note"}) {
		if (column.find(name) == column.end()) {
			error = std::string("missing label column ") + name;
			return false;
		}
	}

	while (std::getline(file, line)) {
		if (trim(line).empty())
			continue;
		const std::vector<std::string> fields = split_csv_line(line);
		if (fields.size() < header.size())
			continue;
		const int start_sample = parse_int(fields[column["start_time"]], -1);
		const int end_sample = parse_int(fields[column["end_time"]], -1);
		const int instrument = parse_int(fields[column["instrument"]], -1);
		const int midi = parse_int(fields[column["note"]], -1);
		if (start_sample < 0 || end_sample <= start_sample || instrument < 0)
			continue;
		if (midi < mao::kFirstAnalyzedMidi || midi > mao::kLastAnalyzedMidi)
			continue;
		notes.push_back(NoteAnnotation{start_sample, end_sample, instrument, midi});
	}

	if (notes.empty()) {
		error = "no usable note labels";
		return false;
	}
	return true;
}

struct Recording {
	int id = 0;
	std::string audio_path;
	std::string label_path;
	uint32_t sample_rate = 0;
	uint64_t frame_count = 0;
	std::vector<NoteAnnotation> notes;
};

bool load_recording(const std::string &audio_path, const std::string &label_path, Recording &recording,
		    std::string &error)
{
	WavFormat format;
	if (!read_wav_format(audio_path, format, error))
		return false;
	if (!read_musicnet_labels(label_path, recording.notes, error))
		return false;
	recording.audio_path = audio_path;
	recording.label_path = label_path;
	recording.sample_rate = format.sample_rate;
	recording.frame_count = format.frame_count;
	return true;
}

int id_from_wav_name(const std::string &name)
{
	if (!ends_with(name, ".wav"))
		return -1;
	return parse_int(name.substr(0, name.size() - 4), -1);
}

void collect_split_recordings(const std::string &root, const char *data_dir, const char *label_dir,
			      std::vector<Recording> &recordings, int &unusable)
{
	const std::string data_path = join_path(root, data_dir);
	const std::string label_path = join_path(root, label_dir);
	if (!is_directory(data_path) || !is_directory(label_path))
		return;

	for (const DirEntry &entry : list_dir(data_path)) {
		if (entry.directory)
			continue;
		const int id = id_from_wav_name(entry.name);
		if (id < 0)
			continue;

		Recording recording;
		recording.id = id;
		std::string error;
		const std::string audio = join_path(data_path, entry.name);
		const std::string labels = join_path(label_path, std::to_string(id) + ".csv");
		if (!load_recording(audio, labels, recording, error)) {
			++unusable;
			if (unusable <= 5)
				std::fprintf(stderr, "analyzer_musicnet: skipping %d: %s\n", id, error.c_str());
			continue;
		}
		recordings.push_back(recording);
	}
}

bool has_musicnet_layout(const std::string &root)
{
	return is_directory(join_path(root, "train_data")) || is_directory(join_path(root, "test_data"));
}

std::string resolve_musicnet_layout(const std::string &root)
{
	if (has_musicnet_layout(root))
		return root;

	const std::vector<std::string> candidates = {
		join_path(root, "musicnet"),
		join_path(root, "MusicNet"),
	};
	for (const std::string &candidate : candidates) {
		if (has_musicnet_layout(candidate))
			return candidate;
	}
	return root;
}

std::string resolve_musicnet_root()
{
	const char *root = std::getenv("MUSIC_ANALYZER_MUSICNET_ROOT");
	if (root && *root)
		return resolve_musicnet_layout(root);

	root = std::getenv("MUSICNET_PATH");
	if (root && *root)
		return resolve_musicnet_layout(root);

	const char *dataset_root = std::getenv("MUSIC_ANALYZER_DATASET_ROOT");
	if (!dataset_root || !*dataset_root)
		return "";

	const std::vector<std::string> candidates = {
		join_path(dataset_root, "MusicNet"),
		join_path(dataset_root, "musicnet"),
		join_path(dataset_root, "MusicNet/musicnet"),
		join_path(dataset_root, "musicnet/musicnet"),
	};
	for (const std::string &candidate : candidates) {
		if (has_musicnet_layout(candidate))
			return candidate;
	}
	return resolve_musicnet_layout(dataset_root);
}

bool env_truthy(const char *name)
{
	const char *value = std::getenv(name);
	return value && *value && std::strcmp(value, "0") != 0 && std::strcmp(value, "false") != 0 &&
	       std::strcmp(value, "FALSE") != 0;
}

int resolve_positive_int_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed > 0 ? parsed : fallback;
}

int resolve_percent_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed >= 0 && parsed <= 100 ? parsed : fallback;
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

bool has_simplified_chord_label(const char *actual, const std::string &expected)
{
	if (!actual)
		return false;
	const std::string simplified_expected = simplified_chord_label(expected);
	const char *cursor = actual;
	while (*cursor) {
		const char *end = cursor;
		while (*end && *end != '=')
			++end;
		if (end > cursor) {
			const std::string component(cursor, static_cast<std::size_t>(end - cursor));
			if (simplified_chord_label(component) == simplified_expected)
				return true;
		}
		cursor = *end == '=' ? end + 1 : end;
	}
	return false;
}

bool snapshot_has_simplified_chord_label(const mao::AnalysisSnapshot &snapshot, const std::string &label)
{
	return has_simplified_chord_label(snapshot.global_chord.label, label) ||
	       has_simplified_chord_label(snapshot.keyboard_chord.label, label) ||
	       has_simplified_chord_label(snapshot.guitar_chord.label, label) ||
	       has_simplified_chord_label(snapshot.other_chord.label, label);
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

std::string pitch_class_list(const std::array<bool, 12> &pitch_classes)
{
	std::string joined;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!pitch_classes[pitch_class])
			continue;
		if (!joined.empty())
			joined += " ";
		joined += mao_test::note_name(pitch_class);
	}
	return joined.empty() ? "--" : joined;
}

struct ActiveNote {
	int instrument = 0;
	int midi = 0;
};

struct CandidateWindow {
	uint64_t center_sample = 0;
	std::vector<ActiveNote> active;
	std::array<bool, 12> pitch_classes = {};
	std::vector<std::string> chord_labels;
	int chord_tone_count = 0;
	double score = 0.0;
};

int active_instrument_count(const CandidateWindow &candidate)
{
	std::set<int> instruments;
	for (const ActiveNote &active : candidate.active)
		instruments.insert(active.instrument);
	return static_cast<int>(instruments.size());
}

CandidateWindow candidate_window_at(const Recording &recording, uint64_t sample)
{
	CandidateWindow candidate;
	candidate.center_sample = sample;

	for (const NoteAnnotation &note : recording.notes) {
		const int duration = note.end_sample - note.start_sample;
		const int edge =
			std::min(static_cast<int>(std::llround(static_cast<double>(recording.sample_rate) * 0.035)),
				 duration / 5);
		const int start = note.start_sample + edge;
		const int end = note.end_sample - edge;
		if (sample < static_cast<uint64_t>(start) || sample > static_cast<uint64_t>(end))
			continue;
		candidate.active.push_back(ActiveNote{note.instrument, note.midi});
		candidate.pitch_classes[((note.midi % 12) + 12) % 12] = true;
	}

	if (candidate.active.size() < 2)
		return candidate;

	candidate.chord_labels = expected_common_chord_labels(candidate.pitch_classes, candidate.chord_tone_count);
	candidate.score = static_cast<double>(active_instrument_count(candidate)) * 120.0 +
			  static_cast<double>(candidate.active.size()) * 80.0 +
			  static_cast<double>(pitch_class_count(candidate.pitch_classes)) * 20.0 +
			  static_cast<double>(candidate.chord_tone_count) * 25.0 +
			  (candidate.chord_labels.empty() ? 0.0 : 50.0);
	return candidate;
}

std::vector<CandidateWindow> select_candidate_windows(const Recording &recording, int max_windows,
						      int min_active_notes, int min_active_instruments,
						      int min_pitch_classes)
{
	std::vector<CandidateWindow> candidates;

	for (const NoteAnnotation &note : recording.notes) {
		const uint64_t sample = static_cast<uint64_t>(note.start_sample) +
					static_cast<uint64_t>(note.end_sample - note.start_sample) / 2;
		CandidateWindow candidate = candidate_window_at(recording, sample);
		if (static_cast<int>(candidate.active.size()) < min_active_notes)
			continue;
		if (active_instrument_count(candidate) < min_active_instruments)
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
			if (distance < static_cast<uint64_t>(recording.sample_rate / 5)) {
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
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "MusicNet labeled real mix", 0);
	return snapshot;
}

struct RecallStats {
	int hits = 0;
	int expected = 0;
	int chord_hits = 0;
	int simple_chord_hits = 0;
	int chord_checks = 0;
};

struct PitchPrecisionStats {
	int windows = 0;
	int true_positives = 0;
	int false_positives = 0;
	int false_negatives = 0;
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

void add_pitch_precision_metrics(PitchPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
				 const CandidateWindow &candidate)
{
	++stats.windows;
	const std::array<bool, 12> detected = detected_pitch_classes(snapshot);
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		const bool expected = candidate.pitch_classes[pitch_class];
		if (expected && detected[pitch_class])
			++stats.true_positives;
		else if (!expected && detected[pitch_class])
			++stats.false_positives;
		else if (expected && !detected[pitch_class])
			++stats.false_negatives;
	}
}

void add_global_chord_precision_metrics(ChordPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
					const CandidateWindow &candidate)
{
	const bool expected = !candidate.chord_labels.empty();
	const std::vector<std::string> predicted = split_chord_labels(snapshot.global_chord.label);
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

void add_global_simplified_chord_precision_metrics(ChordPrecisionStats &stats,
						   const mao::AnalysisSnapshot &snapshot,
						   const CandidateWindow &candidate)
{
	const bool expected = !candidate.chord_labels.empty();
	const std::vector<std::string> predicted = split_chord_labels(snapshot.global_chord.label);
	const bool predicted_any = !predicted.empty();
	bool matched = false;
	for (const std::string &predicted_label : predicted) {
		const std::string simplified_predicted = simplified_chord_label(predicted_label);
		for (const std::string &expected_label : candidate.chord_labels) {
			if (simplified_predicted == simplified_chord_label(expected_label)) {
				matched = true;
				break;
			}
		}
		if (matched)
			break;
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

std::string pitch_precision_summary(const PitchPrecisionStats &stats)
{
	return "pitch precision " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_positives) +
	       ", pitch recall " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_negatives) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", tp/fp/fn " + std::to_string(stats.true_positives) + "/" +
	       std::to_string(stats.false_positives) + "/" + std::to_string(stats.false_negatives);
}

std::string chord_precision_summary(const ChordPrecisionStats &stats)
{
	return "global chord precision " + percent_string(stats.true_positives, stats.predicted_windows) +
	       ", global chord recall " + percent_string(stats.true_positives, stats.expected_windows) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", tp/fp/fn " + std::to_string(stats.true_positives) + "/" +
	       std::to_string(stats.false_positives) + "/" + std::to_string(stats.false_negatives);
}

std::string simplified_chord_summary(const RecallStats &stats)
{
	return "simple chord hits " + std::to_string(stats.simple_chord_hits) + "/" +
	       std::to_string(stats.chord_checks) + " " +
	       percent_string(stats.simple_chord_hits, stats.chord_checks);
}

void check_recall(Runner &runner, const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate,
		  const std::string &context, RecallStats &stats, int min_recall_percent,
		  bool verbose_chord_misses)
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
		} else if (verbose_chord_misses) {
			std::fprintf(stderr,
				     "%s: chord opportunity `%s`, expected pcs `%s`, detected pcs `%s`, "
				     "detected global `%s`, key `%s`, guitar `%s`, other `%s`\n",
				     context.c_str(), join_labels(candidate.chord_labels).c_str(),
				     pitch_class_list(candidate.pitch_classes).c_str(),
				     pitch_class_list(detected).c_str(), snapshot.global_chord.label,
				     snapshot.keyboard_chord.label, snapshot.guitar_chord.label,
				     snapshot.other_chord.label);
		}
		if (simple_chord_hit)
			++stats.simple_chord_hits;
	}
}

struct CompositionStats {
	int windows = 0;
	int active_note_sum = 0;
	int active_instrument_sum = 0;
	int pitch_class_sum = 0;
	int min_active_notes = 0;
	int max_active_notes = 0;
	int min_active_instruments = 0;
	int max_active_instruments = 0;
	int min_pitch_classes = 0;
	int max_pitch_classes = 0;
};

void add_composition(CompositionStats &stats, const CandidateWindow &candidate)
{
	const int active_notes = static_cast<int>(candidate.active.size());
	const int active_instruments = active_instrument_count(candidate);
	const int pitch_classes = pitch_class_count(candidate.pitch_classes);

	++stats.windows;
	stats.active_note_sum += active_notes;
	stats.active_instrument_sum += active_instruments;
	stats.pitch_class_sum += pitch_classes;
	if (stats.windows == 1) {
		stats.min_active_notes = active_notes;
		stats.max_active_notes = active_notes;
		stats.min_active_instruments = active_instruments;
		stats.max_active_instruments = active_instruments;
		stats.min_pitch_classes = pitch_classes;
		stats.max_pitch_classes = pitch_classes;
		return;
	}

	stats.min_active_notes = std::min(stats.min_active_notes, active_notes);
	stats.max_active_notes = std::max(stats.max_active_notes, active_notes);
	stats.min_active_instruments = std::min(stats.min_active_instruments, active_instruments);
	stats.max_active_instruments = std::max(stats.max_active_instruments, active_instruments);
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
		return "active notes min/avg/max 0/0.00/0, active instruments min/avg/max 0/0.00/0, "
		       "pitch classes min/avg/max 0/0.00/0";

	return "active notes min/avg/max " + std::to_string(stats.min_active_notes) + "/" +
	       average_string(stats.active_note_sum, stats.windows) + "/" +
	       std::to_string(stats.max_active_notes) + ", active instruments min/avg/max " +
	       std::to_string(stats.min_active_instruments) + "/" +
	       average_string(stats.active_instrument_sum, stats.windows) + "/" +
	       std::to_string(stats.max_active_instruments) + ", pitch classes min/avg/max " +
	       std::to_string(stats.min_pitch_classes) + "/" +
	       average_string(stats.pitch_class_sum, stats.windows) + "/" +
	       std::to_string(stats.max_pitch_classes);
}

} // namespace

int main()
{
	const std::string root = resolve_musicnet_root();
	if (root.empty()) {
		if (env_truthy("MUSIC_ANALYZER_MUSICNET_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_musicnet: real MusicNet dataset required; set "
				     "MUSIC_ANALYZER_MUSICNET_ROOT, MUSICNET_PATH, or MUSIC_ANALYZER_DATASET_ROOT\n");
			return 1;
		}
		std::printf("analyzer_musicnet: skipped, set MUSIC_ANALYZER_MUSICNET_ROOT to a local MusicNet dataset\n");
		return 0;
	}
	if (!is_directory(root)) {
		std::fprintf(stderr, "analyzer_musicnet: `%s` is not a directory\n", root.c_str());
		return 1;
	}

	std::vector<Recording> recordings;
	int unusable_recordings = 0;
	collect_split_recordings(root, "train_data", "train_labels", recordings, unusable_recordings);
	collect_split_recordings(root, "test_data", "test_labels", recordings, unusable_recordings);
	std::sort(recordings.begin(), recordings.end(), [](const Recording &a, const Recording &b) {
		return a.id < b.id;
	});

	const int required_recordings = resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS", 20);
	const int max_windows_per_recording =
		resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING", 12);
	const int default_required_windows = std::min(required_recordings * 4,
						      max_windows_per_recording * required_recordings);
	const int required_windows =
		resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS", default_required_windows);
	const int min_active_notes =
		resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW", 2);
	const int min_active_instruments =
		resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW", 2);
	const int min_pitch_classes =
		resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW", 2);
	const int min_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT", 40);
	const int min_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT", 35);
	const int min_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT", 20);
	const int min_simple_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT", 0);
	const int min_global_chord_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT", 20);
	const int min_global_simple_chord_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT", 0);
	const int min_global_simple_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT", 0);
	const int min_chord_checks = resolve_positive_int_env("MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS", 5);
	const bool inspect_only = env_truthy("MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY");
	const bool verbose_chord_misses =
		env_truthy("MUSIC_ANALYZER_MUSICNET_VERBOSE_CHORD_MISSES") || min_chord_recall_percent > 0;

	Runner runner;
	RecallStats recall;
	PitchPrecisionStats pitch_precision;
	ChordPrecisionStats global_chord_precision;
	ChordPrecisionStats global_simplified_chord_precision;
	CompositionStats composition;
	int recordings_with_windows = 0;
	int tested_windows = 0;
	int read_failures = 0;
	int no_candidate_recordings = 0;

	for (const Recording &recording : recordings) {
		const std::vector<CandidateWindow> candidates =
			select_candidate_windows(recording, max_windows_per_recording, min_active_notes,
						 min_active_instruments, min_pitch_classes);
		if (candidates.empty()) {
			++no_candidate_recordings;
			continue;
		}

		int recording_windows = 0;
		for (const CandidateWindow &candidate : candidates) {
			++recording_windows;
			++tested_windows;
			add_composition(composition, candidate);
			if (inspect_only)
				continue;

			mao_test::Buffer buffer = {};
			uint32_t sample_rate = 0;
			std::string error;
			if (!read_wav_window(recording.audio_path, candidate.center_sample, buffer, sample_rate, error)) {
				++read_failures;
				runner.expect(false, "MusicNet " + std::to_string(recording.id) + " at sample " +
							     std::to_string(candidate.center_sample) + ": " + error);
				continue;
			}

			const mao::AnalysisSnapshot snapshot = analyze_confirmed_buffer(buffer, sample_rate);
			check_recall(runner, snapshot, candidate,
				     "MusicNet " + std::to_string(recording.id) + " at sample " +
					     std::to_string(candidate.center_sample),
				     recall, min_recall_percent, verbose_chord_misses);
			add_pitch_precision_metrics(pitch_precision, snapshot, candidate);
			add_global_chord_precision_metrics(global_chord_precision, snapshot, candidate);
			add_global_simplified_chord_precision_metrics(global_simplified_chord_precision, snapshot,
								      candidate);
		}

		if (recording_windows > 0)
			++recordings_with_windows;
	}

	if (recordings.empty()) {
		std::fprintf(stderr,
			     "analyzer_musicnet: no MusicNet recordings found under `%s`; expected train_data/test_data "
			     "and train_labels/test_labels\n",
			     root.c_str());
		return 1;
	}

	runner.expect(recordings_with_windows >= required_recordings,
		      "MusicNet coverage: expected at least " + std::to_string(required_recordings) +
			      " labeled recordings with candidate windows, got " +
			      std::to_string(recordings_with_windows));
	runner.expect(tested_windows >= required_windows,
		      "MusicNet coverage: expected at least " + std::to_string(required_windows) +
			      " candidate windows, got " + std::to_string(tested_windows));
	runner.expect(composition.windows == tested_windows,
		      "MusicNet composition: expected composition stats for every window, got " +
			      std::to_string(composition.windows) + "/" + std::to_string(tested_windows));
	if (!inspect_only) {
		runner.expect(recall.expected > 0 && recall.hits * 100 >= recall.expected * min_recall_percent,
			      "MusicNet real-mix pitch-class recall: expected >=" +
				      std::to_string(min_recall_percent) + "%, got " +
				      std::to_string(recall.hits) + "/" + std::to_string(recall.expected));
		runner.expect(pitch_precision.true_positives + pitch_precision.false_negatives > 0,
			      "MusicNet real-mix pitch precision: expected at least one pitch-class check");
		if (pitch_precision.true_positives + pitch_precision.false_negatives > 0) {
			runner.expect(
				percentage_floor(pitch_precision.true_positives,
						 pitch_precision.true_positives +
							 pitch_precision.false_positives) >= min_precision_percent,
				"MusicNet real-mix pitch precision: expected >=" +
					std::to_string(min_precision_percent) + "%, got " +
					percent_string(pitch_precision.true_positives,
						       pitch_precision.true_positives +
							       pitch_precision.false_positives) +
					" (" + pitch_precision_summary(pitch_precision) + ")");
		}
		if (recall.chord_checks >= min_chord_checks) {
			runner.expect(recall.chord_hits * 100 >= recall.chord_checks * min_chord_recall_percent,
				      "MusicNet real-mix chord recall: expected >=" +
					      std::to_string(min_chord_recall_percent) + "%, got " +
					      std::to_string(recall.chord_hits) + "/" +
					      std::to_string(recall.chord_checks));
			if (min_simple_chord_recall_percent > 0) {
				runner.expect(recall.simple_chord_hits * 100 >=
						      recall.chord_checks * min_simple_chord_recall_percent,
					      "MusicNet real-mix simplified chord recall: expected >=" +
						      std::to_string(min_simple_chord_recall_percent) +
						      "%, got " + std::to_string(recall.simple_chord_hits) +
						      "/" + std::to_string(recall.chord_checks));
			}
			if (min_global_simple_chord_precision_percent > 0) {
				runner.expect(
					percentage_floor(global_simplified_chord_precision.true_positives,
							 global_simplified_chord_precision.predicted_windows) >=
						min_global_simple_chord_precision_percent,
					"MusicNet real-mix simplified global chord precision: expected >=" +
						std::to_string(min_global_simple_chord_precision_percent) +
						"%, got " +
						percent_string(global_simplified_chord_precision.true_positives,
							       global_simplified_chord_precision.predicted_windows) +
						" (" +
						chord_precision_summary(global_simplified_chord_precision) + ")");
			}
			if (min_global_simple_chord_recall_percent > 0) {
				runner.expect(
					percentage_floor(global_simplified_chord_precision.true_positives,
							 global_simplified_chord_precision.expected_windows) >=
						min_global_simple_chord_recall_percent,
					"MusicNet real-mix simplified global chord recall: expected >=" +
						std::to_string(min_global_simple_chord_recall_percent) +
						"%, got " +
						percent_string(global_simplified_chord_precision.true_positives,
							       global_simplified_chord_precision.expected_windows) +
						" (" +
						chord_precision_summary(global_simplified_chord_precision) + ")");
			}
			runner.expect(percentage_floor(global_chord_precision.true_positives,
						       global_chord_precision.predicted_windows) >=
					      min_global_chord_precision_percent,
				      "MusicNet real-mix global chord precision: expected >=" +
					      std::to_string(min_global_chord_precision_percent) +
					      "%, got " +
					      percent_string(global_chord_precision.true_positives,
							     global_chord_precision.predicted_windows) +
					      " (" + chord_precision_summary(global_chord_precision) + ")");
		}
	}

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_musicnet: %d/%d checks failed (recordings %d/%zu, windows %d, "
			     "read failures %d, no-candidate recordings %d, unusable %d, note hits %d/%d, "
			     "chord hits %d/%d, %s, %s, simplified %s, %s, %s)\n",
			     runner.failures, runner.checks, recordings_with_windows, recordings.size(), tested_windows,
			     read_failures, no_candidate_recordings, unusable_recordings, recall.hits, recall.expected,
			     recall.chord_hits, recall.chord_checks, pitch_precision_summary(pitch_precision).c_str(),
			     simplified_chord_summary(recall).c_str(),
			     chord_precision_summary(global_simplified_chord_precision).c_str(),
			     chord_precision_summary(global_chord_precision).c_str(),
			     composition_summary(composition).c_str());
		return 1;
	}

	if (inspect_only) {
		std::printf("analyzer_musicnet: inspect passed (recordings %d/%zu, windows %d, "
			    "no-candidate recordings %d, unusable %d, %s)\n",
			    recordings_with_windows, recordings.size(), tested_windows, no_candidate_recordings,
			    unusable_recordings, composition_summary(composition).c_str());
	} else {
		std::printf("analyzer_musicnet: %d checks passed (recordings %d/%zu, windows %d, "
			    "read failures %d, no-candidate recordings %d, unusable %d, note hits %d/%d, "
			    "chord hits %d/%d, %s, %s, simplified %s, %s, %s)\n",
			    runner.checks, recordings_with_windows, recordings.size(), tested_windows, read_failures,
			    no_candidate_recordings, unusable_recordings, recall.hits, recall.expected,
			    recall.chord_hits, recall.chord_checks, pitch_precision_summary(pitch_precision).c_str(),
			    simplified_chord_summary(recall).c_str(),
			    chord_precision_summary(global_simplified_chord_precision).c_str(),
			    chord_precision_summary(global_chord_precision).c_str(),
			    composition_summary(composition).c_str());
	}
	return 0;
}
