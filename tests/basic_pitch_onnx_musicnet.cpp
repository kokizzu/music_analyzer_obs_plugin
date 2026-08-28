// Reuse the established MusicNet fixture parser and score-aligned window
// selection.  Renaming its standalone entry point keeps this offline replay
// aligned with the analyzer's own corpus harness without creating a second
// interpretation of WAV or label files.
#define main analyzer_musicnet_reference_main
#include "analyzer_musicnet.cpp"
#undef main

#include "basic_pitch_onnx_decoder.hpp"
#include "basic_pitch_onnx_runtime.hpp"
#include "basic_pitch_onnx_worker.hpp"
#include "basic_pitch_pcm_history.hpp"
#include "basic_pitch_vocal_fusion.hpp"

#include <array>
#include <cstdlib>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

namespace {

std::set<int> expected_midis(const CandidateWindow &candidate)
{
	std::set<int> notes;
	for (const ActiveNote &active : candidate.active)
		notes.insert(active.midi);
	return notes;
}

std::set<int> native_midis(const mao::AnalysisSnapshot &snapshot)
{
	std::set<int> notes;
	const std::size_t count = std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
							       snapshot.full_mix_debug_candidates.size());
	for (std::size_t index = 0; index < count; ++index) {
		const int midi = snapshot.full_mix_debug_candidates[index].midi;
		if (midi >= 0)
			notes.insert(midi);
	}
	return notes;
}

std::size_t overlap_count(const std::set<int> &left, const std::set<int> &right)
{
	std::size_t matches = 0;
	for (int note : left)
		matches += right.count(note);
	return matches;
}

const mao::FullMixDebugCandidate *debug_candidate_for_midi(const mao::AnalysisSnapshot &snapshot, int midi)
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

bool read_causal_waveform(const Recording &recording, const CandidateWindow &candidate,
			  std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> &waveform,
			  std::string &error)
{
	// Output frame 150 is about 1.736 s into the two-second model context,
	// leaving roughly 250 ms of future audio at the live decision point.
	const double source_per_model_frame =
		static_cast<double>(mao::BasicPitchOnnxRuntime::kInputSamples) /
		static_cast<double>(mao::BasicPitchOnnxOutput::kFrames);
	const double causal_seconds =
		static_cast<double>(mao::BasicPitchOnnxDecoder::kCausalFrame) * source_per_model_frame /
		static_cast<double>(mao::BasicPitchPcmHistory::kTargetSampleRate);
	const uint64_t causal_frames =
		static_cast<uint64_t>(causal_seconds * static_cast<double>(recording.sample_rate) + 0.5);
	const uint64_t start = candidate.center_sample > causal_frames ? candidate.center_sample - causal_frames : 0;
	const std::size_t source_frames = static_cast<std::size_t>(recording.sample_rate) * 2;

	std::vector<float> source;
	source.reserve(source_frames + mao_test::Buffer{}.size());
	for (std::size_t offset = 0; offset < source_frames; offset += mao_test::Buffer{}.size()) {
		mao_test::Buffer buffer = {};
		uint32_t sample_rate = 0;
		const uint64_t center = start + offset + buffer.size() / 2;
		if (!read_wav_window(recording.audio_path, center, buffer, sample_rate, error))
			return false;
		if (sample_rate != recording.sample_rate) {
			error = "WAV sample rate changed while reading";
			return false;
		}
		const std::size_t remaining = source_frames - offset;
		source.insert(source.end(), buffer.begin(), buffer.begin() + std::min(buffer.size(), remaining));
	}

	mao::BasicPitchPcmHistory history;
	bool ready = false;
	for (std::size_t offset = 0; offset < source.size(); offset += mao_test::Buffer{}.size()) {
		const std::size_t count = std::min(mao_test::Buffer{}.size(), source.size() - offset);
		ready = history.push(source.data() + offset, count, recording.sample_rate, waveform) || ready;
	}
	if (!ready)
		error = "insufficient PCM to produce a causal model window";
	return ready;
}

