#include "analyzer.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {

struct Row {
	std::string id;
	int midi = -1;
	std::string path;
};

uint16_t read_u16(std::ifstream &file)
{
	std::array<unsigned char, 2> bytes = {};
	file.read(reinterpret_cast<char *>(bytes.data()), bytes.size());
	return static_cast<uint16_t>(bytes[0]) | static_cast<uint16_t>(bytes[1] << 8);
}

uint32_t read_u32(std::ifstream &file)
{
	std::array<unsigned char, 4> bytes = {};
	file.read(reinterpret_cast<char *>(bytes.data()), bytes.size());
	return static_cast<uint32_t>(bytes[0]) | (static_cast<uint32_t>(bytes[1]) << 8) |
	       (static_cast<uint32_t>(bytes[2]) << 16) | (static_cast<uint32_t>(bytes[3]) << 24);
}

bool read_pcm16_mono(const std::string &path, std::vector<float> &samples, uint32_t &sample_rate,
			     std::string &error)
{
	std::ifstream file(path, std::ios::binary);
	char riff[4] = {};
	char wave[4] = {};
	file.read(riff, sizeof(riff));
	(void)read_u32(file);
	file.read(wave, sizeof(wave));
	if (!file || std::memcmp(riff, "RIFF", sizeof(riff)) != 0 || std::memcmp(wave, "WAVE", sizeof(wave)) != 0) {
		error = "expected RIFF/WAVE";
		return false;
	}

	uint16_t channels = 0;
	uint16_t bits_per_sample = 0;
	std::vector<char> pcm;
	while (file) {
		char chunk[4] = {};
		file.read(chunk, sizeof(chunk));
		if (!file)
			break;
		const uint32_t size = read_u32(file);
		if (!file)
			break;
		if (std::memcmp(chunk, "fmt ", sizeof(chunk)) == 0) {
			const uint16_t format = read_u16(file);
			channels = read_u16(file);
			sample_rate = read_u32(file);
			(void)read_u32(file);
			(void)read_u16(file);
			bits_per_sample = read_u16(file);
			if (format != 1 || size < 16) {
				error = "expected PCM format";
				return false;
			}
			file.seekg(static_cast<std::streamoff>(size - 16), std::ios::cur);
		} else if (std::memcmp(chunk, "data", sizeof(chunk)) == 0) {
			pcm.resize(size);
			file.read(pcm.data(), static_cast<std::streamsize>(pcm.size()));
			break;
		} else {
			file.seekg(static_cast<std::streamoff>(size), std::ios::cur);
		}
		if ((size & 1U) != 0)
			file.seekg(1, std::ios::cur);
	}
	if (!file && pcm.empty()) {
		error = "missing data chunk";
		return false;
	}
	if (channels != 1 || bits_per_sample != 16 || sample_rate == 0 || pcm.size() % 2 != 0) {
		error = "expected 16-bit mono PCM";
		return false;
	}
	samples.resize(pcm.size() / 2);
	for (std::size_t index = 0; index < samples.size(); ++index) {
		const uint16_t raw = static_cast<uint16_t>(static_cast<unsigned char>(pcm[index * 2])) |
			static_cast<uint16_t>(static_cast<unsigned char>(pcm[index * 2 + 1]) << 8);
		samples[index] = static_cast<float>(static_cast<int16_t>(raw)) / 32768.0f;
	}
	return true;
}

bool read_rows(const std::string &root, std::vector<Row> &rows, std::string &error)
{
	std::ifstream file(root + "/manifest.tsv");
	std::string line;
	std::getline(file, line);
	if (!file || line.empty()) {
		error = "missing manifest.tsv";
		return false;
	}
	while (std::getline(file, line)) {
		std::vector<std::string> columns;
		std::stringstream input(line);
		std::string column;
		while (std::getline(input, column, '\t'))
			columns.push_back(column);
		if (columns.size() < 7)
			continue;
		Row row;
		row.id = columns[0];
		row.midi = std::stoi(columns[4]);
		row.path = columns[6];
		rows.push_back(std::move(row));
	}
	if (rows.empty()) {
		error = "manifest has no rows";
		return false;
	}
	return true;
}

bool active_midi(const mao::NoteGrid &grid, int midi)
{
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active && cell.midi == midi && cell.visual_level > 0.0f)
				return true;
		}
	}
	return false;
}

const mao::FullMixDebugCandidate *debug_candidate_for(const mao::AnalysisSnapshot &snapshot, int midi)
{
	const std::size_t count = std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
						      snapshot.full_mix_debug_candidates.size());
	for (std::size_t index = 0; index < count; ++index) {
		const mao::FullMixDebugCandidate &candidate = snapshot.full_mix_debug_candidates[index];
		if (candidate.midi == midi)
			return &candidate;
	}
	return nullptr;
}

