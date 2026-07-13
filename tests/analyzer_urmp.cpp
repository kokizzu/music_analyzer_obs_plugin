#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <fstream>
#include <map>
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

bool file_exists(const std::string &path)
{
	struct stat st = {};
	return ::stat(path.c_str(), &st) == 0 && S_ISREG(st.st_mode);
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

bool starts_with(const std::string &text, const char *prefix)
{
	const std::size_t len = std::strlen(prefix);
	return text.size() >= len && text.compare(0, len, prefix) == 0;
}

bool ends_with(const std::string &text, const char *suffix)
{
	const std::size_t len = std::strlen(suffix);
	return text.size() >= len && text.compare(text.size() - len, len, suffix) == 0;
}

bool has_urmp_piece_files(const std::string &path)
{
	bool has_mix = false;
	bool has_notes = false;
	for (const DirEntry &entry : list_dir(path)) {
		if (entry.directory)
			continue;
		has_mix = has_mix || (starts_with(entry.name, "AuMix_") && ends_with(entry.name, ".wav"));
		has_notes = has_notes || (starts_with(entry.name, "Notes_") && ends_with(entry.name, ".txt"));
	}
	return has_mix && has_notes;
}

void collect_piece_dirs(const std::string &path, int depth, std::vector<std::string> &piece_dirs)
{
	if (has_urmp_piece_files(path)) {
		piece_dirs.push_back(path);
		return;
	}
	if (depth <= 0)
		return;

	for (const DirEntry &entry : list_dir(path)) {
		if (!entry.directory)
			continue;
		collect_piece_dirs(join_path(path, entry.name), depth - 1, piece_dirs);
	}
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

uint16_t read_be_u16(const std::vector<unsigned char> &bytes, std::size_t offset)
{
	return static_cast<uint16_t>(bytes[offset] << 8) | static_cast<uint16_t>(bytes[offset + 1]);
}

uint32_t read_be_u32(const std::vector<unsigned char> &bytes, std::size_t offset)
{
	return (static_cast<uint32_t>(bytes[offset]) << 24) | (static_cast<uint32_t>(bytes[offset + 1]) << 16) |
	       (static_cast<uint32_t>(bytes[offset + 2]) << 8) | static_cast<uint32_t>(bytes[offset + 3]);
}

bool read_file_bytes(const std::string &path, std::vector<unsigned char> &bytes, std::string &error)
{
	std::ifstream file(path, std::ios::binary);
	if (!file) {
		error = "open failed";
		return false;
	}
	file.seekg(0, std::ios::end);
	const std::streamoff size = file.tellg();
	if (size <= 0) {
		error = "empty file";
		return false;
	}
	file.seekg(0, std::ios::beg);
	bytes.resize(static_cast<std::size_t>(size));
	file.read(reinterpret_cast<char *>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
	if (file.gcount() != static_cast<std::streamsize>(bytes.size())) {
		error = "short read";
		return false;
	}
	return true;
}

struct WavFormat {
	uint16_t audio_format = 0;
	uint16_t channels = 0;
	uint32_t sample_rate = 0;
	uint16_t block_align = 0;
	uint16_t bits_per_sample = 0;
	uint64_t data_offset = 0;
	uint64_t data_size = 0;
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
	return true;
}

bool read_midi_var_len(const std::vector<unsigned char> &bytes, std::size_t end, std::size_t &pos,
		       uint32_t &value, std::string &error)
{
	value = 0;
	for (int i = 0; i < 4; ++i) {
		if (pos >= end) {
			error = "truncated variable-length value";
			return false;
		}
		const unsigned char byte = bytes[pos++];
		value = (value << 7) | static_cast<uint32_t>(byte & 0x7f);
		if ((byte & 0x80) == 0)
			return true;
	}
	error = "variable-length value is too long";
	return false;
}

bool midi_read_data_byte(const std::vector<unsigned char> &bytes, std::size_t end, std::size_t &pos, int &value,
			 std::string &error)
{
	if (pos >= end) {
		error = "truncated MIDI event";
		return false;
	}
	if (bytes[pos] & 0x80) {
		error = "expected MIDI data byte";
		return false;
	}
	value = bytes[pos++];
	return true;
}

bool parse_midi_track_notes(const std::vector<unsigned char> &bytes, std::size_t start, std::size_t end,
			    std::array<bool, 12> &pitch_classes, int &note_count, std::string &error)
{
	std::size_t pos = start;
	unsigned char running_status = 0;
	while (pos < end) {
		uint32_t delta = 0;
		if (!read_midi_var_len(bytes, end, pos, delta, error))
			return false;
		(void)delta;
		if (pos >= end)
			break;

		unsigned char status = bytes[pos++];
		int first_data = -1;
		if (status & 0x80) {
			if (status < 0xf0)
				running_status = status;
		} else {
			if (running_status == 0) {
				error = "MIDI running status used before channel status";
				return false;
			}
			first_data = status;
			status = running_status;
		}

		if (status == 0xff) {
			if (first_data >= 0) {
				error = "running status used for MIDI meta event";
				return false;
			}
			int type = 0;
			if (!midi_read_data_byte(bytes, end, pos, type, error))
				return false;
			(void)type;
			uint32_t length = 0;
			if (!read_midi_var_len(bytes, end, pos, length, error))
				return false;
			if (pos + length > end) {
				error = "truncated MIDI meta event";
				return false;
			}
			pos += length;
			continue;
		}

		if (status == 0xf0 || status == 0xf7) {
			if (first_data >= 0) {
				error = "running status used for MIDI sysex event";
				return false;
			}
			uint32_t length = 0;
			if (!read_midi_var_len(bytes, end, pos, length, error))
				return false;
			if (pos + length > end) {
				error = "truncated MIDI sysex event";
				return false;
			}
			pos += length;
			continue;
		}

		if (status < 0x80 || status > 0xef) {
			error = "unsupported MIDI event status";
			return false;
		}

		const unsigned char event_type = status & 0xf0;
		const int data_len = (event_type == 0xc0 || event_type == 0xd0) ? 1 : 2;
		int data1 = first_data;
		if (data1 < 0 && !midi_read_data_byte(bytes, end, pos, data1, error))
			return false;
		int data2 = 0;
		if (data_len == 2 && !midi_read_data_byte(bytes, end, pos, data2, error))
			return false;

		if (event_type == 0x90 && data2 > 0 && data1 >= 0 && data1 <= 127) {
			pitch_classes[data1 % 12] = true;
			++note_count;
		}
	}
	return true;
}

bool read_midi_score_pitch_classes(const std::string &path, std::array<bool, 12> &pitch_classes,
				   int &note_count, std::string &error)
{
	pitch_classes.fill(false);
	note_count = 0;

	std::vector<unsigned char> bytes;
	if (!read_file_bytes(path, bytes, error))
		return false;
	if (bytes.size() < 14 || std::memcmp(bytes.data(), "MThd", 4) != 0) {
		error = "missing MIDI MThd header";
		return false;
	}

	const uint32_t header_size = read_be_u32(bytes, 4);
	if (header_size < 6 || 8u + header_size > bytes.size()) {
		error = "invalid MIDI header size";
		return false;
	}
	const uint16_t track_count = read_be_u16(bytes, 10);
	std::size_t pos = 8u + header_size;
	int parsed_tracks = 0;
	while (pos + 8 <= bytes.size()) {
		const bool is_track = std::memcmp(bytes.data() + pos, "MTrk", 4) == 0;
		const uint32_t chunk_size = read_be_u32(bytes, pos + 4);
		const std::size_t chunk_start = pos + 8;
		const std::size_t chunk_end = chunk_start + chunk_size;
		if (chunk_end > bytes.size()) {
			error = "truncated MIDI chunk";
			return false;
		}
		if (is_track) {
			++parsed_tracks;
			if (!parse_midi_track_notes(bytes, chunk_start, chunk_end, pitch_classes, note_count, error))
				return false;
		}
		pos = chunk_end;
	}

	if (track_count == 0 || parsed_tracks == 0) {
		error = "MIDI score has no tracks";
		return false;
	}
	if (note_count == 0) {
		error = "MIDI score has no note-on events";
		return false;
	}
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

bool read_wav_window(const std::string &path, double center_seconds, mao_test::Buffer &buffer,
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

	const uint64_t frame_count = format.data_size / format.block_align;
	if (frame_count < buffer.size()) {
		error = "audio shorter than analyzer window";
		return false;
	}

	int64_t start_frame =
		static_cast<int64_t>(std::llround(center_seconds * static_cast<double>(format.sample_rate))) -
		static_cast<int64_t>(buffer.size() / 2);
	start_frame = std::max<int64_t>(0, start_frame);
	if (static_cast<uint64_t>(start_frame) + buffer.size() > frame_count)
		start_frame = static_cast<int64_t>(frame_count - buffer.size());

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

int midi_from_frequency(double freq)
{
	return static_cast<int>(std::llround(69.0 + 12.0 * std::log2(freq / 440.0)));
}

int pitch_class_count_bool(const std::array<bool, 12> &pitch_classes)
{
	int count = 0;
	for (bool active : pitch_classes) {
		if (active)
			++count;
	}
	return count;
}

struct NoteAnnotation {
	double onset = 0.0;
	double frequency = 0.0;
	double duration = 0.0;
	int midi = 0;
};

struct TrackData {
	int number = 0;
	std::string instrument;
	std::string audio_path;
	std::vector<NoteAnnotation> notes;
};

int parse_track_number(const std::string &name, const char *prefix)
{
	if (!starts_with(name, prefix))
		return -1;
	std::size_t pos = std::strlen(prefix);
	int value = 0;
	bool any = false;
	while (pos < name.size() && name[pos] >= '0' && name[pos] <= '9') {
		any = true;
		value = value * 10 + (name[pos] - '0');
		++pos;
	}
	return any ? value : -1;
}

std::string parse_notes_instrument(const std::string &name)
{
	const std::size_t first = name.find('_');
	if (first == std::string::npos)
		return "";
	const std::size_t second = name.find('_', first + 1);
	if (second == std::string::npos)
		return "";
	const std::size_t third = name.find('_', second + 1);
	if (third == std::string::npos)
		return "";
	return name.substr(second + 1, third - second - 1);
}

bool read_notes(const std::string &path, std::vector<NoteAnnotation> &notes)
{
	std::ifstream file(path);
	if (!file)
		return false;

	double onset = 0.0;
	double frequency = 0.0;
	double duration = 0.0;
	while (file >> onset >> frequency >> duration) {
		if (frequency <= 0.0 || duration <= 0.0)
			continue;
		const int midi = midi_from_frequency(frequency);
		if (midi < mao::kFirstAnalyzedMidi || midi > mao::kLastAnalyzedMidi)
			continue;
		notes.push_back(NoteAnnotation{onset, frequency, duration, midi});
	}
	return !notes.empty();
}

std::array<bool, 12> annotated_pitch_classes(const std::vector<TrackData> &tracks)
{
	std::array<bool, 12> pitch_classes = {};
	for (const TrackData &track : tracks) {
		for (const NoteAnnotation &note : track.notes)
			pitch_classes[((note.midi % 12) + 12) % 12] = true;
	}
	return pitch_classes;
}

int best_transposed_pitch_class_overlap(const std::array<bool, 12> &source, const std::array<bool, 12> &target)
{
	int best = 0;
	for (int shift = 0; shift < 12; ++shift) {
		int overlap = 0;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			if (source[pitch_class] && target[(pitch_class + shift) % 12])
				++overlap;
		}
		best = std::max(best, overlap);
	}
	return best;
}

bool validate_score_matches_annotations(const std::string &score_path, const std::vector<TrackData> &tracks,
					std::string &reason)
{
	std::array<bool, 12> score_pitch_classes = {};
	int score_notes = 0;
	std::string midi_error;
	if (!read_midi_score_pitch_classes(score_path, score_pitch_classes, score_notes, midi_error)) {
		reason = "invalid Sco_*.mid score file: " + midi_error;
		return false;
	}

	const std::array<bool, 12> note_pitch_classes = annotated_pitch_classes(tracks);
	const int annotation_count = pitch_class_count_bool(note_pitch_classes);
	const int score_count = pitch_class_count_bool(score_pitch_classes);
	if (annotation_count == 0 || score_count == 0) {
		reason = "score/annotation pitch-class set is empty";
		return false;
	}

	const int overlap = best_transposed_pitch_class_overlap(note_pitch_classes, score_pitch_classes);
	if (overlap * 100 < annotation_count * 60) {
		reason = "Sco_*.mid pitch classes disagree with Notes_*.txt annotations";
		return false;
	}
	return true;
}

std::string source_hint_for_instrument(const std::string &instrument)
{
	if (instrument == "db" || instrument == "tba")
		return "bass track";
	if (instrument == "vn" || instrument == "va" || instrument == "vc")
		return "string track";
	if (instrument == "tpt" || instrument == "hn" || instrument == "tbn")
		return "brass track";
	return "wind track";
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
	return pitch_classes;
}

bool has_pitch_class(const std::array<bool, 12> &pitch_classes, int pitch_class)
{
	return pitch_classes[((pitch_class % 12) + 12) % 12];
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
	return has_chord_label(snapshot.keyboard_chord.label, label) ||
	       has_chord_label(snapshot.guitar_chord.label, label) || has_chord_label(snapshot.other_chord.label, label);
}

const NoteAnnotation *active_note_at(const TrackData &track, double time)
{
	const NoteAnnotation *best = nullptr;
	double best_margin = -1.0;
	for (const NoteAnnotation &note : track.notes) {
		const double edge = std::min(0.035, note.duration * 0.20);
		const double start = note.onset + edge;
		const double end = note.onset + note.duration - edge;
		if (time < start || time > end)
			continue;
		const double margin = std::min(time - note.onset, note.onset + note.duration - time);
		if (margin > best_margin) {
			best_margin = margin;
			best = &note;
		}
	}
	return best;
}

struct ActiveNote {
	std::size_t track_index = 0;
	int midi = 0;
};

struct ChordTemplate {
	const char *suffix = "";
	std::vector<int> intervals;
};

struct CandidateWindow {
	double time = 0.0;
	std::vector<ActiveNote> active;
	std::array<bool, 12> pitch_classes = {};
	std::vector<std::string> chord_labels;
	int chord_tone_count = 0;
	double score = 0.0;
};

struct MixRecallStats {
	int hits = 0;
	int expected = 0;
	int chord_hits = 0;
	int chord_checks = 0;
};

struct DatasetCoverageStats {
	int discovered_piece_dirs = 0;
	int loadable_pieces = 0;
	int unusable_pieces = 0;
	int pieces_without_candidates = 0;
	int selected_window_opportunities = 0;
	int mix_read_failures = 0;
	int mix_stream_failures = 0;
	int mix_sequence_failures = 0;
	int summed_mix_failures = 0;
	int summed_stream_failures = 0;
	int summed_sequence_failures = 0;
	int track_read_failures = 0;
};

struct WindowCompositionStats {
	int windows = 0;
	int active_track_sum = 0;
	int pitch_class_sum = 0;
	int min_active_tracks = 0;
	int max_active_tracks = 0;
	int min_pitch_classes = 0;
	int max_pitch_classes = 0;
};

struct RangeStats {
	int count = 0;
	int sum = 0;
	int min_value = 0;
	int max_value = 0;
};

int pitch_class_count(const std::array<bool, 12> &pitch_classes)
{
	int count = 0;
	for (bool active : pitch_classes) {
		if (active)
			++count;
	}
	return count;
}

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

void add_window_composition(WindowCompositionStats &stats, const CandidateWindow &candidate)
{
	const int active_tracks = static_cast<int>(candidate.active.size());
	const int pitch_classes = pitch_class_count(candidate.pitch_classes);

	++stats.windows;
	stats.active_track_sum += active_tracks;
	stats.pitch_class_sum += pitch_classes;
	if (stats.windows == 1) {
		stats.min_active_tracks = active_tracks;
		stats.max_active_tracks = active_tracks;
		stats.min_pitch_classes = pitch_classes;
		stats.max_pitch_classes = pitch_classes;
		return;
	}

	stats.min_active_tracks = std::min(stats.min_active_tracks, active_tracks);
	stats.max_active_tracks = std::max(stats.max_active_tracks, active_tracks);
	stats.min_pitch_classes = std::min(stats.min_pitch_classes, pitch_classes);
	stats.max_pitch_classes = std::max(stats.max_pitch_classes, pitch_classes);
}

void add_range_value(RangeStats &stats, int value)
{
	++stats.count;
	stats.sum += value;
	if (stats.count == 1) {
		stats.min_value = value;
		stats.max_value = value;
		return;
	}
	stats.min_value = std::min(stats.min_value, value);
	stats.max_value = std::max(stats.max_value, value);
}

std::string average_string(int sum, int count)
{
	char buffer[32] = {};
	std::snprintf(buffer, sizeof(buffer), "%.2f", count > 0 ? static_cast<double>(sum) / count : 0.0);
	return buffer;
}

std::string window_composition_summary(const WindowCompositionStats &stats)
{
	if (stats.windows == 0)
		return "active tracks min/avg/max 0/0.00/0, pitch classes min/avg/max 0/0.00/0";

	return "active tracks min/avg/max " + std::to_string(stats.min_active_tracks) + "/" +
	       average_string(stats.active_track_sum, stats.windows) + "/" +
	       std::to_string(stats.max_active_tracks) + ", pitch classes min/avg/max " +
	       std::to_string(stats.min_pitch_classes) + "/" +
	       average_string(stats.pitch_class_sum, stats.windows) + "/" +
	       std::to_string(stats.max_pitch_classes);
}

std::string range_summary(const RangeStats &stats, const char *label)
{
	if (stats.count == 0)
		return std::string(label) + " min/avg/max 0/0.00/0";

	return std::string(label) + " min/avg/max " + std::to_string(stats.min_value) + "/" +
	       average_string(stats.sum, stats.count) + "/" + std::to_string(stats.max_value);
}

CandidateWindow candidate_window_at(const std::vector<TrackData> &tracks, double time)
{
	CandidateWindow candidate;
	candidate.time = time;

	for (std::size_t track_index = 0; track_index < tracks.size(); ++track_index) {
		const NoteAnnotation *note = active_note_at(tracks[track_index], time);
		if (!note)
			continue;
		candidate.active.push_back(ActiveNote{track_index, note->midi});
		candidate.pitch_classes[((note->midi % 12) + 12) % 12] = true;
	}

	if (candidate.active.size() < 2)
		return candidate;

	candidate.chord_labels = expected_common_chord_labels(candidate.pitch_classes, candidate.chord_tone_count);
	candidate.score = static_cast<double>(candidate.active.size()) * 100.0 +
			  static_cast<double>(pitch_class_count(candidate.pitch_classes)) * 10.0 +
			  static_cast<double>(candidate.chord_tone_count) * 20.0 +
			  (candidate.chord_labels.empty() ? 0.0 : 50.0);
	return candidate;
}

void check_mix_recall(Runner &runner, const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate,
		      const std::string &context, MixRecallStats &stats, int min_recall_percent)
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
		if (chord_hit) {
			++stats.chord_hits;
		} else {
			std::fprintf(stderr,
				     "%s: chord opportunity `%s`, detected key `%s`, guitar `%s`, other `%s`\n",
				     context.c_str(), join_labels(candidate.chord_labels).c_str(),
				     snapshot.keyboard_chord.label,
				     snapshot.guitar_chord.label, snapshot.other_chord.label);
		}
	}
}

void require_chord_recall(Runner &runner, const MixRecallStats &stats, const std::string &context,
			  int min_chord_checks, int min_chord_recall_percent)
{
	runner.expect(stats.chord_checks >= min_chord_checks,
		      context + " chord coverage: expected at least " + std::to_string(min_chord_checks) +
			      " chord-checkable windows, got " + std::to_string(stats.chord_checks));
	if (stats.chord_checks < min_chord_checks)
		return;

	runner.expect(stats.chord_hits * 100 >= stats.chord_checks * min_chord_recall_percent,
		      context + " chord recall: expected >=" + std::to_string(min_chord_recall_percent) +
			      "%, got " + std::to_string(stats.chord_hits) + "/" +
			      std::to_string(stats.chord_checks));
}

std::vector<CandidateWindow> select_candidate_windows(const std::vector<TrackData> &tracks, int max_windows,
						      int min_active_tracks, int min_pitch_classes)
{
	std::vector<CandidateWindow> candidates;

	for (std::size_t seed_track = 0; seed_track < tracks.size(); ++seed_track) {
		for (const NoteAnnotation &seed_note : tracks[seed_track].notes) {
			const double time = seed_note.onset + seed_note.duration * 0.5;
			CandidateWindow candidate = candidate_window_at(tracks, time);
			if (static_cast<int>(candidate.active.size()) < min_active_tracks)
				continue;
			if (pitch_class_count(candidate.pitch_classes) < min_pitch_classes)
				continue;
			candidates.push_back(candidate);
		}
	}

	std::sort(candidates.begin(), candidates.end(), [](const CandidateWindow &a, const CandidateWindow &b) {
		if (a.score != b.score)
			return a.score > b.score;
		return a.time < b.time;
	});

	std::vector<CandidateWindow> selected;
	for (const CandidateWindow &candidate : candidates) {
		bool duplicate = false;
		for (const CandidateWindow &existing : selected) {
			if (std::abs(existing.time - candidate.time) < 0.20) {
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
		return a.time < b.time;
	});
	return selected;
}

struct PieceFiles {
	std::string dir;
	std::string mix_path;
	std::string score_path;
	std::vector<TrackData> tracks;
};

bool load_piece_files(const std::string &dir, PieceFiles &piece, bool require_score, std::string &reason)
{
	piece.dir = dir;
	std::map<int, std::string> audio_by_track;
	std::map<int, std::string> notes_by_track;
	std::map<int, std::string> instrument_by_track;

	for (const DirEntry &entry : list_dir(dir)) {
		if (entry.directory)
			continue;
		const std::string path = join_path(dir, entry.name);
		if (starts_with(entry.name, "AuMix_") && ends_with(entry.name, ".wav")) {
			piece.mix_path = path;
			continue;
		}
		if (starts_with(entry.name, "Sco_") && ends_with(entry.name, ".mid")) {
			piece.score_path = path;
			continue;
		}
		if (starts_with(entry.name, "AuSep_") && ends_with(entry.name, ".wav")) {
			const int track = parse_track_number(entry.name, "AuSep_");
			if (track > 0)
				audio_by_track[track] = path;
			continue;
		}
		if (starts_with(entry.name, "Notes_") && ends_with(entry.name, ".txt")) {
			const int track = parse_track_number(entry.name, "Notes_");
			if (track > 0) {
				notes_by_track[track] = path;
				instrument_by_track[track] = parse_notes_instrument(entry.name);
			}
		}
	}

	if (piece.mix_path.empty()) {
		reason = "missing AuMix_*.wav";
		return false;
	}
	if (require_score && piece.score_path.empty()) {
		reason = "missing official URMP Sco_*.mid score file";
		return false;
	}

	for (const auto &item : notes_by_track) {
		const int track = item.first;
		auto audio = audio_by_track.find(track);
		if (audio == audio_by_track.end())
			continue;
		TrackData track_data;
		track_data.number = track;
		track_data.instrument = instrument_by_track[track];
		track_data.audio_path = audio->second;
		if (!read_notes(item.second, track_data.notes))
			continue;
		piece.tracks.push_back(track_data);
	}

	std::sort(piece.tracks.begin(), piece.tracks.end(), [](const TrackData &a, const TrackData &b) {
		return a.number < b.number;
	});
	if (piece.tracks.size() < 2) {
		reason = "fewer than two tracks with matching AuSep_*.wav and readable Notes_*.txt";
		return false;
	}
	if (!piece.score_path.empty() && !validate_score_matches_annotations(piece.score_path, piece.tracks, reason))
		return false;
	reason.clear();
	return true;
}

mao::AnalysisSnapshot analyze_wav_window(const std::string &path, double time, const std::string &source_name,
					 bool &ok, std::string &error)
{
	mao_test::Buffer buffer = {};
	uint32_t sample_rate = 0;
	ok = read_wav_window(path, time, buffer, sample_rate, error);
	if (!ok)
		return {};

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	return engine.analyze(buffer.data(), buffer.size(), settings, source_name.c_str(), 0);
}

mao::AnalysisSnapshot analyze_confirmed_buffer_with_engine(mao::AnalysisEngine &engine,
							   const mao_test::Buffer &buffer, uint32_t sample_rate,
							   const std::string &source_name)
{
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, source_name.c_str(), 0);
	return snapshot;
}

mao::AnalysisSnapshot analyze_confirmed_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate,
					       const std::string &source_name)
{
	mao::AnalysisEngine engine;
	return analyze_confirmed_buffer_with_engine(engine, buffer, sample_rate, source_name);
}

mao::AnalysisSnapshot analyze_wav_confirmed_window(const std::string &path, double time,
						   const std::string &source_name, bool &ok,
						   std::string &error)
{
	mao_test::Buffer buffer = {};
	uint32_t sample_rate = 0;
	ok = read_wav_window(path, time, buffer, sample_rate, error);
	if (!ok)
		return {};

	return analyze_confirmed_buffer(buffer, sample_rate, source_name);
}

bool read_summed_track_window(const PieceFiles &piece, double time, mao_test::Buffer &summed,
			      uint32_t &sample_rate, std::string &error)
{
	summed = {};
	sample_rate = 0;

	for (const TrackData &track : piece.tracks) {
		mao_test::Buffer track_buffer = {};
		uint32_t track_sample_rate = 0;
		std::string track_error;
		if (!read_wav_window(track.audio_path, time, track_buffer, track_sample_rate, track_error)) {
			error = "track " + std::to_string(track.number) + " read failed: " + track_error;
			return false;
		}
		if (sample_rate == 0) {
			sample_rate = track_sample_rate;
		} else if (track_sample_rate != sample_rate) {
			error = "track " + std::to_string(track.number) + " sample-rate mismatch";
			return false;
		}
		for (std::size_t i = 0; i < summed.size(); ++i)
			summed[i] += track_buffer[i];
	}

	for (float &sample : summed)
		sample = std::clamp(sample, -1.0f, 1.0f);

	if (sample_rate == 0) {
		error = "no separated tracks";
		return false;
	}
	return true;
}

mao::AnalysisSnapshot analyze_summed_track_window(const PieceFiles &piece, double time, const std::string &source_name,
						  bool &ok, std::string &error)
{
	mao_test::Buffer summed = {};
	uint32_t sample_rate = 0;
	ok = read_summed_track_window(piece, time, summed, sample_rate, error);
	if (!ok)
		return {};

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	return engine.analyze(summed.data(), summed.size(), settings, source_name.c_str(), 0);
}

mao::AnalysisSnapshot analyze_summed_confirmed_window(const PieceFiles &piece, double time,
						      const std::string &source_name, bool &ok,
						      std::string &error)
{
	mao_test::Buffer summed = {};
	uint32_t sample_rate = 0;
	ok = read_summed_track_window(piece, time, summed, sample_rate, error);
	if (!ok)
		return {};

	return analyze_confirmed_buffer(summed, sample_rate, source_name);
}

std::string basename_of(const std::string &path)
{
	const std::size_t pos = path.find_last_of('/');
	return pos == std::string::npos ? path : path.substr(pos + 1);
}

bool has_official_urmp_piece_id(const std::string &piece_dir)
{
	const std::string name = basename_of(piece_dir);
	static constexpr const char *kOfficialIds[] = {
		"01_Jupiter",	    "02_Sonata",     "03_Dance",	 "04_Allegro",
		"05_Entertainer",   "06_Entertainer", "07_GString",	 "08_Spring",
		"09_Jesus",	    "10_March",      "11_Maria",	 "12_Spring",
		"13_Hark",	    "14_Waltz",      "15_Surprise",	 "16_Surprise",
		"17_Nocturne",	    "18_Nocturne",   "19_Pavane",	 "20_Pavane",
		"21_Rejouissance",  "22_Rejouissance", "23_Rejouissance", "24_Pirates",
		"25_Pirates",	    "26_King",	     "27_King",	 "28_Fugue",
		"29_Fugue",	    "30_Fugue",      "31_Slavonic",	 "32_Fugue",
		"33_Elise",	    "34_Fugue",      "35_Rondeau",	 "36_Rondeau",
		"37_Rondeau",	    "38_Jerusalem",  "39_Jerusalem",	 "40_Miserere",
		"41_Miserere",	    "42_Arioso",     "43_Chorale",	 "44_K515",
	};
	for (const char *id : kOfficialIds) {
		if (starts_with(name, id))
			return true;
	}
	return false;
}

std::string resolve_urmp_root()
{
	const char *root = std::getenv("MUSIC_ANALYZER_URMP_ROOT");
	if (root && *root)
		return root;

	const char *dataset_root = std::getenv("MUSIC_ANALYZER_DATASET_ROOT");
	if (!dataset_root || !*dataset_root)
		return "";

	const std::vector<std::string> candidates = {
		join_path(dataset_root, "URMP"),
		join_path(dataset_root, "urmp"),
		join_path(dataset_root, "University_of_Rochester_Multi-Modal_Music_Performance"),
	};
	for (const std::string &candidate : candidates) {
		if (is_directory(candidate))
			return candidate;
	}
	return dataset_root;
}

int resolve_max_windows_per_piece()
{
	const char *value = std::getenv("MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE");
	if (!value || !*value)
		return 12;

	const int parsed = std::atoi(value);
	return parsed > 0 ? parsed : 12;
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

bool env_truthy(const char *name)
{
	const char *value = std::getenv(name);
	return value && *value && std::strcmp(value, "0") != 0 && std::strcmp(value, "false") != 0 &&
	       std::strcmp(value, "FALSE") != 0;
}

bool is_generated_fixture_root(const std::string &root)
{
	return file_exists(join_path(root, ".music_analyzer_generated_urmp_fixture"));
}

std::string coverage_summary(const DatasetCoverageStats &coverage, int tested_pieces, int tested_windows,
			     const WindowCompositionStats &composition, const RangeStats &source_tracks)
{
	return "discovered " + std::to_string(coverage.discovered_piece_dirs) + " piece dirs, loadable " +
	       std::to_string(coverage.loadable_pieces) + ", unusable " +
	       std::to_string(coverage.unusable_pieces) + ", no-candidate " +
	       std::to_string(coverage.pieces_without_candidates) + ", selected " +
	       std::to_string(coverage.selected_window_opportunities) + " candidate windows, tested " +
	       std::to_string(tested_windows) + " windows across " + std::to_string(tested_pieces) +
	       " pieces, mix-read failures " + std::to_string(coverage.mix_read_failures) +
	       ", mix-stream failures " + std::to_string(coverage.mix_stream_failures) +
	       ", mix-sequence failures " + std::to_string(coverage.mix_sequence_failures) +
	       ", summed-mix failures " + std::to_string(coverage.summed_mix_failures) +
	       ", summed-stream failures " + std::to_string(coverage.summed_stream_failures) +
	       ", summed-sequence failures " + std::to_string(coverage.summed_sequence_failures) +
	       ", track-read failures " + std::to_string(coverage.track_read_failures) + ", " +
	       range_summary(source_tracks, "source tracks") + ", " + window_composition_summary(composition);
}

} // namespace

int main()
{
	const std::string root = resolve_urmp_root();
	if (root.empty()) {
		if (env_truthy("MUSIC_ANALYZER_URMP_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_urmp: real URMP dataset required; set MUSIC_ANALYZER_URMP_ROOT "
				     "or MUSIC_ANALYZER_DATASET_ROOT\n");
			return 1;
		}
		std::printf("analyzer_urmp: skipped, set MUSIC_ANALYZER_URMP_ROOT to a local URMP dataset\n");
		return 0;
	}
	if (!is_directory(root)) {
		std::fprintf(stderr, "analyzer_urmp: `%s` is not a directory\n", root.c_str());
		return 1;
	}
	const bool generated_fixture = is_generated_fixture_root(root);
	const bool allow_generated_fixture = env_truthy("MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE");
	if (generated_fixture && !allow_generated_fixture) {
		std::fprintf(stderr,
			     "analyzer_urmp: `%s` is a generated fixture, not the real URMP dataset; set "
			     "MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 only for fixture tests\n",
			     root.c_str());
		return 1;
	}
	const bool require_official_layout = !allow_generated_fixture;

	std::vector<std::string> piece_dirs;
	collect_piece_dirs(root, 4, piece_dirs);
	std::sort(piece_dirs.begin(), piece_dirs.end());
	const int max_windows_per_piece = resolve_max_windows_per_piece();
	const int required_pieces = resolve_positive_int_env("MUSIC_ANALYZER_URMP_REQUIRED_PIECES", 20);
	const int default_required_windows = std::min(required_pieces * 4, max_windows_per_piece * required_pieces);
	const int required_windows =
		resolve_positive_int_env("MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS", default_required_windows);
	const int min_window_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_URMP_MIN_WINDOW_RECALL_PERCENT", 50);
	const int min_track_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_URMP_MIN_TRACK_RECALL_PERCENT", 70);
	const int min_mix_recall_percent = resolve_percent_env("MUSIC_ANALYZER_URMP_MIN_MIX_RECALL_PERCENT", 55);
	const int min_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_URMP_MIN_CHORD_RECALL_PERCENT", 35);
	const int min_chord_checks = resolve_positive_int_env("MUSIC_ANALYZER_URMP_MIN_CHORD_CHECKS", 5);
	const int min_active_tracks_per_window =
		resolve_positive_int_env("MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW", 2);
	const int min_pitch_classes_per_window =
		resolve_positive_int_env("MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW", 2);

	Runner runner;
	DatasetCoverageStats coverage;
	coverage.discovered_piece_dirs = static_cast<int>(piece_dirs.size());
	int tested_pieces = 0;
	int track_hits = 0;
	int track_checks = 0;
	MixRecallStats provided_mix_stats;
	MixRecallStats summed_mix_stats;
	MixRecallStats provided_stream_stats;
	MixRecallStats summed_stream_stats;
	MixRecallStats provided_sequence_stats;
	MixRecallStats summed_sequence_stats;
	WindowCompositionStats composition_stats;
	RangeStats source_track_stats;
	int tested_windows = 0;

	for (const std::string &piece_dir : piece_dirs) {
		if (require_official_layout && !has_official_urmp_piece_id(piece_dir)) {
			++coverage.unusable_pieces;
			if (coverage.unusable_pieces <= 5) {
				std::fprintf(stderr, "analyzer_urmp: skipping %s: not an official URMP piece folder\n",
					     basename_of(piece_dir).c_str());
			}
			continue;
		}

		PieceFiles piece;
		std::string load_reason;
		if (!load_piece_files(piece_dir, piece, require_official_layout, load_reason)) {
			++coverage.unusable_pieces;
			if (coverage.unusable_pieces <= 5) {
				std::fprintf(stderr, "analyzer_urmp: skipping %s: %s\n",
					     basename_of(piece_dir).c_str(), load_reason.c_str());
			}
			continue;
		}
		++coverage.loadable_pieces;

		const std::vector<CandidateWindow> candidates = select_candidate_windows(
			piece.tracks, max_windows_per_piece, min_active_tracks_per_window,
			min_pitch_classes_per_window);
		if (candidates.empty()) {
			++coverage.pieces_without_candidates;
			if (coverage.pieces_without_candidates <= 5) {
				std::fprintf(stderr,
					     "analyzer_urmp: skipping %s: no overlapping window with %d+ active "
					     "tracks and %d+ pitch classes\n",
					     basename_of(piece_dir).c_str(), min_active_tracks_per_window,
					     min_pitch_classes_per_window);
			}
			continue;
		}
		coverage.selected_window_opportunities += static_cast<int>(candidates.size());

		mao::AnalysisEngine provided_sequence_engine;
		mao::AnalysisEngine summed_sequence_engine;
		int piece_windows = 0;
		for (const CandidateWindow &candidate : candidates) {
			std::string error;
			bool ok = false;
			const mao::AnalysisSnapshot mix_snapshot =
				analyze_wav_window(piece.mix_path, candidate.time, "URMP real full mix", ok, error);
			if (!ok) {
				++coverage.mix_read_failures;
				std::fprintf(stderr, "analyzer_urmp: skipping %s mix at %.3fs: %s\n",
					     basename_of(piece_dir).c_str(), candidate.time, error.c_str());
				continue;
			}

			++piece_windows;
			++tested_windows;
			add_window_composition(composition_stats, candidate);

			const std::string window_context =
				std::string("URMP ") + basename_of(piece_dir) + " at " + std::to_string(candidate.time) +
				"s";
			check_mix_recall(runner, mix_snapshot, candidate, window_context + " provided mix",
					 provided_mix_stats, min_window_recall_percent);

			mao_test::Buffer mix_sequence_buffer = {};
			uint32_t mix_sequence_sample_rate = 0;
			if (!read_wav_window(piece.mix_path, candidate.time, mix_sequence_buffer,
					     mix_sequence_sample_rate, error)) {
				++coverage.mix_sequence_failures;
				runner.expect(false, window_context + " provided mix sequence: " + error);
			} else {
				const mao::AnalysisSnapshot mix_sequence_snapshot =
					analyze_confirmed_buffer_with_engine(
						provided_sequence_engine, mix_sequence_buffer, mix_sequence_sample_rate,
						"URMP real full mix sequence");
				check_mix_recall(runner, mix_sequence_snapshot, candidate,
						 window_context + " provided mix sequence",
						 provided_sequence_stats, min_window_recall_percent);
			}

			const mao::AnalysisSnapshot mix_stream_snapshot = analyze_wav_confirmed_window(
				piece.mix_path, candidate.time, "URMP real full mix stream", ok, error);
			if (!ok) {
				++coverage.mix_stream_failures;
				runner.expect(false, window_context + " provided mix stream: " + error);
			} else {
				check_mix_recall(runner, mix_stream_snapshot,
						 candidate, window_context + " provided mix stream",
						 provided_stream_stats, min_window_recall_percent);
			}

			const mao::AnalysisSnapshot summed_snapshot = analyze_summed_track_window(
				piece, candidate.time, "URMP summed separated tracks", ok, error);
			if (!ok) {
				++coverage.summed_mix_failures;
				runner.expect(false, window_context + " summed separated tracks: " + error);
			} else {
				check_mix_recall(runner, summed_snapshot, candidate,
						 window_context + " summed separated tracks", summed_mix_stats,
						 min_window_recall_percent);
			}

			mao_test::Buffer summed_sequence_buffer = {};
			uint32_t summed_sequence_sample_rate = 0;
			if (!read_summed_track_window(piece, candidate.time, summed_sequence_buffer,
						      summed_sequence_sample_rate, error)) {
				++coverage.summed_sequence_failures;
				runner.expect(false, window_context + " summed separated tracks sequence: " + error);
			} else {
				const mao::AnalysisSnapshot summed_sequence_snapshot =
					analyze_confirmed_buffer_with_engine(
						summed_sequence_engine, summed_sequence_buffer, summed_sequence_sample_rate,
						"URMP summed separated tracks sequence");
				check_mix_recall(runner, summed_sequence_snapshot, candidate,
						 window_context + " summed separated tracks sequence",
						 summed_sequence_stats, min_window_recall_percent);
			}

			const mao::AnalysisSnapshot summed_stream_snapshot = analyze_summed_confirmed_window(
				piece, candidate.time, "URMP summed separated tracks stream", ok, error);
			if (!ok) {
				++coverage.summed_stream_failures;
				runner.expect(false, window_context + " summed separated tracks stream: " + error);
			} else {
				check_mix_recall(runner, summed_stream_snapshot, candidate,
						 window_context + " summed separated tracks stream",
						 summed_stream_stats, min_window_recall_percent);
			}

			for (const ActiveNote &active : candidate.active) {
				const TrackData &track = piece.tracks[active.track_index];
				const std::string source = source_hint_for_instrument(track.instrument);
				const mao::AnalysisSnapshot track_snapshot =
					analyze_wav_window(track.audio_path, candidate.time, source, ok, error);
				if (!ok) {
					++coverage.track_read_failures;
					std::fprintf(stderr, "analyzer_urmp: skipping %s track %d at %.3fs: %s\n",
						     basename_of(piece_dir).c_str(), track.number, candidate.time,
						     error.c_str());
					continue;
				}

				const int pitch_class = ((active.midi % 12) + 12) % 12;
				const bool hit = has_pitch_class(detected_pitch_classes(track_snapshot), pitch_class);
				++track_checks;
				if (hit) {
					++track_hits;
				} else {
					std::fprintf(stderr,
						     "URMP track %s #%d %s at %.3fs: expected %s, detected bass `%s`, "
						     "key `%s`, guitar `%s`, vocal `%s`, other `%s`\n",
						     basename_of(piece_dir).c_str(), track.number,
						     track.instrument.c_str(), candidate.time,
						     mao_test::note_label(active.midi).c_str(),
						     track_snapshot.bass.label, track_snapshot.keyboard.label,
						     track_snapshot.guitar.label, track_snapshot.vocal.label,
						     track_snapshot.other.label);
				}
			}
		}

		if (piece_windows > 0) {
			add_range_value(source_track_stats, static_cast<int>(piece.tracks.size()));
			++tested_pieces;
		}
	}

	if (tested_pieces == 0) {
		std::fprintf(stderr, "analyzer_urmp: no usable URMP pieces found under `%s`\n", root.c_str());
		std::fprintf(stderr, "analyzer_urmp: coverage: %s\n",
			     coverage_summary(coverage, tested_pieces, tested_windows, composition_stats,
					      source_track_stats)
				     .c_str());
		return 1;
	}

	runner.expect(tested_pieces >= required_pieces,
		      "URMP real-audio coverage: expected at least " + std::to_string(required_pieces) +
			      " usable pieces, got " +
			      std::to_string(tested_pieces));
	runner.expect(tested_windows >= required_windows,
		      "URMP real-audio coverage: expected at least " + std::to_string(required_windows) +
			      " tested windows, got " +
			      std::to_string(tested_windows));
	runner.expect(composition_stats.windows == tested_windows,
		      "URMP window composition: expected composition stats for every tested window, got " +
			      std::to_string(composition_stats.windows) + "/" + std::to_string(tested_windows));
	runner.expect(source_track_stats.count == tested_pieces,
		      "URMP source-track composition: expected source track stats for every tested piece, got " +
			      std::to_string(source_track_stats.count) + "/" + std::to_string(tested_pieces));
	runner.expect(composition_stats.min_active_tracks >= min_active_tracks_per_window,
		      "URMP window composition: expected every tested window to contain at least " +
			      std::to_string(min_active_tracks_per_window) + " active tracks, got min " +
			      std::to_string(composition_stats.min_active_tracks));
	runner.expect(composition_stats.min_pitch_classes >= min_pitch_classes_per_window,
		      "URMP window composition: expected every tested window to contain at least " +
			      std::to_string(min_pitch_classes_per_window) + " pitch classes, got min " +
			      std::to_string(composition_stats.min_pitch_classes));
	runner.expect(track_checks > 0 && track_hits * 100 >= track_checks * min_track_recall_percent,
		      "URMP separated-track recall: expected >=" + std::to_string(min_track_recall_percent) +
			      "%, got " + std::to_string(track_hits) + "/" +
			      std::to_string(track_checks));
	runner.expect(provided_mix_stats.expected > 0 &&
			      provided_mix_stats.hits * 100 >= provided_mix_stats.expected * min_mix_recall_percent,
		      "URMP provided full-mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(provided_mix_stats.hits) + "/" +
			      std::to_string(provided_mix_stats.expected));
	runner.expect(summed_mix_stats.expected > 0 &&
			      summed_mix_stats.hits * 100 >= summed_mix_stats.expected * min_mix_recall_percent,
		      "URMP summed separated-track mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(summed_mix_stats.hits) + "/" +
			      std::to_string(summed_mix_stats.expected));
	runner.expect(provided_stream_stats.expected > 0 &&
			      provided_stream_stats.hits * 100 >=
				      provided_stream_stats.expected * min_mix_recall_percent,
		      "URMP streaming provided full-mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(provided_stream_stats.hits) + "/" +
			      std::to_string(provided_stream_stats.expected));
	runner.expect(summed_stream_stats.expected > 0 &&
			      summed_stream_stats.hits * 100 >=
				      summed_stream_stats.expected * min_mix_recall_percent,
		      "URMP streaming summed separated-track mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(summed_stream_stats.hits) + "/" +
			      std::to_string(summed_stream_stats.expected));
	runner.expect(provided_sequence_stats.expected > 0 &&
			      provided_sequence_stats.hits * 100 >=
				      provided_sequence_stats.expected * min_mix_recall_percent,
		      "URMP stateful provided full-mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(provided_sequence_stats.hits) + "/" +
			      std::to_string(provided_sequence_stats.expected));
	runner.expect(summed_sequence_stats.expected > 0 &&
			      summed_sequence_stats.hits * 100 >=
				      summed_sequence_stats.expected * min_mix_recall_percent,
		      "URMP stateful summed separated-track mix pitch-class recall: expected >=" +
			      std::to_string(min_mix_recall_percent) + "%, got " +
			      std::to_string(summed_sequence_stats.hits) + "/" +
			      std::to_string(summed_sequence_stats.expected));
	require_chord_recall(runner, provided_mix_stats, "URMP provided full-mix", min_chord_checks,
			     min_chord_recall_percent);
	require_chord_recall(runner, summed_mix_stats, "URMP summed separated-track mix", min_chord_checks,
			     min_chord_recall_percent);
	require_chord_recall(runner, provided_stream_stats, "URMP streaming provided full-mix", min_chord_checks,
			     min_chord_recall_percent);
	require_chord_recall(runner, summed_stream_stats, "URMP streaming summed separated-track mix",
			     min_chord_checks, min_chord_recall_percent);
	require_chord_recall(runner, provided_sequence_stats, "URMP stateful provided full-mix",
			     min_chord_checks, min_chord_recall_percent);
	require_chord_recall(runner, summed_sequence_stats, "URMP stateful summed separated-track mix",
			     min_chord_checks, min_chord_recall_percent);

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_urmp: %d/%d checks failed (%d pieces, %d windows, %d track hits/%d, "
			     "%d provided mix hits/%d, %d summed mix hits/%d, %d provided stream hits/%d, "
			     "%d summed stream hits/%d, %d provided sequence hits/%d, %d summed sequence hits/%d, "
			     "%d provided chord hits/%d, %d summed chord hits/%d, %d provided stream chord hits/%d, "
			     "%d summed stream chord hits/%d, %d provided sequence chord hits/%d, "
			     "%d summed sequence chord hits/%d)\n",
			     runner.failures, runner.checks, tested_pieces, tested_windows, track_hits,
			     track_checks, provided_mix_stats.hits, provided_mix_stats.expected, summed_mix_stats.hits,
			     summed_mix_stats.expected, provided_stream_stats.hits, provided_stream_stats.expected,
			     summed_stream_stats.hits, summed_stream_stats.expected, provided_sequence_stats.hits,
			     provided_sequence_stats.expected, summed_sequence_stats.hits,
			     summed_sequence_stats.expected, provided_mix_stats.chord_hits,
			     provided_mix_stats.chord_checks, summed_mix_stats.chord_hits, summed_mix_stats.chord_checks,
			     provided_stream_stats.chord_hits, provided_stream_stats.chord_checks,
			     summed_stream_stats.chord_hits, summed_stream_stats.chord_checks,
			     provided_sequence_stats.chord_hits, provided_sequence_stats.chord_checks,
			     summed_sequence_stats.chord_hits, summed_sequence_stats.chord_checks);
		std::fprintf(stderr, "analyzer_urmp: coverage: %s\n",
			     coverage_summary(coverage, tested_pieces, tested_windows, composition_stats,
					      source_track_stats)
				     .c_str());
		return 1;
	}

	std::printf("analyzer_urmp: %d checks passed (%d pieces, %d windows, %d track hits/%d, "
		    "%d provided mix hits/%d, %d summed mix hits/%d, %d provided stream hits/%d, "
		    "%d summed stream hits/%d, %d provided sequence hits/%d, %d summed sequence hits/%d, "
		    "%d provided chord hits/%d, %d summed chord hits/%d, %d provided stream chord hits/%d, "
		    "%d summed stream chord hits/%d, %d provided sequence chord hits/%d, "
		    "%d summed sequence chord hits/%d)\n",
		    runner.checks, tested_pieces, tested_windows, track_hits, track_checks,
		    provided_mix_stats.hits, provided_mix_stats.expected, summed_mix_stats.hits,
		    summed_mix_stats.expected, provided_stream_stats.hits, provided_stream_stats.expected,
		    summed_stream_stats.hits, summed_stream_stats.expected, provided_sequence_stats.hits,
		    provided_sequence_stats.expected, summed_sequence_stats.hits, summed_sequence_stats.expected,
		    provided_mix_stats.chord_hits, provided_mix_stats.chord_checks, summed_mix_stats.chord_hits,
		    summed_mix_stats.chord_checks, provided_stream_stats.chord_hits,
		    provided_stream_stats.chord_checks, summed_stream_stats.chord_hits,
		    summed_stream_stats.chord_checks, provided_sequence_stats.chord_hits,
		    provided_sequence_stats.chord_checks, summed_sequence_stats.chord_hits,
		    summed_sequence_stats.chord_checks);
	std::printf("analyzer_urmp: coverage: %s\n",
		    coverage_summary(coverage, tested_pieces, tested_windows, composition_stats, source_track_stats)
			    .c_str());
	return 0;
}