mao::AnalysisSnapshot analyze_sequential_causal_window(const Recording &recording,
							const CandidateWindow &candidate, std::string &error)
{
	const double source_per_model_frame =
		static_cast<double>(mao::BasicPitchOnnxRuntime::kInputSamples) /
		static_cast<double>(mao::BasicPitchOnnxOutput::kFrames);
	const uint64_t causal_frames = static_cast<uint64_t>(
		static_cast<double>(mao::BasicPitchOnnxDecoder::kCausalFrame) * source_per_model_frame /
		static_cast<double>(mao::BasicPitchPcmHistory::kTargetSampleRate) * recording.sample_rate + 0.5);
	const uint64_t start = candidate.center_sample > causal_frames ? candidate.center_sample - causal_frames : 0;
	const std::size_t source_frames = static_cast<std::size_t>(recording.sample_rate) * 2;
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.sample_rate = recording.sample_rate;
	settings.analysis_interval_seconds = 0.05f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	mao::AnalysisSnapshot snapshot = {};
	for (std::size_t offset = 0; offset < source_frames; offset += mao_test::Buffer{}.size()) {
		mao_test::Buffer buffer = {};
		uint32_t rate = 0;
		if (!read_wav_window(recording.audio_path, start + offset + buffer.size() / 2, buffer, rate, error))
			return {};
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "MusicNet labeled real mix", 0);
	}
	return snapshot;
}

} // namespace

