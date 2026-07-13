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
	int summed_mix_failures = 0;
	int track_read_failures = 0;
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

std::vector<CandidateWindow> select_candidate_windows(const std::vector<TrackData> &tracks, int max_windows)
{
	std::vector<CandidateWindow> candidates;

	for (std::size_t seed_track = 0; seed_track < tracks.size(); ++seed_track) {
		for (const NoteAnnotation &seed_note : tracks[seed_track].notes) {
			const double time = seed_note.onset + seed_note.duration * 0.5;
			CandidateWindow candidate = candidate_window_at(tracks, time);
			if (candidate.active.size() < 2)
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

mao::AnalysisSnapshot analyze_summed_track_window(const PieceFiles &piece, double time, const std::string &source_name,
						  bool &ok, std::string &error)
{
	mao_test::Buffer summed = {};
	uint32_t sample_rate = 0;

	for (const TrackData &track : piece.tracks) {
		mao_test::Buffer track_buffer = {};
		uint32_t track_sample_rate = 0;
		std::string track_error;
		if (!read_wav_window(track.audio_path, time, track_buffer, track_sample_rate, track_error)) {
			error = "track " + std::to_string(track.number) + " read failed: " + track_error;
			ok = false;
			return {};
		}
		if (sample_rate == 0) {
			sample_rate = track_sample_rate;
		} else if (track_sample_rate != sample_rate) {
			error = "track " + std::to_string(track.number) + " sample-rate mismatch";
			ok = false;
			return {};
		}
		for (std::size_t i = 0; i < summed.size(); ++i)
			summed[i] += track_buffer[i];
	}

	for (float &sample : summed)
		sample = std::clamp(sample, -1.0f, 1.0f);

	ok = sample_rate != 0;
	if (!ok) {
		error = "no separated tracks";
		return {};
	}

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	return engine.analyze(summed.data(), summed.size(), settings, source_name.c_str(), 0);
}

std::string basename_of(const std::string &path)
{
	const std::size_t pos = path.find_last_of('/');
	return pos == std::string::npos ? path : path.substr(pos + 1);
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

std::string coverage_summary(const DatasetCoverageStats &coverage, int tested_pieces, int tested_windows)
{
	return "discovered " + std::to_string(coverage.discovered_piece_dirs) + " piece dirs, loadable " +
	       std::to_string(coverage.loadable_pieces) + ", unusable " +
	       std::to_string(coverage.unusable_pieces) + ", no-candidate " +
	       std::to_string(coverage.pieces_without_candidates) + ", selected " +
	       std::to_string(coverage.selected_window_opportunities) + " candidate windows, tested " +
	       std::to_string(tested_windows) + " windows across " + std::to_string(tested_pieces) +
	       " pieces, mix-read failures " + std::to_string(coverage.mix_read_failures) +
	       ", summed-mix failures " + std::to_string(coverage.summed_mix_failures) +
	       ", track-read failures " + std::to_string(coverage.track_read_failures);
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

	Runner runner;
	DatasetCoverageStats coverage;
	coverage.discovered_piece_dirs = static_cast<int>(piece_dirs.size());
	int tested_pieces = 0;
	int track_hits = 0;
	int track_checks = 0;
	MixRecallStats provided_mix_stats;
	MixRecallStats summed_mix_stats;
	int tested_windows = 0;

	for (const std::string &piece_dir : piece_dirs) {
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

		const std::vector<CandidateWindow> candidates =
			select_candidate_windows(piece.tracks, max_windows_per_piece);
		if (candidates.empty()) {
			++coverage.pieces_without_candidates;
			if (coverage.pieces_without_candidates <= 5) {
				std::fprintf(stderr, "analyzer_urmp: skipping %s: no overlapping multi-track note window\n",
					     basename_of(piece_dir).c_str());
			}
			continue;
		}
		coverage.selected_window_opportunities += static_cast<int>(candidates.size());

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

			const std::string window_context =
				std::string("URMP ") + basename_of(piece_dir) + " at " + std::to_string(candidate.time) +
				"s";
			check_mix_recall(runner, mix_snapshot, candidate, window_context + " provided mix",
					 provided_mix_stats, 50);

			const mao::AnalysisSnapshot summed_snapshot = analyze_summed_track_window(
				piece, candidate.time, "URMP summed separated tracks", ok, error);
			if (!ok) {
				++coverage.summed_mix_failures;
				runner.expect(false, window_context + " summed separated tracks: " + error);
			} else {
				check_mix_recall(runner, summed_snapshot, candidate,
						 window_context + " summed separated tracks", summed_mix_stats, 50);
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

		if (piece_windows > 0)
			++tested_pieces;
	}

	if (tested_pieces == 0) {
		std::fprintf(stderr, "analyzer_urmp: no usable URMP pieces found under `%s`\n", root.c_str());
		std::fprintf(stderr, "analyzer_urmp: coverage: %s\n",
			     coverage_summary(coverage, tested_pieces, tested_windows).c_str());
		return 1;
	}

	runner.expect(tested_pieces >= 20,
		      "URMP real-audio coverage: expected at least 20 usable pieces, got " +
			      std::to_string(tested_pieces));
	const int min_required_windows = std::min(80, max_windows_per_piece * 20);
	runner.expect(tested_windows >= min_required_windows,
		      "URMP real-audio coverage: expected at least " + std::to_string(min_required_windows) +
			      " tested windows, got " +
			      std::to_string(tested_windows));
	runner.expect(track_checks > 0 && track_hits * 100 >= track_checks * 70,
		      "URMP separated-track recall: expected >=70%, got " + std::to_string(track_hits) + "/" +
			      std::to_string(track_checks));
	runner.expect(provided_mix_stats.expected > 0 &&
			      provided_mix_stats.hits * 100 >= provided_mix_stats.expected * 55,
		      "URMP provided full-mix pitch-class recall: expected >=55%, got " +
			      std::to_string(provided_mix_stats.hits) + "/" +
			      std::to_string(provided_mix_stats.expected));
	runner.expect(summed_mix_stats.expected > 0 && summed_mix_stats.hits * 100 >= summed_mix_stats.expected * 55,
		      "URMP summed separated-track mix pitch-class recall: expected >=55%, got " +
			      std::to_string(summed_mix_stats.hits) + "/" +
			      std::to_string(summed_mix_stats.expected));
	if (provided_mix_stats.chord_checks >= 5) {
		runner.expect(provided_mix_stats.chord_hits * 100 >= provided_mix_stats.chord_checks * 35,
			      "URMP provided full-mix chord recall: expected >=35%, got " +
				      std::to_string(provided_mix_stats.chord_hits) + "/" +
				      std::to_string(provided_mix_stats.chord_checks));
	}
	if (summed_mix_stats.chord_checks >= 5) {
		runner.expect(summed_mix_stats.chord_hits * 100 >= summed_mix_stats.chord_checks * 35,
			      "URMP summed separated-track mix chord recall: expected >=35%, got " +
				      std::to_string(summed_mix_stats.chord_hits) + "/" +
				      std::to_string(summed_mix_stats.chord_checks));
	}

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_urmp: %d/%d checks failed (%d pieces, %d windows, %d track hits/%d, "
			     "%d provided mix hits/%d, %d summed mix hits/%d, %d provided chord hits/%d, "
			     "%d summed chord hits/%d)\n",
			     runner.failures, runner.checks, tested_pieces, tested_windows, track_hits,
			     track_checks, provided_mix_stats.hits, provided_mix_stats.expected, summed_mix_stats.hits,
			     summed_mix_stats.expected, provided_mix_stats.chord_hits,
			     provided_mix_stats.chord_checks, summed_mix_stats.chord_hits,
			     summed_mix_stats.chord_checks);
		std::fprintf(stderr, "analyzer_urmp: coverage: %s\n",
			     coverage_summary(coverage, tested_pieces, tested_windows).c_str());
		return 1;
	}

	std::printf("analyzer_urmp: %d checks passed (%d pieces, %d windows, %d track hits/%d, "
		    "%d provided mix hits/%d, %d summed mix hits/%d, %d provided chord hits/%d, "
		    "%d summed chord hits/%d)\n",
		    runner.checks, tested_pieces, tested_windows, track_hits, track_checks,
		    provided_mix_stats.hits, provided_mix_stats.expected, summed_mix_stats.hits,
		    summed_mix_stats.expected, provided_mix_stats.chord_hits, provided_mix_stats.chord_checks,
		    summed_mix_stats.chord_hits, summed_mix_stats.chord_checks);
	std::printf("analyzer_urmp: coverage: %s\n", coverage_summary(coverage, tested_pieces, tested_windows).c_str());
	return 0;
}
