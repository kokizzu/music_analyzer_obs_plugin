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
	int midi = 0;
};

bool read_maestro_midi(const std::string &path, std::vector<NoteAnnotation> &notes,
			      std::vector<TempoPoint> *tempo_points_output, bool *has_explicit_tempo,
			      std::string &error)
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

		++parsed_tracks;
		uint64_t tick = 0;
		unsigned char running_status = 0;
		std::map<int, uint64_t> active_notes;

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

			const int key = (status & 0x0f) * 128 + first;
			const unsigned char event_type = status & 0xf0;
			if (event_type == 0x90 && second > 0) {
				active_notes[key] = tick;
			} else if (event_type == 0x80 || (event_type == 0x90 && second == 0)) {
				const auto found = active_notes.find(key);
				if (found == active_notes.end())
					continue;
				if (tick > found->second)
					raw_notes.push_back(RawMidiNote{found->second, tick, static_cast<int>(first)});
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
	if (tempo_points_output)
		*tempo_points_output = tempo_points;
	if (has_explicit_tempo)
		*has_explicit_tempo = !tempo_events.empty();
	for (const RawMidiNote &raw : raw_notes) {
		if (raw.midi < mao::kFirstAnalyzedMidi || raw.midi > mao::kLastAnalyzedMidi)
			continue;
		const double start = tick_to_seconds(tempo_points, raw.start_tick, division);
		const double end = tick_to_seconds(tempo_points, raw.end_tick, division);
		if (end - start < 0.035)
			continue;
		notes.push_back(NoteAnnotation{start, end, raw.midi});
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

struct Recording {
	std::string id;
	std::string audio_path;
	std::string midi_path;
	uint32_t sample_rate = 0;
	uint64_t frame_count = 0;
	std::vector<NoteAnnotation> notes;
	std::vector<TempoPoint> tempo_points;
	bool has_explicit_tempo = false;
	double tempo_audio_offset_seconds = 0.0;
};

std::string find_metadata_csv(const std::string &root)
{
	const std::vector<std::string> preferred = {
		"maestro-v3.0.0.csv",
		"maestro-v2.0.0.csv",
		"maestro-v1.0.0.csv",
		"metadata.csv",
	};
	for (const std::string &name : preferred) {
		const std::string candidate = join_path(root, name);
		if (file_exists(candidate))
			return candidate;
	}

	for (const DirEntry &entry : list_dir(root)) {
		if (entry.directory)
			continue;
		const std::string lower = entry.name;
		if (lower.find("maestro") != std::string::npos && ends_with(lower, ".csv"))
			return join_path(root, entry.name);
	}
	return "";
}

bool has_maestro_layout(const std::string &root)
{
	return !find_metadata_csv(root).empty();
}

std::string resolve_maestro_layout(const std::string &root)
{
	if (has_maestro_layout(root))
		return root;

	const std::vector<std::string> candidates = {
		join_path(root, "maestro-v3.0.0"),
		join_path(root, "maestro-v2.0.0"),
		join_path(root, "MAESTRO"),
		join_path(root, "maestro"),
	};
	for (const std::string &candidate : candidates) {
		if (has_maestro_layout(candidate))
			return candidate;
	}
	return root;
}

std::string resolve_maestro_root()
{
	const char *root = std::getenv("MUSIC_ANALYZER_MAESTRO_ROOT");
	if (root && *root)
		return resolve_maestro_layout(root);

	root = std::getenv("MAESTRO_PATH");
	if (root && *root)
		return resolve_maestro_layout(root);

	const char *dataset_root = std::getenv("MUSIC_ANALYZER_DATASET_ROOT");
	if (!dataset_root || !*dataset_root)
		return "";

	const std::vector<std::string> candidates = {
		join_path(dataset_root, "maestro-v3.0.0"),
		join_path(dataset_root, "maestro-v2.0.0"),
		join_path(dataset_root, "MAESTRO"),
		join_path(dataset_root, "maestro"),
	};
	for (const std::string &candidate : candidates) {
		if (has_maestro_layout(candidate))
			return candidate;
	}
	return resolve_maestro_layout(dataset_root);
}

bool load_recording(const std::string &root, const std::string &id, const std::string &audio_filename,
		    const std::string &midi_filename, double tempo_audio_offset_seconds,
		    Recording &recording, std::string &error)
{
	const std::string audio_path = join_path(root, audio_filename);
	const std::string midi_path = join_path(root, midi_filename);
	WavFormat format;
	if (!read_wav_format(audio_path, format, error))
		return false;
	std::vector<NoteAnnotation> notes;
	std::vector<TempoPoint> tempo_points;
	bool has_explicit_tempo = false;
	if (!read_maestro_midi(midi_path, notes, &tempo_points, &has_explicit_tempo, error))
		return false;

	recording.id = id;
	recording.audio_path = audio_path;
	recording.midi_path = midi_path;
	recording.sample_rate = format.sample_rate;
	recording.frame_count = format.frame_count;
	recording.notes = std::move(notes);
	recording.tempo_points = std::move(tempo_points);
	recording.has_explicit_tempo = has_explicit_tempo;
	recording.tempo_audio_offset_seconds = tempo_audio_offset_seconds;
	return true;
}

void collect_recordings(const std::string &root, std::vector<Recording> &recordings, int &unusable)
{
	const std::string csv_path = find_metadata_csv(root);
	if (csv_path.empty())
		return;

	std::ifstream file(csv_path);
	if (!file) {
		++unusable;
		return;
	}

	std::string line;
	if (!std::getline(file, line)) {
		++unusable;
		return;
	}
	const std::vector<std::string> header = split_csv_line(line);
	std::map<std::string, int> column;
	for (std::size_t i = 0; i < header.size(); ++i)
		column[header[i]] = static_cast<int>(i);

	if (column.find("midi_filename") == column.end() || column.find("audio_filename") == column.end()) {
		++unusable;
		return;
	}

	int row = 0;
	while (std::getline(file, line)) {
		if (trim(line).empty())
			continue;
		++row;
		const std::vector<std::string> fields = split_csv_line(line);
		if (fields.size() < header.size()) {
			++unusable;
			continue;
		}
		const std::string midi_filename = fields[column["midi_filename"]];
		const std::string audio_filename = fields[column["audio_filename"]];
		if (midi_filename.empty() || audio_filename.empty()) {
			++unusable;
			continue;
		}

		double tempo_audio_offset_seconds = 0.0;
		const auto tempo_offset_column = column.find("tempo_audio_offset_seconds");
		if (tempo_offset_column != column.end()) {
			const char *offset_text = fields[tempo_offset_column->second].c_str();
			char *offset_end = nullptr;
			tempo_audio_offset_seconds = std::strtod(offset_text, &offset_end);
			if (offset_end == offset_text || *offset_end != '\0' || !std::isfinite(tempo_audio_offset_seconds) ||
			    tempo_audio_offset_seconds < 0.0) {
				++unusable;
				continue;
			}
		}

		Recording recording;
		std::string error;
		if (!load_recording(root, std::to_string(row), audio_filename, midi_filename,
				    tempo_audio_offset_seconds, recording, error)) {
			++unusable;
			if (unusable <= 5)
				std::fprintf(stderr, "analyzer_maestro: skipping row %d: %s\n", row,
					     error.c_str());
			continue;
		}
		recordings.push_back(recording);
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

struct CandidateWindow {
	uint64_t center_sample = 0;
	std::vector<int> active_midis;
	std::array<bool, 12> pitch_classes = {};
	std::vector<std::string> chord_labels;
	int chord_tone_count = 0;
	double score = 0.0;
};

CandidateWindow candidate_window_at(const Recording &recording, double seconds)
{
	CandidateWindow candidate;
	candidate.center_sample = static_cast<uint64_t>(std::llround(seconds * recording.sample_rate));

	for (const NoteAnnotation &note : recording.notes) {
		const double duration = note.end_seconds - note.start_seconds;
		const double edge = std::min(0.035, duration / 5.0);
		const double start = note.start_seconds + edge;
		const double end = note.end_seconds - edge;
		if (seconds < start || seconds > end)
			continue;
		candidate.active_midis.push_back(note.midi);
		candidate.pitch_classes[((note.midi % 12) + 12) % 12] = true;
	}

	if (candidate.active_midis.size() < 2)
		return candidate;

	candidate.chord_labels = expected_common_chord_labels(candidate.pitch_classes, candidate.chord_tone_count);
	candidate.score = static_cast<double>(candidate.active_midis.size()) * 80.0 +
			  static_cast<double>(pitch_class_count(candidate.pitch_classes)) * 30.0 +
			  static_cast<double>(candidate.chord_tone_count) * 40.0 +
			  (candidate.chord_labels.empty() ? 0.0 : 100.0);
	return candidate;
}

std::vector<CandidateWindow> select_candidate_windows(const Recording &recording, int max_windows,
						      int min_active_notes, int min_pitch_classes)
{
	std::vector<CandidateWindow> candidates;
	const bool prefer_note_onset = min_active_notes == 1 && min_pitch_classes == 1;

	for (const NoteAnnotation &note : recording.notes) {
		const double duration = note.end_seconds - note.start_seconds;
		// A piano note's annotated sustain can be almost silent by its midpoint.
		// For the dedicated monophonic gate, sample a settled onset instead; chord
		// fixtures retain midpoint selection to assess simultaneous harmony.
		const double seconds = prefer_note_onset ?
				       note.start_seconds + std::min(0.08, duration * 0.20) :
				       note.start_seconds + duration * 0.5;
		CandidateWindow candidate = candidate_window_at(recording, seconds);
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
		if (candidate.center_sample >= recording.frame_count)
			continue;
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
	settings.input_mode = mao::AnalysisInputMode::IsolatedKeyboard;

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "MAESTRO piano", 0);
	return snapshot;
}

bool maestro_tempo_interval(const Recording &recording, double max_seconds, double &start_seconds,
			    double &end_seconds, float &expected_bpm)
{
	if (!recording.has_explicit_tempo || recording.tempo_points.empty())
		return false;
	const double available_seconds = static_cast<double>(recording.frame_count) / recording.sample_rate;
	for (std::size_t index = 0; index < recording.tempo_points.size(); ++index) {
		const TempoPoint &point = recording.tempo_points[index];
		const double interval_end = index + 1 < recording.tempo_points.size() ?
					    recording.tempo_points[index + 1].seconds : available_seconds;
		const double duration = std::min(max_seconds, interval_end - point.seconds);
		if (point.microseconds_per_quarter <= 0 || duration < 14.0)
			continue;
	start_seconds = point.seconds + recording.tempo_audio_offset_seconds;
	end_seconds = start_seconds + duration;
		expected_bpm = 60000000.0f / static_cast<float>(point.microseconds_per_quarter);
		return true;
	}
	return false;
}

struct TempoStats {
	int eligible = 0;
	int measured = 0;
	int hits = 0;
	int no_estimate = 0;
	double absolute_error_sum = 0.0;
	double max_absolute_error = 0.0;
};

std::string tempo_candidate_summary(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t index = 0; index < snapshot.tempo_debug_candidate_count; ++index) {
		const mao::TempoDebugCandidate &candidate = snapshot.tempo_debug_candidates[index];
		char part[400] = {};
		std::snprintf(part, sizeof(part),
			      "%s%d(s=%.2f,a=%.2f,b=%.2f,ba=%.2f,ph=%.2f,lock=%.2f,m=%.2f,rep=%.2f/%.2f/%.2f,cov=%.0f/%.0f,src=%.0f/%.0f/%.0f/%.0f,align=%.0f/%.0f/%.0f/%.0f,kb=%.0f)",
			      text.empty() ? "" : " ", candidate.bpm, candidate.score,
			      candidate.adjacent_score, candidate.body_score,
			      candidate.adjacent_body_score, candidate.phase_score,
			      candidate.phase_locked_score, candidate.meter_score,
			      candidate.recurrence_score, candidate.kick_recurrence_score,
			      candidate.bass_recurrence_score,
			      candidate.phase_body_coverage * 100.0f,
			      candidate.phase_all_coverage * 100.0f,
			      candidate.kick_phase_coverage * 100.0f,
			      candidate.bass_phase_coverage * 100.0f,
			      candidate.snare_phase_coverage * 100.0f,
			      candidate.tonal_phase_coverage * 100.0f,
			      candidate.kick_phase_energy_alignment * 100.0f,
			      candidate.bass_phase_energy_alignment * 100.0f,
			      candidate.snare_phase_energy_alignment * 100.0f,
			      candidate.tonal_phase_energy_alignment * 100.0f,
			      candidate.kick_bass_phase_energy_alignment * 100.0f);
		text += part;
	}
	return text.empty() ? "-" : text;
}

bool measure_maestro_tempo(const Recording &recording, double max_seconds, float confidence_floor,
			  float tolerance, TempoStats &stats, std::string &error)
{
	double start_seconds = 0.0;
	double end_seconds = 0.0;
	float expected = 0.0f;
	if (recording.sample_rate == 0 ||
	    !maestro_tempo_interval(recording, max_seconds, start_seconds, end_seconds, expected))
		return false;
	++stats.eligible;

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = recording.sample_rate;
	settings.analysis_interval_seconds =
		static_cast<float>(mao_test::Buffer{}.size()) / static_cast<float>(recording.sample_rate);
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.tempo_debug_probe_bpm = static_cast<int>(std::lround(expected));

	mao_test::Buffer buffer = {};
	const uint64_t first_center = static_cast<uint64_t>(std::llround(start_seconds * recording.sample_rate)) +
				      buffer.size() / 2;
	const uint64_t last_center = static_cast<uint64_t>(std::floor(end_seconds * recording.sample_rate));
	mao::AnalysisSnapshot snapshot = {};
	for (uint64_t center = first_center;
	     center + buffer.size() / 2 <= last_center; center += buffer.size()) {
		uint32_t sample_rate = 0;
		if (!read_wav_window(recording.audio_path, center, buffer, sample_rate, error))
			return false;
		if (sample_rate != recording.sample_rate) {
			error = "sample-rate changed while reading";
			return false;
		}
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "MAESTRO piano tempo", 0);
	}

	++stats.measured;
	if (snapshot.estimated_bpm <= 0.0f || snapshot.bpm_confidence < confidence_floor) {
		++stats.no_estimate;
		std::fprintf(stderr,
			     "MAESTRO tempo diag\tid=%s\texpected=%.2f\tgot=0.00\traw=%.2f\tconfidence=%.3f\terror=%.2f\tstatus=no-estimate\tcandidates=%s\n",
			     recording.id.c_str(), expected, snapshot.estimated_bpm, snapshot.bpm_confidence,
			     static_cast<double>(expected), tempo_candidate_summary(snapshot).c_str());
		return true;
	}
	const double absolute_error = std::abs(static_cast<double>(snapshot.estimated_bpm - expected));
	stats.absolute_error_sum += absolute_error;
	stats.max_absolute_error = std::max(stats.max_absolute_error, absolute_error);
	if (absolute_error <= tolerance)
		++stats.hits;
	std::fprintf(stderr, "MAESTRO tempo diag\tid=%s\texpected=%.2f\tgot=%.2f\traw=%.2f\tconfidence=%.3f\terror=%.2f\tstatus=%s\tcandidates=%s\n",
		     recording.id.c_str(), expected, snapshot.estimated_bpm, snapshot.estimated_bpm, snapshot.bpm_confidence,
		     absolute_error, absolute_error <= tolerance ? "hit" : "miss",
		     tempo_candidate_summary(snapshot).c_str());
	return true;
}

struct RecallStats {
	int hits = 0;
	int expected = 0;
	int chord_hits = 0;
	int chord_checks = 0;
};

std::array<bool, 12> grid_pitch_classes(const mao::NoteGrid &grid)
{
	std::array<bool, 12> pitch_classes = {};
	add_detected_pitch_classes(grid, pitch_classes);
	return pitch_classes;
}

bool grid_has_any_active_pitch_class(const mao::NoteGrid &grid)
{
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (grid_has_pitch_class(grid, pitch_class))
			return true;
	}
	return false;
}

std::string pitch_class_list(const std::array<bool, 12> &pitch_classes)
{
	std::string result;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!pitch_classes[pitch_class])
			continue;
		if (!result.empty())
			result += ',';
		result += mao_test::note_name(pitch_class);
	}
	return result.empty() ? "--" : result;
}

