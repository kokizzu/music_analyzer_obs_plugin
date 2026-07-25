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
	std::string family;
	int program = 0;
	std::string program_name;
	int midi = 0;
	std::string path;
	std::string note;
};

struct RawNoteAttributes {
	float expected_peak = 0.0f;
	float expected_ratio = 0.0f;
	float tuned_peak = 0.0f;
	float tuned_ratio = 0.0f;
	float tuned_cent_offset = 0.0f;
	float tuned_abs_cent_offset = 0.0f;
	int local_best_midi = -1;
	float local_best_peak = 0.0f;
	int expected_rank = 0;
	float prev_ratio = 0.0f;
	float next_ratio = 0.0f;
	float octave_down_ratio = 0.0f;
	float octave_up_ratio = 0.0f;
	float fifth_up_ratio = 0.0f;
	float second_octave_up_ratio = 0.0f;
	float upper_major_third_ratio = 0.0f;
	float upper_fifth_ratio = 0.0f;
	float third_octave_up_ratio = 0.0f;
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
		if (header) {
			header = false;
			continue;
		}
		if (line.empty())
			continue;
		const std::vector<std::string> fields = split_tab(line);
		if (fields.size() < 6)
			continue;
		SampleRow row;
		row.family = fields[0];
		row.program = std::atoi(fields[1].c_str());
		row.program_name = fields[2];
		row.midi = std::atoi(fields[3].c_str());
		row.path = fields[4];
		row.note = fields[5];
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

bool make_sample_buffer(const std::vector<float> &samples, uint32_t sample_rate, mao_test::Buffer &buffer,
			float target_peak, bool transient)
{
	buffer.fill(0.0f);
	if (samples.empty() || sample_rate == 0)
		return false;

	float peak = 0.0f;
	for (float sample : samples)
		peak = std::max(peak, std::abs(sample));
	if (peak < 1.0e-5f)
		return false;

	const std::size_t onset = first_audible_sample(samples, peak);
	std::size_t start = onset;
	if (!transient) {
		const std::size_t sustain_offset = static_cast<std::size_t>(static_cast<double>(sample_rate) * 0.080);
		start = std::min(samples.size() - 1, onset + sustain_offset);
	}
	const std::size_t count = std::min<std::size_t>(buffer.size(), samples.size() - start);
	if (count == 0)
		return false;

	float window_peak = 0.0f;
	for (std::size_t i = 0; i < count; ++i)
		window_peak = std::max(window_peak, std::abs(samples[start + i]));
	if (window_peak < 1.0e-5f)
		return false;

	const float gain = std::min(24.0f, target_peak / window_peak);
	const std::size_t insert = transient ? std::min<std::size_t>(1536, buffer.size() / 3) : 0;
	const std::size_t copy_count = std::min<std::size_t>(count, buffer.size() - insert);
	for (std::size_t i = 0; i < copy_count; ++i)
		buffer[insert + i] = std::clamp(samples[start + i] * gain, -1.0f, 1.0f);
	return true;
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

mao::AnalysisSnapshot analyze_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate,
				     mao::AnalysisInputMode mode, const char *source, float window_seconds,
				     int frames = 4)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = window_seconds;
	settings.input_mode = mode;

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < frames; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
	return snapshot;
}

mao::AnalysisSnapshot analyze_drum_buffer(const mao_test::Buffer &buffer, uint32_t sample_rate, float window_seconds)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = window_seconds;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	mao_test::Buffer warmup = {};
	mao_test::add_midi_note(warmup, 60, 0.006f);
	mao_test::add_midi_note(warmup, 64, 0.004f);
	mao_test::add_midi_note(warmup, 67, 0.003f);

	for (int i = 0; i < 4; ++i)
		(void)engine.analyze(warmup.data(), warmup.size(), settings, "GM drum kit", 0);
	return engine.analyze(buffer.data(), buffer.size(), settings, "GM drum kit", 0);
}

std::string debug_note_label(int midi)
{
	if (midi < mao::kFirstAnalyzedMidi || midi > mao::kLastAnalyzedMidi)
		return "--";
	return mao_test::note_label(midi);
}

const char *instrument_kind_name(mao::InstrumentKind kind)
{
	switch (kind) {
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
	default:
		return "amb";
	}
}

mao_test::Buffer centered_hann_buffer(const mao_test::Buffer &buffer)
{
	mao_test::Buffer windowed = {};
	if (buffer.size() < 2)
		return windowed;

	double sum = 0.0;
	for (float sample : buffer)
		sum += sample;
	const float mean = static_cast<float>(sum / static_cast<double>(buffer.size()));

	for (std::size_t i = 0; i < buffer.size(); ++i) {
		const float phase =
			2.0f * mao_test::kPi * static_cast<float>(i) / static_cast<float>(buffer.size() - 1);
		const float window = 0.5f - 0.5f * std::cos(phase);
		windowed[i] = (buffer[i] - mean) * window;
	}
	return windowed;
}

float raw_goertzel_frequency(const mao_test::Buffer &windowed, uint32_t sample_rate, float frequency)
{
	if (sample_rate == 0 || windowed.size() < 2 || frequency <= 0.0f)
		return 0.0f;

	const float coeff = 2.0f * std::cos(2.0f * mao_test::kPi * frequency /
					     static_cast<float>(sample_rate));
	float s1 = 0.0f;
	float s2 = 0.0f;
	for (float x : windowed) {
		const float s0 = x + coeff * s1 - s2;
		s2 = s1;
		s1 = s0;
	}

	return std::sqrt(std::max(0.0f, s1 * s1 + s2 * s2 - coeff * s1 * s2));
}

float raw_goertzel_midi(const mao_test::Buffer &windowed, uint32_t sample_rate, int midi)
{
	if (midi < mao::kFirstAnalyzedMidi || midi > mao::kLastAnalyzedMidi)
		return 0.0f;
	return raw_goertzel_frequency(windowed, sample_rate, mao_test::midi_frequency(midi));
}

