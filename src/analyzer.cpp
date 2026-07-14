#include "analyzer.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <initializer_list>

namespace mao {
namespace {

constexpr float kPi = 3.14159265358979323846f;
constexpr int kFirstMidi = kFirstAnalyzedMidi;
constexpr int kLastMidi = kLastAnalyzedMidi;
constexpr int kBassMinMidi = 23;
constexpr int kBassMaxMidi = 67;
constexpr int kDefaultBassMaxMidi = 52;
constexpr int kGuitarMinMidi = 40;
constexpr int kGuitarMaxMidi = 88;
constexpr int kKeyboardMinMidi = 21;
constexpr int kKeyboardMaxMidi = 108;
constexpr int kVocalMinMidi = 40;
constexpr int kVocalMaxMidi = 84;
constexpr int kOtherMinMidi = 21;
constexpr int kOtherMaxMidi = 108;
constexpr float kSilenceRms = 0.0025f;
constexpr float kNoteRmsFloor = 0.006f;
constexpr float kFullNoteRms = 0.035f;
constexpr float kNoteRelativeFloor = 0.36f;
constexpr float kMixedNoteRelativeFloor = 0.08f;
constexpr float kMixedTimbreFallbackRatio = 0.055f;
constexpr float kComplexTuningFallbackScale = 0.38f;
constexpr float kHarmonicMaskRatio = 0.62f;
constexpr int kChromaticTuneMinMidi = kGuitarMinMidi;
constexpr float kChromaticTuneToleranceCents = 9.0f;
constexpr float kChromaticActiveTuneToleranceCents = 18.0f;
constexpr float kChromaticTuneEstimatorSlackCents = 0.5f;
constexpr float kChromaticCenterAdjacentRatio = 0.985f;
constexpr float kChromaticCenterEdgeRatio = 0.90f;
constexpr float kNoteEnvelopeReleaseSeconds = 0.65f;
constexpr float kNoteEnvelopeVisibleFloor = 0.015f;
constexpr float kNoteEnvelopeNewNoteFloor = 0.010f;
constexpr float kNoteEnvelopeImmediateConfirmFloor = 0.40f;
constexpr float kMixedNoteEnvelopeImmediateConfirmFloor = 0.24f;
constexpr float kAnalyticalChordNoteReleaseSeconds = 0.22f;
constexpr float kAnalyticalChordNoteVisibleFloor = 0.06f;
constexpr int kNoteAttackConfirmFrames = 2;
constexpr int kChordSwitchConfirmFrames = 2;
constexpr float kChordHoldSeconds = 0.35f;
constexpr float kChordConfidenceFloor = 0.36f;
constexpr float kChordCandidateMarginFloor = 0.025f;
constexpr float kChordMarginConfidenceCeiling = 0.40f;
constexpr float kChordWeakExtensionMargin = 0.16f;
constexpr std::size_t kDrumTransientSegments = 8;
constexpr float kDrumTransientRatio = 1.55f;
constexpr float kMixedBassMinBroadScoreRatio = 0.22f;
constexpr float kMixedBassMinConfidence = 0.025f;

bool contains_case_insensitive(const char *text, const char *needle)
{
	if (!text || !needle || !*needle)
		return false;

	const std::size_t needle_len = std::strlen(needle);
	for (const char *cursor = text; *cursor; ++cursor) {
		std::size_t matched = 0;
		while (matched < needle_len && cursor[matched]) {
			const unsigned char lhs = static_cast<unsigned char>(cursor[matched]);
			const unsigned char rhs = static_cast<unsigned char>(needle[matched]);
			if (std::tolower(lhs) != std::tolower(rhs))
				break;
			++matched;
		}
		if (matched == needle_len)
			return true;
	}
	return false;
}

AnalysisInputMode infer_input_mode_from_source(const char *source_name)
{
	if (contains_case_insensitive(source_name, "bass"))
		return AnalysisInputMode::IsolatedBass;
	if (contains_case_insensitive(source_name, "synth") || contains_case_insensitive(source_name, "brass") ||
	    contains_case_insensitive(source_name, "horn") || contains_case_insensitive(source_name, "violin") ||
	    contains_case_insensitive(source_name, "string") || contains_case_insensitive(source_name, "wind") ||
	    contains_case_insensitive(source_name, "woodwind"))
		return AnalysisInputMode::IsolatedOther;
	if (contains_case_insensitive(source_name, "key") || contains_case_insensitive(source_name, "piano") ||
	    contains_case_insensitive(source_name, "organ"))
		return AnalysisInputMode::IsolatedKeyboard;
	if (contains_case_insensitive(source_name, "guitar"))
		return AnalysisInputMode::IsolatedGuitar;
	if (contains_case_insensitive(source_name, "vocal") || contains_case_insensitive(source_name, "voice") ||
	    contains_case_insensitive(source_name, "sing"))
		return AnalysisInputMode::IsolatedVocal;
	if (contains_case_insensitive(source_name, "other"))
		return AnalysisInputMode::IsolatedOther;
	return AnalysisInputMode::FullMix;
}

AnalysisInputMode resolve_input_mode(const AnalysisSettings &settings, const char *source_name)
{
	if (settings.input_mode != AnalysisInputMode::Auto)
		return settings.input_mode;
	return infer_input_mode_from_source(source_name);
}

bool is_monophonic_other_track_source(const char *source_name)
{
	if (!source_name || !contains_case_insensitive(source_name, "track"))
		return false;
	return contains_case_insensitive(source_name, "string") || contains_case_insensitive(source_name, "brass") ||
	       contains_case_insensitive(source_name, "horn") || contains_case_insensitive(source_name, "violin") ||
	       contains_case_insensitive(source_name, "wind") || contains_case_insensitive(source_name, "woodwind");
}

const char *note_name(int midi)
{
	static constexpr const char *kNames[12] = {"C", "C#", "D", "D#", "E", "F",
						   "F#", "G", "G#", "A", "A#", "B"};
	return kNames[((midi % 12) + 12) % 12];
}

float midi_frequency(int midi)
{
	return 440.0f * std::pow(2.0f, (static_cast<float>(midi) - 69.0f) / 12.0f);
}

void copy_text(char *dst, std::size_t dst_size, const char *src)
{
	if (!dst || dst_size == 0)
		return;
	std::snprintf(dst, dst_size, "%s", src ? src : "");
}

void write_note(char *dst, std::size_t dst_size, int midi)
{
	if (!dst || dst_size == 0)
		return;

	std::size_t cursor = 0;
	const char *name = note_name(midi);
	while (*name && cursor + 1 < dst_size)
		dst[cursor++] = *name++;

	const int octave = std::clamp(midi / 12 - 1, 0, 9);
	if (cursor + 1 < dst_size)
		dst[cursor++] = static_cast<char>('0' + octave);
	dst[cursor] = '\0';
}

void write_octave(char *dst, std::size_t dst_size, int midi)
{
	if (!dst || dst_size == 0)
		return;
	const int octave = std::clamp(midi / 12 - 1, 0, 9);
	dst[0] = static_cast<char>('0' + octave);
	if (dst_size > 1)
		dst[1] = '\0';
}

void append_text(char *dst, std::size_t dst_size, const char *text);

struct RangeResult {
	int midi = 0;
	float confidence = 0.0f;
	float score = 0.0f;
};

float probe_level(const std::array<float, kNoteProbeCount> &powers, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return 0.0f;
	return std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
}

float bass_candidate_score(const std::array<float, kNoteProbeCount> &powers, int midi, bool include_harmonics)
{
	float score = probe_level(powers, midi);
	if (include_harmonics) {
		score += probe_level(powers, midi + 12) * 0.38f;
		score += probe_level(powers, midi + 19) * 0.22f;
		score += probe_level(powers, midi + 24) * 0.12f;
	}
	return score;
}

RangeResult dominant_bass_note(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi,
			       bool include_harmonics)
{
	float total = 0.0f;
	float second_score = 0.0f;
	RangeResult result;

	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float score = bass_candidate_score(powers, midi, include_harmonics);
		total += std::max(score, 0.0f);
		if (score > result.score) {
			second_score = result.score;
			result.score = score;
			result.midi = midi;
		} else {
			second_score = std::max(second_score, score);
		}
	}

	if (include_harmonics && result.score > 1.0e-6f) {
		for (int lower = result.midi - 12; lower >= min_midi; lower -= 12) {
			const float lower_fundamental = probe_level(powers, lower);
			const float current_fundamental = probe_level(powers, result.midi);
			const float lower_score = bass_candidate_score(powers, lower, true);
			if (lower_fundamental < current_fundamental * 0.14f || lower_score < result.score * 0.55f)
				break;
			result.midi = lower;
			result.score = lower_score;
		}
	}

	const float total_confidence = total > 1.0e-6f ? result.score / total : 0.0f;
	const float runner_up_confidence =
		result.score + second_score > 1.0e-6f ? result.score / (result.score + second_score) : 0.0f;
	result.confidence = std::clamp(std::max(total_confidence, runner_up_confidence * 0.55f), 0.0f, 1.0f);
	return result;
}

bool full_mix_bass_supported(const std::array<float, kNoteProbeCount> &powers, const RangeResult &low_note,
			     const RangeResult &broad_note)
{
	if (low_note.midi < kFirstMidi || low_note.score <= 1.0e-6f || low_note.confidence < kMixedBassMinConfidence)
		return false;

	const float fundamental = probe_level(powers, low_note.midi);
	const float broad_level = broad_note.midi >= kFirstMidi ? probe_level(powers, broad_note.midi) : 0.0f;
	const float broad_ratio_floor = fundamental >= broad_level * 0.35f ? 0.12f : kMixedBassMinBroadScoreRatio;
	if (broad_note.score > 1.0e-6f && low_note.score < broad_note.score * broad_ratio_floor)
		return false;
	return fundamental > 1.0e-6f && (broad_level <= 1.0e-6f || fundamental >= broad_level * 0.075f);
}

struct NoteCandidate {
	int midi = -1;
	float score = 0.0f;
	float ownership_confidence = 1.0f;
};

template <typename T, std::size_t Capacity> struct FixedList {
	std::array<T, Capacity> items = {};
	std::size_t count = 0;

	bool push_back(const T &value)
	{
		if (count >= Capacity)
			return false;
		items[count++] = value;
		return true;
	}

	bool empty() const { return count == 0; }
	std::size_t size() const { return count; }
	T &operator[](std::size_t index) { return items[index]; }
	const T &operator[](std::size_t index) const { return items[index]; }
	T &front() { return items[0]; }
	const T &front() const { return items[0]; }
	T *begin() { return items.data(); }
	T *end() { return items.data() + count; }
	const T *begin() const { return items.data(); }
	const T *end() const { return items.data() + count; }
};

using NoteCandidateList = FixedList<NoteCandidate, kNoteProbeCount>;

struct NoteEvidence {
	int midi = -1;
	float spectral_level = 0.0f;
	float pitch_confidence = 0.0f;
	float tuning_error_cents = 0.0f;
	float onset_strength = 0.0f;
	float decay_rate = 0.0f;
	float pitch_stability = 0.0f;
	float harmonicity = 0.0f;
	float harmonic_fit_error = 0.0f;
	float spectral_centroid = 0.0f;
	float spectral_slope = 0.0f;
	float local_noise_level = 0.0f;
	std::array<float, 5> ownership_scores = {};
	InstrumentKind owner = InstrumentKind::Ambiguous;
	float ownership_confidence = 0.0f;
};

struct TemporalNoteFeatures {
	float onset_strength = 0.0f;
	float decay_rate = 0.0f;
	float pitch_stability = 0.0f;
};

NoteCandidate ownership_weighted_candidate(const NoteCandidate &candidate, const NoteEvidence &evidence)
{
	NoteCandidate weighted = candidate;
	weighted.ownership_confidence = std::clamp(evidence.ownership_confidence, 0.0f, 1.0f);
	weighted.score *= weighted.ownership_confidence;
	return weighted;
}

enum class TimbreKind : std::size_t {
	Keyboard = 0,
	Guitar = 1,
	Other = 2,
};

constexpr std::size_t kTimbreKindCount = 3;
constexpr std::size_t kTimbreBandCount = 5;
constexpr std::array<int, kTimbreBandCount> kTimbreIntervals = {0, 12, 19, 24, 28};
constexpr std::array<std::array<float, kTimbreBandCount>, kTimbreKindCount> kTimbreTemplates = {{
	{1.00f, 0.12f, 0.04f, 0.02f, 0.01f},
	{1.00f, 0.36f, 0.17f, 0.07f, 0.03f},
	{1.00f, 0.62f, 0.42f, 0.27f, 0.16f},
}};

struct TimbreMix {
	std::array<float, kTimbreBandCount> bands = {};
	std::array<float, kTimbreKindCount> weights = {};
};

bool likely_lower_harmonic(const std::array<float, kNoteProbeCount> &scores, int min_midi, int midi, float score)
{
	static constexpr int kHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
	for (int interval : kHarmonicIntervals) {
		const int lower = midi - interval;
		if (lower < min_midi || lower < kFirstMidi)
			continue;
		if (scores[lower - kFirstMidi] > score / kHarmonicMaskRatio)
			return true;
	}
	return false;
}

bool has_complex_harmonic_support(const std::array<float, kNoteProbeCount> &powers, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;

	const float fundamental = std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
	if (fundamental <= 1.0e-6f)
		return false;

	float strongest_partial = 0.0f;
	float partial_sum = 0.0f;
	int partial_count = 0;
	static constexpr int kIntervals[] = {12, 19, 24, 28, 31};
	for (int interval : kIntervals) {
		const int harmonic_midi = midi + interval;
		if (harmonic_midi > kLastMidi)
			continue;
		const float partial = std::sqrt(std::max(powers[harmonic_midi - kFirstMidi], 0.0f));
		strongest_partial = std::max(strongest_partial, partial);
		partial_sum += partial;
		if (partial >= fundamental * 0.045f)
			++partial_count;
	}

	return strongest_partial >= fundamental * 0.07f || partial_sum >= fundamental * 0.13f ||
	       partial_count >= 2;
}

bool solve_linear_system(float matrix[3][4], int size, std::array<float, 3> &solution)
{
	for (int column = 0; column < size; ++column) {
		int pivot = column;
		for (int row = column + 1; row < size; ++row) {
			if (std::abs(matrix[row][column]) > std::abs(matrix[pivot][column]))
				pivot = row;
		}
		if (std::abs(matrix[pivot][column]) < 1.0e-8f)
			return false;
		for (int col = column; col <= size; ++col)
			std::swap(matrix[column][col], matrix[pivot][col]);

		const float divisor = matrix[column][column];
		for (int col = column; col <= size; ++col)
			matrix[column][col] /= divisor;

		for (int row = 0; row < size; ++row) {
			if (row == column)
				continue;
			const float factor = matrix[row][column];
			for (int col = column; col <= size; ++col)
				matrix[row][col] -= factor * matrix[column][col];
		}
	}

	for (int row = 0; row < size; ++row)
		solution[row] = matrix[row][size];
	return true;
}

std::array<float, kTimbreKindCount> fit_timbre_weights(const std::array<float, kTimbreBandCount> &bands)
{
	std::array<float, kTimbreKindCount> best = {};
	float best_residual = 1.0e30f;

	for (int mask = 1; mask < (1 << static_cast<int>(kTimbreKindCount)); ++mask) {
		std::array<int, 3> active = {};
		int active_count = 0;
		for (int i = 0; i < static_cast<int>(kTimbreKindCount); ++i) {
			if (mask & (1 << i))
				active[active_count++] = i;
		}

		float matrix[3][4] = {};
		for (int row = 0; row < active_count; ++row) {
			for (int col = 0; col < active_count; ++col) {
				for (std::size_t band = 0; band < kTimbreBandCount; ++band) {
					matrix[row][col] +=
						kTimbreTemplates[active[row]][band] *
						kTimbreTemplates[active[col]][band];
				}
			}
			for (std::size_t band = 0; band < kTimbreBandCount; ++band)
				matrix[row][active_count] += kTimbreTemplates[active[row]][band] * bands[band];
		}

		std::array<float, 3> active_solution = {};
		if (!solve_linear_system(matrix, active_count, active_solution))
			continue;

		std::array<float, kTimbreKindCount> weights = {};
		bool valid = true;
		for (int i = 0; i < active_count; ++i) {
			if (active_solution[i] < -1.0e-4f) {
				valid = false;
				break;
			}
			weights[active[i]] = std::max(active_solution[i], 0.0f);
		}
		if (!valid)
			continue;

		float residual = 0.0f;
		for (std::size_t band = 0; band < kTimbreBandCount; ++band) {
			float predicted = 0.0f;
			for (std::size_t kind = 0; kind < kTimbreKindCount; ++kind)
				predicted += weights[kind] * kTimbreTemplates[kind][band];
			const float error = predicted - bands[band];
			residual += error * error;
		}

		if (residual < best_residual) {
			best_residual = residual;
			best = weights;
		}
	}

	return best;
}

TimbreMix timbre_mix_for_midi(const std::array<float, kNoteProbeCount> &powers, int midi)
{
	TimbreMix mix;
	for (std::size_t band = 0; band < kTimbreBandCount; ++band) {
		const int harmonic_midi = midi + kTimbreIntervals[band];
		if (harmonic_midi > kLastMidi)
			continue;
		mix.bands[band] = std::sqrt(std::max(powers[harmonic_midi - kFirstMidi], 0.0f));
	}

	if (mix.bands[0] > 1.0e-6f)
		mix.weights = fit_timbre_weights(mix.bands);
	return mix;
}

float timbre_fit_residual(const TimbreMix &mix)
{
	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return 1.0f;

	float squared_error = 0.0f;
	for (std::size_t band = 0; band < kTimbreBandCount; ++band) {
		float predicted = 0.0f;
		for (std::size_t kind = 0; kind < kTimbreKindCount; ++kind)
			predicted += mix.weights[kind] * kTimbreTemplates[kind][band];
		const float normalized_error = (predicted - mix.bands[band]) / fundamental;
		squared_error += normalized_error * normalized_error;
	}
	return std::sqrt(squared_error / static_cast<float>(kTimbreBandCount));
}

float local_spectral_noise_ratio(const std::array<float, kNoteProbeCount> &powers, int midi, float fundamental)
{
	if (fundamental <= 1.0e-6f)
		return 1.0f;

	float noise_sum = 0.0f;
	int noise_count = 0;
	for (int offset : {-3, -2, -1, 1, 2, 3}) {
		const int neighbor = midi + offset;
		if (neighbor < kFirstMidi || neighbor > kLastMidi)
			continue;
		noise_sum += std::sqrt(std::max(powers[neighbor - kFirstMidi], 0.0f));
		++noise_count;
	}
	return noise_count > 0 ? (noise_sum / static_cast<float>(noise_count)) / fundamental : 0.0f;
}

TemporalNoteFeatures temporal_note_features(float current_level, float previous_level)
{
	TemporalNoteFeatures features;
	const float current = std::clamp(current_level, 0.0f, 1.0f);
	const float previous = std::clamp(previous_level, 0.0f, 1.0f);
	const float larger = std::max(current, previous);
	features.onset_strength =
		std::clamp((current - previous) / std::max(previous, 0.08f), 0.0f, 1.0f);
	features.decay_rate =
		std::clamp((previous - current) / std::max(previous, 0.08f), 0.0f, 1.0f);
	features.pitch_stability =
		larger > 1.0e-6f ? std::clamp(1.0f - std::abs(current - previous) / larger, 0.0f, 1.0f) : 0.0f;
	return features;
}

NoteEvidence build_note_evidence(const std::array<float, kNoteProbeCount> &powers,
				 const NoteCandidate &candidate, float strongest_score, const TimbreMix &mix,
				 const TemporalNoteFeatures &temporal)
{
	NoteEvidence evidence;
	evidence.midi = candidate.midi;
	evidence.spectral_level =
		strongest_score > 1.0e-6f ? std::clamp(candidate.score / strongest_score, 0.0f, 1.0f) : 0.0f;
	evidence.onset_strength = temporal.onset_strength;
	evidence.decay_rate = temporal.decay_rate;
	evidence.pitch_stability = temporal.pitch_stability;

	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return evidence;

	float harmonic_sum = 0.0f;
	float weighted_interval_sum = 0.0f;
	for (std::size_t band = 1; band < kTimbreBandCount; ++band) {
		harmonic_sum += mix.bands[band];
		weighted_interval_sum += mix.bands[band] * static_cast<float>(kTimbreIntervals[band]);
	}
	const float total_band_energy = fundamental + harmonic_sum;
	evidence.harmonicity = harmonic_sum / fundamental;
	evidence.harmonic_fit_error = timbre_fit_residual(mix);
	evidence.spectral_centroid =
		total_band_energy > 1.0e-6f ?
			std::clamp(weighted_interval_sum /
					   (total_band_energy *
					    static_cast<float>(kTimbreIntervals.back())),
				   0.0f, 1.0f) :
			0.0f;
	const float low_partials = fundamental + mix.bands[1];
	const float high_partials = mix.bands[2] + mix.bands[3] + mix.bands[4];
	evidence.spectral_slope = high_partials / std::max(low_partials, 1.0e-6f);
	evidence.local_noise_level = local_spectral_noise_ratio(powers, candidate.midi, fundamental);
	const float noise_penalty = std::clamp(1.0f - evidence.local_noise_level * 0.45f, 0.35f, 1.0f);
	const float fit_penalty = std::clamp(1.0f - evidence.harmonic_fit_error * 0.40f, 0.45f, 1.0f);
	evidence.pitch_confidence = std::clamp(evidence.spectral_level * noise_penalty * fit_penalty, 0.0f, 1.0f);
	return evidence;
}

bool likely_selected_harmonic(const NoteCandidate &fundamental, const NoteCandidate &candidate)
{
	if (candidate.midi <= fundamental.midi)
		return false;
	static constexpr int kHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
	const int interval = candidate.midi - fundamental.midi;
	for (int harmonic_interval : kHarmonicIntervals) {
		if (interval == harmonic_interval && candidate.score <= fundamental.score * kHarmonicMaskRatio)
			return true;
	}
	return false;
}

bool pitch_class_available(int midi, const std::array<bool, 12> *blocked_pitch_classes,
			   const std::array<bool, 12> *allowed_pitch_classes,
			   const std::array<bool, kNoteProbeCount> *allowed_midis)
{
	if (allowed_midis && (midi < kFirstMidi || midi > kLastMidi || !(*allowed_midis)[midi - kFirstMidi]))
		return false;
	const int pitch_class = ((midi % 12) + 12) % 12;
	if (blocked_pitch_classes && (*blocked_pitch_classes)[pitch_class])
		return false;
	if (allowed_pitch_classes && !(*allowed_pitch_classes)[pitch_class])
		return false;
	return true;
}

NoteCandidateList note_peak_candidates(const std::array<float, kNoteProbeCount> &powers, int min_midi,
				       int max_midi, int max_notes,
				       const std::array<bool, 12> *blocked_pitch_classes = nullptr,
				       const std::array<bool, 12> *allowed_pitch_classes = nullptr,
				       bool suppress_adjacent_neighbors = false,
				       const std::array<bool, kNoteProbeCount> *allowed_midis = nullptr,
				       float relative_floor = kNoteRelativeFloor)
{
	std::array<float, kNoteProbeCount> scores = {};
	float strongest_score = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (!pitch_class_available(midi, blocked_pitch_classes, allowed_pitch_classes, allowed_midis))
			continue;
		const float score = std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
		scores[midi - kFirstMidi] = score;
		strongest_score = std::max(strongest_score, score);
	}

