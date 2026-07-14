#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
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
	return (static_cast<uint32_t>(bytes[offset]) << 24) |
	       (static_cast<uint32_t>(bytes[offset + 1]) << 16) |
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

bool read_midi_var_len(const std::vector<unsigned char> &bytes, std::size_t end, std::size_t &pos,
		       uint32_t &value, std::string &error)
{
	value = 0;
	for (int i = 0; i < 4; ++i) {
		if (pos >= end) {
			error = "truncated MIDI variable-length value";
			return false;
		}
		const unsigned char byte = bytes[pos++];
		value = (value << 7) | (byte & 0x7f);
		if ((byte & 0x80) == 0)
			return true;
	}
	error = "invalid MIDI variable-length value";
	return false;
}

int midi_event_data_length(unsigned char status)
{
	const unsigned char event_type = status & 0xf0;
	if (event_type == 0xc0 || event_type == 0xd0)
		return 1;
	if (event_type == 0x80 || event_type == 0x90 || event_type == 0xa0 || event_type == 0xb0 ||
	    event_type == 0xe0)
		return 2;
	return -1;
}

struct RawMidiNote {
	uint64_t start_tick = 0;
	uint64_t end_tick = 0;
	int part = 0;
	int midi = 0;
};

struct TempoEvent {
	uint64_t tick = 0;
	int microseconds_per_quarter = 500000;
};

struct TempoPoint {
	uint64_t tick = 0;
	double seconds = 0.0;
	int microseconds_per_quarter = 500000;
};

struct ActiveMidiNote {
	uint64_t start_tick = 0;
	int part = 0;
};

std::vector<TempoPoint> build_tempo_points(std::vector<TempoEvent> tempo_events, int division)
{
	std::sort(tempo_events.begin(), tempo_events.end(), [](const TempoEvent &a, const TempoEvent &b) {
		if (a.tick != b.tick)
			return a.tick < b.tick;
		return a.microseconds_per_quarter < b.microseconds_per_quarter;
	});

	std::vector<TempoPoint> points;
	points.push_back(TempoPoint{0, 0.0, 500000});
	uint64_t current_tick = 0;
	double current_seconds = 0.0;
	int current_tempo = 500000;

	for (const TempoEvent &event : tempo_events) {
		if (event.tick < current_tick)
			continue;
		current_seconds += static_cast<double>(event.tick - current_tick) *
				   static_cast<double>(current_tempo) /
				   (static_cast<double>(division) * 1000000.0);
		current_tick = event.tick;
		current_tempo = event.microseconds_per_quarter;
		if (!points.empty() && points.back().tick == current_tick) {
			points.back().seconds = current_seconds;
			points.back().microseconds_per_quarter = current_tempo;
		} else {
			points.push_back(TempoPoint{current_tick, current_seconds, current_tempo});
		}
	}
	return points;
}

double tick_to_seconds(const std::vector<TempoPoint> &points, uint64_t tick, int division)
{
	const TempoPoint *point = &points.front();
	for (const TempoPoint &candidate : points) {
		if (candidate.tick > tick)
			break;
		point = &candidate;
	}
	return point->seconds + static_cast<double>(tick - point->tick) *
				 static_cast<double>(point->microseconds_per_quarter) /
				 (static_cast<double>(division) * 1000000.0);
}

struct NoteAnnotation {
	double start_seconds = 0.0;
	double end_seconds = 0.0;
	int instrument = 0;
	int midi = 0;
};