RawNoteAttributes measure_raw_note_attributes(const mao_test::Buffer &buffer, uint32_t sample_rate,
					      int expected_midi)
{
	RawNoteAttributes attributes;
	if (sample_rate == 0 || buffer.size() < 2 || expected_midi < mao::kFirstAnalyzedMidi ||
	    expected_midi > mao::kLastAnalyzedMidi)
		return attributes;

	const mao_test::Buffer windowed = centered_hann_buffer(buffer);
	attributes.expected_peak = raw_goertzel_midi(windowed, sample_rate, expected_midi);

	int stronger_or_equal = 0;
	for (int midi = std::max(mao::kFirstAnalyzedMidi, expected_midi - 12);
	     midi <= std::min(mao::kLastAnalyzedMidi, expected_midi + 12); ++midi) {
		const float peak = raw_goertzel_midi(windowed, sample_rate, midi);
		if (peak > attributes.local_best_peak) {
			attributes.local_best_peak = peak;
			attributes.local_best_midi = midi;
		}
		if (midi != expected_midi && peak >= attributes.expected_peak)
			++stronger_or_equal;
	}
	attributes.expected_rank = stronger_or_equal + 1;

	const float denominator = std::max(attributes.local_best_peak, 1.0e-9f);
	attributes.expected_ratio = std::clamp(attributes.expected_peak / denominator, 0.0f, 1.0f);
	attributes.prev_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi - 1) / denominator,
			   0.0f, 1.0f);
	attributes.next_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 1) / denominator,
			   0.0f, 1.0f);
	attributes.octave_down_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi - 12) / denominator,
			   0.0f, 1.0f);
	attributes.octave_up_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 12) / denominator,
			   0.0f, 1.0f);
	attributes.fifth_up_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 19) / denominator,
			   0.0f, 1.0f);
	attributes.second_octave_up_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 24) / denominator,
			   0.0f, 1.0f);
	attributes.upper_major_third_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 28) / denominator,
			   0.0f, 1.0f);
	attributes.upper_fifth_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 31) / denominator,
			   0.0f, 1.0f);
	attributes.third_octave_up_ratio =
		std::clamp(raw_goertzel_midi(windowed, sample_rate, expected_midi + 36) / denominator,
			   0.0f, 1.0f);

	static constexpr float kCentOffsets[] = {-18.0f, -9.0f, 0.0f, 9.0f, 18.0f};
	for (float cents : kCentOffsets) {
		const float frequency =
			mao_test::midi_frequency(expected_midi) * std::pow(2.0f, cents / 1200.0f);
		const float peak = raw_goertzel_frequency(windowed, sample_rate, frequency);
		if (peak > attributes.tuned_peak) {
			attributes.tuned_peak = peak;
			attributes.tuned_cent_offset = cents;
		}
	}
	attributes.tuned_ratio = std::clamp(attributes.tuned_peak / denominator, 0.0f, 1.0f);
	attributes.tuned_abs_cent_offset = std::abs(attributes.tuned_cent_offset);
	return attributes;
}

const mao::FullMixDebugCandidate *debug_candidate_for_pitch(const mao::AnalysisSnapshot &snapshot, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (debug.midi == midi)
			return &debug;
	}
	const mao::FullMixDebugCandidate *best = nullptr;
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (debug.midi < mao::kFirstAnalyzedMidi || debug.midi > mao::kLastAnalyzedMidi ||
		    ((debug.midi % 12) + 12) % 12 != pitch_class)
			continue;
		if (!best || debug.owner != mao::InstrumentKind::Ambiguous ||
		    best->owner == mao::InstrumentKind::Ambiguous) {
			if (!best || debug.ownership_confidence > best->ownership_confidence)
				best = &debug;
		}
	}
	return best;
}

const char *category_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								"tom", "ride", "rim"};
	return index < mao::kDrumCount ? kNames[index] : "unknown";
}

const char *bool_cell(bool value)
{
	return value ? "1" : "0";
}

void append_tsv(std::ostringstream &line, const std::string &value)
{
	line << '\t';
	for (char ch : value)
		line << (ch == '\t' || ch == '\n' || ch == '\r' ? ' ' : ch);
}

void append_tsv(std::ostringstream &line, const char *value)
{
	append_tsv(line, std::string(value ? value : ""));
}

template <typename T> void append_tsv(std::ostringstream &line, const T &value)
{
	line << '\t' << value;
}

float grid_pitch_class_level(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	float level = 0.0f;
	if (grid.cells[pitch_class].active)
		level = std::max(level, grid.cells[pitch_class].level);
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max(level, row[pitch_class].level);
	}
	return level;
}

int grid_pitch_class_midi(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	int best_midi = -1;
	float best_level = -1.0f;
	auto consider = [&](const mao::NoteCell &cell) {
		if (!cell.active || cell.midi < mao::kFirstAnalyzedMidi || cell.midi > mao::kLastAnalyzedMidi)
			return;
		if (cell.level > best_level) {
			best_level = cell.level;
			best_midi = cell.midi;
		}
	};
	consider(grid.cells[pitch_class]);
	for (const auto &row : grid.rows)
		consider(row[pitch_class]);
	return best_midi;
}

int grid_primary_pitch_class_midi(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	for (const auto &row : grid.rows) {
		const mao::NoteCell &cell = row[pitch_class];
		if (cell.active && cell.midi >= mao::kFirstAnalyzedMidi && cell.midi <= mao::kLastAnalyzedMidi)
			return cell.midi;
	}
	const mao::NoteCell &cell = grid.cells[pitch_class];
	if (cell.active && cell.midi >= mao::kFirstAnalyzedMidi && cell.midi <= mao::kLastAnalyzedMidi)
		return cell.midi;
	return -1;
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

std::string active_drum_list(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		if (!snapshot.drums[i].active)
			continue;
		if (!text.empty())
			text += ",";
		text += category_name(i);
	}
	return text.empty() ? "--" : text;
}