	NoteCandidateList candidates;
	if (strongest_score <= 1.0e-6f)
		return candidates;

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float score = scores[midi - kFirstMidi];
		if (score >= strongest_score * std::clamp(relative_floor, 0.01f, 1.0f) &&
		    !likely_lower_harmonic(scores, min_midi, midi, score))
			candidates.push_back(NoteCandidate{midi, score});
	}

	std::sort(candidates.begin(), candidates.end(),
		  [](const NoteCandidate &a, const NoteCandidate &b) { return a.score > b.score; });

	NoteCandidateList selected;
	for (const NoteCandidate &candidate : candidates) {
		bool masked = false;
		for (const NoteCandidate &existing : selected) {
			if ((suppress_adjacent_neighbors && std::abs(existing.midi - candidate.midi) <= 1) ||
			    likely_selected_harmonic(existing, candidate)) {
				masked = true;
				break;
			}
		}
		if (masked)
			continue;
		selected.push_back(candidate);
		if (static_cast<int>(selected.size()) >= max_notes)
			break;
	}

	return selected;
}

std::array<float, 12> peak_chroma_for_range(const std::array<float, kNoteProbeCount> &powers, int min_midi,
					    int max_midi,
					    const std::array<bool, 12> *blocked_pitch_classes = nullptr,
					    bool suppress_adjacent_neighbors = false,
					    const std::array<bool, kNoteProbeCount> *allowed_midis = nullptr,
					    float relative_floor = kNoteRelativeFloor)
{
	std::array<float, 12> chroma = {};
	for (const NoteCandidate &candidate : note_peak_candidates(powers, min_midi, max_midi, 6,
								   blocked_pitch_classes, nullptr,
								   suppress_adjacent_neighbors, allowed_midis,
								   relative_floor)) {
		const int pitch_class = ((candidate.midi % 12) + 12) % 12;
		chroma[pitch_class] = std::max(chroma[pitch_class], candidate.score);
	}

	const float max_value = *std::max_element(chroma.begin(), chroma.end());
	if (max_value > 0.0f) {
		for (float &value : chroma)
			value /= max_value;
	}

	return chroma;
}

int lowest_peak_pitch_class(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi,
			    const std::array<bool, 12> *blocked_pitch_classes = nullptr,
			    bool suppress_adjacent_neighbors = false,
			    const std::array<bool, kNoteProbeCount> *allowed_midis = nullptr)
{
	const NoteCandidateList candidates =
		note_peak_candidates(powers, min_midi, max_midi, 6, blocked_pitch_classes, nullptr,
				     suppress_adjacent_neighbors, allowed_midis);
	if (candidates.empty())
		return -1;

	int lowest_midi = candidates.front().midi;
	for (const NoteCandidate &candidate : candidates)
		lowest_midi = std::min(lowest_midi, candidate.midi);
	return ((lowest_midi % 12) + 12) % 12;
}

struct FullMixOwnership {
	std::array<bool, kNoteProbeCount> keyboard = {};
	std::array<bool, kNoteProbeCount> guitar = {};
	std::array<bool, kNoteProbeCount> vocal = {};
	std::array<bool, kNoteProbeCount> other = {};
	std::array<bool, kNoteProbeCount> ambiguous = {};
	std::array<float, kNoteProbeCount> global_note_levels = {};
	std::array<float, 12> global_chroma = {};
	NoteCandidateList keyboard_candidates;
	NoteCandidateList guitar_candidates;
	NoteCandidateList vocal_candidates;
	NoteCandidateList other_candidates;
	NoteCandidateList ambiguous_candidates;
};

int count_owned_notes(const std::array<bool, kNoteProbeCount> &mask)
{
	int count = 0;
	for (bool owned : mask) {
		if (owned)
			++count;
	}
	return count;
}

int count_ambiguous_pitch_classes(const FullMixOwnership &ownership)
{
	std::array<bool, 12> pitch_classes = {};
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		if (!ownership.ambiguous[midi - kFirstMidi])
			continue;
		const int pitch_class = ((midi % 12) + 12) % 12;
		pitch_classes[pitch_class] = true;
	}

	int count = 0;
	for (bool active : pitch_classes) {
		if (active)
			++count;
	}
	return count;
}

void remove_candidate_midi(NoteCandidateList &candidates, int midi)
{
	std::size_t write = 0;
	for (std::size_t read = 0; read < candidates.size(); ++read) {
		if (candidates[read].midi == midi)
			continue;
		candidates[write++] = candidates[read];
	}
	candidates.count = write;
}

void demote_sparse_full_mix_owner(FullMixOwnership &ownership, std::array<bool, kNoteProbeCount> &mask,
				  NoteCandidateList &owner_candidates,
				  const std::array<float, kNoteProbeCount> &candidate_scores)
{
	if (count_owned_notes(mask) != 1 || count_ambiguous_pitch_classes(ownership) < 2)
		return;

	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
		if (!mask[index])
			continue;
		mask[index] = false;
		remove_candidate_midi(owner_candidates, midi);
		ownership.ambiguous[index] = true;
		ownership.ambiguous_candidates.push_back(NoteCandidate{midi, candidate_scores[index]});
		return;
	}
}

float relative_timbre_weight(const TimbreMix &mix, TimbreKind kind)
{
	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return 0.0f;
	return mix.weights[static_cast<std::size_t>(kind)] / fundamental;
}

bool full_mix_vocal_profile_supported(const NoteEvidence &evidence, float second, float third, float fourth,
				      bool polyphonic_vocal_context)
{
	if (polyphonic_vocal_context)
		return false;
	if (evidence.spectral_level < 0.38f)
		return false;
	if (evidence.local_noise_level > 0.22f || evidence.harmonic_fit_error > 0.40f)
		return false;
	if (evidence.spectral_centroid > 0.24f)
		return false;

	const bool clean_sustained_like_partials =
		second <= 0.10f && third <= 0.065f && fourth <= 0.050f;
	const bool near_pure_tone_voice =
		second <= 0.045f && third <= 0.025f && fourth <= 0.018f && evidence.spectral_slope <= 0.10f;
	return clean_sustained_like_partials || near_pure_tone_voice;
}

bool competing_full_mix_timbres(float keyboard_weight, float guitar_weight, float other_weight)
{
	const float total = keyboard_weight + guitar_weight + other_weight;
	if (total <= 1.0e-6f)
		return false;

	std::array<float, 3> weights = {keyboard_weight, guitar_weight, other_weight};
	std::sort(weights.begin(), weights.end(), [](float lhs, float rhs) { return lhs > rhs; });
	const float best_share = weights[0] / total;
	const float second_share = weights[1] / total;
	const float third_share = weights[2] / total;

	if (weights[1] >= 0.055f && best_share <= 0.76f && second_share >= 0.18f)
		return true;
	if (weights[2] >= 0.035f && best_share <= 0.82f && third_share >= 0.10f)
		return true;
	return false;
}

bool blended_full_mix_upper_partials(float second, float third, float fourth, float fifth)
{
	return second >= 0.22f && second <= 0.58f && third >= 0.10f && fourth >= 0.085f &&
	       fifth >= 0.040f;
}

InstrumentKind choose_full_mix_owner(const std::array<float, kNoteProbeCount> &powers,
				     const NoteCandidate &candidate, float strongest_score,
				     bool polyphonic_vocal_context, const TemporalNoteFeatures &temporal,
				     NoteEvidence &evidence)
{
	if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi || strongest_score <= 1.0e-6f)
		return InstrumentKind::Ambiguous;

	const TimbreMix mix = timbre_mix_for_midi(powers, candidate.midi);
	evidence = build_note_evidence(powers, candidate, strongest_score, mix, temporal);
	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return InstrumentKind::Ambiguous;

	const float second = mix.bands[1] / fundamental;
	const float third = mix.bands[2] / fundamental;
	const float fourth = mix.bands[3] / fundamental;
	const float fifth = mix.bands[4] / fundamental;
	const float keyboard_weight = relative_timbre_weight(mix, TimbreKind::Keyboard);
	const float guitar_weight = relative_timbre_weight(mix, TimbreKind::Guitar);
	const float other_weight = relative_timbre_weight(mix, TimbreKind::Other);
	const float note_strength = evidence.spectral_level;
	const float clean_pitch_bonus = evidence.pitch_confidence * 0.12f;
	const float noise_penalty = std::clamp(1.0f - evidence.local_noise_level * 0.42f, 0.42f, 1.0f);
	const float fit_penalty = std::clamp(1.0f - evidence.harmonic_fit_error * 0.32f, 0.52f, 1.0f);

	std::array<float, 4> scores = {};
	if (competing_full_mix_timbres(keyboard_weight, guitar_weight, other_weight)) {
		const float total = keyboard_weight + guitar_weight + other_weight;
		evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Keyboard)] =
			keyboard_weight / total;
		evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Guitar)] =
			guitar_weight / total;
		evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Other)] = other_weight / total;
		evidence.ownership_confidence =
			std::max({keyboard_weight, guitar_weight, other_weight}) / total;
		return InstrumentKind::Ambiguous;
	}
	if (blended_full_mix_upper_partials(second, third, fourth, fifth))
		return InstrumentKind::Ambiguous;

	if (candidate.midi >= 48 && candidate.midi <= 83 && second <= 0.56f) {
		scores[0] = keyboard_weight * 1.18f + std::max(0.0f, 0.50f - second) * 0.30f +
			    std::max(0.0f, 0.16f - third) * 0.08f + clean_pitch_bonus;
		if (evidence.pitch_stability >= 0.62f && evidence.onset_strength <= 0.45f)
			scores[0] += 0.06f;
		if (evidence.spectral_centroid > 0.34f || evidence.spectral_slope > 0.18f)
			scores[0] *= 0.78f;
	}
	if (candidate.midi >= kGuitarMinMidi && candidate.midi <= kGuitarMaxMidi && second >= 0.12f &&
	    third >= 0.035f) {
		scores[1] = guitar_weight * 1.18f + second * 0.24f + third * 0.16f;
		if (evidence.onset_strength >= 0.35f)
			scores[1] += evidence.onset_strength * 0.08f;
		if (evidence.decay_rate >= 0.18f)
			scores[1] += evidence.decay_rate * 0.05f;
		if (evidence.spectral_centroid >= 0.10f && evidence.spectral_centroid <= 0.42f)
			scores[1] += 0.08f;
		if (evidence.spectral_slope >= 0.035f && evidence.spectral_slope <= 0.30f)
			scores[1] += 0.05f;
		if (second > 0.75f || fourth > 0.36f)
			scores[1] *= 0.72f;
	}
	if (candidate.midi >= 72 && candidate.midi <= kVocalMaxMidi &&
	    full_mix_vocal_profile_supported(evidence, second, third, fourth, polyphonic_vocal_context)) {
		scores[2] = 0.74f + std::max(0.0f, 0.10f - second) * 1.8f +
			    std::max(0.0f, 0.065f - third) * 1.3f;
		if (evidence.onset_strength > 0.72f && evidence.pitch_stability < 0.30f)
			scores[2] *= 0.80f;
		if (evidence.pitch_stability >= 0.55f)
			scores[2] += 0.05f;
		if (note_strength < 0.52f)
			scores[2] *= 0.82f;
	}
	if (candidate.midi >= 60 && candidate.midi <= kOtherMaxMidi && second >= 0.24f &&
	    (fourth >= 0.06f || fifth >= 0.035f)) {
		scores[3] = other_weight * 1.12f + second * 0.18f + third * 0.14f + fourth * 0.10f;
		if (evidence.pitch_stability >= 0.45f)
			scores[3] += 0.04f;
		if (evidence.harmonicity >= 0.62f || evidence.spectral_centroid >= 0.20f)
			scores[3] += 0.10f;
	}
	for (float &score : scores)
		score *= noise_penalty * fit_penalty;

	float total = 0.0f;
	for (float score : scores)
		total += std::max(score, 0.0f);
	if (total <= 1.0e-6f)
		return InstrumentKind::Ambiguous;

	int best = 0;
	int second_best = 1;
	if (scores[second_best] > scores[best])
		std::swap(best, second_best);
	for (int i = 2; i < static_cast<int>(scores.size()); ++i) {
		if (scores[i] > scores[best]) {
			second_best = best;
			best = i;
		} else if (scores[i] > scores[second_best]) {
			second_best = i;
		}
	}

	const float best_probability = scores[best] / total;
	const float second_probability = scores[second_best] / total;
	evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Keyboard)] = scores[0] / total;
	evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Guitar)] = scores[1] / total;
	evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Vocal)] = scores[2] / total;
	evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Other)] = scores[3] / total;
	evidence.ownership_confidence = best_probability;
	if (best == 2 && polyphonic_vocal_context)
		return InstrumentKind::Ambiguous;
	if (best_probability < 0.65f || best_probability - second_probability < 0.20f)
		return InstrumentKind::Ambiguous;

	InstrumentKind owner = InstrumentKind::Ambiguous;
	switch (best) {
	case 0:
		owner = InstrumentKind::Keyboard;
		break;
	case 1:
		owner = InstrumentKind::Guitar;
		break;
	case 2:
		owner = InstrumentKind::Vocal;
		break;
	case 3:
		owner = InstrumentKind::Other;
		break;
	default:
		owner = InstrumentKind::Ambiguous;
		break;
	}
	evidence.owner = owner;
	return owner;
}