mao::AnalysisSnapshot analyze_context(const std::vector<float> &samples, uint32_t sample_rate,
				      const mao::AnalysisSettings &settings)
{
	mao::AnalysisEngine engine;
	const std::size_t hop = std::max<std::size_t>(1, static_cast<std::size_t>(sample_rate / 20));
	const std::size_t window = hop * 2;
	mao::AnalysisSnapshot snapshot = {};
	for (std::size_t offset = 0; offset + window <= samples.size(); offset += hop)
		snapshot = engine.analyze(samples.data() + offset, window, settings, "MedleyDB Rainfall full mix", 0);
	if (samples.size() < window)
		return snapshot;
	const float *final_window = samples.data() + samples.size() - window;
	for (int attempt = 0; attempt < 8; ++attempt) {
		std::this_thread::sleep_for(std::chrono::milliseconds(25));
		snapshot = engine.analyze(final_window, window, settings, "MedleyDB Rainfall full mix", 0);
	}
	return snapshot;
}

float direct_onnx_confidence(const std::vector<float> &samples, uint32_t sample_rate, int midi,
			     mao::BasicPitchOnnxRuntime &runtime, mao::BasicPitchOnnxDecoder &decoder)
{
	mao::BasicPitchPcmHistory history;
	std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> waveform = {};
	const std::size_t hop = std::max<std::size_t>(1, static_cast<std::size_t>(sample_rate / 20));
	bool ready = false;
	for (std::size_t offset = 0; offset < samples.size(); offset += hop) {
		const std::size_t count = std::min(hop, samples.size() - offset);
		ready = history.push(samples.data() + offset, count, sample_rate, waveform) || ready;
	}
	if (!ready)
		return 0.0f;
	mao::BasicPitchOnnxOutput output;
	if (!runtime.infer(waveform.data(), waveform.size(), output))
		return 0.0f;
	const mao::BasicPitchCausalNotes notes = decoder.decode(output);
	const int index = midi - mao::BasicPitchOnnxDecoder::kMidiOffset;
	return index >= 0 && static_cast<std::size_t>(index) < notes.confidence.size()
		? notes.confidence[static_cast<std::size_t>(index)]
		: 0.0f;
}

} // namespace

int main(int argc, char **argv)
{
	if (argc != 4) {
		std::fprintf(stderr, "usage: basic_pitch_medleydb_context ROOT ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL\n");
		return 2;
	}
	std::vector<Row> rows;
	std::string error;
	if (!read_rows(argv[1], rows, error)) {
		std::fprintf(stderr, "basic_pitch_medleydb_context: %s\n", error.c_str());
		return 1;
	}
	mao::BasicPitchOnnxRuntime runtime;
	if (!runtime.load(argv[2], argv[3])) {
		std::fprintf(stderr, "basic_pitch_medleydb_context: ONNX load failed: %s\n", runtime.last_error().c_str());
		return 1;
	}
	mao::BasicPitchOnnxDecoder decoder;

	int native_recovered = 0;
	int fused_recovered = 0;
	for (const Row &row : rows) {
		std::vector<float> samples;
		uint32_t sample_rate = 0;
		if (!read_pcm16_mono(std::string(argv[1]) + "/" + row.path, samples, sample_rate, error)) {
			std::fprintf(stderr, "basic_pitch_medleydb_context: %s: %s\n", row.id.c_str(), error.c_str());
			return 1;
		}
		mao::AnalysisSettings settings = {};
		settings.sample_rate = sample_rate;
		settings.analysis_interval_seconds = 0.05f;
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		const mao::AnalysisSnapshot native_snapshot = analyze_context(samples, sample_rate, settings);
		settings.basic_pitch_vocal_fusion_enabled = true;
		settings.basic_pitch_runtime_library = argv[2];
		settings.basic_pitch_model = argv[3];
		const mao::AnalysisSnapshot fused_snapshot = analyze_context(samples, sample_rate, settings);
		const bool native_hit = active_midi(native_snapshot.vocal_notes, row.midi);
		const bool fused_hit = active_midi(fused_snapshot.vocal_notes, row.midi);
		const float onnx_confidence = direct_onnx_confidence(samples, sample_rate, row.midi, runtime, decoder);
		const mao::FullMixDebugCandidate *debug = debug_candidate_for(fused_snapshot, row.midi);
		native_recovered += native_hit ? 1 : 0;
		fused_recovered += fused_hit ? 1 : 0;
		std::printf("id=%s expected_midi=%d native_hit=%d fused_hit=%d onnx_confidence=%.3f debug=%d owner=%d vocal=%.3f keyboard=%.3f guitar=%.3f other=%.3f native_label=%s fused_label=%s\n",
			    row.id.c_str(), row.midi, native_hit ? 1 : 0, fused_hit ? 1 : 0, onnx_confidence,
			    debug ? 1 : 0, debug ? static_cast<int>(debug->owner) : -1, debug ? debug->vocal_score : 0.0f,
			    debug ? debug->keyboard_score : 0.0f, debug ? debug->guitar_score : 0.0f,
			    debug ? debug->other_score : 0.0f,
			    native_snapshot.vocal.label, fused_snapshot.vocal.label);
	}
	std::printf("medleydb-basic-pitch-context native=%d/%zu fused=%d/%zu\n", native_recovered, rows.size(),
		    fused_recovered, rows.size());
	return 0;
}