void print_attribute_header(std::ostream &out)
{
	out << "kind\tstatus\tfamily\texpected_family\tprogram\tprogram_name\tnote\tmidi\tpath\twindow_ms"
	    << "\tdetected_expected_row\tdetected_anywhere\texpected_level"
	    << "\tdisplay_note\tdisplay_midi\tdisplay_delta"
	    << "\tprimary_note\tprimary_midi\tprimary_delta"
	    << "\tbass_level\tpiano_level\tguitar_level\tvocal_level\tother_level\tamb_level"
	    << "\tbass_notes\tpiano_notes\tguitar_notes\tvocal_notes\tother_notes\tamb_notes"
	    << "\tbass_label\tpiano_label\tguitar_label\tvocal_label\tother_label"
	    << "\tglobal_chord\tkeyboard_chord\tguitar_chord\tother_chord"
	    << "\trms\tlow\tmid\thigh"
	    << "\traw_expected_peak\traw_expected_ratio\traw_tuned_peak\traw_tuned_ratio"
	    << "\traw_tuned_cent_offset\traw_tuned_abs_cent_offset"
	    << "\traw_local_best_note\traw_local_best_midi\traw_local_best_peak\traw_expected_rank"
	    << "\traw_prev_ratio\traw_next_ratio\traw_octave_down_ratio\traw_octave_up_ratio"
	    << "\traw_fifth_up_ratio\traw_second_octave_up_ratio\traw_upper_major_third_ratio"
	    << "\traw_upper_fifth_ratio\traw_third_octave_up_ratio"
	    << "\tdebug_note\tdebug_midi\tdebug_owner\tdebug_conf"
	    << "\tbass_score\tkeyboard_score\tguitar_score\tvocal_score\tother_score"
	    << "\tspectral_level\tpitch_confidence\tperiodicity\tharmonicity\tfit_error"
	    << "\tcentroid\tslope\tnoise\tthird_octave_ratio"
	    << "\tpartial1\tpartial2\tpartial3\tpartial4\tpartial5"
	    << "\tdebug_count\tdebug_candidates"
	    << "\tdrum_expected\tdrum_active\tdrum_level\tdrum_active_list"
	    << "\tkick_level\tsnare_level\thihat_level\tcrash_level\ttom_level\tride_level\trim_level"
	    << "\tkick_trigger\tsnare_trigger\thihat_trigger\tcrash_trigger\ttom_trigger\tride_trigger\trim_trigger"
	    << "\tkick_threshold\tsnare_threshold\thihat_threshold\tcrash_threshold\ttom_threshold"
	    << "\tride_threshold\trim_threshold"
	    << "\ttransient\tonset\tkick_body\tsnare_body\ttom_body\tsnare_crack\tupper_tom\tbody_shape\n";
}

void append_snapshot_attribute_fields(std::ostringstream &line, const mao::AnalysisSnapshot &snapshot,
				      int expected_midi)
{
	append_tsv(line, grid_pitch_class_level(snapshot.bass_notes, expected_midi));
	append_tsv(line, grid_pitch_class_level(snapshot.keyboard_notes, expected_midi));
	append_tsv(line, grid_pitch_class_level(snapshot.guitar_notes, expected_midi));
	append_tsv(line, grid_pitch_class_level(snapshot.vocal_notes, expected_midi));
	append_tsv(line, grid_pitch_class_level(snapshot.other_notes, expected_midi));
	append_tsv(line, grid_pitch_class_level(snapshot.ambiguous_notes, expected_midi));
	append_tsv(line, grid_debug_label(snapshot.bass_notes));
	append_tsv(line, grid_debug_label(snapshot.keyboard_notes));
	append_tsv(line, grid_debug_label(snapshot.guitar_notes));
	append_tsv(line, grid_debug_label(snapshot.vocal_notes));
	append_tsv(line, grid_debug_label(snapshot.other_notes));
	append_tsv(line, grid_debug_label(snapshot.ambiguous_notes));
	append_tsv(line, snapshot.bass.label);
	append_tsv(line, snapshot.keyboard.label);
	append_tsv(line, snapshot.guitar.label);
	append_tsv(line, snapshot.vocal.label);
	append_tsv(line, snapshot.other.label);
	append_tsv(line, snapshot.global_chord.label);
	append_tsv(line, snapshot.keyboard_chord.label);
	append_tsv(line, snapshot.guitar_chord.label);
	append_tsv(line, snapshot.other_chord.label);
	append_tsv(line, snapshot.rms);
	append_tsv(line, snapshot.low_energy);
	append_tsv(line, snapshot.mid_energy);
	append_tsv(line, snapshot.high_energy);
}

void append_raw_note_attribute_fields(std::ostringstream &line, const RawNoteAttributes *raw)
{
	if (!raw) {
		for (int i = 0; i < 19; ++i)
			append_tsv(line, "");
		return;
	}

	append_tsv(line, raw->expected_peak);
	append_tsv(line, raw->expected_ratio);
	append_tsv(line, raw->tuned_peak);
	append_tsv(line, raw->tuned_ratio);
	append_tsv(line, raw->tuned_cent_offset);
	append_tsv(line, raw->tuned_abs_cent_offset);
	append_tsv(line, debug_note_label(raw->local_best_midi));
	append_tsv(line, raw->local_best_midi);
	append_tsv(line, raw->local_best_peak);
	append_tsv(line, raw->expected_rank);
	append_tsv(line, raw->prev_ratio);
	append_tsv(line, raw->next_ratio);
	append_tsv(line, raw->octave_down_ratio);
	append_tsv(line, raw->octave_up_ratio);
	append_tsv(line, raw->fifth_up_ratio);
	append_tsv(line, raw->second_octave_up_ratio);
	append_tsv(line, raw->upper_major_third_ratio);
	append_tsv(line, raw->upper_fifth_ratio);
	append_tsv(line, raw->third_octave_up_ratio);
}

void append_debug_candidate_fields(std::ostringstream &line, const mao::FullMixDebugCandidate *debug)
{
	if (!debug) {
		for (int i = 0; i < 23; ++i)
			append_tsv(line, "");
		return;
	}

	append_tsv(line, debug_note_label(debug->midi));
	append_tsv(line, debug->midi);
	append_tsv(line, instrument_kind_name(debug->owner));
	append_tsv(line, debug->ownership_confidence);
	append_tsv(line, debug->bass_score);
	append_tsv(line, debug->keyboard_score);
	append_tsv(line, debug->guitar_score);
	append_tsv(line, debug->vocal_score);
	append_tsv(line, debug->other_score);
	append_tsv(line, debug->spectral_level);
	append_tsv(line, debug->pitch_confidence);
	append_tsv(line, debug->periodicity);
	append_tsv(line, debug->harmonicity);
	append_tsv(line, debug->harmonic_fit_error);
	append_tsv(line, debug->spectral_centroid);
	append_tsv(line, debug->spectral_slope);
	append_tsv(line, debug->local_noise_level);
	append_tsv(line, debug->third_octave_ratio);
	for (float ratio : debug->harmonic_ratios)
		append_tsv(line, ratio);
}