FullMixOwnership build_full_mix_ownership(const std::array<float, kNoteProbeCount> &powers,
					  const std::array<float, kNoteProbeCount> &detection_powers,
					  float rms,
					  const std::array<float, kNoteProbeCount> &previous_note_levels,
					  std::array<float, kNoteProbeCount> &current_note_levels)
{
	FullMixOwnership ownership;
	current_note_levels.fill(0.0f);
	if (rms < kNoteRmsFloor)
		return ownership;

	const NoteCandidateList candidates =
		note_peak_candidates(detection_powers, kGuitarMinMidi, kLastMidi, 24, nullptr, nullptr, true,
				     nullptr, kMixedNoteRelativeFloor);
	std::array<float, kNoteProbeCount> candidate_scores = {};
	float strongest_score = 0.0f;
	for (const NoteCandidate &candidate : candidates) {
		strongest_score = std::max(strongest_score, candidate.score);
		if (candidate.midi >= kFirstMidi && candidate.midi <= kLastMidi)
			candidate_scores[candidate.midi - kFirstMidi] = candidate.score;
	}
	if (strongest_score <= 1.0e-6f)
		return ownership;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;
		current_note_levels[candidate.midi - kFirstMidi] =
			std::max(current_note_levels[candidate.midi - kFirstMidi],
				 std::clamp(candidate.score / strongest_score, 0.0f, 1.0f));
	}

	int vocal_range_candidate_count = 0;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi >= 72 && candidate.midi <= kVocalMaxMidi &&
		    candidate.score >= strongest_score * 0.35f)
			++vocal_range_candidate_count;
	}
	const bool polyphonic_vocal_context = vocal_range_candidate_count >= 2;

	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;

		NoteEvidence evidence;
		const std::size_t note_index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
		const TemporalNoteFeatures temporal =
			temporal_note_features(current_note_levels[note_index], previous_note_levels[note_index]);
		const InstrumentKind owner =
			choose_full_mix_owner(powers, candidate, strongest_score, polyphonic_vocal_context,
					      temporal, evidence);

		const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
		const int pitch_class = ((candidate.midi % 12) + 12) % 12;
		const float chroma_level = std::clamp(candidate.score / strongest_score, 0.0f, 1.0f);
		ownership.global_note_levels[index] = std::max(ownership.global_note_levels[index], chroma_level);
		ownership.global_chroma[pitch_class] = std::max(ownership.global_chroma[pitch_class], chroma_level);

		switch (owner) {
		case InstrumentKind::Keyboard:
			ownership.keyboard[index] = true;
			ownership.keyboard_candidates.push_back(ownership_weighted_candidate(candidate, evidence));
			break;
		case InstrumentKind::Guitar:
			ownership.guitar[index] = true;
			ownership.guitar_candidates.push_back(ownership_weighted_candidate(candidate, evidence));
			break;
		case InstrumentKind::Vocal:
			ownership.vocal[index] = true;
			ownership.vocal_candidates.push_back(ownership_weighted_candidate(candidate, evidence));
			break;
		case InstrumentKind::Other:
			ownership.other[index] = true;
			ownership.other_candidates.push_back(ownership_weighted_candidate(candidate, evidence));
			break;
		case InstrumentKind::Bass:
		case InstrumentKind::Ambiguous:
		default:
			ownership.ambiguous[index] = true;
			ownership.ambiguous_candidates.push_back(candidate);
			break;
		}
	}

	demote_sparse_full_mix_owner(ownership, ownership.keyboard, ownership.keyboard_candidates, candidate_scores);
	demote_sparse_full_mix_owner(ownership, ownership.guitar, ownership.guitar_candidates, candidate_scores);
	demote_sparse_full_mix_owner(ownership, ownership.other, ownership.other_candidates, candidate_scores);

	return ownership;
}

void set_note_grid_from_candidates(NoteGrid &grid, const NoteCandidateList &candidates, float rms, int max_notes)
{
	for (NoteCell &cell : grid.cells)
		cell = {};
	for (auto &row : grid.rows) {
		for (NoteCell &cell : row)
			cell = {};
	}
	if (rms < kNoteRmsFloor || candidates.empty())
		return;

	float strongest_score = 0.0f;
	for (const NoteCandidate &candidate : candidates)
		strongest_score = std::max(strongest_score, candidate.score);

	int written = 0;
	for (const NoteCandidate &candidate : candidates) {
		if (written >= max_notes)
			break;
		const int pitch_class = ((candidate.midi % 12) + 12) % 12;
		NoteCell cell;
		write_octave(cell.label, sizeof(cell.label), candidate.midi);
		cell.level = strongest_score > 1.0e-6f ?
				     std::clamp(candidate.score / strongest_score *
							std::clamp(rms / kFullNoteRms, 0.0f, 1.0f),
						0.0f, 1.0f) :
				     0.0f;
		cell.midi = candidate.midi;
		cell.active = true;
		for (auto &row : grid.rows) {
			if (row[pitch_class].active)
				continue;
			row[pitch_class] = cell;
			break;
		}
		if (!grid.cells[pitch_class].active || cell.level > grid.cells[pitch_class].level)
			grid.cells[pitch_class] = cell;
		++written;
	}
}

struct ChordResult {
	char label[64] = {};
	std::array<bool, 12> tones = {};
	int root = -1;
	float confidence = 0.0f;
	float margin = 0.0f;
	bool uncertain = true;
};

struct ChordCandidate {
	char label[16] = {};
	std::array<bool, 12> tones = {};
	uint16_t mask = 0;
	int root = -1;
	int tone_count = 0;
	float score = 0.0f;
};

using ChordCandidateList = FixedList<ChordCandidate, 256>;

bool chord_candidate_compatible(const ChordCandidate &lhs, const ChordCandidate &rhs)
{
	if (lhs.mask == rhs.mask)
		return true;
	if (lhs.root != rhs.root)
		return false;
	return (lhs.mask & ~rhs.mask) == 0 || (rhs.mask & ~lhs.mask) == 0;
}

ChordResult detect_chord(const std::array<float, 12> &chroma, int bass_pitch_class = -1, bool allow_extensions = true)
{
	ChordResult best;
	float best_score = 0.0f;
	uint16_t best_mask = 0;
	ChordCandidate best_candidate;
	ChordCandidateList candidates;
	static constexpr float kToneThreshold = 0.24f;

	auto tone = [&](int root, int offset) -> float { return chroma[(root + offset) % 12]; };
	auto present = [&](int root, int offset) -> bool { return tone(root, offset) >= kToneThreshold; };
	auto contains_interval = [](std::initializer_list<int> intervals, int needle) {
		for (int interval : intervals) {
			if (interval % 12 == needle)
				return true;
		}
		return false;
	};
	auto interval_weight = [](int interval) {
		switch (interval % 12) {
		case 0:
			return 1.20f;
		case 2:
		case 9:
		case 10:
		case 11:
			return 1.08f;
		case 6:
		case 7:
		case 8:
			return 0.95f;
		default:
			return 1.0f;
		}
	};
	auto consider = [&](int root, const char *suffix, float score, std::initializer_list<int> intervals) {
		if (root == bass_pitch_class)
			score += 0.40f;

		ChordCandidate candidate;
		candidate.root = root;
		candidate.score = score;
		std::snprintf(candidate.label, sizeof(candidate.label), "%s%s", note_name(root), suffix);
		for (int interval : intervals) {
			const int pitch_class = (root + interval) % 12;
			candidate.tones[pitch_class] = true;
			candidate.mask |= static_cast<uint16_t>(1u << pitch_class);
		}
		candidate.tone_count = static_cast<int>(intervals.size());
		candidates.push_back(candidate);

		if (score > best_score) {
			best_score = score;
			best_mask = candidate.mask;
			best_candidate = candidate;
			best.root = root;
			best.tones = candidate.tones;
		}
	};
	auto consider_template = [&](int root, const char *suffix, std::initializer_list<int> intervals, float priority) {
		float score = priority;
		for (int interval : intervals) {
			const float value = tone(root, interval);
			if (value < kToneThreshold)
				return;
			score += value * interval_weight(interval);
		}

		static constexpr int kConflictIntervals[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
		for (int interval : kConflictIntervals) {
			if (contains_interval(intervals, interval))
				continue;
			score -= tone(root, interval) * 0.18f;
		}

		consider(root, suffix, score, intervals);
	};

	for (int root = 0; root < 12; ++root) {
		if (tone(root, 0) < kToneThreshold)
			continue;

		if (allow_extensions) {
			consider_template(root, "9", {0, 2, 4, 7, 10}, 0.34f);
			consider_template(root, "maj9", {0, 2, 4, 7, 11}, 0.34f);
			consider_template(root, "m9", {0, 2, 3, 7, 10}, 0.34f);
			consider_template(root, "dim7", {0, 3, 6, 9}, 0.28f);
			consider_template(root, "m7b5", {0, 3, 6, 10}, 0.28f);
			consider_template(root, "7", {0, 4, 7, 10}, 0.22f);
			consider_template(root, "maj7", {0, 4, 7, 11}, 0.22f);
			consider_template(root, "m7", {0, 3, 7, 10}, 0.22f);
			consider_template(root, "6", {0, 4, 7, 9}, 0.20f);
			consider_template(root, "m6", {0, 3, 7, 9}, 0.20f);
			consider_template(root, "add9", {0, 2, 4, 7}, 0.20f);
		}
		consider_template(root, "", {0, 4, 7}, 0.06f);
		consider_template(root, "m", {0, 3, 7}, 0.06f);
		if (allow_extensions) {
			consider_template(root, "dim", {0, 3, 6}, 0.08f);
			consider_template(root, "aug", {0, 4, 8}, 0.08f);
		}
		consider_template(root, "sus2", {0, 2, 7}, 0.05f);
		consider_template(root, "sus4", {0, 5, 7}, 0.05f);
		if (!present(root, 2) && !present(root, 3) && !present(root, 4) && !present(root, 5) &&
		    !present(root, 6) && !present(root, 8) && !present(root, 9) && !present(root, 10) &&
		    !present(root, 11))
			consider_template(root, "pow", {0, 7}, 0.02f);
	}

	float chroma_sum = 0.0f;
	for (float value : chroma)
		chroma_sum += value;

	if (best_candidate.tone_count > 3 && chroma_sum > 1.0e-6f) {
		ChordCandidate simpler;
		float simpler_score = 0.0f;
		for (const ChordCandidate &candidate : candidates) {
			if (candidate.root != best_candidate.root || candidate.tone_count < 3 ||
			    candidate.tone_count >= best_candidate.tone_count)
				continue;
			if ((candidate.mask & ~best_candidate.mask) != 0)
				continue;
			const float normalized_gap = (best_score - candidate.score) / (chroma_sum + 1.0e-6f);
			if (normalized_gap > kChordWeakExtensionMargin)
				continue;
			if (candidate.score > simpler_score) {
				simpler_score = candidate.score;
				simpler = candidate;
			}
		}
		if (simpler_score > 0.0f) {
			best_score = simpler_score;
			best_mask = simpler.mask;
			best_candidate = simpler;
			best.root = simpler.root;
			best.tones = simpler.tones;
		}
	}

	float competing_score = 0.0f;
	for (const ChordCandidate &candidate : candidates) {
		if (chord_candidate_compatible(candidate, best_candidate))
			continue;
		competing_score = std::max(competing_score, candidate.score);
	}

	best.confidence = chroma_sum > 0.0f ? std::clamp(best_score / (chroma_sum + 1.0e-6f), 0.0f, 1.0f) : 0.0f;
	best.margin = chroma_sum > 0.0f ?
			      std::clamp((best_score - competing_score) / (chroma_sum + 1.0e-6f), 0.0f, 1.0f) :
			      0.0f;
	best.uncertain = best.confidence < 0.34f ||
			 (competing_score > 0.0f && best.confidence < kChordMarginConfidenceCeiling &&
			  best.margin < kChordCandidateMarginFloor);
	if (best.uncertain) {
		best.root = -1;
		best.tones.fill(false);
		copy_text(best.label, sizeof(best.label), "--");
		return best;
	}

	ChordCandidateList aliases;
	for (const ChordCandidate &candidate : candidates) {
		if (candidate.mask == best_mask)
			aliases.push_back(candidate);
	}

	std::sort(aliases.begin(), aliases.end(), [](const ChordCandidate &a, const ChordCandidate &b) {
		if (a.score != b.score)
			return a.score > b.score;
		return a.root < b.root;
	});

	best.label[0] = '\0';
	for (const ChordCandidate &candidate : aliases) {
		if (std::strstr(best.label, candidate.label))
			continue;
		if (best.label[0])
			append_text(best.label, sizeof(best.label), "=");
		append_text(best.label, sizeof(best.label), candidate.label);
		if (std::strlen(best.label) + 1 >= sizeof(best.label))
			break;
	}
	return best;
}

struct RootCandidate {
	std::array<float, 12> scores = {};
	int pitch_class = -1;
	float confidence = 0.0f;
	float total = 0.0f;
};

RootCandidate detect_root_candidate(const std::array<float, kNoteProbeCount> &powers, float rms)
{
	RootCandidate candidate;
	if (rms < kSilenceRms)
		return candidate;

	for (int midi = kFirstMidi; midi <= 84; ++midi) {
		const int pitch_class = ((midi % 12) + 12) % 12;
		float octave_weight = 0.25f;
		if (midi <= 47)
			octave_weight = 1.0f;
		else if (midi <= 59)
			octave_weight = 0.68f;
		else if (midi <= 72)
			octave_weight = 0.36f;

		candidate.scores[pitch_class] += std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f)) * octave_weight;
	}

	const ChordResult chord = detect_chord(peak_chroma_for_range(powers, 40, 84));
	if (chord.root >= 0 && chord.confidence >= 0.36f) {
		float seed_total = 0.0f;
		for (float score : candidate.scores)
			seed_total += score;
		candidate.scores[chord.root] += seed_total * chord.confidence * 1.10f;
	}

	float best_score = 0.0f;
	for (int i = 0; i < 12; ++i) {
		const float score = candidate.scores[i];
		candidate.total += score;
		if (score > best_score) {
			candidate.pitch_class = i;
			best_score = score;
		}
	}

	if (candidate.total <= 1.0e-6f || candidate.pitch_class < 0)
		return candidate;

	candidate.confidence = std::clamp(best_score / candidate.total * 2.6f, 0.0f, 1.0f);
	if (candidate.confidence < 0.28f)
		candidate.pitch_class = -1;
	return candidate;
}

enum class RootChordQuality {
	Major,
	Minor,
	Diminished,
	NoThird,
	Other,
};

struct ParsedRootChord {
	int root = -1;
	RootChordQuality quality = RootChordQuality::Other;
};

int note_letter_pitch_class(char note)
{
	switch (note) {
	case 'C':
		return 0;
	case 'D':
		return 2;
	case 'E':
		return 4;
	case 'F':
		return 5;
	case 'G':
		return 7;
	case 'A':
		return 9;
	case 'B':
		return 11;
	default:
		return -1;
	}
}

bool suffix_is(const char *suffix, std::size_t suffix_len, const char *expected)
{
	return std::strlen(expected) == suffix_len && std::strncmp(suffix, expected, suffix_len) == 0;
}

bool parse_root_chord_component(const char *start, std::size_t len, ParsedRootChord &parsed)
{
	if (!start || len == 0)
		return false;

	int root = note_letter_pitch_class(start[0]);
	if (root < 0)
		return false;

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#') {
		root = (root + 1) % 12;
		root_len = 2;
	}

	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;

	RootChordQuality quality = RootChordQuality::Other;
	if (suffix_len == 0 || suffix_is(suffix, suffix_len, "6") || suffix_is(suffix, suffix_len, "7") ||
	    suffix_is(suffix, suffix_len, "9") || suffix_is(suffix, suffix_len, "maj7") ||
	    suffix_is(suffix, suffix_len, "maj9") || suffix_is(suffix, suffix_len, "add9")) {
		quality = RootChordQuality::Major;
	} else if (suffix_is(suffix, suffix_len, "m") || suffix_is(suffix, suffix_len, "m6") ||
		   suffix_is(suffix, suffix_len, "m7") || suffix_is(suffix, suffix_len, "m9")) {
		quality = RootChordQuality::Minor;
	} else if (suffix_is(suffix, suffix_len, "dim") || suffix_is(suffix, suffix_len, "dim7") ||
		   suffix_is(suffix, suffix_len, "m7b5")) {
		quality = RootChordQuality::Diminished;
	} else if (suffix_is(suffix, suffix_len, "sus2") || suffix_is(suffix, suffix_len, "sus4") ||
		   suffix_is(suffix, suffix_len, "pow")) {
		quality = RootChordQuality::NoThird;
	}

	parsed.root = root;
	parsed.quality = quality;
	return true;
}