std::string pitch_class_difference_list(const std::array<bool, 12> &left,
						 const std::array<bool, 12> &right)
{
	std::array<bool, 12> difference = {};
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		difference[pitch_class] = left[pitch_class] && !right[pitch_class];
	return pitch_class_list(difference);
}

std::string midi_list(const std::vector<int> &midis)
{
	std::string result;
	for (int midi : midis) {
		if (!result.empty())
			result += ',';
		result += std::to_string(midi);
	}
	return result.empty() ? "--" : result;
}

std::string grid_midi_list(const mao::NoteGrid &grid)
{
	std::vector<int> midis;
	for (const auto &row : grid.rows)
		for (const auto &cell : row)
			if (cell.active && cell.midi >= 0)
				midis.push_back(cell.midi);
	for (const auto &cell : grid.cells)
		if (cell.active && cell.midi >= 0 &&
		    std::find(midis.begin(), midis.end(), cell.midi) == midis.end())
			midis.push_back(cell.midi);
	std::sort(midis.begin(), midis.end());
	return midi_list(midis);
}

std::string grid_pitch_level_list(const mao::NoteGrid &grid)
{
	std::array<float, 12> levels = {};
	auto collect = [&](const mao::NoteCell &cell) {
		if (cell.active && cell.midi >= 0)
			levels[static_cast<std::size_t>(cell.midi % 12)] =
				std::max(levels[static_cast<std::size_t>(cell.midi % 12)], cell.level);
	};
	for (const auto &row : grid.rows)
		for (const auto &cell : row)
			collect(cell);
	for (const auto &cell : grid.cells)
		collect(cell);

	std::string result;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (levels[static_cast<std::size_t>(pitch_class)] <= 0.0f)
			continue;
		if (!result.empty())
			result += ',';
		char level[16] = {};
		std::snprintf(level, sizeof(level), ":%.3f", levels[static_cast<std::size_t>(pitch_class)]);
		result += mao_test::note_name(pitch_class);
		result += level;
	}
	return result.empty() ? "--" : result;
}

