#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace mao {

constexpr std::size_t kAnalysisWindow = 4096;
constexpr std::size_t kDrumCount = 6;
constexpr std::size_t kNoteRowCount = 2;
constexpr int kFirstAnalyzedMidi = 21;
constexpr int kLastAnalyzedMidi = 108;
constexpr std::size_t kNoteProbeCount = static_cast<std::size_t>(kLastAnalyzedMidi - kFirstAnalyzedMidi + 1);

enum DrumIndex : std::size_t {
	Kick = 0,
	Snare = 1,
	HiHat = 2,
	Crash = 3,
	Tom = 4,
	Ride = 5,
};

struct AnalysisSettings {
	uint32_t sample_rate = 48000;
	float sensitivity = 1.0f;
	float analysis_interval_seconds = 0.05f;
	float root_window_seconds = 15.0f;
};

struct DrumState {
	char label[12] = {};
	float level = 0.0f;
	bool active = false;
};

struct InstrumentState {
	char label[64] = {};
	float confidence = 0.0f;
};

struct NoteCell {
	char label[8] = {};
	float level = 0.0f;
	int midi = -1;
	bool active = false;
};

struct NoteGrid {
	std::array<NoteCell, 12> cells = {};
	std::array<std::array<NoteCell, 12>, kNoteRowCount> rows = {};
};

struct AnalysisSnapshot {
	uint64_t sequence = 0;
	char source[64] = {};
	float rms = 0.0f;
	float peak = 0.0f;
	float low_energy = 0.0f;
	float mid_energy = 0.0f;
	float high_energy = 0.0f;
	uint64_t dropped_windows = 0;
	uint64_t audio_frames = 0;
	uint64_t analyzed_windows = 0;
	bool audio_seen = false;
	std::array<DrumState, kDrumCount> drums = {};
	InstrumentState root = {};
	char root_candidates[64] = {};
	InstrumentState bass = {};
	NoteGrid bass_notes = {};
	InstrumentState guitar = {};
	NoteGrid guitar_notes = {};
	InstrumentState guitar_chord = {};
	InstrumentState keyboard = {};
	NoteGrid keyboard_notes = {};
	InstrumentState keyboard_chord = {};
	InstrumentState vocal = {};
	NoteGrid vocal_notes = {};
	InstrumentState other = {};
	NoteGrid other_notes = {};
	InstrumentState other_chord = {};
};

class AnalysisEngine {
public:
	AnalysisEngine();

	void configure(uint32_t sample_rate);
	AnalysisSnapshot analyze(const float *samples, std::size_t count, const AnalysisSettings &settings,
				  const char *source_name, uint64_t dropped_windows);

private:
	struct Probe {
		int midi = 0;
		float freq = 0.0f;
		float coeff = 0.0f;
	};

	struct RootVote {
		std::array<float, 12> scores = {};
		bool valid = false;
	};

	static constexpr std::size_t kMaxRootVotes = 1500;

	std::array<float, kAnalysisWindow> window_ = {};
	std::array<Probe, kNoteProbeCount> note_probes_ = {};
	std::array<Probe, 15> drum_probes_ = {};
	uint32_t sample_rate_ = 0;
	float previous_rms_ = 0.0f;
	std::array<float, kDrumCount> drum_average_ = {};
	std::array<float, kDrumCount> drum_level_ = {};
	std::array<RootVote, kMaxRootVotes> root_votes_ = {};
	std::array<float, 12> root_sum_ = {};
	std::size_t root_vote_pos_ = 0;
	std::size_t root_vote_count_ = 0;
	std::size_t root_vote_target_ = 0;
	int locked_root_ = -1;
	float silence_seconds_ = 0.0f;

	void rebuild_plans(uint32_t sample_rate);
	float goertzel_power(const float *samples, std::size_t count, float mean, const Probe &probe) const;
	void reset_root_window();
	void add_root_vote(const RootVote &vote);
	InstrumentState track_root(const std::array<float, kNoteProbeCount> &powers, float rms,
				   const AnalysisSettings &settings, char *root_candidates,
				   std::size_t root_candidates_size);
};

} // namespace mao