float major_key_chord_likelihood(int degree, RootChordQuality quality)
{
	switch (degree) {
	case 0:
		return quality == RootChordQuality::Major ? 1.35f :
		       quality == RootChordQuality::NoThird ? 0.82f :
							      0.20f;
	case 2:
		return quality == RootChordQuality::Minor ? 0.90f :
		       quality == RootChordQuality::NoThird ? 0.36f :
		       quality == RootChordQuality::Major   ? 0.28f :
							      0.08f;
	case 4:
		return quality == RootChordQuality::Minor ? 0.75f :
		       quality == RootChordQuality::NoThird ? 0.34f :
							      0.08f;
	case 5:
		return quality == RootChordQuality::Major ? 1.05f :
		       quality == RootChordQuality::NoThird ? 0.76f :
							      0.12f;
	case 7:
		return quality == RootChordQuality::Major ? 1.15f :
		       quality == RootChordQuality::NoThird ? 0.80f :
							      0.18f;
	case 9:
		return quality == RootChordQuality::Minor ? 0.85f :
		       quality == RootChordQuality::NoThird ? 0.34f :
							      0.10f;
	case 11:
		return quality == RootChordQuality::Diminished ? 0.70f :
		       quality == RootChordQuality::Minor	   ? 0.25f :
		       quality == RootChordQuality::NoThird   ? 0.20f :
							      0.06f;
	default:
		return 0.04f;
	}
}

void add_chord_key_evidence(std::array<float, 12> &scores, const InstrumentState &chord, float weight)
{
	if (!chord.label[0] || chord.label[0] == '-' || chord.confidence < 0.28f || weight <= 0.0f)
		return;

	std::array<ParsedRootChord, 4> parsed_components = {};
	std::size_t parsed_count = 0;
	const char *cursor = chord.label;
	while (*cursor && parsed_count < parsed_components.size()) {
		const char *end = cursor;
		while (*end && *end != '=')
			++end;

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, static_cast<std::size_t>(end - cursor), parsed))
			parsed_components[parsed_count++] = parsed;

		cursor = *end == '=' ? end + 1 : end;
	}

	if (parsed_count == 0)
		return;

	const float component_weight = weight * std::clamp(chord.confidence, 0.0f, 1.0f) /
				       static_cast<float>(parsed_count);
	for (std::size_t i = 0; i < parsed_count; ++i) {
		const ParsedRootChord &parsed = parsed_components[i];
		for (int key = 0; key < 12; ++key) {
			const int degree = (parsed.root - key + 12) % 12;
			scores[key] += major_key_chord_likelihood(degree, parsed.quality) * component_weight;
		}
	}
}

bool strongest_grid_pitch_class(const NoteGrid &grid, int &pitch_class, float &level)
{
	pitch_class = -1;
	level = 0.0f;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < kFirstMidi || cell.level <= level)
				continue;
			pitch_class = ((cell.midi % 12) + 12) % 12;
			level = cell.level;
		}
	}
	return pitch_class >= 0;
}

void add_bass_key_evidence(std::array<float, 12> &scores, const NoteGrid &bass_notes)
{
	int bass_pitch_class = -1;
	float bass_level = 0.0f;
	if (!strongest_grid_pitch_class(bass_notes, bass_pitch_class, bass_level))
		return;

	static constexpr std::array<float, 12> kMajorBassDegreeWeights = {
		1.45f, 0.04f, 0.45f, 0.04f, 0.45f, 0.95f,
		0.03f, 1.00f, 0.04f, 0.65f, 0.04f, 0.16f,
	};

	const float weight = std::clamp(bass_level, 0.0f, 1.0f);
	for (int key = 0; key < 12; ++key) {
		const int degree = (bass_pitch_class - key + 12) % 12;
		scores[key] += kMajorBassDegreeWeights[degree] * weight;
	}
}

RootCandidate detect_root_candidate_with_context(const std::array<float, kNoteProbeCount> &powers, float rms,
						 const NoteGrid &bass_notes,
						 const InstrumentState &global_chord,
						 const InstrumentState &keyboard_chord,
						 const InstrumentState &guitar_chord,
						 const InstrumentState &other_chord)
{
	RootCandidate candidate;
	if (rms < kSilenceRms)
		return candidate;

	const RootCandidate spectral = detect_root_candidate(powers, rms);
	add_bass_key_evidence(candidate.scores, bass_notes);
	add_chord_key_evidence(candidate.scores, global_chord, 1.35f);
	add_chord_key_evidence(candidate.scores, keyboard_chord, 1.05f);
	add_chord_key_evidence(candidate.scores, guitar_chord, 1.05f);
	add_chord_key_evidence(candidate.scores, other_chord, 0.80f);

	float structural_total = 0.0f;
	for (float score : candidate.scores)
		structural_total += score;

	if (spectral.pitch_class >= 0 && spectral.total > 1.0e-6f) {
		const float spectral_weight = structural_total > 1.0e-6f ? 0.22f : 1.0f;
		for (int i = 0; i < 12; ++i)
			candidate.scores[i] += spectral.scores[i] / spectral.total * spectral.confidence *
					       spectral_weight;
	}

	float best_score = 0.0f;
	for (int i = 0; i < 12; ++i) {
		const float score = candidate.scores[i];
		candidate.total += score;
		if (score > best_score) {
			candidate.pitch_class = i;
			best_score = score;
		}
	}

	if (candidate.total <= 1.0e-6f || candidate.pitch_class < 0)
		return candidate;

	candidate.confidence = std::clamp(best_score / candidate.total * 2.25f, 0.0f, 1.0f);
	if (candidate.confidence < 0.24f)
		candidate.pitch_class = -1;
	return candidate;
}

float sum_notes(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi)
{
	float sum = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi)
		sum += std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
	return sum;
}

float note_visual_loudness(float rms)
{
	return std::clamp((rms - kNoteRmsFloor) / (kFullNoteRms - kNoteRmsFloor), 0.0f, 1.0f);
}

void set_instrument_note(InstrumentState &state, const RangeResult &note, float energy, float rms)
{
	if (rms < kNoteRmsFloor || energy < 1.0e-5f || note.confidence < 0.08f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	write_note(state.label, sizeof(state.label), note.midi);
	state.confidence = std::clamp(note.confidence * 1.8f * note_visual_loudness(rms), 0.0f, 1.0f);
}

void clear_note_grid(NoteGrid &grid)
{
	for (NoteCell &cell : grid.cells)
		cell = {};
	for (auto &row : grid.rows) {
		for (NoteCell &cell : row)
			cell = {};
	}
}

void clear_instrument_note_grid(NoteGrid &grid, InstrumentState &state)
{
	clear_note_grid(grid);
	copy_text(state.label, sizeof(state.label), "--");
	state.confidence = 0.0f;
}

void clear_instrument_state(InstrumentState &state)
{
	copy_text(state.label, sizeof(state.label), "--");
	state.confidence = 0.0f;
}

void write_note_grid_cell(NoteGrid &grid, const NoteCandidate &candidate, float strongest_score, float visual_loudness)
{
	const int pitch_class = ((candidate.midi % 12) + 12) % 12;
	NoteCell cell;
	write_octave(cell.label, sizeof(cell.label), candidate.midi);
	cell.level = strongest_score > 1.0e-6f ?
			     std::clamp(candidate.score / strongest_score * visual_loudness, 0.0f, 1.0f) :
			     0.0f;
	cell.midi = candidate.midi;
	cell.active = true;

	for (auto &row : grid.rows) {
		if (row[pitch_class].active)
			continue;
		row[pitch_class] = cell;
		break;
	}

	if (!grid.cells[pitch_class].active || cell.level > grid.cells[pitch_class].level)
		grid.cells[pitch_class] = cell;
}

void write_note_grid_label(InstrumentState &state, const NoteGrid &grid, int preferred_root)
{
	char label[64] = {};
	const int start = preferred_root >= 0 ? preferred_root % 12 : 0;
	for (int offset = 0; offset < 12; ++offset) {
		const int pitch_class = (start + offset) % 12;
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (!cell.active || cell.midi < 0)
				continue;

			char note[8] = {};
			write_note(note, sizeof(note), cell.midi);
			const std::size_t used = std::strlen(label);
			const std::size_t needed = std::strlen(note) + (used > 0 ? 1 : 0);
			if (used + needed + 1 > sizeof(label))
				goto done;

			std::size_t cursor = used;
			if (cursor > 0)
				label[cursor++] = ' ';
			for (const char *p = note; *p && cursor + 1 < sizeof(label); ++p)
				label[cursor++] = *p;
			label[cursor] = '\0';
		}
	}

done:
	if (!label[0]) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	copy_text(state.label, sizeof(state.label), label);
	float confidence = 0.0f;
	for (const NoteCell &cell : grid.cells)
		confidence = std::max(confidence, cell.level);
	state.confidence = confidence;
}

int lowest_candidate_pitch_class(const NoteCandidateList &candidates)
{
	int lowest_midi = kLastMidi + 1;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi >= kFirstMidi && candidate.midi <= kLastMidi)
			lowest_midi = std::min(lowest_midi, candidate.midi);
	}
	return lowest_midi <= kLastMidi ? ((lowest_midi % 12) + 12) % 12 : -1;
}

std::array<float, 12> candidate_chroma(const NoteCandidateList &candidates)
{
	std::array<float, 12> chroma = {};
	float strongest_score = 0.0f;
	for (const NoteCandidate &candidate : candidates)
		strongest_score = std::max(strongest_score, candidate.score);
	if (strongest_score <= 1.0e-6f)
		return chroma;

	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;
		const int pitch_class = ((candidate.midi % 12) + 12) % 12;
		chroma[pitch_class] =
			std::max(chroma[pitch_class], std::clamp(candidate.score / strongest_score, 0.0f, 1.0f));
	}
	return chroma;
}

void set_instrument_note_set_from_candidates(NoteGrid &grid, InstrumentState &state,
					     const NoteCandidateList &candidates, int preferred_root,
					     float energy, float rms, int max_notes)
{
	clear_note_grid(grid);
	if (rms < kNoteRmsFloor || energy < 1.0e-5f || candidates.empty()) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	float strongest_score = 0.0f;
	for (const NoteCandidate &candidate : candidates)
		strongest_score = std::max(strongest_score, candidate.score);
	if (strongest_score <= 1.0e-6f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	int written = 0;
	for (const NoteCandidate &candidate : candidates) {
		if (written >= std::max(1, max_notes))
			break;
		write_note_grid_cell(grid, candidate, strongest_score, note_visual_loudness(rms));
		++written;
	}
	write_note_grid_label(state, grid, preferred_root);
}

void collect_note_grid_levels(const NoteGrid &grid, std::array<float, kNoteProbeCount> &levels)
{
	levels.fill(0.0f);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < kFirstMidi || cell.midi > kLastMidi)
				continue;
			levels[cell.midi - kFirstMidi] = std::max(levels[cell.midi - kFirstMidi], cell.level);
		}
	}
}

void smooth_note_grid_envelope(NoteGrid &grid, InstrumentState &state,
			       std::array<NoteTrackingState, kNoteProbeCount> &tracking,
			       int preferred_root, float interval_seconds, int max_notes,
			       const std::array<bool, kNoteProbeCount> *new_note_midi_filter = nullptr,
			       int attack_confirm_frames = kNoteAttackConfirmFrames,
			       float immediate_confirm_floor = kNoteEnvelopeImmediateConfirmFloor,
			       float release_seconds = kNoteEnvelopeReleaseSeconds,
			       float visible_floor = kNoteEnvelopeVisibleFloor)
{
	std::array<float, kNoteProbeCount> raw_levels = {};
	collect_note_grid_levels(grid, raw_levels);

	const float release_step =
		std::clamp(interval_seconds, 0.01f, 1.0f) / std::max(release_seconds, 0.01f);
	for (std::size_t i = 0; i < tracking.size(); ++i) {
		NoteTrackingState &note = tracking[i];
		float raw_level = std::clamp(raw_levels[i], 0.0f, 1.0f);
		if (!note.confirmed && raw_level > 0.0f && new_note_midi_filter &&
		    !(*new_note_midi_filter)[i])
			raw_level = 0.0f;
		if (!note.confirmed && raw_level > 0.0f && raw_level < kNoteEnvelopeNewNoteFloor)
			raw_level = 0.0f;

		if (raw_level > 0.0f) {
			note.consecutive_hits = std::min(note.consecutive_hits + 1, 1000);
			note.consecutive_misses = 0;
			if (!note.confirmed &&
			    (note.consecutive_hits >= std::max(1, attack_confirm_frames) ||
			     raw_level >= immediate_confirm_floor))
				note.confirmed = true;
		} else {
			note.consecutive_hits = 0;
			note.consecutive_misses = std::min(note.consecutive_misses + 1, 1000);
		}

		if (!note.confirmed) {
			note.envelope = 0.0f;
			continue;
		}

		const float level = raw_level >= note.envelope ?
					    raw_level :
					    std::max(raw_level, note.envelope - release_step);
		note.envelope = std::clamp(level, 0.0f, 1.0f);
		if (note.envelope < visible_floor) {
			note = {};
		}
	}

	clear_note_grid(grid);
	NoteCandidateList candidates;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const float level = tracking[midi - kFirstMidi].envelope;
		if (level > 0.0f)
			candidates.push_back(NoteCandidate{midi, level});
	}
	std::sort(candidates.begin(), candidates.end(),
		  [](const NoteCandidate &a, const NoteCandidate &b) { return a.score > b.score; });

	int written = 0;
	for (const NoteCandidate &candidate : candidates) {
		write_note_grid_cell(grid, candidate, 1.0f, 1.0f);
		if (++written >= std::max(1, max_notes))
			break;
	}

	write_note_grid_label(state, grid, preferred_root);
}

void update_note_tracking_from_levels(std::array<NoteTrackingState, kNoteProbeCount> &tracking,
				      const std::array<float, kNoteProbeCount> &raw_levels,
				      float interval_seconds,
				      int attack_confirm_frames = kNoteAttackConfirmFrames,
				      float immediate_confirm_floor = kNoteEnvelopeImmediateConfirmFloor,
				      float release_seconds = kNoteEnvelopeReleaseSeconds,
				      float visible_floor = kNoteEnvelopeVisibleFloor)
{
	const float release_step =
		std::clamp(interval_seconds, 0.01f, 1.0f) / std::max(release_seconds, 0.01f);
	for (std::size_t i = 0; i < tracking.size(); ++i) {
		NoteTrackingState &note = tracking[i];
		const float raw_level = std::clamp(raw_levels[i], 0.0f, 1.0f);

		if (raw_level > 0.0f) {
			note.consecutive_hits = std::min(note.consecutive_hits + 1, 1000);
			note.consecutive_misses = 0;
			if (!note.confirmed &&
			    (note.consecutive_hits >= std::max(1, attack_confirm_frames) ||
			     raw_level >= immediate_confirm_floor))
				note.confirmed = true;
		} else {
			note.consecutive_hits = 0;
			note.consecutive_misses = std::min(note.consecutive_misses + 1, 1000);
		}

		if (!note.confirmed) {
			note.envelope = 0.0f;
			continue;
		}

		const float level = raw_level >= note.envelope ?
					    raw_level :
					    std::max(raw_level, note.envelope - release_step);
		note.envelope = std::clamp(level, 0.0f, 1.0f);
		if (note.envelope < visible_floor)
			note = {};
	}
}

std::array<float, 12> tracked_note_chroma(const std::array<NoteTrackingState, kNoteProbeCount> &tracking)
{
	std::array<float, 12> chroma = {};
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const NoteTrackingState &note = tracking[midi - kFirstMidi];
		if (!note.confirmed || note.envelope <= 0.0f)
			continue;
		const int pitch_class = ((midi % 12) + 12) % 12;
		chroma[pitch_class] = std::max(chroma[pitch_class], note.envelope);
	}
	return chroma;
}

void reset_note_grid_envelope(NoteGrid &grid, InstrumentState &state,
			      std::array<NoteTrackingState, kNoteProbeCount> &tracking)
{
	for (NoteTrackingState &note : tracking)
		note = {};
	clear_instrument_note_grid(grid, state);
}

std::array<float, 12> note_grid_chroma(const NoteGrid &grid)
{
	std::array<float, 12> chroma = {};
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0)
				continue;
			const int pitch_class = ((cell.midi % 12) + 12) % 12;
			chroma[pitch_class] = std::max(chroma[pitch_class], cell.level);
		}
	}
	return chroma;
}

int lowest_note_grid_pitch_class(const NoteGrid &grid)
{
	int lowest_midi = kLastMidi + 1;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active && cell.midi >= kFirstMidi && cell.midi < lowest_midi)
				lowest_midi = cell.midi;
		}
	}
	return lowest_midi <= kLastMidi ? ((lowest_midi % 12) + 12) % 12 : -1;
}

NoteCandidateList note_grid_candidates(const NoteGrid &grid)
{
	NoteCandidateList candidates;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < kFirstMidi || cell.midi > kLastMidi)
				continue;
			candidates.push_back(NoteCandidate{cell.midi, cell.level});
		}
	}
	std::sort(candidates.begin(), candidates.end(), [](const NoteCandidate &a, const NoteCandidate &b) {
		if (a.midi != b.midi)
			return a.midi < b.midi;
		return a.score > b.score;
	});
	std::size_t write = 0;
	for (std::size_t read = 0; read < candidates.size(); ++read) {
		if (write > 0 && candidates[read].midi == candidates[write - 1].midi)
			continue;
		candidates[write++] = candidates[read];
	}
	candidates.count = write;
	return candidates;
}