void append_full_mix_debug_summary_fields(std::ostringstream &line, const mao::AnalysisSnapshot &snapshot)
{
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	append_tsv(line, count);
	std::string summary;
	const std::size_t limit = std::min<std::size_t>(count, 8);
	for (std::size_t i = 0; i < limit; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		char part[160] = {};
		std::snprintf(part, sizeof(part), "%s%s/%s/%.3f/b%.3f/k%.3f/g%.3f/v%.3f/o%.3f",
			      summary.empty() ? "" : ",", debug_note_label(debug.midi).c_str(),
			      instrument_kind_name(debug.owner), debug.ownership_confidence, debug.bass_score,
			      debug.keyboard_score, debug.guitar_score, debug.vocal_score,
			      debug.other_score);
		summary += part;
	}
	append_tsv(line, summary);
}

void append_drum_attribute_fields(std::ostringstream &line, const mao::AnalysisSnapshot &snapshot,
				  std::size_t expected)
{
	append_tsv(line, category_name(expected));
	append_tsv(line, bool_cell(snapshot.drums[expected].active));
	append_tsv(line, snapshot.drums[expected].level);
	append_tsv(line, active_drum_list(snapshot));
	for (std::size_t i = 0; i < mao::kDrumCount; ++i)
		append_tsv(line, snapshot.drums[i].level);
	for (std::size_t i = 0; i < mao::kDrumCount; ++i)
		append_tsv(line, snapshot.drum_debug_trigger_scores[i]);
	for (std::size_t i = 0; i < mao::kDrumCount; ++i)
		append_tsv(line, snapshot.drum_debug_trigger_thresholds[i]);
	append_tsv(line, snapshot.drum_debug_transient_ratio);
	append_tsv(line, snapshot.drum_debug_onset);
	append_tsv(line, snapshot.drum_debug_kick_body);
	append_tsv(line, snapshot.drum_debug_snare_body);
	append_tsv(line, snapshot.drum_debug_tom_body);
	append_tsv(line, snapshot.drum_debug_snare_crack);
	append_tsv(line, snapshot.drum_debug_upper_tom_body);
	append_tsv(line, snapshot.drum_debug_body_shape);
}

void append_note_attribute_row(std::ostream &out, const std::string &suite_family, const SampleRow &row,
			       const mao::AnalysisSnapshot &snapshot, float window_seconds,
			       bool detected_expected_row, bool detected_anywhere,
			       const RawNoteAttributes &raw,
			       const mao::FullMixDebugCandidate *debug)
{
	const float expected_level = grid_pitch_class_level(family_grid(snapshot, suite_family), row.midi);
	const std::string status = detected_expected_row ? "hit" :
				   detected_anywhere ? "ownership_miss" :
						      "miss";
	std::ostringstream line;
	line << "note";
	append_tsv(line, status);
	append_tsv(line, suite_family);
	append_tsv(line, row.family);
	append_tsv(line, row.program);
	append_tsv(line, row.program_name);
	append_tsv(line, row.note);
	append_tsv(line, row.midi);
	append_tsv(line, row.path);
	append_tsv(line, static_cast<int>(std::lround(window_seconds * 1000.0f)));
	append_tsv(line, bool_cell(detected_expected_row));
	append_tsv(line, bool_cell(detected_anywhere));
	append_tsv(line, expected_level);
	const int display_midi = grid_pitch_class_midi(family_grid(snapshot, suite_family), row.midi);
	if (display_midi >= 0) {
		append_tsv(line, debug_note_label(display_midi));
		append_tsv(line, display_midi);
		append_tsv(line, display_midi - row.midi);
	} else {
		append_tsv(line, "");
		append_tsv(line, "");
		append_tsv(line, "");
	}
	const int primary_midi = grid_primary_pitch_class_midi(family_grid(snapshot, suite_family), row.midi);
	if (primary_midi >= 0) {
		append_tsv(line, debug_note_label(primary_midi));
		append_tsv(line, primary_midi);
		append_tsv(line, primary_midi - row.midi);
	} else {
		append_tsv(line, "");
		append_tsv(line, "");
		append_tsv(line, "");
	}
	append_snapshot_attribute_fields(line, snapshot, row.midi);
	append_raw_note_attribute_fields(line, &raw);
	append_debug_candidate_fields(line, debug);
	append_full_mix_debug_summary_fields(line, snapshot);
	for (int i = 0; i < 33; ++i)
		append_tsv(line, "");
	out << line.str() << '\n';
}

void append_drum_attribute_row(std::ostream &out, const SampleRow &row,
			       const mao::AnalysisSnapshot &snapshot, float window_seconds,
			       std::size_t expected)
{
	const bool detected = snapshot.drums[expected].active;
	std::ostringstream line;
	line << "drum";
	append_tsv(line, detected ? "hit" : "miss");
	append_tsv(line, "drum");
	append_tsv(line, row.family);
	append_tsv(line, row.program);
	append_tsv(line, row.program_name);
	append_tsv(line, row.note);
	append_tsv(line, row.midi);
	append_tsv(line, row.path);
	append_tsv(line, static_cast<int>(std::lround(window_seconds * 1000.0f)));
	append_tsv(line, bool_cell(detected));
	append_tsv(line, bool_cell(detected));
	append_tsv(line, snapshot.drums[expected].level);
	for (int i = 0; i < 6; ++i)
		append_tsv(line, "");
	append_snapshot_attribute_fields(line, snapshot, row.midi);
	append_raw_note_attribute_fields(line, nullptr);
	append_debug_candidate_fields(line, nullptr);
	append_full_mix_debug_summary_fields(line, snapshot);
	append_drum_attribute_fields(line, snapshot, expected);
	out << line.str() << '\n';
}

