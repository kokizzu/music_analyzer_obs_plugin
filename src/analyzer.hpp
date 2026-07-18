#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace mao {

constexpr std::size_t kLegacyAnalysisWindow = 4096;
constexpr std::size_t kAnalysisWindow = 8192;
constexpr uint32_t kDefaultAnalysisWindowMs = 100;
constexpr std::size_t kDrumCount = 7;
constexpr std::size_t kNoteRowCount = 3;
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
	Rim = 6,
};

enum class AnalysisInputMode {
	Auto,
	FullMix,
	IsolatedBass,
	IsolatedGuitar,
	IsolatedKeyboard,
	IsolatedVocal,
	IsolatedOther,
};

enum class InstrumentKind {
	Bass,
	Guitar,
	Keyboard,
	Vocal,
	Other,
	Ambiguous,
};

struct AnalysisSettings {
	uint32_t sample_rate = 48000;
	float sensitivity = 1.0f;
	float analysis_interval_seconds = 0.05f;
	float analysis_window_seconds = static_cast<float>(kDefaultAnalysisWindowMs) / 1000.0f;
	uint32_t analysis_window_samples = 0;
	float root_window_seconds = 15.0f;
	AnalysisInputMode input_mode = AnalysisInputMode::Auto;
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
	float estimated_bpm = 0.0f;
	float bpm_confidence = 0.0f;
	uint64_t dropped_windows = 0;
	uint64_t audio_frames = 0;
	uint64_t analyzed_windows = 0;
	float cpu_percent = -1.0f;
	float ram_mb = -1.0f;
	bool audio_seen = false;
	std::array<DrumState, kDrumCount> drums = {};
	std::array<float, kDrumCount> drum_debug_bands = {};
	std::array<float, kDrumCount> drum_debug_segment_bands = {};
	std::array<float, kDrumCount> drum_debug_shape_scores = {};
	std::array<float, kDrumCount> drum_debug_trigger_scores = {};
	std::array<float, kDrumCount> drum_debug_trigger_thresholds = {};
	std::array<bool, kDrumCount> drum_debug_shape_supported = {};
	float drum_debug_transient_ratio = 0.0f;
	float drum_debug_onset = 0.0f;
	int bass_debug_spectral_midi = -1;
	float bass_debug_spectral_confidence = 0.0f;
	float bass_debug_spectral_score = 0.0f;
	int bass_debug_periodic_midi = -1;
	float bass_debug_periodic_confidence = 0.0f;
	float bass_debug_periodic_score = 0.0f;
	int bass_debug_displayed_midi = -1;
	float bass_debug_displayed_confidence = 0.0f;
	float bass_debug_displayed_score = 0.0f;
	InstrumentState root = {};
	char root_candidates[64] = {};
	InstrumentState global_chord = {};
	NoteGrid ambiguous_notes = {};
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

struct NoteTrackingState {
	int consecutive_hits = 0;
	int consecutive_misses = 0;
	float envelope = 0.0f;
	bool confirmed = false;
};

struct ChordTrackingState {
	char displayed_label[64] = {};
	float displayed_confidence = 0.0f;
	char pending_label[64] = {};
	float pending_confidence = 0.0f;
	int pending_frames = 0;
	float missing_seconds = 0.0f;
};

std::size_t resolve_analysis_window_samples(const AnalysisSettings &settings);

class AnalysisEngine {
public:
	AnalysisEngine();

	void configure(uint32_t sample_rate);
	void reset();
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
	static constexpr std::size_t kMaxTempoEvents = 64;

	std::array<float, kAnalysisWindow> window_ = {};
	std::array<Probe, kNoteProbeCount> note_probes_ = {};
	std::array<Probe, 15> drum_probes_ = {};
	uint32_t sample_rate_ = 0;
	float previous_rms_ = 0.0f;
	std::array<float, kDrumCount> drum_average_ = {};
	std::array<float, kDrumCount> drum_level_ = {};
	std::array<RootVote, kMaxRootVotes> root_votes_ = {};
	std::array<float, 12> root_sum_ = {};
	std::array<float, kMaxTempoEvents> tempo_events_ = {};
	int tracked_bass_midi_ = -1;
	int pending_bass_midi_ = -1;
	int pending_bass_hits_ = 0;
	int tracked_bass_misses_ = 0;
	float tracked_bass_confidence_ = 0.0f;
	float tracked_bass_score_ = 0.0f;
	int tracked_vocal_midi_ = -1;
	int pending_vocal_midi_ = -1;
	int pending_vocal_hits_ = 0;
	int tracked_vocal_misses_ = 0;
	float tracked_vocal_score_ = 0.0f;
	std::array<NoteTrackingState, kNoteProbeCount> bass_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> guitar_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> keyboard_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> vocal_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> other_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> full_mix_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> full_mix_other_ownership_tracking_ = {};
	std::array<float, kNoteProbeCount> previous_full_mix_note_levels_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> guitar_chord_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> keyboard_chord_note_tracking_ = {};
	std::array<NoteTrackingState, kNoteProbeCount> other_chord_note_tracking_ = {};
	ChordTrackingState guitar_chord_tracking_ = {};
	ChordTrackingState keyboard_chord_tracking_ = {};
	ChordTrackingState other_chord_tracking_ = {};
	ChordTrackingState global_chord_tracking_ = {};
	std::size_t root_vote_pos_ = 0;
	std::size_t root_vote_count_ = 0;
	std::size_t root_vote_target_ = 0;
	std::size_t tempo_event_pos_ = 0;
	std::size_t tempo_event_count_ = 0;
	int locked_root_ = -1;
	float silence_seconds_ = 0.0f;
	float tempo_clock_seconds_ = 0.0f;
	float last_tempo_event_seconds_ = -10.0f;
	float estimated_bpm_ = 0.0f;
	float bpm_confidence_ = 0.0f;
	std::size_t analysis_window_samples_ = 0;
	AnalysisInputMode active_input_mode_ = AnalysisInputMode::Auto;
	bool has_active_input_mode_ = false;
	char active_source_[64] = {};

	void rebuild_plans(uint32_t sample_rate);
	void rebuild_window(std::size_t window_samples);
	void reset_note_envelopes();
	void reset_analysis_state();
	void update_tempo(bool transient_event, float interval_seconds, float rms);
	float goertzel_power(const float *samples, std::size_t count, float mean, const Probe &probe) const;
	float goertzel_power_at_frequency(const float *samples, std::size_t count, float mean, float freq) const;
	bool chromatic_tuning_match(const float *samples, std::size_t count, float mean, int midi,
				    float tolerance_cents, bool allow_ratio_rescue) const;
	bool tracked_note_active(AnalysisInputMode input_mode, int midi) const;
	void reset_root_window();
	void add_root_vote(const RootVote &vote);
	InstrumentState track_root(const std::array<float, kNoteProbeCount> &powers, float rms,
				   const AnalysisSettings &settings, char *root_candidates,
				   std::size_t root_candidates_size, const NoteGrid &bass_notes,
				   const InstrumentState &global_chord,
				   const InstrumentState &keyboard_chord, const InstrumentState &guitar_chord,
				   const InstrumentState &other_chord);
};

} // namespace mao