std::string grid_midi_level_list(const mao::NoteGrid &grid)
{
	std::map<int, float> levels;
	auto collect = [&](const mao::NoteCell &cell) {
		if (cell.active && cell.midi >= 0)
			levels[cell.midi] = std::max(levels[cell.midi], cell.level);
	};
	for (const auto &row : grid.rows)
		for (const auto &cell : row)
			collect(cell);
	for (const auto &cell : grid.cells)
		collect(cell);

	std::string result;
	for (const auto &[midi, value] : levels) {
		if (!result.empty())
			result += ',';
		result += std::to_string(midi);
		char level[16] = {};
		std::snprintf(level, sizeof(level), ":%.3f", value);
		result += level;
	}
	return result.empty() ? "--" : result;
}

struct KeyboardPrecisionStats {
	int windows = 0;
	int expected_pitch_classes = 0;
	int true_positives = 0;
	int false_positives = 0;
	int false_negatives = 0;
	int contaminated_pitch_classes = 0;
	int bass_contamination = 0;
	int guitar_contamination = 0;
	int vocal_contamination = 0;
	int other_contamination = 0;
	int ambiguous_pitch_classes = 0;
	int false_non_keyboard_windows = 0;
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

void add_keyboard_precision_metrics(KeyboardPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
				    const CandidateWindow &candidate)
{
	++stats.windows;
	const std::array<bool, 12> keyboard = grid_pitch_classes(snapshot.keyboard_notes);
	const std::array<bool, 12> bass = grid_pitch_classes(snapshot.bass_notes);
	const std::array<bool, 12> guitar = grid_pitch_classes(snapshot.guitar_notes);
	const std::array<bool, 12> vocal = grid_pitch_classes(snapshot.vocal_notes);
	const std::array<bool, 12> other = grid_pitch_classes(snapshot.other_notes);
	const std::array<bool, 12> ambiguous = grid_pitch_classes(snapshot.ambiguous_notes);

	if (grid_has_any_active_pitch_class(snapshot.bass_notes) ||
	    grid_has_any_active_pitch_class(snapshot.guitar_notes) ||
	    grid_has_any_active_pitch_class(snapshot.vocal_notes) ||
	    grid_has_any_active_pitch_class(snapshot.other_notes))
		++stats.false_non_keyboard_windows;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		const bool expected = candidate.pitch_classes[pitch_class];
		if (expected) {
			++stats.expected_pitch_classes;
			if (keyboard[pitch_class])
				++stats.true_positives;
			else
				++stats.false_negatives;

			bool contaminated = false;
			if (bass[pitch_class]) {
				++stats.bass_contamination;
				contaminated = true;
			}
			if (guitar[pitch_class]) {
				++stats.guitar_contamination;
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
		} else if (keyboard[pitch_class]) {
			++stats.false_positives;
		}
	}
}

void add_keyboard_chord_precision_metrics(ChordPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
					  const CandidateWindow &candidate)
{
	const bool expected = !candidate.chord_labels.empty();
	const std::vector<std::string> predicted = split_chord_labels(snapshot.keyboard_chord.label);
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

void print_maestro_attribute_header(std::ostream &out)
{
	out << "recording\tcenter_sample\texpected_midis\tdetected_keyboard_midis\texpected_pcs\tdetected_keyboard_pcs\tdetected_chord_pcs\tkeyboard_levels\tkeyboard_midi_levels\tkeyboard_chord_levels\tchord_debug\tmissing_pcs\textra_pcs\t"
	       "expected_chords\tchord_hit\taudio_rms\taudio_peak\tglobal_chord\tkeyboard_chord\n";
}

void append_maestro_attribute_row(std::ostream &out, const Recording &recording,
					  const CandidateWindow &candidate, const mao::AnalysisSnapshot &snapshot,
					  const mao_test::Buffer &buffer)
{
	const std::array<bool, 12> keyboard = grid_pitch_classes(snapshot.keyboard_notes);
	const std::array<bool, 12> chord_keyboard = grid_pitch_classes(snapshot.keyboard_chord_smoothed_notes);
	const bool chord_hit = std::any_of(candidate.chord_labels.begin(), candidate.chord_labels.end(),
					     [&](const std::string &label) { return snapshot_has_chord_label(snapshot, label); });
	double energy = 0.0;
	float peak = 0.0f;
	for (float sample : buffer) {
		energy += static_cast<double>(sample) * sample;
		peak = std::max(peak, std::fabs(sample));
	}
	const double rms = buffer.empty() ? 0.0 : std::sqrt(energy / static_cast<double>(buffer.size()));
	out << recording.id << '\t' << candidate.center_sample << '\t' << midi_list(candidate.active_midis) << '\t'
	    << grid_midi_list(snapshot.keyboard_notes) << '\t'
	    << pitch_class_list(candidate.pitch_classes) << '\t' << pitch_class_list(keyboard) << '\t'
	    << pitch_class_list(chord_keyboard) << '\t'
	    << grid_pitch_level_list(snapshot.keyboard_notes) << '\t'
	    << grid_midi_level_list(snapshot.keyboard_notes) << '\t'
	    << grid_pitch_level_list(snapshot.keyboard_chord_smoothed_notes) << '\t'
	    << snapshot.keyboard_chord_debug_reason << '\t'
	    << pitch_class_difference_list(candidate.pitch_classes, keyboard) << '\t'
	    << pitch_class_difference_list(keyboard, candidate.pitch_classes) << '\t'
	    << join_labels(candidate.chord_labels) << '\t' << (chord_hit ? 1 : 0) << '\t' << rms << '\t' << peak << '\t'
	    << snapshot.global_chord.label << '\t' << snapshot.keyboard_chord.label << '\n';
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

std::string keyboard_precision_summary(const KeyboardPrecisionStats &stats)
{
	return "keyboard precision " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_positives) +
	       ", keyboard recall " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_negatives) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", contamination " + percent_string(stats.contaminated_pitch_classes, stats.expected_pitch_classes) +
	       " (" + std::to_string(stats.contaminated_pitch_classes) + "/" +
	       std::to_string(stats.expected_pitch_classes) + ")" +
	       ", false non-keyboard windows " + percent_string(stats.false_non_keyboard_windows, stats.windows) +
	       " (" + std::to_string(stats.false_non_keyboard_windows) + "/" + std::to_string(stats.windows) + ")" +
	       ", ambiguous " + std::to_string(stats.ambiguous_pitch_classes) + "/" +
	       std::to_string(stats.expected_pitch_classes) + ", row leaks bass/guitar/vocal/other " +
	       std::to_string(stats.bass_contamination) + "/" + std::to_string(stats.guitar_contamination) +
	       "/" + std::to_string(stats.vocal_contamination) + "/" +
	       std::to_string(stats.other_contamination) + ", tp/fp/fn " +
	       std::to_string(stats.true_positives) + "/" + std::to_string(stats.false_positives) + "/" +
	       std::to_string(stats.false_negatives);
}

std::string chord_precision_summary(const ChordPrecisionStats &stats)
{
	return "keyboard chord precision " + percent_string(stats.true_positives, stats.predicted_windows) +
	       ", keyboard chord recall " + percent_string(stats.true_positives, stats.expected_windows) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", tp/fp/fn " + std::to_string(stats.true_positives) + "/" +
	       std::to_string(stats.false_positives) + "/" + std::to_string(stats.false_negatives);
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

} // namespace

int main()
{
	const std::string root = resolve_maestro_root();
	if (root.empty()) {
		if (env_truthy("MUSIC_ANALYZER_MAESTRO_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_maestro: real MAESTRO audio required; set "
				     "MUSIC_ANALYZER_MAESTRO_ROOT, MAESTRO_PATH, or MUSIC_ANALYZER_DATASET_ROOT\n");
			return 1;
		}
		std::printf("analyzer_maestro: skipped, set MUSIC_ANALYZER_MAESTRO_ROOT to a local MAESTRO dataset\n");
		return 0;
	}
	if (!is_directory(root)) {
		std::fprintf(stderr, "analyzer_maestro: `%s` is not a directory\n", root.c_str());
		return 1;
	}

	std::vector<Recording> recordings;
	int unusable = 0;
	collect_recordings(root, recordings, unusable);
	std::sort(recordings.begin(), recordings.end(), [](const Recording &a, const Recording &b) {
		return a.id < b.id;
	});

	const int required_recordings = resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS", 20);
	const int max_windows_per_recording =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING", 4);
	const int default_required_windows = std::min(required_recordings * 4,
						      max_windows_per_recording * required_recordings);
	const int required_windows =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS", default_required_windows);
	const int min_active_notes =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW", 2);
	const int min_pitch_classes =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW", 2);
	const int min_recall_percent = resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT", 40);
	const int min_keyboard_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT", 90);
	const int min_keyboard_row_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT", 90);
	const int max_keyboard_contamination_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT", 5);
	const int max_false_non_keyboard_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT", 5);
	const int min_chord_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT", 20);
	const int min_chord_precision_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT", 85);
	const int min_chord_checks = resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS", 5);
	const int shard_count = resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_SHARD_COUNT", 1);
	const int shard_index = resolve_nonnegative_int_env("MUSIC_ANALYZER_MAESTRO_SHARD_INDEX", 0);
	if (shard_index >= shard_count) {
		std::fprintf(stderr, "analyzer_maestro: shard index %d outside shard count %d\n", shard_index,
			     shard_count);
		return 1;
	}
	const bool inspect_only = env_truthy("MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY");
	const bool validate_tempo = env_truthy("MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM");
	const bool measure_all_tempo = env_truthy("MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO");
	const int required_tempo_recordings =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS", 20);
	const int tempo_max_seconds =
		resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS", 20);
	const int bpm_tolerance = resolve_positive_int_env("MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE", 8);
	const int min_bpm_pass_percent =
		resolve_percent_env("MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT", 0);
	const char *attribute_path_env = std::getenv("MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV");
	std::ofstream attribute_file;
	if (attribute_path_env && *attribute_path_env) {
		attribute_file.open(attribute_path_env);
		if (!attribute_file) {
			std::fprintf(stderr, "analyzer_maestro: failed to open attribute TSV `%s`\n", attribute_path_env);
			return 1;
		}
		print_maestro_attribute_header(attribute_file);
	}

	Runner runner;
	RecallStats recall;
	KeyboardPrecisionStats precision;
	ChordPrecisionStats keyboard_chord_precision;
	CompositionStats composition;
	int recordings_with_windows = 0;
	int tested_windows = 0;
	int read_failures = 0;
	int no_candidate_recordings = 0;
	TempoStats tempo;

	std::size_t recording_ordinal = 0;
	for (const Recording &recording : recordings) {
		const std::size_t current_recording_ordinal = recording_ordinal++;
		if (shard_count > 1 &&
		    current_recording_ordinal % static_cast<std::size_t>(shard_count) !=
			    static_cast<std::size_t>(shard_index))
			continue;
		if (validate_tempo && (measure_all_tempo || tempo.measured < required_tempo_recordings)) {
			std::string tempo_error;
			if (!measure_maestro_tempo(recording, tempo_max_seconds, mao::kBpmDisplayConfidenceThreshold,
						 static_cast<float>(bpm_tolerance), tempo, tempo_error) &&
			    !tempo_error.empty()) {
				runner.expect(false, "MAESTRO tempo " + recording.id + ": " + tempo_error);
			}
		}

		const std::vector<CandidateWindow> candidates =
			select_candidate_windows(recording, max_windows_per_recording, min_active_notes,
						 min_pitch_classes);
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
				runner.expect(false, "MAESTRO " + recording.id + " at sample " +
							     std::to_string(candidate.center_sample) + ": " + error);
				continue;
			}

			const mao::AnalysisSnapshot snapshot = analyze_confirmed_buffer(buffer, sample_rate);
			if (attribute_file)
				append_maestro_attribute_row(attribute_file, recording, candidate, snapshot, buffer);
			check_recall(runner, snapshot, candidate,
				     "MAESTRO " + recording.id + " at sample " +
					     std::to_string(candidate.center_sample),
				     recall, min_recall_percent);
			add_keyboard_precision_metrics(precision, snapshot, candidate);
			add_keyboard_chord_precision_metrics(keyboard_chord_precision, snapshot, candidate);
		}