bool read_multtipop_midi(const std::string &path, std::vector<NoteAnnotation> &notes, std::string &error)
{
	std::vector<unsigned char> bytes;
	if (!read_file_bytes(path, bytes, error))
		return false;
	if (bytes.size() < 14 || std::memcmp(bytes.data(), "MThd", 4) != 0) {
		error = "not a MIDI file";
		return false;
	}

	const uint32_t header_len = read_be_u32(bytes, 4);
	if (header_len < 6 || 8 + header_len > bytes.size()) {
		error = "invalid MIDI header";
		return false;
	}
	const uint16_t track_count = read_be_u16(bytes, 10);
	const uint16_t division_raw = read_be_u16(bytes, 12);
	if (division_raw & 0x8000) {
		error = "SMPTE MIDI timing is not supported";
		return false;
	}
	const int division = static_cast<int>(division_raw);
	if (division <= 0) {
		error = "invalid MIDI division";
		return false;
	}

	std::size_t pos = 8 + header_len;
	std::vector<RawMidiNote> raw_notes;
	std::vector<TempoEvent> tempo_events;
	int parsed_tracks = 0;

	while (pos + 8 <= bytes.size() && parsed_tracks < static_cast<int>(track_count)) {
		const bool is_track = std::memcmp(bytes.data() + pos, "MTrk", 4) == 0;
		const uint32_t chunk_len = read_be_u32(bytes, pos + 4);
		pos += 8;
		if (pos + chunk_len > bytes.size()) {
			error = "truncated MIDI chunk";
			return false;
		}
		const std::size_t chunk_end = pos + chunk_len;
		if (!is_track) {
			pos = chunk_end;
			continue;
		}

		const int track_index = parsed_tracks++;
		uint64_t tick = 0;
		unsigned char running_status = 0;
		std::map<int, ActiveMidiNote> active_notes;

		while (pos < chunk_end) {
			uint32_t delta = 0;
			if (!read_midi_var_len(bytes, chunk_end, pos, delta, error))
				return false;
			tick += delta;
			if (pos >= chunk_end) {
				error = "truncated MIDI event";
				return false;
			}

			unsigned char status = bytes[pos];
			if (status & 0x80) {
				++pos;
				if (status < 0xf0)
					running_status = status;
			} else {
				if (!running_status) {
					error = "MIDI running status without previous status";
					return false;
				}
				status = running_status;
			}

			if (status == 0xff) {
				if (pos >= chunk_end) {
					error = "truncated MIDI meta event";
					return false;
				}
				const unsigned char meta_type = bytes[pos++];
				uint32_t length = 0;
				if (!read_midi_var_len(bytes, chunk_end, pos, length, error))
					return false;
				if (pos + length > chunk_end) {
					error = "truncated MIDI meta payload";
					return false;
				}
				if (meta_type == 0x51 && length == 3) {
					const int tempo = (static_cast<int>(bytes[pos]) << 16) |
							  (static_cast<int>(bytes[pos + 1]) << 8) |
							  static_cast<int>(bytes[pos + 2]);
					tempo_events.push_back(TempoEvent{tick, tempo});
				}
				pos += length;
				continue;
			}

			if (status == 0xf0 || status == 0xf7) {
				uint32_t length = 0;
				if (!read_midi_var_len(bytes, chunk_end, pos, length, error))
					return false;
				if (pos + length > chunk_end) {
					error = "truncated MIDI sysex payload";
					return false;
				}
				pos += length;
				continue;
			}

			const int data_len = midi_event_data_length(status);
			if (data_len < 0 || pos + static_cast<std::size_t>(data_len) > chunk_end) {
				error = "truncated or unsupported MIDI channel event";
				return false;
			}
			const unsigned char first = bytes[pos];
			const unsigned char second = data_len > 1 ? bytes[pos + 1] : 0;
			pos += static_cast<std::size_t>(data_len);

			const int channel = status & 0x0f;
			const int key = channel * 128 + first;
			const int part = track_index * 16 + channel;
			const unsigned char event_type = status & 0xf0;
			if (event_type == 0x90 && second > 0) {
				active_notes[key] = ActiveMidiNote{tick, part};
			} else if (event_type == 0x80 || (event_type == 0x90 && second == 0)) {
				const auto found = active_notes.find(key);
				if (found == active_notes.end())
					continue;
				if (tick > found->second.start_tick) {
					raw_notes.push_back(RawMidiNote{found->second.start_tick, tick,
									found->second.part, static_cast<int>(first)});
				}
				active_notes.erase(found);
			}
		}
		pos = chunk_end;
	}

	if (raw_notes.empty()) {
		error = "no MIDI notes";
		return false;
	}

	const std::vector<TempoPoint> tempo_points = build_tempo_points(tempo_events, division);
	for (const RawMidiNote &raw : raw_notes) {
		if (raw.midi < mao::kFirstAnalyzedMidi || raw.midi > mao::kLastAnalyzedMidi)
			continue;
		const double start = tick_to_seconds(tempo_points, raw.start_tick, division);
		const double end = tick_to_seconds(tempo_points, raw.end_tick, division);
		if (end - start < 0.035)
			continue;
		notes.push_back(NoteAnnotation{start, end, raw.part, raw.midi});
	}

	if (notes.empty()) {
		error = "no usable MIDI notes";
		return false;
	}
	std::sort(notes.begin(), notes.end(), [](const NoteAnnotation &a, const NoteAnnotation &b) {
		if (a.start_seconds != b.start_seconds)
			return a.start_seconds < b.start_seconds;
		return a.midi < b.midi;
	});
	return true;
}