void prune_note_grid_to_chord_tones(NoteGrid &grid, InstrumentState &state, const ChordResult &chord,
				    int max_notes, int preferred_root)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	int tone_count = 0;
	for (bool tone : chord.tones) {
		if (tone)
			++tone_count;
	}
	if (tone_count < 2)
		return;

	int active_tone_pitch_classes = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!chord.tones[pitch_class])
			continue;
		bool active = grid.cells[pitch_class].active;
		for (const auto &row : grid.rows)
			active = active || row[pitch_class].active;
		if (active)
			++active_tone_pitch_classes;
	}
	if (active_tone_pitch_classes < 3)
		return;

	NoteCandidateList candidates;
	for (const NoteCandidate &candidate : note_grid_candidates(grid)) {
		const int pitch_class = ((candidate.midi % 12) + 12) % 12;
		if (chord.tones[pitch_class])
			candidates.push_back(candidate);
	}
	if (candidates.empty())
		return;

	std::sort(candidates.begin(), candidates.end(), [](const NoteCandidate &a, const NoteCandidate &b) {
		if (a.score != b.score)
			return a.score > b.score;
		return a.midi < b.midi;
	});

	clear_note_grid(grid);
	int written = 0;
	for (const NoteCandidate &candidate : candidates) {
		write_note_grid_cell(grid, candidate, 1.0f, 1.0f);
		if (++written >= std::max(1, max_notes))
			break;
	}
	write_note_grid_label(state, grid, preferred_root);
}

NoteCandidateList prune_adjacent_keyboard_candidates(const NoteCandidateList &notes)
{
	NoteCandidateList pruned;
	for (std::size_t i = 0; i < notes.size(); ++i) {
		bool weaker_neighbor = false;
		for (std::size_t j = 0; j < notes.size(); ++j) {
			if (i == j || std::abs(notes[i].midi - notes[j].midi) > 1)
				continue;
			if (notes[j].score > notes[i].score * 1.18f) {
				weaker_neighbor = true;
				break;
			}
		}
		if (!weaker_neighbor)
			pruned.push_back(notes[i]);
	}
	return pruned;
}

int longest_chromatic_run(const std::array<float, 12> &chroma)
{
	int longest = 0;
	int run = 0;
	for (int i = 0; i < 24; ++i) {
		if (chroma[i % 12] > 0.0f) {
			++run;
			longest = std::max(longest, run);
		} else {
			run = 0;
		}
	}
	return std::min(longest, 12);
}

bool chord_label_has_keyboard_ninth(const char *label)
{
	return label && (std::strstr(label, "9") || std::strstr(label, "add"));
}

ChordResult simplify_weak_keyboard_ninth(const std::array<float, 12> &chroma, const ChordResult &chord,
					 bool allow_extensions)
{
	if (chord.root < 0 || !chord_label_has_keyboard_ninth(chord.label))
		return chord;

	const int ninth = (chord.root + 2) % 12;
	float core_sum = 0.0f;
	int core_count = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!chord.tones[pitch_class] || pitch_class == ninth)
			continue;
		core_sum += chroma[pitch_class];
		++core_count;
	}

	if (core_count == 0 || chroma[ninth] >= (core_sum / static_cast<float>(core_count)) * 0.82f)
		return chord;

	std::array<float, 12> simplified_chroma = chroma;
	simplified_chroma[ninth] = 0.0f;
	const ChordResult simplified = detect_chord(simplified_chroma, chord.root, allow_extensions);
	if (simplified.root == chord.root && simplified.confidence >= 0.34f &&
	    !chord_label_has_keyboard_ninth(simplified.label))
		return simplified;

	return chord;
}

ChordResult detect_keyboard_chord_from_grid(const NoteGrid &grid, bool allow_extensions, int preferred_root = -1)
{
	static constexpr int kKeyboardHandSpanSemitones = 16;
	const NoteCandidateList notes = prune_adjacent_keyboard_candidates(note_grid_candidates(grid));
	ChordResult best;
	float best_score = 0.0f;

	for (std::size_t start = 0; start < notes.size(); ++start) {
		std::size_t last = start;
		float strongest = 0.0f;
		for (; last < notes.size(); ++last) {
			if (notes[last].midi - notes[start].midi > kKeyboardHandSpanSemitones)
				break;
			strongest = std::max(strongest, notes[last].score);
		}

		if (strongest <= 1.0e-6f)
			continue;

		std::array<float, 12> chroma = {};
		float level_sum = 0.0f;
		int distinct_pitch_classes = 0;
		const float relative_level_floor = notes[start].midi < 40 ? 0.62f : 0.50f;
		for (std::size_t i = start; i < last; ++i) {
			if (notes[i].score < strongest * relative_level_floor)
				continue;

			const int pitch_class = ((notes[i].midi % 12) + 12) % 12;
			if (chroma[pitch_class] <= 0.0f)
				++distinct_pitch_classes;
			chroma[pitch_class] = std::max(chroma[pitch_class], notes[i].score);
			level_sum += notes[i].score;
		}

		if (distinct_pitch_classes < 2)
			continue;
		if (longest_chromatic_run(chroma) >= 4)
			continue;

		const int cluster_root = preferred_root >= 0 && chroma[preferred_root % 12] > 0.0f ?
						 preferred_root :
						 ((notes[start].midi % 12) + 12) % 12;
		const ChordResult chord =
			simplify_weak_keyboard_ninth(chroma, detect_chord(chroma, cluster_root, allow_extensions),
						    allow_extensions);
		if (chord.root < 0)
			continue;
		bool lower_conflict = false;
		for (std::size_t i = 0; i < start; ++i) {
			if (notes[start].midi - notes[i].midi > kKeyboardHandSpanSemitones)
				continue;
			if (notes[i].score < strongest * 0.78f)
				continue;
			const int pitch_class = ((notes[i].midi % 12) + 12) % 12;
			if (!chord.tones[pitch_class]) {
				lower_conflict = true;
				break;
			}
		}
		if (lower_conflict)
			continue;

		const float preferred_bonus =
			preferred_root >= 0 && chord.root == preferred_root % 12 && chroma[chord.root] > 0.0f ? 0.35f :
												  0.0f;
		const float score = chord.confidence + level_sum * 0.30f +
				    static_cast<float>(distinct_pitch_classes) * 0.10f + preferred_bonus -
				    static_cast<float>(start) * 0.02f;
		if (score > best_score) {
			best_score = score;
			best = chord;
		}
	}

	if (best.root < 0)
		copy_text(best.label, sizeof(best.label), "--");
	return best;
}

ChordResult detect_caged_guitar_chord(const std::array<float, 12> &chroma, int preferred_root)
{
	ChordResult best;
	float best_score = 0.0f;
	static constexpr float kToneThreshold = 0.24f;

	auto consider = [&](int root, const char *suffix, std::initializer_list<int> intervals, float priority) {
		float score = priority;
		std::array<bool, 12> tones = {};
		for (int interval : intervals) {
			const int pitch_class = (root + interval) % 12;
			const float value = chroma[pitch_class];
			if (value < kToneThreshold)
				return;
			tones[pitch_class] = true;
			score += value;
		}

		if (root == preferred_root)
			score += 0.60f;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			if (!tones[pitch_class])
				score -= chroma[pitch_class] * 0.08f;
		}

		if (score <= best_score)
			return;

		best_score = score;
		best.root = root;
		best.tones = tones;
		best.confidence = std::clamp(score / 4.2f, 0.0f, 1.0f);
		std::snprintf(best.label, sizeof(best.label), "%s%s", note_name(root), suffix);
	};

	for (int root = 0; root < 12; ++root) {
		consider(root, "", {0, 4, 7}, 0.16f);
		consider(root, "m", {0, 3, 7}, 0.16f);
		consider(root, "sus2", {0, 2, 7}, 0.12f);
		consider(root, "sus4", {0, 5, 7}, 0.12f);
		consider(root, "pow", {0, 7}, 0.04f);
	}

	if (best.root < 0)
		copy_text(best.label, sizeof(best.label), "--");
	return best;
}

bool chord_label_has_guitar_extension_or_alteration(const char *label)
{
	if (!label)
		return false;
	return std::strstr(label, "7") || std::strstr(label, "9") || std::strstr(label, "6") ||
	       std::strstr(label, "add") || std::strstr(label, "aug") || std::strstr(label, "dim");
}

ChordResult detect_guitar_chord_from_grid(const NoteGrid &grid, bool allow_extensions)
{
	const std::array<float, 12> chroma = note_grid_chroma(grid);
	const int preferred_root = lowest_note_grid_pitch_class(grid);
	ChordResult chord = detect_chord(chroma, preferred_root, allow_extensions);
	const ChordResult caged = detect_caged_guitar_chord(chroma, preferred_root);

	if (caged.root < 0)
		return chord;
	if (chord.root < 0)
		return caged;

	int caged_tone_cells = 0;
	int non_caged_chord_tone_cells = 0;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0)
				continue;
			const int pitch_class = ((cell.midi % 12) + 12) % 12;
			if (caged.tones[pitch_class])
				++caged_tone_cells;
			else if (chord.tones[pitch_class])
				++non_caged_chord_tone_cells;
		}
	}

	bool weak_guitar_tone = false;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (chord.tones[pitch_class] && chroma[pitch_class] < 0.55f) {
			weak_guitar_tone = true;
			break;
		}
	}

	if (chord_label_has_guitar_extension_or_alteration(chord.label) && caged.confidence >= 0.58f &&
	    weak_guitar_tone)
		return caged;
	if (chord_label_has_guitar_extension_or_alteration(chord.label) && caged.confidence >= 0.50f &&
	    caged_tone_cells >= 4 && non_caged_chord_tone_cells <= 2)
		return caged;

	return chord;
}

void set_single_note_grid(NoteGrid &grid, InstrumentState &state, const RangeResult &note, float energy, float rms)
{
	clear_note_grid(grid);
	set_instrument_note(state, note, energy, rms);
	if (state.label[0] == '-' || note.midi < 0)
		return;

	const int pitch_class = ((note.midi % 12) + 12) % 12;
	NoteCell &cell = grid.cells[pitch_class];
	write_octave(cell.label, sizeof(cell.label), note.midi);
	cell.level = state.confidence;
	cell.midi = note.midi;
	cell.active = true;
	grid.rows[0][pitch_class] = cell;
}

