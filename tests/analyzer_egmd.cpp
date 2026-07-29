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

struct DrumHit {
	double seconds = 0.0;
	int midi = 0;
	int velocity = 0;
	mao::DrumIndex category = mao::Kick;
};

bool drum_category_for_midi(int midi, mao::DrumIndex &category)
{
	switch (midi) {
	case 35:
	case 36:
		category = mao::Kick;
		return true;
	case 38:
	case 40:
		category = mao::Snare;
		return true;
	case 37:
		category = mao::Rim;
		return true;
	case 42:
	case 44:
	case 46:
		category = mao::HiHat;
		return true;
	case 49:
	case 52:
	case 55:
	case 57:
		category = mao::Crash;
		return true;
	case 41:
	case 43:
	case 45:
	case 47:
	case 48:
	case 50:
		category = mao::Tom;
		return true;
	case 51:
	case 53:
	case 59:
		category = mao::Ride;
		return true;
	default:
		return false;
	}
}

struct RawHit {
	uint64_t tick = 0;
	int midi = 0;
	int velocity = 0;
	mao::DrumIndex category = mao::Kick;
};

bool read_egmd_midi(const std::string &path, std::vector<DrumHit> &hits, std::string &error)
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
	std::vector<RawHit> raw_hits;
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

			const unsigned char event_type = status & 0xf0;
			if (event_type != 0x90 || second == 0)
				continue;

			mao::DrumIndex category = mao::Kick;
			if (!drum_category_for_midi(static_cast<int>(first), category))
				continue;
			raw_hits.push_back(RawHit{tick, static_cast<int>(first), static_cast<int>(second), category});
		}
		pos = chunk_end;
	}

	if (raw_hits.empty()) {
		error = "no usable drum note-on hits";
		return false;
	}

	const std::vector<TempoPoint> tempo_points = build_tempo_points(tempo_events, division);
	for (const RawHit &raw : raw_hits)
		hits.push_back(DrumHit{tick_to_seconds(tempo_points, raw.tick, division), raw.midi, raw.velocity,
				       raw.category});

	std::sort(hits.begin(), hits.end(), [](const DrumHit &a, const DrumHit &b) {
		if (a.seconds != b.seconds)
			return a.seconds < b.seconds;
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

std::string find_metadata_csv(const std::string &root)
{
	const std::vector<std::string> preferred = {
		"e-gmd-v1.0.0.csv",
		"egmd-v1.0.0.csv",
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
		if ((entry.name.find("e-gmd") != std::string::npos || entry.name.find("egmd") != std::string::npos) &&
		    ends_with(entry.name, ".csv"))
			return join_path(root, entry.name);
	}
	return "";
}

bool has_egmd_layout(const std::string &root)
{
	return !find_metadata_csv(root).empty();
}

std::string resolve_egmd_layout(const std::string &root)
{
	if (has_egmd_layout(root))
		return root;

	const std::vector<std::string> candidates = {
		join_path(root, "e-gmd-v1.0.0"),
		join_path(root, "e-gmd"),
		join_path(root, "EGMD"),
		join_path(root, "E-GMD"),
	};
	for (const std::string &candidate : candidates) {
		if (has_egmd_layout(candidate))
			return candidate;
	}
	return root;
}

std::string resolve_egmd_root()
{
	const char *root = std::getenv("MUSIC_ANALYZER_EGMD_ROOT");
	if (root && *root)
		return resolve_egmd_layout(root);

	root = std::getenv("EGMD_PATH");
	if (root && *root)
		return resolve_egmd_layout(root);

	const char *dataset_root = std::getenv("MUSIC_ANALYZER_DATASET_ROOT");
	if (!dataset_root || !*dataset_root)
		return "";

	const std::vector<std::string> candidates = {
		join_path(dataset_root, "e-gmd-v1.0.0"),
		join_path(dataset_root, "e-gmd"),
		join_path(dataset_root, "EGMD"),
		join_path(dataset_root, "E-GMD"),
	};
	for (const std::string &candidate : candidates) {
		if (has_egmd_layout(candidate))
			return candidate;
	}
	return resolve_egmd_layout(dataset_root);
}

struct Recording {
	std::string id;
	std::string audio_path;
	std::string midi_path;
	uint32_t sample_rate = 0;
	uint64_t frame_count = 0;
	std::vector<DrumHit> hits;
};

bool load_recording(const std::string &root, const std::string &id, const std::string &audio_filename,
		    const std::string &midi_filename, Recording &recording, std::string &error)
{
	const std::string audio_path = join_path(root, audio_filename);
	const std::string midi_path = join_path(root, midi_filename);
	WavFormat format;
	if (!read_wav_format(audio_path, format, error))
		return false;
	std::vector<DrumHit> hits;
	if (!read_egmd_midi(midi_path, hits, error))
		return false;

	recording.id = id;
	recording.audio_path = audio_path;
	recording.midi_path = midi_path;
	recording.sample_rate = format.sample_rate;
	recording.frame_count = format.frame_count;
	recording.hits = std::move(hits);
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

		std::string id = std::to_string(row);
		const auto id_column = column.find("id");
		if (id_column != column.end())
			id = fields[id_column->second];

		Recording recording;
		std::string error;
		if (!load_recording(root, id, audio_filename, midi_filename, recording, error)) {
			++unusable;
			if (unusable <= 5)
				std::fprintf(stderr, "analyzer_egmd: skipping row %d: %s\n", row, error.c_str());
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

int resolve_percent_env(const char *name, int fallback)
{
	const char *value = std::getenv(name);
	if (!value || !*value)
		return fallback;
	const int parsed = std::atoi(value);
	return parsed >= 0 && parsed <= 100 ? parsed : fallback;
}

struct CandidateWindow {
	uint64_t center_sample = 0;
	std::array<bool, mao::kDrumCount> categories = {};
	int category_count = 0;
	int hit_count = 0;
	int max_velocity = 0;
	double score = 0.0;
};

CandidateWindow candidate_window_at(const Recording &recording, double seconds)
{
	CandidateWindow candidate;
	candidate.center_sample = static_cast<uint64_t>(std::llround(seconds * recording.sample_rate));
	for (const DrumHit &hit : recording.hits) {
		if (std::abs(hit.seconds - seconds) > 0.035)
			continue;
		const std::size_t index = static_cast<std::size_t>(hit.category);
		if (!candidate.categories[index]) {
			candidate.categories[index] = true;
			++candidate.category_count;
		}
		++candidate.hit_count;
		candidate.max_velocity = std::max(candidate.max_velocity, hit.velocity);
	}
	candidate.score = static_cast<double>(candidate.category_count) * 120.0 +
			  static_cast<double>(candidate.hit_count) * 60.0 +
			  static_cast<double>(candidate.max_velocity);
	return candidate;
}

std::vector<CandidateWindow> select_candidate_windows(const Recording &recording, int max_windows)
{
	std::vector<CandidateWindow> candidates;
	for (const DrumHit &hit : recording.hits) {
		CandidateWindow candidate = candidate_window_at(recording, hit.seconds);
		if (candidate.hit_count <= 0)
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
			if (distance < static_cast<uint64_t>(recording.sample_rate / 12)) {
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

bool analyze_drum_window_sequence(const std::string &audio_path, uint64_t center_sample,
				  uint32_t recording_sample_rate, const char *analyzer_source_name,
				  mao::AnalysisSnapshot &snapshot, uint32_t &sample_rate, std::string &error)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	mao_test::Buffer buffer = {};
	const uint64_t analyzer_window_samples = settings.analysis_window_samples > 0 ?
						     settings.analysis_window_samples :
						     static_cast<uint64_t>(buffer.size());
	const uint64_t read_center_offset =
		buffer.size() > analyzer_window_samples ? (buffer.size() - analyzer_window_samples) / 2 : 0;
	const uint32_t interval_samples =
		static_cast<uint32_t>(std::lround(0.05 * static_cast<double>(recording_sample_rate)));
	for (int frame = -2; frame <= 0; ++frame) {
		const int64_t offset = static_cast<int64_t>(frame) * static_cast<int64_t>(interval_samples);
		const uint64_t frame_center =
			offset < 0 && center_sample < static_cast<uint64_t>(-offset) ?
				0 :
				static_cast<uint64_t>(static_cast<int64_t>(center_sample) + offset);
		if (!read_wav_window(audio_path, frame_center + read_center_offset, buffer, sample_rate, error))
			return false;
		settings.sample_rate = sample_rate;
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, analyzer_source_name, 0);
	}
	return true;
}

struct RecallStats {
	int hits = 0;
	int expected = 0;
};

struct DrumPrecisionStats {
	int windows = 0;
	int true_positives = 0;
	int false_positives = 0;
	int false_negatives = 0;
	int expected_categories = 0;
	int predicted_categories = 0;
	int false_positive_windows = 0;
	std::array<int, mao::kDrumCount> true_positives_by_category = {};
	std::array<int, mao::kDrumCount> false_negatives_by_category = {};
	std::array<int, mao::kDrumCount> expected_by_category = {};
	std::array<int, mao::kDrumCount> false_positives_by_category = {};
};

std::string drum_snapshot_details(const mao::AnalysisSnapshot &snapshot)
{
	std::string details = " levels";
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[96] = {};
		std::snprintf(part, sizeof(part), " %s=%.2f%s", snapshot.drums[i].label,
			      snapshot.drums[i].level, snapshot.drums[i].active ? "*" : "");
		details += part;
	}
	return details;
}

std::string drum_debug_details(const mao::AnalysisSnapshot &snapshot)
{
	std::string details;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[176] = {};
		std::snprintf(part, sizeof(part),
			      "%s%s band=%.2f seg=%.2f shape=%.2f trig=%.2f/%.2f supported=%d level=%.2f%s",
			      details.empty() ? "" : " | ", snapshot.drums[i].label,
			      snapshot.drum_debug_bands[i], snapshot.drum_debug_segment_bands[i],
			      snapshot.drum_debug_shape_scores[i], snapshot.drum_debug_trigger_scores[i],
			      snapshot.drum_debug_trigger_thresholds[i],
			      snapshot.drum_debug_shape_supported[i] ? 1 : 0, snapshot.drums[i].level,
			      snapshot.drums[i].active ? "*" : "");
		details += part;
	}
	char tail[256] = {};
	std::snprintf(tail, sizeof(tail),
		      " | rms=%.4f energy=%.2f/%.2f/%.2f transient=%.2f onset=%.2f body=%.2f/%.2f/%.2f crack=%.2f upperTom=%.2f bodyShape=%d",
		      snapshot.rms, snapshot.low_energy, snapshot.mid_energy, snapshot.high_energy,
		      snapshot.drum_debug_transient_ratio, snapshot.drum_debug_onset,
		      snapshot.drum_debug_kick_body, snapshot.drum_debug_snare_body,
		      snapshot.drum_debug_tom_body, snapshot.drum_debug_snare_crack,
		      snapshot.drum_debug_upper_tom_body, snapshot.drum_debug_body_shape);
	details += tail;
	return details;
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

void add_drum_precision_metrics(DrumPrecisionStats &stats, const mao::AnalysisSnapshot &snapshot,
				const CandidateWindow &candidate)
{
	++stats.windows;
	bool false_positive_window = false;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		const bool expected = candidate.categories[i];
		const bool predicted = snapshot.drums[i].active;
		if (expected)
			++stats.expected_categories;
		if (predicted)
			++stats.predicted_categories;
		if (expected)
			++stats.expected_by_category[i];

		if (expected && predicted) {
			++stats.true_positives;
			++stats.true_positives_by_category[i];
		} else if (expected && !predicted) {
			++stats.false_negatives;
			++stats.false_negatives_by_category[i];
		} else if (!expected && predicted) {
			++stats.false_positives;
			++stats.false_positives_by_category[i];
			false_positive_window = true;
		}
	}
	if (false_positive_window)
		++stats.false_positive_windows;
}

bool has_false_positive(const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate)
{
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!candidate.categories[i] && snapshot.drums[i].active)
			return true;
	}
	return false;
}

bool has_false_negative(const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate)
{
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (candidate.categories[i] && !snapshot.drums[i].active)
			return true;
	}
	return false;
}