std::string basename(const std::string &path)
{
	const std::size_t pos = path.find_last_of('/');
	return pos == std::string::npos ? path : path.substr(pos + 1);
}

std::string find_audio_path(const std::string &segment_dir, const std::string &split, const std::string &id)
{
	const std::vector<std::string> names = {"audio.wav", "segment.wav", id + ".wav"};
	for (const std::string &name : names) {
		const std::string candidate = join_path(segment_dir, name);
		if (file_exists(candidate))
			return candidate;
	}

	const char *audio_root_env = std::getenv("MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT");
	if (!audio_root_env || !*audio_root_env)
		return "";

	const std::string audio_root = audio_root_env;
	const std::vector<std::string> roots = {
		audio_root,
		join_path(audio_root, id),
		join_path(join_path(audio_root, split), id),
	};
	for (const std::string &root : roots) {
		for (const std::string &name : names) {
			const std::string candidate = join_path(root, name);
			if (file_exists(candidate))
				return candidate;
		}
	}
	return "";
}

struct Segment {
	std::string id;
	std::string split;
	std::string audio_path;
	std::string midi_path;
	uint32_t sample_rate = 0;
	uint64_t frame_count = 0;
	std::vector<NoteAnnotation> notes;
};

bool load_segment(const std::string &split, const std::string &segment_dir, Segment &segment,
		  std::string &error)
{
	const std::string id = basename(segment_dir);
	const std::string midi_path = join_path(segment_dir, "aligned.mid");
	if (!file_exists(midi_path)) {
		error = "missing aligned.mid";
		return false;
	}

	const std::string audio_path = find_audio_path(segment_dir, split, id);
	if (audio_path.empty()) {
		error = "missing local WAV audio segment";
		return false;
	}

	WavFormat format;
	if (!read_wav_format(audio_path, format, error))
		return false;

	std::vector<NoteAnnotation> notes;
	if (!read_multtipop_midi(midi_path, notes, error))
		return false;

	segment.id = id;
	segment.split = split;
	segment.audio_path = audio_path;
	segment.midi_path = midi_path;
	segment.sample_rate = format.sample_rate;
	segment.frame_count = format.frame_count;
	segment.notes = std::move(notes);
	return true;
}

bool has_multtipop_layout(const std::string &root)
{
	return is_directory(join_path(root, "dev")) || is_directory(join_path(root, "test"));
}