bool env_filter_active()
{
	return std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY") != nullptr ||
	       std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM") != nullptr ||
	       std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH") != nullptr;
}

bool filter_matches(const std::string &suite_family, const SampleRow &row)
{
	if (const char *family = std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY")) {
		if (suite_family != family && row.family != family)
			return false;
	}
	if (const char *program = std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM")) {
		if (row.program_name != program)
			return false;
	}
	if (const char *path = std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH")) {
		if (row.path.find(path) == std::string::npos)
			return false;
	}
	return true;
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

bool shard_includes_row(std::size_t row_index, int shard_count, int shard_index)
{
	if (shard_count <= 1)
		return true;
	return static_cast<int>(row_index % static_cast<std::size_t>(shard_count)) == shard_index;
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

std::string drum_details(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[192] = {};
		std::snprintf(part, sizeof(part),
			      "%s%s=%.2f%s band=%.2f seg=%.2f shape=%.2f trig=%.2f/%.2f sup=%d",
			      text.empty() ? "" : " ", category_name(i), snapshot.drums[i].level,
			      snapshot.drums[i].active ? "*" : "", snapshot.drum_debug_bands[i],
			      snapshot.drum_debug_segment_bands[i], snapshot.drum_debug_shape_scores[i],
			      snapshot.drum_debug_trigger_scores[i], snapshot.drum_debug_trigger_thresholds[i],
			      snapshot.drum_debug_shape_supported[i] ? 1 : 0);
		text += part;
	}
	char tail[320] = {};
	std::snprintf(tail, sizeof(tail),
		      " transient=%.2f onset=%.2f energy=%.2f/%.2f/%.2f body=%.2f/%.2f/%.2f crack=%.2f upperTom=%.2f bodyShape=%d",
		      snapshot.drum_debug_transient_ratio, snapshot.drum_debug_onset, snapshot.low_energy,
		      snapshot.mid_energy, snapshot.high_energy, snapshot.drum_debug_kick_body,
		      snapshot.drum_debug_snare_body, snapshot.drum_debug_tom_body,
		      snapshot.drum_debug_snare_crack, snapshot.drum_debug_upper_tom_body,
		      snapshot.drum_debug_body_shape);
	text += tail;
	return text;
}

bool load_sample(const std::string &root, const std::string &family_dir, const SampleRow &row,
		 mao_test::Buffer &buffer, uint32_t &sample_rate, float target_peak, bool transient,
		 std::string &error)
{
	std::vector<float> samples;
	const std::string path = join_path(join_path(root, family_dir), row.path);
	if (!read_wav_mono(path, samples, sample_rate, error))
		return false;
	if (!make_sample_buffer(samples, sample_rate, buffer, target_peak, transient)) {
		error = "empty or silent sample";
		return false;
	}
	return true;
}

const SampleRow *find_row(const std::vector<SampleRow> &rows, const std::string &family, int midi)
{
	for (const SampleRow &row : rows) {
		if (row.family == family && row.midi == midi)
			return &row;
	}
	return nullptr;
}

bool expects_full_mix_vocal_recovery(const std::string &suite_family, const SampleRow &row)
{
	if (suite_family != "vocals")
		return false;
	if (row.program_name == "choir_aahs" && (row.note == "B3" || row.note == "G3"))
		return true;
	if (row.program_name == "voice_oohs" && row.note == "G3")
		return true;
	if (row.program_name == "synth_voice" && row.note == "C4")
		return true;
	if (row.program_name == "voice_lead" && row.note == "C5")
		return true;
	return false;
}

bool expects_full_mix_vocal_primary_octave_recovery(const std::string &suite_family,
						    const SampleRow &row)
{
	return suite_family == "vocals" && row.program_name == "voice_oohs" &&
	       (row.note == "C4" || row.note == "D4" || row.note == "E4");
}

bool expects_full_mix_vocal_display_octave_recovery(const std::string &suite_family,
						    const SampleRow &row)
{
	return suite_family == "vocals" && row.program_name == "voice_oohs" && row.note == "E4";
}

bool expects_full_mix_bass_primary_octave_recovery(const std::string &suite_family,
						   const SampleRow &row)
{
	if (suite_family != "bass")
		return false;
	if (row.note == "G3" || row.note == "B3" || row.note == "C4" || row.note == "E4")
		return true;
	if (row.program_name == "pick_bass" && row.note == "G2") {
		return row.path == "034_pick_bass_043_G2_v100_d0900.wav" ||
		       row.path == "034_pick_bass_043_G2_v088_d1100.wav" ||
		       row.path == "034_pick_bass_043_G2_v100_d1100.wav" ||
		       row.path == "034_pick_bass_043_G2_v088_d0900.wav";
	}
	return false;
}

bool expects_full_mix_keyboard_primary_octave_recovery(const std::string &suite_family,
						       const SampleRow &row)
{
	return suite_family == "piano" &&
	       ((row.program_name == "acoustic_grand" && row.note == "E2") ||
		(row.program_name == "bright_acoustic" && row.note == "G2") ||
		(row.program_name == "electric_piano_1" && row.note == "G3") ||
		(row.program_name == "harpsichord" && row.note == "G5"));
}

bool expects_full_mix_guitar_primary_octave_recovery(const std::string &suite_family,
						     const SampleRow &row)
{
	if (suite_family != "guitar")
		return false;
	if (row.program_name == "jazz_guitar" && (row.note == "E3" || row.note == "E4"))
		return true;
	if ((row.program_name == "nylon_guitar" || row.program_name == "steel_guitar") &&
	    row.note == "E2")
		return true;
	if ((row.program_name == "steel_guitar" || row.program_name == "clean_guitar") &&
	    row.note == "G2")
		return true;
	if (row.program_name == "clean_guitar" && (row.note == "E2" || row.note == "E3"))
		return true;
	if (row.program_name == "muted_guitar" && row.note == "E4")
		return true;
	if (row.program_name == "distortion_guitar" && (row.note == "B4" || row.note == "E5"))
		return true;
	return false;
}

bool expects_full_mix_other_primary_octave_recovery(const std::string &suite_family,
						    const SampleRow &row)
{
	return (suite_family == "strings" &&
		((row.program_name == "viola" && row.note == "C4") ||
		 (row.program_name == "cello" && row.note == "G4"))) ||
	       (suite_family == "synth" &&
		((row.program_name == "metallic_pad" && row.note == "G3") ||
		 (row.program_name == "square_lead" && row.note == "C2")));
}

bool expects_full_mix_other_recovery(const std::string &suite_family, const SampleRow &row)
{
	return (suite_family == "synth" && row.program_name == "square_lead" &&
		(row.note == "C2" || row.note == "G3")) ||
	       (suite_family == "synth" && row.program_name == "chiff_lead" && row.note == "C2") ||
	       (suite_family == "strings" && row.program_name == "contrabass" && row.note == "E1") ||
	       (suite_family == "strings" &&
		((row.program_name == "pizzicato_strings" && row.note == "G2") ||
		 (row.program_name == "tremolo_strings" && row.note == "E5") ||
		 (row.program_name == "string_ensemble_1" && row.note == "E5") ||
		 (row.program_name == "synth_strings_1" &&
		  (row.note == "G4" || row.note == "C5")) ||
		 (row.program_name == "synth_strings_2" && row.note == "G3")));
}

void check_instrument_samples(Runner &runner, const std::string &root, std::ostream *attribute_out,
			      int shard_count, int shard_index)
{
	static constexpr const char *kFamilies[] = {"piano", "guitar", "bass", "synth", "strings", "vocals"};
	for (const char *family_name : kFamilies) {
		const std::string family = family_name;
		const std::string family_dir = family + "_samples";
		std::vector<SampleRow> rows;
		runner.expect(read_manifest(join_path(join_path(root, family_dir), "manifest.tsv"), rows),
			      "missing manifest for " + family);
		if (!env_filter_active())
			runner.expect(rows.size() >= 1000, "expected at least 1000 " + family + " samples");

		for (std::size_t row_index = 0; row_index < rows.size(); ++row_index) {
			if (!shard_includes_row(row_index, shard_count, shard_index))
				continue;
			const SampleRow &row = rows[row_index];
			if (!filter_matches(family, row))
				continue;
			mao_test::Buffer buffer = {};
			uint32_t sample_rate = 0;
			std::string error;
			if (!load_sample(root, family_dir, row, buffer, sample_rate, 0.62f, false, error)) {
				runner.expect(false, "failed to load " + family + " sample " + row.path + ": " + error);
				continue;
			}

			for (float window_seconds : {kDefaultWindowSeconds}) {
				const mao::AnalysisSnapshot snapshot =
					analyze_buffer(buffer, sample_rate, family_mode(family), family.c_str(),
						       window_seconds);
				const std::string expected = mao_test::note_label(row.midi);
				char window_label[16] = {};
				std::snprintf(window_label, sizeof(window_label), "%.0fms", window_seconds * 1000.0f);
				const std::string context = family + " " + row.program_name + " " + expected +
							    " " + row.path + " " + window_label;
				const bool label_ok =
					mao_test::has_note_token(family_state(snapshot, family).label,
								 expected.c_str()) ||
					std::strcmp(family_state(snapshot, family).label, expected.c_str()) == 0;
				const bool grid_ok = grid_has_pitch_class(family_grid(snapshot, family), row.midi);
				const bool expect_full_mix_vocal = expects_full_mix_vocal_recovery(family, row);
				const bool expect_full_mix_vocal_primary =
					expects_full_mix_vocal_primary_octave_recovery(family, row);
				const bool expect_full_mix_vocal_display =
					expects_full_mix_vocal_display_octave_recovery(family, row);
				const bool expect_full_mix_bass_primary =
					expects_full_mix_bass_primary_octave_recovery(family, row);
				const bool expect_full_mix_keyboard_primary =
					expects_full_mix_keyboard_primary_octave_recovery(family, row);
				const bool expect_full_mix_guitar_primary =
					expects_full_mix_guitar_primary_octave_recovery(family, row);
				const bool expect_full_mix_other_primary =
					expects_full_mix_other_primary_octave_recovery(family, row);
				const bool expect_full_mix_other = expects_full_mix_other_recovery(family, row);
				mao::AnalysisSnapshot full_mix_snapshot = {};
				bool full_mix_grid_ok = false;
				bool full_mix_anywhere = false;
				if (attribute_out || expect_full_mix_vocal || expect_full_mix_vocal_primary ||
				    expect_full_mix_vocal_display || expect_full_mix_bass_primary ||
				    expect_full_mix_keyboard_primary || expect_full_mix_guitar_primary ||
				    expect_full_mix_other_primary || expect_full_mix_other) {
					full_mix_snapshot =
						analyze_buffer(buffer, sample_rate, mao::AnalysisInputMode::FullMix,
							       family.c_str(), window_seconds);
					full_mix_grid_ok =
						grid_has_pitch_class(family_grid(full_mix_snapshot, family),
								     row.midi);
					full_mix_anywhere = snapshot_has_pitch_class(full_mix_snapshot, row.midi);
				}
				if (attribute_out) {
					const RawNoteAttributes raw =
						measure_raw_note_attributes(buffer, sample_rate, row.midi);
					append_note_attribute_row(*attribute_out, family, row, full_mix_snapshot,
								  window_seconds, full_mix_grid_ok,
								  full_mix_anywhere, raw,
								  debug_candidate_for_pitch(full_mix_snapshot, row.midi));
				}
				if (expect_full_mix_vocal) {
					runner.expect(grid_has_pitch_class(full_mix_snapshot.vocal_notes, row.midi),
						      context + ": expected full-mix vocal row recovery, got label `" +
							      full_mix_snapshot.vocal.label + "`");
				}
				if (expect_full_mix_vocal_primary) {
					const int primary_midi =
						grid_primary_pitch_class_midi(full_mix_snapshot.vocal_notes,
									      row.midi);
					runner.expect(primary_midi == row.midi,
						      context +
							      ": expected full-mix vocal primary octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.vocal_notes) + "`");
				}
				if (expect_full_mix_vocal_display) {
					const int display_midi =
						grid_pitch_class_midi(full_mix_snapshot.vocal_notes, row.midi);
					runner.expect(display_midi == row.midi,
						      context +
							      ": expected full-mix vocal display octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.vocal_notes) + "`");
				}
				if (expect_full_mix_bass_primary) {
					const int primary_midi =
						grid_primary_pitch_class_midi(full_mix_snapshot.bass_notes,
									      row.midi);
					runner.expect(primary_midi == row.midi,
						      context +
							      ": expected full-mix bass primary octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.bass_notes) + "`");
				}
				if (expect_full_mix_keyboard_primary) {
					const int primary_midi =
						grid_primary_pitch_class_midi(full_mix_snapshot.keyboard_notes,
									      row.midi);
					runner.expect(primary_midi == row.midi,
						      context +
							      ": expected full-mix keyboard primary octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.keyboard_notes) + "`");
				}
				if (expect_full_mix_guitar_primary) {
					const int primary_midi =
						grid_primary_pitch_class_midi(full_mix_snapshot.guitar_notes,
									      row.midi);
					runner.expect(primary_midi == row.midi,
						      context +
							      ": expected full-mix guitar primary octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.guitar_notes) + "`");
				}
				if (expect_full_mix_other_primary) {
					const int primary_midi =
						grid_primary_pitch_class_midi(full_mix_snapshot.other_notes,
									      row.midi);
					runner.expect(primary_midi == row.midi,
						      context +
							      ": expected full-mix other primary octave recovery, got `" +
							      grid_debug_label(full_mix_snapshot.other_notes) + "`");
				}
				if (expect_full_mix_other) {
					runner.expect(grid_has_pitch_class(full_mix_snapshot.other_notes, row.midi),
						      context + ": expected full-mix other row recovery, got label `" +
							      full_mix_snapshot.other.label + "`");
				}
				runner.expect(label_ok || grid_ok,
					      context + ": expected detected note, got label `" +
						      family_state(snapshot, family).label + "`");
			}
		}
	}
}

void check_drum_kit_samples(Runner &runner, const std::string &root, std::ostream *attribute_out,
			    int shard_count, int shard_index)
{
	const std::string family_dir = "drum_kit_samples";
	std::vector<SampleRow> rows;
	runner.expect(read_manifest(join_path(join_path(root, family_dir), "manifest.tsv"), rows),
		      "missing manifest for drum kit samples");
	if (!env_filter_active())
		runner.expect(rows.size() >= 1000, "expected at least 1000 generated drum kit samples");

	for (std::size_t row_index = 0; row_index < rows.size(); ++row_index) {
		if (!shard_includes_row(row_index, shard_count, shard_index))
			continue;
		const SampleRow &row = rows[row_index];
		if (!filter_matches("drum", row))
			continue;
		std::size_t expected = 0;
		if (!category_index(row.family, expected))
			continue;

		mao_test::Buffer buffer = {};
		uint32_t sample_rate = 0;
		std::string error;
		if (!load_sample(root, family_dir, row, buffer, sample_rate, 0.82f, true, error)) {
			runner.expect(false, "failed to load drum sample " + row.path + ": " + error);
			continue;
		}
		for (float window_seconds : {kDefaultWindowSeconds}) {
			const mao::AnalysisSnapshot snapshot = analyze_drum_buffer(buffer, sample_rate, window_seconds);
			char window_label[16] = {};
			std::snprintf(window_label, sizeof(window_label), "%.0fms", window_seconds * 1000.0f);
			if (attribute_out)
				append_drum_attribute_row(*attribute_out, row, snapshot, window_seconds, expected);
			runner.expect(snapshot.drums[expected].active,
				      "drum kit " + row.program_name + " " + row.family + " " + window_label +
					      ": expected " + snapshot.drums[expected].label + " active (" +
					      drum_details(snapshot) + ")");
		}
	}
}

bool family_has_detected_note(const mao::AnalysisSnapshot &snapshot, const std::string &family, int midi)
{
	const std::string expected = mao_test::note_label(midi);
	return mao_test::has_note_token(family_state(snapshot, family).label, expected.c_str()) ||
	       std::strcmp(family_state(snapshot, family).label, expected.c_str()) == 0 ||
	       grid_has_pitch_class(family_grid(snapshot, family), midi);
}

void add_sample_to_mix(const std::string &root, const std::string &family, const std::vector<SampleRow> &rows,
		       int midi, mao_test::Buffer &mix, Runner &runner, float target_peak = 0.24f)
{
	const SampleRow *row = find_row(rows, family, midi);
	runner.expect(row != nullptr, "missing combination sample " + family + " " + mao_test::note_label(midi));
	if (!row)
		return;

	mao_test::Buffer part = {};
	uint32_t sample_rate = 0;
	std::string error;
	if (!load_sample(root, family + "_samples", *row, part, sample_rate, target_peak, false, error)) {
		runner.expect(false, "failed to load combination sample " + row->path + ": " + error);
		return;
	}
	for (std::size_t i = 0; i < mix.size(); ++i)
		mix[i] = std::clamp(mix[i] + part[i], -1.0f, 1.0f);
}

void check_same_pitch_rendered_samples(Runner &runner, const std::string &root,
				       const std::vector<SampleRow> &all_rows)
{
	static constexpr int kSharedMidi = 60;
	for (const char *family_name : {"piano", "guitar", "bass", "synth", "strings", "vocals"}) {
		const std::string family = family_name;
		const SampleRow *row = find_row(all_rows, family, kSharedMidi);
		runner.expect(row != nullptr,
			      "missing same-pitch rendered sample " + family + " " +
				      mao_test::note_label(kSharedMidi));
		if (!row)
			continue;

		mao_test::Buffer buffer = {};
		uint32_t sample_rate = 0;
		std::string error;
		if (!load_sample(root, family + "_samples", *row, buffer, sample_rate, 0.62f, false, error)) {
			runner.expect(false, "failed to load same-pitch sample " + row->path + ": " + error);
			continue;
		}
		const mao::AnalysisSnapshot snapshot =
			analyze_buffer(buffer, sample_rate, family_mode(family), family.c_str(),
				       kDefaultWindowSeconds);
		runner.expect(family_has_detected_note(snapshot, family, kSharedMidi),
			      "same-pitch rendered " + family + " " + row->program_name +
				      ": expected " + mao_test::note_label(kSharedMidi) + ", got label `" +
				      family_state(snapshot, family).label + "`");
	}

	mao_test::Buffer same_pitch_mix = {};
	for (const char *family : {"piano", "guitar", "synth", "strings", "vocals"})
		add_sample_to_mix(root, family, all_rows, kSharedMidi, same_pitch_mix, runner, 0.16f);
	{
		const mao::AnalysisSnapshot snapshot =
			analyze_buffer(same_pitch_mix, static_cast<uint32_t>(mao_test::kSampleRate),
				       mao::AnalysisInputMode::FullMix, "same-pitch rendered mix",
				       kDefaultWindowSeconds, 5);
		runner.expect(snapshot_has_pitch_class(snapshot, kSharedMidi),
			      "same-pitch rendered mix: expected global " + mao_test::note_label(kSharedMidi) +
				      " pitch class active");
	}

	mao_test::Buffer chord_mix = {};
	for (int midi : {60, 64, 67}) {
		for (const char *family : {"piano", "guitar", "strings", "vocals"})
			add_sample_to_mix(root, family, all_rows, midi, chord_mix, runner, 0.09f);
	}
	const mao::AnalysisSnapshot snapshot =
		analyze_buffer(chord_mix, static_cast<uint32_t>(mao_test::kSampleRate),
			       mao::AnalysisInputMode::FullMix, "same-pitch rendered chord mix",
			       kDefaultWindowSeconds, 5);
	for (int midi : {60, 64, 67})
		runner.expect(snapshot_has_pitch_class(snapshot, midi),
			      "same-pitch rendered chord mix: expected " + mao_test::note_label(midi) +
				      " pitch class active");
	runner.expect(mao_test::contains(snapshot.global_chord.label, "C"),
		      std::string("same-pitch rendered chord mix: expected C-family chord, got `") +
			      snapshot.global_chord.label + "`");
}

void check_combined_samples(Runner &runner, const std::string &root)
{
	std::vector<SampleRow> all_rows;
	for (const char *family : {"piano", "guitar", "bass", "synth", "strings", "vocals"}) {
		std::vector<SampleRow> rows;
		if (read_manifest(join_path(join_path(root, std::string(family) + "_samples"), "manifest.tsv"), rows))
			all_rows.insert(all_rows.end(), rows.begin(), rows.end());
	}

	mao_test::Buffer mix = {};
	for (int midi : {60, 64, 67})
		add_sample_to_mix(root, "piano", all_rows, midi, mix, runner);
	for (int midi : {52, 55, 60})
		add_sample_to_mix(root, "guitar", all_rows, midi, mix, runner);
	add_sample_to_mix(root, "bass", all_rows, 36, mix, runner);
	add_sample_to_mix(root, "strings", all_rows, 55, mix, runner);
	add_sample_to_mix(root, "synth", all_rows, 72, mix, runner);
	add_sample_to_mix(root, "vocals", all_rows, 67, mix, runner);

	for (float window_seconds : {kDefaultWindowSeconds}) {
		const mao::AnalysisSnapshot snapshot =
			analyze_buffer(mix, static_cast<uint32_t>(mao_test::kSampleRate),
				       mao::AnalysisInputMode::FullMix, "sample combination", window_seconds, 5);
		char window_label[16] = {};
		std::snprintf(window_label, sizeof(window_label), "%.0fms", window_seconds * 1000.0f);

		for (int midi : {36, 52, 55, 60, 64, 67, 72})
			runner.expect(snapshot_has_pitch_class(snapshot, midi),
				      std::string("combined samples ") + window_label +
					      ": expected pitch class " + mao_test::note_name(midi) + " active");
		runner.expect(mao_test::contains(snapshot.global_chord.label, "C") ||
				      mao_test::contains(snapshot.global_chord.label, "Em") ||
				      mao_test::contains(snapshot.global_chord.label, "G"),
			      std::string("combined samples ") + window_label +
				      ": expected C/Em/G-family chord, got `" + snapshot.global_chord.label + "`");
	}

	check_same_pitch_rendered_samples(runner, root, all_rows);
}

} // namespace

int main()
{
	const char *root_env = std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT");
	const std::string root = root_env && *root_env ? root_env : "build";
	const bool required = std::getenv("MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED") != nullptr;
	if (!std::ifstream(join_path(join_path(root, "piano_samples"), "manifest.tsv"))) {
		if (required) {
			std::fprintf(stderr, "analyzer_instrument_samples: missing generated samples under %s\n",
				     root.c_str());
			return 1;
		}
		std::printf("analyzer_instrument_samples: skipped; no generated samples under %s\n", root.c_str());
		return 0;
	}

	Runner runner;
	const int shard_count = positive_int_env("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT", 1);
	const int shard_index = nonnegative_int_env("MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX", 0);
	if (shard_index >= shard_count) {
		std::fprintf(stderr,
			     "analyzer_instrument_samples: invalid shard index %d for shard count %d\n",
			     shard_index, shard_count);
		return 1;
	}
	const char *attribute_path_env = std::getenv("MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV");
	std::ofstream attribute_out;
	if (attribute_path_env && *attribute_path_env) {
		attribute_out.open(attribute_path_env, std::ios::out | std::ios::trunc);
		runner.expect(attribute_out.good(),
			      std::string("failed to open attribute TSV `") + attribute_path_env + "`");
		if (attribute_out.good())
			print_attribute_header(attribute_out);
	}
	std::ostream *attribute_stream = attribute_out.good() ? &attribute_out : nullptr;
	check_instrument_samples(runner, root, attribute_stream, shard_count, shard_index);
	check_drum_kit_samples(runner, root, attribute_stream, shard_count, shard_index);
	if (shard_index == 0)
		check_combined_samples(runner, root);

	if (runner.failures) {
		std::fprintf(stderr, "analyzer_instrument_samples: %d/%d checks failed\n", runner.failures,
			     runner.checks);
		return 1;
	}
	std::printf("analyzer_instrument_samples: %d checks passed\n", runner.checks);
	return 0;
}