std::string expected_categories_text(const CandidateWindow &candidate)
{
	static constexpr const char *kLabels[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								 "tom", "ride", "rim"};
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!candidate.categories[i])
			continue;
		if (!text.empty())
			text += ",";
		text += kLabels[i];
	}
	return text.empty() ? "-" : text;
}

std::string missing_categories_text(const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate)
{
	static constexpr const char *kLabels[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								 "tom", "ride", "rim"};
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!candidate.categories[i] || snapshot.drums[i].active)
			continue;
		if (!text.empty())
			text += ",";
		text += kLabels[i];
	}
	return text.empty() ? "-" : text;
}

std::string drum_precision_summary(const DrumPrecisionStats &stats)
{
	static constexpr const char *kLabels[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								 "tom", "ride", "rim"};
	std::string by_category;
	std::string recall_by_category;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!by_category.empty())
			by_category += "/";
		by_category += std::string(kLabels[i]) + ":" + std::to_string(stats.false_positives_by_category[i]);
		if (!recall_by_category.empty())
			recall_by_category += "/";
		recall_by_category += std::string(kLabels[i]) + ":" +
				      std::to_string(stats.true_positives_by_category[i]) + "/" +
				      std::to_string(stats.expected_by_category[i]) + "-" +
				      std::to_string(stats.false_negatives_by_category[i]);
	}

	return "drum precision " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_positives) +
	       ", drum recall " +
	       percent_string(stats.true_positives, stats.true_positives + stats.false_negatives) +
	       ", F1 " + f1_string(stats.true_positives, stats.false_positives, stats.false_negatives) +
	       ", false-positive windows " + percent_string(stats.false_positive_windows, stats.windows) +
	       ", recall by category " + recall_by_category +
	       ", fp by category " + by_category + ", tp/fp/fn " + std::to_string(stats.true_positives) +
	       "/" + std::to_string(stats.false_positives) + "/" + std::to_string(stats.false_negatives);
}