std::string resolve_multtipop_layout(const std::string &root)
{
	if (has_multtipop_layout(root))
		return root;

	const std::vector<std::string> candidates = {
		join_path(root, "multtipop"),
		join_path(root, "MulTTiPop"),
		join_path(root, "gclef-cmu-multtipop"),
		join_path(root, "gclef-cmu_multtipop"),
		join_path(root, "gclef-cmu/multtipop"),
	};
	for (const std::string &candidate : candidates) {
		if (has_multtipop_layout(candidate))
			return candidate;
	}
	return root;
}

std::string resolve_multtipop_root()
{
	const char *root = std::getenv("MUSIC_ANALYZER_MULTTIPOP_ROOT");
	if (root && *root)
		return resolve_multtipop_layout(root);

	root = std::getenv("MULTTIPOP_PATH");
	if (root && *root)
		return resolve_multtipop_layout(root);

	const char *dataset_root = std::getenv("MUSIC_ANALYZER_DATASET_ROOT");
	if (!dataset_root || !*dataset_root)
		return "";

	const std::vector<std::string> candidates = {
		join_path(dataset_root, "MulTTiPop"),
		join_path(dataset_root, "multtipop"),
		join_path(dataset_root, "gclef-cmu-multtipop"),
		join_path(dataset_root, "gclef-cmu_multtipop"),
		join_path(dataset_root, "gclef-cmu/multtipop"),
	};
	for (const std::string &candidate : candidates) {
		if (has_multtipop_layout(candidate))
			return candidate;
	}
	return resolve_multtipop_layout(dataset_root);
}