void set_instrument_note_set(NoteGrid &grid, InstrumentState &state, const std::array<float, kNoteProbeCount> &powers,
			     int min_midi, int max_midi, int preferred_root, float energy, float rms, int max_notes,
			     const std::array<bool, 12> *blocked_pitch_classes = nullptr,
			     const std::array<bool, 12> *allowed_pitch_classes = nullptr,
			     bool suppress_adjacent_neighbors = false,
			     const std::array<bool, kNoteProbeCount> *allowed_midis = nullptr,
			     float relative_floor = kNoteRelativeFloor)
{
	clear_note_grid(grid);
	if (rms < kNoteRmsFloor || energy < 1.0e-5f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	float strongest_score = 0.0f;
	const NoteCandidateList candidates =
		note_peak_candidates(powers, min_midi, max_midi, max_notes, blocked_pitch_classes,
				     allowed_pitch_classes, suppress_adjacent_neighbors, allowed_midis,
				     relative_floor);
	for (const NoteCandidate &candidate : candidates)
		strongest_score = std::max(strongest_score, candidate.score);

	if (strongest_score <= 1.0e-6f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	for (const NoteCandidate &candidate : candidates)
		write_note_grid_cell(grid, candidate, strongest_score, note_visual_loudness(rms));

	write_note_grid_label(state, grid, preferred_root);
}

void set_instrument_chord(InstrumentState &state, const ChordResult &chord, float energy, float rms)
{
	if (rms < kNoteRmsFloor || energy < 1.0e-5f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	if (chord.confidence >= 0.36f && !chord.uncertain) {
		copy_text(state.label, sizeof(state.label), chord.label);
		state.confidence = chord.confidence;
		return;
	}

	copy_text(state.label, sizeof(state.label), "--");
	state.confidence = 0.0f;
}

bool valid_chord_result(const ChordResult &chord)
{
	return chord.root >= 0 && chord.confidence >= kChordConfidenceFloor && !chord.uncertain &&
	       chord.label[0] && chord.label[0] != '-';
}

std::array<float, 12> strongest_chord_chroma(const std::array<float, 12> &chroma)
{
	std::array<float, 12> pruned = {};
	const float strongest = *std::max_element(chroma.begin(), chroma.end());
	if (strongest <= 1.0e-6f)
		return pruned;

	std::array<int, 12> order = {};
	for (int i = 0; i < 12; ++i)
		order[i] = i;
	std::sort(order.begin(), order.end(), [&](int a, int b) {
		if (chroma[a] != chroma[b])
			return chroma[a] > chroma[b];
		return a < b;
	});

	int kept = 0;
	for (int pitch_class : order) {
		if (chroma[pitch_class] < strongest * 0.30f)
			break;
		pruned[pitch_class] = chroma[pitch_class] / strongest;
		if (++kept >= 5)
			break;
	}

	return pruned;
}

ChordResult stronger_chord(const ChordResult &lhs, const ChordResult &rhs)
{
	if (!valid_chord_result(lhs))
		return rhs;
	if (!valid_chord_result(rhs))
		return lhs;
	if (rhs.confidence != lhs.confidence)
		return rhs.confidence > lhs.confidence ? rhs : lhs;
	return rhs.margin > lhs.margin ? rhs : lhs;
}

ChordResult detect_mixed_chord_from_grid(const NoteGrid &grid, int preferred_root, bool allow_extensions)
{
	const std::array<float, 12> chroma = note_grid_chroma(grid);
	const std::array<float, 12> pruned = strongest_chord_chroma(chroma);
	ChordResult best = detect_chord(chroma, preferred_root, allow_extensions);
	best = stronger_chord(best, detect_chord(chroma, -1, allow_extensions));
	best = stronger_chord(best, detect_chord(pruned, preferred_root, allow_extensions));
	best = stronger_chord(best, detect_chord(pruned, -1, allow_extensions));
	return best;
}

ChordResult choose_chord_candidate(const ChordResult &raw, const ChordResult &smoothed)
{
	if (valid_chord_result(raw) && (!valid_chord_result(smoothed) || raw.confidence >= smoothed.confidence * 0.96f))
		return raw;
	if (valid_chord_result(smoothed))
		return smoothed;
	ChordResult empty;
	copy_text(empty.label, sizeof(empty.label), "--");
	return empty;
}

void reset_chord_tracking(ChordTrackingState &tracking, InstrumentState &state)
{
	tracking = {};
	clear_instrument_state(state);
}

void write_tracked_chord(InstrumentState &state, const ChordTrackingState &tracking)
{
	if (!tracking.displayed_label[0] || tracking.displayed_label[0] == '-') {
		clear_instrument_state(state);
		return;
	}
	copy_text(state.label, sizeof(state.label), tracking.displayed_label);
	state.confidence = tracking.displayed_confidence;
}

void stabilize_chord(InstrumentState &state, ChordTrackingState &tracking, const ChordResult &raw,
		     const ChordResult &smoothed, bool enabled, float interval_seconds,
		     bool allow_smoothed_initial = true, bool prefer_displayed_smoothed = false)
{
	if (!enabled) {
		reset_chord_tracking(tracking, state);
		return;
	}

	ChordResult candidate = choose_chord_candidate(raw, smoothed);
	const bool has_displayed = tracking.displayed_label[0] && tracking.displayed_label[0] != '-';
	if (prefer_displayed_smoothed && has_displayed && valid_chord_result(smoothed) &&
	    std::strcmp(tracking.displayed_label, smoothed.label) == 0 &&
	    (!valid_chord_result(raw) || std::strcmp(raw.label, smoothed.label) != 0))
		candidate = smoothed;
	if (!allow_smoothed_initial && !valid_chord_result(raw) && valid_chord_result(smoothed) && !has_displayed) {
		candidate = {};
		copy_text(candidate.label, sizeof(candidate.label), "--");
	}
	if (valid_chord_result(candidate)) {
		tracking.missing_seconds = 0.0f;
		if (!has_displayed) {
			copy_text(tracking.displayed_label, sizeof(tracking.displayed_label), candidate.label);
			tracking.displayed_confidence = candidate.confidence;
			tracking.pending_label[0] = '\0';
			tracking.pending_frames = 0;
			write_tracked_chord(state, tracking);
			return;
		}

		if (std::strcmp(tracking.displayed_label, candidate.label) == 0) {
			tracking.displayed_confidence = std::max(tracking.displayed_confidence, candidate.confidence);
			tracking.pending_label[0] = '\0';
			tracking.pending_frames = 0;
			write_tracked_chord(state, tracking);
			return;
		}

		if (std::strcmp(tracking.pending_label, candidate.label) == 0) {
			tracking.pending_frames = std::min(tracking.pending_frames + 1, 1000);
			tracking.pending_confidence = std::max(tracking.pending_confidence, candidate.confidence);
		} else {
			copy_text(tracking.pending_label, sizeof(tracking.pending_label), candidate.label);
			tracking.pending_confidence = candidate.confidence;
			tracking.pending_frames = 1;
		}

		if (tracking.pending_frames >= kChordSwitchConfirmFrames) {
			copy_text(tracking.displayed_label, sizeof(tracking.displayed_label), tracking.pending_label);
			tracking.displayed_confidence = tracking.pending_confidence;
			tracking.pending_label[0] = '\0';
			tracking.pending_confidence = 0.0f;
			tracking.pending_frames = 0;
		}

		write_tracked_chord(state, tracking);
		return;
	}

	tracking.pending_label[0] = '\0';
	tracking.pending_confidence = 0.0f;
	tracking.pending_frames = 0;
	if (tracking.displayed_label[0] && tracking.displayed_label[0] != '-') {
		tracking.missing_seconds += std::clamp(interval_seconds, 0.01f, 1.0f);
		if (tracking.missing_seconds <= kChordHoldSeconds) {
			write_tracked_chord(state, tracking);
			return;
		}
	}

	reset_chord_tracking(tracking, state);
}

void append_text(char *dst, std::size_t dst_size, const char *text)
{
	if (!dst || dst_size == 0 || !text)
		return;

	std::size_t used = std::strlen(dst);
	while (*text && used + 1 < dst_size)
		dst[used++] = *text++;
	dst[used] = '\0';
}

void append_root_candidate(char *dst, std::size_t dst_size, int pitch_class, float confidence)
{
	if (!dst || dst_size == 0 || pitch_class < 0)
		return;

	if (dst[0])
		append_text(dst, dst_size, "  ");
	append_text(dst, dst_size, note_name(pitch_class));
	append_text(dst, dst_size, " ");

	char percentage[8] = {};
	std::snprintf(percentage, sizeof(percentage), "%d%%",
		      std::clamp(static_cast<int>(confidence * 100.0f + 0.5f), 0, 100));
	append_text(dst, dst_size, percentage);
}

void write_root_candidates(char *dst, std::size_t dst_size, const std::array<float, 12> &scores, float total)
{
	if (!dst || dst_size == 0)
		return;

	dst[0] = '\0';
	if (total <= 1.0e-6f) {
		copy_text(dst, dst_size, "-- 0%");
		return;
	}

	std::array<int, 12> order = {};
	for (int i = 0; i < 12; ++i)
		order[i] = i;
	std::sort(order.begin(), order.end(), [&](int a, int b) { return scores[a] > scores[b]; });

	for (int i = 0, written = 0; i < 12 && written < 3; ++i) {
		const int pitch_class = order[i];
		const float confidence = std::max(scores[pitch_class], 0.0f) / total;
		if (written > 0 && confidence < 0.10f)
			break;
		if (confidence < 0.04f)
			break;

		append_root_candidate(dst, dst_size, pitch_class, confidence);
		++written;
	}

	if (!dst[0])
		copy_text(dst, dst_size, "-- 0%");
}

} // namespace

AnalysisEngine::AnalysisEngine()
{
	for (std::size_t i = 0; i < window_.size(); ++i) {
		const float phase = 2.0f * kPi * static_cast<float>(i) / static_cast<float>(window_.size() - 1);
		window_[i] = 0.5f - 0.5f * std::cos(phase);
	}

	rebuild_plans(48000);
}

void AnalysisEngine::configure(uint32_t sample_rate)
{
	if (sample_rate == 0)
		sample_rate = 48000;
	if (sample_rate != sample_rate_) {
		rebuild_plans(sample_rate);
		reset_analysis_state();
	}
}

void AnalysisEngine::reset()
{
	reset_analysis_state();
	has_active_input_mode_ = false;
	active_source_[0] = '\0';
}

void AnalysisEngine::rebuild_plans(uint32_t sample_rate)
{
	sample_rate_ = sample_rate ? sample_rate : 48000;

	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		Probe &probe = note_probes_[midi - kFirstMidi];
		probe.midi = midi;
		probe.freq = midi_frequency(midi);
		probe.coeff = 2.0f * std::cos(2.0f * kPi * probe.freq / static_cast<float>(sample_rate_));
	}

	static constexpr float kDrumFreqs[15] = {55.0f,   70.0f,   90.0f,   120.0f,  160.0f,
						 220.0f,  300.0f,  650.0f,  1100.0f, 2200.0f,
						 3600.0f, 5600.0f, 7600.0f, 9800.0f, 12500.0f};
	for (std::size_t i = 0; i < drum_probes_.size(); ++i) {
		Probe &probe = drum_probes_[i];
		probe.freq = std::min(kDrumFreqs[i], static_cast<float>(sample_rate_) * 0.45f);
		probe.coeff = 2.0f * std::cos(2.0f * kPi * probe.freq / static_cast<float>(sample_rate_));
	}
}

void AnalysisEngine::reset_note_envelopes()
{
	for (NoteTrackingState &note : bass_note_tracking_)
		note = {};
	for (NoteTrackingState &note : guitar_note_tracking_)
		note = {};
	for (NoteTrackingState &note : keyboard_note_tracking_)
		note = {};
	for (NoteTrackingState &note : vocal_note_tracking_)
		note = {};
	for (NoteTrackingState &note : other_note_tracking_)
		note = {};
	for (NoteTrackingState &note : full_mix_note_tracking_)
		note = {};
	previous_full_mix_note_levels_.fill(0.0f);
	for (NoteTrackingState &note : guitar_chord_note_tracking_)
		note = {};
	for (NoteTrackingState &note : keyboard_chord_note_tracking_)
		note = {};
	for (NoteTrackingState &note : other_chord_note_tracking_)
		note = {};
	guitar_chord_tracking_ = {};
	keyboard_chord_tracking_ = {};
	other_chord_tracking_ = {};
	global_chord_tracking_ = {};
}

void AnalysisEngine::reset_analysis_state()
{
	reset_note_envelopes();
	reset_root_window();
	drum_average_.fill(0.0f);
	drum_level_.fill(0.0f);
	previous_rms_ = 0.0f;
	silence_seconds_ = 0.0f;
	tempo_events_.fill(0.0f);
	tempo_event_pos_ = 0;
	tempo_event_count_ = 0;
	tempo_clock_seconds_ = 0.0f;
	last_tempo_event_seconds_ = -10.0f;
	estimated_bpm_ = 0.0f;
	bpm_confidence_ = 0.0f;
}

void AnalysisEngine::update_tempo(bool transient_event, float interval_seconds, float rms)
{
	const float clamped_interval = std::clamp(interval_seconds, 0.01f, 1.0f);
	tempo_clock_seconds_ += clamped_interval;

	if (rms <= kSilenceRms) {
		estimated_bpm_ *= 0.992f;
		bpm_confidence_ *= 0.985f;
		if (bpm_confidence_ < 0.05f) {
			estimated_bpm_ = 0.0f;
			bpm_confidence_ = 0.0f;
		}
		return;
	}

	if (transient_event && tempo_clock_seconds_ - last_tempo_event_seconds_ >= 0.30f) {
		tempo_events_[tempo_event_pos_] = tempo_clock_seconds_;
		tempo_event_pos_ = (tempo_event_pos_ + 1) % tempo_events_.size();
		tempo_event_count_ = std::min<std::size_t>(tempo_event_count_ + 1, tempo_events_.size());
		last_tempo_event_seconds_ = tempo_clock_seconds_;
	}

	if (tempo_event_count_ < 3) {
		bpm_confidence_ *= 0.98f;
		return;
	}

	static constexpr std::size_t kMaxTempoCandidates = 512;
	std::array<float, kMaxTempoEvents> recent_events = {};
	std::array<float, kMaxTempoCandidates> candidates = {};
	std::array<float, kMaxTempoCandidates> weights = {};
	std::size_t candidate_count = 0;
	std::size_t recent_count = 0;

	for (std::size_t i = 0; i < tempo_event_count_; ++i) {
		const std::size_t index =
			(tempo_event_pos_ + tempo_events_.size() - tempo_event_count_ + i) % tempo_events_.size();
		const float event_time = tempo_events_[index];
		if (tempo_clock_seconds_ - event_time <= 12.0f)
			recent_events[recent_count++] = event_time;
	}

	for (std::size_t older_index = 0; older_index < recent_count; ++older_index) {
		for (std::size_t newer_index = older_index + 1; newer_index < recent_count; ++newer_index) {
			const float newer = recent_events[newer_index];
			const float older = recent_events[older_index];
			const float delta = newer - older;
			if (delta < 0.30f || delta > 4.0f)
				continue;

			for (int beat_span = 1; beat_span <= 4; ++beat_span) {
				const float bpm = 60.0f * static_cast<float>(beat_span) / delta;
				if (bpm < 70.0f || bpm > 190.0f)
					continue;
				if (candidate_count >= candidates.size())
					break;
				const float age = tempo_clock_seconds_ - newer;
				const float recency = std::max(0.15f, 1.0f - age / 12.0f);
				const float span_weight = 1.0f / std::sqrt(static_cast<float>(beat_span));
				candidates[candidate_count] = bpm;
				weights[candidate_count] = recency * span_weight;
				++candidate_count;
			}
		}
	}

	if (candidate_count < 2) {
		bpm_confidence_ *= 0.98f;
		return;
	}

	float best_cluster_weight = 0.0f;
	float best_cluster_sum = 0.0f;
	float best_cluster_weight_sum = 0.0f;
	for (std::size_t i = 0; i < candidate_count; ++i) {
		float cluster_weight = 0.0f;
		float cluster_sum = 0.0f;
		for (std::size_t j = 0; j < candidate_count; ++j) {
			if (std::abs(candidates[i] - candidates[j]) > 4.0f)
				continue;
			cluster_weight += weights[j];
			cluster_sum += candidates[j] * weights[j];
		}
		if (cluster_weight > best_cluster_weight) {
			best_cluster_weight = cluster_weight;
			best_cluster_sum = cluster_sum;
			best_cluster_weight_sum = cluster_weight;
		}
	}

	if (best_cluster_weight_sum <= 0.0f) {
		bpm_confidence_ *= 0.98f;
		return;
	}

	const float mean_bpm = best_cluster_sum / best_cluster_weight_sum;
	float variance = 0.0f;
	float variance_weight = 0.0f;
	for (std::size_t i = 0; i < candidate_count; ++i) {
		if (std::abs(candidates[i] - mean_bpm) > 4.0f)
			continue;
		const float delta = candidates[i] - mean_bpm;
		variance += delta * delta * weights[i];
		variance_weight += weights[i];
	}
	variance /= std::max(variance_weight, 1.0e-6f);
	const float stdev = std::sqrt(std::max(variance, 0.0f));
	const float count_confidence = std::clamp(best_cluster_weight / 10.0f, 0.0f, 1.0f);
	const float stability_confidence = std::clamp(1.0f - stdev / std::max(mean_bpm * 0.10f, 1.0f), 0.0f, 1.0f);
	const float target_confidence = count_confidence * stability_confidence;

	if (estimated_bpm_ <= 0.0f)
		estimated_bpm_ = mean_bpm;
	else
		estimated_bpm_ = estimated_bpm_ * 0.72f + mean_bpm * 0.28f;
	bpm_confidence_ = bpm_confidence_ * 0.70f + target_confidence * 0.30f;
}

float AnalysisEngine::goertzel_power(const float *samples, std::size_t count, float mean, const Probe &probe) const
{
	float s1 = 0.0f;
	float s2 = 0.0f;

	const std::size_t usable = std::min(count, window_.size());
	for (std::size_t i = 0; i < usable; ++i) {
		const float x = (samples[i] - mean) * window_[i];
		const float s0 = x + probe.coeff * s1 - s2;
		s2 = s1;
		s1 = s0;
	}

	return std::max(0.0f, s1 * s1 + s2 * s2 - probe.coeff * s1 * s2);
}

float AnalysisEngine::goertzel_power_at_frequency(const float *samples, std::size_t count, float mean, float freq) const
{
	Probe probe;
	probe.freq = freq;
	probe.coeff = 2.0f * std::cos(2.0f * kPi * freq / static_cast<float>(sample_rate_));
	return goertzel_power(samples, count, mean, probe);
}

bool AnalysisEngine::chromatic_tuning_match(const float *samples, std::size_t count, float mean, int midi,
					    float tolerance_cents, bool allow_ratio_rescue) const
{
	static constexpr std::array<float, 5> kProbeCents = {-18.0f, -9.0f, 0.0f, 9.0f, 18.0f};
	std::array<float, kProbeCents.size()> scores = {};
	const float center_freq = midi_frequency(midi);

	std::size_t best = 0;
	for (std::size_t i = 0; i < kProbeCents.size(); ++i) {
		const float freq = center_freq * std::pow(2.0f, kProbeCents[i] / 1200.0f);
		scores[i] = std::sqrt(std::max(goertzel_power_at_frequency(samples, count, mean, freq), 0.0f));
		if (scores[i] > scores[best])
			best = i;
	}

	const float center_score = scores[kProbeCents.size() / 2];
	const float best_score = scores[best];
	float cents = kProbeCents[best];
	if (best > 0 && best + 1 < kProbeCents.size()) {
		const float previous = scores[best - 1];
		const float current = scores[best];
		const float next = scores[best + 1];
		const float denominator = previous - 2.0f * current + next;
		if (std::abs(denominator) > 1.0e-9f) {
			const float step = kProbeCents[best] - kProbeCents[best - 1];
			cents += 0.5f * (previous - next) / denominator * step;
		}
	}

	cents = std::clamp(cents, kProbeCents.front(), kProbeCents.back());
	if (std::abs(cents) <= tolerance_cents + kChromaticTuneEstimatorSlackCents)
		return true;
	if (!allow_ratio_rescue)
		return false;
	if (std::abs(cents) <= kProbeCents.back() && best_score > 1.0e-6f &&
	    center_score >= best_score * kChromaticCenterAdjacentRatio)
		return true;

	const bool edge_peak = best == 0 || best + 1 == kProbeCents.size();
	return edge_peak && best_score > 1.0e-6f && center_score >= best_score * kChromaticCenterEdgeRatio;
}

bool AnalysisEngine::tracked_note_active(AnalysisInputMode input_mode, int midi) const
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;
	const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
	const auto active = [index](const std::array<NoteTrackingState, kNoteProbeCount> &tracking) {
		const NoteTrackingState &note = tracking[index];
		return note.confirmed && note.envelope > 0.0f;
	};
	switch (input_mode) {
	case AnalysisInputMode::IsolatedBass:
		return active(bass_note_tracking_);
	case AnalysisInputMode::IsolatedGuitar:
		return active(guitar_note_tracking_);
	case AnalysisInputMode::IsolatedKeyboard:
		return active(keyboard_note_tracking_);
	case AnalysisInputMode::IsolatedVocal:
		return active(vocal_note_tracking_);
	case AnalysisInputMode::IsolatedOther:
		return active(other_note_tracking_);
	case AnalysisInputMode::Auto:
	case AnalysisInputMode::FullMix:
	default:
		return active(full_mix_note_tracking_);
	}
}

void AnalysisEngine::reset_root_window()
{
	for (RootVote &vote : root_votes_)
		vote = {};
	root_sum_.fill(0.0f);
	root_vote_pos_ = 0;
	root_vote_count_ = 0;
	locked_root_ = -1;
}

void AnalysisEngine::add_root_vote(const RootVote &vote)
{
	if (root_vote_target_ == 0)
		return;

	if (root_vote_count_ == root_vote_target_) {
		const RootVote &old_vote = root_votes_[root_vote_pos_];
		if (old_vote.valid) {
			for (int i = 0; i < 12; ++i)
				root_sum_[i] -= old_vote.scores[i];
		}
	} else {
		++root_vote_count_;
	}

	root_votes_[root_vote_pos_] = vote;
	if (vote.valid) {
		for (int i = 0; i < 12; ++i)
			root_sum_[i] += vote.scores[i];
	}

	root_vote_pos_ = (root_vote_pos_ + 1) % root_vote_target_;
}

InstrumentState AnalysisEngine::track_root(const std::array<float, kNoteProbeCount> &powers, float rms,
					   const AnalysisSettings &settings, char *root_candidates,
					   std::size_t root_candidates_size, const NoteGrid &bass_notes,
					   const InstrumentState &global_chord,
					   const InstrumentState &keyboard_chord,
					   const InstrumentState &guitar_chord,
					   const InstrumentState &other_chord)
{
	constexpr float kMinimumRootWindowSeconds = 15.0f;
	constexpr float kSilenceResetSeconds = 2.0f;
	constexpr float kModulationLead = 1.08f;
	constexpr float kModulationMinShare = 0.18f;

	InstrumentState state;
	const float interval_seconds = std::clamp(settings.analysis_interval_seconds, 0.01f, 1.0f);
	const float requested_window_seconds = std::max(settings.root_window_seconds, kMinimumRootWindowSeconds);
	const std::size_t target_votes = std::clamp<std::size_t>(
		static_cast<std::size_t>(std::ceil(requested_window_seconds / interval_seconds)), 1, kMaxRootVotes);

	if (target_votes != root_vote_target_) {
		root_vote_target_ = target_votes;
		reset_root_window();
	}

	const RootCandidate candidate =
		detect_root_candidate_with_context(powers, rms, bass_notes, global_chord, keyboard_chord,
						   guitar_chord, other_chord);

	if (rms < kSilenceRms) {
		silence_seconds_ += interval_seconds;
		if (silence_seconds_ >= kSilenceResetSeconds)
			reset_root_window();

		float total = 0.0f;
		for (float score : root_sum_)
			total += std::max(score, 0.0f);
		write_root_candidates(root_candidates, root_candidates_size, root_sum_, total);

		if (locked_root_ >= 0) {
			copy_text(state.label, sizeof(state.label), note_name(locked_root_));
			state.confidence = 0.0f;
		} else {
			copy_text(state.label, sizeof(state.label), "--");
		}
		return state;
	}

	silence_seconds_ = 0.0f;
	if (candidate.pitch_class >= 0 && candidate.total > 1.0e-6f) {
		RootVote vote;
		vote.valid = true;
		for (int i = 0; i < 12; ++i)
			vote.scores[i] = candidate.scores[i] / candidate.total * candidate.confidence;
		add_root_vote(vote);
	}

	int best = -1;
	float best_score = 0.0f;
	float total = 0.0f;
	for (int i = 0; i < 12; ++i) {
		const float score = std::max(root_sum_[i], 0.0f);
		total += score;
		if (score > best_score) {
			best = i;
			best_score = score;
		}
	}

	write_root_candidates(root_candidates, root_candidates_size, root_sum_, total);

	if (locked_root_ < 0 && best >= 0 && total > 1.0e-6f)
		locked_root_ = best;

	if (locked_root_ >= 0 && best >= 0 && best != locked_root_) {
		const float locked_score = std::max(root_sum_[locked_root_], 0.0f);
		const float confidence = total > 1.0e-6f ? best_score / total : 0.0f;
		const bool window_ready = root_vote_count_ >= root_vote_target_;
		if (window_ready && confidence >= kModulationMinShare && best_score > locked_score * kModulationLead)
			locked_root_ = best;
	}

	if (locked_root_ >= 0) {
		const float confidence = total > 1.0e-6f ? std::max(root_sum_[locked_root_], 0.0f) / total : 0.0f;
		copy_text(state.label, sizeof(state.label), note_name(locked_root_));
		state.confidence = std::clamp(confidence * 1.8f, 0.0f, 1.0f);
	} else {
		copy_text(state.label, sizeof(state.label), "--");
	}

	return state;
}