int main(int argc, char **argv)
{
	if (argc != 7) {
		std::fprintf(stderr,
			     "usage: basic_pitch_onnx_musicnet CORPUS MUSICNET_ROOT ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL MODE THRESHOLD\n");
		return 2;
	}
	const std::string corpus = argv[1];
	const std::string mode = argv[5];
	if (mode != "true-miss" && mode != "all" && mode != "sequential" && mode != "worker" &&
	    mode != "owner-evidence") {
		std::fprintf(stderr,
			     "basic_pitch_onnx_musicnet: MODE must be true-miss, all, sequential, worker, or owner-evidence\n");
		return 2;
	}
	const bool true_miss_only = mode == "true-miss" || mode == "sequential";
	char *threshold_end = nullptr;
	const float threshold = std::strtof(argv[6], &threshold_end);
	if (!threshold_end || *threshold_end != '\0' || threshold < mao::BasicPitchOnnxDecoder::kFrameThreshold ||
	    threshold > 1.0f) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: THRESHOLD must be between %.2f and 1.00\n",
			     mao::BasicPitchOnnxDecoder::kFrameThreshold);
		return 2;
	}
	std::vector<Recording> recordings;
	int unusable = 0;
	collect_split_recordings(argv[2], "train_data", "train_labels", recordings, unusable);
	collect_split_recordings(argv[2], "test_data", "test_labels", recordings, unusable);
	if (recordings.empty()) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: no readable MusicNet recordings under `%s`\n", argv[2]);
		return 1;
	}

	mao::BasicPitchOnnxRuntime runtime;
	if (mode != "worker" && !runtime.load(argv[3], argv[4])) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: ONNX load failed: %s\n", runtime.last_error().c_str());
		return 1;
	}
	mao::BasicPitchOnnxWorker worker(argv[3], argv[4]);
	if (mode == "worker" && !worker.start()) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: worker start failed: %s\n", worker.last_error().c_str());
		return 1;
	}
	mao::BasicPitchOnnxDecoder decoder;
	int windows = 0;
	int expected = 0;
	int native_hits = 0;
	int onnx_hits = 0;
	int fused_hits = 0;
	int novel_correct = 0;
	int novel_false = 0;
	if (mode == "owner-evidence") {
		std::printf("corpus\tthreshold\tmidi\tvocal_truth\tprotected_false\tnative_owner\tnative_confidence"
			    "\tvocal_score\tkeyboard_score\tguitar_score\tother_score\tpitch_confidence\tperiodicity"
			    "\tnoise\tonnx_confidence\tcandidate_gate\n");
	}

	for (const Recording &recording : recordings) {
		for (const CandidateWindow &candidate : select_candidate_windows(recording, 4, 2, 2, 2)) {
			mao_test::Buffer native_buffer = {};
			uint32_t native_rate = 0;
			std::string error;
			if (!read_wav_window(recording.audio_path, candidate.center_sample, native_buffer, native_rate,
					     error)) {
				std::fprintf(stderr, "basic_pitch_onnx_musicnet: native window read failed: %s\n", error.c_str());
				return 1;
			}
			const std::set<int> truth = expected_midis(candidate);
			const mao::AnalysisSnapshot native_snapshot = analyze_confirmed_buffer(native_buffer, native_rate);
			const std::set<int> native = native_midis(native_snapshot);
			if (true_miss_only && overlap_count(truth, native) == truth.size())
				continue; // This replay is intentionally the native true-miss subset.

			std::set<int> onnx;
			if (mode == "sequential") {
				const mao::AnalysisSnapshot sequential = analyze_sequential_causal_window(recording, candidate, error);
				if (!error.empty()) {
					std::fprintf(stderr, "basic_pitch_onnx_musicnet: sequential window failed: %s\n", error.c_str());
					return 1;
				}
				onnx = native_midis(sequential);
			} else {
				std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> waveform = {};
				if (!read_causal_waveform(recording, candidate, waveform, error)) {
					std::fprintf(stderr, "basic_pitch_onnx_musicnet: causal window read failed: %s\n", error.c_str());
					return 1;
				}
				mao::BasicPitchCausalNotes decoded;
				if (mode == "worker") {
					uint64_t sequence = 0;
					if (!worker.submit(waveform.data(), waveform.size(), &sequence) ||
					    !worker.wait_for_result(sequence, 10000) ||
					    !worker.copy_latest(decoded)) {
						std::fprintf(stderr, "basic_pitch_onnx_musicnet: worker inference failed: %s\n",
							     worker.last_error().c_str());
						return 1;
					}
				} else {
					mao::BasicPitchOnnxOutput output;
					if (!runtime.infer(waveform.data(), waveform.size(), output)) {
						std::fprintf(stderr, "basic_pitch_onnx_musicnet: infer failed: %s\n", runtime.last_error().c_str());
						return 1;
					}
					decoded = decoder.decode(output);
				}
				for (std::size_t index = 0; index < decoded.confidence.size(); ++index) {
					if (decoded.confidence[index] < threshold)
						continue;
					const int midi = mao::BasicPitchOnnxDecoder::kMidiOffset + static_cast<int>(index);
					onnx.insert(midi);
					if (mode != "owner-evidence")
						continue;
					const mao::FullMixDebugCandidate *debug = debug_candidate_for_midi(native_snapshot, midi);
					if (!debug)
						continue;
					const bool vocal_truth = corpus != "MusicNet" && truth.count(midi) != 0;
					const bool protected_false = !vocal_truth;
					const bool candidate_gate =
						mao::basic_pitch_vocal_fusion_supported(*debug, decoded.confidence[index]);
					std::printf("%s\t%.2f\t%d\t%d\t%d\t%s\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f"
						    "\t%.6f\t%.6f\t%.6f\t%d\n",
						    corpus.c_str(), threshold, midi, vocal_truth ? 1 : 0,
						    protected_false ? 1 : 0, owner_name(debug->owner),
						    debug->ownership_confidence, debug->vocal_score, debug->keyboard_score,
						    debug->guitar_score, debug->other_score, debug->pitch_confidence,
						    debug->periodicity, debug->local_noise_level, decoded.confidence[index],
						    candidate_gate ? 1 : 0);
				}
			}
			std::set<int> fused = native;
			fused.insert(onnx.begin(), onnx.end());
			expected += static_cast<int>(truth.size());
			native_hits += static_cast<int>(overlap_count(truth, native));
			onnx_hits += static_cast<int>(overlap_count(truth, onnx));
			fused_hits += static_cast<int>(overlap_count(truth, fused));
			for (int note : onnx) {
				if (native.count(note))
					continue;
				if (truth.count(note))
					++novel_correct;
				else
					++novel_false;
			}
			if (++windows == 12 && true_miss_only)
				break;
		}
		if (windows == 12 && true_miss_only)
			break;
	}
	if (true_miss_only && windows != 12) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: %s yielded %d/12 true-miss windows\n", corpus.c_str(), windows);
		return 1;
	}
	if (!true_miss_only && windows == 0) {
		std::fprintf(stderr, "basic_pitch_onnx_musicnet: %s yielded no score-aligned windows\n", corpus.c_str());
		return 1;
	}
	if (mode == "owner-evidence")
		return 0;
	std::printf("%s\t%.2f\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n", corpus.c_str(), threshold, windows, expected,
		    native_hits, onnx_hits, fused_hits, novel_correct, novel_false);
	return 0;
}