		if (recording_windows > 0)
			++recordings_with_windows;
	}

	if (recordings.empty()) {
		std::fprintf(stderr,
			     "analyzer_maestro: no MAESTRO WAV/MIDI pairs found under `%s`; expected "
			     "maestro-v*.csv metadata with audio_filename and midi_filename columns\n",
			     root.c_str());
		return 1;
	}

	runner.expect(recordings_with_windows >= required_recordings,
		      "MAESTRO coverage: expected at least " + std::to_string(required_recordings) +
			      " recordings with candidate windows, got " +
			      std::to_string(recordings_with_windows));
	runner.expect(tested_windows >= required_windows,
		      "MAESTRO coverage: expected at least " + std::to_string(required_windows) +
			      " candidate windows, got " + std::to_string(tested_windows));
	runner.expect(composition.windows == tested_windows,
		      "MAESTRO composition: expected composition stats for every window, got " +
			      std::to_string(composition.windows) + "/" + std::to_string(tested_windows));
	if (!inspect_only) {
		runner.expect(recall.expected > 0 && recall.hits * 100 >= recall.expected * min_recall_percent,
			      "MAESTRO piano pitch-class recall: expected >=" +
				      std::to_string(min_recall_percent) + "%, got " +
				      std::to_string(recall.hits) + "/" + std::to_string(recall.expected));
		runner.expect(precision.expected_pitch_classes > 0,
			      "MAESTRO keyboard precision: expected at least one pitch-class check");
		if (precision.expected_pitch_classes > 0) {
			runner.expect(
				percentage_floor(precision.true_positives,
						 precision.true_positives + precision.false_positives) >=
					min_keyboard_precision_percent,
				"MAESTRO keyboard precision: expected >=" +
					std::to_string(min_keyboard_precision_percent) + "%, got " +
					percent_string(precision.true_positives,
						       precision.true_positives + precision.false_positives) +
					" (" + keyboard_precision_summary(precision) + ")");
			runner.expect(
				percentage_floor(precision.true_positives,
						 precision.true_positives + precision.false_negatives) >=
					min_keyboard_row_recall_percent,
				"MAESTRO keyboard row recall: expected >=" +
					std::to_string(min_keyboard_row_recall_percent) + "%, got " +
					percent_string(precision.true_positives,
						       precision.true_positives + precision.false_negatives) +
					" (" + keyboard_precision_summary(precision) + ")");
			runner.expect(
				percentage_floor(precision.contaminated_pitch_classes,
						 precision.expected_pitch_classes) <=
					max_keyboard_contamination_percent,
				"MAESTRO cross-row contamination: expected <=" +
					std::to_string(max_keyboard_contamination_percent) + "%, got " +
					percent_string(precision.contaminated_pitch_classes,
						       precision.expected_pitch_classes) +
					" (" + keyboard_precision_summary(precision) + ")");
			runner.expect(percentage_floor(precision.false_non_keyboard_windows,
						       precision.windows) <= max_false_non_keyboard_percent,
				      "MAESTRO false non-keyboard detection: expected <=" +
					      std::to_string(max_false_non_keyboard_percent) +
					      "% of windows, got " +
					      percent_string(precision.false_non_keyboard_windows,
							     precision.windows) +
					      " (" + keyboard_precision_summary(precision) + ")");
		}
		if (recall.chord_checks >= min_chord_checks) {
			runner.expect(recall.chord_hits * 100 >= recall.chord_checks * min_chord_recall_percent,
				      "MAESTRO piano chord recall: expected >=" +
					      std::to_string(min_chord_recall_percent) + "%, got " +
					      std::to_string(recall.chord_hits) + "/" +
					      std::to_string(recall.chord_checks));
			runner.expect(percentage_floor(keyboard_chord_precision.true_positives,
						       keyboard_chord_precision.predicted_windows) >=
					      min_chord_precision_percent,
				      "MAESTRO keyboard chord precision: expected >=" +
					      std::to_string(min_chord_precision_percent) + "%, got " +
					      percent_string(keyboard_chord_precision.true_positives,
							     keyboard_chord_precision.predicted_windows) +
					      " (" + chord_precision_summary(keyboard_chord_precision) + ")");
		}
	}
	if (validate_tempo) {
		runner.expect(tempo.eligible >= required_tempo_recordings,
			      "MAESTRO tempo coverage: expected at least " +
				      std::to_string(required_tempo_recordings) +
				      " constant-tempo recordings, got " + std::to_string(tempo.eligible));
		runner.expect(tempo.measured >= required_tempo_recordings,
			      "MAESTRO tempo measurement: expected at least " +
				      std::to_string(required_tempo_recordings) +
				      " recordings, got " + std::to_string(tempo.measured));
		if (tempo.measured > 0) {
			runner.expect(tempo.hits * 100 >= tempo.measured * min_bpm_pass_percent,
			      "MAESTRO tempo accuracy: expected >=" + std::to_string(min_bpm_pass_percent) +
				      "%, got " + std::to_string(tempo.hits) + "/" +
				      std::to_string(tempo.measured));
		}
		std::printf("analyzer_maestro: tempo hits %d/%d, no-estimate %d, mean abs error %.2f, max abs error %.2f\n",
			    tempo.hits, tempo.measured, tempo.no_estimate,
			    tempo.measured > 0 ? tempo.absolute_error_sum / tempo.measured : 0.0,
			    tempo.max_absolute_error);
	}

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_maestro: %d/%d checks failed (recordings %d/%zu, windows %d, "
			     "read failures %d, no-candidate recordings %d, unusable %d, "
			     "note hits %d/%d, chord hits %d/%d, %s, %s, %s)\n",
			     runner.failures, runner.checks, recordings_with_windows, recordings.size(),
			     tested_windows, read_failures, no_candidate_recordings, unusable, recall.hits,
			     recall.expected, recall.chord_hits, recall.chord_checks,
			     keyboard_precision_summary(precision).c_str(),
			     chord_precision_summary(keyboard_chord_precision).c_str(),
			     composition_summary(composition).c_str());
		return 1;
	}

	if (inspect_only) {
		std::printf("analyzer_maestro: inspect passed (recordings %d/%zu, windows %d, "
			    "no-candidate recordings %d, unusable %d, %s)\n",
			    recordings_with_windows, recordings.size(), tested_windows, no_candidate_recordings,
			    unusable, composition_summary(composition).c_str());
	} else {
		std::printf("analyzer_maestro: %d checks passed (recordings %d/%zu, windows %d, "
			    "read failures %d, no-candidate recordings %d, unusable %d, "
			    "note hits %d/%d, chord hits %d/%d, %s, %s, %s)\n",
			    runner.checks, recordings_with_windows, recordings.size(), tested_windows,
			    read_failures, no_candidate_recordings, unusable, recall.hits, recall.expected,
			    recall.chord_hits, recall.chord_checks,
			    keyboard_precision_summary(precision).c_str(),
			    chord_precision_summary(keyboard_chord_precision).c_str(),
			    composition_summary(composition).c_str());
	}
	return 0;
}