AnalysisSnapshot AnalysisEngine::analyze(const float *samples, std::size_t count, const AnalysisSettings &settings,
					 const char *source_name, uint64_t dropped_windows)
{
	configure(settings.sample_rate);

	AnalysisSnapshot snapshot;
	const char *resolved_source_name = source_name && *source_name ? source_name : "Music";
	const AnalysisInputMode input_mode = resolve_input_mode(settings, resolved_source_name);
	if (!has_active_input_mode_ || active_input_mode_ != input_mode ||
	    std::strncmp(active_source_, resolved_source_name, sizeof(active_source_)) != 0) {
		reset_analysis_state();
		active_input_mode_ = input_mode;
		has_active_input_mode_ = true;
		copy_text(active_source_, sizeof(active_source_), resolved_source_name);
	}

	copy_text(snapshot.source, sizeof(snapshot.source), resolved_source_name);
	copy_text(snapshot.drums[Kick].label, sizeof(snapshot.drums[Kick].label), "BASS DRUM");
	copy_text(snapshot.drums[Snare].label, sizeof(snapshot.drums[Snare].label), "SNARE");
	copy_text(snapshot.drums[HiHat].label, sizeof(snapshot.drums[HiHat].label), "HIHAT");
	copy_text(snapshot.drums[Crash].label, sizeof(snapshot.drums[Crash].label), "CRASH");
	copy_text(snapshot.drums[Tom].label, sizeof(snapshot.drums[Tom].label), "TOMS");
	copy_text(snapshot.drums[Ride].label, sizeof(snapshot.drums[Ride].label), "RIDE");
	snapshot.dropped_windows = dropped_windows;

	if (!samples || count == 0) {
		reset_analysis_state();
		copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
		copy_text(snapshot.root.label, sizeof(snapshot.root.label), "--");
		copy_text(snapshot.root_candidates, sizeof(snapshot.root_candidates), "-- 0%");
		copy_text(snapshot.global_chord.label, sizeof(snapshot.global_chord.label), "--");
		copy_text(snapshot.guitar.label, sizeof(snapshot.guitar.label), "--");
		copy_text(snapshot.guitar_chord.label, sizeof(snapshot.guitar_chord.label), "--");
		copy_text(snapshot.keyboard.label, sizeof(snapshot.keyboard.label), "--");
		copy_text(snapshot.keyboard_chord.label, sizeof(snapshot.keyboard_chord.label), "--");
		copy_text(snapshot.vocal.label, sizeof(snapshot.vocal.label), "--");
		copy_text(snapshot.other.label, sizeof(snapshot.other.label), "--");
		copy_text(snapshot.other_chord.label, sizeof(snapshot.other_chord.label), "--");
		return snapshot;
	}

	const std::size_t usable = std::min(count, kAnalysisWindow);
	double sum = 0.0;
	double square_sum = 0.0;
	std::array<double, kDrumTransientSegments> segment_square_sum = {};
	std::array<std::size_t, kDrumTransientSegments> segment_counts = {};
	float peak = 0.0f;
	for (std::size_t i = 0; i < usable; ++i) {
		const float sample = std::clamp(samples[i], -4.0f, 4.0f);
		sum += sample;
		square_sum += static_cast<double>(sample) * sample;
		const std::size_t segment =
			std::min<std::size_t>(kDrumTransientSegments - 1, i * kDrumTransientSegments / usable);
		segment_square_sum[segment] += static_cast<double>(sample) * sample;
		++segment_counts[segment];
		peak = std::max(peak, std::abs(sample));
	}

	const float mean = static_cast<float>(sum / static_cast<double>(usable));
	const float rms = std::sqrt(static_cast<float>(square_sum / static_cast<double>(usable)));
	float strongest_segment_rms = 0.0f;
	for (std::size_t i = 0; i < kDrumTransientSegments; ++i) {
		if (segment_counts[i] == 0)
			continue;
		strongest_segment_rms =
			std::max(strongest_segment_rms,
				 std::sqrt(static_cast<float>(segment_square_sum[i] /
							      static_cast<double>(segment_counts[i]))));
	}
	const float drum_transient_ratio = rms > 1.0e-6f ? strongest_segment_rms / rms : 0.0f;
	const bool drum_transient = drum_transient_ratio >= kDrumTransientRatio;
	snapshot.rms = rms;
	snapshot.peak = peak;
	const bool mixed_source = input_mode == AnalysisInputMode::FullMix;

	std::array<float, kNoteProbeCount> note_powers = {};
	for (std::size_t i = 0; i < note_probes_.size(); ++i)
		note_powers[i] = goertzel_power(samples, usable, mean, note_probes_[i]);

	std::array<float, kNoteProbeCount> tuned_note_powers = note_powers;
	std::array<float, kNoteProbeCount> detection_note_powers = note_powers;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		if (midi < kChromaticTuneMinMidi)
			continue;
		const bool complex_harmonic_support = has_complex_harmonic_support(note_powers, midi);
		const bool strict_ratio_rescue_allowed = !mixed_source || complex_harmonic_support;
		if (chromatic_tuning_match(samples, usable, mean, midi, kChromaticTuneToleranceCents,
					   strict_ratio_rescue_allowed))
			continue;
		if (tracked_note_active(input_mode, midi) &&
		    chromatic_tuning_match(samples, usable, mean, midi, kChromaticActiveTuneToleranceCents, true))
			continue;
		tuned_note_powers[midi - kFirstMidi] = 0.0f;
		const float fallback_scale = complex_harmonic_support ? kComplexTuningFallbackScale : 0.0f;
		detection_note_powers[midi - kFirstMidi] = note_powers[midi - kFirstMidi] * fallback_scale;
	}

	std::array<float, 15> drum_powers = {};
	for (std::size_t i = 0; i < drum_probes_.size(); ++i)
		drum_powers[i] = std::sqrt(goertzel_power(samples, usable, mean, drum_probes_[i]));

	std::array<float, 15> drum_segment_peaks = {};
	for (std::size_t segment = 0; segment < kDrumTransientSegments; ++segment) {
		const std::size_t start = segment * usable / kDrumTransientSegments;
		const std::size_t end = (segment + 1) * usable / kDrumTransientSegments;
		const std::size_t segment_count = end > start ? end - start : 0;
		if (segment_count == 0)
			continue;

		double segment_sum = 0.0;
		for (std::size_t i = start; i < end; ++i)
			segment_sum += std::clamp(samples[i], -4.0f, 4.0f);
		const float segment_mean = static_cast<float>(segment_sum / static_cast<double>(segment_count));
		const float segment_scale = static_cast<float>(usable) / static_cast<float>(segment_count);
		for (std::size_t i = 0; i < drum_probes_.size(); ++i) {
			const float segment_power =
				std::sqrt(goertzel_power(samples + start, segment_count, segment_mean,
							 drum_probes_[i])) *
				segment_scale;
			drum_segment_peaks[i] = std::max(drum_segment_peaks[i], segment_power);
		}
	}

	const float low = sum_notes(detection_note_powers, kBassMinMidi, 47);
	const float mid = sum_notes(detection_note_powers, 48, 72);
	const float high = sum_notes(detection_note_powers, 73, kLastMidi) + drum_powers[11] + drum_powers[12] + drum_powers[13];
	const float bass_energy = sum_notes(detection_note_powers, kBassMinMidi, kBassMaxMidi);
	const float guitar_energy = sum_notes(detection_note_powers, kGuitarMinMidi, kGuitarMaxMidi);
	const float keyboard_energy = sum_notes(detection_note_powers, kKeyboardMinMidi, kKeyboardMaxMidi);
	const float vocal_energy = sum_notes(detection_note_powers, kVocalMinMidi, kVocalMaxMidi);
	const float other_energy = sum_notes(detection_note_powers, kOtherMinMidi, kOtherMaxMidi);
	const float total = low + mid + high + 1.0e-6f;
	snapshot.low_energy = low / total;
	snapshot.mid_energy = mid / total;
	snapshot.high_energy = high / total;
	const float interval_seconds = std::clamp(settings.analysis_interval_seconds, 0.01f, 1.0f);

	const bool had_previous_audio = previous_rms_ > kSilenceRms;
	const float onset = previous_rms_ > 1.0e-5f ? rms / previous_rms_ : (rms > kSilenceRms ? 2.0f : 0.0f);
	previous_rms_ = previous_rms_ * 0.78f + rms * 0.22f;

	const std::array<float, kDrumCount> drum_bands = {
		drum_powers[0] + drum_powers[1] + drum_powers[2] * 0.75f,
		drum_powers[4] + drum_powers[5] + drum_powers[8] * 0.65f + drum_powers[9] * 0.55f,
		drum_powers[11] + drum_powers[12] + drum_powers[13],
		drum_powers[12] + drum_powers[13] + drum_powers[14],
		drum_powers[2] + drum_powers[3] + drum_powers[4] + drum_powers[5] * 0.5f,
		drum_powers[10] + drum_powers[11] + drum_powers[12] * 0.75f,
	};
	const std::array<float, kDrumCount> drum_segment_bands = {
		drum_segment_peaks[0] + drum_segment_peaks[1] + drum_segment_peaks[2] * 0.75f,
		drum_segment_peaks[4] + drum_segment_peaks[5] + drum_segment_peaks[8] * 0.65f +
			drum_segment_peaks[9] * 0.55f,
		drum_segment_peaks[11] + drum_segment_peaks[12] + drum_segment_peaks[13],
		drum_segment_peaks[12] + drum_segment_peaks[13] + drum_segment_peaks[14],
		drum_segment_peaks[2] + drum_segment_peaks[3] + drum_segment_peaks[4] +
			drum_segment_peaks[5] * 0.5f,
		drum_segment_peaks[10] + drum_segment_peaks[11] + drum_segment_peaks[12] * 0.75f,
	};
	const float strongest_body_drum =
		std::max(drum_segment_bands[Kick], std::max(drum_segment_bands[Snare], drum_segment_bands[Tom]));
	const float kick_body = drum_segment_peaks[0] + drum_segment_peaks[1] + drum_segment_peaks[2] * 0.45f;
	const float snare_body =
		drum_segment_peaks[4] + drum_segment_peaks[5] + drum_segment_peaks[8] * 0.45f;
	const float tom_body = drum_segment_peaks[2] + drum_segment_peaks[3] + drum_segment_peaks[4];
	const bool kick_shape = strongest_body_drum <= 0.0f ||
				(drum_segment_bands[Kick] >= strongest_body_drum * 0.58f &&
				 kick_body >= std::max(snare_body, tom_body) * 0.50f);
	const bool snare_shape = strongest_body_drum <= 0.0f ||
				 (drum_segment_bands[Snare] >= strongest_body_drum * 0.58f &&
				  snare_body >= kick_body * 0.38f && snare_body >= tom_body * 0.46f);
	const bool tom_shape = strongest_body_drum <= 0.0f ||
			       (drum_segment_bands[Tom] >= strongest_body_drum * 0.58f &&
				tom_body >= kick_body * 0.42f && tom_body >= snare_body * 0.40f);
	const float cymbal_low = drum_segment_peaks[10] + drum_segment_peaks[11];
	const float cymbal_mid = drum_segment_peaks[11] + drum_segment_peaks[12];
	const float cymbal_high = drum_segment_peaks[13] + drum_segment_peaks[14];
	const std::array<float, 3> body_shape_scores = {
		kick_body * (1.0f + snapshot.low_energy * 0.90f),
		snare_body * (1.0f + snapshot.mid_energy * 0.45f),
		tom_body,
	};
	std::size_t body_shape = Kick;
	if (body_shape_scores[1] > body_shape_scores[0] && body_shape_scores[1] >= body_shape_scores[2])
		body_shape = Snare;
	else if (body_shape_scores[2] > body_shape_scores[0] && body_shape_scores[2] > body_shape_scores[1])
		body_shape = Tom;
	const float strongest_cymbal_drum =
		std::max(drum_segment_bands[HiHat], std::max(drum_segment_bands[Crash], drum_segment_bands[Ride]));
	std::size_t cymbal_shape = HiHat;
	if (drum_segment_peaks[14] > (drum_segment_peaks[12] + drum_segment_peaks[13]) * 0.65f)
		cymbal_shape = Crash;
	else if (cymbal_low > cymbal_mid * 1.15f && cymbal_low > cymbal_high * 1.15f)
		cymbal_shape = Ride;
	const bool cymbal_shape_allowed =
		strongest_cymbal_drum > 0.0f &&
		(snapshot.high_energy >= 0.03f || strongest_cymbal_drum >= strongest_body_drum * 0.10f);
	const bool body_shape_allowed =
		strongest_body_drum > 0.0f &&
		(!cymbal_shape_allowed || snapshot.high_energy < 0.62f ||
		 strongest_body_drum >= strongest_cymbal_drum * 0.45f);
	const std::array<bool, kDrumCount> drum_shape_supported = {
		body_shape_allowed && body_shape == Kick && kick_shape,
		body_shape_allowed && body_shape == Snare && snare_shape,
		cymbal_shape_allowed && cymbal_shape == HiHat,
		cymbal_shape_allowed && cymbal_shape == Crash,
		body_shape_allowed && body_shape == Tom && tom_shape,
		cymbal_shape_allowed && cymbal_shape == Ride,
	};

	const float sensitivity = std::clamp(settings.sensitivity, 0.25f, 4.0f);
	const float trigger_threshold = 1.42f / sensitivity;
	bool tempo_event = false;
	for (std::size_t i = 0; i < kDrumCount; ++i) {
		if (drum_average_[i] <= 0.0f)
			drum_average_[i] = drum_bands[i];

		const float band_ratio = drum_bands[i] / (drum_average_[i] + 1.0e-6f);
		const float segment_ratio = drum_segment_bands[i] / (drum_average_[i] + 1.0e-6f);
		const bool cymbal = i == HiHat || i == Crash || i == Ride;
		const bool kick = i == Kick;
		const bool snare = i == Snare;
		const bool tom = i == Tom;
		const float kick_click_peak =
			drum_segment_peaks[7] + drum_segment_peaks[8] * 0.70f + drum_segment_peaks[9] * 0.45f;
		const float kick_competing_body =
			std::max(drum_segment_bands[Snare], drum_segment_bands[Tom]);
		const bool kick_low_body_transient =
			kick && drum_transient && snapshot.low_energy >= 0.62f &&
			drum_segment_bands[Kick] >= kick_competing_body * 0.90f;
		const bool kick_click_transient =
			!kick || kick_click_peak >= drum_segment_bands[Kick] * 0.09f ||
			kick_low_body_transient;
		const bool segment_supported =
			band_ratio >= 1.03f ||
			(kick && kick_click_transient && snapshot.low_energy >= 0.15f);
		const float transient_ratio = segment_supported ? std::max(band_ratio, segment_ratio) : band_ratio;
		float score = transient_ratio * 0.72f + onset * 0.28f;
		if (i == Kick)
			score *= 1.0f + snapshot.low_energy * 0.8f;
		if (i == HiHat || i == Crash || i == Ride)
			score *= 1.0f + snapshot.high_energy * 0.55f;
		if (i == Snare)
			score *= 1.0f + snapshot.mid_energy * 0.45f;

		const bool cymbal_family_evidence =
			strongest_cymbal_drum >= strongest_body_drum * 0.10f || snapshot.high_energy >= 0.03f;
		const bool soft_cymbal_transient =
			had_previous_audio && cymbal && cymbal_family_evidence && transient_ratio >= 0.65f;
		const bool soft_kick_transient =
			had_previous_audio && kick && kick_click_transient && transient_ratio >= 1.00f;
		const bool soft_snare_transient = had_previous_audio && snare && transient_ratio >= 1.10f;
		const bool soft_tom_transient = had_previous_audio && tom && transient_ratio >= 1.18f;
		const bool soft_body_transient = soft_kick_transient || soft_snare_transient || soft_tom_transient;
		const bool shape_supported = drum_shape_supported[i];
		const bool quiet_cymbal_shape =
			had_previous_audio && cymbal && shape_supported && cymbal_family_evidence &&
			strongest_cymbal_drum >= strongest_body_drum * 0.10f;
		const float threshold_scale = (soft_cymbal_transient || quiet_cymbal_shape) ? 0.26f :
					      soft_kick_transient ? 0.25f :
					      soft_snare_transient ? 0.48f :
					      soft_tom_transient ? 0.60f :
								     1.0f;
		const float effective_threshold = trigger_threshold * threshold_scale;
		if (rms > kSilenceRms && shape_supported && (!kick || kick_click_transient) &&
		    (drum_transient || soft_cymbal_transient || quiet_cymbal_shape || soft_body_transient) &&
		    score > effective_threshold) {
			const float level = std::clamp((score - effective_threshold) * 0.85f, 0.35f, 1.0f);
			drum_level_[i] = std::max(drum_level_[i], level);
			tempo_event = true;
		} else {
			drum_level_[i] *= 0.72f;
		}

		drum_average_[i] = drum_average_[i] * 0.92f + drum_bands[i] * 0.08f;
		snapshot.drums[i].level = drum_level_[i];
		snapshot.drums[i].active = drum_level_[i] > 0.30f;
	}
	const bool onset_tempo_event =
		rms > kSilenceRms && drum_transient && (had_previous_audio ? onset >= 1.25f : true);
	update_tempo(tempo_event || onset_tempo_event, interval_seconds, rms);
	snapshot.estimated_bpm = estimated_bpm_;
	snapshot.bpm_confidence = bpm_confidence_;

	int mixed_bass_pitch_class = -1;
	ChordResult raw_keyboard_chord;
	ChordResult raw_guitar_chord;
	ChordResult raw_other_chord;
	ChordResult raw_global_chord;
	ChordResult smoothed_global_chord;
	FullMixOwnership full_mix_ownership;
	const bool monophonic_other_source =
		input_mode == AnalysisInputMode::IsolatedOther && is_monophonic_other_track_source(resolved_source_name);
	const int other_max_notes = monophonic_other_source ? 1 : (mixed_source ? 12 : 8);
	if (mixed_source) {
		std::array<float, kNoteProbeCount> current_full_mix_note_levels = {};
		full_mix_ownership = build_full_mix_ownership(note_powers, detection_note_powers, rms,
							      previous_full_mix_note_levels_,
							      current_full_mix_note_levels);
		previous_full_mix_note_levels_ = current_full_mix_note_levels;
		update_note_tracking_from_levels(full_mix_note_tracking_, full_mix_ownership.global_note_levels,
						 interval_seconds, kNoteAttackConfirmFrames,
						 kMixedNoteEnvelopeImmediateConfirmFloor,
						 kAnalyticalChordNoteReleaseSeconds,
						 kAnalyticalChordNoteVisibleFloor);
		set_note_grid_from_candidates(snapshot.ambiguous_notes, full_mix_ownership.ambiguous_candidates, rms, 12);
	} else {
		clear_note_grid(snapshot.ambiguous_notes);
	}

	if (input_mode == AnalysisInputMode::FullMix || input_mode == AnalysisInputMode::IsolatedBass) {
		const bool isolated_bass = input_mode == AnalysisInputMode::IsolatedBass;
		const int bass_max_midi = isolated_bass ? kBassMaxMidi : kDefaultBassMaxMidi;
		const bool include_bass_harmonics = true;
		const RangeResult bass_note =
			dominant_bass_note(detection_note_powers, kBassMinMidi, bass_max_midi,
					   include_bass_harmonics);
		const RangeResult broad_bass_note = isolated_bass ?
							    bass_note :
							    dominant_bass_note(detection_note_powers, kBassMinMidi,
									       kBassMaxMidi, include_bass_harmonics);
		const bool mixed_bass_supported =
			isolated_bass || full_mix_bass_supported(detection_note_powers, bass_note, broad_bass_note);
		if (mixed_bass_supported) {
			set_single_note_grid(snapshot.bass_notes, snapshot.bass, bass_note, bass_energy, rms);
			if (bass_note.midi >= 0 && snapshot.bass.confidence > 0.0f)
				mixed_bass_pitch_class = ((bass_note.midi % 12) + 12) % 12;
		} else {
			clear_note_grid(snapshot.bass_notes);
			copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
			snapshot.bass.confidence = 0.0f;
		}
	} else {
		clear_note_grid(snapshot.bass_notes);
		copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
		snapshot.bass.confidence = 0.0f;
	}

	if (mixed_source) {
		const bool strong_bass_hint = mixed_bass_pitch_class >= 0 && snapshot.bass.confidence >= 0.32f;
		if (strong_bass_hint && full_mix_ownership.global_chroma[mixed_bass_pitch_class] < 0.20f)
			full_mix_ownership.global_chroma[mixed_bass_pitch_class] =
				std::max(full_mix_ownership.global_chroma[mixed_bass_pitch_class],
					 snapshot.bass.confidence * 0.55f);
		raw_global_chord = detect_chord(full_mix_ownership.global_chroma, -1, false);
		if (strong_bass_hint) {
			const ChordResult bass_hint_chord =
				detect_chord(full_mix_ownership.global_chroma, mixed_bass_pitch_class, false);
			if (valid_chord_result(bass_hint_chord) &&
			    !valid_chord_result(raw_global_chord))
				raw_global_chord = bass_hint_chord;
		}

		const std::array<float, 12> smoothed_global_chroma = tracked_note_chroma(full_mix_note_tracking_);
		smoothed_global_chord = detect_chord(smoothed_global_chroma, -1, false);
		if (strong_bass_hint) {
			const ChordResult smoothed_bass_hint_chord =
				detect_chord(smoothed_global_chroma, mixed_bass_pitch_class, false);
			if (valid_chord_result(smoothed_bass_hint_chord) &&
			    !valid_chord_result(smoothed_global_chord))
				smoothed_global_chord = smoothed_bass_hint_chord;
		}
	}

	auto process_keyboard = [&]() {
		const bool allow_extensions = !mixed_source;
		int preferred_root = -1;
		const int max_notes = 10;
		if (mixed_source) {
			preferred_root = mixed_bass_pitch_class >= 0 ?
						 mixed_bass_pitch_class :
						 lowest_candidate_pitch_class(full_mix_ownership.keyboard_candidates);
			set_instrument_note_set_from_candidates(snapshot.keyboard_notes, snapshot.keyboard,
								full_mix_ownership.keyboard_candidates,
								preferred_root, keyboard_energy, rms, max_notes);
		} else {
			const int min_midi = kKeyboardMinMidi;
			const int max_midi = kKeyboardMaxMidi;
			const int detected_root =
				lowest_peak_pitch_class(detection_note_powers, min_midi, max_midi);
			preferred_root = detected_root;
			set_instrument_note_set(snapshot.keyboard_notes, snapshot.keyboard, detection_note_powers,
						min_midi, max_midi, preferred_root, keyboard_energy, rms,
						max_notes);
		}
		const int keyboard_chord_root_hint = mixed_source ? preferred_root : -1;
		raw_keyboard_chord = detect_keyboard_chord_from_grid(snapshot.keyboard_notes, allow_extensions,
								     keyboard_chord_root_hint);
		if (mixed_source && !valid_chord_result(raw_keyboard_chord))
			raw_keyboard_chord =
				detect_mixed_chord_from_grid(snapshot.keyboard_notes, keyboard_chord_root_hint,
							     allow_extensions);
		set_instrument_chord(snapshot.keyboard_chord, raw_keyboard_chord, keyboard_energy, rms);
	};

	auto process_guitar = [&]() {
		const int min_midi = kGuitarMinMidi;
		const bool allow_extensions = !mixed_source;
		int preferred_root = -1;
		const int max_notes = mixed_source ? 12 : 8;
		if (mixed_source) {
			preferred_root = lowest_candidate_pitch_class(full_mix_ownership.guitar_candidates);
			set_instrument_note_set_from_candidates(snapshot.guitar_notes, snapshot.guitar,
								full_mix_ownership.guitar_candidates,
								preferred_root, guitar_energy, rms, max_notes);
		} else {
			preferred_root =
				lowest_peak_pitch_class(detection_note_powers, min_midi, kGuitarMaxMidi);
			set_instrument_note_set(snapshot.guitar_notes, snapshot.guitar, detection_note_powers,
						min_midi, kGuitarMaxMidi, preferred_root, guitar_energy, rms,
						max_notes);
		}
		raw_guitar_chord = detect_guitar_chord_from_grid(snapshot.guitar_notes, allow_extensions);
		if (!mixed_source && raw_guitar_chord.root >= 0) {
			prune_note_grid_to_chord_tones(snapshot.guitar_notes, snapshot.guitar, raw_guitar_chord, 6,
						      preferred_root);
			raw_guitar_chord = detect_guitar_chord_from_grid(snapshot.guitar_notes, allow_extensions);
		}
		if (mixed_source && !valid_chord_result(raw_guitar_chord))
			raw_guitar_chord =
				detect_mixed_chord_from_grid(snapshot.guitar_notes, preferred_root, allow_extensions);
		set_instrument_chord(snapshot.guitar_chord, raw_guitar_chord, guitar_energy, rms);
	};

	auto process_vocal = [&]() {
		if (mixed_source) {
			const int preferred_root = lowest_candidate_pitch_class(full_mix_ownership.vocal_candidates);
			set_instrument_note_set_from_candidates(snapshot.vocal_notes, snapshot.vocal,
								full_mix_ownership.vocal_candidates,
								preferred_root, vocal_energy, rms, 1);
		} else {
			const int preferred_root =
				lowest_peak_pitch_class(detection_note_powers, kVocalMinMidi, kVocalMaxMidi);
			set_instrument_note_set(snapshot.vocal_notes, snapshot.vocal, detection_note_powers,
						kVocalMinMidi, kVocalMaxMidi, preferred_root, vocal_energy,
						rms, 1);
		}
	};

	auto process_other = [&]() {
		const bool allow_extensions = !mixed_source && !monophonic_other_source;
		std::array<float, 12> chroma = {};
		int preferred_root = -1;
		if (mixed_source) {
			chroma = candidate_chroma(full_mix_ownership.other_candidates);
			preferred_root = mixed_bass_pitch_class >= 0 ?
						 mixed_bass_pitch_class :
						 lowest_candidate_pitch_class(full_mix_ownership.other_candidates);
		} else {
			const int min_midi = kOtherMinMidi;
			chroma = peak_chroma_for_range(detection_note_powers, min_midi, kOtherMaxMidi,
						       nullptr, false, nullptr, kNoteRelativeFloor);
			preferred_root =
				lowest_peak_pitch_class(detection_note_powers, min_midi, kOtherMaxMidi);
		}
		raw_other_chord = monophonic_other_source ? ChordResult{} :
						     detect_chord(chroma, preferred_root, allow_extensions);
		const int note_root = raw_other_chord.root >= 0 ? raw_other_chord.root : preferred_root;
		if (mixed_source) {
			set_instrument_note_set_from_candidates(snapshot.other_notes, snapshot.other,
								full_mix_ownership.other_candidates, note_root,
								other_energy, rms, other_max_notes);
		} else {
			const int min_midi = kOtherMinMidi;
			set_instrument_note_set(snapshot.other_notes, snapshot.other, detection_note_powers,
						min_midi, kOtherMaxMidi, note_root, other_energy, rms,
						other_max_notes);
		}
		set_instrument_chord(snapshot.other_chord, raw_other_chord, other_energy, rms);
	};

	const bool keyboard_enabled = input_mode == AnalysisInputMode::FullMix ||
				      input_mode == AnalysisInputMode::IsolatedKeyboard;
	const bool guitar_enabled = input_mode == AnalysisInputMode::FullMix ||
				    input_mode == AnalysisInputMode::IsolatedGuitar;
	const bool vocal_enabled = input_mode == AnalysisInputMode::FullMix ||
				   input_mode == AnalysisInputMode::IsolatedVocal;
	const bool other_enabled = input_mode == AnalysisInputMode::FullMix ||
				   input_mode == AnalysisInputMode::IsolatedOther;

	if (keyboard_enabled) {
		process_keyboard();
	} else {
		clear_instrument_note_grid(snapshot.keyboard_notes, snapshot.keyboard);
		clear_instrument_state(snapshot.keyboard_chord);
	}

	if (guitar_enabled) {
		process_guitar();
	} else {
		clear_instrument_note_grid(snapshot.guitar_notes, snapshot.guitar);
		clear_instrument_state(snapshot.guitar_chord);
	}

	if (vocal_enabled) {
		process_vocal();
	} else {
		clear_instrument_note_grid(snapshot.vocal_notes, snapshot.vocal);
	}

	if (other_enabled) {
		process_other();
	} else {
		clear_instrument_note_grid(snapshot.other_notes, snapshot.other);
		clear_instrument_state(snapshot.other_chord);
	}

	NoteGrid keyboard_chord_grid = snapshot.keyboard_notes;
	NoteGrid guitar_chord_grid = snapshot.guitar_notes;
	NoteGrid other_chord_grid = snapshot.other_notes;
	InstrumentState keyboard_chord_note_state = {};
	InstrumentState guitar_chord_note_state = {};
	InstrumentState other_chord_note_state = {};

	const bool bass_processed = input_mode == AnalysisInputMode::FullMix ||
				    input_mode == AnalysisInputMode::IsolatedBass;
	const bool allow_smoothed_extensions = !mixed_source;
	const std::array<bool, kNoteProbeCount> *keyboard_new_notes = nullptr;
	const std::array<bool, kNoteProbeCount> *guitar_new_notes = nullptr;
	const std::array<bool, kNoteProbeCount> *other_new_notes = nullptr;

	if (bass_processed) {
		smooth_note_grid_envelope(snapshot.bass_notes, snapshot.bass, bass_note_tracking_, -1,
					  interval_seconds, 1, nullptr, 1);
	} else {
		reset_note_grid_envelope(snapshot.bass_notes, snapshot.bass, bass_note_tracking_);
	}

	if (keyboard_enabled) {
		smooth_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_tracking_, -1,
					  interval_seconds, 10, keyboard_new_notes, kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		smooth_note_grid_envelope(keyboard_chord_grid, keyboard_chord_note_state, keyboard_chord_note_tracking_,
					  -1, interval_seconds, 10, keyboard_new_notes, kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor,
					  kAnalyticalChordNoteReleaseSeconds, kAnalyticalChordNoteVisibleFloor);
		ChordResult smoothed_keyboard_chord =
			detect_keyboard_chord_from_grid(keyboard_chord_grid, allow_smoothed_extensions);
		if (mixed_source && !valid_chord_result(smoothed_keyboard_chord))
			smoothed_keyboard_chord =
				detect_mixed_chord_from_grid(keyboard_chord_grid,
							     lowest_note_grid_pitch_class(keyboard_chord_grid),
							     allow_smoothed_extensions);
		stabilize_chord(snapshot.keyboard_chord, keyboard_chord_tracking_, raw_keyboard_chord,
				smoothed_keyboard_chord, true, interval_seconds);
	} else {
		reset_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_tracking_);
		reset_note_grid_envelope(keyboard_chord_grid, keyboard_chord_note_state, keyboard_chord_note_tracking_);
		reset_chord_tracking(keyboard_chord_tracking_, snapshot.keyboard_chord);
	}

	if (guitar_enabled) {
		smooth_note_grid_envelope(snapshot.guitar_notes, snapshot.guitar, guitar_note_tracking_, -1,
					  interval_seconds, mixed_source ? 12 : 6, guitar_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		smooth_note_grid_envelope(guitar_chord_grid, guitar_chord_note_state, guitar_chord_note_tracking_,
					  -1, interval_seconds, mixed_source ? 12 : 6, guitar_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor,
					  kAnalyticalChordNoteReleaseSeconds, kAnalyticalChordNoteVisibleFloor);
		ChordResult smoothed_guitar_chord =
			detect_guitar_chord_from_grid(guitar_chord_grid, allow_smoothed_extensions);
		if (mixed_source && !valid_chord_result(smoothed_guitar_chord))
			smoothed_guitar_chord =
				detect_mixed_chord_from_grid(guitar_chord_grid,
							     lowest_note_grid_pitch_class(guitar_chord_grid),
							     allow_smoothed_extensions);
		stabilize_chord(snapshot.guitar_chord, guitar_chord_tracking_, raw_guitar_chord,
				smoothed_guitar_chord, true, interval_seconds);
	} else {
		reset_note_grid_envelope(snapshot.guitar_notes, snapshot.guitar, guitar_note_tracking_);
		reset_note_grid_envelope(guitar_chord_grid, guitar_chord_note_state, guitar_chord_note_tracking_);
		reset_chord_tracking(guitar_chord_tracking_, snapshot.guitar_chord);
	}

	if (vocal_enabled) {
		smooth_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_tracking_, -1,
					  interval_seconds, 1);
	} else {
		reset_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_tracking_);
	}

	if (other_enabled) {
		smooth_note_grid_envelope(snapshot.other_notes, snapshot.other, other_note_tracking_, -1,
					  interval_seconds, other_max_notes, other_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		smooth_note_grid_envelope(other_chord_grid, other_chord_note_state, other_chord_note_tracking_,
					  -1, interval_seconds, other_max_notes, other_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor,
					  kAnalyticalChordNoteReleaseSeconds, kAnalyticalChordNoteVisibleFloor);
		const ChordResult smoothed_other_chord =
			monophonic_other_source ?
				ChordResult{} :
				detect_chord(note_grid_chroma(other_chord_grid),
					     lowest_note_grid_pitch_class(other_chord_grid),
					     allow_smoothed_extensions);
		stabilize_chord(snapshot.other_chord, other_chord_tracking_, raw_other_chord, smoothed_other_chord,
				true, interval_seconds, false);
	} else {
		reset_note_grid_envelope(snapshot.other_notes, snapshot.other, other_note_tracking_);
		reset_note_grid_envelope(other_chord_grid, other_chord_note_state, other_chord_note_tracking_);
		reset_chord_tracking(other_chord_tracking_, snapshot.other_chord);
	}

	if (mixed_source) {
		stabilize_chord(snapshot.global_chord, global_chord_tracking_, raw_global_chord, smoothed_global_chord,
				true, interval_seconds, true, true);
	} else {
		reset_chord_tracking(global_chord_tracking_, snapshot.global_chord);
	}

	snapshot.root = track_root(detection_note_powers, rms, settings, snapshot.root_candidates,
				   sizeof(snapshot.root_candidates), snapshot.bass_notes, snapshot.global_chord,
				   snapshot.keyboard_chord, snapshot.guitar_chord, snapshot.other_chord);

	return snapshot;
}

} // namespace mao