void check_recall(Runner &runner, const mao::AnalysisSnapshot &snapshot, const CandidateWindow &candidate,
		  const std::string &context, RecallStats &stats, int min_recall_percent)
{
	int expected = 0;
	int hits = 0;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!candidate.categories[i])
			continue;
		++expected;
		if (snapshot.drums[i].active)
			++hits;
	}

	stats.hits += hits;
	stats.expected += expected;
	runner.expect(expected > 0 && hits * 100 >= expected * min_recall_percent,
		      context + ": expected at least " + std::to_string(min_recall_percent) +
			      "% drum-category recall, got " + std::to_string(hits) + "/" +
			      std::to_string(expected) + drum_snapshot_details(snapshot));
}

struct CompositionStats {
	int windows = 0;
	int hit_sum = 0;
	int category_sum = 0;
	int min_hits = 0;
	int max_hits = 0;
	int min_categories = 0;
	int max_categories = 0;
};

void add_composition(CompositionStats &stats, const CandidateWindow &candidate)
{
	++stats.windows;
	stats.hit_sum += candidate.hit_count;
	stats.category_sum += candidate.category_count;
	if (stats.windows == 1) {
		stats.min_hits = candidate.hit_count;
		stats.max_hits = candidate.hit_count;
		stats.min_categories = candidate.category_count;
		stats.max_categories = candidate.category_count;
		return;
	}
	stats.min_hits = std::min(stats.min_hits, candidate.hit_count);
	stats.max_hits = std::max(stats.max_hits, candidate.hit_count);
	stats.min_categories = std::min(stats.min_categories, candidate.category_count);
	stats.max_categories = std::max(stats.max_categories, candidate.category_count);
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
		return "hits min/avg/max 0/0.00/0, categories min/avg/max 0/0.00/0";

	return "hits min/avg/max " + std::to_string(stats.min_hits) + "/" +
	       average_string(stats.hit_sum, stats.windows) + "/" + std::to_string(stats.max_hits) +
	       ", categories min/avg/max " + std::to_string(stats.min_categories) + "/" +
	       average_string(stats.category_sum, stats.windows) + "/" + std::to_string(stats.max_categories);
}

} // namespace