void collect_split_segments(const std::string &root, const char *split, std::vector<Segment> &segments,
			    int &missing_audio_or_unusable)
{
	const std::string split_path = join_path(root, split);
	if (!is_directory(split_path))
		return;

	for (const DirEntry &entry : list_dir(split_path)) {
		if (!entry.directory)
			continue;
		Segment segment;
		std::string error;
		const std::string segment_dir = join_path(split_path, entry.name);
		if (!load_segment(split, segment_dir, segment, error)) {
			++missing_audio_or_unusable;
			if (missing_audio_or_unusable <= 5)
				std::fprintf(stderr, "analyzer_multtipop: skipping %s/%s: %s\n", split,
					     entry.name.c_str(), error.c_str());
			continue;
		}
		segments.push_back(segment);
	}
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

CandidateWindow candidate_window_at(const Segment &segment, double seconds)
{
	CandidateWindow candidate;
	candidate.center_sample = static_cast<uint64_t>(std::llround(seconds * segment.sample_rate));

	for (const NoteAnnotation &note : segment.notes) {
		const double duration = note.end_seconds - note.start_seconds;
		const double edge = std::min(0.035, duration / 5.0);
		const double start = note.start_seconds + edge;
		const double end = note.end_seconds - edge;
		if (seconds < start || seconds > end)
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

std::vector<CandidateWindow> select_candidate_windows(const Segment &segment, int max_windows,
						      int min_active_notes, int min_active_instruments,
						      int min_pitch_classes)
{
	std::vector<CandidateWindow> candidates;

	for (const NoteAnnotation &note : segment.notes) {
		const double seconds = note.start_seconds + (note.end_seconds - note.start_seconds) * 0.5;
		CandidateWindow candidate = candidate_window_at(segment, seconds);
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
		if (candidate.center_sample >= segment.frame_count)
			continue;
		bool duplicate = false;
		for (const CandidateWindow &existing : selected) {
			const uint64_t distance = candidate.center_sample > existing.center_sample
							  ? candidate.center_sample - existing.center_sample
							  : existing.center_sample - candidate.center_sample;
			if (distance < static_cast<uint64_t>(segment.sample_rate / 5)) {
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

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "MulTTiPop real pop mix", 0);
	return snapshot;
}

struct RecallStats {
	int hits = 0;
	int expected = 0;
	int chord_hits = 0;
	int chord_checks = 0;
};

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
		const bool chord_hit =
			std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
				    [&](const std::string &label) { return snapshot_has_chord_label(snapshot, label); });
		if (chord_hit) {
			++stats.chord_hits;
		} else {
			std::fprintf(stderr,
				     "%s: chord opportunity `%s`, detected global `%s`, key `%s`, guitar `%s`, "
				     "other `%s`\n",
				     context.c_str(), join_labels(candidate.chord_labels).c_str(),
				     snapshot.global_chord.label, snapshot.keyboard_chord.label,
				     snapshot.guitar_chord.label, snapshot.other_chord.label);
		}
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
		return "active notes min/avg/max 0/0.00/0, active parts min/avg/max 0/0.00/0, "
		       "pitch classes min/avg/max 0/0.00/0";

	return "active notes min/avg/max " + std::to_string(stats.min_active_notes) + "/" +
	       average_string(stats.active_note_sum, stats.windows) + "/" +
	       std::to_string(stats.max_active_notes) + ", active parts min/avg/max " +
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
	const std::string root = resolve_multtipop_root();
	if (root.empty()) {
		if (env_truthy("MUSIC_ANALYZER_MULTTIPOP_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_multtipop: real MulTTiPop audio required; set "
				     "MUSIC_ANALYZER_MULTTIPOP_ROOT, MULTTIPOP_PATH, or "
				     "MUSIC_ANALYZER_DATASET_ROOT\n");
			return 1;
		}
		std::printf("analyzer_multtipop: skipped, set MUSIC_ANALYZER_MULTTIPOP_ROOT to a local MulTTiPop dataset with WAV segments\n");
		return 0;
	}
	if (!is_directory(root)) {
		std::fprintf(stderr, "analyzer_multtipop: `%s` is not a directory\n", root.c_str());
		return 1;
	}

	std::vector<Segment> segments;
	int missing_audio_or_unusable = 0;
	collect_split_segments(root, "dev", segments, missing_audio_or_unusable);
	collect_split_segments(root, "test", segments, missing_audio_or_unusable);
	std::sort(segments.begin(), segments.end(), [](const Segment &a, const Segment &b) {
		if (a.split != b.split)
			return a.split < b.split;
		return a.id < b.id;
	});

	const int required_segments = resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_REQUIRED_SEGMENTS", 20);
	const int max_windows_per_segment =
		resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MAX_WINDOWS_PER_SEGMENT", 4);
	const int default_required_windows = std::min(required_segments * 4,
						      max_windows_per_segment * required_segments);
	const int required_windows =
		resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_REQUIRED_WINDOWS", default_required_windows);
	const int min_active_notes =
		resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_ACTIVE_NOTES_PER_WINDOW", 2);
	const int min_active_parts =
		resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_ACTIVE_PARTS_PER_WINDOW", 2);
	const int min_pitch_classes =
		resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_PITCH_CLASSES_PER_WINDOW", 2);
	const int min_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MULTTIPOP_MIN_RECALL_PERCENT", 40);
	const int min_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MULTTIPOP_MIN_CHORD_RECALL_PERCENT", 20);
	const int min_chord_checks = resolve_positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_CHORD_CHECKS", 5);
	const bool inspect_only = env_truthy("MUSIC_ANALYZER_MULTTIPOP_INSPECT_ONLY");

	Runner runner;
	RecallStats recall;
	CompositionStats composition;
	int segments_with_windows = 0;
	int tested_windows = 0;
	int read_failures = 0;
	int no_candidate_segments = 0;

	for (const Segment &segment : segments) {
		const std::vector<CandidateWindow> candidates =
			select_candidate_windows(segment, max_windows_per_segment, min_active_notes, min_active_parts,
						 min_pitch_classes);
		if (candidates.empty()) {
			++no_candidate_segments;
			continue;
		}

		int segment_windows = 0;
		for (const CandidateWindow &candidate : candidates) {
			++segment_windows;
			++tested_windows;
			add_composition(composition, candidate);
			if (inspect_only)
				continue;

			mao_test::Buffer buffer = {};
			uint32_t sample_rate = 0;
			std::string error;
			if (!read_wav_window(segment.audio_path, candidate.center_sample, buffer, sample_rate, error)) {
				++read_failures;
				runner.expect(false, "MulTTiPop " + segment.split + "/" + segment.id +
							     " at sample " +
							     std::to_string(candidate.center_sample) + ": " + error);
				continue;
			}

			const mao::AnalysisSnapshot snapshot = analyze_confirmed_buffer(buffer, sample_rate);
			check_recall(runner, snapshot, candidate,
				     "MulTTiPop " + segment.split + "/" + segment.id + " at sample " +
					     std::to_string(candidate.center_sample),
				     recall, min_recall_percent);
		}

		if (segment_windows > 0)
			++segments_with_windows;
	}

	if (segments.empty()) {
		std::fprintf(stderr,
			     "analyzer_multtipop: no MulTTiPop segments with local WAV audio found under `%s`; "
			     "expected dev/test segment folders with aligned.mid plus audio.wav, segment.wav, "
			     "or <id>.wav\n",
			     root.c_str());
		return 1;
	}

	runner.expect(segments_with_windows >= required_segments,
		      "MulTTiPop coverage: expected at least " + std::to_string(required_segments) +
			      " audio-backed segments with candidate windows, got " +
			      std::to_string(segments_with_windows));
	runner.expect(tested_windows >= required_windows,
		      "MulTTiPop coverage: expected at least " + std::to_string(required_windows) +
			      " candidate windows, got " + std::to_string(tested_windows));
	runner.expect(composition.windows == tested_windows,
		      "MulTTiPop composition: expected composition stats for every window, got " +
			      std::to_string(composition.windows) + "/" + std::to_string(tested_windows));
	if (!inspect_only) {
		runner.expect(recall.expected > 0 && recall.hits * 100 >= recall.expected * min_recall_percent,
			      "MulTTiPop real-pop pitch-class recall: expected >=" +
				      std::to_string(min_recall_percent) + "%, got " +
				      std::to_string(recall.hits) + "/" + std::to_string(recall.expected));
		if (recall.chord_checks >= min_chord_checks) {
			runner.expect(recall.chord_hits * 100 >= recall.chord_checks * min_chord_recall_percent,
				      "MulTTiPop real-pop chord recall: expected >=" +
					      std::to_string(min_chord_recall_percent) + "%, got " +
					      std::to_string(recall.chord_hits) + "/" +
					      std::to_string(recall.chord_checks));
		}
	}

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_multtipop: %d/%d checks failed (segments %d/%zu, windows %d, "
			     "read failures %d, no-candidate segments %d, missing/unusable %d, "
			     "note hits %d/%d, chord hits %d/%d, %s)\n",
			     runner.failures, runner.checks, segments_with_windows, segments.size(), tested_windows,
			     read_failures, no_candidate_segments, missing_audio_or_unusable, recall.hits,
			     recall.expected, recall.chord_hits, recall.chord_checks,
			     composition_summary(composition).c_str());
		return 1;
	}

	if (inspect_only) {
		std::printf("analyzer_multtipop: inspect passed (segments %d/%zu, windows %d, "
			    "no-candidate segments %d, missing/unusable %d, %s)\n",
			    segments_with_windows, segments.size(), tested_windows, no_candidate_segments,
			    missing_audio_or_unusable, composition_summary(composition).c_str());
	} else {
		std::printf("analyzer_multtipop: %d checks passed (segments %d/%zu, windows %d, "
			    "read failures %d, no-candidate segments %d, missing/unusable %d, "
			    "note hits %d/%d, chord hits %d/%d, %s)\n",
			    runner.checks, segments_with_windows, segments.size(), tested_windows, read_failures,
			    no_candidate_segments, missing_audio_or_unusable, recall.hits, recall.expected,
			    recall.chord_hits, recall.chord_checks, composition_summary(composition).c_str());
	}
	return 0;
}
