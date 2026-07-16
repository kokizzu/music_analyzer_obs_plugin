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

const char *category_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								"tom", "ride", "rim"};
	return index < mao::kDrumCount ? kNames[index] : "unknown";
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
		char part[96] = {};
		std::snprintf(part, sizeof(part), "%s%s=%.2f%s", text.empty() ? "" : " ",
			      category_name(i), snapshot.drums[i].level, snapshot.drums[i].active ? "*" : "");
		text += part;
	}
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

void check_instrument_samples(Runner &runner, const std::string &root)
{
	static constexpr const char *kFamilies[] = {"piano", "guitar", "bass", "synth", "strings", "vocals"};
	for (const char *family_name : kFamilies) {
		const std::string family = family_name;
		const std::string family_dir = family + "_samples";
		std::vector<SampleRow> rows;
		runner.expect(read_manifest(join_path(join_path(root, family_dir), "manifest.tsv"), rows),
			      "missing manifest for " + family);
		runner.expect(rows.size() >= 1000, "expected at least 1000 " + family + " samples");

		for (const SampleRow &row : rows) {
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
				runner.expect(label_ok || grid_ok,
					      context + ": expected detected note, got label `" +
						      family_state(snapshot, family).label + "`");
			}
		}
	}
}

void check_drum_kit_samples(Runner &runner, const std::string &root)
{
	const std::string family_dir = "drum_kit_samples";
	std::vector<SampleRow> rows;
	runner.expect(read_manifest(join_path(join_path(root, family_dir), "manifest.tsv"), rows),
		      "missing manifest for drum kit samples");
	runner.expect(rows.size() >= 1000, "expected at least 1000 generated drum kit samples");

	for (const SampleRow &row : rows) {
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
			runner.expect(snapshot.drums[expected].active,
				      "drum kit " + row.program_name + " " + row.family + " " + window_label +
					      ": expected " + snapshot.drums[expected].label + " active (" +
					      drum_details(snapshot) + ")");
		}
	}
}

void add_sample_to_mix(const std::string &root, const std::string &family, const std::vector<SampleRow> &rows,
		       int midi, mao_test::Buffer &mix, Runner &runner)
{
	const SampleRow *row = find_row(rows, family, midi);
	runner.expect(row != nullptr, "missing combination sample " + family + " " + mao_test::note_label(midi));
	if (!row)
		return;

	mao_test::Buffer part = {};
	uint32_t sample_rate = 0;
	std::string error;
	if (!load_sample(root, family + "_samples", *row, part, sample_rate, 0.24f, false, error)) {
		runner.expect(false, "failed to load combination sample " + row->path + ": " + error);
		return;
	}
	for (std::size_t i = 0; i < mix.size(); ++i)
		mix[i] = std::clamp(mix[i] + part[i], -1.0f, 1.0f);
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
	check_instrument_samples(runner, root);
	check_drum_kit_samples(runner, root);
	check_combined_samples(runner, root);

	if (runner.failures) {
		std::fprintf(stderr, "analyzer_instrument_samples: %d/%d checks failed\n", runner.failures,
			     runner.checks);
		return 1;
	}
	std::printf("analyzer_instrument_samples: %d checks passed\n", runner.checks);
	return 0;
}