int main()
{
	const std::string root = resolve_egmd_root();
	if (root.empty()) {
		if (env_truthy("MUSIC_ANALYZER_EGMD_REQUIRED")) {
			std::fprintf(stderr,
				     "analyzer_egmd: real E-GMD audio required; set "
				     "MUSIC_ANALYZER_EGMD_ROOT, EGMD_PATH, or MUSIC_ANALYZER_DATASET_ROOT\n");
			return 1;
		}
		std::printf("analyzer_egmd: skipped, set MUSIC_ANALYZER_EGMD_ROOT to a local E-GMD dataset\n");
		return 0;
	}
	if (!is_directory(root)) {
		std::fprintf(stderr, "analyzer_egmd: `%s` is not a directory\n", root.c_str());
		return 1;
	}

	std::vector<Recording> recordings;
	int unusable = 0;
	collect_recordings(root, recordings, unusable);
	std::sort(recordings.begin(), recordings.end(), [](const Recording &a, const Recording &b) {
		return a.id < b.id;
	});

	const int required_recordings = resolve_positive_int_env("MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS", 20);
	const int max_windows_per_recording =
		resolve_positive_int_env("MUSIC_ANALYZER_EGMD_MAX_WINDOWS_PER_RECORDING", 4);
	const int default_required_windows = std::min(required_recordings * 4,
						      max_windows_per_recording * required_recordings);
	const int required_windows =
		resolve_positive_int_env("MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS", default_required_windows);
	const int min_recall_percent = resolve_percent_env("MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT", 35);
	const int min_window_recall_percent =
		resolve_percent_env("MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT", min_recall_percent);
	const int min_precision_percent = resolve_percent_env("MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT", 50);
	const int max_false_positive_windows_percent =
		resolve_percent_env("MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT", 75);
	const bool inspect_only = env_truthy("MUSIC_ANALYZER_EGMD_INSPECT_ONLY");
	const bool verbose_false_positives = env_truthy("MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVES");
	const int verbose_false_positive_limit =
		resolve_positive_int_env("MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVE_LIMIT", 24);
	const bool verbose_misses = env_truthy("MUSIC_ANALYZER_EGMD_VERBOSE_MISSES");
	const int verbose_miss_limit = resolve_positive_int_env("MUSIC_ANALYZER_EGMD_VERBOSE_MISS_LIMIT", 24);
	const char *analyzer_source_name = std::getenv("MUSIC_ANALYZER_EGMD_SOURCE_NAME");
	if (!analyzer_source_name || !*analyzer_source_name)
		analyzer_source_name = "E-GMD drums";

	Runner runner;
	RecallStats recall;
	DrumPrecisionStats precision;
	CompositionStats composition;
	int recordings_with_windows = 0;
	int tested_windows = 0;
	int read_failures = 0;
	int no_candidate_recordings = 0;
	int verbose_false_positive_lines = 0;
	int verbose_miss_lines = 0;

	for (const Recording &recording : recordings) {
		const std::vector<CandidateWindow> candidates =
			select_candidate_windows(recording, max_windows_per_recording);
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

			mao::AnalysisSnapshot snapshot;
			uint32_t sample_rate = 0;
			std::string error;
			if (!analyze_drum_window_sequence(recording.audio_path, candidate.center_sample,
							  recording.sample_rate, analyzer_source_name, snapshot,
							  sample_rate, error)) {
				++read_failures;
				runner.expect(false, "E-GMD " + recording.id + " at sample " +
							     std::to_string(candidate.center_sample) + ": " + error);
				continue;
			}

			check_recall(runner, snapshot, candidate,
				     "E-GMD " + recording.id + " at sample " +
					     std::to_string(candidate.center_sample),
				     recall, min_window_recall_percent);
			if (verbose_misses && verbose_miss_lines < verbose_miss_limit &&
			    has_false_negative(snapshot, candidate)) {
				std::fprintf(stderr,
					     "E-GMD miss %s sample %llu expected %s missing %s: %s %s\n",
					     recording.id.c_str(),
					     static_cast<unsigned long long>(candidate.center_sample),
					     expected_categories_text(candidate).c_str(),
					     missing_categories_text(snapshot, candidate).c_str(),
					     drum_snapshot_details(snapshot).c_str(),
					     drum_debug_details(snapshot).c_str());
				++verbose_miss_lines;
			}
			if (verbose_false_positives && verbose_false_positive_lines < verbose_false_positive_limit &&
			    has_false_positive(snapshot, candidate)) {
				std::fprintf(stderr,
					     "E-GMD false-positive %s sample %llu expected %s: %s\n",
					     recording.id.c_str(),
					     static_cast<unsigned long long>(candidate.center_sample),
					     expected_categories_text(candidate).c_str(),
					     drum_debug_details(snapshot).c_str());
				++verbose_false_positive_lines;
			}
			add_drum_precision_metrics(precision, snapshot, candidate);
		}

		if (recording_windows > 0)
			++recordings_with_windows;
	}

	if (recordings.empty()) {
		std::fprintf(stderr,
			     "analyzer_egmd: no E-GMD WAV/MIDI pairs found under `%s`; expected "
			     "e-gmd-v*.csv metadata with audio_filename and midi_filename columns\n",
			     root.c_str());
		return 1;
	}

	runner.expect(recordings_with_windows >= required_recordings,
		      "E-GMD coverage: expected at least " + std::to_string(required_recordings) +
			      " recordings with candidate drum windows, got " +
			      std::to_string(recordings_with_windows));
	runner.expect(tested_windows >= required_windows,
		      "E-GMD coverage: expected at least " + std::to_string(required_windows) +
			      " candidate windows, got " + std::to_string(tested_windows));
	runner.expect(composition.windows == tested_windows,
		      "E-GMD composition: expected composition stats for every window, got " +
			      std::to_string(composition.windows) + "/" + std::to_string(tested_windows));
	if (!inspect_only) {
		runner.expect(recall.expected > 0 && recall.hits * 100 >= recall.expected * min_recall_percent,
			      "E-GMD drum-category recall: expected >=" + std::to_string(min_recall_percent) +
				      "%, got " + std::to_string(recall.hits) + "/" +
				      std::to_string(recall.expected));
		runner.expect(precision.expected_categories > 0,
			      "E-GMD drum precision: expected at least one category check");
		if (precision.expected_categories > 0) {
			runner.expect(percentage_floor(precision.true_positives,
						       precision.true_positives + precision.false_positives) >=
					      min_precision_percent,
				      "E-GMD drum precision: expected >=" +
					      std::to_string(min_precision_percent) + "%, got " +
					      percent_string(precision.true_positives,
							     precision.true_positives +
								     precision.false_positives) +
					      " (" + drum_precision_summary(precision) + ")");
			runner.expect(percentage_floor(precision.false_positive_windows, precision.windows) <=
					      max_false_positive_windows_percent,
				      "E-GMD drum false-positive windows: expected <=" +
					      std::to_string(max_false_positive_windows_percent) + "%, got " +
					      percent_string(precision.false_positive_windows, precision.windows) +
					      " (" + drum_precision_summary(precision) + ")");
		}
	}

	if (runner.failures != 0) {
		std::fprintf(stderr,
			     "analyzer_egmd: %d/%d checks failed (recordings %d/%zu, windows %d, "
			     "read failures %d, no-candidate recordings %d, unusable %d, "
			     "drum hits %d/%d, %s, %s)\n",
			     runner.failures, runner.checks, recordings_with_windows, recordings.size(),
			     tested_windows, read_failures, no_candidate_recordings, unusable, recall.hits,
			     recall.expected, drum_precision_summary(precision).c_str(),
			     composition_summary(composition).c_str());
		return 1;
	}

	if (inspect_only) {
		std::printf("analyzer_egmd: inspect passed (recordings %d/%zu, windows %d, "
			    "no-candidate recordings %d, unusable %d, %s)\n",
			    recordings_with_windows, recordings.size(), tested_windows, no_candidate_recordings,
			    unusable, composition_summary(composition).c_str());
	} else {
		std::printf("analyzer_egmd: %d checks passed (recordings %d/%zu, windows %d, "
			    "read failures %d, no-candidate recordings %d, unusable %d, "
			    "drum hits %d/%d, %s, %s)\n",
			    runner.checks, recordings_with_windows, recordings.size(), tested_windows,
			    read_failures, no_candidate_recordings, unusable, recall.hits, recall.expected,
			    drum_precision_summary(precision).c_str(), composition_summary(composition).c_str());
	}
	return 0;
}
