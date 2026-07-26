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
constexpr int kFullMixUpperBassMaxMidi = 59;
constexpr int kFullMixCleanHighSynthBassMaxMidi = 64;
constexpr int kGuitarMinMidi = 40;
constexpr int kGuitarMaxMidi = 88;
constexpr int kKeyboardMinMidi = 21;
constexpr int kKeyboardMaxMidi = 108;
constexpr int kVocalMinMidi = 40;
constexpr int kVocalMaxMidi = 84;
constexpr int kFullMixVocalMinMidi = 53;
constexpr int kOtherMinMidi = 21;
constexpr int kOtherMaxMidi = 108;
constexpr float kSilenceRms = 0.0025f;
constexpr float kNoteRmsFloor = 0.006f;
constexpr float kPolyphonicNoteRmsFloor = 0.0030f;
constexpr float kFullNoteRms = 0.035f;
constexpr float kNoteRelativeFloor = 0.36f;
constexpr float kMixedNoteRelativeFloor = 0.08f;
constexpr float kComplexTuningFallbackScale = 0.38f;
constexpr float kMixedDominantDetunedFallbackScale = 0.62f;
constexpr int kMixedDominantDetunedFallbackMinMidi = 73;
constexpr float kMixedStringSourceDetunedFallbackScale = 0.92f;
constexpr float kMixedSynthSourceDetunedFallbackScale = 0.86f;
constexpr float kIsolatedComplexTuningFallbackScale = 0.78f;
constexpr float kIsolatedDetunedFallbackScale = 0.0f;
constexpr float kIsolatedNamedInstrumentTuningFallbackScale = 0.78f;
constexpr float kIsolatedPolyphonicTuningFallbackScale = 0.78f;
constexpr float kHarmonicMaskRatio = 0.62f;
constexpr int kChromaticTuneMinMidi = kGuitarMinMidi;
constexpr float kChromaticTuneToleranceCents = 9.0f;
constexpr float kChromaticActiveTuneToleranceCents = 18.0f;
constexpr float kChromaticTuneEstimatorSlackCents = 0.0f;
constexpr float kChromaticCenterAdjacentRatio = 0.985f;
constexpr float kChromaticCenterEdgeRatio = 0.78f;
constexpr int kStrictTunedPowerPromotionMinMidi = 84;
constexpr float kHighMixedStrictTuneToleranceCents = 12.0f;
constexpr float kStrictTunedPowerPromotionFloor = 0.18f;
constexpr float kStrictTunedPowerPromotionCap = 1.10f;
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
constexpr float kChordStrongExtensionToneFloor = 0.32f;
constexpr float kChordStrongExtensionCoreRatio = 0.36f;
constexpr float kGuitarCagedPresenceFloor = 0.50f;
constexpr std::size_t kDrumTransientSegments = 8;
constexpr float kDrumTransientRatio = 1.55f;
constexpr float kMixedBassMinBroadScoreRatio = 0.22f;
constexpr float kMixedBassMinConfidence = 0.025f;
constexpr float kIsolatedBassPeriodicityFloor = 0.34f;
constexpr float kIsolatedBassPeriodicitySpectralRatio = 0.62f;
constexpr int kIsolatedBassStrongHarmonicMaxMidi = 47;
constexpr int kIsolatedBassPeriodicReplacementMaxMidi = 43;

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

AnalysisInputMode single_family_hint_from_source(const char *source_name)
{
	const bool bass_hint = contains_case_insensitive(source_name, "bass");
	const bool other_hint =
		contains_case_insensitive(source_name, "synth") || contains_case_insensitive(source_name, "brass") ||
		contains_case_insensitive(source_name, "horn") || contains_case_insensitive(source_name, "violin") ||
		contains_case_insensitive(source_name, "string") || contains_case_insensitive(source_name, "wind") ||
		contains_case_insensitive(source_name, "woodwind") || contains_case_insensitive(source_name, "other");
	const bool keyboard_hint =
		contains_case_insensitive(source_name, "key") || contains_case_insensitive(source_name, "piano") ||
		contains_case_insensitive(source_name, "organ");
	const bool guitar_hint = contains_case_insensitive(source_name, "guitar");
	const bool vocal_hint =
		contains_case_insensitive(source_name, "vocal") || contains_case_insensitive(source_name, "voice") ||
		contains_case_insensitive(source_name, "sing");

	const int hint_count = static_cast<int>(bass_hint) + static_cast<int>(other_hint) +
			       static_cast<int>(keyboard_hint) + static_cast<int>(guitar_hint) +
			       static_cast<int>(vocal_hint);
	if (hint_count != 1)
		return AnalysisInputMode::FullMix;
	if (bass_hint)
		return AnalysisInputMode::IsolatedBass;
	if (other_hint)
		return AnalysisInputMode::IsolatedOther;
	if (keyboard_hint)
		return AnalysisInputMode::IsolatedKeyboard;
	if (guitar_hint)
		return AnalysisInputMode::IsolatedGuitar;
	return AnalysisInputMode::IsolatedVocal;
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

float bass_candidate_score(const std::array<float, kNoteProbeCount> &powers, int midi, bool include_harmonics,
			   bool isolated_harmonic_support = false)
{
	const float fundamental = probe_level(powers, midi);
	float score = fundamental;
	if (include_harmonics) {
		if (isolated_harmonic_support && midi <= kIsolatedBassStrongHarmonicMaxMidi) {
			score += probe_level(powers, midi + 12) * 0.54f;
			score += probe_level(powers, midi + 19) * 0.96f;
			score += probe_level(powers, midi + 24) * 0.68f;
			score += probe_level(powers, midi + 28) * 0.20f;
			score += probe_level(powers, midi + 31) * 0.16f;
		} else {
			score += probe_level(powers, midi + 12) * 0.38f;
			score += probe_level(powers, midi + 19) * 0.22f;
			score += probe_level(powers, midi + 24) * 0.12f;
		}
	}
	return score;
}

bool correct_isolated_bass_upper_partial_alias(const std::array<float, kNoteProbeCount> &powers, int max_midi,
					       RangeResult &result, float &second_score)
{
	if (result.midi < kFirstMidi || result.midi > kIsolatedBassStrongHarmonicMaxMidi || result.score <= 1.0e-6f)
		return false;

	const int upper_midi = result.midi + 19;
	if (upper_midi > max_midi || upper_midi > kLastMidi)
		return false;

	const float lower_fundamental = probe_level(powers, result.midi);
	const float upper_fundamental = probe_level(powers, upper_midi);
	const float octave_support =
		std::max(probe_level(powers, result.midi + 12), probe_level(powers, result.midi + 24) * 0.80f);
	const float upper_score = bass_candidate_score(powers, upper_midi, true, false);
	const bool weak_same_pitch_chain =
		octave_support < std::max(lower_fundamental * 1.45f, upper_fundamental * 0.42f);
	const bool upper_dominant =
		upper_fundamental >= lower_fundamental * 2.30f && upper_fundamental >= octave_support * 2.20f;
	const bool upper_competitive =
		upper_score >= result.score * 0.88f || upper_fundamental >= result.score * 0.82f;
	if (!weak_same_pitch_chain || !upper_dominant || !upper_competitive)
		return false;

	second_score = std::max(second_score, result.score);
	result.midi = upper_midi;
	result.score = upper_score;
	return true;
}

float melodic_candidate_score(const std::array<float, kNoteProbeCount> &powers, int midi, bool include_harmonics)
{
	float score = probe_level(powers, midi);
	if (include_harmonics) {
		score += probe_level(powers, midi + 12) * 0.72f;
		score += probe_level(powers, midi + 19) * 0.62f;
		score += probe_level(powers, midi + 24) * 0.48f;
		score += probe_level(powers, midi + 28) * 0.34f;
		score += probe_level(powers, midi + 31) * 0.26f;
		score += probe_level(powers, midi + 36) * 0.18f;
		score += probe_level(powers, midi + 40) * 0.12f;
		score += probe_level(powers, midi + 43) * 0.10f;
	}
	return score;
}

RangeResult dominant_bass_note(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi,
			       bool include_harmonics, bool isolated_harmonic_support = false)
{
	float total = 0.0f;
	float second_score = 0.0f;
	RangeResult result;

	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float score = bass_candidate_score(powers, midi, include_harmonics,
							 isolated_harmonic_support);
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
			const float lower_score = bass_candidate_score(powers, lower, true,
								       isolated_harmonic_support);
			if (lower_fundamental < current_fundamental * 0.14f || lower_score < result.score * 0.55f)
				break;
			result.midi = lower;
			result.score = lower_score;
		}
	}
	if (include_harmonics && isolated_harmonic_support)
		correct_isolated_bass_upper_partial_alias(powers, max_midi, result, second_score);

	const float total_confidence = total > 1.0e-6f ? result.score / total : 0.0f;
	const float runner_up_confidence =
		result.score + second_score > 1.0e-6f ? result.score / (result.score + second_score) : 0.0f;
	result.confidence = std::clamp(std::max(total_confidence, runner_up_confidence * 0.55f), 0.0f, 1.0f);
	return result;
}

float normalized_bass_autocorrelation(const float *samples, std::size_t count, float mean, uint32_t sample_rate,
				      int midi)
{
	if (!samples || count == 0 || sample_rate == 0)
		return 0.0f;

	const float frequency = midi_frequency(midi);
	if (frequency <= 0.0f)
		return 0.0f;
	const std::size_t lag =
		static_cast<std::size_t>(std::max(1.0f, std::round(static_cast<float>(sample_rate) / frequency)));
	if (lag >= count)
		return 0.0f;

	double numerator = 0.0;
	double left = 0.0;
	double right = 0.0;
	const std::size_t limit = count - lag;
	for (std::size_t i = 0; i < limit; ++i) {
		const float a = std::clamp(samples[i], -4.0f, 4.0f) - mean;
		const float b = std::clamp(samples[i + lag], -4.0f, 4.0f) - mean;
		numerator += static_cast<double>(a) * static_cast<double>(b);
		left += static_cast<double>(a) * static_cast<double>(a);
		right += static_cast<double>(b) * static_cast<double>(b);
	}

	if (left <= 1.0e-12 || right <= 1.0e-12)
		return 0.0f;
	return std::clamp(static_cast<float>(numerator / std::sqrt(left * right)), 0.0f, 1.0f);
}

RangeResult periodic_bass_note(const float *samples, std::size_t count, float mean, uint32_t sample_rate,
			       const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi,
			       bool isolated_harmonic_support = false)
{
	RangeResult result;
	float strongest_spectral = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi)
		strongest_spectral = std::max(strongest_spectral,
					      bass_candidate_score(powers, midi, true,
								   isolated_harmonic_support));
	if (strongest_spectral <= 1.0e-6f)
		return result;

	float second_score = 0.0f;
	float best_periodicity = 0.0f;
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float periodicity = normalized_bass_autocorrelation(samples, count, mean, sample_rate, midi);
		if (periodicity < kIsolatedBassPeriodicityFloor)
			continue;
		const float spectral_score = bass_candidate_score(powers, midi, true,
								  isolated_harmonic_support);
		const float spectral_ratio = spectral_score / strongest_spectral;
		if (spectral_ratio < kIsolatedBassPeriodicitySpectralRatio)
			continue;

		const float score = periodicity * (0.35f + spectral_ratio * 0.65f);
		if (score > result.score) {
			second_score = result.score;
			result.score = score;
			result.midi = midi;
			best_periodicity = periodicity;
		} else {
			second_score = std::max(second_score, score);
		}
	}

	if (result.midi < 0)
		return result;

	const float margin = result.score + second_score > 1.0e-6f ? result.score / (result.score + second_score) :
									      1.0f;
	const float spectral_score = bass_candidate_score(powers, result.midi, true,
							  isolated_harmonic_support);
	RangeResult corrected_spectral;
	corrected_spectral.midi = result.midi;
	corrected_spectral.score = spectral_score;
	float alias_second_score = 0.0f;
	if (correct_isolated_bass_upper_partial_alias(powers, max_midi, corrected_spectral, alias_second_score))
		result.midi = corrected_spectral.midi;
	result.confidence = std::clamp(std::max(best_periodicity * 0.85f, margin * 0.58f), 0.0f, 1.0f);
	result.score = bass_candidate_score(powers, result.midi, true, isolated_harmonic_support);
	return result;
}

RangeResult choose_isolated_bass_note(const RangeResult &spectral_note, const RangeResult &periodic_note,
				      int periodic_replacement_max_midi)
{
	if (periodic_note.midi < kFirstMidi || periodic_note.confidence < kIsolatedBassPeriodicityFloor)
		return spectral_note;
	if (spectral_note.midi < kFirstMidi)
		return periodic_note;
	const bool same_note = periodic_note.midi == spectral_note.midi;
	const int upward_interval = spectral_note.midi - periodic_note.midi;
	const bool related_partial = upward_interval == 12 || upward_interval == 19 || upward_interval == 24 ||
				     upward_interval == 28 || upward_interval == 31;
	const int periodic_above_spectral = periodic_note.midi - spectral_note.midi;
	const bool upward_harmonic = periodic_above_spectral == 12 || periodic_above_spectral == 19 ||
				     periodic_above_spectral == 24 || periodic_above_spectral == 28 ||
				     periodic_above_spectral == 31;
	const bool neighboring_low_lobe = std::abs(periodic_note.midi - spectral_note.midi) <= 2;
	const bool score_close = periodic_note.score >= spectral_note.score * kIsolatedBassPeriodicitySpectralRatio;
	const bool strong_periodic_replacement =
		periodic_above_spectral > 2 && periodic_note.midi <= periodic_replacement_max_midi &&
		periodic_note.confidence >= 0.50f && periodic_note.score >= spectral_note.score * 0.82f &&
		(spectral_note.confidence < 0.30f || periodic_note.score >= spectral_note.score * 1.08f);
	const bool upward_low_lobe = periodic_above_spectral > 2 && periodic_above_spectral <= 5 &&
				     !upward_harmonic && score_close && periodic_note.confidence >= 0.68f;
	if (periodic_above_spectral > 2 && !upward_low_lobe && !strong_periodic_replacement)
		return spectral_note;
	if (!same_note && !related_partial && !neighboring_low_lobe && !upward_low_lobe && !score_close)
		return spectral_note;
	if (!score_close && spectral_note.confidence >= 0.18f)
		return spectral_note;

	RangeResult result = periodic_note;
	result.confidence = std::max(result.confidence, spectral_note.confidence * 0.92f);
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

bool full_mix_upper_bass_supported(const std::array<float, kNoteProbeCount> &powers, const RangeResult &upper_note,
				   const RangeResult &broad_note)
{
	if (upper_note.midi <= kDefaultBassMaxMidi || upper_note.midi > kFullMixCleanHighSynthBassMaxMidi ||
	    upper_note.score <= 1.0e-6f || upper_note.confidence < 0.06f)
		return false;

	const float fundamental = probe_level(powers, upper_note.midi);
	if (fundamental <= 1.0e-6f)
		return false;

	const float octave = probe_level(powers, upper_note.midi + 12);
	const float fifth = probe_level(powers, upper_note.midi + 19);
	const float second_octave = probe_level(powers, upper_note.midi + 24);
	const bool upper_bass_range = upper_note.midi <= kFullMixUpperBassMaxMidi;
	const bool supported_upper_stack =
		upper_bass_range &&
		octave >= fundamental * 0.44f &&
		(fifth >= fundamental * 0.16f || second_octave >= fundamental * 0.08f);
	const bool competitive_with_broad_bass =
		broad_note.score <= 1.0e-6f || upper_note.score >= broad_note.score * 0.24f;
	const bool clean_upper_synth_bass =
		competitive_with_broad_bass &&
		upper_note.confidence >= (upper_bass_range ? 0.34f : 0.60f) &&
		octave <= fundamental * 0.18f &&
		fifth <= fundamental * 0.105f &&
		second_octave <= fundamental * 0.050f;
	return supported_upper_stack || clean_upper_synth_bass;
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
	float simultaneous_onset = 0.0f;
	float periodicity = 0.0f;
	float harmonicity = 0.0f;
	float harmonic_fit_error = 0.0f;
	float spectral_centroid = 0.0f;
	float spectral_slope = 0.0f;
	float local_noise_level = 0.0f;
	float third_octave_ratio = 0.0f;
	std::array<float, 5> harmonic_ratios = {};
	std::array<float, 5> ownership_scores = {};
	InstrumentKind owner = InstrumentKind::Ambiguous;
	float ownership_confidence = 0.0f;
};

struct TemporalNoteFeatures {
	float onset_strength = 0.0f;
	float decay_rate = 0.0f;
	float pitch_stability = 0.0f;
	float simultaneous_onset = 0.0f;
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

enum class FullMixDisplayRow {
	Keyboard,
	Guitar,
	Vocal,
	Other,
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
	evidence.simultaneous_onset = temporal.simultaneous_onset;

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
	if (candidate.midi + 36 <= kLastMidi) {
		const float third_octave =
			std::sqrt(std::max(powers[candidate.midi + 36 - kFirstMidi], 0.0f));
		evidence.third_octave_ratio = std::clamp(third_octave / fundamental, 0.0f, 1.0f);
	}
	const float harmonic_support = std::clamp(harmonic_sum / std::max(fundamental, 1.0e-6f), 0.0f, 1.0f);
	const float noise_penalty = std::clamp(1.0f - evidence.local_noise_level * 0.45f, 0.35f, 1.0f);
	const float fit_penalty = std::clamp(1.0f - evidence.harmonic_fit_error * 0.40f, 0.45f, 1.0f);
	evidence.periodicity = std::clamp(noise_penalty * fit_penalty * (0.72f + harmonic_support * 0.28f),
					  0.0f, 1.0f);
	evidence.pitch_confidence = std::clamp(evidence.spectral_level * noise_penalty * fit_penalty *
						       (0.85f + evidence.periodicity * 0.15f),
					       0.0f, 1.0f);
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

int midi_pitch_class(int midi)
{
	return ((midi % 12) + 12) % 12;
}

bool candidate_list_has_pitch_class(const NoteCandidateList &candidates, int pitch_class)
{
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi >= kFirstMidi && candidate.midi <= kLastMidi &&
		    midi_pitch_class(candidate.midi) == pitch_class)
			return true;
	}
	return false;
}

void add_or_replace_candidate(NoteCandidateList &candidates, const NoteCandidate &candidate, int max_notes)
{
	if (max_notes <= 0)
		return;

	if (candidates.size() < static_cast<std::size_t>(max_notes)) {
		candidates.push_back(candidate);
		return;
	}

	std::array<int, 12> pitch_class_counts = {};
	for (const NoteCandidate &existing : candidates) {
		if (existing.midi >= kFirstMidi && existing.midi <= kLastMidi)
			++pitch_class_counts[midi_pitch_class(existing.midi)];
	}

	std::size_t replace_index = candidates.size();
	float replace_score = 1.0e30f;
	for (std::size_t i = 0; i < candidates.size(); ++i) {
		const int pitch_class = midi_pitch_class(candidates[i].midi);
		if (pitch_class_counts[pitch_class] <= 1)
			continue;
		if (candidates[i].score < replace_score) {
			replace_score = candidates[i].score;
			replace_index = i;
		}
	}

	if (replace_index == candidates.size()) {
		for (std::size_t i = 0; i < candidates.size(); ++i) {
			if (candidates[i].score < replace_score) {
				replace_score = candidates[i].score;
				replace_index = i;
			}
		}
	}

	if (replace_index < candidates.size() && candidate.score >= replace_score * 0.45f)
		candidates[replace_index] = candidate;
}

NoteCandidateList note_peak_candidates(const std::array<float, kNoteProbeCount> &powers, int min_midi,
				       int max_midi, int max_notes,
				       const std::array<bool, 12> *blocked_pitch_classes = nullptr,
				       const std::array<bool, 12> *allowed_pitch_classes = nullptr,
				       bool suppress_adjacent_neighbors = false,
				       const std::array<bool, kNoteProbeCount> *allowed_midis = nullptr,
				       float relative_floor = kNoteRelativeFloor,
				       bool include_harmonic_support = false)
{
	std::array<float, kNoteProbeCount> scores = {};
	float strongest_score = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (!pitch_class_available(midi, blocked_pitch_classes, allowed_pitch_classes, allowed_midis))
			continue;
		float score = melodic_candidate_score(powers, midi, include_harmonic_support);
		if (include_harmonic_support) {
			const float raw = probe_level(powers, midi);
			if (raw < score * 0.18f)
				score = raw;
		}
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
			const bool adjacent_mask =
				suppress_adjacent_neighbors && std::abs(existing.midi - candidate.midi) <= 1 &&
				candidate.score < existing.score * 0.72f;
			const bool harmonic_mask =
				likely_selected_harmonic(existing, candidate) &&
				probe_level(powers, candidate.midi) < probe_level(powers, existing.midi) * 0.35f;
			if (adjacent_mask || harmonic_mask) {
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

	if (include_harmonic_support && max_notes > 1) {
		std::array<float, 12> best_raw = {};
		std::array<int, 12> best_midi = {};
		best_midi.fill(-1);
		float strongest_raw = 0.0f;
		for (int midi = min_midi; midi <= max_midi; ++midi) {
			if (!pitch_class_available(midi, blocked_pitch_classes, allowed_pitch_classes, allowed_midis))
				continue;
			const float raw = probe_level(powers, midi);
			strongest_raw = std::max(strongest_raw, raw);
			const int pitch_class = midi_pitch_class(midi);
			if (raw > best_raw[pitch_class]) {
				best_raw[pitch_class] = raw;
				best_midi[pitch_class] = midi;
			}
		}

		const float raw_floor = strongest_raw * 0.18f;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			if (best_midi[pitch_class] < 0 || best_raw[pitch_class] < raw_floor ||
			    candidate_list_has_pitch_class(selected, pitch_class))
				continue;
			const int midi = best_midi[pitch_class];
			const float score = std::max(scores[midi - kFirstMidi], best_raw[pitch_class]);
			add_or_replace_candidate(selected, NoteCandidate{midi, score}, max_notes);
		}
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
	std::array<bool, kNoteProbeCount> keyboard_display_suppressed = {};
	std::array<bool, kNoteProbeCount> guitar_display_suppressed = {};
	std::array<bool, kNoteProbeCount> vocal_display_suppressed = {};
	std::array<bool, kNoteProbeCount> other_display_suppressed = {};
	std::array<float, kNoteProbeCount> global_note_levels = {};
	std::array<float, 12> global_chroma = {};
	NoteCandidateList keyboard_candidates;
	NoteCandidateList guitar_candidates;
	NoteCandidateList vocal_candidates;
	NoteCandidateList other_candidates;
	NoteCandidateList ambiguous_candidates;
	std::array<FullMixDebugCandidate, kFullMixDebugCandidateCount> debug_candidates = {};
	std::size_t debug_candidate_count = 0;
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

void append_full_mix_debug_candidate(FullMixOwnership &ownership, const NoteCandidate &candidate,
				     const NoteEvidence &evidence, InstrumentKind owner)
{
	if (ownership.debug_candidate_count >= ownership.debug_candidates.size())
		return;

	FullMixDebugCandidate debug;
	debug.midi = candidate.midi;
	debug.owner = owner;
	debug.ownership_confidence = evidence.ownership_confidence;
	debug.bass_score = evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Bass)];
	debug.keyboard_score = evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Keyboard)];
	debug.guitar_score = evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Guitar)];
	debug.vocal_score = evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Vocal)];
	debug.other_score = evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Other)];
	debug.spectral_level = evidence.spectral_level;
	debug.pitch_confidence = evidence.pitch_confidence;
	debug.periodicity = evidence.periodicity;
	debug.harmonicity = evidence.harmonicity;
	debug.harmonic_fit_error = evidence.harmonic_fit_error;
	debug.spectral_centroid = evidence.spectral_centroid;
	debug.spectral_slope = evidence.spectral_slope;
	debug.local_noise_level = evidence.local_noise_level;
	debug.third_octave_ratio = evidence.third_octave_ratio;
	debug.harmonic_ratios = evidence.harmonic_ratios;
	ownership.debug_candidates[ownership.debug_candidate_count++] = debug;
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

bool confident_full_mix_row_midi(const std::array<bool, kNoteProbeCount> &mask,
				 const NoteCandidateList &candidates, int midi, float min_confidence)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;

	const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
	if (!mask[index])
		return false;

	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi == midi && candidate.ownership_confidence >= min_confidence)
			return true;
	}
	return false;
}

void remove_full_mix_row_midi(std::array<bool, kNoteProbeCount> &mask, NoteCandidateList &candidates, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return;

	mask[static_cast<std::size_t>(midi - kFirstMidi)] = false;
	remove_candidate_midi(candidates, midi);
}

void suppress_full_mix_row_display_midi(FullMixOwnership &ownership, FullMixDisplayRow row, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return;

	const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
	switch (row) {
	case FullMixDisplayRow::Keyboard:
		ownership.keyboard_display_suppressed[index] = true;
		break;
	case FullMixDisplayRow::Guitar:
		ownership.guitar_display_suppressed[index] = true;
		break;
	case FullMixDisplayRow::Vocal:
		ownership.vocal_display_suppressed[index] = true;
		break;
	case FullMixDisplayRow::Other:
		ownership.other_display_suppressed[index] = true;
		break;
	}
}

bool full_mix_row_display_midi_suppressed(const FullMixOwnership &ownership, FullMixDisplayRow row, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;

	const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
	switch (row) {
	case FullMixDisplayRow::Keyboard:
		return ownership.keyboard_display_suppressed[index];
	case FullMixDisplayRow::Guitar:
		return ownership.guitar_display_suppressed[index];
	case FullMixDisplayRow::Vocal:
		return ownership.vocal_display_suppressed[index];
	case FullMixDisplayRow::Other:
		return ownership.other_display_suppressed[index];
	}
	return false;
}

bool full_mix_row_midi_active(const std::array<bool, kNoteProbeCount> &mask, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;
	return mask[static_cast<std::size_t>(midi - kFirstMidi)];
}

bool candidate_list_has_midi(const NoteCandidateList &candidates, int midi)
{
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi == midi)
			return true;
	}
	return false;
}

bool full_mix_named_row_midi_active(const FullMixOwnership &ownership, int midi)
{
	return full_mix_row_midi_active(ownership.keyboard, midi) ||
	       full_mix_row_midi_active(ownership.guitar, midi) ||
	       full_mix_row_midi_active(ownership.vocal, midi) ||
	       full_mix_row_midi_active(ownership.other, midi);
}

void suppress_full_mix_bass_duplicate_ownership(FullMixOwnership &ownership, int bass_midi)
{
	static constexpr float kPreserveConfidentOwner = 0.78f;
	static constexpr float kPreserveSupportedOtherOwner = 0.44f;
	static constexpr int kPreserveConfidentOwnerMinMidi = 48;
	if (bass_midi < kPreserveConfidentOwnerMinMidi) {
		remove_full_mix_row_midi(ownership.keyboard, ownership.keyboard_candidates, bass_midi);
		remove_full_mix_row_midi(ownership.guitar, ownership.guitar_candidates, bass_midi);
		remove_full_mix_row_midi(ownership.vocal, ownership.vocal_candidates, bass_midi);
		remove_full_mix_row_midi(ownership.other, ownership.other_candidates, bass_midi);
		return;
	}
	if (!confident_full_mix_row_midi(ownership.keyboard, ownership.keyboard_candidates, bass_midi,
					 kPreserveConfidentOwner))
		remove_full_mix_row_midi(ownership.keyboard, ownership.keyboard_candidates, bass_midi);
	if (!confident_full_mix_row_midi(ownership.guitar, ownership.guitar_candidates, bass_midi,
					 kPreserveConfidentOwner))
		remove_full_mix_row_midi(ownership.guitar, ownership.guitar_candidates, bass_midi);
	if (!confident_full_mix_row_midi(ownership.vocal, ownership.vocal_candidates, bass_midi,
					 kPreserveConfidentOwner))
		remove_full_mix_row_midi(ownership.vocal, ownership.vocal_candidates, bass_midi);
	if (!confident_full_mix_row_midi(ownership.other, ownership.other_candidates, bass_midi,
					 kPreserveSupportedOtherOwner))
		remove_full_mix_row_midi(ownership.other, ownership.other_candidates, bass_midi);
}

void suppress_full_mix_low_bass_harmonic_aliases(FullMixOwnership &ownership,
						 const std::array<float, kNoteProbeCount> &powers,
						 int bass_midi, bool preserve_synthetic_other)
{
	if (bass_midi < kBassMinMidi || bass_midi >= kGuitarMinMidi)
		return;

	const float fundamental = probe_level(powers, bass_midi);
	if (fundamental <= 1.0e-6f)
		return;

	auto suppress_alias = [&](int midi) {
		static constexpr float kPreserveConfidentNamedOwner = 0.76f;
		static constexpr float kPreserveSupportedOtherOwner = 0.48f;
		static constexpr float kPreserveSyntheticOtherOwner = 0.40f;
		const float preserve_other_confidence =
			preserve_synthetic_other ? kPreserveSyntheticOtherOwner : kPreserveSupportedOtherOwner;
		auto suppress_row = [&](FullMixDisplayRow row, std::array<bool, kNoteProbeCount> &mask,
					NoteCandidateList &candidates, float preserve_confidence) {
			if (confident_full_mix_row_midi(mask, candidates, midi, preserve_confidence))
				return;
			remove_full_mix_row_midi(mask, candidates, midi);
			suppress_full_mix_row_display_midi(ownership, row, midi);
		};

		suppress_row(FullMixDisplayRow::Keyboard, ownership.keyboard, ownership.keyboard_candidates,
			     kPreserveConfidentNamedOwner);
		suppress_row(FullMixDisplayRow::Guitar, ownership.guitar, ownership.guitar_candidates,
			     kPreserveConfidentNamedOwner);
		suppress_row(FullMixDisplayRow::Vocal, ownership.vocal, ownership.vocal_candidates,
			     kPreserveConfidentNamedOwner);
		suppress_row(FullMixDisplayRow::Other, ownership.other, ownership.other_candidates,
			     preserve_other_confidence);
	};

	suppress_alias(bass_midi);
	for (int interval : {12, 19, 24, 28, 31, 36}) {
		const int harmonic_midi = bass_midi + interval;
		if (harmonic_midi < kFirstMidi || harmonic_midi > kLastMidi)
			continue;

		const float harmonic = probe_level(powers, harmonic_midi);
		if (harmonic < fundamental * 0.040f)
			continue;

		if (interval == 12) {
			for (int delta : {-1, 0, 1})
				suppress_alias(harmonic_midi + delta);
		} else {
			suppress_alias(harmonic_midi);
		}
	}
}

float strongest_candidate_score_except_midi(const NoteCandidateList &candidates, int excluded_midi)
{
	float score = 0.0f;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi != excluded_midi)
			score = std::max(score, candidate.score);
	}
	return score;
}

float capped_restored_low_owner_score(const NoteCandidateList &existing_candidates, int midi, float score)
{
	const float reference = strongest_candidate_score_except_midi(existing_candidates, midi);
	if (reference <= 1.0e-6f)
		return score;
	return std::min(score, reference * 0.82f);
}

void restore_full_mix_low_guitar_from_bass(FullMixOwnership &ownership,
					   const std::array<float, kNoteProbeCount> &powers,
					   int bass_midi)
{
	if (bass_midi < kGuitarMinMidi || bass_midi > kDefaultBassMaxMidi ||
	    full_mix_row_midi_active(ownership.guitar, bass_midi))
		return;

	const float fundamental = probe_level(powers, bass_midi);
	if (fundamental <= 1.0e-6f)
		return;

	const float octave = probe_level(powers, bass_midi + 12);
	const float fifth = probe_level(powers, bass_midi + 19);
	const float second_octave = probe_level(powers, bass_midi + 24);
	const float upper_major_third = probe_level(powers, bass_midi + 28);
	const bool dominant_guitar_octave = octave >= fundamental * 0.62f;
	const bool same_midi_rich_melodic_owner =
		full_mix_row_midi_active(ownership.other, bass_midi) ||
		full_mix_row_midi_active(ownership.ambiguous, bass_midi);
	const bool supported_guitar_stack =
		fifth >= fundamental * 0.16f &&
		(second_octave >= fundamental * 0.045f ||
		 (same_midi_rich_melodic_owner && upper_major_third >= fundamental * 0.020f));
	const bool too_bass_like = octave < fundamental * 0.58f &&
				   (fifth + second_octave + upper_major_third) < fundamental * 0.34f;
	if (!dominant_guitar_octave || !supported_guitar_stack || too_bass_like)
		return;

	const float display_level = std::max(fundamental, octave * 0.72f);
	NoteCandidate candidate;
	candidate.midi = bass_midi;
	candidate.score =
		capped_restored_low_owner_score(ownership.guitar_candidates, bass_midi,
						display_level * display_level);
	candidate.ownership_confidence = 0.52f;
	ownership.guitar[static_cast<std::size_t>(bass_midi - kFirstMidi)] = true;
	ownership.guitar_candidates.push_back(candidate);
}

void restore_full_mix_low_keyboard_from_bass(FullMixOwnership &ownership,
					     const std::array<float, kNoteProbeCount> &powers,
					     int bass_midi)
{
	auto restore_candidate = [&](int keyboard_midi, bool octave_alias) {
		if (keyboard_midi < kKeyboardMinMidi || keyboard_midi >= 48 ||
		    full_mix_row_midi_active(ownership.keyboard, keyboard_midi))
			return false;

		const float fundamental = probe_level(powers, keyboard_midi);
		if (fundamental <= 1.0e-6f)
			return false;

		const float octave = probe_level(powers, keyboard_midi + 12);
		const float fifth = probe_level(powers, keyboard_midi + 19);
		const float second_octave = probe_level(powers, keyboard_midi + 24);
		const float upper_major_third = probe_level(powers, keyboard_midi + 28);
		const float upper_fifth = probe_level(powers, keyboard_midi + 31);
		const float upper_stack = fifth + second_octave + upper_major_third;
		const bool strong_electronic_stack =
			!octave_alias &&
			octave >= fundamental * 0.60f &&
			(fifth >= fundamental * 0.26f || second_octave >= fundamental * 0.20f ||
			 upper_major_third >= fundamental * 0.16f) &&
			upper_stack >= fundamental * 0.42f;
		const bool sub_low_electronic_keyboard_stack =
			!octave_alias &&
			keyboard_midi < kGuitarMinMidi &&
			octave >= fundamental * 0.34f &&
			octave <= fundamental * 0.72f &&
			fifth >= fundamental * 0.070f &&
			fifth <= fundamental * 0.18f &&
			second_octave >= fundamental * 0.070f &&
			upper_major_third <= fundamental * 0.14f &&
			upper_stack >= fundamental * 0.18f;
		const bool octave_dominant_sub_low_keyboard_stack =
			!octave_alias &&
			keyboard_midi >= 30 &&
			keyboard_midi < kGuitarMinMidi &&
			octave > fundamental * 0.72f &&
			fifth >= fundamental * 0.12f &&
			upper_major_third <= fundamental * 0.14f &&
			upper_stack >= fundamental * 0.18f;
		const bool rich_sub_low_electronic_keyboard_stack =
			!octave_alias &&
			keyboard_midi <= 34 &&
			keyboard_midi < kGuitarMinMidi &&
			octave >= fundamental * 0.46f &&
			octave <= fundamental * 0.86f &&
			fifth >= fundamental * 0.055f &&
			upper_stack >= fundamental * 0.25f &&
			(second_octave >= fundamental * 0.045f ||
			 upper_major_third >= fundamental * 0.045f);
		const bool fundamental_stack_sub_low_keyboard =
			!octave_alias &&
			keyboard_midi >= 30 &&
			keyboard_midi <= 34 &&
			keyboard_midi < kGuitarMinMidi &&
			octave >= fundamental * 0.18f &&
			octave <= fundamental * 0.36f &&
			fifth >= fundamental * 0.20f &&
			fifth <= fundamental * 0.54f &&
			second_octave >= fundamental * 0.20f &&
			second_octave <= fundamental * 0.44f &&
			upper_major_third <= fundamental * 0.045f &&
			upper_fifth <= fundamental * 0.16f &&
			(fifth + second_octave + upper_major_third + upper_fifth) >= fundamental * 0.48f;
		const bool octave_alias_sub_low_keyboard_stack =
			octave_alias &&
			keyboard_midi < kGuitarMinMidi &&
			octave >= fundamental * 0.62f &&
			upper_stack >= fundamental * 0.42f &&
			(fifth >= fundamental * 0.24f ||
			 second_octave >= fundamental * 0.20f ||
			 upper_major_third >= fundamental * 0.16f);
		const bool strong_sub_low_keyboard_stack =
			strong_electronic_stack &&
			!octave_alias &&
			keyboard_midi < kGuitarMinMidi;
		if (!strong_electronic_stack && !sub_low_electronic_keyboard_stack &&
		    !octave_dominant_sub_low_keyboard_stack &&
		    !rich_sub_low_electronic_keyboard_stack &&
		    !fundamental_stack_sub_low_keyboard &&
		    !octave_alias_sub_low_keyboard_stack)
			return false;

		const float display_level =
			std::max({fundamental, octave * 0.68f, fifth * 0.76f,
				  second_octave * 0.62f, upper_major_third * 0.58f,
				  upper_fifth * 0.54f});
		NoteCandidate candidate;
		candidate.midi = keyboard_midi;
		candidate.score =
			capped_restored_low_owner_score(ownership.keyboard_candidates, keyboard_midi,
							display_level * display_level);
		candidate.ownership_confidence =
			(strong_sub_low_keyboard_stack ||
			 sub_low_electronic_keyboard_stack ||
			 octave_dominant_sub_low_keyboard_stack ||
			 rich_sub_low_electronic_keyboard_stack ||
			 fundamental_stack_sub_low_keyboard ||
			 octave_alias_sub_low_keyboard_stack) ? 0.80f : 0.50f;
		ownership.keyboard[static_cast<std::size_t>(keyboard_midi - kFirstMidi)] = true;
		ownership.keyboard_candidates.push_back(candidate);
		return true;
	};

	(void)restore_candidate(bass_midi, false);
	(void)restore_candidate(bass_midi - 12, true);
}

void restore_full_mix_low_other_from_bass(FullMixOwnership &ownership,
					  const std::array<float, kNoteProbeCount> &powers,
					  int bass_midi)
{
	if (bass_midi < kOtherMinMidi || bass_midi > kDefaultBassMaxMidi ||
	    full_mix_row_midi_active(ownership.other, bass_midi))
		return;

	const float fundamental = probe_level(powers, bass_midi);
	if (fundamental <= 1.0e-6f)
		return;

	const float octave = probe_level(powers, bass_midi + 12);
	const float fifth = probe_level(powers, bass_midi + 19);
	const float second_octave = probe_level(powers, bass_midi + 24);
	const float upper_major_third = probe_level(powers, bass_midi + 28);
	const float upper_stack = fifth + second_octave + upper_major_third;
	const bool keyboard_octave_alias =
		bass_midi + 12 <= kLastMidi &&
		full_mix_row_midi_active(ownership.keyboard, bass_midi + 12);
	const bool low_bowed_string_stack =
		bass_midi >= kGuitarMinMidi &&
		octave <= fundamental * 0.34f &&
		upper_stack >= fundamental * 0.20f &&
		(fifth >= fundamental * 0.070f || second_octave >= fundamental * 0.065f) &&
		upper_major_third <= fundamental * 0.18f;
	const bool sub_low_bowed_string_stack =
		bass_midi >= 36 &&
		bass_midi < kGuitarMinMidi &&
		octave <= fundamental * 0.34f &&
		upper_stack >= fundamental * 0.16f &&
		(fifth >= fundamental * 0.055f || second_octave >= fundamental * 0.050f) &&
		upper_major_third <= fundamental * 0.20f;
	const bool sparse_sub_low_bowed_string_stack =
		bass_midi >= 36 &&
		bass_midi < kGuitarMinMidi &&
		octave <= fundamental * 0.09f &&
		upper_stack >= fundamental * 0.035f &&
		upper_stack <= fundamental * 0.16f &&
		fifth <= fundamental * 0.14f &&
		second_octave <= fundamental * 0.040f &&
		upper_major_third <= fundamental * 0.030f;
	const bool octave_alias_sparse_sub_low_bowed_string_stack =
		bass_midi >= 36 &&
		bass_midi < kGuitarMinMidi &&
		keyboard_octave_alias &&
		octave >= fundamental * 0.040f &&
		octave <= fundamental * 0.30f &&
		upper_stack <= fundamental * 0.080f &&
		fifth <= fundamental * 0.040f &&
		second_octave <= fundamental * 0.040f &&
		upper_major_third <= fundamental * 0.015f;
	if (!low_bowed_string_stack && !sub_low_bowed_string_stack &&
	    !sparse_sub_low_bowed_string_stack &&
	    !octave_alias_sparse_sub_low_bowed_string_stack)
		return;

	const float display_level =
		std::max(fundamental, std::max(fifth * 0.86f, second_octave * 0.92f));
	NoteCandidate candidate;
	candidate.midi = bass_midi;
	candidate.score =
		capped_restored_low_owner_score(ownership.other_candidates, bass_midi,
						display_level * display_level);
	candidate.ownership_confidence =
		(sub_low_bowed_string_stack || sparse_sub_low_bowed_string_stack ||
		 octave_alias_sparse_sub_low_bowed_string_stack) ? 0.50f : 0.42f;
	ownership.other[static_cast<std::size_t>(bass_midi - kFirstMidi)] = true;
	ownership.other_candidates.push_back(candidate);
}

void restore_full_mix_low_synth_other_from_bass(FullMixOwnership &ownership,
						const std::array<float, kNoteProbeCount> &powers,
						int bass_midi, float bass_confidence, float bass_score)
{
	if (bass_midi < kOtherMinMidi || bass_midi > kDefaultBassMaxMidi ||
	    full_mix_row_midi_active(ownership.other, bass_midi))
		return;

	const float fundamental = probe_level(powers, bass_midi);
	if (fundamental <= 1.0e-6f)
		return;

	const float octave = probe_level(powers, bass_midi + 12);
	const float fifth = probe_level(powers, bass_midi + 19);
	const float second_octave = probe_level(powers, bass_midi + 24);
	const float upper_major_third = probe_level(powers, bass_midi + 28);
	const float upper_sixth = probe_level(powers, bass_midi + 33);
	const float third_octave = probe_level(powers, bass_midi + 36);
	const float upper_stack =
		octave * 0.42f + fifth + second_octave * 0.58f + upper_major_third +
		upper_sixth * 0.36f + third_octave * 0.30f;
	const bool low_synthetic_stack =
		(fifth >= fundamental * 0.18f ||
		 upper_major_third >= fundamental * 0.18f ||
		 second_octave >= fundamental * 0.16f) &&
		upper_stack >= fundamental * 0.58f;
	const bool bass_tracker_backed =
		bass_midi <= 48 && bass_confidence >= 0.20f && bass_score > 1.0e-6f;
	if (!low_synthetic_stack && !bass_tracker_backed)
		return;

	const float display_level =
		std::max({fundamental, fifth * 0.74f, upper_major_third * 0.74f, second_octave * 0.68f});
	NoteCandidate candidate;
	candidate.midi = bass_midi;
	candidate.score =
		capped_restored_low_owner_score(ownership.other_candidates, bass_midi,
						std::max(display_level * display_level, bass_score * 0.64f));
	candidate.ownership_confidence = 0.42f;
	ownership.other[static_cast<std::size_t>(bass_midi - kFirstMidi)] = true;
	ownership.other_candidates.push_back(candidate);
}

void restore_full_mix_named_synth_other_from_keyboard(FullMixOwnership &ownership)
{
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.owner != InstrumentKind::Keyboard)
			continue;
		if (debug.midi < kGuitarMinMidi || debug.midi > 60 ||
		    full_mix_row_midi_active(ownership.other, debug.midi))
			continue;
		if (debug.keyboard_score < 0.80f ||
		    debug.spectral_level < 0.70f ||
		    debug.pitch_confidence < 0.45f ||
		    debug.periodicity < 0.50f ||
		    debug.harmonic_fit_error > 0.10f ||
		    debug.local_noise_level > 0.72f)
			continue;

		float keyboard_score = 0.0f;
		for (const NoteCandidate &keyboard_candidate : ownership.keyboard_candidates) {
			if (keyboard_candidate.midi == debug.midi)
				keyboard_score = std::max(keyboard_score, keyboard_candidate.score);
		}
		if (keyboard_score <= 1.0e-6f)
			continue;

		NoteCandidate candidate;
		candidate.midi = debug.midi;
		candidate.score =
			capped_restored_low_owner_score(ownership.other_candidates, debug.midi,
							keyboard_score * 0.72f);
		candidate.ownership_confidence = 0.40f;
		ownership.other[static_cast<std::size_t>(debug.midi - kFirstMidi)] = true;
		ownership.other_candidates.push_back(candidate);
	}
}

void demote_sparse_full_mix_owner(FullMixOwnership &ownership, std::array<bool, kNoteProbeCount> &mask,
				  NoteCandidateList &owner_candidates,
				  const std::array<float, kNoteProbeCount> &candidate_scores)
{
	if (count_owned_notes(mask) != 1)
		return;

	std::array<bool, 12> ambiguous_pitch_classes = {};
	float strongest_ambiguous_score = 0.0f;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
		if (!ownership.ambiguous[index])
			continue;
		ambiguous_pitch_classes[midi_pitch_class(midi)] = true;
		strongest_ambiguous_score = std::max(strongest_ambiguous_score, candidate_scores[index]);
	}

	int ambiguous_pitch_class_count = 0;
	for (bool active : ambiguous_pitch_classes) {
		if (active)
			++ambiguous_pitch_class_count;
	}
	if (ambiguous_pitch_class_count < 2)
		return;

	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
		if (!mask[index])
			continue;
		const float owner_score = candidate_scores[index];
		if (ambiguous_pitch_class_count < 4 && strongest_ambiguous_score < owner_score * 0.62f)
			return;
		mask[index] = false;
		remove_candidate_midi(owner_candidates, midi);
		ownership.ambiguous[index] = true;
		ownership.ambiguous_candidates.push_back(NoteCandidate{midi, candidate_scores[index]});
		return;
	}
}

float candidate_midi_score(const NoteCandidateList &candidates, int midi)
{
	float score = 0.0f;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi == midi)
			score = std::max(score, candidate.score);
	}
	return score;
}

bool high_octave_electronic_keyboard_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi < 84 || debug.midi > kKeyboardMaxMidi)
		return false;
	if (debug.spectral_level < 0.38f || debug.pitch_confidence < 0.30f || debug.periodicity < 0.66f)
		return false;
	if (debug.local_noise_level > 0.035f || debug.harmonic_fit_error > 0.82f)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return second >= 1.30f &&
	       second <= 2.35f &&
	       third >= 0.002f &&
	       third <= 0.78f &&
	       fourth <= 0.055f &&
	       fifth <= 0.025f &&
	       debug.spectral_centroid >= 0.23f &&
	       debug.spectral_centroid <= 0.34f &&
	       debug.spectral_slope <= 0.12f;
}

void mirror_high_full_mix_guitar_candidates(FullMixOwnership &ownership)
{
	static constexpr int kHighGuitarMirrorMinMidi = 77;
	static constexpr float kHighGuitarMirrorMinLevel = 0.50f;
	static constexpr float kHighGuitarMirrorScoreScale = 0.42f;
	for (int midi = kHighGuitarMirrorMinMidi; midi <= kGuitarMaxMidi; ++midi) {
		if (midi < kFirstMidi || midi > kLastMidi || full_mix_row_midi_active(ownership.guitar, midi))
			continue;
		const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
		if (ownership.global_note_levels[index] < kHighGuitarMirrorMinLevel)
			continue;
		bool high_electronic_keyboard_alias = false;
		const std::size_t debug_count =
			std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
		for (std::size_t debug_index = 0; debug_index < debug_count; ++debug_index) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[debug_index];
			if (debug.midi == midi && high_octave_electronic_keyboard_alias_supported(debug)) {
				high_electronic_keyboard_alias = true;
				break;
			}
		}
		if (high_electronic_keyboard_alias)
			continue;
		if (!full_mix_row_midi_active(ownership.keyboard, midi) &&
		    !full_mix_row_midi_active(ownership.ambiguous, midi))
			continue;

		const float source_score =
			std::max({candidate_midi_score(ownership.keyboard_candidates, midi),
				  candidate_midi_score(ownership.ambiguous_candidates, midi)});
		if (source_score <= 1.0e-6f)
			continue;

		NoteCandidate candidate;
		candidate.midi = midi;
		candidate.score = source_score * kHighGuitarMirrorScoreScale;
		candidate.ownership_confidence = 0.36f;
		ownership.guitar[index] = true;
		ownership.guitar_candidates.push_back(candidate);
	}
}

void add_full_mix_row_mirror(std::array<bool, kNoteProbeCount> &mask, NoteCandidateList &candidates,
			     const NoteCandidate &source, float score_scale, float confidence)
{
	if (source.midi < kFirstMidi || source.midi > kLastMidi)
		return;

	const std::size_t index = static_cast<std::size_t>(source.midi - kFirstMidi);
	if (mask[index])
		return;

	NoteCandidate mirrored = source;
	mirrored.score *= score_scale;
	mirrored.ownership_confidence = confidence;
	mask[index] = true;
	candidates.push_back(mirrored);
}

const FullMixDebugCandidate *full_mix_debug_for_midi(const FullMixOwnership &ownership, int midi)
{
	for (std::size_t i = 0; i < ownership.debug_candidate_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi == midi)
			return &debug;
	}
	return nullptr;
}

InstrumentKind strongest_named_owner_hint(const FullMixDebugCandidate &debug)
{
	static constexpr float kMinHintScore = 0.55f;
	static constexpr float kMinHintMargin = 0.08f;
	std::array<std::pair<float, InstrumentKind>, 3> scores = {{
		{debug.keyboard_score, InstrumentKind::Keyboard},
		{debug.guitar_score, InstrumentKind::Guitar},
		{debug.other_score, InstrumentKind::Other},
	}};
	std::sort(scores.begin(), scores.end(), [](const auto &lhs, const auto &rhs) {
		return lhs.first > rhs.first;
	});
	if (scores[0].first < kMinHintScore || scores[0].first - scores[1].first < kMinHintMargin)
		return InstrumentKind::Ambiguous;
	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool guitar_shaped =
		debug.midi >= 52 && debug.midi <= 76 &&
		second >= 0.24f && second <= 0.52f &&
		third >= 0.080f && third <= 0.28f &&
		fourth <= 0.20f && fifth <= 0.14f &&
		debug.guitar_score >= scores[0].first * 0.58f;
	if (scores[0].second == InstrumentKind::Keyboard && guitar_shaped)
		return InstrumentKind::Guitar;
	return scores[0].second;
}

void mirror_ambiguous_full_mix_candidates(FullMixOwnership &ownership)
{
	static constexpr float kMirrorMinLevel = 0.18f;
	static constexpr float kKeyboardMirrorScale = 0.28f;
	static constexpr float kGuitarMirrorScale = 0.32f;
	static constexpr float kOtherMirrorScale = 0.28f;
	static constexpr float kMirrorConfidence = 0.20f;
	for (const NoteCandidate &candidate : ownership.ambiguous_candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;
		if (full_mix_named_row_midi_active(ownership, candidate.midi))
			continue;
		const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
		if (ownership.global_note_levels[index] < kMirrorMinLevel)
			continue;

		const FullMixDebugCandidate *debug = full_mix_debug_for_midi(ownership, candidate.midi);
		if (!debug)
			continue;
		InstrumentKind target = strongest_named_owner_hint(*debug);
		if (target == InstrumentKind::Keyboard &&
		    candidate.midi >= kGuitarMinMidi && candidate.midi <= kGuitarMaxMidi &&
		    count_owned_notes(ownership.guitar) >= 2)
			target = InstrumentKind::Guitar;
		if (target == InstrumentKind::Keyboard &&
		    candidate.midi >= kKeyboardMinMidi && candidate.midi <= kKeyboardMaxMidi) {
			add_full_mix_row_mirror(ownership.keyboard, ownership.keyboard_candidates, candidate,
						kKeyboardMirrorScale, kMirrorConfidence);
		} else if (target == InstrumentKind::Guitar &&
			   candidate.midi >= kGuitarMinMidi && candidate.midi <= kGuitarMaxMidi) {
			add_full_mix_row_mirror(ownership.guitar, ownership.guitar_candidates, candidate,
						kGuitarMirrorScale, kMirrorConfidence);
		} else if (target == InstrumentKind::Other &&
			   candidate.midi >= kOtherMinMidi && candidate.midi <= kOtherMaxMidi) {
			add_full_mix_row_mirror(ownership.other, ownership.other_candidates, candidate,
						kOtherMirrorScale, kMirrorConfidence);
		}
	}
}

float strongest_candidate_score(const NoteCandidateList &candidates)
{
	float score = 0.0f;
	for (const NoteCandidate &candidate : candidates)
		score = std::max(score, candidate.score);
	return score;
}

bool full_mix_display_row_midi_allowed(FullMixDisplayRow row, int midi)
{
	switch (row) {
	case FullMixDisplayRow::Keyboard:
		return midi >= kKeyboardMinMidi && midi <= kKeyboardMaxMidi;
	case FullMixDisplayRow::Guitar:
		return midi >= kGuitarMinMidi && midi <= kGuitarMaxMidi;
	case FullMixDisplayRow::Vocal:
		return midi >= kFullMixVocalMinMidi && midi <= kVocalMaxMidi;
	case FullMixDisplayRow::Other:
		return midi >= kOtherMinMidi && midi <= kOtherMaxMidi;
	}
	return false;
}

bool full_mix_source_hint_allows_row(AnalysisInputMode source_hint, FullMixDisplayRow row)
{
	if (source_hint == AnalysisInputMode::Auto || source_hint == AnalysisInputMode::FullMix)
		return true;
	switch (row) {
	case FullMixDisplayRow::Keyboard:
		return source_hint == AnalysisInputMode::IsolatedKeyboard;
	case FullMixDisplayRow::Guitar:
		return source_hint == AnalysisInputMode::IsolatedGuitar;
	case FullMixDisplayRow::Vocal:
		return source_hint == AnalysisInputMode::IsolatedVocal;
	case FullMixDisplayRow::Other:
		return source_hint == AnalysisInputMode::IsolatedOther;
	}
	return true;
}

InstrumentKind full_mix_source_hint_owner(AnalysisInputMode source_hint, int midi)
{
	switch (source_hint) {
	case AnalysisInputMode::IsolatedKeyboard:
		return full_mix_display_row_midi_allowed(FullMixDisplayRow::Keyboard, midi) ?
			       InstrumentKind::Keyboard :
			       InstrumentKind::Ambiguous;
	case AnalysisInputMode::IsolatedGuitar:
		return full_mix_display_row_midi_allowed(FullMixDisplayRow::Guitar, midi) ?
			       InstrumentKind::Guitar :
			       InstrumentKind::Ambiguous;
	case AnalysisInputMode::IsolatedVocal:
		return full_mix_display_row_midi_allowed(FullMixDisplayRow::Vocal, midi) ?
			       InstrumentKind::Vocal :
			       InstrumentKind::Ambiguous;
	case AnalysisInputMode::IsolatedOther:
		return full_mix_display_row_midi_allowed(FullMixDisplayRow::Other, midi) ?
			       InstrumentKind::Other :
			       InstrumentKind::Ambiguous;
	case AnalysisInputMode::IsolatedBass:
		return midi >= kBassMinMidi && midi <= kBassMaxMidi ? InstrumentKind::Bass :
								      InstrumentKind::Ambiguous;
	case AnalysisInputMode::Auto:
	case AnalysisInputMode::FullMix:
	default:
		return InstrumentKind::Ambiguous;
	}
}

bool source_hinted_single_vocal_candidate_supported(const NoteEvidence &evidence, int midi,
						    std::size_t candidate_count)
{
	return candidate_count == 1 &&
	       midi >= kFullMixVocalMinMidi &&
	       midi <= kVocalMaxMidi &&
	       evidence.spectral_level >= 0.68f &&
	       evidence.pitch_confidence >= 0.64f &&
	       evidence.periodicity >= 0.70f &&
	       evidence.harmonic_fit_error <= 0.10f &&
	       evidence.local_noise_level <= 0.18f &&
	       evidence.spectral_centroid <= 0.34f &&
	       evidence.spectral_slope <= 0.56f;
}

void apply_full_mix_source_hint_owner(AnalysisInputMode source_hint, const NoteCandidate &candidate,
				      NoteEvidence &evidence, InstrumentKind &owner,
				      std::size_t candidate_count)
{
	const InstrumentKind hinted_owner = full_mix_source_hint_owner(source_hint, candidate.midi);
	if (hinted_owner == InstrumentKind::Ambiguous)
		return;
	if (hinted_owner == InstrumentKind::Vocal && owner == InstrumentKind::Keyboard &&
	    evidence.ownership_scores[static_cast<std::size_t>(InstrumentKind::Vocal)] < 0.35f &&
	    !source_hinted_single_vocal_candidate_supported(evidence, candidate.midi, candidate_count))
		return;

	owner = hinted_owner;
	evidence.owner = hinted_owner;
	const std::size_t owner_index = static_cast<std::size_t>(hinted_owner);
	if (owner_index < evidence.ownership_scores.size())
		evidence.ownership_scores[owner_index] =
			std::max(evidence.ownership_scores[owner_index], 0.72f);
	evidence.ownership_confidence = std::max(evidence.ownership_confidence, 0.72f);
}

bool strong_full_mix_pitch_for_display(const FullMixDebugCandidate &debug, float min_level, float min_pitch,
				       float min_periodicity, float max_fit, float max_noise)
{
	if (debug.spectral_level < min_level || debug.pitch_confidence < min_pitch ||
	    debug.periodicity < min_periodicity)
		return false;

	const bool clean_enough = debug.harmonic_fit_error <= max_fit && debug.local_noise_level <= max_noise;
	const bool confident_pitch = debug.pitch_confidence >= min_pitch + 0.22f &&
				     debug.periodicity >= min_periodicity + 0.10f;
	return clean_enough || confident_pitch;
}

bool electronic_keyboard_alias_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner == InstrumentKind::Vocal || debug.midi < 48 || debug.midi > 96)
		return false;
	if (!strong_full_mix_pitch_for_display(debug, 0.24f, 0.16f, 0.46f, 0.78f, 0.72f))
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool octave_or_organ_stack =
		second >= 0.46f || fourth >= 0.10f || fifth >= 0.050f;
	const bool clean_sine_like_keyboard =
		second <= 0.16f && third <= 0.16f && fourth <= 0.080f &&
		debug.harmonic_fit_error <= 0.16f && debug.local_noise_level <= 0.18f &&
		debug.spectral_centroid <= 0.24f;
	const bool keyboard_score_hint = debug.keyboard_score >= 0.080f;
	const bool electronic_alias_shape =
		second >= 1.05f || fourth >= 0.30f || debug.harmonic_fit_error >= 3.0f;
	const bool rich_electronic_keyboard_alias =
		debug.owner == InstrumentKind::Other &&
		debug.pitch_confidence >= 0.48f &&
		debug.periodicity >= 0.72f &&
		debug.harmonic_fit_error <= 0.70f &&
		debug.local_noise_level <= 0.12f &&
		second >= 0.70f && third >= 0.20f && fourth >= 0.18f;
	if (debug.keyboard_score < 0.30f && !rich_electronic_keyboard_alias)
		return false;
	const bool neighboring_owner = (debug.owner == InstrumentKind::Other &&
					(keyboard_score_hint || clean_sine_like_keyboard ||
					 electronic_alias_shape)) ||
				       (debug.owner == InstrumentKind::Guitar &&
					debug.keyboard_score >= 0.28f &&
					(clean_sine_like_keyboard || fourth >= 0.10f || fifth >= 0.050f)) ||
				       (debug.owner == InstrumentKind::Ambiguous &&
					debug.keyboard_score >= 0.30f);
	return rich_electronic_keyboard_alias ||
	       (neighboring_owner && electronic_alias_shape &&
		(keyboard_score_hint || octave_or_organ_stack || clean_sine_like_keyboard));
}

bool shared_guitar_pitch_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner == InstrumentKind::Vocal || debug.midi < kGuitarMinMidi || debug.midi > kGuitarMaxMidi)
		return false;
	if (!strong_full_mix_pitch_for_display(debug, 0.30f, 0.24f, 0.54f, 0.44f, 0.62f))
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool plucked_or_stringy =
		(second >= 0.070f && third >= 0.012f) ||
		(fourth >= 0.035f && fifth >= 0.010f) ||
		debug.guitar_score >= 0.12f;
	const bool low_string_fundamental =
		debug.midi <= 59 && debug.pitch_confidence >= 0.48f &&
		debug.periodicity >= 0.58f &&
		debug.harmonic_fit_error <= 0.16f &&
		debug.local_noise_level <= 0.62f &&
		second >= 0.070f;
	const bool low_acoustic_guitar_from_other =
		debug.owner == InstrumentKind::Other &&
		debug.midi <= 52 &&
		debug.pitch_confidence >= 0.50f &&
		debug.periodicity >= 0.65f &&
		debug.harmonic_fit_error <= 0.20f &&
		debug.local_noise_level >= 0.18f &&
		debug.local_noise_level <= 0.70f &&
		second >= 0.25f && third >= 0.18f && fourth >= 0.050f;
	const bool keyboard_owned_pluck =
		debug.owner == InstrumentKind::Keyboard &&
		((debug.guitar_score >= 0.35f && (third >= 0.080f || fourth >= 0.035f)) ||
		 (debug.pitch_confidence >= 0.84f && debug.local_noise_level <= 0.060f &&
		  third >= 0.10f && second <= 0.18f));
	const bool neighboring_owner = low_acoustic_guitar_from_other ||
				       keyboard_owned_pluck ||
				       (debug.owner == InstrumentKind::Ambiguous &&
					debug.guitar_score >= 0.45f);
	return neighboring_owner && (plucked_or_stringy || low_string_fundamental);
}

bool noisy_other_owned_low_acoustic_guitar_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Other)
		return false;
	if (debug.midi < 40 || debug.midi > 56)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.other_score >= 0.78f &&
	       debug.guitar_score >= 0.12f &&
	       debug.guitar_score <= 0.24f &&
	       debug.spectral_level >= 0.14f &&
	       debug.spectral_level <= 0.38f &&
	       debug.pitch_confidence >= 0.055f &&
	       debug.periodicity >= 0.34f &&
	       debug.harmonic_fit_error >= 0.95f &&
	       debug.harmonic_fit_error <= 3.20f &&
	       debug.local_noise_level >= 0.12f &&
	       debug.local_noise_level <= 0.56f &&
	       debug.spectral_centroid >= 0.50f &&
	       debug.spectral_centroid <= 0.68f &&
	       debug.spectral_slope >= 0.95f &&
	       second >= 0.42f &&
	       third >= 2.50f &&
	       fourth >= 0.50f &&
	       fifth >= 0.20f;
}

bool shared_other_pitch_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner == InstrumentKind::Vocal || debug.midi < kOtherMinMidi || debug.midi > kOtherMaxMidi)
		return false;
	if (!strong_full_mix_pitch_for_display(debug, 0.34f, 0.28f, 0.56f, 0.36f, 0.74f))
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	if (debug.owner == InstrumentKind::Ambiguous)
		return false;
	if (debug.owner == InstrumentKind::Guitar && debug.other_score < 0.12f)
		return false;
	if (debug.owner == InstrumentKind::Keyboard && debug.other_score < 0.08f)
		return false;
	const bool sustained_or_bowed =
		debug.owner == InstrumentKind::Other ||
		debug.other_score >= 0.020f ||
		(second >= 0.055f && third >= 0.018f) ||
		(fourth >= 0.040f && debug.spectral_centroid >= 0.10f);
	return sustained_or_bowed;
}

bool shared_vocal_pitch_display_supported(const FullMixDebugCandidate &debug)
{
	const bool high_keyboard_vocal_octave_alias =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi > kVocalMaxMidi && debug.midi <= kVocalMaxMidi + 4 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.68f &&
		debug.harmonicity <= 0.040f &&
		debug.harmonic_fit_error <= 0.090f &&
		debug.spectral_centroid >= 0.007f &&
		debug.spectral_centroid <= 0.030f &&
		debug.local_noise_level <= 0.035f &&
		debug.harmonic_ratios[1] <= 0.020f &&
		debug.harmonic_ratios[2] <= 0.026f &&
		debug.harmonic_ratios[3] <= 0.008f &&
		debug.harmonic_ratios[4] <= 0.008f;
	if (debug.midi < kFullMixVocalMinMidi || (debug.midi > kVocalMaxMidi && !high_keyboard_vocal_octave_alias))
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	if (debug.owner == InstrumentKind::Vocal) {
		const bool measured_low_vocal_owner =
			debug.ownership_confidence >= 0.56f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.78f &&
			debug.harmonic_fit_error <= 0.025f &&
			debug.midi >= 55 &&
			debug.midi <= 60 &&
			second >= 0.27f &&
			second <= 0.29f &&
			third >= 0.090f &&
			third <= 0.096f;
		return debug.ownership_confidence >= 0.58f || measured_low_vocal_owner;
	}
	const bool keyboard_owned_pure_choir =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 69 && debug.midi <= 84 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity >= 0.68f &&
		debug.harmonic_fit_error <= 0.056f &&
		second <= 0.019f &&
		fourth <= 0.007f;
	const bool guitar_owned_synthetic_voice =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 55 && debug.midi <= 76 &&
		debug.spectral_level >= 0.80f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.80f &&
		debug.harmonic_fit_error <= 0.16f &&
		debug.local_noise_level >= 0.029f &&
		debug.local_noise_level <= 0.030f &&
		debug.other_score <= 0.001f &&
		second >= 0.265f;
	const bool guitar_owned_voice_lead =
		debug.owner == InstrumentKind::Guitar &&
		debug.ownership_confidence <= 0.78f &&
		debug.guitar_score >= 0.77f &&
		debug.spectral_level >= 0.94f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.045f &&
		second >= 0.30f &&
		third >= 0.10f &&
		fourth <= 0.012f &&
		fifth <= 0.010f;
	const bool guitar_owned_synth_voice_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.guitar_score >= 0.60f &&
		debug.keyboard_score <= 0.22f &&
		debug.spectral_level >= 0.80f &&
		debug.pitch_confidence >= 0.80f &&
		debug.periodicity >= 0.75f &&
		debug.harmonic_fit_error <= 0.085f &&
		third <= 0.030f &&
		fourth >= 0.050f &&
		fourth <= 0.095f;
	const bool guitar_owned_voice_lead_edge =
		debug.owner == InstrumentKind::Guitar &&
		debug.guitar_score >= 0.78f &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.055f &&
		second >= 0.40f &&
		third >= 0.20f &&
		fourth <= 0.030f &&
		fifth <= 0.015f;
	const bool guitar_owned_measured_voice_lead_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.guitar_score >= 0.78f &&
		debug.midi >= 55 &&
		debug.midi <= 69 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.89f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.055f &&
		second >= 0.33f &&
		second <= 0.50f &&
		third >= 0.090f &&
		third <= 0.19f &&
		fourth <= 0.026f &&
		fifth <= 0.021f;
	const bool guitar_owned_synth_voice_edge =
		debug.owner == InstrumentKind::Guitar &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.84f &&
		debug.harmonicity <= 0.81f &&
		debug.local_noise_level >= 0.020f &&
		second >= 0.62f &&
		third >= 0.060f &&
		third <= 0.090f &&
		fourth <= 0.030f &&
		fifth <= 0.018f;
	const bool guitar_owned_measured_synth_voice =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 55 && debug.midi <= 76 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.89f &&
		debug.periodicity >= 0.83f &&
		debug.harmonic_fit_error <= 0.10f &&
		debug.local_noise_level >= 0.020f &&
		debug.local_noise_level <= 0.036f &&
		debug.keyboard_score >= 0.10f &&
		debug.guitar_score >= 0.78f &&
		debug.guitar_score <= 0.90f &&
		second >= 0.36f &&
		second <= 0.56f &&
		third <= 0.060f &&
		fourth <= 0.040f &&
		fifth <= 0.020f;
	const bool ambiguous_choir_alias =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence <= 0.939f &&
		debug.local_noise_level >= 0.004f &&
		debug.vocal_score >= 0.388f &&
		debug.vocal_score <= 0.398f;
	const bool measured_ambiguous_acoustic_vocal_body =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.midi >= 60 &&
		debug.midi <= 76 &&
		debug.keyboard_score >= 0.61f &&
		debug.keyboard_score <= 0.63f &&
		debug.guitar_score <= 0.001f &&
		debug.vocal_score >= 0.37f &&
		debug.vocal_score <= 0.385f &&
		debug.other_score <= 0.001f &&
		debug.spectral_level >= 0.95f &&
		debug.pitch_confidence >= 0.93f &&
		debug.pitch_confidence <= 0.94f &&
		debug.periodicity >= 0.70f &&
		debug.periodicity <= 0.78f &&
		debug.harmonic_fit_error <= 0.040f &&
		debug.local_noise_level >= 0.020f &&
		debug.local_noise_level <= 0.040f &&
		second >= 0.045f &&
		second <= 0.065f &&
		third >= 0.030f &&
		third <= 0.055f &&
		fourth >= 0.020f &&
		fourth <= 0.045f &&
		fifth >= 0.020f &&
		fifth <= 0.055f;
	const bool ambiguous_rounded_ooh =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.spectral_level >= 0.35f &&
		debug.periodicity >= 0.86f &&
		debug.harmonic_fit_error <= 0.040f &&
		second >= 0.28f && second <= 0.34f &&
		third >= 0.24f && third <= 0.29f &&
		fourth >= 0.090f && fourth <= 0.13f &&
		fifth >= 0.040f && fifth <= 0.070f;
	const bool keyboard_owned_low_confidence_ooh_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.spectral_level >= 0.65f &&
		debug.pitch_confidence >= 0.62f &&
		debug.periodicity >= 0.90f &&
		debug.harmonic_fit_error <= 0.095f &&
		debug.harmonicity <= 0.88f &&
		debug.guitar_score >= 0.21f &&
		second >= 0.20f &&
		second <= 0.25f &&
		third >= 0.28f &&
		third <= 0.34f &&
		fourth >= 0.11f &&
		fourth <= 0.15f &&
		fifth >= 0.16f &&
		fifth <= 0.22f;
	if (keyboard_owned_pure_choir || guitar_owned_synthetic_voice || guitar_owned_voice_lead ||
	    guitar_owned_synth_voice_body || ambiguous_choir_alias || ambiguous_rounded_ooh ||
	    measured_ambiguous_acoustic_vocal_body ||
	    guitar_owned_voice_lead_edge || guitar_owned_synth_voice_edge ||
	    guitar_owned_measured_voice_lead_body || guitar_owned_measured_synth_voice ||
	    keyboard_owned_low_confidence_ooh_octave || high_keyboard_vocal_octave_alias)
		return true;

	if (debug.owner != InstrumentKind::Keyboard && debug.owner != InstrumentKind::Other)
		return false;
	const bool measured_dense_choir_vowel =
		debug.owner == InstrumentKind::Other &&
		debug.midi >= 57 &&
		debug.midi <= 62 &&
		debug.other_score >= 0.80f &&
		debug.spectral_level >= 0.42f &&
		debug.periodicity >= 0.69f &&
		debug.harmonic_fit_error <= 0.53f &&
		debug.spectral_centroid >= 0.40f &&
		debug.spectral_slope >= 0.80f &&
		debug.local_noise_level >= 0.20f &&
		third >= 1.15f &&
		((second >= 0.42f && second <= 0.46f && fourth <= 0.12f) ||
		 (second >= 1.20f && second <= 1.36f && fourth >= 0.35f && fourth <= 0.43f));
	const bool measured_other_owned_choir_partial =
		debug.owner == InstrumentKind::Other &&
		debug.midi >= 55 &&
		debug.midi <= 62 &&
		debug.spectral_level >= 0.80f &&
		debug.pitch_confidence >= 0.55f &&
		debug.periodicity >= 0.69f &&
		debug.harmonic_fit_error <= 0.53f &&
		debug.local_noise_level <= 0.269f &&
		debug.spectral_slope <= 0.993f &&
		third >= 0.957f &&
		fourth <= 0.16f &&
		fifth <= 0.13f;
	if (measured_dense_choir_vowel || measured_other_owned_choir_partial)
		return true;
	if (!strong_full_mix_pitch_for_display(debug, 0.70f, 0.70f, 0.64f, 0.34f, 0.72f))
		return false;

	const bool ultra_clean_choir_alias =
		second <= 0.075f &&
		third <= 0.006f &&
		fourth <= 0.006f &&
		debug.spectral_centroid <= 0.055f &&
		debug.spectral_slope <= 0.022f;
	const bool synthetic_voice_alias =
		second >= 0.10f &&
		debug.spectral_centroid >= 0.065f &&
		debug.spectral_slope >= 0.030f &&
		debug.spectral_slope <= 0.080f;
	const bool upper_clear_vowel =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 67 && debug.midi <= 84 &&
		second >= 0.045f && second <= 0.19f &&
		third <= 0.055f &&
		fourth <= 0.055f &&
		fifth <= 0.045f &&
		debug.pitch_confidence >= 0.84f &&
		debug.harmonic_fit_error <= 0.080f &&
		(ultra_clean_choir_alias || synthetic_voice_alias);
	const bool rounded_ooh_vowel =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 53 && debug.midi <= 71 &&
		second >= 0.24f && second <= 0.38f &&
		third <= 0.065f &&
		fourth >= 0.050f && fourth <= 0.105f &&
		fifth <= 0.085f &&
		debug.pitch_confidence >= 0.84f &&
		debug.harmonic_fit_error <= 0.090f;
	const bool bright_choir_vowel =
		debug.owner == InstrumentKind::Other &&
		debug.midi >= 53 && debug.midi <= 60 &&
		second >= 0.45f && second <= 0.58f &&
		third >= 0.88f && third <= 1.05f &&
		fourth >= 0.10f && fourth <= 0.20f &&
		debug.pitch_confidence >= 0.78f &&
		debug.harmonic_fit_error <= 0.28f &&
		debug.spectral_centroid >= 0.35f;
	const bool dense_low_choir_vowel =
		debug.owner == InstrumentKind::Other &&
		debug.midi >= 53 && debug.midi <= 60 &&
		debug.spectral_level >= 0.78f &&
		debug.pitch_confidence >= 0.55f &&
		debug.periodicity >= 0.69f &&
		debug.harmonic_fit_error >= 0.36f &&
		debug.local_noise_level >= 0.22f &&
		second >= 0.42f &&
		second <= 0.46f &&
		third >= 1.18f &&
		fourth <= 0.11f &&
		fifth <= 0.13f;
	const bool bright_keyboard_owned_choir =
		debug.owner == InstrumentKind::Keyboard &&
		debug.spectral_level >= 0.88f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.70f &&
		debug.harmonic_fit_error <= 0.070f &&
		debug.spectral_centroid <= 0.165f &&
		debug.local_noise_level <= 0.14f &&
		fourth >= 0.115f &&
		fourth <= 0.14f &&
		fifth <= 0.045f;
	const bool keyboard_owned_voice_ooh =
		debug.owner == InstrumentKind::Keyboard &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity >= 0.70f &&
		second >= 0.010f &&
		second <= 0.028f &&
		fifth <= 0.008f;
	const bool keyboard_owned_upper_choir =
		debug.owner == InstrumentKind::Keyboard &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.74f &&
		debug.harmonicity <= 0.21f &&
		debug.harmonic_fit_error <= 0.040f &&
		second >= 0.080f &&
		second <= 0.11f &&
		third <= 0.025f &&
		fourth >= 0.080f &&
		fourth <= 0.095f &&
		fifth <= 0.020f;
	const bool keyboard_owned_ooh_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.spectral_level >= 0.65f &&
		debug.pitch_confidence >= 0.62f &&
		debug.periodicity >= 0.90f &&
		debug.harmonicity <= 0.88f &&
		debug.guitar_score >= 0.21f &&
		second >= 0.20f &&
		second <= 0.25f &&
		third >= 0.28f &&
		third <= 0.34f &&
		fourth >= 0.11f &&
		fourth <= 0.15f &&
		fifth >= 0.16f &&
		fifth <= 0.22f;
	return upper_clear_vowel || rounded_ooh_vowel || bright_choir_vowel ||
	       dense_low_choir_vowel ||
	       bright_keyboard_owned_choir || keyboard_owned_voice_ooh ||
	       keyboard_owned_upper_choir || keyboard_owned_ooh_octave;
}

bool measured_vocal_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi - 12 < kFullMixVocalMinMidi || debug.midi - 12 > kVocalMaxMidi)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool vocal_owned_ooh_octave_alias =
		debug.owner == InstrumentKind::Vocal &&
		debug.midi >= 72 &&
		debug.midi <= 76 &&
		debug.vocal_score >= 0.70f &&
		debug.keyboard_score >= 0.30f &&
		debug.other_score >= 0.40f &&
		debug.spectral_level >= 0.34f &&
		debug.pitch_confidence >= 0.34f &&
		debug.periodicity >= 0.86f &&
		debug.harmonic_fit_error <= 0.055f &&
		second >= 0.30f &&
		second <= 0.34f &&
		third >= 0.26f &&
		third <= 0.34f &&
		fourth >= 0.10f &&
		fourth <= 0.18f &&
		fifth >= 0.045f &&
		fifth <= 0.11f;
	const bool ambiguous_voice_ooh_alias =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.keyboard_score >= 0.33f &&
		debug.spectral_level >= 0.35f &&
		debug.pitch_confidence <= 0.39f &&
		debug.periodicity >= 0.86f &&
		debug.harmonic_fit_error <= 0.050f &&
		second >= 0.28f &&
		second <= 0.34f &&
		third >= 0.24f &&
		third <= 0.30f &&
		fourth >= 0.090f &&
		fourth <= 0.13f &&
		fifth >= 0.040f &&
		fifth <= 0.070f;
	const bool ambiguous_choir_alias =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.88f &&
		debug.pitch_confidence <= 0.94f &&
		debug.periodicity >= 0.70f &&
		debug.periodicity <= 0.73f &&
		debug.harmonic_fit_error <= 0.060f &&
		((debug.vocal_score >= 0.38f && debug.vocal_score <= 0.40f) ||
		 (second <= 0.006f && third >= 0.060f && third <= 0.080f)) &&
		fourth <= 0.055f &&
		fifth <= 0.020f;
	const bool keyboard_ooh_alias =
		debug.owner == InstrumentKind::Keyboard &&
		debug.guitar_score >= 0.21f &&
		debug.spectral_level >= 0.65f &&
		debug.pitch_confidence >= 0.62f &&
		debug.periodicity >= 0.90f &&
		debug.harmonic_fit_error <= 0.095f &&
		second >= 0.20f &&
		second <= 0.25f &&
		third >= 0.28f &&
		third <= 0.34f &&
		fourth >= 0.11f &&
		fourth <= 0.15f &&
		fifth >= 0.16f &&
		fifth <= 0.22f;
	const bool keyboard_synth_voice_alias =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 72 &&
		debug.midi <= 76 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.92f &&
		debug.periodicity >= 0.70f &&
		debug.harmonicity <= 0.075f &&
		debug.harmonic_fit_error <= 0.050f &&
		debug.spectral_centroid <= 0.050f &&
		debug.local_noise_level <= 0.012f &&
		second >= 0.010f &&
		second <= 0.032f &&
		third >= 0.010f &&
		third <= 0.015f &&
		fourth >= 0.008f &&
		fourth <= 0.014f &&
		fifth <= 0.010f;
	const bool measured_keyboard_choir_bass_octave_alias =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi == 71 &&
		debug.keyboard_score >= 0.99f &&
		debug.guitar_score <= 0.001f &&
		debug.vocal_score <= 0.001f &&
		debug.other_score <= 0.001f &&
		debug.spectral_level >= 0.99f &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity >= 0.70f &&
		debug.harmonic_fit_error <= 0.040f &&
		debug.spectral_centroid <= 0.045f &&
		debug.spectral_slope <= 0.020f &&
		debug.local_noise_level <= 0.055f &&
		second >= 0.050f &&
		second <= 0.065f &&
		third <= 0.004f &&
		fourth <= 0.004f &&
		fifth <= 0.012f;
	const bool measured_keyboard_synth_voice_octave_alias =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi == 72 &&
		debug.keyboard_score >= 0.99f &&
		debug.guitar_score <= 0.001f &&
		debug.vocal_score <= 0.001f &&
		debug.other_score <= 0.001f &&
		debug.spectral_level >= 0.99f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.74f &&
		debug.harmonic_fit_error <= 0.020f &&
		debug.spectral_centroid <= 0.080f &&
		debug.spectral_slope <= 0.045f &&
		debug.local_noise_level <= 0.015f &&
		second >= 0.10f &&
		second <= 0.13f &&
		third >= 0.010f &&
		third <= 0.016f &&
		fourth >= 0.016f &&
		fourth <= 0.024f &&
		fifth <= 0.010f;
	const bool measured_ambiguous_voice_ooh_octave_alias =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.midi >= 72 &&
		debug.local_noise_level >= 0.076f &&
		debug.other_score >= 0.472f;
	return vocal_owned_ooh_octave_alias ||
	       ambiguous_voice_ooh_alias || ambiguous_choir_alias || keyboard_ooh_alias ||
	       keyboard_synth_voice_alias || measured_keyboard_choir_bass_octave_alias ||
	       measured_keyboard_synth_voice_octave_alias || measured_ambiguous_voice_ooh_octave_alias;
}

bool measured_vocal_octave_alias_priority_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Ambiguous &&
	       debug.midi >= 72 &&
	       debug.midi - 12 >= kFullMixVocalMinMidi &&
	       debug.local_noise_level >= 0.092f &&
	       debug.other_score >= 0.471f;
}

bool raw_supported_vocal_lower_octave_alias(const FullMixDebugCandidate &debug, int display_midi,
					    const std::array<float, kNoteProbeCount> *raw_powers)
{
	if (!raw_powers || display_midi != debug.midi - 12)
		return false;
	if (!measured_vocal_octave_alias_supported(debug))
		return false;

	const float lower_level = probe_level(*raw_powers, display_midi);
	const float upper_level = probe_level(*raw_powers, debug.midi);
	const float fifth_level = probe_level(*raw_powers, display_midi + 7);
	const float second_octave_level = probe_level(*raw_powers, display_midi + 24);
	if (lower_level <= 1.0e-6f)
		return false;

	const bool dominant_lower = lower_level >= std::max(upper_level * 6.0f, second_octave_level * 12.0f);
	const bool harmonic_context = fifth_level >= lower_level * 0.020f || upper_level >= lower_level * 0.010f;
	return dominant_lower && harmonic_context;
}

bool measured_keyboard_double_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Ambiguous)
		return false;
	if (debug.midi - 24 < kKeyboardMinMidi || debug.midi - 24 > kKeyboardMaxMidi)
		return false;

	const float third = debug.harmonic_ratios[2];
	const bool high_harpsichord_alias =
		debug.spectral_centroid <= 0.001f &&
		debug.local_noise_level >= 0.002f &&
		debug.pitch_confidence >= 0.932f;
	const bool clavinet_alias =
		third >= 0.002f &&
		third <= 0.003f;
	return high_harpsichord_alias || clavinet_alias;
}

bool measured_low_organ_keyboard_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi - 12 < kKeyboardMinMidi || debug.midi - 12 > kKeyboardMaxMidi)
		return false;
	if (debug.owner != InstrumentKind::Guitar && debug.owner != InstrumentKind::Ambiguous)
		return false;
	if (debug.midi < 47 || debug.midi > 50)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool measured_low_organ_alias =
		debug.spectral_level >= 0.116f &&
		debug.spectral_level <= 0.506f &&
		debug.spectral_centroid >= 0.100f &&
		debug.spectral_centroid <= 0.156f &&
		debug.local_noise_level >= 0.239f &&
		debug.local_noise_level <= 0.317f &&
		debug.pitch_confidence >= 0.091f &&
		debug.pitch_confidence <= 0.411f &&
		debug.periodicity >= 0.64f &&
		debug.harmonic_fit_error <= 0.070f &&
		fourth <= 0.012f &&
		fifth >= 0.014f &&
		fifth <= 0.039f;
	const bool measured_b1_organ_alias =
		debug.midi == 47 &&
		debug.spectral_level >= 0.38f &&
		debug.spectral_level <= 0.51f &&
		debug.spectral_centroid >= 0.060f &&
		debug.spectral_centroid <= 0.105f &&
		debug.local_noise_level >= 0.30f &&
		debug.local_noise_level <= 0.33f &&
		debug.pitch_confidence >= 0.30f &&
		debug.pitch_confidence <= 0.42f &&
		debug.periodicity >= 0.64f &&
		debug.periodicity <= 0.68f &&
		debug.harmonic_fit_error <= 0.022f &&
		second >= 0.075f &&
		second <= 0.15f &&
		third <= 0.070f &&
		fourth <= 0.013f &&
		fifth >= 0.007f &&
		fifth <= 0.031f;
	return measured_low_organ_alias || measured_b1_organ_alias;
}

bool measured_guitar_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard)
		return false;
	if (debug.midi - 12 < kGuitarMinMidi || debug.midi - 12 > kGuitarMaxMidi)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool low_nylon_octave_body =
		debug.keyboard_score >= 0.82f &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.78f &&
		debug.periodicity >= 0.78f &&
		debug.harmonic_fit_error <= 0.20f &&
		fourth >= 0.50f &&
		second >= 0.20f &&
		second <= 0.34f &&
		third <= 0.070f &&
		fifth <= 0.030f;
	const bool low_steel_octave_body =
		debug.ownership_confidence <= 0.84f &&
		debug.keyboard_score >= 0.82f &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.84f &&
		debug.periodicity >= 0.72f &&
		debug.harmonic_fit_error <= 0.055f &&
		second >= 0.18f &&
		second <= 0.24f &&
		third <= 0.085f &&
		fourth >= 0.090f &&
		fourth <= 0.13f &&
		fifth >= 0.090f &&
		fifth <= 0.14f;
	const bool high_nylon_octave_body =
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity <= 0.84f &&
		debug.harmonic_fit_error <= 0.090f &&
		second >= 0.26f &&
		third <= 0.001f &&
		fourth <= 0.001f &&
		fifth <= 0.001f;
	const bool pure_high_nylon_octave_body =
		debug.midi >= 76 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.73f &&
		debug.periodicity <= 0.80f &&
		debug.harmonic_fit_error <= 0.070f &&
		second >= 0.090f &&
		second <= 0.32f &&
		third <= 0.002f &&
		fourth <= 0.002f &&
		fifth <= 0.002f;
	const bool clean_jazz_octave_body =
		debug.midi >= 76 &&
		debug.midi <= 88 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.73f &&
		debug.periodicity <= 0.86f &&
		debug.harmonic_fit_error <= 0.070f &&
		second >= 0.060f &&
		second <= 0.25f &&
		third >= 0.080f &&
		third <= 0.23f &&
		fourth <= 0.003f &&
		fifth <= 0.003f;
	const bool mid_jazz_octave_body =
		debug.spectral_level >= 0.65f &&
		debug.spectral_level <= 0.95f &&
		debug.pitch_confidence <= 0.81f &&
		debug.periodicity >= 0.88f &&
		debug.harmonic_fit_error >= 0.21f &&
		debug.harmonic_fit_error <= 0.26f &&
		third >= 0.54f &&
		third <= 0.74f &&
		fourth <= 0.025f &&
		fifth <= 0.035f;
	return low_nylon_octave_body || low_steel_octave_body ||
	       high_nylon_octave_body || pure_high_nylon_octave_body ||
	       clean_jazz_octave_body || mid_jazz_octave_body;
}

bool ambiguous_high_guitar_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Ambiguous)
		return false;
	if (debug.midi - 12 < kGuitarMinMidi || debug.midi - 12 > kGuitarMaxMidi)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const bool clean_high_string_alias =
		debug.ownership_confidence <= 0.001f &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.89f &&
		debug.periodicity >= 0.80f &&
		debug.local_noise_level <= 0.003f &&
		second >= 0.31f &&
		third <= 0.001f &&
		fourth <= 0.001f;
	const bool driven_high_string_alias =
		debug.ownership_confidence <= 0.001f &&
		debug.pitch_confidence >= 0.40f &&
		debug.periodicity >= 0.80f &&
		debug.harmonic_fit_error >= 0.037f &&
		debug.spectral_level <= 0.96f &&
		second >= 0.30f &&
		third <= 0.001f &&
		fourth <= 0.001f;
	return clean_high_string_alias || driven_high_string_alias;
}

bool other_owned_distorted_guitar_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Other)
		return false;
	if (debug.midi - 12 < kGuitarMinMidi || debug.midi - 12 > kGuitarMaxMidi)
		return false;

	return debug.midi >= 67 &&
	       debug.other_score >= 0.80f &&
	       debug.periodicity >= 0.80f &&
	       debug.harmonic_fit_error >= 0.40f &&
	       debug.spectral_centroid >= 0.45f &&
	       debug.spectral_slope >= 1.0f &&
	       debug.local_noise_level <= 0.010f &&
	       debug.harmonic_ratios[1] >= 0.85f &&
	       debug.harmonic_ratios[2] >= 0.883f &&
	       debug.harmonic_ratios[3] >= 0.60f;
}

bool other_owned_noisy_distorted_guitar_octave_up_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Other)
		return false;
	if (debug.midi + 12 < kGuitarMinMidi || debug.midi + 12 > kGuitarMaxMidi)
		return false;

	const float second = debug.harmonic_ratios[1];
	return debug.midi >= 58 &&
	       debug.midi <= 64 &&
	       debug.other_score >= 0.74f &&
	       debug.guitar_score >= 0.18f &&
	       debug.guitar_score <= 0.30f &&
	       debug.spectral_level >= 0.12f &&
	       debug.spectral_level <= 0.24f &&
	       debug.pitch_confidence <= 0.055f &&
	       debug.periodicity >= 0.12f &&
	       debug.periodicity <= 0.24f &&
	       debug.harmonic_fit_error >= 800.0f &&
	       debug.local_noise_level >= 1.0f &&
	       debug.spectral_centroid >= 0.38f &&
	       debug.spectral_centroid <= 0.50f &&
	       second >= 100.0f;
}

bool other_owned_overdrive_guitar_body_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Other)
		return false;
	if (debug.midi < 57 || debug.midi > 59)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.other_score >= 0.78f &&
	       debug.guitar_score >= 0.070f &&
	       debug.guitar_score <= 0.17f &&
	       debug.spectral_level >= 0.75f &&
	       debug.spectral_level <= 0.90f &&
	       debug.pitch_confidence >= 0.68f &&
	       debug.pitch_confidence <= 0.78f &&
	       debug.periodicity >= 0.84f &&
	       debug.periodicity <= 0.92f &&
	       debug.harmonic_fit_error >= 0.10f &&
	       debug.harmonic_fit_error <= 0.20f &&
	       debug.spectral_centroid >= 0.40f &&
	       debug.spectral_centroid <= 0.50f &&
	       debug.spectral_slope >= 0.70f &&
	       debug.spectral_slope <= 0.90f &&
	       debug.local_noise_level >= 0.070f &&
	       debug.local_noise_level <= 0.12f &&
	       second >= 0.50f &&
	       second <= 0.60f &&
	       third >= 0.45f &&
	       third <= 0.55f &&
	       fourth >= 0.22f &&
	       fourth <= 0.30f &&
	       fifth >= 0.45f &&
	       fifth <= 0.56f;
}

bool measured_other_owned_electric_piano_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Other &&
	       debug.midi >= 52 &&
	       debug.midi <= 64 &&
	       debug.guitar_score >= 0.118f &&
	       debug.other_score >= 0.881f &&
	       debug.spectral_level >= 0.90f &&
	       debug.pitch_confidence >= 0.88f &&
	       debug.periodicity >= 0.89f &&
	       debug.harmonic_fit_error >= 0.080f &&
	       debug.harmonic_fit_error <= 0.105f &&
	       debug.harmonic_ratios[1] >= 0.75f;
}

bool measured_other_owned_electric_piano_octave_up_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Other)
		return false;
	if (debug.midi + 12 < kKeyboardMinMidi || debug.midi + 12 > kKeyboardMaxMidi)
		return false;

	return debug.other_score >= 0.70f &&
	       debug.other_score <= 0.86f &&
	       debug.guitar_score >= 0.18f &&
	       debug.guitar_score <= 0.28f &&
	       debug.vocal_score <= 0.001f &&
	       debug.keyboard_score <= 0.001f &&
	       debug.harmonic_fit_error >= 1000.0f &&
	       debug.harmonicity >= 3000.0f &&
	       debug.harmonic_ratios[1] >= 3000.0f &&
	       debug.harmonic_ratios[3] >= 100.0f &&
	       debug.spectral_centroid >= 0.40f &&
	       debug.spectral_centroid <= 0.48f &&
	       debug.spectral_slope <= 0.050f;
}

bool measured_low_pure_keyboard_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Ambiguous)
		return false;
	if (debug.midi < 96 || debug.midi > kKeyboardMaxMidi)
		return false;

	return debug.spectral_level >= 0.98f &&
	       debug.pitch_confidence >= 0.90f &&
	       debug.periodicity >= 0.68f &&
	       debug.periodicity <= 0.72f &&
	       debug.harmonic_fit_error >= 0.045f &&
	       debug.harmonic_fit_error <= 0.070f &&
	       debug.harmonicity <= 0.010f &&
	       debug.spectral_centroid <= 0.010f &&
	       debug.spectral_slope <= 0.001f &&
	       debug.local_noise_level <= 0.020f &&
	       debug.harmonic_ratios[1] <= 0.012f &&
	       debug.harmonic_ratios[2] <= 0.001f &&
	       debug.harmonic_ratios[3] <= 0.001f &&
	       debug.harmonic_ratios[4] <= 0.001f;
}

bool keyboard_owned_synth_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard)
		return false;
	if (debug.spectral_level < 0.90f || debug.pitch_confidence < 0.70f)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool square_lead =
		debug.keyboard_score >= 0.80f &&
		third >= 0.095f &&
		fourth <= 0.033f &&
		fifth >= 0.107f;
	const bool sparse_square_lead =
		debug.keyboard_score >= 0.80f &&
		third >= 0.095f &&
		fourth <= 0.005f &&
		fifth >= 0.037f &&
		debug.pitch_confidence <= 0.945f;
	const bool low_period_square_lead =
		debug.keyboard_score >= 0.80f &&
		debug.periodicity <= 0.652f &&
		debug.local_noise_level <= 0.384f;
	const bool high_warm_pad =
		debug.keyboard_score >= 0.80f &&
		debug.harmonic_ratios[3] >= 0.30f &&
		debug.harmonic_ratios[3] <= 0.37f &&
		debug.periodicity >= 0.82f;
	const bool sparse_chiff_pad =
		third >= 0.004f &&
		third <= 0.007f &&
		debug.pitch_confidence <= 0.928f &&
		fifth >= 0.001f;
	const bool choir_pad =
		debug.ownership_confidence <= 0.75f &&
		debug.harmonic_fit_error <= 0.022f &&
		second >= 0.16f &&
		second <= 0.24f &&
		third <= 0.070f &&
		fourth <= 0.030f &&
		fifth <= 0.012f;
	const bool soft_halo_pad =
		debug.ownership_confidence <= 0.73f &&
		debug.harmonic_fit_error <= 0.024f &&
		second >= 0.12f &&
		second <= 0.26f &&
		third <= 0.13f &&
		fourth <= 0.035f &&
		fifth <= 0.040f;
	const bool bowed_pad_tail =
		debug.spectral_centroid <= 0.427f &&
		fifth >= 0.640f;
	const bool mid_bowed_pad_tail =
		debug.keyboard_score >= 0.74f &&
		debug.spectral_centroid >= 0.38f &&
		debug.harmonicity <= 1.063f &&
		fifth >= 0.60f;
	const bool calliope_pad_body =
		debug.spectral_centroid <= 0.427f &&
		debug.harmonicity >= 1.02f &&
		debug.harmonic_fit_error <= 0.28f &&
		third >= 0.045f;
	const bool low_thin_square_lead =
		debug.keyboard_score >= 0.80f &&
		debug.periodicity >= 0.64f &&
		debug.periodicity <= 0.72f &&
		debug.harmonic_fit_error <= 0.10f &&
		second <= 0.005f &&
		third >= 0.16f &&
		third <= 0.19f &&
		fourth <= 0.005f &&
		fifth >= 0.012f &&
		fifth <= 0.026f;
	const bool bright_saw_lead =
		debug.keyboard_score >= 0.84f &&
		debug.midi >= 72 &&
		debug.midi <= 84 &&
		debug.pitch_confidence >= 0.94f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.075f &&
		debug.spectral_centroid >= 0.24f &&
		debug.spectral_centroid <= 0.40f &&
		third >= 0.045f &&
		fourth >= 0.12f &&
		fifth >= 0.09f;
	const bool breathy_voice_lead =
		debug.keyboard_score >= 0.90f &&
		debug.midi >= 60 &&
		debug.midi <= 84 &&
		debug.pitch_confidence >= 0.92f &&
		debug.periodicity >= 0.76f &&
		debug.harmonic_fit_error <= 0.025f &&
		debug.local_noise_level <= 0.012f &&
		second >= 0.14f &&
		second <= 0.20f &&
		third <= 0.060f &&
		fourth <= 0.003f &&
		fifth <= 0.004f;
	const bool measured_keyboard_synth_lead =
		debug.midi >= 36 &&
		debug.midi <= 84 &&
		debug.pitch_confidence >= 0.76f &&
		debug.periodicity >= 0.65f &&
		debug.harmonic_fit_error <= 0.13f &&
		debug.local_noise_level >= 0.007f &&
		debug.local_noise_level <= 0.40f &&
		debug.spectral_centroid <= 0.28f &&
		second <= 0.27f &&
		third <= 0.33f &&
		fourth <= 0.085f &&
		fifth <= 0.14f;
	const bool new_age_pad =
		debug.harmonic_fit_error >= 0.075f &&
		debug.guitar_score >= 0.142f &&
		debug.keyboard_score >= 0.792f &&
		debug.local_noise_level >= 0.081f &&
		third >= 0.063f;
	return square_lead || sparse_square_lead || low_period_square_lead ||
	       high_warm_pad || sparse_chiff_pad ||
	       choir_pad || soft_halo_pad || bowed_pad_tail ||
	       mid_bowed_pad_tail || calliope_pad_body ||
	       low_thin_square_lead || bright_saw_lead || breathy_voice_lead ||
	       measured_keyboard_synth_lead || new_age_pad;
}

bool measured_keyboard_synth_other_priority_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Keyboard &&
	       debug.midi <= 60 &&
	       debug.guitar_score >= 0.142f &&
	       debug.keyboard_score >= 0.831f &&
	       debug.local_noise_level >= 0.12f &&
	       debug.spectral_slope >= 0.272f;
}

bool keyboard_owned_string_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard)
		return false;
	if (debug.spectral_level < 0.70f || debug.pitch_confidence < 0.66f || debug.periodicity < 0.66f)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool contrabass_body =
		debug.midi >= 36 &&
		debug.midi <= 52 &&
		debug.harmonic_fit_error <= 0.060f &&
		debug.spectral_slope <= 0.18f &&
		second >= 0.045f &&
		second <= 0.11f &&
		third >= 0.060f &&
		third <= 0.10f &&
		fourth <= 0.030f &&
		fifth >= 0.018f &&
		fifth <= 0.070f;
	const bool noisy_pizzicato_body =
		debug.midi >= 48 &&
		debug.midi <= 55 &&
		debug.harmonic_fit_error <= 0.085f &&
		debug.local_noise_level >= 0.28f &&
		second >= 0.09f &&
		second <= 0.20f &&
		third <= 0.080f &&
		fourth >= 0.20f &&
		fourth <= 0.26f &&
		fifth <= 0.055f;
	const bool tremolo_string_body =
		debug.midi >= 52 &&
		debug.midi <= 60 &&
		debug.harmonic_fit_error <= 0.14f &&
		debug.local_noise_level >= 0.16f &&
		debug.local_noise_level <= 0.23f &&
		second >= 0.10f &&
		second <= 0.14f &&
		third >= 0.36f &&
		third <= 0.42f &&
		fourth >= 0.12f &&
		fourth <= 0.17f &&
		fifth <= 0.045f;
	const bool sparse_harp_body =
		debug.midi >= 60 &&
		debug.midi <= 72 &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity >= 0.70f &&
		debug.harmonic_fit_error <= 0.060f &&
		debug.local_noise_level <= 0.030f &&
		debug.spectral_centroid <= 0.090f &&
		second <= 0.010f &&
		third >= 0.055f &&
		third <= 0.080f &&
		fourth <= 0.010f &&
		fifth <= 0.010f;
	const bool high_pizzicato_body =
		debug.midi >= 72 &&
		debug.midi <= 84 &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.70f &&
		debug.harmonic_fit_error <= 0.060f &&
		debug.local_noise_level <= 0.13f &&
		second >= 0.050f &&
		second <= 0.095f &&
		third <= 0.12f &&
		fourth <= 0.065f &&
		fifth <= 0.012f;
	const bool string_ensemble_body =
		debug.midi >= 52 &&
		debug.midi <= 60 &&
		debug.keyboard_score >= 0.99f &&
		debug.pitch_confidence >= 0.83f &&
		debug.periodicity >= 0.79f &&
		debug.harmonic_fit_error >= 0.13f &&
		debug.harmonic_fit_error <= 0.15f &&
		debug.spectral_slope >= 0.54f &&
		third >= 0.40f &&
		fourth >= 0.15f;
	return contrabass_body || noisy_pizzicato_body || tremolo_string_body ||
	       sparse_harp_body || high_pizzicato_body || string_ensemble_body;
}

bool keyboard_owned_piano_chord_other_spillover(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.keyboard_score >= 0.84f &&
	       debug.guitar_score <= 0.16f &&
	       debug.vocal_score <= 0.02f &&
	       debug.other_score <= 0.02f &&
	       debug.spectral_level >= 0.95f &&
	       debug.pitch_confidence >= 0.80f &&
	       debug.periodicity >= 0.66f &&
	       debug.harmonic_fit_error <= 0.055f &&
	       debug.spectral_centroid <= 0.16f &&
	       second >= 0.10f &&
	       second <= 0.17f &&
	       third >= 0.035f &&
	       third <= 0.17f &&
	       fourth <= 0.020f &&
	       fifth <= 0.020f;
}

bool measured_ambiguous_string_other_priority_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Ambiguous)
		return false;

	const bool noisy_string_tail =
		debug.harmonic_fit_error >= 0.016f &&
		debug.local_noise_level >= 0.122f &&
		debug.harmonic_ratios[3] >= 0.032f &&
		debug.harmonic_ratios[4] <= 0.014f;
	const bool low_contrabass_tail =
		debug.harmonic_fit_error >= 0.017f &&
		debug.guitar_score <= 0.001f &&
		debug.local_noise_level >= 0.122f &&
		debug.periodicity >= 0.750f;
	return noisy_string_tail || low_contrabass_tail;
}

bool measured_guitar_string_other_priority_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Guitar)
		return false;

	const bool measured_synth_string_body =
		debug.local_noise_level >= 0.10f &&
		debug.keyboard_score >= 0.127f &&
		debug.keyboard_score <= 0.140f;
	const bool measured_vocal_blend_string_body =
		debug.local_noise_level >= 0.08f &&
		debug.periodicity >= 0.810f &&
		debug.vocal_score >= 0.220f;
	const bool measured_soft_synth_string_body =
		debug.local_noise_level >= 0.08f &&
		debug.keyboard_score >= 0.088f &&
		debug.keyboard_score <= 0.090f &&
		debug.vocal_score >= 0.210f &&
		debug.periodicity >= 0.824f;
	const bool measured_low_synth_string_body =
		debug.midi == 48 &&
		debug.keyboard_score >= 0.10f &&
		debug.local_noise_level >= 0.29f &&
		debug.harmonic_ratios[1] >= 0.42f &&
		debug.harmonic_ratios[4] >= 0.060f;
	return measured_synth_string_body || measured_vocal_blend_string_body ||
	       measured_soft_synth_string_body || measured_low_synth_string_body;
}

bool guitar_owned_low_contrabass_other_display_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Guitar &&
	       debug.midi <= 40 &&
	       debug.harmonic_ratios[2] <= 0.076f;
}

bool guitar_owned_synth_strings_other_display_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Guitar &&
	       debug.keyboard_score >= 0.128f &&
	       debug.keyboard_score <= 0.139f;
}

bool guitar_owned_high_string_ensemble_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Guitar)
		return false;
	if (debug.midi < 67 || debug.midi > 76)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.keyboard_score <= 0.14f &&
	       debug.guitar_score >= 0.64f &&
	       debug.vocal_score <= 0.24f &&
	       debug.other_score <= 0.001f &&
	       debug.spectral_level >= 0.95f &&
	       debug.pitch_confidence >= 0.95f &&
	       debug.periodicity >= 0.81f &&
	       debug.harmonic_fit_error <= 0.055f &&
	       debug.local_noise_level <= 0.025f &&
	       debug.spectral_centroid >= 0.14f &&
	       debug.spectral_centroid <= 0.21f &&
	       debug.spectral_slope >= 0.080f &&
	       debug.spectral_slope <= 0.14f &&
	       second >= 0.25f &&
	       second <= 0.46f &&
	       third >= 0.060f &&
	       third <= 0.13f &&
	       fourth <= 0.055f &&
	       fifth <= 0.030f;
}

bool guitar_owned_measured_string_other_display_supported(const FullMixDebugCandidate &debug)
{
	return guitar_owned_low_contrabass_other_display_supported(debug) ||
	       guitar_owned_synth_strings_other_display_supported(debug) ||
	       guitar_owned_high_string_ensemble_other_display_supported(debug) ||
	       measured_guitar_string_other_priority_supported(debug);
}

bool measured_vocal_synth_other_priority_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Vocal &&
	       debug.keyboard_score >= 0.162f &&
	       debug.vocal_score >= 0.837f;
}

bool measured_guitar_synth_other_priority_supported(const FullMixDebugCandidate &debug)
{
	return debug.owner == InstrumentKind::Guitar &&
	       debug.guitar_score >= 0.652f &&
	       debug.vocal_score >= 0.226f;
}

bool measured_vocal_synth_other_octave_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Vocal)
		return false;
	if (debug.midi - 12 < kOtherMinMidi || debug.midi - 12 > kOtherMaxMidi)
		return false;

	return debug.midi >= 84 &&
	       debug.vocal_score >= 0.99f &&
	       debug.pitch_confidence >= 0.93f &&
	       debug.periodicity >= 0.71f &&
	       debug.harmonic_fit_error <= 0.045f &&
	       debug.spectral_centroid <= 0.020f &&
	       debug.spectral_slope <= 0.006f &&
	       debug.harmonic_ratios[1] <= 0.040f &&
	       debug.harmonic_ratios[2] <= 0.004f;
}

bool measured_guitar_synth_other_octave_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Guitar)
		return false;
	if (debug.midi - 12 < kOtherMinMidi || debug.midi - 12 > kOtherMaxMidi)
		return false;

	const bool high_chiff_lead =
		debug.midi >= 84 &&
		debug.guitar_score >= 0.99f &&
		debug.spectral_level <= 0.55f &&
		debug.pitch_confidence <= 0.50f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.045f &&
		debug.harmonic_ratios[1] >= 0.32f &&
		debug.harmonic_ratios[1] <= 0.38f &&
		debug.harmonic_ratios[2] <= 0.11f &&
		debug.harmonic_ratios[3] <= 0.004f;
	const bool low_metallic_pad =
		debug.midi >= 48 &&
		debug.midi <= 52 &&
		debug.guitar_score >= 0.74f &&
		debug.keyboard_score >= 0.24f &&
		debug.local_noise_level >= 0.29f &&
		debug.periodicity <= 0.74f &&
		debug.harmonic_fit_error <= 0.055f;
	return high_chiff_lead || low_metallic_pad;
}

bool measured_low_acoustic_string_other_octave_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard && debug.owner != InstrumentKind::Ambiguous)
		return false;
	if (debug.midi - 12 < kOtherMinMidi || debug.midi - 12 > kOtherMaxMidi)
		return false;
	if (debug.midi < 48 || debug.midi > 55)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.spectral_level >= 0.10f &&
	       debug.spectral_level <= 0.34f &&
	       debug.pitch_confidence >= 0.085f &&
	       debug.periodicity >= 0.64f &&
	       debug.harmonic_fit_error <= 0.080f &&
	       debug.local_noise_level >= 0.20f &&
	       debug.local_noise_level <= 0.42f &&
	       debug.spectral_centroid >= 0.050f &&
	       debug.spectral_centroid <= 0.15f &&
	       debug.spectral_slope <= 0.070f &&
	       second >= 0.10f &&
	       second <= 0.42f &&
	       third <= 0.065f &&
	       fourth <= 0.055f &&
	       fifth <= 0.012f;
}

bool measured_other_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi - 12 < kOtherMinMidi || debug.midi - 12 > kOtherMaxMidi)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool low_keyboard_synth_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 43 &&
		debug.midi <= 60 &&
		keyboard_owned_synth_other_display_supported(debug) &&
		debug.harmonic_fit_error <= 0.13f &&
		debug.spectral_slope >= 0.060f;
	const bool low_keyboard_string_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 43 &&
		debug.midi <= 60 &&
		keyboard_owned_string_other_display_supported(debug);
	const bool ambiguous_high_string_octave =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.midi >= 84 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.93f &&
		debug.periodicity >= 0.74f &&
		debug.harmonic_fit_error <= 0.050f &&
		debug.local_noise_level >= 0.015f &&
		second >= 0.18f &&
		second <= 0.23f &&
		third <= 0.002f &&
		fourth <= 0.002f &&
		fifth <= 0.002f;
	const bool low_ambiguous_string_octave =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.midi >= 43 &&
		debug.midi <= 52 &&
		debug.spectral_level >= 0.78f &&
		debug.pitch_confidence >= 0.58f &&
		debug.periodicity >= 0.74f &&
		 debug.harmonic_fit_error <= 0.27f &&
		second >= 0.09f &&
		second <= 0.30f &&
		third >= 0.18f &&
		fourth >= 0.12f;
	const bool measured_ambiguous_contrabass_octave =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.harmonic_fit_error >= 0.017f &&
		second >= 0.084f &&
		debug.periodicity >= 0.666f &&
		debug.periodicity <= 0.685f;
	const bool measured_ambiguous_cello_octave =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.local_noise_level >= 0.122f &&
		second >= 0.084f &&
		fourth >= 0.247f &&
		debug.periodicity <= 0.773f;
	return low_keyboard_synth_octave || low_keyboard_string_octave ||
	       ambiguous_high_string_octave || low_ambiguous_string_octave ||
	       measured_ambiguous_contrabass_octave || measured_ambiguous_cello_octave ||
	       measured_low_acoustic_string_other_octave_supported(debug);
}

bool measured_other_weak_octave_alias_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi - 12 < kOtherMinMidi || debug.midi - 12 > kOtherMaxMidi)
		return false;
	if (debug.owner != InstrumentKind::Ambiguous)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float fourth = debug.harmonic_ratios[3];
	return debug.local_noise_level >= 0.122f &&
	       second >= 0.084f &&
	       fourth >= 0.247f &&
	       debug.periodicity <= 0.773f;
}

bool sustained_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi < 52 || debug.midi > 84)
		return false;
	if (debug.spectral_level < 0.72f || debug.pitch_confidence < 0.70f || debug.periodicity < 0.72f)
		return false;
	if (debug.local_noise_level > 0.13f || debug.harmonic_fit_error > 0.20f)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool wind_like_mid_harmonics =
		second >= 0.20f && second <= 0.48f &&
		third >= 0.045f && third <= 0.18f &&
		fourth <= 0.16f && fifth <= 0.10f &&
		debug.spectral_centroid >= 0.12f && debug.spectral_centroid <= 0.25f &&
		debug.spectral_slope >= 0.065f && debug.spectral_slope <= 0.24f;
	const bool reed_like_odd_harmonics =
		second >= 0.08f && second <= 0.24f &&
		third >= 0.09f && third <= 0.24f &&
		fourth <= 0.16f && fifth <= 0.10f &&
		debug.spectral_centroid >= 0.11f && debug.spectral_centroid <= 0.25f;
	const bool pure_wind_like =
		debug.midi >= 65 &&
		second <= 0.16f && third <= 0.30f && fourth <= 0.30f && fifth <= 0.12f &&
		debug.harmonicity <= 0.55f &&
		debug.harmonic_fit_error <= 0.12f &&
		debug.local_noise_level <= 0.020f &&
		debug.spectral_centroid <= 0.24f &&
		debug.spectral_slope <= 0.36f;
	const bool bright_reed_like =
		second <= 0.24f &&
		third >= 0.20f && third <= 0.60f &&
		fourth <= 0.32f && fifth <= 0.16f &&
		debug.harmonic_fit_error <= 0.20f &&
		debug.spectral_centroid >= 0.16f && debug.spectral_centroid <= 0.34f &&
		debug.spectral_slope >= 0.24f && debug.spectral_slope <= 0.72f;
	const bool hollow_reed_like =
		debug.midi >= 68 &&
		second >= 0.18f && second <= 0.48f &&
		third <= 0.070f &&
		fourth <= 0.050f &&
		fifth <= 0.018f &&
		debug.harmonic_fit_error <= 0.16f &&
		debug.local_noise_level <= 0.035f &&
		debug.spectral_centroid >= 0.080f && debug.spectral_centroid <= 0.24f &&
		debug.spectral_slope <= 0.16f;
	return wind_like_mid_harmonics || reed_like_odd_harmonics || pure_wind_like || bright_reed_like ||
	       hollow_reed_like;
}

bool hollow_reed_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (!sustained_other_display_supported(debug))
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	return debug.midi >= 68 &&
	       second >= 0.18f && second <= 0.48f &&
	       third <= 0.070f &&
	       fourth <= 0.050f &&
	       fifth <= 0.018f &&
	       debug.spectral_centroid >= 0.080f && debug.spectral_centroid <= 0.24f &&
	       debug.spectral_slope <= 0.16f;
}

bool guitar_owned_reed_other_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Guitar && debug.owner != InstrumentKind::Ambiguous)
		return false;

	const float second = debug.harmonic_ratios[1];
	const float third = debug.harmonic_ratios[2];
	const float fourth = debug.harmonic_ratios[3];
	const float fifth = debug.harmonic_ratios[4];
	const bool octave_dominant_reed =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 60 && debug.midi <= 84 &&
		debug.spectral_level >= 0.33f &&
		debug.periodicity >= 0.62f &&
		debug.local_noise_level <= 0.012f &&
		second >= 1.10f &&
		third >= 0.24f &&
		fourth <= 0.09f &&
		debug.spectral_centroid >= 0.28f &&
		debug.spectral_centroid <= 0.42f &&
		debug.spectral_slope >= 0.10f &&
		debug.spectral_slope <= 0.32f;
	const bool octave_rich_reed =
		debug.midi >= 72 && debug.midi <= 84 &&
		debug.spectral_level >= 0.62f &&
		debug.pitch_confidence >= 0.52f &&
		debug.periodicity >= 0.78f &&
		debug.local_noise_level <= 0.012f &&
		debug.harmonic_fit_error <= 0.46f &&
		second >= 0.50f &&
		second <= 1.60f &&
		third <= 0.14f &&
		fourth <= 0.040f &&
		fifth <= 0.025f &&
		debug.spectral_centroid >= 0.14f &&
		debug.spectral_centroid <= 0.30f &&
		debug.spectral_slope <= 0.09f;
	return octave_dominant_reed || octave_rich_reed || hollow_reed_other_display_supported(debug);
}

float ownership_global_note_level(const FullMixOwnership &ownership, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return 0.0f;
	const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
	return std::clamp(ownership.global_note_levels[index], 0.0f, 1.0f);
}

bool keyboard_owned_other_mirror_blocked_in_chord_context(const FullMixOwnership &ownership,
							 const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Keyboard ||
	    count_owned_notes(ownership.keyboard) < 2 ||
	    debug.keyboard_score < 0.80f)
		return false;

	return keyboard_owned_piano_chord_other_spillover(debug) ||
	       (!keyboard_owned_synth_other_display_supported(debug) &&
		!keyboard_owned_string_other_display_supported(debug) &&
		!measured_keyboard_synth_other_priority_supported(debug));
}

bool clean_owned_chord_context_for_row(const FullMixOwnership &ownership, const FullMixDebugCandidate &debug,
				       FullMixDisplayRow row)
{
	if (row == FullMixDisplayRow::Other) {
		if (count_owned_notes(ownership.other) > 0)
			return false;
		if (debug.other_score >= 0.035f || debug.vocal_score >= 0.20f)
			return false;
		if (keyboard_owned_other_mirror_blocked_in_chord_context(ownership, debug))
			return true;
		if ((debug.owner == InstrumentKind::Guitar || debug.owner == InstrumentKind::Ambiguous) &&
		    count_owned_notes(ownership.guitar) >= 2 &&
		    debug.keyboard_score >= 0.50f && debug.vocal_score <= 0.02f)
			return true;
		if (debug.owner == InstrumentKind::Guitar && count_owned_notes(ownership.guitar) >= 2 &&
		    debug.guitar_score >= 0.70f && debug.vocal_score <= 0.02f &&
		    !guitar_owned_measured_string_other_display_supported(debug) &&
		    !guitar_owned_reed_other_display_supported(debug) &&
		    !measured_guitar_synth_other_priority_supported(debug) &&
		    !measured_guitar_synth_other_octave_supported(debug))
			return true;
	}

	if (row == FullMixDisplayRow::Vocal && debug.owner == InstrumentKind::Keyboard &&
	    count_owned_notes(ownership.keyboard) >= 2 &&
	    count_owned_notes(ownership.vocal) == 0 &&
	    debug.vocal_score <= 0.02f &&
	    debug.keyboard_score >= 0.80f &&
	    !measured_vocal_octave_alias_supported(debug))
		return true;

	return false;
}

int full_mix_display_mirror_midi(FullMixDisplayRow row, const FullMixDebugCandidate &debug,
				 const FullMixOwnership &ownership)
{
	if (row == FullMixDisplayRow::Vocal && debug.midi > kVocalMaxMidi &&
	    shared_vocal_pitch_display_supported(debug)) {
		const int lowered = debug.midi - 12;
		if (lowered >= kFullMixVocalMinMidi)
			return lowered;
	}
	if (row == FullMixDisplayRow::Vocal && measured_vocal_octave_alias_supported(debug)) {
		const int lowered = debug.midi - 12;
		return lowered;
	}
	if (row == FullMixDisplayRow::Keyboard && measured_keyboard_double_octave_alias_supported(debug)) {
		const int lowered = debug.midi - 24;
		if (ownership_global_note_level(ownership, lowered) >= 0.10f)
			return lowered;
	}
	if (row == FullMixDisplayRow::Keyboard &&
	    measured_low_organ_keyboard_octave_alias_supported(debug)) {
		const int lowered = debug.midi - 12;
		if (ownership_global_note_level(ownership, lowered) >= 0.006f ||
		    ownership_global_note_level(ownership, debug.midi) >= 0.10f)
			return lowered;
	}
	if (row == FullMixDisplayRow::Keyboard &&
	    measured_other_owned_electric_piano_octave_up_supported(debug)) {
		const int raised = debug.midi + 12;
		if (ownership_global_note_level(ownership, raised) >=
		    ownership_global_note_level(ownership, debug.midi))
			return raised;
	}
	if (row == FullMixDisplayRow::Keyboard &&
	    measured_low_pure_keyboard_octave_alias_supported(debug)) {
		const int pitch_class = ((debug.midi % 12) + 12) % 12;
		for (int midi = kKeyboardMinMidi; midi <= 48 && midi < debug.midi; ++midi) {
			if (((midi % 12) + 12) % 12 != pitch_class)
				continue;
			if (ownership_global_note_level(ownership, midi) >= 0.45f)
				return midi;
		}
	}
	if (row == FullMixDisplayRow::Guitar && measured_guitar_octave_alias_supported(debug))
		return debug.midi - 12;
	if (row == FullMixDisplayRow::Guitar && ambiguous_high_guitar_octave_alias_supported(debug)) {
		const int down_one = debug.midi - 12;
		const int down_two = debug.midi - 24;
		const float down_one_level = ownership_global_note_level(ownership, down_one);
		const float down_two_level = ownership_global_note_level(ownership, down_two);
		if (down_two >= kGuitarMinMidi &&
		    down_two_level >= 0.08f &&
		    down_two_level >= down_one_level * 0.65f)
			return down_two;
		if (down_one_level >= 0.08f)
			return down_one;
	}
	if (row == FullMixDisplayRow::Guitar && other_owned_distorted_guitar_octave_alias_supported(debug))
		return debug.midi - 12;
	if (row == FullMixDisplayRow::Guitar &&
	    other_owned_noisy_distorted_guitar_octave_up_supported(debug))
		return debug.midi + 12;
	if (row == FullMixDisplayRow::Other &&
	    (measured_vocal_synth_other_octave_supported(debug) ||
	     measured_guitar_synth_other_octave_supported(debug)))
		return debug.midi - 12;
	if (row == FullMixDisplayRow::Other &&
	    measured_keyboard_synth_other_priority_supported(debug) &&
	    debug.midi >= 60)
		return debug.midi;
	if (row == FullMixDisplayRow::Other && measured_other_octave_alias_supported(debug)) {
		const int lowered = debug.midi - 12;
		if (ownership_global_note_level(ownership, lowered) >= 0.14f)
			return lowered;
	}
	if (row == FullMixDisplayRow::Other && measured_other_weak_octave_alias_supported(debug)) {
		const int lowered = debug.midi - 12;
		if (ownership_global_note_level(ownership, lowered) >= 0.075f)
			return lowered;
	}
	return debug.midi;
}

bool full_mix_display_mirror_supported(FullMixDisplayRow row, const FullMixDebugCandidate &debug,
				       int display_midi)
{
	if (!full_mix_display_row_midi_allowed(row, display_midi))
		return false;
	const bool measured_low_organ_keyboard_alias =
		row == FullMixDisplayRow::Keyboard &&
		measured_low_organ_keyboard_octave_alias_supported(debug);
	const bool measured_noisy_guitar_octave_up_alias =
		row == FullMixDisplayRow::Guitar &&
		other_owned_noisy_distorted_guitar_octave_up_supported(debug) &&
		display_midi == debug.midi + 12;
	if ((debug.spectral_level < 0.16f || debug.pitch_confidence < 0.055f) &&
	    !measured_low_organ_keyboard_alias && !measured_noisy_guitar_octave_up_alias)
		return false;

	switch (row) {
	case FullMixDisplayRow::Keyboard: {
		const bool competing_guitar_range_hint =
			debug.midi >= kGuitarMinMidi && debug.midi <= kGuitarMaxMidi &&
			debug.guitar_score >= 0.30f &&
			debug.keyboard_score < debug.guitar_score + 0.32f;
		const bool noisy_low_keyboard_hint =
			debug.midi < 60 && debug.local_noise_level >= 0.28f &&
			debug.spectral_level >= 0.45f && debug.pitch_confidence >= 0.20f &&
			debug.guitar_score < 0.42f;
		const bool electronic_keyboard_partial_shape =
			debug.harmonic_ratios[1] >= 0.40f || debug.harmonic_ratios[3] >= 0.10f;
		const bool noisy_electronic_keyboard_hint =
			debug.midi >= 48 && debug.midi <= 84 &&
			debug.local_noise_level >= 0.12f &&
			debug.spectral_level >= 0.50f &&
			debug.pitch_confidence >= 0.70f &&
			debug.keyboard_score >= 0.085f &&
			debug.guitar_score >= 0.55f &&
			debug.other_score <= 0.08f &&
			electronic_keyboard_partial_shape;
		const bool noisy_low_electronic_keyboard_hint =
			debug.midi >= 40 && debug.midi <= 52 &&
			debug.local_noise_level >= 0.34f &&
			debug.local_noise_level <= 0.64f &&
			debug.spectral_level >= 0.62f &&
			debug.pitch_confidence >= 0.66f &&
			debug.periodicity >= 0.62f &&
			debug.harmonic_fit_error <= 0.09f &&
			debug.harmonic_ratios[1] >= 0.46f &&
			debug.harmonic_ratios[1] <= 0.58f &&
			debug.harmonic_ratios[2] >= 0.064f &&
			debug.harmonic_ratios[2] <= 0.16f &&
			debug.harmonic_ratios[3] >= 0.10f &&
			debug.harmonic_ratios[3] <= 0.19f &&
			debug.harmonic_ratios[4] <= 0.085f &&
			debug.spectral_slope >= 0.12f &&
			debug.spectral_slope <= 0.30f;
		const bool noisy_low_thin_electronic_keyboard_hint =
			debug.midi >= 40 && debug.midi <= 52 &&
			debug.local_noise_level >= 0.24f &&
			debug.local_noise_level <= 0.58f &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.66f &&
			debug.periodicity >= 0.62f &&
			debug.harmonic_fit_error <= 0.10f &&
			debug.harmonic_ratios[1] >= 0.24f &&
			debug.harmonic_ratios[1] <= 0.44f &&
			debug.harmonic_ratios[2] >= 0.050f &&
			debug.harmonic_ratios[2] <= 0.15f &&
			debug.harmonic_ratios[3] <= 0.055f &&
			debug.harmonic_ratios[4] <= 0.075f &&
			debug.spectral_slope >= 0.050f &&
			debug.spectral_slope <= 0.26f;
		const bool noisy_low_sparse_electronic_keyboard_hint =
			debug.midi >= 40 && debug.midi <= 54 &&
			debug.local_noise_level >= 0.23f &&
			debug.local_noise_level <= 0.64f &&
			debug.spectral_level >= 0.62f &&
			debug.pitch_confidence >= 0.66f &&
			debug.periodicity >= 0.58f &&
			debug.harmonic_fit_error <= 0.075f &&
			debug.harmonic_ratios[1] >= 0.10f &&
			debug.harmonic_ratios[1] <= 0.28f &&
			debug.harmonic_ratios[2] >= 0.035f &&
			debug.harmonic_ratios[2] <= 0.23f &&
			debug.harmonic_ratios[3] <= 0.055f &&
			debug.harmonic_ratios[4] <= 0.12f &&
			debug.spectral_centroid >= 0.12f &&
			debug.spectral_centroid <= 0.26f &&
			debug.spectral_slope >= 0.090f &&
			debug.spectral_slope <= 0.30f;
		const bool noisy_low_mid_electronic_keyboard_hint =
			(debug.owner == InstrumentKind::Guitar ||
			 debug.owner == InstrumentKind::Ambiguous) &&
			debug.midi >= 48 && debug.midi <= 54 &&
			debug.local_noise_level >= 0.23f &&
			debug.local_noise_level <= 0.37f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.72f &&
			debug.periodicity >= 0.70f &&
			debug.harmonic_fit_error <= 0.055f &&
			debug.harmonic_ratios[1] >= 0.337f &&
			debug.harmonic_ratios[1] <= 0.38f &&
			debug.harmonic_ratios[2] >= 0.050f &&
			debug.harmonic_ratios[2] <= 0.14f &&
			debug.harmonic_ratios[3] >= 0.055f &&
			debug.harmonic_ratios[3] <= 0.090f &&
			debug.harmonic_ratios[4] <= 0.020f &&
			debug.spectral_centroid >= 0.16f &&
			debug.spectral_centroid <= 0.21f &&
			debug.spectral_slope >= 0.090f &&
			debug.spectral_slope <= 0.17f;
		const bool clean_octave_electronic_keyboard_hint =
			debug.midi >= 60 && debug.midi <= 96 &&
			debug.local_noise_level <= 0.12f &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.66f &&
			debug.periodicity >= 0.64f &&
			debug.harmonic_fit_error <= 0.18f &&
			debug.harmonic_ratios[1] >= 0.52f &&
			debug.harmonic_ratios[1] <= 1.10f &&
			debug.harmonic_ratios[2] <= 0.15f &&
			debug.harmonic_ratios[3] <= 0.11f &&
			debug.harmonic_ratios[4] <= 0.070f &&
			debug.spectral_centroid >= 0.10f &&
			debug.spectral_centroid <= 0.34f &&
			debug.spectral_slope <= 0.34f;
		const bool high_octave_alias_electronic_keyboard_hint =
			(debug.owner == InstrumentKind::Guitar || debug.owner == InstrumentKind::Ambiguous ||
			 debug.owner == InstrumentKind::Other) &&
			high_octave_electronic_keyboard_alias_supported(debug);
		const bool clean_sustained_keyboard_hint =
			debug.midi >= 52 && debug.midi <= 84 &&
			debug.spectral_level >= 0.72f &&
			debug.pitch_confidence >= 0.74f &&
			debug.periodicity >= 0.72f &&
			debug.keyboard_score >= 0.18f &&
			debug.other_score <= 0.12f &&
			debug.local_noise_level <= 0.22f &&
			debug.harmonic_fit_error <= 0.12f &&
			(debug.owner == InstrumentKind::Vocal ||
			 debug.owner == InstrumentKind::Ambiguous ||
			 (debug.owner == InstrumentKind::Guitar && debug.guitar_score <= 0.74f));
		const bool clean_vocal_owned_keyboard_hint =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 52 && debug.midi <= 72 &&
			debug.spectral_level >= 0.82f &&
			debug.pitch_confidence >= 0.82f &&
			debug.periodicity >= 0.68f &&
			debug.keyboard_score >= 0.10f &&
			debug.other_score <= 0.08f &&
			debug.local_noise_level <= 0.20f &&
			debug.harmonic_fit_error <= 0.055f &&
			debug.harmonic_ratios[1] <= 0.28f &&
			debug.harmonic_ratios[2] <= 0.095f &&
			debug.harmonic_ratios[3] <= 0.055f &&
			debug.harmonic_ratios[4] <= 0.040f &&
			debug.spectral_centroid <= 0.16f &&
			debug.spectral_slope <= 0.14f;
		const bool pure_high_electronic_keyboard_hint =
			(debug.owner == InstrumentKind::Vocal ||
			 debug.owner == InstrumentKind::Ambiguous ||
			 debug.owner == InstrumentKind::Guitar ||
			 debug.owner == InstrumentKind::Other) &&
			debug.midi >= 72 && debug.midi <= 84 &&
			debug.spectral_level >= 0.78f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.040f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[1] <= 0.055f &&
			debug.harmonic_ratios[2] <= 0.13f &&
			debug.harmonic_ratios[3] <= 0.035f &&
			debug.harmonic_ratios[4] <= 0.035f &&
			debug.spectral_centroid <= 0.14f &&
			debug.spectral_slope <= 0.22f;
		const bool low_octave_organ_keyboard_hint =
			(debug.owner == InstrumentKind::Guitar ||
			 debug.owner == InstrumentKind::Ambiguous) &&
			debug.midi >= 40 && debug.midi <= 52 &&
			debug.local_noise_level >= 0.20f &&
			debug.local_noise_level <= 0.56f &&
			debug.spectral_level >= 0.30f &&
			debug.pitch_confidence >= 0.10f &&
			debug.periodicity >= 0.64f &&
			debug.harmonic_fit_error <= 0.065f &&
			debug.harmonic_ratios[1] >= 0.24f &&
			debug.harmonic_ratios[1] <= 0.46f &&
			debug.harmonic_ratios[2] >= 0.030f &&
			debug.harmonic_ratios[2] <= 0.14f &&
			debug.harmonic_ratios[3] <= 0.055f &&
			debug.harmonic_ratios[4] <= 0.060f &&
			debug.spectral_centroid >= 0.080f &&
			debug.spectral_centroid <= 0.21f &&
			debug.spectral_slope <= 0.13f;
		const bool bright_ambiguous_piano_keyboard_hint =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 60 && debug.midi <= 84 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.88f &&
			debug.harmonic_fit_error <= 0.16f &&
			debug.local_noise_level <= 0.080f &&
			debug.harmonic_ratios[1] >= 0.45f &&
			debug.harmonic_ratios[2] >= 0.30f &&
			debug.harmonic_ratios[3] <= 0.080f &&
			debug.harmonic_ratios[4] >= 0.20f &&
			debug.spectral_centroid >= 0.28f &&
			debug.spectral_centroid <= 0.38f;
		const bool ambiguous_high_acoustic_piano_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 80 &&
			debug.harmonic_fit_error <= 0.024f &&
			debug.keyboard_score <= 0.001f &&
			debug.harmonic_ratios[3] <= 0.051f;
		const bool ambiguous_electric_grand_piano_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.ownership_confidence <= 0.631f &&
			debug.periodicity >= 0.894f &&
			debug.periodicity <= 0.907f &&
			debug.pitch_confidence >= 0.932f &&
			debug.pitch_confidence <= 0.949f;
		const bool ambiguous_electric_piano2_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.ownership_confidence <= 0.465f &&
			debug.keyboard_score >= 0.344f &&
			debug.pitch_confidence >= 0.932f &&
			debug.harmonic_ratios[4] <= 0.099f;
		const bool high_guitar_owned_piano_hint =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 84 && debug.midi <= 96 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.90f &&
			debug.periodicity >= 0.70f &&
			debug.harmonic_fit_error <= 0.025f &&
			debug.local_noise_level <= 0.006f &&
			debug.harmonic_ratios[1] <= 0.17f &&
			debug.harmonic_ratios[2] <= 0.080f &&
			debug.harmonic_ratios[3] >= 0.006f &&
			debug.harmonic_ratios[3] <= 0.030f &&
			debug.harmonic_ratios[4] <= 0.004f;
		const bool measured_guitar_owned_piano_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.spectral_centroid <= 0.145f &&
			debug.guitar_score >= 0.69f &&
			debug.pitch_confidence >= 0.946f &&
			debug.spectral_level >= 0.90f &&
			debug.periodicity >= 0.78f &&
			debug.local_noise_level <= 0.12f;
		const bool guitar_owned_piano_attack_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.93f &&
			debug.periodicity >= 0.82f &&
			debug.harmonic_fit_error >= 0.039f &&
			debug.local_noise_level <= 0.070f &&
			debug.other_score >= 0.196f;
		const bool low_honky_tonk_piano_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 40 &&
			debug.midi <= 52 &&
			debug.guitar_score >= 0.69f &&
			debug.spectral_level >= 0.54f &&
			debug.pitch_confidence >= 0.51f &&
			debug.pitch_confidence <= 0.64f &&
			debug.periodicity >= 0.70f &&
			debug.local_noise_level <= 0.44f &&
			debug.harmonic_ratios[3] >= 0.035f;
		const bool noisy_guitar_owned_low_piano_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 40 &&
			debug.midi <= 52 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.70f &&
			debug.periodicity >= 0.66f &&
			debug.harmonicity <= 0.77f &&
			debug.local_noise_level >= 0.52f &&
			debug.harmonic_fit_error <= 0.070f &&
			debug.harmonic_ratios[1] >= 0.20f &&
			debug.harmonic_ratios[1] <= 0.44f;
		const bool ambiguous_electric_piano_dense_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 48 &&
			debug.midi <= 72 &&
			debug.ownership_confidence <= 0.52f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.92f &&
			debug.periodicity >= 0.887f &&
			debug.harmonic_fit_error <= 0.090f &&
			debug.harmonic_ratios[1] >= 0.45f &&
			debug.harmonic_ratios[2] >= 0.36f &&
			debug.harmonic_ratios[4] <= 0.090f;
		const bool ambiguous_electric_piano_tine_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 52 &&
			debug.midi <= 76 &&
			debug.guitar_score >= 0.49f &&
			debug.guitar_score <= 0.53f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.94f &&
			debug.periodicity >= 0.94f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.harmonic_ratios[1] >= 0.49f &&
			debug.harmonic_ratios[2] >= 0.20f &&
			debug.harmonic_ratios[2] <= 0.27f &&
			debug.harmonic_ratios[3] >= 0.18f &&
			debug.harmonic_ratios[3] <= 0.23f &&
			debug.harmonic_ratios[4] <= 0.020f;
		const bool ambiguous_electric_piano_bell_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 55 &&
			debug.midi <= 79 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.947f &&
			debug.periodicity >= 0.88f &&
			debug.harmonic_fit_error >= 0.082f &&
			debug.harmonic_fit_error <= 0.095f &&
			debug.spectral_slope >= 0.338f &&
			debug.harmonic_ratios[2] >= 0.32f &&
			debug.harmonic_ratios[3] >= 0.18f &&
			debug.harmonic_ratios[3] <= 0.24f &&
			debug.harmonic_ratios[4] <= 0.020f;
		const bool ambiguous_electric_piano_partial_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 55 &&
			debug.midi <= 76 &&
			debug.ownership_confidence <= 0.647f &&
			debug.spectral_centroid <= 0.31f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.92f &&
			debug.periodicity >= 0.894f &&
			debug.harmonic_fit_error <= 0.090f &&
			debug.harmonic_ratios[2] >= 0.369f &&
			debug.harmonic_ratios[3] <= 0.13f;
		const bool ambiguous_harpsichord_piano_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 52 &&
			debug.midi <= 60 &&
			debug.other_score >= 0.393f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.86f &&
			debug.periodicity >= 0.88f &&
			debug.harmonic_fit_error <= 0.070f &&
			debug.harmonic_ratios[1] >= 0.43f &&
			debug.harmonic_ratios[1] <= 0.52f &&
			debug.harmonic_ratios[2] >= 0.30f &&
			debug.harmonic_ratios[2] <= 0.34f &&
			debug.harmonic_ratios[3] <= 0.056f &&
			debug.harmonic_ratios[4] <= 0.143f;
		const bool other_owned_bright_piano_body =
			debug.owner == InstrumentKind::Other &&
			debug.harmonic_ratios[4] >= 0.355f &&
			debug.harmonic_ratios[4] <= 0.423f &&
			debug.pitch_confidence >= 0.70f &&
			debug.periodicity >= 0.818f;
		const bool other_owned_electric_piano_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= 52 &&
			debug.midi <= 64 &&
			debug.periodicity >= 0.88f &&
			debug.harmonic_fit_error <= 0.040f &&
			debug.spectral_slope >= 0.39f &&
			debug.spectral_slope <= 0.43f &&
			debug.harmonic_ratios[1] >= 0.42f &&
			debug.harmonic_ratios[2] >= 0.30f &&
			debug.harmonic_ratios[3] >= 0.20f;
		const bool other_owned_clavinet_piano_body =
			debug.owner == InstrumentKind::Other &&
			debug.harmonic_ratios[1] >= 0.422f &&
			debug.pitch_confidence >= 0.701f &&
			debug.spectral_slope >= 1.021f;
		const bool vocal_owned_acoustic_piano_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.vocal_score >= 0.837f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.94f &&
			debug.periodicity >= 0.79f &&
			debug.harmonic_ratios[2] >= 0.033f &&
			debug.harmonicity <= 0.35f;
		const bool guitar_owned_mid_piano_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 60 &&
			debug.guitar_score >= 0.823f &&
			((debug.spectral_centroid >= 0.166f &&
			  debug.periodicity <= 0.845f &&
			  debug.spectral_slope <= 0.105f) ||
			 (debug.harmonic_ratios[3] >= 0.035f &&
			  debug.pitch_confidence <= 0.906f));
		const bool guitar_owned_clavinet_piano_body =
			debug.owner == InstrumentKind::Guitar &&
			debug.spectral_centroid <= 0.174f &&
			debug.pitch_confidence <= 0.753f &&
			debug.periodicity >= 0.842f;
		return debug.owner == InstrumentKind::Keyboard ||
		       (debug.keyboard_score >= 0.46f && !competing_guitar_range_hint) ||
		       electronic_keyboard_alias_display_supported(debug) ||
		       noisy_low_keyboard_hint ||
		       noisy_electronic_keyboard_hint ||
		       noisy_low_electronic_keyboard_hint ||
		       noisy_low_thin_electronic_keyboard_hint ||
		       noisy_low_sparse_electronic_keyboard_hint ||
		       noisy_low_mid_electronic_keyboard_hint ||
		       clean_octave_electronic_keyboard_hint ||
		       high_octave_alias_electronic_keyboard_hint ||
		       clean_sustained_keyboard_hint ||
		       clean_vocal_owned_keyboard_hint ||
		       pure_high_electronic_keyboard_hint ||
		       low_octave_organ_keyboard_hint ||
		       measured_low_organ_keyboard_alias ||
		       bright_ambiguous_piano_keyboard_hint ||
		       measured_keyboard_double_octave_alias_supported(debug) ||
		       ambiguous_high_acoustic_piano_body ||
		       ambiguous_electric_grand_piano_body ||
		       ambiguous_electric_piano2_body ||
		       high_guitar_owned_piano_hint ||
		       measured_guitar_owned_piano_body ||
		       guitar_owned_piano_attack_body ||
		       low_honky_tonk_piano_body ||
		       noisy_guitar_owned_low_piano_body ||
		       ambiguous_electric_piano_dense_body ||
		       ambiguous_electric_piano_tine_body ||
		       ambiguous_electric_piano_bell_body ||
		       ambiguous_electric_piano_partial_body ||
		       ambiguous_harpsichord_piano_body ||
		       other_owned_bright_piano_body ||
		       other_owned_electric_piano_body ||
		       measured_other_owned_electric_piano_supported(debug) ||
		       measured_other_owned_electric_piano_octave_up_supported(debug) ||
		       measured_low_pure_keyboard_octave_alias_supported(debug) ||
		       other_owned_clavinet_piano_body ||
		       vocal_owned_acoustic_piano_body ||
		       guitar_owned_mid_piano_body ||
		       guitar_owned_clavinet_piano_body;
	}
	case FullMixDisplayRow::Guitar: {
		const bool low_noisy_bass_shaped_guitar_hint =
			debug.midi < 48 && debug.owner == InstrumentKind::Guitar &&
			debug.ownership_confidence >= 0.92f &&
			debug.local_noise_level > 0.55f &&
			debug.harmonic_ratios[1] < 0.56f &&
			debug.harmonic_ratios[2] < 0.28f;
		if (low_noisy_bass_shaped_guitar_hint)
			return false;
		const bool octave_dominant_acoustic_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= 40 && debug.midi <= 64 &&
			debug.spectral_level >= 0.50f &&
			debug.pitch_confidence >= 0.45f &&
			debug.periodicity >= 0.62f &&
			debug.harmonic_ratios[1] >= 0.88f &&
			debug.harmonic_ratios[1] <= 1.85f &&
			debug.harmonic_ratios[2] >= 0.060f &&
			debug.harmonic_ratios[2] <= 0.26f &&
			debug.harmonic_ratios[3] <= 0.12f &&
			debug.harmonic_ratios[4] >= 0.030f &&
			debug.harmonic_ratios[4] <= 0.18f &&
			debug.spectral_centroid >= 0.22f &&
			debug.spectral_centroid <= 0.48f &&
			debug.harmonic_fit_error <= 0.58f;
		const bool low_noisy_acoustic_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 40 && debug.midi <= 45 &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.66f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level >= 0.34f &&
			debug.local_noise_level <= 0.58f &&
			debug.harmonic_fit_error <= 0.13f &&
			debug.harmonic_ratios[1] >= 0.32f &&
			debug.harmonic_ratios[1] <= 0.50f &&
			debug.harmonic_ratios[2] <= 0.040f &&
			debug.harmonic_ratios[3] >= 0.22f &&
			debug.harmonic_ratios[3] <= 0.33f &&
			debug.harmonic_ratios[4] >= 0.050f &&
			debug.harmonic_ratios[4] <= 0.11f &&
			debug.spectral_centroid >= 0.23f &&
			debug.spectral_centroid <= 0.33f &&
			debug.spectral_slope >= 0.22f &&
			debug.spectral_slope <= 0.32f;
		const bool mid_keyboard_owned_acoustic_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 48 && debug.midi <= 58 &&
			debug.spectral_level >= 0.72f &&
			debug.pitch_confidence >= 0.80f &&
			debug.periodicity >= 0.70f &&
			debug.local_noise_level >= 0.085f &&
			debug.local_noise_level <= 0.31f &&
			debug.harmonic_fit_error >= 0.025f &&
			debug.harmonic_fit_error <= 0.12f &&
			debug.harmonic_ratios[1] >= 0.10f &&
			debug.harmonic_ratios[1] <= 0.37f &&
			debug.harmonic_ratios[2] >= 0.018f &&
			debug.harmonic_ratios[2] <= 0.050f &&
			debug.harmonic_ratios[3] >= 0.080f &&
			debug.harmonic_ratios[3] <= 0.28f &&
			debug.harmonic_ratios[4] >= 0.003f &&
			debug.harmonic_ratios[4] <= 0.075f &&
			debug.spectral_centroid >= 0.15f &&
			debug.spectral_centroid <= 0.27f &&
			debug.spectral_slope >= 0.11f &&
			debug.spectral_slope <= 0.26f &&
			debug.guitar_score <= 0.22f;
		const bool high_plucked_acoustic_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 64 && debug.midi <= 76 &&
			debug.spectral_level >= 0.68f &&
			debug.pitch_confidence >= 0.82f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.040f &&
			debug.harmonic_fit_error <= 0.12f &&
			debug.harmonic_ratios[1] >= 0.070f &&
			debug.harmonic_ratios[1] <= 0.16f &&
			debug.harmonic_ratios[2] >= 0.10f &&
			debug.harmonic_ratios[2] <= 0.25f &&
			debug.harmonic_ratios[3] >= 0.050f &&
			debug.harmonic_ratios[3] <= 0.18f &&
			debug.harmonic_ratios[4] <= 0.040f &&
			debug.spectral_centroid >= 0.10f &&
			debug.spectral_centroid <= 0.26f &&
			debug.spectral_slope >= 0.10f &&
			debug.spectral_slope <= 0.40f;
		const bool clean_high_acoustic_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 60 && debug.midi <= 76 &&
			debug.spectral_level >= 0.80f &&
			debug.pitch_confidence >= 0.86f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.065f &&
			debug.harmonic_fit_error <= 0.095f &&
			debug.harmonic_ratios[1] >= 0.035f &&
			debug.harmonic_ratios[1] <= 0.18f &&
			debug.harmonic_ratios[2] <= 0.070f &&
			debug.harmonic_ratios[3] <= 0.16f &&
			debug.harmonic_ratios[4] <= 0.045f &&
			debug.spectral_centroid <= 0.19f &&
			debug.spectral_slope <= 0.25f;
		const bool mid_vocal_like_acoustic_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 52 && debug.midi <= 59 &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.84f &&
			debug.periodicity >= 0.72f &&
			debug.local_noise_level <= 0.22f &&
			debug.harmonic_fit_error <= 0.055f &&
			debug.harmonic_ratios[1] >= 0.120f &&
			debug.harmonic_ratios[1] <= 0.18f &&
			debug.harmonic_ratios[2] >= 0.030f &&
			debug.harmonic_ratios[2] <= 0.060f &&
			debug.harmonic_ratios[3] >= 0.080f &&
			debug.harmonic_ratios[3] <= 0.15f &&
			debug.harmonic_ratios[4] <= 0.060f &&
			debug.spectral_centroid >= 0.14f &&
			debug.spectral_centroid <= 0.20f &&
			debug.spectral_slope >= 0.12f &&
			debug.spectral_slope <= 0.22f;
		const bool clean_high_keyboard_owned_acoustic_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 66 && debug.midi <= 76 &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.70f &&
			debug.local_noise_level <= 0.080f &&
			debug.harmonic_fit_error <= 0.085f &&
			debug.harmonic_ratios[1] >= 0.030f &&
			debug.harmonic_ratios[1] <= 0.20f &&
			debug.harmonic_ratios[2] <= 0.18f &&
			debug.harmonic_ratios[3] >= 0.020f &&
			debug.harmonic_ratios[3] <= 0.080f &&
			debug.harmonic_ratios[4] <= 0.040f &&
			debug.spectral_centroid <= 0.20f &&
			debug.spectral_slope <= 0.24f;
		const bool bright_keyboard_owned_high_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 72 && debug.midi <= 76 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.72f &&
			debug.periodicity >= 0.70f &&
			debug.local_noise_level <= 0.020f &&
			debug.harmonic_fit_error <= 0.10f &&
			debug.harmonic_ratios[1] >= 0.045f &&
			debug.harmonic_ratios[1] <= 0.095f &&
			debug.harmonic_ratios[2] >= 0.18f &&
			debug.harmonic_ratios[2] <= 0.24f &&
			debug.harmonic_ratios[3] <= 0.045f &&
			debug.harmonic_ratios[4] <= 0.045f &&
			debug.spectral_centroid >= 0.12f &&
			debug.spectral_centroid <= 0.22f &&
			debug.spectral_slope <= 0.28f;
		const bool pure_keyboard_owned_high_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 68 && debug.midi <= 76 &&
			debug.spectral_level >= 0.80f &&
			debug.pitch_confidence >= 0.84f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.030f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[1] <= 0.11f &&
			debug.harmonic_ratios[2] <= 0.045f &&
			debug.harmonic_ratios[3] <= 0.030f &&
			debug.harmonic_ratios[4] <= 0.025f &&
			debug.spectral_centroid <= 0.090f &&
			debug.spectral_slope <= 0.090f;
		const bool resonant_mid_ambiguous_acoustic_body =
			(debug.owner == InstrumentKind::Ambiguous ||
			 debug.owner == InstrumentKind::Vocal) &&
			debug.midi >= 60 && debug.midi <= 64 &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.90f &&
			debug.periodicity >= 0.78f &&
			debug.local_noise_level <= 0.075f &&
			debug.harmonic_fit_error <= 0.095f &&
			debug.keyboard_score >= 0.45f &&
			debug.harmonic_ratios[1] >= 0.22f &&
			debug.harmonic_ratios[1] <= 0.46f &&
			debug.harmonic_ratios[2] <= 0.10f &&
			debug.harmonic_ratios[3] >= 0.12f &&
			debug.harmonic_ratios[3] <= 0.25f &&
			debug.harmonic_ratios[4] <= 0.080f &&
			debug.spectral_centroid <= 0.22f &&
			debug.spectral_slope <= 0.26f;
		const bool bright_mid_ambiguous_acoustic_body =
			(debug.owner == InstrumentKind::Ambiguous ||
			 debug.owner == InstrumentKind::Vocal) &&
			debug.midi >= 60 && debug.midi <= 64 &&
			debug.spectral_level >= 0.92f &&
			debug.pitch_confidence >= 0.91f &&
			debug.periodicity >= 0.82f &&
			debug.local_noise_level <= 0.040f &&
			debug.harmonic_fit_error <= 0.12f &&
			debug.harmonic_ratios[1] >= 0.26f &&
			debug.harmonic_ratios[1] <= 0.35f &&
			debug.harmonic_ratios[2] <= 0.14f &&
			debug.harmonic_ratios[3] >= 0.070f &&
			debug.harmonic_ratios[3] <= 0.32f &&
			debug.harmonic_ratios[4] <= 0.010f &&
			debug.spectral_centroid >= 0.17f &&
			debug.spectral_centroid <= 0.27f &&
			debug.spectral_slope <= 0.26f;
		const bool very_high_clean_acoustic_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 77 && debug.midi <= 84 &&
			debug.spectral_level >= 0.78f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.040f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[1] <= 0.055f &&
			debug.harmonic_ratios[2] <= 0.13f &&
			debug.harmonic_ratios[3] <= 0.035f &&
			debug.harmonic_ratios[4] <= 0.035f &&
			debug.spectral_centroid <= 0.14f &&
			debug.spectral_slope <= 0.22f;
		const bool keyboard_owned_jazz_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.spectral_level >= 0.65f &&
			debug.spectral_level <= 0.95f &&
			debug.pitch_confidence >= 0.60f &&
			debug.periodicity <= 0.90f &&
			debug.local_noise_level <= 0.20f &&
			debug.harmonic_fit_error <= 0.25f &&
			debug.harmonic_ratios[2] >= 0.48f &&
			debug.harmonic_ratios[3] <= 0.040f &&
			debug.harmonic_ratios[4] <= 0.040f;
		const bool keyboard_owned_clean_guitar_octave =
			debug.owner == InstrumentKind::Keyboard &&
			debug.spectral_level >= 0.75f &&
			debug.spectral_level <= 0.95f &&
			debug.pitch_confidence >= 0.74f &&
			debug.periodicity <= 0.90f &&
			debug.local_noise_level <= 0.20f &&
			debug.harmonic_fit_error <= 0.045f &&
			debug.harmonic_ratios[1] >= 0.12f &&
			debug.harmonic_ratios[1] <= 0.18f &&
			debug.harmonic_ratios[2] <= 0.025f &&
			debug.harmonic_ratios[3] <= 0.020f &&
			debug.harmonic_ratios[4] <= 0.012f;
		const bool keyboard_owned_nylon_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 52 &&
			debug.midi <= 60 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.86f &&
			debug.periodicity >= 0.86f &&
			debug.harmonic_fit_error >= 0.12f &&
			debug.harmonic_fit_error <= 0.14f &&
			debug.local_noise_level <= 0.16f &&
			debug.harmonic_ratios[1] >= 0.40f &&
			debug.harmonic_ratios[1] <= 0.46f &&
			debug.harmonic_ratios[2] >= 0.045f &&
			debug.harmonic_ratios[2] <= 0.060f &&
			debug.harmonic_ratios[3] >= 0.13f &&
			debug.harmonic_ratios[3] <= 0.15f &&
			debug.harmonic_ratios[4] >= 0.29f &&
			debug.harmonic_ratios[4] <= 0.33f;
		const bool keyboard_owned_clean_guitar_resonance =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 71 &&
			debug.midi <= kGuitarMaxMidi &&
			debug.spectral_slope >= 1.012f &&
			debug.keyboard_score >= 0.70f &&
			debug.guitar_score >= 0.10f &&
			debug.periodicity >= 0.82f;
		const bool keyboard_owned_high_jazz_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 60 &&
			debug.midi <= 76 &&
			debug.pitch_confidence >= 0.953f &&
			debug.harmonic_fit_error >= 0.028f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[1] >= 0.18f &&
			debug.harmonic_ratios[1] <= 0.28f &&
			debug.harmonic_ratios[3] >= 0.10f &&
			debug.harmonic_ratios[3] <= 0.22f &&
			debug.harmonic_ratios[4] <= 0.010f;
		const bool keyboard_owned_muted_guitar_body =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi == 60 &&
			debug.keyboard_score >= 0.99f &&
			debug.pitch_confidence >= 0.90f &&
			debug.pitch_confidence <= 0.92f &&
			debug.periodicity >= 0.70f &&
			debug.periodicity <= 0.72f &&
			debug.harmonic_fit_error >= 0.040f &&
			debug.harmonic_fit_error <= 0.050f &&
			debug.local_noise_level >= 0.060f &&
			debug.local_noise_level <= 0.080f &&
			debug.spectral_centroid <= 0.060f &&
			debug.spectral_slope <= 0.065f &&
			debug.harmonic_ratios[1] <= 0.030f &&
			debug.harmonic_ratios[2] >= 0.030f &&
			debug.harmonic_ratios[2] <= 0.040f &&
			debug.harmonic_ratios[3] <= 0.010f &&
			debug.harmonic_ratios[4] >= 0.010f &&
			debug.harmonic_ratios[4] <= 0.020f;
		const bool other_owned_resonant_guitar_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= kGuitarMinMidi &&
			debug.midi <= kGuitarMaxMidi &&
			debug.spectral_level >= 0.45f &&
			debug.pitch_confidence >= 0.35f &&
			debug.periodicity <= 0.906f &&
			debug.harmonicity >= 1.966f &&
			debug.local_noise_level <= 0.058f;
		const bool noisy_low_acoustic_guitar_body =
			noisy_other_owned_low_acoustic_guitar_supported(debug);
		const bool other_owned_overdrive_guitar_body =
			other_owned_overdrive_guitar_body_supported(debug);
		const bool other_owned_driven_guitar_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= 52 &&
			debug.midi <= 64 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.80f &&
			debug.periodicity >= 0.84f &&
			debug.harmonic_fit_error <= 0.25f &&
			debug.local_noise_level <= 0.16f &&
			debug.harmonic_ratios[1] >= 0.45f &&
			debug.harmonic_ratios[2] >= 0.45f &&
			debug.harmonic_ratios[3] >= 0.20f;
		const bool other_owned_clean_guitar_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= 52 &&
			debug.midi <= 64 &&
			debug.spectral_level >= 0.50f &&
			debug.pitch_confidence >= 0.35f &&
			debug.periodicity >= 0.72f &&
			debug.harmonic_fit_error <= 0.62f &&
			debug.local_noise_level <= 0.07f &&
			debug.harmonic_ratios[1] >= 0.78f &&
			debug.harmonic_ratios[2] >= 1.50f &&
			debug.harmonic_ratios[3] >= 0.16f &&
			debug.harmonic_ratios[4] >= 0.12f;
		const bool other_owned_bright_guitar_body =
			debug.owner == InstrumentKind::Other &&
			debug.midi >= 67 &&
			debug.midi <= kGuitarMaxMidi &&
			debug.harmonic_ratios[2] >= 0.883f;
		const bool measured_low_acoustic_guitar_ownership_mirror =
			(debug.owner == InstrumentKind::Other ||
			 debug.owner == InstrumentKind::Ambiguous) &&
			debug.midi >= 40 &&
			debug.midi <= 56 &&
			debug.spectral_level >= 0.14f &&
			debug.pitch_confidence >= 0.055f &&
			debug.periodicity >= 0.34f &&
			debug.harmonic_fit_error <= 1.30f &&
			debug.local_noise_level <= 0.75f &&
			debug.spectral_centroid <= 0.82f;
		const bool other_owned_distorted_guitar_octave_body =
			other_owned_distorted_guitar_octave_alias_supported(debug);
		const bool other_owned_noisy_distorted_guitar_octave_up_body =
			other_owned_noisy_distorted_guitar_octave_up_supported(debug);
		const bool ambiguous_steel_guitar_octave_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 71 &&
			debug.midi - 12 >= kGuitarMinMidi &&
			debug.midi - 12 <= kGuitarMaxMidi &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.90f &&
			debug.periodicity >= 0.86f &&
			debug.local_noise_level <= 0.010f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.other_score >= 0.377f &&
			debug.other_score <= 0.395f &&
			debug.harmonic_ratios[1] >= 0.30f &&
			debug.harmonic_ratios[1] <= 0.42f &&
			debug.harmonic_ratios[2] >= 0.10f &&
			debug.harmonic_ratios[2] <= 0.18f &&
			debug.harmonic_ratios[3] >= 0.12f &&
			debug.harmonic_ratios[3] <= 0.20f &&
			debug.harmonic_ratios[4] <= 0.085f;
		const bool ambiguous_high_steel_guitar_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 76 &&
			debug.midi <= kGuitarMaxMidi &&
			debug.spectral_level >= 0.95f &&
			debug.pitch_confidence >= 0.95f &&
			debug.periodicity >= 0.90f &&
			debug.local_noise_level <= 0.010f &&
			debug.harmonic_fit_error <= 0.070f &&
			debug.keyboard_score >= 0.20f &&
			debug.guitar_score >= 0.35f &&
			debug.other_score >= 0.39f &&
			debug.other_score <= 0.40f &&
			debug.harmonic_ratios[1] >= 0.40f &&
			debug.harmonic_ratios[1] <= 0.43f &&
			debug.harmonic_ratios[2] >= 0.17f &&
			debug.harmonic_ratios[2] <= 0.20f &&
			debug.harmonic_ratios[3] >= 0.20f &&
			debug.harmonic_ratios[3] <= 0.24f &&
			debug.harmonic_ratios[4] <= 0.005f;
		const bool ambiguous_clean_jazz_guitar_body =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi == 76 &&
			debug.spectral_level >= 0.95f &&
			debug.pitch_confidence >= 0.94f &&
			debug.periodicity >= 0.72f &&
			debug.periodicity <= 0.78f &&
			debug.local_noise_level <= 0.005f &&
			debug.harmonic_fit_error <= 0.025f &&
			debug.keyboard_score >= 0.60f &&
			debug.keyboard_score <= 0.65f &&
			debug.vocal_score >= 0.35f &&
			debug.vocal_score <= 0.39f &&
			debug.harmonic_ratios[1] >= 0.070f &&
			debug.harmonic_ratios[1] <= 0.090f &&
			debug.harmonic_ratios[2] <= 0.025f &&
			debug.harmonic_ratios[3] <= 0.025f &&
			debug.harmonic_ratios[4] <= 0.001f;
		const bool vocal_owned_muted_guitar_body =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= kGuitarMinMidi &&
			debug.midi <= 59 &&
			debug.spectral_level >= 0.80f &&
			debug.pitch_confidence >= 0.80f &&
			debug.harmonic_fit_error <= 0.040f &&
			debug.spectral_centroid >= 0.118f &&
			debug.local_noise_level >= 0.154f &&
			debug.vocal_score >= 0.742f &&
			debug.harmonic_ratios[1] <= 0.18f &&
			debug.harmonic_ratios[3] <= 0.020f;
		const bool ambiguous_high_guitar_alias =
			ambiguous_high_guitar_octave_alias_supported(debug);
		return debug.owner == InstrumentKind::Guitar ||
		       debug.guitar_score >= 0.52f ||
		       shared_guitar_pitch_display_supported(debug) ||
		       octave_dominant_acoustic_body ||
		       low_noisy_acoustic_body ||
		       mid_keyboard_owned_acoustic_body ||
		       high_plucked_acoustic_body ||
		       clean_high_acoustic_body ||
		       mid_vocal_like_acoustic_body ||
		       clean_high_keyboard_owned_acoustic_body ||
		       bright_keyboard_owned_high_guitar_body ||
		       pure_keyboard_owned_high_guitar_body ||
		       resonant_mid_ambiguous_acoustic_body ||
		       bright_mid_ambiguous_acoustic_body ||
		       very_high_clean_acoustic_body ||
		       keyboard_owned_jazz_guitar_body ||
		       keyboard_owned_clean_guitar_octave ||
		       keyboard_owned_nylon_guitar_body ||
		       keyboard_owned_clean_guitar_resonance ||
		       keyboard_owned_high_jazz_guitar_body ||
		       keyboard_owned_muted_guitar_body ||
		       other_owned_resonant_guitar_body ||
		       noisy_low_acoustic_guitar_body ||
		       other_owned_driven_guitar_body ||
		       other_owned_clean_guitar_body ||
		       other_owned_bright_guitar_body ||
		       measured_low_acoustic_guitar_ownership_mirror ||
		       other_owned_overdrive_guitar_body ||
		       other_owned_distorted_guitar_octave_body ||
		       other_owned_noisy_distorted_guitar_octave_up_body ||
		       ambiguous_steel_guitar_octave_body ||
		       ambiguous_high_steel_guitar_body ||
		       ambiguous_clean_jazz_guitar_body ||
		       vocal_owned_muted_guitar_body ||
		       ambiguous_high_guitar_alias ||
		       measured_guitar_octave_alias_supported(debug);
	}
	case FullMixDisplayRow::Vocal:
		return shared_vocal_pitch_display_supported(debug) || measured_vocal_octave_alias_supported(debug);
	case FullMixDisplayRow::Other:
		const bool sustained_other = sustained_other_display_supported(debug);
		const bool low_weak_upper_string_other =
			debug.midi >= 39 && debug.midi <= 59 &&
			debug.spectral_level >= 0.70f &&
			debug.pitch_confidence >= 0.70f &&
			debug.periodicity >= 0.62f &&
			debug.harmonic_fit_error <= 0.09f &&
			debug.harmonic_ratios[1] >= 0.10f &&
			debug.harmonic_ratios[1] <= 0.32f &&
			debug.harmonic_ratios[2] <= 0.075f &&
			debug.harmonic_ratios[3] <= 0.040f &&
			debug.harmonic_ratios[4] <= 0.045f &&
			debug.spectral_centroid >= 0.050f &&
			debug.spectral_centroid <= 0.17f &&
			debug.spectral_slope <= 0.14f;
		const bool noisy_low_ambiguous_bowed_string_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 40 && debug.midi <= 44 &&
			debug.spectral_level >= 0.68f &&
			debug.pitch_confidence >= 0.56f &&
			debug.periodicity >= 0.54f &&
			debug.local_noise_level >= 0.38f &&
			debug.local_noise_level <= 0.62f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.harmonic_ratios[1] <= 0.22f &&
			debug.harmonic_ratios[2] <= 0.11f &&
			debug.harmonic_ratios[3] <= 0.13f &&
			debug.harmonic_ratios[4] <= 0.060f &&
			debug.spectral_centroid >= 0.080f &&
			debug.spectral_centroid <= 0.18f &&
			debug.spectral_slope <= 0.20f;
		const bool bright_high_brass_other =
			debug.midi >= 68 && debug.midi <= 84 &&
			debug.spectral_level >= 0.72f &&
			debug.pitch_confidence >= 0.84f &&
			debug.periodicity >= 0.84f &&
			debug.local_noise_level <= 0.045f &&
			debug.harmonic_fit_error <= 0.34f &&
			debug.harmonic_ratios[1] <= 0.26f &&
			debug.harmonic_ratios[2] >= 0.24f &&
			debug.harmonic_ratios[2] <= 0.66f &&
			debug.harmonic_ratios[3] >= 0.28f &&
			debug.harmonic_ratios[3] <= 0.85f &&
			debug.harmonic_ratios[4] <= 0.08f &&
			debug.spectral_centroid >= 0.30f &&
			debug.spectral_centroid <= 0.50f &&
			debug.spectral_slope >= 0.45f &&
			debug.spectral_slope <= 1.20f;
		const bool low_bowed_string_display_other =
			(debug.owner == InstrumentKind::Keyboard ||
			 debug.owner == InstrumentKind::Guitar ||
			 debug.owner == InstrumentKind::Ambiguous) &&
			debug.midi >= 48 && debug.midi <= 65 &&
			debug.spectral_level >= 0.35f &&
			debug.periodicity >= 0.65f &&
			debug.harmonic_fit_error <= 0.16f &&
			debug.local_noise_level >= 0.24f &&
			debug.local_noise_level <= 0.50f &&
			debug.harmonic_ratios[1] >= 0.12f &&
			debug.harmonic_ratios[1] <= 0.36f &&
			debug.harmonic_ratios[2] >= 0.025f &&
			debug.harmonic_ratios[2] <= 0.40f &&
			debug.harmonic_ratios[3] <= 0.20f &&
			debug.spectral_centroid >= 0.12f &&
			debug.spectral_centroid <= 0.30f &&
			debug.spectral_slope >= 0.10f &&
			debug.spectral_slope <= 0.40f;
		const bool octave_dominant_reed_display_other =
			guitar_owned_reed_other_display_supported(debug);
		const bool octave_rich_reed_display_other =
			guitar_owned_reed_other_display_supported(debug);
		const bool smooth_bowed_string_display_other =
			(debug.owner == InstrumentKind::Guitar ||
			 debug.owner == InstrumentKind::Ambiguous ||
			 debug.owner == InstrumentKind::Vocal) &&
			debug.midi >= 60 && debug.midi <= 66 &&
			debug.spectral_level >= 0.80f &&
			debug.pitch_confidence >= 0.80f &&
			debug.periodicity >= 0.68f &&
			debug.local_noise_level <= 0.16f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[1] >= 0.050f &&
			debug.harmonic_ratios[1] <= 0.32f &&
			debug.harmonic_ratios[2] <= 0.040f &&
			debug.harmonic_ratios[3] <= 0.040f &&
			debug.harmonic_ratios[4] <= 0.040f &&
			debug.spectral_centroid >= 0.020f &&
			debug.spectral_centroid <= 0.14f &&
			debug.spectral_slope <= 0.060f;
		const bool square_lead_display_other =
			debug.owner == InstrumentKind::Keyboard &&
			debug.keyboard_score >= 0.80f &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.70f &&
			debug.harmonic_ratios[1] <= 0.025f &&
			debug.harmonic_ratios[2] >= 0.095f &&
			debug.harmonic_ratios[3] <= 0.012f &&
			debug.harmonic_ratios[4] >= 0.080f;
		const bool measured_keyboard_synth_other =
			keyboard_owned_synth_other_display_supported(debug);
		const bool keyboard_owned_bowed_string_other =
			debug.owner == InstrumentKind::Keyboard &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.88f &&
			debug.periodicity >= 0.78f &&
			debug.harmonic_fit_error <= 0.14f &&
			debug.harmonicity <= 0.51f &&
			debug.harmonic_ratios[3] >= 0.16f &&
			debug.harmonic_ratios[4] >= 0.005f;
		const bool keyboard_owned_contrabass_other =
			debug.owner == InstrumentKind::Keyboard &&
			debug.midi >= 36 &&
			debug.midi <= 48 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.78f &&
			debug.periodicity >= 0.66f &&
			debug.periodicity <= 0.69f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.spectral_slope <= 0.18f &&
			debug.harmonic_ratios[1] >= 0.060f &&
			debug.harmonic_ratios[1] <= 0.10f &&
			debug.harmonic_ratios[2] >= 0.060f &&
			debug.harmonic_ratios[2] <= 0.10f &&
			debug.harmonic_ratios[3] <= 0.030f &&
			debug.harmonic_ratios[4] >= 0.040f &&
			debug.harmonic_ratios[4] <= 0.070f;
		const bool ambiguous_viola_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.79f &&
			debug.periodicity >= 0.80f &&
			debug.harmonic_fit_error >= 0.30f &&
			debug.spectral_centroid >= 0.53f &&
			debug.ownership_confidence <= 0.64f &&
			debug.harmonic_ratios[2] >= 0.80f &&
			debug.harmonic_ratios[3] >= 0.80f &&
			debug.harmonic_ratios[4] >= 0.30f;
		const bool ambiguous_high_violin_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.79f &&
			debug.periodicity >= 0.86f &&
			debug.harmonic_fit_error >= 0.24f &&
			debug.local_noise_level >= 0.018f &&
			debug.ownership_confidence <= 0.64f &&
			debug.harmonic_ratios[1] >= 0.90f &&
			debug.harmonic_ratios[2] <= 0.010f &&
			debug.harmonic_ratios[3] <= 0.010f &&
			debug.harmonic_ratios[4] <= 0.010f;
		const bool ambiguous_octave_string_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi >= 72 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.85f &&
			debug.periodicity >= 0.70f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.local_noise_level >= 0.015f &&
			debug.harmonic_ratios[1] >= 0.18f &&
			debug.harmonic_ratios[1] <= 0.24f &&
			debug.harmonic_ratios[2] <= 0.025f &&
			debug.harmonic_ratios[3] <= 0.055f &&
			debug.harmonic_ratios[4] <= 0.025f;
		const bool guitar_owned_viola_string_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.guitar_score >= 0.701f &&
			debug.other_score >= 0.189f &&
			debug.harmonic_ratios[2] >= 0.072f &&
			debug.spectral_slope <= 0.244f;
		const bool guitar_owned_synth_string_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.keyboard_score >= 0.135f &&
			debug.keyboard_score <= 0.139f &&
			debug.guitar_score >= 0.80f &&
			debug.pitch_confidence >= 0.83f &&
			debug.periodicity >= 0.80f &&
			debug.harmonic_fit_error <= 0.040f &&
			debug.harmonic_ratios[1] >= 0.35f &&
			debug.harmonic_ratios[1] <= 0.45f &&
			debug.harmonic_ratios[2] >= 0.25f &&
			debug.harmonic_ratios[2] <= 0.34f &&
			debug.harmonic_ratios[3] >= 0.080f &&
			debug.harmonic_ratios[3] <= 0.12f;
		const bool ambiguous_pizzicato_string_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.other_score <= 0.001f &&
			debug.pitch_confidence >= 0.898f &&
			debug.local_noise_level >= 0.095f &&
			debug.harmonic_fit_error <= 0.020f &&
			debug.harmonic_ratios[1] <= 0.096f &&
			debug.harmonic_ratios[2] >= 0.018f &&
			debug.harmonic_ratios[2] <= 0.030f;
		const bool ambiguous_contrabass_string_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.harmonic_fit_error >= 0.017f &&
			debug.harmonic_ratios[1] >= 0.084f &&
			debug.periodicity >= 0.666f &&
			debug.periodicity <= 0.685f;
		const bool ambiguous_cello_string_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.local_noise_level >= 0.122f &&
			debug.harmonic_ratios[1] >= 0.084f &&
			debug.harmonic_ratios[3] >= 0.247f &&
			debug.periodicity <= 0.773f;
		const bool low_acoustic_string_octave_other =
			measured_low_acoustic_string_other_octave_supported(debug);
		const bool guitar_owned_measured_synth_strings_other =
			guitar_owned_synth_strings_other_display_supported(debug);
		const bool guitar_owned_low_contrabass_other =
			guitar_owned_low_contrabass_other_display_supported(debug);
		const bool guitar_owned_high_string_ensemble_other =
			guitar_owned_high_string_ensemble_other_display_supported(debug);
		const bool guitar_owned_high_violin_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 88 &&
			debug.harmonicity >= 1.035f &&
			debug.local_noise_level >= 0.003f;
		const bool vocal_owned_pizzicato_string_other =
			debug.owner == InstrumentKind::Vocal &&
			debug.spectral_centroid >= 0.049f &&
			debug.periodicity <= 0.709f &&
			debug.pitch_confidence <= 0.914f &&
			debug.spectral_slope <= 0.134f;
		const bool vocal_owned_harp_string_other =
			debug.owner == InstrumentKind::Vocal &&
			debug.ownership_confidence >= 0.748f &&
			debug.ownership_confidence <= 0.807f &&
			debug.harmonicity <= 0.405f &&
			debug.keyboard_score <= 0.193f &&
			debug.harmonic_ratios[4] <= 0.037f;
		const bool vocal_owned_measured_pizzicato_string_other =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi <= 60 &&
			debug.harmonic_fit_error >= 0.031f &&
			debug.keyboard_score >= 0.193f &&
			debug.harmonic_ratios[1] >= 0.036f;
		const bool measured_string_other =
			keyboard_owned_string_other_display_supported(debug) ||
			keyboard_owned_bowed_string_other ||
			keyboard_owned_contrabass_other ||
			ambiguous_viola_other ||
			ambiguous_high_violin_other ||
			ambiguous_octave_string_other ||
			measured_ambiguous_string_other_priority_supported(debug) ||
			guitar_owned_viola_string_other ||
			guitar_owned_synth_string_other ||
			measured_guitar_string_other_priority_supported(debug) ||
			ambiguous_pizzicato_string_other ||
			ambiguous_contrabass_string_other ||
			ambiguous_cello_string_other ||
			low_acoustic_string_octave_other ||
			guitar_owned_measured_synth_strings_other ||
			guitar_owned_low_contrabass_other ||
			guitar_owned_high_string_ensemble_other ||
			guitar_owned_high_violin_other ||
			vocal_owned_pizzicato_string_other ||
			vocal_owned_harp_string_other ||
			vocal_owned_measured_pizzicato_string_other;
		const bool guitar_owned_synth_lead_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 48 &&
			debug.midi <= 72 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.90f &&
			debug.periodicity >= 0.75f &&
			debug.harmonic_fit_error <= 0.040f &&
			debug.spectral_centroid >= 0.144f &&
			debug.vocal_score >= 0.227f &&
			debug.harmonic_ratios[1] >= 0.20f &&
			debug.harmonic_ratios[2] <= 0.080f &&
			debug.harmonic_ratios[3] <= 0.090f;
		const bool guitar_owned_choir_pad_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 40 &&
			debug.midi <= 60 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.70f &&
			debug.periodicity >= 0.676f &&
			debug.local_noise_level >= 0.289f &&
			debug.harmonic_fit_error <= 0.080f &&
			debug.harmonic_ratios[3] >= 0.12f &&
			debug.harmonic_ratios[4] <= 0.004f;
		const bool guitar_owned_bowed_pad_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 40 &&
			debug.midi <= 60 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence <= 0.66f &&
			debug.periodicity >= 0.65f &&
			debug.harmonic_fit_error >= 0.30f &&
			debug.spectral_centroid >= 0.29f &&
			debug.harmonic_ratios[2] <= 0.040f &&
			debug.harmonic_ratios[4] >= 0.80f;
		const bool guitar_owned_chiff_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 36 &&
			debug.midi <= 72 &&
			debug.spectral_level >= 0.78f &&
			debug.pitch_confidence >= 0.78f &&
			debug.periodicity >= 0.72f &&
			debug.harmonic_fit_error <= 0.085f &&
			debug.local_noise_level >= 0.10f &&
			debug.harmonic_ratios[1] >= 0.32f &&
			debug.harmonic_ratios[1] <= 0.50f &&
			debug.harmonic_ratios[2] <= 0.20f &&
			debug.harmonic_ratios[3] <= 0.025f &&
			debug.harmonic_ratios[4] <= 0.095f;
		const bool guitar_owned_voice_or_warm_pad_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 48 &&
			debug.midi <= 84 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.83f &&
			debug.periodicity >= 0.78f &&
			debug.harmonic_fit_error <= 0.12f &&
			debug.local_noise_level <= 0.20f &&
			debug.harmonic_ratios[1] >= 0.32f &&
			debug.harmonic_ratios[1] <= 0.70f &&
			debug.harmonic_ratios[2] >= 0.12f &&
			debug.harmonic_ratios[2] <= 0.24f &&
			debug.harmonic_ratios[3] <= 0.10f &&
			debug.harmonic_ratios[4] <= 0.13f;
		const bool guitar_owned_noisy_warm_pad_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 36 &&
			debug.midi <= 72 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.80f &&
			debug.periodicity >= 0.76f &&
			debug.harmonic_fit_error <= 0.060f &&
			debug.local_noise_level >= 0.24f &&
			debug.local_noise_level <= 0.36f &&
			debug.harmonic_ratios[1] >= 0.36f &&
			debug.harmonic_ratios[1] <= 0.44f &&
			debug.harmonic_ratios[2] >= 0.20f &&
			debug.harmonic_ratios[2] <= 0.25f &&
			debug.harmonic_ratios[3] <= 0.060f &&
			debug.harmonic_ratios[4] <= 0.050f;
		const bool guitar_owned_choir_partial_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.78f &&
			debug.periodicity <= 0.81f &&
			debug.vocal_score <= 0.001f &&
			debug.harmonic_fit_error <= 0.18f &&
			debug.harmonic_ratios[2] >= 0.058f &&
			debug.harmonic_ratios[2] <= 0.060f &&
			debug.harmonic_ratios[3] >= 0.026f &&
			debug.harmonic_ratios[3] <= 0.13f &&
			debug.harmonic_ratios[4] <= 0.010f;
		const bool guitar_owned_metallic_pad_other =
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 48 &&
			debug.local_noise_level >= 0.298f &&
			debug.periodicity <= 0.786f;
		const bool vocal_owned_synth_lead_other =
			debug.owner == InstrumentKind::Vocal &&
			debug.midi >= 55 &&
			debug.midi <= 84 &&
			debug.spectral_level >= 0.90f &&
			debug.pitch_confidence >= 0.87f &&
			debug.periodicity >= 0.72f &&
			debug.harmonic_fit_error <= 0.045f &&
			debug.keyboard_score >= 0.10f &&
			debug.vocal_score >= 0.59f &&
			debug.other_score <= 0.001f &&
			debug.harmonic_ratios[1] >= 0.055f &&
			debug.harmonic_ratios[1] <= 0.24f &&
			debug.harmonic_ratios[2] <= 0.14f &&
			debug.harmonic_ratios[3] <= 0.090f &&
			debug.harmonic_ratios[4] <= 0.020f;
		const bool ambiguous_sparse_calliope_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.local_noise_level >= 0.007f &&
			debug.harmonic_ratios[2] >= 0.013f &&
			debug.harmonic_ratios[3] <= 0.008f &&
			debug.periodicity <= 0.712f;
		const bool ambiguous_low_synth_lead_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.midi <= 43 &&
			debug.harmonicity <= 0.308f &&
			debug.harmonic_ratios[1] <= 0.085f;
		const bool ambiguous_calliope_pad_other =
			debug.owner == InstrumentKind::Ambiguous &&
			debug.other_score <= 0.001f &&
			debug.harmonic_ratios[3] <= 0.135f &&
			debug.harmonic_ratios[4] >= 0.030f &&
			debug.periodicity >= 0.712f;
		const bool measured_ambiguous_synth_other =
			ambiguous_sparse_calliope_other ||
			ambiguous_low_synth_lead_other ||
			ambiguous_calliope_pad_other;
		const bool measured_guitar_synth_other =
			guitar_owned_synth_lead_other ||
			guitar_owned_choir_pad_other ||
			guitar_owned_bowed_pad_other ||
			guitar_owned_chiff_other ||
			guitar_owned_voice_or_warm_pad_other ||
			guitar_owned_noisy_warm_pad_other ||
			guitar_owned_choir_partial_other ||
			guitar_owned_metallic_pad_other ||
			measured_guitar_synth_other_priority_supported(debug) ||
			measured_guitar_synth_other_octave_supported(debug);
		const bool high_wind_like_guitar_other =
			sustained_other &&
			debug.owner == InstrumentKind::Guitar &&
			debug.midi >= 68 &&
			debug.spectral_centroid >= 0.18f &&
			debug.spectral_slope >= 0.050f;
		const bool hollow_reed_like_guitar_other =
			debug.owner == InstrumentKind::Guitar &&
			hollow_reed_other_display_supported(debug);
		const bool sustained_guitar_other =
			sustained_other &&
			(debug.other_score >= 0.060f || high_wind_like_guitar_other ||
			 hollow_reed_like_guitar_other);
		if (debug.owner == InstrumentKind::Guitar && debug.ownership_confidence >= 0.58f &&
		    debug.other_score < 0.30f && !sustained_guitar_other && !bright_high_brass_other &&
		    !low_weak_upper_string_other && !low_bowed_string_display_other &&
		    !octave_dominant_reed_display_other && !octave_rich_reed_display_other &&
		    !smooth_bowed_string_display_other && !measured_string_other &&
		    !measured_guitar_synth_other)
			return false;
		return debug.owner == InstrumentKind::Other ||
		       debug.other_score >= 0.035f ||
		       shared_other_pitch_display_supported(debug) ||
		       sustained_other ||
		       bright_high_brass_other ||
		       low_weak_upper_string_other ||
		       noisy_low_ambiguous_bowed_string_other ||
		       low_bowed_string_display_other ||
		       octave_dominant_reed_display_other ||
		       octave_rich_reed_display_other ||
		       smooth_bowed_string_display_other ||
		       square_lead_display_other ||
		       measured_keyboard_synth_other ||
		       measured_keyboard_synth_other_priority_supported(debug) ||
		       measured_string_other ||
		       measured_guitar_synth_other ||
		       measured_ambiguous_synth_other ||
		       vocal_owned_synth_lead_other ||
		       measured_vocal_synth_other_priority_supported(debug) ||
		       measured_vocal_synth_other_octave_supported(debug) ||
		       measured_guitar_synth_other_octave_supported(debug);
	}
	return false;
}

void add_full_mix_display_mirror(NoteCandidateList &candidates, const FullMixOwnership &ownership,
				 const FullMixDebugCandidate &debug, FullMixDisplayRow row,
				 const std::array<float, kNoteProbeCount> *raw_powers = nullptr)
{
	const int display_midi = full_mix_display_mirror_midi(row, debug, ownership);
	if (display_midi < kFirstMidi || display_midi > kLastMidi)
		return;
	const std::size_t index = static_cast<std::size_t>(display_midi - kFirstMidi);
	if (full_mix_row_display_midi_suppressed(ownership, row, display_midi))
		return;
	if (clean_owned_chord_context_for_row(ownership, debug, row))
		return;
	const bool candidate_exists = candidate_list_has_midi(candidates, display_midi);
	if (row == FullMixDisplayRow::Other &&
	    keyboard_owned_other_mirror_blocked_in_chord_context(ownership, debug))
		return;
	if (!full_mix_display_mirror_supported(row, debug, display_midi))
		return;

	float global_level = std::clamp(ownership.global_note_levels[index], 0.0f, 1.0f);
	if (display_midi != debug.midi && debug.midi >= kFirstMidi && debug.midi <= kLastMidi) {
		const std::size_t debug_index = static_cast<std::size_t>(debug.midi - kFirstMidi);
		global_level = std::max(global_level,
					std::clamp(ownership.global_note_levels[debug_index], 0.0f, 1.0f));
	}
	const bool measured_low_organ_keyboard_alias =
		row == FullMixDisplayRow::Keyboard &&
		display_midi != debug.midi &&
		measured_low_organ_keyboard_octave_alias_supported(debug);
	if (measured_low_organ_keyboard_alias)
		global_level = std::max(global_level, 0.34f);
	if (row == FullMixDisplayRow::Vocal && display_midi != debug.midi &&
	    measured_vocal_octave_alias_supported(debug)) {
		global_level = std::max(global_level,
					std::clamp(debug.spectral_level * debug.pitch_confidence, 0.0f, 1.0f));
	}
	if (global_level < 0.10f)
		return;

	const float row_reference = strongest_candidate_score(candidates);
	const float base_score = row_reference > 1.0e-6f ? row_reference : 1.0f;
	float candidate_score = base_score * std::clamp(global_level, 0.18f, 1.0f) * 0.52f;
	if (row == FullMixDisplayRow::Vocal && display_midi != debug.midi &&
	    (measured_vocal_octave_alias_priority_supported(debug) ||
	     raw_supported_vocal_lower_octave_alias(debug, display_midi, raw_powers)))
		candidate_score = std::max(candidate_score, base_score * 1.08f);
	if (row == FullMixDisplayRow::Guitar && display_midi != debug.midi &&
	    other_owned_distorted_guitar_octave_alias_supported(debug))
		candidate_score = std::max(candidate_score, base_score * 1.05f);
	if (row == FullMixDisplayRow::Guitar && display_midi != debug.midi &&
	    other_owned_noisy_distorted_guitar_octave_up_supported(debug))
		candidate_score = std::max(candidate_score, base_score * 0.72f);
	if (row == FullMixDisplayRow::Guitar &&
	    noisy_other_owned_low_acoustic_guitar_supported(debug))
		candidate_score = std::max(candidate_score, base_score * 1.04f);
	if (row == FullMixDisplayRow::Guitar &&
	    other_owned_overdrive_guitar_body_supported(debug))
		candidate_score = std::max(candidate_score, base_score * 1.04f);
	if (row == FullMixDisplayRow::Keyboard &&
	    measured_other_owned_electric_piano_supported(debug))
		candidate_score = std::max(candidate_score, base_score * 1.04f);
	if (measured_low_organ_keyboard_alias)
		candidate_score = std::max(candidate_score, base_score * 0.22f);
	if (row == FullMixDisplayRow::Other &&
	    (measured_keyboard_synth_other_priority_supported(debug) ||
	     measured_ambiguous_string_other_priority_supported(debug) ||
	     guitar_owned_measured_string_other_display_supported(debug) ||
	     measured_vocal_synth_other_priority_supported(debug) ||
	     measured_guitar_synth_other_priority_supported(debug) ||
	     measured_vocal_synth_other_octave_supported(debug) ||
	     measured_guitar_synth_other_octave_supported(debug)))
		candidate_score = std::max(candidate_score, base_score * 1.04f);
	float candidate_confidence = row == FullMixDisplayRow::Other ? 0.21f : 0.20f;
	if (measured_low_organ_keyboard_alias) {
		candidate_score = std::max(candidate_score, base_score * 0.72f);
		candidate_confidence = std::max(candidate_confidence, 0.58f);
	}
	if (candidate_exists) {
		for (NoteCandidate &candidate : candidates) {
			if (candidate.midi == display_midi) {
				candidate.score = std::max(candidate.score, candidate_score);
				candidate.ownership_confidence =
					std::max(candidate.ownership_confidence, candidate_confidence);
			}
		}
		return;
	}
	NoteCandidate candidate;
	candidate.midi = display_midi;
	candidate.score = candidate_score;
	candidate.ownership_confidence = candidate_confidence;
	candidates.push_back(candidate);
}

NoteCandidateList full_mix_display_candidates(const FullMixOwnership &ownership, FullMixDisplayRow row,
					      const std::array<float, kNoteProbeCount> *raw_powers = nullptr)
{
	NoteCandidateList candidates;
	switch (row) {
	case FullMixDisplayRow::Keyboard:
		candidates = ownership.keyboard_candidates;
		break;
	case FullMixDisplayRow::Guitar:
		candidates = ownership.guitar_candidates;
		break;
	case FullMixDisplayRow::Vocal:
		candidates = ownership.vocal_candidates;
		break;
	case FullMixDisplayRow::Other:
		candidates = ownership.other_candidates;
		break;
	}

	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i)
		add_full_mix_display_mirror(candidates, ownership, ownership.debug_candidates[i], row, raw_powers);
	return candidates;
}

bool non_guitar_debug_pitch_support(const FullMixDebugCandidate &debug)
{
	if (debug.owner == InstrumentKind::Keyboard || debug.owner == InstrumentKind::Other ||
	    debug.owner == InstrumentKind::Vocal)
		return true;
	const float non_guitar_score = std::max({debug.keyboard_score, debug.other_score, debug.vocal_score});
	return non_guitar_score >= 0.42f && non_guitar_score >= debug.guitar_score * 1.35f;
}

const FullMixDebugCandidate *strongest_same_pitch_non_guitar_debug_at_or_below(
	const FullMixOwnership &ownership, int midi)
{
	const int pitch_class = midi_pitch_class(midi);
	const FullMixDebugCandidate *best = nullptr;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi > midi || midi_pitch_class(debug.midi) != pitch_class)
			continue;
		if (!non_guitar_debug_pitch_support(debug))
			continue;
		if (!best || ownership_global_note_level(ownership, debug.midi) >
				     ownership_global_note_level(ownership, best->midi))
			best = &debug;
	}
	return best;
}

bool guitar_display_candidate_shadowed_by_non_guitar_pitch(const FullMixOwnership &ownership,
							   const NoteCandidate &candidate)
{
	if (candidate.midi < kGuitarMinMidi || candidate.midi > kGuitarMaxMidi)
		return false;

	const FullMixDebugCandidate *lower =
		strongest_same_pitch_non_guitar_debug_at_or_below(ownership, candidate.midi);
	if (!lower)
		return false;
	const float lower_level = ownership_global_note_level(ownership, lower->midi);
	if (lower_level < 0.18f)
		return false;

	const FullMixDebugCandidate *debug = full_mix_debug_for_midi(ownership, candidate.midi);
	if (debug && debug->midi == lower->midi)
		return false;

	if (!debug || candidate.midi - lower->midi < 12 || candidate.midi - lower->midi > 24)
		return false;

	const bool upper_harmonic_shadow =
		debug->owner == InstrumentKind::Guitar &&
		lower_level >= 0.42f &&
		debug->spectral_level <= lower->spectral_level * 1.28f &&
		debug->harmonicity >= 0.42f &&
		debug->spectral_centroid <= 0.32f &&
		debug->spectral_slope <= 0.16f &&
		debug->local_noise_level <= 0.14f &&
		(debug->keyboard_score + debug->other_score + debug->vocal_score) <= 0.22f;
	if (upper_harmonic_shadow)
		return true;

	return candidate.ownership_confidence <= 0.36f &&
	       lower_level >= ownership_global_note_level(ownership, candidate.midi) * 0.65f;
}

NoteCandidateList prune_shadowed_full_mix_guitar_display_candidates(const FullMixOwnership &ownership,
								    const NoteCandidateList &candidates)
{
	NoteCandidateList pruned;
	for (const NoteCandidate &candidate : candidates) {
		if (guitar_display_candidate_shadowed_by_non_guitar_pitch(ownership, candidate))
			continue;
		pruned.push_back(candidate);
	}
	return pruned;
}

void prefer_supported_lower_octave_candidates(NoteCandidateList &candidates, int min_midi,
					      float relative_floor, float global_floor)
{
	float global_best = 0.0f;
	for (const NoteCandidate &candidate : candidates)
		global_best = std::max(global_best, candidate.score);
	if (global_best <= 1.0e-6f)
		return;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		float best_score = 0.0f;
		int best_midi = -1;
		for (const NoteCandidate &candidate : candidates) {
			if (candidate.midi < min_midi || midi_pitch_class(candidate.midi) != pitch_class)
				continue;
			if (candidate.score > best_score) {
				best_score = candidate.score;
				best_midi = candidate.midi;
			}
		}
		if (best_midi < 0)
			continue;

		NoteCandidate *lowest_supported = nullptr;
		for (NoteCandidate &candidate : candidates) {
			if (candidate.midi < min_midi || candidate.midi >= best_midi ||
			    midi_pitch_class(candidate.midi) != pitch_class)
				continue;
			if (candidate.score < best_score * relative_floor ||
			    candidate.score < global_best * global_floor)
				continue;
			if (!lowest_supported || candidate.midi < lowest_supported->midi)
				lowest_supported = &candidate;
		}
		if (!lowest_supported)
			continue;
		lowest_supported->score = std::max(lowest_supported->score, best_score * 1.06f);
	}
}

void prefer_existing_candidate_midi(NoteCandidateList &candidates, int midi,
				    float score_scale, float confidence_floor)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return;

	const float strongest = strongest_candidate_score(candidates);
	if (strongest <= 1.0e-6f)
		return;

	for (NoteCandidate &candidate : candidates) {
		if (candidate.midi != midi)
			continue;
		candidate.score = std::max(candidate.score, strongest * score_scale);
		candidate.ownership_confidence =
			std::max(candidate.ownership_confidence, confidence_floor);
	}
}

void restore_supported_lower_guitar_debug_candidates(NoteCandidateList &candidates,
						     const FullMixOwnership &ownership)
{
	float global_best = strongest_candidate_score(candidates);
	if (global_best <= 1.0e-6f)
		global_best = 1.0f;

	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi < kGuitarMinMidi || debug.midi > kGuitarMaxMidi)
			continue;
		if (debug.owner != InstrumentKind::Guitar || debug.guitar_score < 0.70f)
			continue;
		if (debug.ownership_confidence < 0.70f && debug.spectral_level < 0.34f)
			continue;

		float strongest_upper = 0.0f;
		for (const NoteCandidate &candidate : candidates) {
			if (candidate.midi <= debug.midi || midi_pitch_class(candidate.midi) != midi_pitch_class(debug.midi))
				continue;
			strongest_upper = std::max(strongest_upper, candidate.score);
		}
		if (strongest_upper <= 1.0e-6f)
			continue;

		const float raw_level = ownership_global_note_level(ownership, debug.midi);
		if (raw_level < 0.16f && debug.spectral_level < 0.30f)
			continue;

		const float restored_score = std::max(strongest_upper * 1.06f, global_best * 0.30f);
		bool exists = false;
		for (NoteCandidate &candidate : candidates) {
			if (candidate.midi != debug.midi)
				continue;
			candidate.score = std::max(candidate.score, restored_score);
			candidate.ownership_confidence = std::max(candidate.ownership_confidence, 0.72f);
			exists = true;
		}
		if (!exists) {
			NoteCandidate candidate;
			candidate.midi = debug.midi;
			candidate.score = restored_score;
			candidate.ownership_confidence = 0.72f;
			candidates.push_back(candidate);
		}
	}
}

bool full_mix_debug_bass_display_supported(const FullMixDebugCandidate &debug)
{
	if (debug.midi < kBassMinMidi || debug.midi > kBassMaxMidi + 12)
		return false;

	const bool source_hinted_bass_body =
		debug.owner == InstrumentKind::Bass &&
		debug.bass_score >= 0.70f &&
		debug.spectral_level >= 0.08f &&
		debug.pitch_confidence >= 0.020f &&
		debug.periodicity >= 0.29f;
	const bool acoustic_upper_bass_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.ownership_confidence >= 0.70f &&
		debug.other_score >= 0.070f &&
		debug.other_score <= 0.14f &&
		debug.spectral_level >= 0.75f &&
		debug.pitch_confidence >= 0.70f &&
		debug.periodicity >= 0.74f &&
		debug.harmonic_fit_error <= 0.085f &&
		debug.harmonic_ratios[1] >= 0.30f &&
		debug.harmonic_ratios[2] <= 0.14f &&
		debug.harmonic_ratios[4] <= 0.070f;
	const bool picked_upper_bass_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.spectral_level >= 0.78f &&
		debug.spectral_level <= 0.98f &&
		debug.pitch_confidence >= 0.71f &&
		debug.periodicity >= 0.80f &&
		debug.spectral_slope <= 0.27f &&
		debug.harmonic_fit_error <= 0.20f &&
		debug.harmonic_ratios[1] >= 0.40f &&
		debug.harmonic_ratios[2] >= 0.040f &&
		debug.harmonic_ratios[4] >= 0.020f;
	const bool clean_keyboard_owned_bass_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 64 && debug.midi <= 76 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.74f &&
		debug.periodicity >= 0.74f &&
		debug.harmonic_fit_error <= 0.060f &&
		debug.local_noise_level <= 0.008f &&
		debug.harmonic_ratios[1] <= 0.060f &&
		debug.harmonic_ratios[2] <= 0.14f &&
		debug.harmonic_ratios[3] <= 0.014f &&
		debug.harmonic_ratios[4] <= 0.008f;
	const bool guitar_owned_upper_bass_edge =
		debug.owner == InstrumentKind::Guitar &&
		debug.ownership_confidence <= 0.78f &&
		debug.guitar_score >= 0.775f &&
		debug.keyboard_score <= 0.17f &&
		debug.spectral_level >= 0.70f &&
		debug.pitch_confidence >= 0.70f &&
		debug.periodicity >= 0.78f &&
		debug.harmonic_fit_error <= 0.070f;
	const bool guitar_owned_upper_bass_fundamental =
		debug.owner == InstrumentKind::Guitar &&
		debug.ownership_confidence <= 0.78f &&
		debug.guitar_score >= 0.775f &&
		debug.harmonic_ratios[1] <= 0.40f &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.78f &&
		debug.harmonic_fit_error <= 0.050f;
	const bool acoustic_high_bass_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 59 &&
		debug.midi <= 60 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.90f &&
		debug.periodicity >= 0.80f &&
		debug.harmonic_fit_error <= 0.045f &&
		debug.harmonic_ratios[1] >= 0.31f &&
		debug.harmonic_ratios[1] <= 0.36f &&
		debug.harmonic_ratios[2] >= 0.060f &&
		debug.harmonic_ratios[2] <= 0.080f &&
		debug.harmonic_ratios[3] <= 0.022f &&
		debug.harmonic_ratios[4] >= 0.018f &&
		debug.harmonic_ratios[4] <= 0.026f;
	const bool picked_high_bass_octave =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 59 &&
		debug.midi <= 76 &&
		debug.spectral_level >= 0.70f &&
		debug.pitch_confidence >= 0.70f &&
		debug.periodicity >= 0.86f &&
		debug.harmonic_fit_error <= 0.18f &&
		debug.harmonic_ratios[1] >= 0.40f &&
		debug.harmonic_ratios[1] <= 0.82f &&
		debug.harmonic_ratios[2] <= 0.10f &&
		debug.harmonic_ratios[3] >= 0.070f &&
		debug.harmonic_ratios[3] <= 0.15f &&
		debug.harmonic_ratios[4] <= 0.20f;
	const bool measured_slap_mid_bass_body =
		debug.owner == InstrumentKind::Guitar &&
		debug.midi >= 55 &&
		debug.midi <= 59 &&
		debug.spectral_level >= 0.98f &&
		debug.pitch_confidence >= 0.88f &&
		debug.periodicity >= 0.82f &&
		debug.harmonic_fit_error <= 0.065f &&
		debug.local_noise_level <= 0.15f &&
		debug.harmonic_ratios[1] >= 0.38f &&
		debug.harmonic_ratios[1] <= 0.49f &&
		debug.harmonic_ratios[2] >= 0.075f &&
		debug.harmonic_ratios[2] <= 0.23f &&
		debug.harmonic_ratios[3] >= 0.065f &&
		debug.harmonic_ratios[3] <= 0.13f &&
		debug.harmonic_ratios[4] >= 0.012f &&
		debug.harmonic_ratios[4] <= 0.040f;
	const bool other_owned_fretless_bass_body =
		debug.owner == InstrumentKind::Other &&
		debug.midi >= 60 &&
		debug.midi <= 64 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.95f &&
		debug.periodicity >= 0.95f &&
		debug.harmonic_fit_error <= 0.080f &&
		debug.local_noise_level <= 0.065f &&
		debug.harmonic_ratios[1] >= 0.58f &&
		debug.harmonic_ratios[2] >= 0.40f &&
		debug.harmonic_ratios[3] >= 0.31f &&
		debug.harmonic_ratios[4] >= 0.12f &&
		debug.harmonic_ratios[4] <= 0.15f;
	const bool keyboard_owned_high_slap_bass_octave =
		debug.owner == InstrumentKind::Keyboard &&
		debug.midi >= 72 &&
		debug.midi <= 76 &&
		debug.spectral_level >= 0.83f &&
		debug.pitch_confidence >= 0.78f &&
		debug.periodicity >= 0.90f &&
		debug.harmonic_fit_error <= 0.10f &&
		debug.local_noise_level <= 0.020f &&
		debug.harmonic_ratios[1] >= 0.20f &&
		debug.harmonic_ratios[1] <= 0.25f &&
		debug.harmonic_ratios[2] >= 0.30f &&
		debug.harmonic_ratios[2] <= 0.32f &&
		debug.harmonic_ratios[3] >= 0.25f &&
		debug.harmonic_ratios[3] <= 0.28f;
	const bool ambiguous_upper_synth_bass_body =
		debug.owner == InstrumentKind::Ambiguous &&
		debug.midi >= 60 &&
		debug.midi <= 64 &&
		debug.spectral_level >= 0.90f &&
		debug.pitch_confidence >= 0.91f &&
		debug.periodicity >= 0.86f &&
		debug.harmonic_fit_error <= 0.09f &&
		debug.harmonic_ratios[1] >= 0.36f &&
		debug.harmonic_ratios[1] <= 0.52f &&
		debug.harmonic_ratios[2] >= 0.08f &&
		debug.harmonic_ratios[2] <= 0.22f &&
		debug.harmonic_ratios[3] >= 0.08f &&
		debug.harmonic_ratios[3] <= 0.27f;
	return source_hinted_bass_body ||
	       acoustic_upper_bass_body || picked_upper_bass_body ||
	       clean_keyboard_owned_bass_octave ||
	       guitar_owned_upper_bass_edge ||
	       guitar_owned_upper_bass_fundamental ||
	       measured_slap_mid_bass_body ||
	       acoustic_high_bass_body || picked_high_bass_octave ||
	       other_owned_fretless_bass_body ||
	       keyboard_owned_high_slap_bass_octave ||
	       ambiguous_upper_synth_bass_body;
}

bool source_hinted_bass_fifth_harmonic(const FullMixOwnership &ownership,
				       const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Bass)
		return false;

	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &lower = ownership.debug_candidates[i];
		if (lower.owner != InstrumentKind::Bass || lower.midi >= debug.midi)
			continue;
		const int interval = debug.midi - lower.midi;
		if (interval % 12 == 7 &&
		    lower.spectral_level >= debug.spectral_level * 0.70f &&
		    lower.pitch_confidence >= debug.pitch_confidence * 0.70f)
			return true;
	}
	return false;
}

RangeResult recover_full_mix_bass_from_debug(const FullMixOwnership &ownership,
					     const std::array<float, kNoteProbeCount> &powers)
{
	RangeResult best;
	best.midi = -1;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (!full_mix_debug_bass_display_supported(debug))
			continue;
		if (source_hinted_bass_fifth_harmonic(ownership, debug))
			continue;

		int display_midi = debug.midi;
		float display_score = bass_candidate_score(powers, display_midi, true);
		for (int lower = display_midi - 12; lower >= kBassMinMidi && lower >= kFirstMidi; lower -= 12) {
			const float current_level = probe_level(powers, display_midi);
			const float lower_level = probe_level(powers, lower);
			const float lower_score = bass_candidate_score(powers, lower, true);
			if (lower_level < current_level * 0.035f && lower_score < display_score * 0.10f)
				break;
			display_midi = lower;
			display_score = lower_score;
		}

		float global_level = 0.0f;
		if (display_midi >= kFirstMidi && display_midi <= kLastMidi) {
			const std::size_t index = static_cast<std::size_t>(display_midi - kFirstMidi);
			global_level = std::max(global_level,
						std::clamp(ownership.global_note_levels[index], 0.0f, 1.0f));
		}
		if (debug.midi >= kFirstMidi && debug.midi <= kLastMidi) {
			const std::size_t index = static_cast<std::size_t>(debug.midi - kFirstMidi);
			global_level = std::max(global_level,
						std::clamp(ownership.global_note_levels[index], 0.0f, 1.0f));
		}
		if (global_level < 0.10f)
			continue;

		const float support =
			global_level * (0.45f + debug.pitch_confidence * 0.30f + debug.periodicity * 0.25f);
		if (support <= best.score)
			continue;
		best.midi = display_midi;
		best.score = support;
		best.confidence =
			std::clamp(0.12f + debug.pitch_confidence * 0.32f +
					   debug.periodicity * 0.24f + global_level * 0.24f,
				   0.0f, 0.82f);
	}
	return best;
}

bool high_zero_partial_alias_candidate(const FullMixDebugCandidate &debug)
{
	if (debug.owner != InstrumentKind::Ambiguous || debug.midi < kGuitarMaxMidi + 8)
		return false;
	if (debug.spectral_centroid > 0.001f || debug.spectral_slope > 0.001f ||
	    debug.harmonicity > 0.001f || debug.harmonic_fit_error > 0.065f ||
	    debug.local_noise_level > 0.145f || debug.periodicity < 0.60f)
		return false;

	for (std::size_t i = 1; i < debug.harmonic_ratios.size(); ++i) {
		if (debug.harmonic_ratios[i] > 0.001f)
			return false;
	}
	return true;
}

bool low_bass_candidate_shadowed_by_upper_keyboard_pitch(const FullMixOwnership &ownership,
							 const RangeResult &bass_note)
{
	if (bass_note.midi <= kDefaultBassMaxMidi || bass_note.midi > 59)
		return false;

	const int pitch_class = midi_pitch_class(bass_note.midi);
	bool upper_keyboard_support = false;
	for (const NoteCandidate &candidate : ownership.keyboard_candidates) {
		if (candidate.midi < bass_note.midi + 12)
			continue;
		if (midi_pitch_class(candidate.midi) != pitch_class)
			continue;
		if (candidate.score >= 0.16f || candidate.ownership_confidence >= 0.42f) {
			upper_keyboard_support = true;
			break;
		}
	}
	if (!upper_keyboard_support)
		return false;

	bool non_bass_low_alias = false;
	bool upper_keyboard_debug = false;
	bool real_bass_debug = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (midi_pitch_class(debug.midi) != pitch_class)
			continue;

		const bool bass_owned =
			debug.owner == InstrumentKind::Bass ||
			(debug.bass_score >= 0.34f &&
			 debug.bass_score >= std::max({debug.keyboard_score, debug.guitar_score,
						       debug.vocal_score, debug.other_score}) * 0.84f);
		if (debug.midi <= bass_note.midi + 2 && bass_owned)
			real_bass_debug = true;

		if (std::abs(debug.midi - bass_note.midi) <= 1 &&
		    debug.owner != InstrumentKind::Bass &&
		    debug.bass_score <= 0.22f &&
		    debug.spectral_level >= 0.35f &&
		    debug.pitch_confidence >= 0.18f)
			non_bass_low_alias = true;

		if (debug.midi >= bass_note.midi + 12 &&
		    (debug.owner == InstrumentKind::Keyboard || debug.keyboard_score >= 0.45f) &&
		    debug.spectral_level >= 0.25f)
			upper_keyboard_debug = true;
	}

	return non_bass_low_alias && upper_keyboard_debug && !real_bass_debug;
}

bool full_mix_bass_shadowed_by_keyboard_alias(const FullMixOwnership &ownership, const RangeResult &bass_note)
{
	if (bass_note.midi < kFirstMidi || bass_note.midi > kBassMaxMidi)
		return false;

	const int pitch_class = ((bass_note.midi % 12) + 12) % 12;
	bool keyboard_pitch_support = false;
	for (const NoteCandidate &candidate : ownership.keyboard_candidates) {
		if (candidate.midi < bass_note.midi)
			continue;
		if (((candidate.midi % 12) + 12) % 12 != pitch_class)
			continue;
		if (candidate.score >= 0.16f || candidate.ownership_confidence >= 0.42f) {
			keyboard_pitch_support = true;
			break;
		}
	}
	if (!keyboard_pitch_support)
		return false;

	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (!high_zero_partial_alias_candidate(debug))
			continue;
		if (debug.midi < bass_note.midi + 24)
			continue;
		if (((debug.midi % 12) + 12) % 12 == pitch_class)
			return true;
	}
	return low_bass_candidate_shadowed_by_upper_keyboard_pitch(ownership, bass_note);
}

bool strongest_candidate(const NoteCandidateList &candidates, NoteCandidate &candidate)
{
	if (candidates.empty())
		return false;

	candidate = candidates.front();
	for (const NoteCandidate &current : candidates) {
		if (current.score > candidate.score)
			candidate = current;
	}
	return true;
}

void demote_full_mix_vocal_candidate(FullMixOwnership &ownership, const NoteCandidate &candidate)
{
	if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
		return;

	const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
	ownership.vocal[index] = false;
	remove_candidate_midi(ownership.vocal_candidates, candidate.midi);
	ownership.ambiguous[index] = true;
	ownership.ambiguous_candidates.push_back(candidate);
}

void demote_full_mix_other_candidate(FullMixOwnership &ownership, const NoteCandidate &candidate)
{
	if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
		return;

	const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
	ownership.other[index] = false;
	remove_candidate_midi(ownership.other_candidates, candidate.midi);
	ownership.ambiguous[index] = true;
	ownership.ambiguous_candidates.push_back(candidate);
}

void stabilize_full_mix_vocal_ownership(FullMixOwnership &ownership, int &tracked_midi, int &pending_midi,
					int &pending_hits, int &tracked_misses, float &tracked_score)
{
	NoteCandidate candidate;
	if (!strongest_candidate(ownership.vocal_candidates, candidate)) {
		pending_midi = -1;
		pending_hits = 0;
		if (tracked_midi >= 0 && tracked_misses < 2) {
			++tracked_misses;
			tracked_score *= 0.72f;
		} else {
			tracked_midi = -1;
			tracked_misses = 0;
			tracked_score = 0.0f;
		}
		return;
	}

	if (tracked_midi >= 0 && candidate.midi == tracked_midi) {
		tracked_score = std::max(tracked_score * 0.80f, candidate.score);
		pending_midi = -1;
		pending_hits = 0;
		tracked_misses = 0;
		return;
	}

	if (pending_midi == candidate.midi)
		++pending_hits;
	else {
		pending_midi = candidate.midi;
		pending_hits = 1;
	}

	if (pending_hits >= 2) {
		tracked_midi = candidate.midi;
		tracked_score = candidate.score;
		pending_midi = -1;
		pending_hits = 0;
		tracked_misses = 0;
		return;
	}

	demote_full_mix_vocal_candidate(ownership, candidate);
}

void stabilize_sparse_full_mix_other_ownership(FullMixOwnership &ownership,
					       std::array<NoteTrackingState, kNoteProbeCount> &tracking)
{
	std::array<bool, kNoteProbeCount> current = {};
	for (const NoteCandidate &candidate : ownership.other_candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;
		current[candidate.midi - kFirstMidi] = true;
	}

	for (std::size_t i = 0; i < tracking.size(); ++i) {
		NoteTrackingState &note = tracking[i];
		if (current[i]) {
			note.consecutive_hits = std::min(note.consecutive_hits + 1, 1000);
			note.consecutive_misses = 0;
			if (note.consecutive_hits >= kNoteAttackConfirmFrames)
				note.confirmed = true;
			note.envelope = 1.0f;
		} else {
			note.consecutive_hits = 0;
			note.consecutive_misses = std::min(note.consecutive_misses + 1, 1000);
			note.envelope = std::max(0.0f, note.envelope - 0.34f);
			if (note.consecutive_misses > 2 || note.envelope <= 0.0f)
				note = {};
		}
	}

	if (ownership.other_candidates.size() != 1)
		return;

	const NoteCandidate candidate = ownership.other_candidates.front();
	if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
		return;
	if (tracking[candidate.midi - kFirstMidi].confirmed)
		return;

	demote_full_mix_other_candidate(ownership, candidate);
}

float relative_timbre_weight(const TimbreMix &mix, TimbreKind kind)
{
	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return 0.0f;
	return mix.weights[static_cast<std::size_t>(kind)] / fundamental;
}

bool measured_full_mix_sustained_voice_profile(const NoteEvidence &evidence, int midi, float second,
					       float third, float fourth, float fifth)
{
	const bool choir_vowel_stack_voice =
		midi >= 60 && midi <= 76 &&
		evidence.spectral_level >= 0.70f &&
		evidence.pitch_confidence >= 0.60f &&
		evidence.periodicity >= 0.80f &&
		evidence.harmonic_fit_error <= 0.35f &&
		evidence.local_noise_level <= 0.18f &&
		evidence.spectral_slope >= 0.050f &&
		evidence.spectral_slope <= 0.32f &&
		second >= 0.95f && second <= 1.45f &&
		third >= 0.42f && third <= 0.70f &&
		fourth >= 0.030f && fourth <= 0.085f &&
		fifth <= 0.045f;
	const bool voice_lead_sustained_voice =
		midi >= 55 && midi <= 64 &&
		evidence.spectral_level >= 0.90f &&
		evidence.pitch_confidence >= 0.84f &&
		evidence.periodicity >= 0.80f &&
		evidence.harmonic_fit_error <= 0.11f &&
		evidence.local_noise_level <= 0.18f &&
		evidence.spectral_centroid <= 0.24f &&
		evidence.spectral_slope <= 0.20f &&
		second >= 0.35f && second <= 0.75f &&
		third >= 0.13f && third <= 0.26f &&
		fourth <= 0.055f &&
		fifth <= 0.055f;
	const bool synth_voice_sustained_voice =
		midi >= 60 && midi <= 66 &&
		evidence.spectral_level >= 0.75f &&
		evidence.pitch_confidence >= 0.60f &&
		evidence.periodicity >= 0.80f &&
		evidence.harmonic_fit_error <= 0.35f &&
		evidence.local_noise_level <= 0.18f &&
		evidence.spectral_centroid <= 0.30f &&
		evidence.spectral_slope <= 0.13f &&
		second >= 1.0f && second <= 1.35f &&
		third >= 0.12f && third <= 0.20f &&
		fourth <= 0.045f &&
		fifth <= 0.035f;
	return choir_vowel_stack_voice || voice_lead_sustained_voice || synth_voice_sustained_voice;
}

bool full_mix_vocal_profile_supported(const NoteEvidence &evidence, int midi, float second, float third,
				      float fourth, float fifth, bool polyphonic_vocal_context)
{
	if (polyphonic_vocal_context)
		return false;
	const bool high_register = midi >= 72;
	if (evidence.simultaneous_onset > (high_register ? 0.35f : 0.42f))
		return false;
	if (evidence.spectral_level < (high_register ? 0.38f : 0.28f))
		return false;
	if (evidence.periodicity < (high_register ? 0.42f : 0.34f))
		return false;
	if (evidence.local_noise_level > (high_register ? 0.22f : 0.34f) ||
	    evidence.harmonic_fit_error > (high_register ? 0.40f : 0.58f))
		return false;
	if (evidence.spectral_centroid > (high_register ? 0.24f : 0.36f))
		return false;
	if (!high_register && (second < 0.025f || third < 0.008f))
		return false;

	const bool clean_sustained_like_partials =
		second <= (high_register ? 0.10f : 0.18f) &&
		third <= (high_register ? 0.065f : 0.115f) &&
		fourth <= (high_register ? 0.050f : 0.085f);
	const bool near_pure_tone_voice =
		second <= 0.045f && third <= 0.025f && fourth <= 0.018f && evidence.spectral_slope <= 0.10f;
	const bool midrange_sustained_voice =
		!high_register && second <= 0.22f && third <= 0.13f && fourth <= 0.095f &&
		evidence.pitch_stability >= 0.34f && evidence.spectral_slope <= 0.30f;
	const bool rich_sustained_voice =
		!high_register && second >= 0.08f && second <= 0.32f && third <= 0.22f &&
		fourth <= 0.145f && fifth <= 0.085f && evidence.spectral_slope <= 0.42f;
	const bool measured_sustained_voice =
		measured_full_mix_sustained_voice_profile(evidence, midi, second, third, fourth, fifth);
	return clean_sustained_like_partials || near_pure_tone_voice || midrange_sustained_voice ||
	       rich_sustained_voice || measured_sustained_voice;
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
	evidence.harmonic_ratios = {1.0f, second, third, fourth, fifth};
	const float keyboard_weight = relative_timbre_weight(mix, TimbreKind::Keyboard);
	const float guitar_weight = relative_timbre_weight(mix, TimbreKind::Guitar);
	const float other_weight = relative_timbre_weight(mix, TimbreKind::Other);
	const float note_strength = evidence.spectral_level;
	const float clean_pitch_bonus = evidence.pitch_confidence * 0.12f;
	const float noise_penalty = std::clamp(1.0f - evidence.local_noise_level * 0.42f, 0.42f, 1.0f);
	const float fit_penalty = std::clamp(1.0f - evidence.harmonic_fit_error * 0.32f, 0.52f, 1.0f);

	std::array<float, 4> scores = {};
	const bool vocal_supported =
		candidate.midi >= kFullMixVocalMinMidi && candidate.midi <= kVocalMaxMidi &&
		full_mix_vocal_profile_supported(evidence, candidate.midi, second, third, fourth, fifth,
						 polyphonic_vocal_context);
	const bool measured_sustained_voice =
		vocal_supported &&
		measured_full_mix_sustained_voice_profile(evidence, candidate.midi, second, third, fourth, fifth);
	const bool low_other_candidate = candidate.midi >= kGuitarMinMidi && candidate.midi < 55;
	const bool lower_mid_other_candidate = candidate.midi >= 55 && candidate.midi < 60;
	const bool lower_mid_bright_other_candidate =
		lower_mid_other_candidate && second >= 0.14f && second <= 0.34f &&
		third >= 0.075f && third <= 0.22f &&
		fourth <= 0.12f && fifth <= 0.10f &&
		evidence.spectral_centroid >= 0.18f;
	const bool low_other_profile_supported =
		(low_other_candidate && second >= 0.30f && third >= 0.12f &&
		 (fourth >= 0.075f || fifth >= 0.045f) &&
		 (other_weight >= guitar_weight * 1.05f || fourth >= 0.14f || fifth >= 0.075f)) ||
		lower_mid_bright_other_candidate ||
		(lower_mid_other_candidate && second >= 0.38f && third >= 0.18f &&
		 (fourth >= 0.20f || fifth >= 0.12f || other_weight >= guitar_weight * 1.38f));
	const bool sparse_acoustic_guitar_profile =
		candidate.midi >= 52 && candidate.midi <= 76 &&
		second >= 0.24f && second <= 0.48f &&
		third >= 0.010f && third <= 0.090f &&
		fourth <= 0.085f && fifth <= 0.065f &&
		evidence.spectral_slope <= 0.115f &&
		evidence.spectral_centroid <= 0.220f &&
		!lower_mid_bright_other_candidate;
	const bool clean_plucked_guitar_profile =
		candidate.midi >= 52 && candidate.midi <= 76 &&
		second >= 0.12f && second <= 0.24f &&
		third >= 0.025f && third <= 0.090f &&
		fourth >= 0.035f && fourth <= 0.100f &&
		fifth <= 0.080f &&
		evidence.spectral_centroid >= 0.10f && evidence.spectral_centroid <= 0.22f &&
		evidence.spectral_slope <= 0.18f &&
		evidence.local_noise_level <= 0.09f &&
		!lower_mid_bright_other_candidate;
	const bool thin_plucked_guitar_profile =
		candidate.midi >= 52 && candidate.midi <= 76 &&
		second >= 0.24f && second <= 0.50f &&
		third >= 0.006f && third <= 0.030f &&
		fourth >= 0.010f && fourth <= 0.060f &&
		fifth <= 0.025f &&
		evidence.spectral_centroid >= 0.08f && evidence.spectral_centroid <= 0.18f &&
		evidence.spectral_slope <= 0.08f &&
		evidence.local_noise_level <= 0.04f &&
		!lower_mid_bright_other_candidate;
	const bool upper_clean_guitar_profile =
		candidate.midi >= 67 && candidate.midi <= 80 &&
		second >= 0.070f && second <= 0.140f &&
		third >= 0.045f && third <= 0.120f &&
		fourth >= 0.045f && fourth <= 0.120f &&
		fifth <= 0.025f &&
		evidence.spectral_centroid >= 0.09f && evidence.spectral_centroid <= 0.18f &&
		evidence.spectral_slope <= 0.20f &&
		evidence.local_noise_level <= 0.030f &&
		!lower_mid_bright_other_candidate;
	const bool upper_harmonic_guitar_profile =
		candidate.midi >= 60 && candidate.midi <= kGuitarMaxMidi &&
		second >= 0.55f &&
		fifth <= 0.22f &&
		evidence.harmonicity >= 2.55f &&
		evidence.local_noise_level <= 0.008f &&
		!lower_mid_bright_other_candidate;
	const bool distorted_harmonic_guitar_profile =
		candidate.midi >= 64 && candidate.midi <= 72 &&
		second >= 1.20f &&
		third >= 3.20f &&
		fourth >= 0.90f &&
		fifth <= 0.45f &&
		evidence.spectral_centroid >= 0.58f &&
		evidence.spectral_slope >= 2.0f &&
		!lower_mid_bright_other_candidate;
	const bool competing_timbres = competing_full_mix_timbres(keyboard_weight, guitar_weight, other_weight);
	const bool blended_partials = blended_full_mix_upper_partials(second, third, fourth, fifth);
	const bool force_blended_ambiguous =
		!vocal_supported && !low_other_profile_supported && (competing_timbres || blended_partials) &&
		temporal.simultaneous_onset >= 0.18f;
	if (force_blended_ambiguous && competing_timbres) {
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
	if (force_blended_ambiguous && blended_partials)
		return InstrumentKind::Ambiguous;

	const bool normal_keyboard_profile_supported =
		candidate.midi >= 48 && candidate.midi <= 83 && second <= 0.56f;
	const bool high_keyboard_profile_supported =
		candidate.midi > kVocalMaxMidi && candidate.midi <= 95 && second <= 0.42f && third <= 0.20f &&
		(other_weight <= keyboard_weight * 1.45f || second <= 0.20f);
	const bool octave_stack_guitar_profile =
		candidate.midi >= 48 && candidate.midi <= 76 &&
		second >= 0.62f && third <= 0.08f && fourth >= 0.18f && fifth >= 0.06f;
	if (normal_keyboard_profile_supported || high_keyboard_profile_supported) {
		scores[0] = keyboard_weight * 1.18f + std::max(0.0f, 0.50f - second) * 0.30f +
			    std::max(0.0f, 0.16f - third) * 0.08f + clean_pitch_bonus;
		if (evidence.pitch_stability >= 0.62f && evidence.onset_strength <= 0.45f)
			scores[0] += 0.06f;
		if (evidence.simultaneous_onset > 0.0f)
			scores[0] += evidence.simultaneous_onset * 0.08f;
		if (high_keyboard_profile_supported)
			scores[0] += 0.08f;
		if (evidence.spectral_centroid > 0.34f || evidence.spectral_slope > 0.18f)
			scores[0] *= 0.78f;
	}
	if (candidate.midi >= kGuitarMinMidi && candidate.midi <= kGuitarMaxMidi &&
	    ((second >= 0.12f && third >= 0.035f) || octave_stack_guitar_profile ||
	     sparse_acoustic_guitar_profile || clean_plucked_guitar_profile ||
	     thin_plucked_guitar_profile || upper_clean_guitar_profile ||
	     upper_harmonic_guitar_profile || distorted_harmonic_guitar_profile)) {
		scores[1] = guitar_weight * 1.18f + second * 0.24f + third * 0.16f;
		if (octave_stack_guitar_profile)
			scores[1] += 0.60f + fourth * 0.34f + fifth * 0.20f;
		if (sparse_acoustic_guitar_profile)
			scores[1] += 0.48f + second * 0.14f;
		if (clean_plucked_guitar_profile)
			scores[1] += 0.52f + fourth * 0.18f;
		if (thin_plucked_guitar_profile)
			scores[1] += 0.46f + second * 0.12f;
		if (upper_clean_guitar_profile)
			scores[1] += 0.42f + fourth * 0.18f;
		if (upper_harmonic_guitar_profile)
			scores[1] += 0.86f + std::min(second, 1.8f) * 0.12f;
		if (distorted_harmonic_guitar_profile)
			scores[1] += 3.20f + std::min(third, 6.0f) * 0.18f + fourth * 0.10f;
		if (evidence.onset_strength >= 0.35f)
			scores[1] += evidence.onset_strength * 0.08f;
		if (evidence.decay_rate >= 0.18f)
			scores[1] += evidence.decay_rate * 0.05f;
		if (evidence.simultaneous_onset > 0.0f)
			scores[1] += evidence.simultaneous_onset * 0.04f;
		if (evidence.spectral_centroid >= 0.10f && evidence.spectral_centroid <= 0.42f)
			scores[1] += 0.08f;
		if (evidence.spectral_slope >= 0.035f && evidence.spectral_slope <= 0.30f)
			scores[1] += 0.05f;
		if (!upper_harmonic_guitar_profile && !distorted_harmonic_guitar_profile &&
		    (second > 0.75f || fourth > 0.36f))
			scores[1] *= 0.72f;
		if (lower_mid_bright_other_candidate && !octave_stack_guitar_profile)
			scores[1] = 0.0f;
	}
	if (vocal_supported) {
		const bool high_register = candidate.midi >= 72;
		const float second_target = high_register ? 0.10f : 0.18f;
		const float third_target = high_register ? 0.065f : 0.115f;
		scores[2] = (high_register ? 0.74f : 1.34f) +
			    std::max(0.0f, second_target - second) * (high_register ? 1.8f : 1.25f) +
			    std::max(0.0f, third_target - third) * (high_register ? 1.3f : 0.95f);
		if (evidence.onset_strength > 0.72f && evidence.pitch_stability < 0.30f)
			scores[2] *= 0.80f;
		if (evidence.simultaneous_onset > 0.0f)
			scores[2] *= std::clamp(1.0f - evidence.simultaneous_onset * 0.32f, 0.55f, 1.0f);
		if (evidence.pitch_stability >= 0.55f)
			scores[2] += high_register ? 0.05f : 0.12f;
		if (note_strength < 0.52f)
			scores[2] *= 0.82f;
		if (measured_sustained_voice)
			scores[2] += 0.46f;
		if (!high_register) {
			scores[0] *= 0.28f;
			if (second < 0.20f)
				scores[1] *= 0.80f;
			if (lower_mid_bright_other_candidate)
				scores[2] *= 0.65f;
			if (sparse_acoustic_guitar_profile)
				scores[2] *= 0.30f;
			if (clean_plucked_guitar_profile)
				scores[2] *= 0.38f;
			if (thin_plucked_guitar_profile || upper_clean_guitar_profile ||
			    upper_harmonic_guitar_profile || distorted_harmonic_guitar_profile)
				scores[2] *= 0.36f;
		}
	}
	const bool normal_other_profile_supported =
		candidate.midi >= 60 && candidate.midi <= kOtherMaxMidi && second >= 0.24f &&
		(fourth >= 0.06f || fifth >= 0.035f);
	if (low_other_profile_supported || normal_other_profile_supported) {
		scores[3] = other_weight * 1.12f + second * 0.18f + third * 0.14f + fourth * 0.10f;
		if (octave_stack_guitar_profile)
			scores[3] *= 0.40f;
		if (evidence.pitch_stability >= 0.45f)
			scores[3] += 0.04f;
		if (evidence.harmonicity >= 0.62f || evidence.spectral_centroid >= 0.20f)
			scores[3] += 0.10f;
		if (low_other_profile_supported)
			scores[3] += 0.24f;
		if (lower_mid_bright_other_candidate)
			scores[3] += 0.40f;
		if (upper_harmonic_guitar_profile)
			scores[3] *= 0.58f;
		if (distorted_harmonic_guitar_profile)
			scores[3] *= 0.34f;
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
	const bool supported_vocal_winner = best == 2 && vocal_supported;
	const bool supported_measured_sustained_voice_winner = best == 2 && measured_sustained_voice;
	const bool supported_octave_stack_guitar_winner = best == 1 && octave_stack_guitar_profile;
	const bool supported_sparse_acoustic_guitar_winner = best == 1 && sparse_acoustic_guitar_profile;
	const bool supported_clean_plucked_guitar_winner = best == 1 && clean_plucked_guitar_profile;
	const bool supported_thin_plucked_guitar_winner = best == 1 && thin_plucked_guitar_profile;
	const bool supported_upper_clean_guitar_winner = best == 1 && upper_clean_guitar_profile;
	const bool supported_upper_harmonic_guitar_winner = best == 1 && upper_harmonic_guitar_profile;
	const bool supported_distorted_harmonic_guitar_winner =
		best == 1 && distorted_harmonic_guitar_profile;
	const bool supported_lower_mid_bright_other_winner = best == 3 && lower_mid_bright_other_candidate;
	const bool supported_low_other_winner = best == 3 && low_other_profile_supported;
	const bool blended_non_vocal = (competing_timbres || blended_partials) && !supported_vocal_winner;
	const float probability_floor =
		supported_measured_sustained_voice_winner ? 0.40f :
		(supported_octave_stack_guitar_winner || supported_sparse_acoustic_guitar_winner ||
		 supported_clean_plucked_guitar_winner || supported_thin_plucked_guitar_winner ||
		 supported_upper_clean_guitar_winner ||
		 supported_upper_harmonic_guitar_winner ||
		 supported_distorted_harmonic_guitar_winner) ? 0.38f :
		supported_lower_mid_bright_other_winner ? 0.34f :
		(supported_vocal_winner || supported_low_other_winner) ? 0.44f :
		blended_non_vocal ? 0.68f :
				     0.65f;
	const float margin_floor =
		supported_measured_sustained_voice_winner ? 0.04f :
		(supported_octave_stack_guitar_winner || supported_sparse_acoustic_guitar_winner ||
		 supported_clean_plucked_guitar_winner || supported_thin_plucked_guitar_winner ||
		 supported_upper_clean_guitar_winner ||
		 supported_upper_harmonic_guitar_winner ||
		 supported_distorted_harmonic_guitar_winner) ? 0.08f :
		supported_lower_mid_bright_other_winner ? 0.04f :
		(supported_vocal_winner || supported_low_other_winner) ? 0.12f :
		blended_non_vocal ? 0.24f :
				     0.20f;
	if (best_probability < probability_floor || best_probability - second_probability < margin_floor)
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
					  std::array<float, kNoteProbeCount> &current_note_levels,
					  AnalysisInputMode source_hint)
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

	int simultaneous_onset_count = 0;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;
		const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
		const TemporalNoteFeatures temporal =
			temporal_note_features(current_note_levels[index], previous_note_levels[index]);
		if (current_note_levels[index] >= 0.20f && temporal.onset_strength >= 0.28f)
			++simultaneous_onset_count;
	}
	const float simultaneous_onset_context =
		simultaneous_onset_count >= 2 ?
			std::clamp(static_cast<float>(simultaneous_onset_count - 1) / 4.0f, 0.0f, 1.0f) :
			0.0f;

	int vocal_range_candidate_count = 0;
	int dominant_vocal_candidate_midi = -1;
	float dominant_vocal_candidate_score = 0.0f;
	float second_vocal_candidate_score = 0.0f;
	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFullMixVocalMinMidi || candidate.midi > kVocalMaxMidi ||
		    candidate.score < strongest_score * 0.35f)
			continue;

		bool upper_harmonic = false;
		for (const NoteCandidate &lower : candidates) {
			if (lower.midi >= candidate.midi)
				continue;
			if (likely_selected_harmonic(lower, candidate)) {
				upper_harmonic = true;
				break;
			}
		}
		if (upper_harmonic)
			continue;

		++vocal_range_candidate_count;
		if (candidate.score > dominant_vocal_candidate_score) {
			second_vocal_candidate_score = dominant_vocal_candidate_score;
			dominant_vocal_candidate_score = candidate.score;
			dominant_vocal_candidate_midi = candidate.midi;
		} else {
			second_vocal_candidate_score = std::max(second_vocal_candidate_score, candidate.score);
		}
	}
	const bool dominant_vocal_candidate =
		dominant_vocal_candidate_midi >= 0 &&
		(second_vocal_candidate_score <= 1.0e-6f ||
		 dominant_vocal_candidate_score >= second_vocal_candidate_score * 1.20f);

	for (const NoteCandidate &candidate : candidates) {
		if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi)
			continue;

		NoteEvidence evidence;
		const std::size_t note_index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
		TemporalNoteFeatures temporal =
			temporal_note_features(current_note_levels[note_index], previous_note_levels[note_index]);
		if (temporal.onset_strength >= 0.18f)
			temporal.simultaneous_onset = simultaneous_onset_context;
		const bool polyphonic_vocal_context =
			vocal_range_candidate_count >= 2 &&
			(!dominant_vocal_candidate || candidate.midi != dominant_vocal_candidate_midi);
		InstrumentKind owner =
			choose_full_mix_owner(powers, candidate, strongest_score, polyphonic_vocal_context, temporal,
					      evidence);
		apply_full_mix_source_hint_owner(source_hint, candidate, evidence, owner, candidates.size());
		append_full_mix_debug_candidate(ownership, candidate, evidence, owner);

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
			break;
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
	mirror_high_full_mix_guitar_candidates(ownership);
	mirror_ambiguous_full_mix_candidates(ownership);

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
	char label[256] = {};
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

bool chord_label_has_exact_component(const char *label, const char *component);

bool chord_candidate_compatible(const ChordCandidate &lhs, const ChordCandidate &rhs)
{
	if (lhs.mask == rhs.mask)
		return true;
	if (lhs.root != rhs.root)
		return false;
	return (lhs.mask & ~rhs.mask) == 0 || (rhs.mask & ~lhs.mask) == 0;
}

float chroma_mask_max(const std::array<float, 12> &chroma, uint16_t mask)
{
	float result = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if ((mask & static_cast<uint16_t>(1u << pitch_class)) != 0)
			result = std::max(result, chroma[pitch_class]);
	}
	return result;
}

bool chord_extension_tones_are_strong(const std::array<float, 12> &chroma, uint16_t core_mask,
				      uint16_t extension_mask)
{
	if (extension_mask == 0)
		return false;

	const float extension_max = chroma_mask_max(chroma, extension_mask);
	const float core_max = chroma_mask_max(chroma, core_mask);
	return extension_max >= kChordStrongExtensionToneFloor &&
	       extension_max >= core_max * kChordStrongExtensionCoreRatio;
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
			const uint16_t extension_mask = best_candidate.mask & ~candidate.mask;
			if (chord_extension_tones_are_strong(chroma, candidate.mask, extension_mask))
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
		if (chord_label_has_exact_component(best.label, candidate.label))
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

float note_visual_loudness(float rms, float rms_floor = kNoteRmsFloor)
{
	return std::clamp((rms - rms_floor) / (kFullNoteRms - rms_floor), 0.0f, 1.0f);
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

void prune_note_grid_below_level(NoteGrid &grid, float min_level)
{
	for (NoteCell &cell : grid.cells) {
		if (cell.active && cell.level < min_level)
			cell = {};
	}
	for (auto &row : grid.rows) {
		for (NoteCell &cell : row) {
			if (cell.active && cell.level < min_level)
				cell = {};
		}
	}
}

void write_note_grid_cell(NoteGrid &grid, const NoteCandidate &candidate, float strongest_score, float visual_loudness)
{
	const int pitch_class = ((candidate.midi % 12) + 12) % 12;
	NoteCell cell;
	write_octave(cell.label, sizeof(cell.label), candidate.midi);
	const float ownership_scale =
		candidate.ownership_confidence <= 0.24f ? std::clamp(candidate.ownership_confidence, 0.0f, 1.0f) :
							  1.0f;
	const float level = strongest_score > 1.0e-6f ?
				    std::clamp(candidate.score / strongest_score * visual_loudness * ownership_scale,
					       0.0f, 1.0f) :
				    0.0f;
	if (level <= 1.0e-6f)
		return;
	cell.level = level;
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
					     float energy, float rms, int max_notes, float relative_floor = 0.0f)
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

	NoteCandidateList sorted = candidates;
	std::sort(sorted.begin(), sorted.end(), [](const NoteCandidate &a, const NoteCandidate &b) {
		if (a.score != b.score)
			return a.score > b.score;
		return a.midi < b.midi;
	});
	const float score_floor = strongest_score * std::clamp(relative_floor, 0.0f, 1.0f);
	int written = 0;
	for (const NoteCandidate &candidate : sorted) {
		if (written >= std::max(1, max_notes))
			break;
		if (candidate.score < score_floor)
			continue;
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
	struct TrackedDisplayCandidate {
		int midi = -1;
		float level = 0.0f;
		bool current = false;
	};
	FixedList<TrackedDisplayCandidate, kNoteProbeCount> candidates;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
		const float level = tracking[index].envelope;
		if (level > 0.0f)
			candidates.push_back(TrackedDisplayCandidate{midi, level, raw_levels[index] > 0.0f});
	}
	std::sort(candidates.begin(), candidates.end(),
		  [](const TrackedDisplayCandidate &a, const TrackedDisplayCandidate &b) {
			  if (a.current != b.current)
				  return a.current;
			  if (a.level != b.level)
				  return a.level > b.level;
			  return a.midi < b.midi;
		  });

	int written = 0;
	for (const TrackedDisplayCandidate &candidate : candidates) {
		write_note_grid_cell(grid, NoteCandidate{candidate.midi, candidate.level}, 1.0f, 1.0f);
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

int note_grid_active_pitch_class_count(const NoteGrid &grid)
{
	int count = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		bool active = grid.cells[pitch_class].active;
		for (const auto &row : grid.rows)
			active = active || row[pitch_class].active;
		if (active)
			++count;
	}
	return count;
}

bool note_grid_has_midi(const NoteGrid &grid, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active && cell.midi == midi)
				return true;
		}
	}
	return false;
}

float note_grid_midi_level(const NoteGrid &grid, int midi)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return 0.0f;
	const int pitch_class = ((midi % 12) + 12) % 12;
	float level = 0.0f;
	if (grid.cells[pitch_class].active && grid.cells[pitch_class].midi == midi)
		level = std::max(level, grid.cells[pitch_class].level);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active && cell.midi == midi)
				level = std::max(level, cell.level);
		}
	}
	return level;
}

void prefer_supported_lower_octave_display(NoteGrid &grid, InstrumentState &state,
					   const std::array<float, kNoteProbeCount> &powers,
					   int min_midi, int max_promoted_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	max_promoted_midi = std::min(max_promoted_midi, kLastMidi);
	bool changed = false;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		FixedList<NoteCell, kNoteRowCount> active_cells;
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi)
				active_cells.push_back(cell);
		}
		if (active_cells.empty())
			continue;

		const NoteCell primary = active_cells.front();
		if (primary.midi <= min_midi)
			continue;

		const float primary_raw = probe_level(powers, primary.midi);
		NoteCell promoted = {};
		for (int midi = std::min(max_promoted_midi, primary.midi - 12); midi >= min_midi; --midi) {
			if (midi_pitch_class(midi) != pitch_class)
				continue;
			const int octave_delta = primary.midi - midi;
			if (octave_delta % 12 != 0)
				continue;

			const float visible_level = note_grid_midi_level(grid, midi);
			const float raw_level = probe_level(powers, midi);
			const bool visible_supported =
				visible_level >= std::max(0.045f, primary.level * 0.38f);
			const bool raw_supported =
				primary_raw > 1.0e-6f && raw_level >= primary_raw * 0.30f &&
				active_cells.size() >= kNoteRowCount;
			if (!visible_supported && !raw_supported)
				continue;

			const float support_score =
				std::max(visible_level, raw_supported ? primary.level : 0.0f);

			promoted = {};
			write_octave(promoted.label, sizeof(promoted.label), midi);
			promoted.level = std::max({visible_level, support_score, primary.level});
			promoted.midi = midi;
			promoted.active = true;
			break;
		}

		if (!promoted.active || active_cells.front().midi == promoted.midi)
			continue;

		std::array<NoteCell, kNoteRowCount> reordered = {};
		reordered[0] = promoted;
		std::size_t write = 1;
		std::array<bool, kNoteRowCount> used = {};
		while (write < reordered.size()) {
			std::size_t best = active_cells.size();
			for (std::size_t i = 0; i < active_cells.size(); ++i) {
				if (used[i] || active_cells[i].midi == promoted.midi)
					continue;
				if (best == active_cells.size() || active_cells[i].level > active_cells[best].level ||
				    (active_cells[i].level == active_cells[best].level &&
				     active_cells[i].midi < active_cells[best].midi))
					best = i;
			}
			if (best == active_cells.size())
				break;
			used[best] = true;
			reordered[write++] = active_cells[best];
		}

		for (std::size_t row = 0; row < grid.rows.size(); ++row)
			grid.rows[row][pitch_class] = reordered[row];
		grid.cells[pitch_class] = promoted;
		changed = true;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_visible_lower_octave_primary(NoteGrid &grid, InstrumentState &state, int min_midi,
					 float relative_floor, int preferred_root,
					 float absolute_floor = 0.24f,
					 int deep_low_promotion_floor = kFirstMidi)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		FixedList<NoteCell, kNoteRowCount> active_cells;
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi)
				active_cells.push_back(cell);
		}
		if (active_cells.empty())
			continue;

		NoteCell lower = {};
		NoteCell primary = active_cells.front();
		const NoteCell &display = grid.cells[pitch_class];
		if (display.active && display.midi > primary.midi && display.level > primary.level)
			primary = display;
		for (const NoteCell &cell : active_cells) {
			if (cell.midi >= primary.midi || cell.midi < min_midi)
				continue;
			if (cell.midi < deep_low_promotion_floor && primary.midi - cell.midi > 12)
				continue;
			if (cell.level < std::max(absolute_floor, primary.level * relative_floor))
				continue;
			if (!lower.active || cell.midi < lower.midi) {
				lower = cell;
			}
		}
		if (!lower.active)
			continue;

		lower.level = std::max(lower.level, primary.level);
		std::array<NoteCell, kNoteRowCount> reordered = {};
		reordered[0] = lower;
		std::size_t write = 1;
		std::array<bool, kNoteRowCount> used = {};
		while (write < reordered.size()) {
			std::size_t best = active_cells.size();
			for (std::size_t i = 0; i < active_cells.size(); ++i) {
				if (used[i] || active_cells[i].midi == lower.midi)
					continue;
				if (best == active_cells.size() || active_cells[i].level > active_cells[best].level ||
				    (active_cells[i].level == active_cells[best].level &&
				     active_cells[i].midi < active_cells[best].midi))
					best = i;
			}
			if (best == active_cells.size())
				break;
			used[best] = true;
			reordered[write++] = active_cells[best];
		}

		for (std::size_t row = 0; row < grid.rows.size(); ++row)
			grid.rows[row][pitch_class] = reordered[row];
		grid.cells[pitch_class] = lower;
		changed = true;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

bool promote_note_grid_primary_midi(NoteGrid &grid, int midi, float level)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return false;

	const int pitch_class = midi_pitch_class(midi);
	NoteCell promoted = {};
	write_octave(promoted.label, sizeof(promoted.label), midi);
	promoted.level = std::clamp(level, 0.0f, 1.0f);
	promoted.midi = midi;
	promoted.active = true;

	std::array<NoteCell, kNoteRowCount> reordered = {};
	reordered[0] = promoted;
	std::size_t write = 1;
	for (const auto &row : grid.rows) {
		const NoteCell &cell = row[pitch_class];
		if (!cell.active || cell.midi == promoted.midi || write >= reordered.size())
			continue;
		reordered[write++] = cell;
	}
	for (std::size_t row = 0; row < grid.rows.size(); ++row)
		grid.rows[row][pitch_class] = reordered[row];
	grid.cells[pitch_class] = promoted;
	return true;
}

void prefer_debug_supported_high_bass_primary(NoteGrid &grid, InstrumentState &state,
					      const FullMixOwnership &ownership,
					      const std::array<float, kNoteProbeCount> &powers,
					      int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.owner != InstrumentKind::Bass || !full_mix_debug_bass_display_supported(debug))
				continue;
			if (debug.midi < 55 || debug.midi > kFullMixCleanHighSynthBassMaxMidi ||
			    debug.midi <= primary.midi || midi_pitch_class(debug.midi) != pitch_class)
				continue;

			const float high_level = probe_level(powers, debug.midi);
			const float lower_octave_level = probe_level(powers, debug.midi - 12);
			if (high_level <= 1.0e-6f || lower_octave_level >= high_level * 0.12f)
				continue;
			if (note_grid_midi_level(grid, debug.midi - 12) >= 0.55f)
				continue;

			if (supported_midi < 0 || debug.midi < supported_midi) {
				supported_midi = debug.midi;
				supported_level = std::max(primary.level,
							   ownership_global_note_level(ownership, debug.midi));
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_debug_supported_mid_bass_primary(NoteGrid &grid, InstrumentState &state,
					     const FullMixOwnership &ownership, int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_confidence = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.owner != InstrumentKind::Bass || !full_mix_debug_bass_display_supported(debug))
				continue;
			if (primary.midi >= 36 || debug.midi < 36 || debug.midi > 43 ||
			    debug.midi != primary.midi + 12 || midi_pitch_class(debug.midi) != pitch_class)
				continue;
			if (debug.ownership_confidence < 0.80f || debug.pitch_confidence > 0.32f ||
			    debug.periodicity < 0.40f)
				continue;

			const float raw_level = ownership_global_note_level(ownership, debug.midi);
			const float promote_level = std::max(raw_level, primary.level);
			if (supported_midi < 0 || debug.ownership_confidence > supported_confidence) {
				supported_midi = debug.midi;
				supported_level = promote_level;
				supported_confidence = debug.ownership_confidence;
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_probe_supported_lower_bass_primary(NoteGrid &grid, InstrumentState &state,
					       const FullMixOwnership &ownership,
					       const std::array<float, kNoteProbeCount> &powers,
					       int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active || primary.midi < 55 || primary.midi > 59)
			continue;

		const int lower_midi = primary.midi - 12;
		if (lower_midi < kBassMinMidi || midi_pitch_class(lower_midi) != pitch_class)
			continue;
		if (note_grid_midi_level(grid, lower_midi) >= 0.55f)
			continue;

		const float primary_probe = probe_level(powers, primary.midi);
		const float lower_probe = probe_level(powers, lower_midi);
		if (primary_probe <= 1.0e-6f || lower_probe < primary_probe * 0.020f ||
		    lower_probe > primary_probe * 0.18f)
			continue;

		bool supported_primary = false;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi != primary.midi || debug.owner != InstrumentKind::Bass)
				continue;
			if (!full_mix_debug_bass_display_supported(debug))
				continue;
			if (debug.ownership_confidence < 0.95f || debug.pitch_confidence < 0.70f ||
			    debug.periodicity < 0.85f)
				continue;
			supported_primary = true;
			break;
		}
		if (!supported_primary)
			continue;

		changed = promote_note_grid_primary_midi(grid, lower_midi, primary.level) || changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
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

	int strongest_pitch_class = -1;
	float strongest_level = 0.0f;
	if (strongest_grid_pitch_class(grid, strongest_pitch_class, strongest_level) &&
	    !chord.tones[strongest_pitch_class])
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
	const NoteCandidateList notes =
		allow_extensions ? note_grid_candidates(grid) :
				   prune_adjacent_keyboard_candidates(note_grid_candidates(grid));
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
		std::array<float, 12> extension_chroma = {};
		float level_sum = 0.0f;
		float extension_level_sum = 0.0f;
		int distinct_pitch_classes = 0;
		int extension_distinct_pitch_classes = 0;
		const float relative_level_floor = notes[start].midi < 40 ? 0.62f : 0.50f;
		const float extension_level_floor = allow_extensions ? 0.22f : relative_level_floor;
		for (std::size_t i = start; i < last; ++i) {
			const int pitch_class = ((notes[i].midi % 12) + 12) % 12;
			if (notes[i].score >= strongest * extension_level_floor) {
				if (extension_chroma[pitch_class] <= 0.0f)
					++extension_distinct_pitch_classes;
				extension_chroma[pitch_class] = std::max(extension_chroma[pitch_class], notes[i].score);
				extension_level_sum += notes[i].score;
			}
			if (notes[i].score >= strongest * relative_level_floor) {
				if (chroma[pitch_class] <= 0.0f)
					++distinct_pitch_classes;
				chroma[pitch_class] = std::max(chroma[pitch_class], notes[i].score);
				level_sum += notes[i].score;
			}
		}

		if (distinct_pitch_classes < 2 && extension_distinct_pitch_classes < 2)
			continue;

		const int cluster_root = preferred_root >= 0 && chroma[preferred_root % 12] > 0.0f ?
						 preferred_root :
						 ((notes[start].midi % 12) + 12) % 12;
		ChordResult chord;
		if (distinct_pitch_classes >= 2 && longest_chromatic_run(chroma) < 4) {
			chord = simplify_weak_keyboard_ninth(chroma,
							    detect_chord(chroma, cluster_root, allow_extensions),
							    allow_extensions);
		}
		if (allow_extensions && extension_distinct_pitch_classes >= 2 &&
		    longest_chromatic_run(extension_chroma) < 4) {
			const ChordResult extension_chord =
				simplify_weak_keyboard_ninth(extension_chroma,
							    detect_chord(extension_chroma, cluster_root,
									 allow_extensions),
							    allow_extensions);
			if (extension_chord.root >= 0 && extension_chord.confidence >= kChordConfidenceFloor &&
			    !extension_chord.uncertain && extension_chord.label[0] &&
			    extension_chord.label[0] != '-' &&
			    chord_label_has_keyboard_ninth(extension_chord.label)) {
				chord = extension_chord;
				chroma = extension_chroma;
				level_sum = extension_level_sum;
				distinct_pitch_classes = extension_distinct_pitch_classes;
			}
		}
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

ChordResult detect_caged_guitar_chord(const std::array<float, 12> &chroma, int preferred_root,
				      bool allow_altered = false)
{
	ChordResult best;
	float best_score = 0.0f;
	static constexpr float kToneThreshold = 0.08f;

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
		best.margin = best.confidence;
		best.uncertain = false;
		std::snprintf(best.label, sizeof(best.label), "%s%s", note_name(root), suffix);
	};

	for (int root = 0; root < 12; ++root) {
		consider(root, "", {0, 4, 7}, 0.16f);
		consider(root, "m", {0, 3, 7}, 0.16f);
		consider(root, "sus2", {0, 2, 7}, 0.12f);
		consider(root, "sus4", {0, 5, 7}, 0.12f);
		consider(root, "pow", {0, 7}, 0.04f);
		if (allow_altered) {
			consider(root, "dim", {0, 3, 6}, 0.10f);
			consider(root, "aug", {0, 4, 8}, 0.10f);
		}
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

bool chord_label_has_exact_component(const char *label, const char *component)
{
	if (!label || !component || !*component)
		return false;
	const std::size_t component_len = std::strlen(component);
	const char *cursor = label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		if (len == component_len && std::strncmp(cursor, component, component_len) == 0)
			return true;
		if (!end)
			break;
		cursor = end + 1;
	}
	return false;
}

bool chord_label_contains_all_components(const char *label, const char *required)
{
	if (!label || !required || !*label || !*required || label[0] == '-' || required[0] == '-')
		return false;

	const char *cursor = required;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		if (len == 0 || len >= 32)
			return false;

		char component[32] = {};
		std::memcpy(component, cursor, len);
		component[len] = '\0';
		if (!chord_label_has_exact_component(label, component))
			return false;

		if (!end)
			break;
		cursor = end + 1;
	}
	return true;
}

int chord_label_component_count(const char *label)
{
	if (!label || !*label || label[0] == '-')
		return 0;

	int count = 0;
	const char *cursor = label;
	while (*cursor) {
		++count;
		const char *end = std::strchr(cursor, '=');
		if (!end)
			break;
		cursor = end + 1;
	}
	return count;
}

bool chord_label_has_root_component(const char *label, int root)
{
	if (!label || root < 0)
		return false;
	const char *cursor = label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) && parsed.root == root)
			return true;
		if (!end)
			break;
		cursor = end + 1;
	}
	return false;
}

bool chord_label_has_root_third_component(const char *label, int root)
{
	if (!label || root < 0)
		return false;
	const char *cursor = label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) && parsed.root == root &&
		    (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor))
			return true;
		if (!end)
			break;
		cursor = end + 1;
	}
	return false;
}

bool chord_label_has_unambiguous_root_third_component(const char *label, int root)
{
	if (!label || root < 0)
		return false;
	bool has_major = false;
	bool has_minor = false;
	const char *cursor = label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) && parsed.root == root) {
			has_major = has_major || parsed.quality == RootChordQuality::Major;
			has_minor = has_minor || parsed.quality == RootChordQuality::Minor;
		}
		if (!end)
			break;
		cursor = end + 1;
	}
	return has_major != has_minor;
}

float note_grid_pitch_level(const NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	float level = 0.0f;
	if (grid.cells[pitch_class].active)
		level = std::max(level, grid.cells[pitch_class].level);
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max(level, row[pitch_class].level);
	}
	return level;
}

void guitar_harmonic_support_from_display(const NoteGrid &grid, int midi, int &count, float &strongest)
{
	static constexpr int kGuitarHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
	count = 0;
	strongest = 0.0f;
	for (int interval : kGuitarHarmonicIntervals) {
		const float level = note_grid_midi_level(grid, midi + interval);
		strongest = std::max(strongest, level);
		if (level >= 0.20f)
			++count;
	}
}

bool low_guitar_harmonic_primary_supported(const NoteGrid &grid, int midi)
{
	if (midi > 47)
		return false;
	int harmonic_count = 0;
	float strongest_harmonic = 0.0f;
	guitar_harmonic_support_from_display(grid, midi, harmonic_count, strongest_harmonic);
	return note_grid_midi_level(grid, midi + 12) >= 0.20f &&
	       note_grid_midi_level(grid, midi + 19) >= 0.20f &&
	       harmonic_count >= 2 &&
	       strongest_harmonic >= 0.70f;
}

bool full_mix_debug_guitar_note_supported(const FullMixOwnership &ownership, int midi)
{
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi != midi)
			continue;
		if (debug.owner != InstrumentKind::Guitar || debug.guitar_score < 0.70f)
			continue;
		if (debug.ownership_confidence < 0.70f && debug.spectral_level < 0.34f)
			continue;
		const float raw_level = ownership_global_note_level(ownership, debug.midi);
		const bool confident_harmonic_body =
			debug.ownership_confidence >= 0.80f &&
			debug.other_score >= 0.70f &&
			debug.pitch_confidence <= 0.080f &&
			debug.periodicity >= 0.35f &&
			debug.harmonic_fit_error >= 1.0f;
		if (raw_level < 0.16f && debug.spectral_level < 0.30f && !confident_harmonic_body)
			continue;
		return true;
	}
	return false;
}

float full_mix_debug_keyboard_note_score(const FullMixOwnership &ownership, int midi)
{
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	float best = -1.0f;
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi != midi)
			continue;
		if (debug.owner != InstrumentKind::Keyboard || debug.keyboard_score < 0.68f)
			continue;
		if (debug.ownership_confidence < 0.68f && debug.spectral_level < 0.28f)
			continue;
		const float raw_level = ownership_global_note_level(ownership, debug.midi);
		if (raw_level < 0.08f && debug.spectral_level < 0.24f)
			continue;
		best = std::max(best, debug.ownership_confidence);
	}
	return best;
}

float full_mix_debug_other_note_score(const FullMixOwnership &ownership, int midi)
{
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	float best = -1.0f;
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.midi != midi || debug.owner != InstrumentKind::Other)
			continue;
		if (debug.ownership_confidence < 0.80f)
			continue;
		if (debug.periodicity < 0.30f && debug.spectral_level < 0.28f)
			continue;
		const float raw_level = ownership_global_note_level(ownership, debug.midi);
		if (raw_level < 0.025f && debug.spectral_level < 0.24f)
			continue;
		best = std::max(best, debug.ownership_confidence);
	}
	return best;
}

void prefer_debug_supported_lower_other_octave_primary(NoteGrid &grid, InstrumentState &state,
						       const FullMixOwnership &ownership,
						       int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active) {
				primary = cell;
				break;
			}
		}
		if (!primary.active)
			continue;

		const float primary_debug_score =
			std::max(0.0f, full_mix_debug_other_note_score(ownership, primary.midi));
		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < min_midi || debug.midi >= primary.midi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			const float debug_score = full_mix_debug_other_note_score(ownership, debug.midi);
			if (debug_score < 0.80f || debug_score + 0.02f < primary_debug_score)
				continue;

			const float visible_level = note_grid_midi_level(grid, debug.midi);
			if (visible_level <= 0.0f)
				continue;
			const float raw_level = ownership_global_note_level(ownership, debug.midi);
			const int octave_delta = primary.midi - debug.midi;
			const bool one_octave = octave_delta <= 12;
			const bool visible_supported = visible_level >= 0.08f;
			const bool weak_visible_but_measured =
				visible_level >= 0.025f && raw_level >= 0.040f && debug.periodicity >= 0.32f;
			const bool deep_low_supported =
				octave_delta <= 24 && debug.midi >= 40 && visible_level >= 0.50f &&
				raw_level >= 0.30f && debug_score >= 0.90f && debug.periodicity >= 0.55f;
			if (!(one_octave && (visible_supported || weak_visible_but_measured)) &&
			    !deep_low_supported)
				continue;

			const float score = std::max(visible_level, raw_level);
			if (supported_midi < 0 || debug_score > supported_debug_score ||
			    (debug_score == supported_debug_score && score > supported_level) ||
			    (debug_score == supported_debug_score && score == supported_level &&
			     debug.midi < supported_midi)) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug_score;
			}
		}
		if (supported_midi < 0 || supported_midi == primary.midi)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

NoteCell note_grid_primary_cell_for_pitch_class(const NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	for (const auto &row : grid.rows) {
		const NoteCell &cell = row[pitch_class];
		if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi &&
		    midi_pitch_class(cell.midi) == pitch_class)
			return cell;
	}
	const NoteCell &cell = grid.cells[pitch_class];
	if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi &&
	    midi_pitch_class(cell.midi) == pitch_class)
		return cell;
	return {};
}

void promote_source_hinted_other_debug_primaries(NoteGrid &grid, InstrumentState &state,
						 const FullMixOwnership &ownership,
						 const std::array<float, kNoteProbeCount> &powers,
						 int min_midi, int preferred_root,
						 bool allow_probe_lower_octave,
						 bool allow_independent_fundamental)
{
	min_midi = std::max(min_midi, kFirstMidi);
	float strongest_probe = 0.0f;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi)
		strongest_probe = std::max(strongest_probe, probe_level(powers, midi));
	if (strongest_probe <= 1.0e-6f)
		return;

	std::array<int, 12> promoted_midis = {};
	std::array<float, 12> promoted_levels = {};
	promoted_midis.fill(-1);

	auto consider = [&](int midi, float level, bool prefer_lowest) {
		if (midi < min_midi || midi > kOtherMaxMidi)
			return;
		const int pitch_class = midi_pitch_class(midi);
		if (promoted_midis[pitch_class] < 0 ||
		    (prefer_lowest ? midi < promoted_midis[pitch_class] :
				     midi > promoted_midis[pitch_class]) ||
		    (midi == promoted_midis[pitch_class] && level > promoted_levels[pitch_class])) {
			promoted_midis[pitch_class] = midi;
			promoted_levels[pitch_class] = std::clamp(level, 0.0f, 1.0f);
		}
	};

	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (std::size_t i = 0; i < debug_count; ++i) {
		const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
		if (debug.owner != InstrumentKind::Other || debug.midi < min_midi ||
		    debug.midi > kOtherMaxMidi)
			continue;
		if (debug.ownership_confidence < 0.72f || debug.other_score < 0.70f)
			continue;
		if (debug.periodicity < 0.30f && debug.pitch_confidence < 0.030f &&
		    debug.spectral_level < 0.080f)
			continue;

		const int pitch_class = midi_pitch_class(debug.midi);
		const NoteCell primary = note_grid_primary_cell_for_pitch_class(grid, pitch_class);
		if (primary.active && debug.midi < primary.midi) {
			const float debug_level = std::max(ownership_global_note_level(ownership, debug.midi),
							  debug.spectral_level);
			consider(debug.midi, std::max({primary.level, debug_level, debug.other_score}), true);
		}

		const bool source_hinted_exact_debug_primary =
			(allow_probe_lower_octave || allow_independent_fundamental) &&
			!primary.active &&
			debug.pitch_confidence >= 0.30f &&
			debug.periodicity >= 0.55f;
		if (source_hinted_exact_debug_primary) {
			const float debug_level = std::max(ownership_global_note_level(ownership, debug.midi),
							  debug.spectral_level);
			consider(debug.midi,
				 std::max({debug_level, debug.other_score, debug.pitch_confidence, 0.72f}),
				 allow_independent_fundamental);
		}

		const bool independent_string_fundamental =
			allow_independent_fundamental &&
			!primary.active &&
			debug.other_score >= 0.80f &&
			debug.keyboard_score <= 0.20f &&
			debug.guitar_score <= 0.25f &&
			debug.vocal_score <= 0.05f &&
			debug.spectral_level >= 0.12f &&
			debug.pitch_confidence >= 0.12f &&
			debug.periodicity >= 0.40f;
		if (independent_string_fundamental) {
			const float debug_level = std::max(ownership_global_note_level(ownership, debug.midi),
							  debug.spectral_level);
			consider(debug.midi, std::max({debug_level, debug.other_score, 0.80f}), false);
		}

		if (!allow_probe_lower_octave)
			continue;
		const int lower_midi = debug.midi - 12;
		if (lower_midi < min_midi || midi_pitch_class(lower_midi) != pitch_class)
			continue;
		const float debug_probe = probe_level(powers, debug.midi);
		const float lower_probe = probe_level(powers, lower_midi);
		const float source_hint_probe_floor = allow_independent_fundamental ? 0.030f : 0.080f;
		const float source_hint_debug_probe_floor = allow_independent_fundamental ? 0.080f : 0.20f;
		const bool lower_probe_supported =
			lower_probe >= strongest_probe * source_hint_probe_floor &&
			(debug_probe <= 1.0e-6f || lower_probe >= debug_probe * source_hint_debug_probe_floor);
		if (!lower_probe_supported)
			continue;
		const float normalized = std::clamp(lower_probe / strongest_probe, 0.0f, 1.0f);
		consider(lower_midi, std::max({normalized, debug.other_score, 0.72f}), true);
	}

	bool changed = false;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (promoted_midis[pitch_class] < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, promoted_midis[pitch_class],
							 promoted_levels[pitch_class]) ||
			  changed;
	}
	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_strong_visible_lower_other_octave_primary(NoteGrid &grid, InstrumentState &state,
						      int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi) {
				primary = cell;
				break;
			}
		}
		if (!primary.active) {
			const NoteCell &cell = grid.cells[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi)
				primary = cell;
		}
		if (!primary.active)
			continue;

		NoteCell lower = {};
		auto consider = [&](const NoteCell &cell) {
			if (!cell.active || cell.midi < min_midi || cell.midi >= primary.midi ||
			    cell.midi > kLastMidi || midi_pitch_class(cell.midi) != pitch_class)
				return;
			const int octave_delta = primary.midi - cell.midi;
			if (octave_delta > 12 || cell.level < 0.60f)
				return;
			if (!lower.active || cell.midi < lower.midi ||
			    (cell.midi == lower.midi && cell.level > lower.level))
				lower = cell;
		};

		consider(grid.cells[pitch_class]);
		for (const auto &row : grid.rows)
			consider(row[pitch_class]);

		if (!lower.active)
			continue;
		changed = promote_note_grid_primary_midi(grid, lower.midi,
							 std::max(lower.level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_probe_supported_lower_synth_primary(NoteGrid &grid, InstrumentState &state,
						const FullMixOwnership &ownership,
						const std::array<float, kNoteProbeCount> &powers,
						int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi) {
				primary = cell;
				break;
			}
		}
		if (!primary.active) {
			const NoteCell &cell = grid.cells[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi)
				primary = cell;
		}
		if (!primary.active)
			continue;

		const int lower_midi = primary.midi - 12;
		if (lower_midi < min_midi || midi_pitch_class(lower_midi) != pitch_class)
			continue;

		const float primary_probe = probe_level(powers, primary.midi);
		const float lower_probe = probe_level(powers, lower_midi);
		if (primary_probe <= 1.0e-6f)
			continue;
		const bool lower_probe_supported =
			(lower_probe >= primary_probe * 0.020f && lower_probe <= primary_probe * 1.15f) ||
			(lower_midi >= 60 && lower_probe >= primary_probe * 2.0f);
		const float lower_fifth = note_grid_midi_level(grid, lower_midi + 19);
		const float lower_major_third = note_grid_midi_level(grid, lower_midi + 28);
		const bool lower_harmonic_stack_supported =
			primary.midi >= 60 && lower_midi + 28 <= kLastMidi &&
			lower_fifth >= primary.level * 0.28f &&
			lower_major_third >= primary.level * 0.12f &&
			lower_fifth + lower_major_third >= primary.level * 0.45f;
		if (!lower_probe_supported && !lower_harmonic_stack_supported)
			continue;

		bool supported_primary = false;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi != primary.midi || debug.owner != InstrumentKind::Other)
				continue;
			if (debug.ownership_confidence < 0.70f || debug.pitch_confidence < 0.45f ||
			    debug.periodicity < 0.55f)
				continue;
			supported_primary = true;
			break;
		}
		if (!supported_primary)
			continue;

		changed = promote_note_grid_primary_midi(grid, lower_midi, primary.level) || changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_measured_string_lower_other_octave_primary(NoteGrid &grid, InstrumentState &state,
						       const FullMixOwnership &ownership,
						       int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active) {
				primary = cell;
				break;
			}
		}
		if (!primary.active)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < min_midi || debug.midi >= primary.midi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			if (primary.midi - debug.midi != 12)
				continue;
			if (debug.owner != InstrumentKind::Other)
				continue;
			if (debug.ownership_confidence < 0.775f || debug.ownership_confidence >= 0.80f)
				continue;
			if (debug.pitch_confidence < 0.65f || debug.periodicity < 0.70f)
				continue;

			const float visible_level = note_grid_midi_level(grid, debug.midi);
			const float raw_level = ownership_global_note_level(ownership, debug.midi);
			if (visible_level < 0.10f)
				continue;

			const float score = std::max({visible_level, raw_level, debug.ownership_confidence});
			if (supported_midi < 0 || debug.ownership_confidence > supported_debug_score ||
			    (debug.ownership_confidence == supported_debug_score && score > supported_level) ||
			    (debug.ownership_confidence == supported_debug_score && score == supported_level &&
			     debug.midi < supported_midi)) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug.ownership_confidence;
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_weak_debug_string_lower_other_octave_primary(NoteGrid &grid, InstrumentState &state,
							 const FullMixOwnership &ownership,
							 int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active) {
				primary = cell;
				break;
			}
		}
		if (!primary.active)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < min_midi || debug.midi >= primary.midi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			if (primary.midi - debug.midi != 12)
				continue;
			if (debug.owner != InstrumentKind::Other)
				continue;
			if (debug.ownership_confidence < 0.82f || debug.ownership_confidence > 0.87f)
				continue;
			if (debug.pitch_confidence > 0.18f || debug.periodicity < 0.32f ||
			    debug.periodicity > 0.46f)
				continue;

			const float visible_level = note_grid_midi_level(grid, debug.midi);
			if (visible_level < 0.025f || visible_level > 0.060f)
				continue;

			const float score = std::max(visible_level, debug.ownership_confidence);
			if (supported_midi < 0 || debug.ownership_confidence > supported_debug_score ||
			    (debug.ownership_confidence == supported_debug_score && score > supported_level) ||
			    (debug.ownership_confidence == supported_debug_score && score == supported_level &&
			     debug.midi < supported_midi)) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug.ownership_confidence;
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_debug_supported_upper_other_octave_primary(NoteGrid &grid, InstrumentState &state,
						       const FullMixOwnership &ownership,
						       int min_midi, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active) {
				primary = cell;
				break;
			}
		}
		if (!primary.active)
			continue;

		const float primary_debug_score =
			std::max(0.0f, full_mix_debug_other_note_score(ownership, primary.midi));
		if (primary_debug_score >= 0.80f)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi <= primary.midi || debug.midi < min_midi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			const int octave_delta = debug.midi - primary.midi;
			if (octave_delta != 12)
				continue;
			const float debug_score = full_mix_debug_other_note_score(ownership, debug.midi);
			if (debug_score < 0.85f)
				continue;
			const float visible_level = note_grid_midi_level(grid, debug.midi);
			const float raw_level = ownership_global_note_level(ownership, debug.midi);
			if (visible_level < 0.45f || raw_level < 0.20f)
				continue;

			const float score = std::max(visible_level, raw_level);
			if (supported_midi < 0 || debug_score > supported_debug_score ||
			    (debug_score == supported_debug_score && score > supported_level)) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug_score;
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_debug_supported_keyboard_octave_primary(NoteGrid &grid, InstrumentState &state,
						    const FullMixOwnership &ownership,
						    int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active)
			continue;
		const float primary_debug_score =
			std::max(0.0f, full_mix_debug_keyboard_note_score(ownership, primary.midi));

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < kKeyboardMinMidi || debug.midi > kKeyboardMaxMidi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			const float debug_score = full_mix_debug_keyboard_note_score(ownership, debug.midi);
			if (debug_score < primary_debug_score + 0.025f)
				continue;
			const float visible_level = note_grid_midi_level(grid, debug.midi);
			if (visible_level <= 0.0f)
				continue;
			const float score = std::max(visible_level, ownership_global_note_level(ownership, debug.midi));
			if (supported_midi < 0 || debug_score > supported_debug_score ||
			    (debug_score == supported_debug_score && score > supported_level) ||
			    (debug_score == supported_debug_score && score == supported_level &&
			     std::abs(debug.midi - primary.midi) < std::abs(supported_midi - primary.midi))) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug_score;
			}
		}
		if (supported_midi < 0 || supported_midi == primary.midi)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_exact_debug_keyboard_lower_octave_primary(NoteGrid &grid, InstrumentState &state,
						      const FullMixOwnership &ownership,
						      int preferred_root)
{
	static constexpr int kExactDebugKeyboardPromotionMinMidi = 40;
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active) {
				primary = cell;
				break;
			}
		}
		if (!primary.active)
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		float supported_debug_score = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < kExactDebugKeyboardPromotionMinMidi || debug.midi >= primary.midi ||
			    debug.midi > kKeyboardMaxMidi || midi_pitch_class(debug.midi) != pitch_class)
				continue;
			const int octave_delta = primary.midi - debug.midi;
			if (octave_delta != 12 && octave_delta != 24)
				continue;

			const float debug_score = full_mix_debug_keyboard_note_score(ownership, debug.midi);
			if (debug_score < 0.70f)
				continue;
			const bool keyboard_body_supported =
				debug.other_score >= 0.10f ||
				debug.harmonic_ratios[2] >= 0.004f ||
				debug.harmonic_ratios[3] >= 0.004f;
			if (!keyboard_body_supported)
				continue;
			const float visible_level = note_grid_midi_level(grid, debug.midi);
			const float raw_level = ownership_global_note_level(ownership, debug.midi);
			if (visible_level < 0.08f && raw_level < 0.08f)
				continue;

			const float score = std::max(visible_level, raw_level);
			if (supported_midi < 0 || debug_score > supported_debug_score ||
			    (debug_score == supported_debug_score && score > supported_level) ||
			    (debug_score == supported_debug_score && score == supported_level &&
			     debug.midi > supported_midi)) {
				supported_midi = debug.midi;
				supported_level = score;
				supported_debug_score = debug_score;
			}
		}
		if (supported_midi < 0)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void promote_low_guitar_display_fundamentals(NoteGrid &display_grid, InstrumentState &display_state,
					     const NoteGrid &analysis_grid, int preferred_root)
{
	if (note_grid_active_pitch_class_count(display_grid) > 8)
		return;

	bool changed = false;
	for (int midi = kGuitarMinMidi; midi <= 52; ++midi) {
		if (note_grid_has_midi(display_grid, midi))
			continue;

		const float analysis_level = note_grid_midi_level(analysis_grid, midi);

		float strongest_visible_octave = 0.0f;
		int visible_octave_count = 0;
		for (int octave_midi = midi + 12; octave_midi <= kGuitarMaxMidi; octave_midi += 12) {
			const float octave_level = note_grid_midi_level(display_grid, octave_midi);
			if (octave_level <= 0.0f)
				continue;
			strongest_visible_octave = std::max(strongest_visible_octave, octave_level);
			if (octave_level >= 0.20f)
				++visible_octave_count;
		}
		const bool direct_supported = analysis_level >= 0.050f;
		const bool low_harmonic_supported = low_guitar_harmonic_primary_supported(display_grid, midi);
		if (!direct_supported && !low_harmonic_supported)
			continue;

		int harmonic_count = 0;
		float strongest_harmonic = 0.0f;
		guitar_harmonic_support_from_display(display_grid, midi, harmonic_count, strongest_harmonic);
		if (strongest_visible_octave < 0.75f && strongest_harmonic < 0.75f)
			continue;
		if (visible_octave_count < 1 && harmonic_count < 2)
			continue;

		const float promote_level = std::max({strongest_visible_octave, strongest_harmonic, 0.80f});
		changed = promote_note_grid_primary_midi(display_grid, midi, promote_level) || changed;
	}

	if (changed)
		write_note_grid_label(display_state, display_grid, preferred_root);
}

void prefer_supported_guitar_lower_octave_primary(NoteGrid &grid, InstrumentState &state,
						  const FullMixOwnership &ownership, int min_midi,
						  float relative_floor, int preferred_root)
{
	min_midi = std::max(min_midi, kFirstMidi);
	bool changed = false;

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		FixedList<NoteCell, kNoteRowCount> active_cells;
		for (const auto &row : grid.rows) {
			const NoteCell &cell = row[pitch_class];
			if (cell.active && cell.midi >= kFirstMidi && cell.midi <= kLastMidi)
				active_cells.push_back(cell);
		}
		if (active_cells.empty())
			continue;

		const NoteCell primary = active_cells.front();
		NoteCell lower = {};
		for (const NoteCell &cell : active_cells) {
			if (cell.midi >= primary.midi || cell.midi < min_midi)
				continue;
			if (cell.level < std::max(0.24f, primary.level * relative_floor))
				continue;

			const bool low_harmonic_supported =
				low_guitar_harmonic_primary_supported(grid, cell.midi);
			if (!low_harmonic_supported &&
			    !full_mix_debug_guitar_note_supported(ownership, cell.midi))
				continue;
			if (!lower.active || cell.midi < lower.midi)
				lower = cell;
		}
		if (!lower.active)
			continue;

		lower.level = std::max(lower.level, primary.level);
		changed = promote_note_grid_primary_midi(grid, lower.midi, lower.level) || changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void prefer_debug_supported_guitar_octave_primary(NoteGrid &grid, InstrumentState &state,
						  const FullMixOwnership &ownership, int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active || low_guitar_harmonic_primary_supported(grid, primary.midi))
			continue;
		if (full_mix_debug_guitar_note_supported(ownership, primary.midi))
			continue;

		int supported_midi = -1;
		float supported_level = 0.0f;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < kGuitarMinMidi || debug.midi > kGuitarMaxMidi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			if (!full_mix_debug_guitar_note_supported(ownership, debug.midi))
				continue;
			if (supported_midi < 0 || debug.midi < supported_midi) {
				supported_midi = debug.midi;
				supported_level = std::max(primary.level,
							   ownership_global_note_level(ownership, debug.midi));
			}
		}
		if (supported_midi < 0 || supported_midi == primary.midi)
			continue;
		changed = promote_note_grid_primary_midi(grid, supported_midi,
							 std::max(supported_level, primary.level)) ||
			  changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void promote_guitar_debug_lower_octave_primary(NoteGrid &grid, InstrumentState &state,
					       const FullMixOwnership &ownership, int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active)
			continue;

		const FullMixDebugCandidate *lower = nullptr;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi < kGuitarMinMidi || debug.midi >= primary.midi ||
			    midi_pitch_class(debug.midi) != pitch_class)
				continue;
			if (!full_mix_debug_guitar_note_supported(ownership, debug.midi))
				continue;
			if (!lower || debug.midi < lower->midi)
				lower = &debug;
		}
		if (!lower)
			continue;

		const float level = std::max(primary.level, ownership_global_note_level(ownership, lower->midi));
		changed = promote_note_grid_primary_midi(grid, lower->midi, level) || changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

void promote_raw_supported_high_guitar_lower_octave_primary(
	NoteGrid &grid, InstrumentState &state, const FullMixOwnership &ownership,
	const std::array<float, kNoteProbeCount> &powers, int preferred_root)
{
	bool changed = false;
	const std::size_t debug_count =
		std::min<std::size_t>(ownership.debug_candidate_count, ownership.debug_candidates.size());

	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		NoteCell primary = {};
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active) {
				primary = row[pitch_class];
				break;
			}
		}
		if (!primary.active || primary.midi < 79)
			continue;

		const int lower_midi = primary.midi - 12;
		if (lower_midi < kGuitarMinMidi || lower_midi > kGuitarMaxMidi)
			continue;

		const FullMixDebugCandidate *primary_debug = nullptr;
		for (std::size_t i = 0; i < debug_count; ++i) {
			const FullMixDebugCandidate &debug = ownership.debug_candidates[i];
			if (debug.midi == primary.midi && debug.owner == InstrumentKind::Guitar) {
				primary_debug = &debug;
				break;
			}
		}
		if (!primary_debug)
			continue;

		const bool high_distorted_octave_body =
			primary_debug->guitar_score >= 0.70f &&
			primary_debug->spectral_level >= 0.30f &&
			primary_debug->spectral_level <= 0.70f &&
			primary_debug->pitch_confidence <= 0.45f &&
			primary_debug->periodicity >= 0.50f &&
			primary_debug->harmonic_fit_error >= 0.45f;
		if (!high_distorted_octave_body)
			continue;

		const float primary_raw = probe_level(powers, primary.midi);
		const float lower_raw = probe_level(powers, lower_midi);
		if (primary_raw <= 1.0e-6f || lower_raw < primary_raw * 0.12f)
			continue;

		changed = promote_note_grid_primary_midi(grid, lower_midi, primary.level) || changed;
	}

	if (changed)
		write_note_grid_label(state, grid, preferred_root);
}

bool note_grid_pitch_active(const NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	if (grid.cells[pitch_class].active)
		return true;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return true;
	}
	return false;
}

int note_grid_chord_tone_count(const NoteGrid &grid, const ChordResult &chord)
{
	int count = 0;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (chord.tones[pitch_class] && note_grid_pitch_active(grid, pitch_class))
			++count;
	}
	return count;
}

float note_grid_pitch_supported_level(const NoteGrid &grid, int pitch_class, float active_floor)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	float level = 0.0f;
	if (grid.cells[pitch_class].active)
		level = std::max({level, grid.cells[pitch_class].level, active_floor});
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max({level, row[pitch_class].level, active_floor});
	}
	return level;
}

bool note_grid_pitch_midi_range(const NoteGrid &grid, int pitch_class, int &min_midi, int &max_midi)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	bool found = false;
	auto consider = [&](const NoteCell &cell) {
		if (!cell.active || cell.midi < 0 || midi_pitch_class(cell.midi) != pitch_class)
			return;
		if (!found) {
			min_midi = cell.midi;
			max_midi = cell.midi;
			found = true;
		} else {
			min_midi = std::min(min_midi, cell.midi);
			max_midi = std::max(max_midi, cell.midi);
		}
	};

	consider(grid.cells[pitch_class]);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row)
			consider(cell);
	}
	return found;
}

bool note_grid_pitch_in_midi_window(const NoteGrid &grid, int pitch_class, int min_midi, int max_midi)
{
	int pitch_min = 0;
	int pitch_max = 0;
	if (!note_grid_pitch_midi_range(grid, pitch_class, pitch_min, pitch_max))
		return false;
	return pitch_max >= min_midi && pitch_min <= max_midi;
}

ChordResult make_guitar_plain_triad(int root, bool minor, float confidence)
{
	ChordResult chord;
	chord.root = ((root % 12) + 12) % 12;
	chord.confidence = confidence;
	chord.margin = confidence * 0.72f;
	chord.uncertain = false;
	chord.tones[chord.root] = true;
	chord.tones[(chord.root + (minor ? 3 : 4)) % 12] = true;
	chord.tones[(chord.root + 7) % 12] = true;
	std::snprintf(chord.label, sizeof(chord.label), "%s%s", note_name(chord.root), minor ? "m" : "");
	return chord;
}

ChordResult detect_display_supported_guitar_analysis_triad(const NoteGrid &display_grid,
							   const NoteGrid &analysis_grid,
							   int preferred_root)
{
	ChordResult best;
	copy_text(best.label, sizeof(best.label), "--");

	const int active_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (active_pitch_classes < 3 || active_pitch_classes > 10)
		return best;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	if (display_pitch_classes > 7)
		return best;

	const bool noisy_analysis_grid = active_pitch_classes > 8;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(analysis_grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return best;

	float best_score = 0.0f;
	auto consider = [&](int root, bool minor) {
		root = ((root % 12) + 12) % 12;
		const int third_pitch_class = (root + (minor ? 3 : 4)) % 12;
		const int fifth_pitch_class = (root + 7) % 12;
		const float root_level = note_grid_pitch_level(analysis_grid, root);
		const float third_level = note_grid_pitch_level(analysis_grid, third_pitch_class);
		const float fifth_level = note_grid_pitch_level(analysis_grid, fifth_pitch_class);
		const bool display_root = note_grid_pitch_active(display_grid, root);
		const bool display_third = note_grid_pitch_active(display_grid, third_pitch_class);
		const bool display_fifth = note_grid_pitch_active(display_grid, fifth_pitch_class);
		const int display_tones =
			(display_root ? 1 : 0) + (display_third ? 1 : 0) + (display_fifth ? 1 : 0);
		const bool compact_analysis_with_displayed_fifth =
			display_tones == 1 && display_fifth && active_pitch_classes <= 4 &&
			display_pitch_classes <= 2;
		if (display_tones < 2 && !compact_analysis_with_displayed_fifth)
			return;

		const float anchor = std::min(root_level, fifth_level);
		const float other_third = note_grid_pitch_level(analysis_grid, root + (minor ? 4 : 3));
		if (noisy_analysis_grid) {
			if (!display_root)
				return;
			const float core_floor = std::max(0.12f, strongest * 0.10f);
			if (root_level < core_floor || fifth_level < core_floor)
				return;
			const float third_floor = std::max({0.16f, anchor * 0.30f, strongest * 0.10f});
			if (third_level < third_floor)
				return;
			if (other_third >= std::max(0.10f, third_level * 0.80f))
				return;
		} else {
			const float root_floor = std::max(0.060f, strongest * 0.055f);
			const float fifth_floor = std::max(0.055f, strongest * 0.050f);
			if (root_level < root_floor || fifth_level < fifth_floor)
				return;
			const float third_floor = std::max(0.024f, anchor * 0.045f);
			if (third_level < third_floor)
				return;
			if (other_third >= std::max(0.12f, anchor * 0.22f) &&
			    other_third >= third_level * 1.30f)
				return;
		}
		if (compact_analysis_with_displayed_fifth &&
		    (root_level < 0.060f || third_level < std::max(0.024f, anchor * 0.045f) ||
		     fifth_level < std::max(0.40f, strongest * 0.40f)))
			return;

		if (note_grid_pitch_active(display_grid, root - 1) && note_grid_pitch_active(display_grid, root + 1) &&
		    third_level < anchor * 0.12f)
			return;

		float score = 0.40f + std::min({root_level, third_level, fifth_level}) * 0.72f +
			      anchor * 0.16f + static_cast<float>(display_tones) * 0.12f;
		if (preferred_root >= 0 && root == ((preferred_root % 12) + 12) % 12)
			score += noisy_analysis_grid ? 0.46f : 0.22f;
		if (score <= best_score)
			return;

		best_score = score;
		best = make_guitar_plain_triad(root, minor, std::clamp(score, 0.42f, 0.68f));
	};

	for (int root = 0; root < 12; ++root) {
		consider(root, false);
		consider(root, true);
	}
	return best;
}

ChordResult detect_visible_supported_guitar_plain_triad(const NoteGrid &grid, int preferred_root)
{
	ChordResult best;
	copy_text(best.label, sizeof(best.label), "--");

	const int active_pitch_classes = note_grid_active_pitch_class_count(grid);
	if (active_pitch_classes < 3 || active_pitch_classes > 6)
		return best;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return best;

	float best_score = 0.0f;
	auto consider = [&](int root, bool minor) {
		root = ((root % 12) + 12) % 12;
		const int third_pitch_class = (root + (minor ? 3 : 4)) % 12;
		const int fifth_pitch_class = (root + 7) % 12;
		const float root_level = note_grid_pitch_level(grid, root);
		const float third_level = note_grid_pitch_level(grid, third_pitch_class);
		const float fifth_level = note_grid_pitch_level(grid, fifth_pitch_class);
		const float anchor = std::min(root_level, fifth_level);
		if (root_level < std::max(0.10f, strongest * 0.14f) ||
		    fifth_level < std::max(0.08f, strongest * 0.08f) ||
		    third_level < std::max(0.08f, anchor * 0.10f))
			return;

		const float other_third = note_grid_pitch_level(grid, root + (minor ? 4 : 3));
		if (other_third >= std::max(0.10f, third_level * 0.72f))
			return;

		int extra_pitch_classes = 0;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			if (pitch_class == root || pitch_class == third_pitch_class || pitch_class == fifth_pitch_class)
				continue;
			if (note_grid_pitch_active(grid, pitch_class))
				++extra_pitch_classes;
		}
		if (extra_pitch_classes > 3)
			return;

		float score = 0.42f + std::min({root_level, third_level, fifth_level}) * 0.65f +
			      anchor * 0.12f - static_cast<float>(extra_pitch_classes) * 0.035f;
		if (preferred_root >= 0 && root == ((preferred_root % 12) + 12) % 12)
			score += 0.16f;
		if (score <= best_score)
			return;

		best_score = score;
		best = make_guitar_plain_triad(root, minor, std::clamp(score, 0.42f, 0.68f));
	};

	for (int root = 0; root < 12; ++root) {
		consider(root, false);
		consider(root, true);
	}
	return best;
}

void append_chord_alias(ChordResult &chord, int root, const char *suffix)
{
	if (root < 0 || !suffix)
		return;
	char alias[16] = {};
	std::snprintf(alias, sizeof(alias), "%s%s", note_name(root), suffix);
	if (chord_label_has_exact_component(chord.label, alias))
		return;
	if (chord.label[0])
		append_text(chord.label, sizeof(chord.label), "=");
	append_text(chord.label, sizeof(chord.label), alias);
}

void prepend_chord_alias(ChordResult &chord, int root, const char *suffix)
{
	if (root < 0 || !suffix)
		return;
	char alias[16] = {};
	std::snprintf(alias, sizeof(alias), "%s%s", note_name(root), suffix);
	if (chord_label_has_exact_component(chord.label, alias))
		return;

	char promoted[sizeof(chord.label)] = {};
	copy_text(promoted, sizeof(promoted), alias);
	if (chord.label[0]) {
		append_text(promoted, sizeof(promoted), "=");
		append_text(promoted, sizeof(promoted), chord.label);
	}
	copy_text(chord.label, sizeof(chord.label), promoted);
}

void append_equivalent_sixth_seventh_aliases(ChordResult &chord)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	struct AliasToAdd {
		int root = -1;
		char suffix[8] = {};
	};
	FixedList<AliasToAdd, 16> aliases;

	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed)) {
			std::size_t root_len = 1;
			if (len > 1 && cursor[1] == '#')
				root_len = 2;
			const char *suffix = cursor + root_len;
			const std::size_t suffix_len = len - root_len;
			AliasToAdd alias;
			if (suffix_is(suffix, suffix_len, "6")) {
				alias.root = (parsed.root + 9) % 12;
				copy_text(alias.suffix, sizeof(alias.suffix), "m7");
			} else if (suffix_is(suffix, suffix_len, "m7")) {
				alias.root = (parsed.root + 3) % 12;
				copy_text(alias.suffix, sizeof(alias.suffix), "6");
			} else if (suffix_is(suffix, suffix_len, "m6")) {
				alias.root = (parsed.root + 9) % 12;
				copy_text(alias.suffix, sizeof(alias.suffix), "m7b5");
			} else if (suffix_is(suffix, suffix_len, "m7b5")) {
				alias.root = (parsed.root + 3) % 12;
				copy_text(alias.suffix, sizeof(alias.suffix), "m6");
			}
			if (alias.root >= 0)
				aliases.push_back(alias);
		}

		if (!end)
			break;
		cursor = end + 1;
	}

	for (const AliasToAdd &alias : aliases)
		append_chord_alias(chord, alias.root, alias.suffix);
}

void append_same_root_chord_aliases(ChordResult &target, const ChordResult &source)
{
	if (target.root < 0 || !target.label[0] || target.label[0] == '-' ||
	    source.root < 0 || !source.label[0] || source.label[0] == '-')
		return;

	bool shared_root = false;
	const char *cursor = source.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) &&
		    chord_label_has_root_component(target.label, parsed.root)) {
			shared_root = true;
			break;
		}
		if (!end)
			break;
		cursor = end + 1;
	}
	if (!shared_root)
		return;

	cursor = source.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		if (len > 0 && len < 32) {
			char alias[32] = {};
			std::memcpy(alias, cursor, len);
			alias[len] = '\0';
			ParsedRootChord parsed;
			const bool extended_alias = chord_label_has_guitar_extension_or_alteration(alias);
			if (parse_root_chord_component(alias, len, parsed) &&
			    chord_label_has_root_component(target.label, parsed.root) &&
			    (!extended_alias || chord_label_has_guitar_extension_or_alteration(target.label)) &&
			    !chord_label_has_exact_component(target.label, alias)) {
				if (target.label[0])
					append_text(target.label, sizeof(target.label), "=");
				append_text(target.label, sizeof(target.label), alias);
				for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
					target.tones[pitch_class] = target.tones[pitch_class] || source.tones[pitch_class];
				target.confidence = std::max(target.confidence, source.confidence);
				target.margin = std::max(target.margin, source.margin);
				target.uncertain = target.uncertain && source.uncertain;
			}
		}
		if (!end)
			break;
		cursor = end + 1;
	}
}

void append_display_supported_guitar_analysis_triad_aliases(ChordResult &target,
							   const NoteGrid &display_grid,
							   const NoteGrid &analysis_grid)
{
	if (target.root < 0 || !target.label[0] || target.label[0] == '-')
		return;
	if (std::strstr(target.label, "pow"))
		return;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 3 || display_pitch_classes > 6 ||
	    analysis_pitch_classes < 3 || analysis_pitch_classes > 8)
		return;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 5 || longest_chromatic_run(analysis_chroma) >= 5)
		return;

	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	if (strongest_analysis <= 1.0e-6f)
		return;

	for (int root = 0; root < 12; ++root) {
		for (bool minor : {false, true}) {
			const int third = (root + (minor ? 3 : 4)) % 12;
			const int opposite_third = (root + (minor ? 4 : 3)) % 12;
			const int fifth = (root + 7) % 12;
			if (!note_grid_pitch_active(display_grid, root) ||
			    !note_grid_pitch_active(display_grid, third) ||
			    !note_grid_pitch_active(analysis_grid, root) ||
			    !note_grid_pitch_active(analysis_grid, third) ||
			    !note_grid_pitch_active(analysis_grid, fifth))
				continue;

			const float display_root = note_grid_pitch_level(display_grid, root);
			const float display_third = note_grid_pitch_level(display_grid, third);
			const float display_anchor = std::min(display_root, display_third);
			if (display_root < 0.12f || display_third < std::max(0.14f, display_anchor * 0.35f))
				continue;

			const float analysis_root = note_grid_pitch_level(analysis_grid, root);
			const float analysis_third = note_grid_pitch_level(analysis_grid, third);
			const float analysis_fifth = note_grid_pitch_level(analysis_grid, fifth);
			const float analysis_anchor = std::min(analysis_root, analysis_fifth);
			if (analysis_root < std::max(0.08f, strongest_analysis * 0.06f) ||
			    analysis_third < std::max(0.05f, analysis_anchor * 0.075f) ||
			    analysis_fifth < std::max(0.06f, strongest_analysis * 0.04f))
				continue;

			const float display_opposite = note_grid_pitch_level(display_grid, opposite_third);
			const float analysis_opposite = note_grid_pitch_level(analysis_grid, opposite_third);
			if (display_opposite >= std::max(0.12f, display_anchor * 0.68f) ||
			    analysis_opposite >= std::max(0.12f, analysis_anchor * 0.68f))
				continue;

			int display_extras = 0;
			for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
				if (pitch_class == root || pitch_class == third || pitch_class == fifth)
					continue;
				if (note_grid_pitch_active(display_grid, pitch_class))
					++display_extras;
			}
			if (display_extras > 3)
				continue;

			append_chord_alias(target, root, minor ? "m" : "");
		}
	}
}

void append_root_anchored_guitar_analysis_triad_aliases(ChordResult &target,
							const NoteGrid &display_grid,
							const NoteGrid &analysis_grid)
{
	if (target.root < 0 || !target.label[0] || target.label[0] == '-')
		return;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || display_pitch_classes > 7 ||
	    analysis_pitch_classes < 3 || analysis_pitch_classes > 10)
		return;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	const int display_chromatic_run = longest_chromatic_run(display_chroma);
	const int analysis_chromatic_run = longest_chromatic_run(analysis_chroma);

	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	if (strongest_analysis <= 1.0e-6f)
		return;

	for (int root = 0; root < 12; ++root) {
		for (bool minor : {false, true}) {
			const int third = (root + (minor ? 3 : 4)) % 12;
			const int opposite_third = (root + (minor ? 4 : 3)) % 12;
			const int fifth = (root + 7) % 12;
			const bool target_already_has_root = chord_label_has_root_component(target.label, root);
			const bool display_root = note_grid_pitch_active(display_grid, root);
			const bool display_third = note_grid_pitch_active(display_grid, third);
			const bool display_fifth = note_grid_pitch_active(display_grid, fifth);
			if (!display_root || (!display_third && !display_fifth))
				continue;
			if (display_chromatic_run >= 6 && !target_already_has_root)
				continue;
			if (analysis_chromatic_run >= 7 && !display_third && !target_already_has_root)
				continue;
			if (!note_grid_pitch_active(analysis_grid, root) ||
			    !note_grid_pitch_active(analysis_grid, third) ||
			    !note_grid_pitch_active(analysis_grid, fifth))
				continue;

			const float analysis_root = note_grid_pitch_level(analysis_grid, root);
			const float analysis_third = note_grid_pitch_level(analysis_grid, third);
			const float analysis_fifth = note_grid_pitch_level(analysis_grid, fifth);
			const float analysis_anchor = std::min(analysis_root, analysis_fifth);
			if (analysis_root < std::max(0.08f, strongest_analysis * 0.06f) ||
			    analysis_fifth < std::max(0.06f, strongest_analysis * 0.04f))
				continue;

			if (!display_fifth && display_third && !target_already_has_root &&
			    analysis_fifth < std::max({0.55f, analysis_root * 0.30f, strongest_analysis * 0.22f}))
				continue;
			if (analysis_chromatic_run >= 9 &&
			    (!target_already_has_root || !display_fifth ||
			     analysis_third < std::max({0.16f, analysis_anchor * 0.18f,
							strongest_analysis * 0.12f})))
				continue;
			float third_floor = display_third ?
						    std::max(0.035f, analysis_anchor * 0.055f) :
						    std::max(0.018f, analysis_anchor * 0.028f);
			if (!target_already_has_root && !display_third)
				third_floor = std::max(third_floor, analysis_anchor * 0.18f);
			if (analysis_pitch_classes > 8)
				third_floor = std::max(third_floor, analysis_anchor * 0.12f);
			if (analysis_third < third_floor)
				continue;

			const float display_anchor =
				std::min(note_grid_pitch_level(display_grid, root),
					 std::max(note_grid_pitch_level(display_grid, third),
						  note_grid_pitch_level(display_grid, fifth)));
			const float display_opposite = note_grid_pitch_level(display_grid, opposite_third);
			const float analysis_opposite = note_grid_pitch_level(analysis_grid, opposite_third);
			if (display_opposite >= std::max(0.12f, display_anchor * 0.68f) ||
			    analysis_opposite >= std::max(0.12f, analysis_anchor * 0.68f))
				continue;

			int display_extras = 0;
			for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
				if (pitch_class == root || pitch_class == third || pitch_class == fifth)
					continue;
				if (note_grid_pitch_active(display_grid, pitch_class))
					++display_extras;
			}
			if (display_extras > (target_already_has_root ? 4 : 3))
				continue;

			if (target_already_has_root && !chord_label_has_root_third_component(target.label, root))
				prepend_chord_alias(target, root, minor ? "m" : "");
			else
				append_chord_alias(target, root, minor ? "m" : "");
		}
	}
}

float strongest_probe_pitch_class_level(const std::array<float, kNoteProbeCount> &powers, int pitch_class,
					int min_midi, int max_midi);
float strongest_probe_level(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi);

void append_probe_supported_guitar_rootless_plain_triad_aliases(ChordResult &target,
							       const NoteGrid &display_grid,
							       const NoteGrid &analysis_grid,
							       const std::array<float, kNoteProbeCount> &powers,
							       int min_midi,
							       int max_midi)
{
	if (target.root < 0 || !target.label[0] || target.label[0] == '-')
		return;
	if (!chord_label_has_guitar_extension_or_alteration(target.label))
		return;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || display_pitch_classes > 5 ||
	    analysis_pitch_classes < 3 || analysis_pitch_classes > 6)
		return;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 4 || longest_chromatic_run(analysis_chroma) >= 5)
		return;

	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_probe <= 1.0e-6f)
		return;

	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	if (strongest_analysis <= 1.0e-6f)
		return;

	for (int root = 0; root < 12; ++root) {
		if (chord_label_has_root_component(target.label, root))
			continue;

		for (bool minor : {false, true}) {
			const int third = (root + (minor ? 3 : 4)) % 12;
			const int opposite_third = (root + (minor ? 4 : 3)) % 12;
			const int fifth = (root + 7) % 12;
			if (note_grid_pitch_active(display_grid, root) ||
			    !note_grid_pitch_active(display_grid, third) ||
			    !note_grid_pitch_active(display_grid, fifth))
				continue;
			if (!note_grid_pitch_active(analysis_grid, root) ||
			    !note_grid_pitch_active(analysis_grid, third) ||
			    !note_grid_pitch_active(analysis_grid, fifth))
				continue;

			const float display_third = note_grid_pitch_level(display_grid, third);
			const float display_fifth = note_grid_pitch_level(display_grid, fifth);
			const float display_anchor = std::min(display_third, display_fifth);
			if (display_anchor < 0.16f)
				continue;

			const float analysis_root = note_grid_pitch_level(analysis_grid, root);
			const float analysis_third = note_grid_pitch_level(analysis_grid, third);
			const float analysis_fifth = note_grid_pitch_level(analysis_grid, fifth);
			const float analysis_anchor = std::min(analysis_third, analysis_fifth);
			if (analysis_root < std::max(0.005f, strongest_analysis * 0.004f) ||
			    analysis_third < std::max(0.08f, strongest_analysis * 0.06f) ||
			    analysis_fifth < std::max(0.08f, strongest_analysis * 0.06f))
				continue;

			const float probe_root =
				strongest_probe_pitch_class_level(powers, root, min_midi, max_midi);
			const float probe_third =
				strongest_probe_pitch_class_level(powers, third, min_midi, max_midi);
			const float probe_fifth =
				strongest_probe_pitch_class_level(powers, fifth, min_midi, max_midi);
			const float probe_opposite =
				strongest_probe_pitch_class_level(powers, opposite_third, min_midi, max_midi);
			const float probe_anchor = std::min(probe_third, probe_fifth);
			if (probe_root < std::max({strongest_probe * 0.020f, probe_anchor * 0.24f, 0.020f}))
				continue;
			if (probe_opposite >= std::max(0.12f, probe_root * 0.58f))
				continue;

			const float analysis_opposite = note_grid_pitch_level(analysis_grid, opposite_third);
			if (analysis_opposite >= std::max(0.12f, analysis_anchor * 0.62f))
				continue;

			int display_extras = 0;
			for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
				if (pitch_class == third || pitch_class == fifth)
					continue;
				if (note_grid_pitch_active(display_grid, pitch_class))
					++display_extras;
			}
			if (display_extras > 2)
				continue;

			append_chord_alias(target, root, minor ? "m" : "");
		}
	}
}

void append_supported_guitar_plain_triad_aliases(ChordResult &chord, const NoteGrid &grid, int only_root = -1)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return;

	constexpr float kActiveAliasFloor = 0.12f;
	constexpr float kRootFloor = 0.10f;
	constexpr float kThirdFloor = 0.08f;
	constexpr float kFifthFloor = 0.08f;
	for (int root = 0; root < 12; ++root) {
		if (only_root >= 0 && root != ((only_root % 12) + 12) % 12)
			continue;
		const float root_level = note_grid_pitch_supported_level(grid, root, kActiveAliasFloor);
		const float major_third = note_grid_pitch_supported_level(grid, root + 4, kActiveAliasFloor);
		const float minor_third = note_grid_pitch_supported_level(grid, root + 3, kActiveAliasFloor);
		const float fifth = note_grid_pitch_supported_level(grid, root + 7, kActiveAliasFloor);
		if (root_level < std::max(kRootFloor, strongest * 0.14f) || fifth < kFifthFloor)
			continue;
		if (major_third >= kThirdFloor && major_third >= minor_third * 1.10f)
			append_chord_alias(chord, root, "");
		if (minor_third >= kThirdFloor && minor_third >= major_third * 1.10f)
			append_chord_alias(chord, root, "m");
	}
}

void append_supported_guitar_ambiguous_third_aliases(ChordResult &chord, const NoteGrid &grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return;

	for (int root = 0; root < 12; ++root) {
		if (!chord_label_has_root_component(chord.label, root))
			continue;

		const float root_level = note_grid_pitch_level(grid, root);
		const float fifth = note_grid_pitch_level(grid, root + 7);
		if (root_level < std::max(0.10f, strongest * 0.14f) ||
		    fifth < std::max(0.08f, strongest * 0.10f))
			continue;

		const float major_third = note_grid_pitch_level(grid, root + 4);
		const float minor_third = note_grid_pitch_level(grid, root + 3);
		const float third_floor = std::max(0.18f, std::min(root_level, fifth) * 0.42f);
		if (major_third < third_floor || minor_third < third_floor)
			continue;

		const float weaker_third = std::min(major_third, minor_third);
		const float stronger_third = std::max(major_third, minor_third);
		if (weaker_third < stronger_third * 0.72f)
			continue;

		append_chord_alias(chord, root, "");
		append_chord_alias(chord, root, "m");
	}
}

bool plain_chord_exactly_matches_display_grid(const ChordResult &chord, const NoteGrid &grid)
{
	ParsedRootChord parsed;
	if (!parse_root_chord_component(chord.label, std::strcspn(chord.label, "="), parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return false;
	std::array<bool, 12> primary_tones = {};
	primary_tones[parsed.root] = true;
	primary_tones[(parsed.root + (parsed.quality == RootChordQuality::Minor ? 3 : 4)) % 12] = true;
	primary_tones[(parsed.root + 7) % 12] = true;
	const std::array<float, 12> visible_chroma = note_grid_chroma(grid);
	int visible_pitch_classes = 0;
	for (float level : visible_chroma) {
		if (level > 0.0f)
			++visible_pitch_classes;
	}
	if (visible_pitch_classes != 3)
		return false;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (visible_chroma[pitch_class] > 0.0f && !primary_tones[pitch_class])
			return false;
	}
	return true;
}

bool parse_primary_major_minor_chord(const ChordResult &chord, ParsedRootChord &parsed)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return false;
	const std::size_t label_len = std::strcspn(chord.label, "=");
	if (!parse_root_chord_component(chord.label, label_len, parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return false;

	std::size_t root_len = 1;
	if (label_len > 1 && chord.label[1] == '#')
		root_len = 2;
	const char *suffix = chord.label + root_len;
	const std::size_t suffix_len = label_len - root_len;
	const bool plain_primary =
		parsed.quality == RootChordQuality::Minor ? suffix_is(suffix, suffix_len, "m") :
							    suffix_len == 0;
	return parsed.root == chord.root && plain_primary;
}

float primary_major_minor_min_tone_level(const NoteGrid &grid, const ParsedRootChord &parsed)
{
	const int third = parsed.root + (parsed.quality == RootChordQuality::Minor ? 3 : 4);
	return std::min({note_grid_pitch_level(grid, parsed.root), note_grid_pitch_level(grid, third),
			 note_grid_pitch_level(grid, parsed.root + 7)});
}

bool clean_primary_guitar_chord_display(const ChordResult &chord, const NoteGrid &display_grid,
					const NoteGrid &)
{
	ParsedRootChord parsed;
	if (!parse_primary_major_minor_chord(chord, parsed))
		return false;

	if (plain_chord_exactly_matches_display_grid(chord, display_grid) &&
	    primary_major_minor_min_tone_level(display_grid, parsed) >= 0.30f)
		return true;

	const int fifth = parsed.root + 7;
	if (note_grid_pitch_level(display_grid, parsed.root) < 0.30f ||
	    note_grid_pitch_level(display_grid, fifth) < 0.30f)
		return false;
	return true;
}

float strongest_grid_pitch_level(const NoteGrid &display_grid, const NoteGrid &analysis_grid, int pitch_class)
{
	return std::max(note_grid_pitch_level(display_grid, pitch_class),
			note_grid_pitch_level(analysis_grid, pitch_class));
}

bool same_root_alias_component_supported_by_clean_primary(const char *start, std::size_t len,
							  const ParsedRootChord &component,
							  const ParsedRootChord &primary,
							  const NoteGrid &display_grid,
							  const NoteGrid &analysis_grid)
{
	if (!start || component.root != primary.root)
		return false;

	const int primary_third = primary.root + (primary.quality == RootChordQuality::Minor ? 3 : 4);
	const float primary_root = strongest_grid_pitch_level(display_grid, analysis_grid, primary.root);
	const float primary_fifth = strongest_grid_pitch_level(display_grid, analysis_grid, primary.root + 7);
	const float primary_anchor = std::min(primary_root, primary_fifth);
	const float primary_third_level =
		strongest_grid_pitch_level(display_grid, analysis_grid, primary_third);
	const float primary_support = std::max(primary_anchor, primary_third_level);

	auto supported_alias_tone = [&](int pitch_class, float relative_floor, float third_relative_floor) {
		const float level = strongest_grid_pitch_level(display_grid, analysis_grid, pitch_class);
		return level >= std::max({0.12f, primary_support * relative_floor,
					  primary_third_level * third_relative_floor});
	};

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#')
		root_len = 2;
	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;
	const bool primary_plain =
		primary.quality == RootChordQuality::Minor ? suffix_is(suffix, suffix_len, "m") :
							    suffix_len == 0;
	if (primary_plain)
		return false;

	if (component.quality == RootChordQuality::Major || component.quality == RootChordQuality::Minor) {
		const bool minor = component.quality == RootChordQuality::Minor;
		const int alias_third = component.root + (minor ? 3 : 4);
		if (alias_third != primary_third && supported_alias_tone(alias_third, 0.34f, 0.72f))
			return true;
		if (suffix_is(suffix, suffix_len, "6") || suffix_is(suffix, suffix_len, "m6")) {
			if (supported_alias_tone(component.root + 9, 0.42f, 0.35f))
				return true;
		} else if (suffix_is(suffix, suffix_len, "7") || suffix_is(suffix, suffix_len, "m7")) {
			if (supported_alias_tone(component.root + 10, 0.42f, 0.35f))
				return true;
		} else if (suffix_is(suffix, suffix_len, "maj7")) {
			if (supported_alias_tone(component.root + 11, 0.42f, 0.35f))
				return true;
		} else if (suffix_is(suffix, suffix_len, "9") || suffix_is(suffix, suffix_len, "m9") ||
			   suffix_is(suffix, suffix_len, "maj9") ||
			   suffix_is(suffix, suffix_len, "add9")) {
			if (supported_alias_tone(component.root + 2, 0.42f, 0.35f))
				return true;
		}
	} else if (component.quality == RootChordQuality::NoThird) {
		if (suffix_is(suffix, suffix_len, "sus2") &&
		    supported_alias_tone(component.root + 2, 0.38f, 0.55f))
			return true;
		if (suffix_is(suffix, suffix_len, "sus4") &&
		    supported_alias_tone(component.root + 5, 0.38f, 0.55f))
			return true;
	} else if (component.quality == RootChordQuality::Diminished) {
		if (supported_alias_tone(component.root + 6, 0.38f, 0.55f))
			return true;
	}
	return false;
}

bool chord_label_has_major_and_minor_for_root(const char *label, int root)
{
	bool primary_major = false;
	bool primary_minor = false;
	const char *cursor = label;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord component;
		if (parse_root_chord_component(cursor, len, component) && component.root == root) {
			primary_major = primary_major || component.quality == RootChordQuality::Major;
			primary_minor = primary_minor || component.quality == RootChordQuality::Minor;
		}
		if (!end)
			break;
		cursor = end + 1;
	}
	return primary_major && primary_minor;
}

bool different_root_plain_alias_supported_by_clean_primary(const ParsedRootChord &component,
							   const ParsedRootChord &primary,
							   const NoteGrid &display_grid,
							   const NoteGrid &analysis_grid,
							   bool allow_different_root_plain,
							   bool exact_clean_primary,
							   bool same_root_alias_supported)
{
	if (component.root == primary.root ||
	    (component.quality != RootChordQuality::Major && component.quality != RootChordQuality::Minor))
		return false;

	ChordResult alias =
		make_guitar_plain_triad(component.root, component.quality == RootChordQuality::Minor, 0.58f);
	if (allow_different_root_plain && note_grid_chord_tone_count(display_grid, alias) >= 2 &&
	    note_grid_chord_tone_count(analysis_grid, alias) >= 3)
		return true;

	const bool relative_minor_alias = primary.quality == RootChordQuality::Major &&
					  component.quality == RootChordQuality::Minor &&
					  component.root == (primary.root + 4) % 12;
	const bool relative_major_alias = primary.quality == RootChordQuality::Minor &&
					  component.quality == RootChordQuality::Major &&
					  component.root == (primary.root + 8) % 12;
	if ((exact_clean_primary && !same_root_alias_supported) ||
	    (!relative_minor_alias && !relative_major_alias))
		return false;

	const float primary_root = strongest_grid_pitch_level(display_grid, analysis_grid, primary.root);
	const float primary_fifth = strongest_grid_pitch_level(display_grid, analysis_grid, primary.root + 7);
	const float alias_root = strongest_grid_pitch_level(display_grid, analysis_grid, component.root);
	const float root_floor = same_root_alias_supported ? 0.14f : 0.30f;
	const float root_ratio = same_root_alias_supported ? 0.40f : 0.72f;
	if (alias_root < std::max(root_floor, std::min(primary_root, primary_fifth) * root_ratio))
		return false;

	return note_grid_chord_tone_count(display_grid, alias) >= 2 &&
	       note_grid_chord_tone_count(analysis_grid, alias) >= 2;
}

bool label_has_supported_same_root_alias_for_primary(const ChordResult &chord,
						    const ParsedRootChord &primary,
						    const NoteGrid &display_grid,
						    const NoteGrid &analysis_grid)
{
	const char *cursor = chord.label;
	bool first_component = true;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord component;
		if (!first_component && parse_root_chord_component(cursor, len, component) &&
		    same_root_alias_component_supported_by_clean_primary(cursor, len, component, primary,
									display_grid, analysis_grid))
			return true;
		if (!end)
			break;
		cursor = end + 1;
		first_component = false;
	}
	return false;
}

bool equivalent_sixth_seventh_alias_supported_by_clean_primary(const char *start, std::size_t len,
							       const ParsedRootChord &component,
							       const ParsedRootChord &primary,
							       const NoteGrid &display_grid,
							       const NoteGrid &analysis_grid)
{
	if (!start || component.root == primary.root)
		return false;

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#')
		root_len = 2;
	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;

	const bool major_sixth_minor_seventh =
		primary.quality == RootChordQuality::Major &&
		component.quality == RootChordQuality::Minor &&
		component.root == (primary.root + 9) % 12 &&
		suffix_is(suffix, suffix_len, "m7");
	const bool minor_sixth_half_diminished =
		primary.quality == RootChordQuality::Minor &&
		component.quality == RootChordQuality::Diminished &&
		component.root == (primary.root + 9) % 12 &&
		suffix_is(suffix, suffix_len, "m7b5");
	if (!major_sixth_minor_seventh && !minor_sixth_half_diminished)
		return false;

	ChordResult alias = {};
	alias.root = component.root;
	alias.confidence = 0.58f;
	alias.uncertain = false;
	std::memcpy(alias.label, start, std::min(len, sizeof(alias.label) - 1));
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		alias.tones[pitch_class] = false;
	alias.tones[component.root] = true;
	alias.tones[(component.root + 3) % 12] = true;
	alias.tones[(component.root + 6) % 12] = minor_sixth_half_diminished;
	alias.tones[(component.root + 7) % 12] = major_sixth_minor_seventh;
	alias.tones[(component.root + 10) % 12] = true;
	return note_grid_chord_tone_count(display_grid, alias) >= 2 &&
	       note_grid_chord_tone_count(analysis_grid, alias) >= 3;
}

void append_chord_label_component(char *dst, std::size_t dst_size, const char *start, std::size_t len)
{
	if (!dst || dst_size == 0 || !start || len == 0)
		return;
	if (dst[0])
		append_text(dst, dst_size, "=");
	const std::size_t used = std::strlen(dst);
	if (used + 1 >= dst_size)
		return;
	const std::size_t copy_len = std::min(len, dst_size - used - 1);
	std::memcpy(dst + used, start, copy_len);
	dst[used + copy_len] = '\0';
}

bool parse_plain_major_minor_component(const char *start, std::size_t len, ParsedRootChord &parsed)
{
	if (!parse_root_chord_component(start, len, parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return false;

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#')
		root_len = 2;
	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;
	return parsed.quality == RootChordQuality::Minor ? suffix_is(suffix, suffix_len, "m") :
							    suffix_len == 0;
}

float plain_guitar_component_primary_score(const ParsedRootChord &component,
					   const NoteGrid &display_grid,
					   const NoteGrid &analysis_grid)
{
	const ChordResult plain =
		make_guitar_plain_triad(component.root, component.quality == RootChordQuality::Minor, 0.58f);
	const int display_tones = note_grid_chord_tone_count(display_grid, plain);
	const int analysis_tones = note_grid_chord_tone_count(analysis_grid, plain);
	if (display_tones < 2 || analysis_tones < 2)
		return -1.0f;

	const int third = component.root + (component.quality == RootChordQuality::Minor ? 3 : 4);
	const float root_level = strongest_grid_pitch_level(display_grid, analysis_grid, component.root);
	const float third_level = strongest_grid_pitch_level(display_grid, analysis_grid, third);
	const float fifth_level = strongest_grid_pitch_level(display_grid, analysis_grid, component.root + 7);
	const float anchor = std::min(root_level, fifth_level);
	const float opposite_third =
		strongest_grid_pitch_level(display_grid, analysis_grid,
					   component.root + (component.quality == RootChordQuality::Minor ? 4 : 3));
	if (anchor < 0.08f)
		return -1.0f;
	if (third_level < std::max(0.012f, anchor * 0.018f) && display_tones + analysis_tones < 5)
		return -1.0f;
	if (opposite_third >= std::max(0.18f, anchor * 0.55f) && opposite_third > third_level * 1.35f)
		return -1.0f;

	return static_cast<float>(display_tones) * 1.15f +
	       static_cast<float>(analysis_tones) * 0.85f +
	       anchor * 0.55f + third_level * 0.35f;
}

bool label_has_same_root_power_component(const char *label, int root)
{
	if (!label || root < 0)
		return false;

	const char *cursor = label;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord component;
		if (parse_root_chord_component(cursor, len, component) &&
		    component.root == root && component.quality == RootChordQuality::NoThird) {
			std::size_t root_len = 1;
			if (len > 1 && cursor[1] == '#')
				root_len = 2;
			if (suffix_is(cursor + root_len, len - root_len, "pow"))
				return true;
		}
		if (!end)
			break;
		cursor = end + 1;
	}
	return false;
}

void promote_supported_plain_guitar_primary(ChordResult &chord, const NoteGrid &display_grid,
					    const NoteGrid &analysis_grid)
{
	if (chord.root < 0 || chord.confidence < kChordConfidenceFloor || chord.uncertain ||
	    !chord.label[0] || chord.label[0] == '-' || chord_label_component_count(chord.label) < 2)
		return;

	ParsedRootChord current_primary;
	const std::size_t current_len = std::strcspn(chord.label, "=");
	const bool current_plain =
		parse_plain_major_minor_component(chord.label, current_len, current_primary);
	const float current_score = current_plain ?
					    plain_guitar_component_primary_score(current_primary, display_grid,
										 analysis_grid) :
					    -1.0f;

	const char *best_start = nullptr;
	std::size_t best_len = 0;
	ParsedRootChord best_component;
	float best_score = -1.0f;
	bool best_has_power = false;
	const char *cursor = chord.label;
	bool first_component = true;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord component;
		if (!first_component && parse_plain_major_minor_component(cursor, len, component)) {
			float score = plain_guitar_component_primary_score(component, display_grid, analysis_grid);
			const bool has_power = label_has_same_root_power_component(chord.label, component.root);
			if (has_power)
				score += 0.72f;
			const bool different_root = !current_plain || current_primary.root != component.root;
			const float required_margin =
				!current_plain ? 0.20f : has_power && different_root ? 0.18f : 0.48f;
			if (score > best_score && score >= current_score + required_margin) {
				best_score = score;
				best_start = cursor;
				best_len = len;
				best_component = component;
				best_has_power = has_power;
			}
		}
		if (!end)
			break;
		cursor = end + 1;
		first_component = false;
	}

	if (!best_start || best_len == 0)
		return;
	if (current_plain && current_primary.root == best_component.root && !best_has_power)
		return;

	char promoted[sizeof(chord.label)] = {};
	append_chord_label_component(promoted, sizeof(promoted), best_start, best_len);
	cursor = chord.label;
	bool skipped_promoted = false;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		const bool same_component =
			!skipped_promoted && len == best_len && std::strncmp(cursor, best_start, len) == 0;
		if (same_component) {
			skipped_promoted = true;
		} else {
			append_chord_label_component(promoted, sizeof(promoted), cursor, len);
		}
		if (!end)
			break;
		cursor = end + 1;
	}
	copy_text(chord.label, sizeof(chord.label), promoted);
}

void prune_clean_primary_guitar_aliases(ChordResult &chord, const NoteGrid &display_grid,
					const NoteGrid &analysis_grid)
{
	ParsedRootChord primary;
	if (!parse_primary_major_minor_chord(chord, primary))
		return;
	if (!clean_primary_guitar_chord_display(chord, display_grid, analysis_grid))
		return;

	const bool allow_different_root_plain =
		chord_label_has_major_and_minor_for_root(chord.label, primary.root);
	const bool exact_clean_primary = plain_chord_exactly_matches_display_grid(chord, display_grid) &&
					 primary_major_minor_min_tone_level(display_grid, primary) >= 0.30f;
	const bool same_root_alias_supported =
		label_has_supported_same_root_alias_for_primary(chord, primary, display_grid, analysis_grid);
	char filtered[sizeof(chord.label)] = {};
	const char *cursor = chord.label;
	bool first_component = true;
	while (cursor && *cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len =
			end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		bool keep = first_component;
		ParsedRootChord component;
		if (!keep && parse_root_chord_component(cursor, len, component)) {
			keep = same_root_alias_component_supported_by_clean_primary(
				       cursor, len, component, primary, display_grid, analysis_grid) ||
			       different_root_plain_alias_supported_by_clean_primary(
				       component, primary, display_grid, analysis_grid,
				       allow_different_root_plain, exact_clean_primary,
				       same_root_alias_supported) ||
			       equivalent_sixth_seventh_alias_supported_by_clean_primary(
				       cursor, len, component, primary, display_grid, analysis_grid);
		}
		if (keep)
			append_chord_label_component(filtered, sizeof(filtered), cursor, len);

		if (!end)
			break;
		cursor = end + 1;
		first_component = false;
	}

	if (filtered[0])
		copy_text(chord.label, sizeof(chord.label), filtered);
}

void prune_promoted_plain_guitar_primary_aliases(ChordResult &chord, const NoteGrid &display_grid,
						 const NoteGrid &analysis_grid,
						 const char *label_before_promotion)
{
	if (!label_before_promotion || !*label_before_promotion)
		return;

	ParsedRootChord original_primary;
	if (!parse_plain_major_minor_component(label_before_promotion,
					       std::strcspn(label_before_promotion, "="),
					       original_primary))
		return;

	ParsedRootChord displayed_primary;
	if (!parse_plain_major_minor_component(chord.label, std::strcspn(chord.label, "="),
					       displayed_primary))
		return;
	if (original_primary.root != displayed_primary.root ||
	    original_primary.quality != displayed_primary.quality)
		return;

	ChordResult display_rooted = chord;
	display_rooted.root = displayed_primary.root;
	if (!plain_chord_exactly_matches_display_grid(display_rooted, display_grid) ||
	    primary_major_minor_min_tone_level(display_grid, displayed_primary) < 0.30f)
		return;
	prune_clean_primary_guitar_aliases(display_rooted, display_grid, analysis_grid);
	copy_text(chord.label, sizeof(chord.label), display_rooted.label);
}

void append_supported_guitar_power_aliases(ChordResult &chord, const NoteGrid &grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return;

	constexpr float kActiveAliasFloor = 0.12f;
	std::array<float, 12> scores = {};
	float best_score = 0.0f;
	for (int root = 0; root < 12; ++root) {
		const bool grid_minor_active = note_grid_pitch_active(grid, root + 3);
		const bool grid_major_active = note_grid_pitch_active(grid, root + 4);
		if (chord_label_has_root_third_component(chord.label, root) &&
		    (grid_minor_active || grid_major_active))
			continue;

		const float root_level = note_grid_pitch_supported_level(grid, root, kActiveAliasFloor);
		const float fifth = note_grid_pitch_supported_level(grid, root + 7, kActiveAliasFloor);
		if (root_level < std::max(0.10f, strongest * 0.18f) ||
		    fifth < std::max(0.08f, strongest * 0.10f))
			continue;

		const float major_third = note_grid_pitch_supported_level(grid, root + 4, kActiveAliasFloor);
		const float minor_third = note_grid_pitch_supported_level(grid, root + 3, kActiveAliasFloor);
		const float third_floor = std::max(0.10f, std::min(root_level, fifth) * 0.45f);
		if (major_third >= third_floor || minor_third >= third_floor)
			continue;

		const float score = std::min(root_level, fifth) * 0.80f + std::max(root_level, fifth) * 0.20f;
		scores[root] = score;
		best_score = std::max(best_score, score);
	}

	if (best_score < 0.24f)
		return;
	for (int root = 0; root < 12; ++root) {
		if (scores[root] >= best_score * 0.80f)
			append_chord_alias(chord, root, "pow");
	}
}

bool supported_guitar_root_fifth_dyad(const NoteGrid &display_grid, const NoteGrid &analysis_grid,
				      int root, float *score_out = nullptr)
{
	root = ((root % 12) + 12) % 12;
	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || analysis_pitch_classes < 2 ||
	    display_pitch_classes > 6 || analysis_pitch_classes > 8)
		return false;

	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(analysis_chroma) >= 5)
		return false;

	float strongest_display = 0.0f;
	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		strongest_display = std::max(strongest_display, note_grid_pitch_level(display_grid, pitch_class));
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	}
	if (strongest_display <= 1.0e-6f || strongest_analysis <= 1.0e-6f)
		return false;

	constexpr float kActiveAliasFloor = 0.12f;
	const float display_root = note_grid_pitch_supported_level(display_grid, root, kActiveAliasFloor);
	const float display_fifth = note_grid_pitch_supported_level(display_grid, root + 7, kActiveAliasFloor);
	const float analysis_root = note_grid_pitch_supported_level(analysis_grid, root, kActiveAliasFloor);
	const float analysis_fifth = note_grid_pitch_supported_level(analysis_grid, root + 7, kActiveAliasFloor);
	if (display_root < std::max(0.10f, strongest_display * 0.14f) ||
	    display_fifth < std::max(0.08f, strongest_display * 0.10f) ||
	    analysis_root < std::max(0.08f, strongest_analysis * 0.08f) ||
	    analysis_fifth < std::max(0.06f, strongest_analysis * 0.06f))
		return false;

	const float display_anchor = std::min(display_root, display_fifth);
	const float analysis_anchor = std::min(analysis_root, analysis_fifth);
	const float display_third_floor = std::max(0.10f, display_anchor * 0.45f);
	const float analysis_third_floor = std::max(0.08f, analysis_anchor * 0.34f);
	const float display_major = note_grid_pitch_supported_level(display_grid, root + 4, kActiveAliasFloor);
	const float display_minor = note_grid_pitch_supported_level(display_grid, root + 3, kActiveAliasFloor);
	const float analysis_major = note_grid_pitch_supported_level(analysis_grid, root + 4, kActiveAliasFloor);
	const float analysis_minor = note_grid_pitch_supported_level(analysis_grid, root + 3, kActiveAliasFloor);
	if (display_major >= display_third_floor || display_minor >= display_third_floor ||
	    analysis_major >= analysis_third_floor || analysis_minor >= analysis_third_floor)
		return false;

	if (score_out)
		*score_out = display_anchor * 0.65f + analysis_anchor * 0.35f;
	return true;
}

bool display_supported_guitar_root_fifth_dyad(const NoteGrid &display_grid,
					     const NoteGrid &analysis_grid,
					     int root,
					     float *score_out = nullptr)
{
	root = ((root % 12) + 12) % 12;
	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || analysis_pitch_classes < 2 ||
	    display_pitch_classes > 6 || analysis_pitch_classes > 8)
		return false;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 5 || longest_chromatic_run(analysis_chroma) >= 5)
		return false;

	float strongest_display = 0.0f;
	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		strongest_display = std::max(strongest_display, note_grid_pitch_level(display_grid, pitch_class));
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	}
	if (strongest_display <= 1.0e-6f || strongest_analysis <= 1.0e-6f)
		return false;

	constexpr float kActiveAliasFloor = 0.12f;
	const float display_root = note_grid_pitch_supported_level(display_grid, root, kActiveAliasFloor);
	const float display_fifth = note_grid_pitch_supported_level(display_grid, root + 7, kActiveAliasFloor);
	const float analysis_root = note_grid_pitch_supported_level(analysis_grid, root, kActiveAliasFloor);
	const float analysis_fifth = note_grid_pitch_supported_level(analysis_grid, root + 7, kActiveAliasFloor);
	if (display_root < std::max(0.10f, strongest_display * 0.14f) ||
	    display_fifth < std::max(0.08f, strongest_display * 0.10f) ||
	    analysis_root < std::max(0.08f, strongest_analysis * 0.08f) ||
	    analysis_fifth < std::max(0.06f, strongest_analysis * 0.06f))
		return false;

	const float display_anchor = std::min(display_root, display_fifth);
	const float display_third_floor = std::max(0.10f, display_anchor * 0.45f);
	const float display_major = note_grid_pitch_supported_level(display_grid, root + 4, kActiveAliasFloor);
	const float display_minor = note_grid_pitch_supported_level(display_grid, root + 3, kActiveAliasFloor);
	if (display_major >= display_third_floor || display_minor >= display_third_floor)
		return false;

	if (score_out) {
		const float analysis_anchor = std::min(analysis_root, analysis_fifth);
		*score_out = display_anchor * 0.70f + analysis_anchor * 0.30f;
	}
	return true;
}

ChordResult detect_supported_guitar_power_dyad(const NoteGrid &display_grid,
					       const NoteGrid &analysis_grid,
					       int preferred_root)
{
	ChordResult best;
	float best_score = 0.0f;
	for (int root = 0; root < 12; ++root) {
		float score = 0.0f;
		if (!supported_guitar_root_fifth_dyad(display_grid, analysis_grid, root, &score) &&
		    !display_supported_guitar_root_fifth_dyad(display_grid, analysis_grid, root, &score))
			continue;
		if (preferred_root >= 0 && root == ((preferred_root % 12) + 12) % 12)
			score += 0.06f;
		if (score <= best_score)
			continue;

		best_score = score;
		best = ChordResult{};
		best.root = root;
		best.confidence = std::clamp(0.42f + score * 0.12f, kChordConfidenceFloor, 0.58f);
		best.margin = best.confidence * 0.60f;
		best.uncertain = false;
		best.tones[root] = true;
		best.tones[(root + 7) % 12] = true;
		std::snprintf(best.label, sizeof(best.label), "%spow", note_name(root));
	}
	return best;
}

ChordResult detect_preferred_guitar_root_third_dyad(const NoteGrid &grid, int preferred_root)
{
	ChordResult dyad;
	if (preferred_root < 0 || note_grid_active_pitch_class_count(grid) > 5)
		return dyad;

	const std::array<float, 12> chroma = note_grid_chroma(grid);
	if (longest_chromatic_run(chroma) >= 4)
		return dyad;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return dyad;

	const float root_floor = std::max(0.14f, strongest * 0.20f);
	const float third_floor = std::max(0.12f, strongest * 0.18f);
	float best_score = 0.0f;
	auto consider_root = [&](int root_pitch_class) {
		root_pitch_class = ((root_pitch_class % 12) + 12) % 12;
		const float root = note_grid_pitch_level(grid, root_pitch_class);
		const float major_third = note_grid_pitch_level(grid, root_pitch_class + 4);
		const float minor_third = note_grid_pitch_level(grid, root_pitch_class + 3);
		if (root < root_floor)
			return;

		const bool choose_minor = minor_third >= third_floor && minor_third >= major_third * 1.10f;
		const bool choose_major = major_third >= third_floor && major_third >= minor_third * 1.10f;
		if (choose_minor == choose_major)
			return;

		const float third = choose_minor ? minor_third : major_third;
		float score = std::min(root, third) + std::max(root, third) * 0.10f;
		if (preferred_root >= 0 && root_pitch_class == ((preferred_root % 12) + 12) % 12)
			score += 0.12f;
		if (score <= best_score)
			return;

		best_score = score;
		dyad = ChordResult{};
		dyad.root = root_pitch_class;
		dyad.confidence = std::clamp(0.36f + std::min(root, third) * 0.20f,
					     kChordConfidenceFloor, 0.56f);
		dyad.margin = dyad.confidence * 0.65f;
		dyad.uncertain = false;
		dyad.tones[root_pitch_class] = true;
		dyad.tones[(root_pitch_class + (choose_minor ? 3 : 4)) % 12] = true;
		std::snprintf(dyad.label, sizeof(dyad.label), "%s%s", note_name(root_pitch_class),
			      choose_minor ? "m" : "");
	};

	if (preferred_root >= 0)
		consider_root(preferred_root);
	for (int root = 0; root < 12; ++root)
		consider_root(root);
	return dyad;
}

int note_grid_lowest_active_midi(const NoteGrid &grid)
{
	int lowest = 128;
	auto visit = [&](const NoteCell &cell) {
		if (cell.active && cell.midi >= 0)
			lowest = std::min(lowest, cell.midi);
	};
	for (const NoteCell &cell : grid.cells)
		visit(cell);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row)
			visit(cell);
	}
	return lowest == 128 ? -1 : lowest;
}

int note_grid_lowest_active_midi_for_pitch_class(const NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	int lowest = 128;
	auto visit = [&](const NoteCell &cell) {
		if (cell.active && cell.midi >= 0 && midi_pitch_class(cell.midi) == pitch_class)
			lowest = std::min(lowest, cell.midi);
	};
	for (const NoteCell &cell : grid.cells)
		visit(cell);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row)
			visit(cell);
	}
	return lowest == 128 ? -1 : lowest;
}

bool note_grid_has_guitar_root_third_voicing(const NoteGrid &grid, int root_pitch_class, int third_pitch_class)
{
	root_pitch_class = ((root_pitch_class % 12) + 12) % 12;
	third_pitch_class = ((third_pitch_class % 12) + 12) % 12;

	const int root_midi = note_grid_lowest_active_midi_for_pitch_class(grid, root_pitch_class);
	if (root_midi < 0)
		return false;
	const int lowest_midi = note_grid_lowest_active_midi(grid);
	if (lowest_midi >= 0 && root_midi > lowest_midi + 2)
		return note_grid_pitch_in_midi_window(grid, third_pitch_class, root_midi - 12, root_midi - 3);

	bool found = false;
	auto visit = [&](const NoteCell &cell) {
		if (found || !cell.active || cell.midi < 0 || midi_pitch_class(cell.midi) != third_pitch_class)
			return;
		const int interval = cell.midi - root_midi;
		if (interval >= 3 && interval <= 16)
			found = true;
	};
	for (const NoteCell &cell : grid.cells)
		visit(cell);
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row)
			visit(cell);
	}
	return found;
}

ChordResult detect_supported_guitar_root_third_dyad(const NoteGrid &display_grid,
						    const NoteGrid &analysis_grid,
						    int preferred_root)
{
	ChordResult dyad;
	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || analysis_pitch_classes < 2 ||
	    display_pitch_classes > 5 || analysis_pitch_classes > 6)
		return dyad;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 4 || longest_chromatic_run(analysis_chroma) >= 4)
		return dyad;

	float strongest_display = 0.0f;
	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		strongest_display = std::max(strongest_display, note_grid_pitch_level(display_grid, pitch_class));
		strongest_analysis = std::max(strongest_analysis, note_grid_pitch_level(analysis_grid, pitch_class));
	}
	if (strongest_display <= 1.0e-6f || strongest_analysis <= 1.0e-6f)
		return dyad;

	float best_score = 0.0f;
	auto consider_root = [&](int root_pitch_class, bool minor) {
		root_pitch_class = ((root_pitch_class % 12) + 12) % 12;
		const int third_pitch_class = (root_pitch_class + (minor ? 3 : 4)) % 12;
		const int opposite_third_pitch_class = (root_pitch_class + (minor ? 4 : 3)) % 12;
		const float display_root = note_grid_pitch_level(display_grid, root_pitch_class);
		const float display_third = note_grid_pitch_level(display_grid, third_pitch_class);
		const float analysis_root = note_grid_pitch_level(analysis_grid, root_pitch_class);
		const float analysis_third = note_grid_pitch_level(analysis_grid, third_pitch_class);
		const float display_anchor = std::min(display_root, display_third);
		const float analysis_anchor = std::min(analysis_root, analysis_third);
		if (display_root < std::max(0.10f, strongest_display * 0.10f) ||
		    display_third < std::max(0.10f, strongest_display * 0.10f) ||
		    analysis_root < std::max(0.06f, strongest_analysis * 0.06f) ||
		    analysis_third < std::max(0.08f, strongest_analysis * 0.08f))
			return;
		if (!note_grid_has_guitar_root_third_voicing(display_grid, root_pitch_class, third_pitch_class) ||
		    !note_grid_has_guitar_root_third_voicing(analysis_grid, root_pitch_class, third_pitch_class))
			return;

		const float display_opposite = note_grid_pitch_level(display_grid, opposite_third_pitch_class);
		const float analysis_opposite = note_grid_pitch_level(analysis_grid, opposite_third_pitch_class);
		if (display_opposite >= std::max(0.12f, display_anchor * 0.78f) ||
		    analysis_opposite >= std::max(0.10f, analysis_anchor * 0.78f))
			return;

		float score = 0.34f + display_anchor * 0.35f + analysis_anchor * 0.26f;
		if (preferred_root >= 0 && root_pitch_class == ((preferred_root % 12) + 12) % 12)
			score += 0.10f;
		if (score <= best_score)
			return;

		best_score = score;
		dyad = make_guitar_plain_triad(root_pitch_class, minor, std::clamp(score, 0.38f, 0.58f));
	};

	if (preferred_root >= 0) {
		consider_root(preferred_root, false);
		consider_root(preferred_root, true);
	}
	for (int root = 0; root < 12; ++root) {
		consider_root(root, false);
		consider_root(root, true);
	}
	return dyad;
}

void append_preferred_guitar_root_third_dyad_alias(ChordResult &chord, const ChordResult &dyad)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;
	if (dyad.root < 0 || !dyad.label[0] || dyad.label[0] == '-')
		return;
	const char *suffix = "";
	const char *root_end = dyad.label + 1;
	if (dyad.label[1] == '#')
		root_end = dyad.label + 2;
	suffix = root_end;
	append_chord_alias(chord, dyad.root, suffix);
}

bool parse_power_chord_component(const char *start, std::size_t len, ParsedRootChord &parsed)
{
	if (!parse_root_chord_component(start, len, parsed) || parsed.quality != RootChordQuality::NoThird)
		return false;

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#')
		root_len = 2;
	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;
	return suffix_is(suffix, suffix_len, "pow");
}

void remove_superseded_guitar_power_aliases(ChordResult &chord, const NoteGrid *grid = nullptr)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	char filtered[sizeof(chord.label)] = {};
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		bool skip = false;
		if (parse_power_chord_component(cursor, len, parsed) &&
		    chord_label_has_unambiguous_root_third_component(chord.label, parsed.root)) {
			skip = true;
			if (grid) {
				bool has_major = false;
				bool has_minor = false;
				const char *scan = chord.label;
				while (*scan) {
					const char *scan_end = std::strchr(scan, '=');
					const std::size_t scan_len =
						scan_end ? static_cast<std::size_t>(scan_end - scan) :
							   std::strlen(scan);
					ParsedRootChord component;
					if (parse_root_chord_component(scan, scan_len, component) &&
					    component.root == parsed.root) {
						has_major = has_major || component.quality == RootChordQuality::Major;
						has_minor = has_minor || component.quality == RootChordQuality::Minor;
					}
					if (!scan_end)
						break;
					scan = scan_end + 1;
				}
				const int third =
					parsed.root + (has_minor && !has_major ? 3 : 4);
				skip = note_grid_pitch_active(*grid, third);
			}
		}
		if (!skip) {
			if (filtered[0])
				append_text(filtered, sizeof(filtered), "=");
			const std::size_t used = std::strlen(filtered);
			const std::size_t copy_len = std::min(len, sizeof(filtered) - used - 1);
			std::memcpy(filtered + used, cursor, copy_len);
			filtered[used + copy_len] = '\0';
		}

		if (!end)
			break;
		cursor = end + 1;
	}

	if (!filtered[0]) {
		chord = ChordResult{};
		return;
	}
	copy_text(chord.label, sizeof(chord.label), filtered);
}

void remove_power_aliases_for_root(ChordResult &chord, int root)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;
	root = ((root % 12) + 12) % 12;

	char filtered[sizeof(chord.label)] = {};
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		const bool skip = parse_power_chord_component(cursor, len, parsed) && parsed.root == root &&
				  chord_label_has_unambiguous_root_third_component(chord.label, root);
		if (!skip) {
			if (filtered[0])
				append_text(filtered, sizeof(filtered), "=");
			const std::size_t used = std::strlen(filtered);
			const std::size_t copy_len = std::min(len, sizeof(filtered) - used - 1);
			std::memcpy(filtered + used, cursor, copy_len);
			filtered[used + copy_len] = '\0';
		}

		if (!end)
			break;
		cursor = end + 1;
	}

	if (!filtered[0]) {
		chord = ChordResult{};
		return;
	}
	copy_text(chord.label, sizeof(chord.label), filtered);
}

float strongest_probe_pitch_class_level(const std::array<float, kNoteProbeCount> &powers, int pitch_class,
					int min_midi, int max_midi)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	float level = 0.0f;
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (midi_pitch_class(midi) == pitch_class)
			level = std::max(level, probe_level(powers, midi));
	}
	return level;
}

float strongest_probe_level(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi)
{
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	float level = 0.0f;
	for (int midi = min_midi; midi <= max_midi; ++midi)
		level = std::max(level, probe_level(powers, midi));
	return level;
}

float strongest_melodic_probe_pitch_class_level(const std::array<float, kNoteProbeCount> &powers,
						int pitch_class, int min_midi, int max_midi)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	float level = 0.0f;
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (midi_pitch_class(midi) == pitch_class)
			level = std::max(level, melodic_candidate_score(powers, midi, true));
	}
	return level;
}

float strongest_melodic_probe_level(const std::array<float, kNoteProbeCount> &powers, int min_midi,
				    int max_midi)
{
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	float level = 0.0f;
	for (int midi = min_midi; midi <= max_midi; ++midi)
		level = std::max(level, melodic_candidate_score(powers, midi, true));
	return level;
}

ChordResult detect_probe_supported_guitar_plain_triad(const NoteGrid &display_grid,
						      const NoteGrid &analysis_grid,
						      const std::array<float, kNoteProbeCount> &powers,
						      int min_midi, int max_midi, int preferred_root)
{
	ChordResult best;
	copy_text(best.label, sizeof(best.label), "--");

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || analysis_pitch_classes < 2 ||
	    display_pitch_classes > 8 || analysis_pitch_classes > 10)
		return best;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 6 || longest_chromatic_run(analysis_chroma) >= 7)
		return best;

	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_probe <= 1.0e-6f)
		return best;

	auto grid_active = [&](int pitch_class) {
		return note_grid_pitch_active(display_grid, pitch_class) ||
		       note_grid_pitch_active(analysis_grid, pitch_class);
	};
	auto grid_level = [&](int pitch_class) {
		return std::max(note_grid_pitch_level(display_grid, pitch_class),
				note_grid_pitch_level(analysis_grid, pitch_class));
	};

	float best_score = 0.0f;
	auto consider = [&](int root, bool minor) {
		root = ((root % 12) + 12) % 12;
		const int third = (root + (minor ? 3 : 4)) % 12;
		const int opposite_third = (root + (minor ? 4 : 3)) % 12;
		const int fifth = (root + 7) % 12;
		const bool display_root = note_grid_pitch_active(display_grid, root);
		const bool display_third = note_grid_pitch_active(display_grid, third);
		const bool display_fifth = note_grid_pitch_active(display_grid, fifth);
		const bool analysis_root = note_grid_pitch_active(analysis_grid, root);
		const bool analysis_third = note_grid_pitch_active(analysis_grid, third);
		const bool analysis_fifth = note_grid_pitch_active(analysis_grid, fifth);
		if (!display_root || !analysis_root)
			return;

		const int display_tones = (display_root ? 1 : 0) + (display_third ? 1 : 0) +
					  (display_fifth ? 1 : 0);
		const int analysis_tones = (analysis_root ? 1 : 0) + (analysis_third ? 1 : 0) +
					   (analysis_fifth ? 1 : 0);
		const int combined_tones = (grid_active(root) ? 1 : 0) + (grid_active(third) ? 1 : 0) +
					   (grid_active(fifth) ? 1 : 0);
		if (display_tones < 2 || analysis_tones < 2 || combined_tones < 2)
			return;

		const float root_probe =
			strongest_probe_pitch_class_level(powers, root, min_midi, max_midi);
		const float third_probe =
			strongest_probe_pitch_class_level(powers, third, min_midi, max_midi);
		const float fifth_probe =
			strongest_probe_pitch_class_level(powers, fifth, min_midi, max_midi);
		const float opposite_probe =
			strongest_probe_pitch_class_level(powers, opposite_third, min_midi, max_midi);
		const float root_norm = root_probe / strongest_probe;
		const float third_norm = third_probe / strongest_probe;
		const float fifth_norm = fifth_probe / strongest_probe;
		const float opposite_norm = opposite_probe / strongest_probe;
		if (root_norm < 0.18f || fifth_norm < 0.070f)
			return;

		const float anchor_norm = std::max(root_norm, fifth_norm);
		const float grid_third = grid_level(third);
		const float grid_opposite = grid_level(opposite_third);
		const bool third_grid_supported = grid_third >= std::max(0.12f, grid_opposite * 1.08f);
		const float third_floor = third_grid_supported ?
						  std::max(0.030f, anchor_norm * 0.030f) :
						  std::max(0.048f, anchor_norm * 0.055f);
		if (third_norm < third_floor)
			return;
		if (!third_grid_supported && third_norm < opposite_norm * 1.12f)
			return;
		if (third_grid_supported && opposite_norm > third_norm * 1.45f)
			return;

		int extra_pitch_classes = 0;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			if (pitch_class == root || pitch_class == third || pitch_class == fifth)
				continue;
			if (note_grid_pitch_active(display_grid, pitch_class))
				++extra_pitch_classes;
		}
		if (extra_pitch_classes > 5 && !third_grid_supported)
			return;

		float score = 0.38f + std::min({root_norm, third_norm, fifth_norm}) * 0.42f +
			      std::min(root_norm, fifth_norm) * 0.12f +
			      static_cast<float>(display_tones + analysis_tones) * 0.035f -
			      static_cast<float>(extra_pitch_classes) * 0.018f;
		if (preferred_root >= 0 && root == ((preferred_root % 12) + 12) % 12)
			score += 0.08f;
		if (score <= best_score)
			return;

		best_score = score;
		best = make_guitar_plain_triad(root, minor, std::clamp(score, 0.38f, 0.62f));
	};

	if (preferred_root >= 0) {
		consider(preferred_root, false);
		consider(preferred_root, true);
	}
	for (int root = 0; root < 12; ++root) {
		consider(root, false);
		consider(root, true);
	}
	return best;
}

void append_guitar_power_probe_third_aliases(ChordResult &chord, const NoteGrid &grid,
					     const std::array<float, kNoteProbeCount> &powers, int min_midi,
					     int max_midi)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-' || !std::strstr(chord.label, "pow"))
		return;

	float strongest_grid = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest_grid = std::max(strongest_grid, note_grid_pitch_level(grid, pitch_class));
	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_grid <= 1.0e-6f || strongest_probe <= 1.0e-6f)
		return;
	const float strongest_melodic_probe = strongest_melodic_probe_level(powers, min_midi, max_midi);

	constexpr float kActiveAliasFloor = 0.12f;
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_power_chord_component(cursor, len, parsed) &&
		    !chord_label_has_root_third_component(chord.label, parsed.root)) {
			const float root_grid =
				note_grid_pitch_supported_level(grid, parsed.root, kActiveAliasFloor);
			const float fifth_grid =
				note_grid_pitch_supported_level(grid, parsed.root + 7, kActiveAliasFloor);
			const float root_probe =
				strongest_probe_pitch_class_level(powers, parsed.root, min_midi, max_midi);
			const float fifth_probe =
				strongest_probe_pitch_class_level(powers, parsed.root + 7, min_midi, max_midi);
			const float minor_third =
				strongest_probe_pitch_class_level(powers, parsed.root + 3, min_midi, max_midi);
			const float major_third =
				strongest_probe_pitch_class_level(powers, parsed.root + 4, min_midi, max_midi);
			const float anchor =
				std::max({root_probe, fifth_probe, std::min(root_grid, fifth_grid) * 0.50f});
			const float third_floor =
				std::max({strongest_probe * 0.0015f, anchor * 0.004f, 0.0004f});
			const float grid_anchor = std::min(root_grid, fifth_grid);
			const float grid_third_floor = std::max(0.10f, grid_anchor * 0.32f);
			const float grid_minor =
				note_grid_pitch_supported_level(grid, parsed.root + 3, kActiveAliasFloor);
			const float grid_major =
				note_grid_pitch_supported_level(grid, parsed.root + 4, kActiveAliasFloor);
			const bool grid_thirdless = grid_minor < grid_third_floor && grid_major < grid_third_floor;
			const float single_third_floor =
				grid_thirdless ? std::max(third_floor, anchor * 0.055f) : third_floor;
			const float melodic_root =
				strongest_melodic_probe_pitch_class_level(powers, parsed.root, min_midi,
									 max_midi);
			const float melodic_fifth =
				strongest_melodic_probe_pitch_class_level(powers, parsed.root + 7,
									 min_midi, max_midi);
			const float melodic_minor =
				strongest_melodic_probe_pitch_class_level(powers, parsed.root + 3,
									 min_midi, max_midi);
			const float melodic_major =
				strongest_melodic_probe_pitch_class_level(powers, parsed.root + 4,
									 min_midi, max_midi);
			const float melodic_anchor = std::max(melodic_root, melodic_fifth);
			const float melodic_competing_floor =
				std::max({strongest_melodic_probe * 0.001f, melodic_anchor * 0.015f, 0.0002f});
			const float melodic_third_floor =
				std::max({strongest_melodic_probe * 0.001f,
					  melodic_anchor * (grid_thirdless ? 0.09f : 0.015f),
					  0.0002f});
			const float strong_third_margin = grid_thirdless ? 1.60f : 1.10f;
			const float weak_third_margin = grid_thirdless ? 1.60f : 1.02f;
			const bool competing_minor =
				melodic_minor >= melodic_competing_floor && melodic_minor >= melodic_major * 0.70f;
			const bool competing_major =
				melodic_major >= melodic_competing_floor && melodic_major >= melodic_minor * 0.70f;
			const bool strong_direct_minor =
				minor_third >= std::max(single_third_floor, anchor * 0.004f) &&
				minor_third >= major_third * strong_third_margin;
			const bool strong_direct_major =
				major_third >= std::max(single_third_floor, anchor * 0.004f) &&
				major_third >= minor_third * strong_third_margin;
			const bool primary_power_component = cursor == chord.label && std::strchr(chord.label, '=') != nullptr;
			const float primary_power_third_floor = std::max({anchor * 0.040f, 0.005f, 0.0004f});
			const bool primary_power_direct_minor =
				primary_power_component && grid_thirdless &&
				minor_third >= primary_power_third_floor &&
				minor_third >= major_third * strong_third_margin;
			const bool primary_power_direct_major =
				primary_power_component && grid_thirdless &&
				major_third >= primary_power_third_floor &&
				major_third >= minor_third * strong_third_margin;
				const bool strong_melodic_minor =
					melodic_minor >= melodic_third_floor &&
					melodic_minor >= melodic_major * strong_third_margin;
			const bool strong_melodic_major =
				melodic_major >= melodic_third_floor &&
				melodic_major >= melodic_minor * strong_third_margin;
			const float consistent_probe_third_floor =
				std::max({third_floor, anchor * 0.030f, 0.018f});
			const bool consistent_probe_minor =
				grid_thirdless &&
				minor_third >= consistent_probe_third_floor &&
				minor_third >= major_third * 1.22f &&
				melodic_minor >= melodic_third_floor * 0.70f &&
				melodic_minor >= melodic_major * 1.18f;
			const bool consistent_probe_major =
				grid_thirdless &&
				major_third >= consistent_probe_third_floor &&
				major_third >= minor_third * 1.22f &&
				melodic_major >= melodic_third_floor * 0.70f &&
				melodic_major >= melodic_minor * 1.18f;
			const bool choose_minor =
				strong_direct_minor || primary_power_direct_minor || strong_melodic_minor ||
				consistent_probe_minor ||
				(minor_third >= single_third_floor &&
				 minor_third >= major_third * weak_third_margin &&
				 !competing_major);
			const bool choose_major =
				strong_direct_major || primary_power_direct_major || strong_melodic_major ||
				consistent_probe_major ||
				(major_third >= single_third_floor &&
				 major_third >= minor_third * weak_third_margin &&
				 !competing_minor);
			const bool melodic_only_quality =
				!strong_direct_minor && !strong_direct_major &&
				(strong_melodic_minor != strong_melodic_major) &&
				minor_third < single_third_floor && major_third < single_third_floor;
			if (melodic_only_quality) {
				append_chord_alias(chord, parsed.root, "");
				append_chord_alias(chord, parsed.root, "m");
			} else if (choose_minor != choose_major) {
				append_chord_alias(chord, parsed.root, choose_minor ? "m" : "");
			}
		}

		if (!end)
			break;
		cursor = end + 1;
	}
}

void append_guitar_power_quality_candidates(ChordResult &chord, const NoteGrid &grid,
					    const std::array<float, kNoteProbeCount> &powers, int min_midi,
					    int max_midi)
{
	(void)chord;
	(void)grid;
	(void)powers;
	(void)min_midi;
	(void)max_midi;
	// Thirdless power evidence should stay labeled as pow. Clear single-third evidence
	// is handled by append_guitar_power_probe_third_aliases above.
}

bool append_guitar_thirdless_dyad_quality_aliases(ChordResult &chord,
						  const NoteGrid &display_grid,
						  const NoteGrid &analysis_grid,
						  const std::array<float, kNoteProbeCount> &powers,
						  int min_midi,
						  int max_midi)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return false;

	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_probe <= 1.0e-6f)
		return false;
	const float strongest_melodic_probe = strongest_melodic_probe_level(powers, min_midi, max_midi);
	const bool scan_supported_roots =
		chord_label_has_guitar_extension_or_alteration(chord.label) ||
		std::strstr(chord.label, "pow") != nullptr || std::strstr(chord.label, "sus") != nullptr;

	bool appended = false;
	for (int root = 0; root < 12; ++root) {
		const bool labeled_root = chord_label_has_root_component(chord.label, root);
		if (!labeled_root && !scan_supported_roots)
			continue;
		if (!supported_guitar_root_fifth_dyad(display_grid, analysis_grid, root))
			continue;

		const float root_probe = strongest_probe_pitch_class_level(powers, root, min_midi, max_midi);
		const float fifth_probe = strongest_probe_pitch_class_level(powers, root + 7, min_midi, max_midi);
		const float minor_third = strongest_probe_pitch_class_level(powers, root + 3, min_midi, max_midi);
		const float major_third = strongest_probe_pitch_class_level(powers, root + 4, min_midi, max_midi);
		const float anchor = std::max(root_probe, fifth_probe);
		constexpr float kActiveAliasFloor = 0.12f;
		const float display_root = note_grid_pitch_supported_level(display_grid, root, kActiveAliasFloor);
		const float display_fifth = note_grid_pitch_supported_level(display_grid, root + 7, kActiveAliasFloor);
		const float analysis_root = note_grid_pitch_supported_level(analysis_grid, root, kActiveAliasFloor);
		const float analysis_fifth = note_grid_pitch_supported_level(analysis_grid, root + 7, kActiveAliasFloor);
		const float grid_anchor =
			std::max(std::min(display_root, display_fifth), std::min(analysis_root, analysis_fifth));
		const float display_minor =
			note_grid_pitch_supported_level(display_grid, root + 3, kActiveAliasFloor);
		const float display_major =
			note_grid_pitch_supported_level(display_grid, root + 4, kActiveAliasFloor);
		const float analysis_minor =
			note_grid_pitch_supported_level(analysis_grid, root + 3, kActiveAliasFloor);
		const float analysis_major =
			note_grid_pitch_supported_level(analysis_grid, root + 4, kActiveAliasFloor);
		const float grid_third_floor = std::max(0.12f, grid_anchor * 0.32f);
		const bool grid_minor = std::max(display_minor, analysis_minor) >= grid_third_floor;
		const bool grid_major = std::max(display_major, analysis_major) >= grid_third_floor;
		if (!labeled_root) {
			const bool compact_display = note_grid_active_pitch_class_count(display_grid) <= 5;
			const bool root_visible = note_grid_pitch_active(display_grid, root);
			const bool fifth_visible = note_grid_pitch_active(display_grid, root + 7);
			const bool weak_grid_third = !grid_minor && !grid_major;
			if (!compact_display || !root_visible || !fifth_visible || !weak_grid_third)
				continue;
		}
		const float third_floor = std::max({strongest_probe * 0.0015f, anchor * 0.004f, 0.0004f});
		const bool has_minor = minor_third >= third_floor;
		const bool has_major = major_third >= third_floor;
		const bool grid_thirdless = !grid_minor && !grid_major;
		const float single_third_floor =
			grid_thirdless ? std::max(third_floor, anchor * 0.055f) : third_floor;
		const float melodic_root =
			strongest_melodic_probe_pitch_class_level(powers, root, min_midi, max_midi);
		const float melodic_fifth =
			strongest_melodic_probe_pitch_class_level(powers, root + 7, min_midi, max_midi);
		const float melodic_minor =
			strongest_melodic_probe_pitch_class_level(powers, root + 3, min_midi, max_midi);
		const float melodic_major =
			strongest_melodic_probe_pitch_class_level(powers, root + 4, min_midi, max_midi);
		const float melodic_anchor = std::max(melodic_root, melodic_fifth);
		const float melodic_competing_floor =
			std::max({strongest_melodic_probe * 0.001f, melodic_anchor * 0.015f, 0.0002f});
		const float melodic_third_floor =
			std::max({strongest_melodic_probe * 0.001f,
				  melodic_anchor * (grid_thirdless ? 0.09f : 0.015f), 0.0002f});
		const float strong_third_margin = grid_thirdless ? 1.60f : 1.10f;
		const float weak_third_margin = grid_thirdless ? 1.60f : 1.02f;
		const bool competing_minor =
			melodic_minor >= melodic_competing_floor && melodic_minor >= melodic_major * 0.70f;
		const bool competing_major =
			melodic_major >= melodic_competing_floor && melodic_major >= melodic_minor * 0.70f;
		const bool strong_direct_minor =
			has_minor && minor_third >= std::max(single_third_floor, anchor * 0.004f) &&
			minor_third >= major_third * strong_third_margin;
		const bool strong_direct_major =
			has_major && major_third >= std::max(single_third_floor, anchor * 0.004f) &&
			major_third >= minor_third * strong_third_margin;
		const bool strong_melodic_minor =
			melodic_minor >= melodic_third_floor &&
			melodic_minor >= melodic_major * strong_third_margin;
		const bool strong_melodic_major =
			melodic_major >= melodic_third_floor &&
			melodic_major >= melodic_minor * strong_third_margin;
		const bool choose_minor = strong_direct_minor || strong_melodic_minor ||
					  (has_minor && minor_third >= single_third_floor &&
					   minor_third >= major_third * weak_third_margin && !competing_major);
		const bool choose_major = strong_direct_major || strong_melodic_major ||
					  (has_major && major_third >= single_third_floor &&
					   major_third >= minor_third * weak_third_margin && !competing_minor);
		const bool melodic_only_quality =
			!strong_direct_minor && !strong_direct_major &&
			(strong_melodic_minor != strong_melodic_major) &&
			minor_third < single_third_floor && major_third < single_third_floor;
		bool root_has_power = false;
		const char *cursor = chord.label;
		while (*cursor) {
			const char *end = std::strchr(cursor, '=');
			const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
			ParsedRootChord parsed_power;
			if (parse_power_chord_component(cursor, len, parsed_power) && parsed_power.root == root) {
				root_has_power = true;
				break;
			}
			if (!end)
				break;
			cursor = end + 1;
		}
		const bool root_flanked_by_noise =
			(note_grid_pitch_active(display_grid, root - 1) &&
			 note_grid_pitch_active(display_grid, root + 1)) ||
			(note_grid_pitch_active(analysis_grid, root - 1) &&
			 note_grid_pitch_active(analysis_grid, root + 1));
		const bool weak_power_quality_probe =
			root_has_power &&
			grid_thirdless &&
			root_flanked_by_noise &&
			note_grid_active_pitch_class_count(analysis_grid) >= 5 &&
			!chord_label_has_root_third_component(chord.label, root) &&
			(melodic_minor >= melodic_competing_floor ||
			 melodic_major >= melodic_competing_floor) &&
			std::max(minor_third, major_third) < single_third_floor;
		if (melodic_only_quality) {
			append_chord_alias(chord, root, "");
			append_chord_alias(chord, root, "m");
			appended = true;
		} else if (choose_minor != choose_major) {
			const bool minor = choose_minor;
			append_chord_alias(chord, root, minor ? "m" : "");
			appended = true;
		} else if (labeled_root &&
			   (!root_has_power || (grid_thirdless &&
						!root_flanked_by_noise &&
						!chord_label_has_root_third_component(chord.label, root)) ||
			    weak_power_quality_probe)) {
			append_chord_alias(chord, root, "");
			append_chord_alias(chord, root, "m");
			appended = true;
		}
	}
	return appended;
}

void append_guitar_probe_opposite_quality_aliases(ChordResult &chord, const NoteGrid &grid,
						  const std::array<float, kNoteProbeCount> &powers,
						  int min_midi,
						  int max_midi)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_probe <= 1.0e-6f)
		return;

	struct AliasToAdd {
		int root = -1;
		char suffix[4] = {};
	};
	FixedList<AliasToAdd, 12> aliases;
	constexpr float kActiveAliasFloor = 0.12f;

	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) &&
		    (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor)) {
			const int root = parsed.root;
			ChordResult primary = {};
			primary.root = root;
			primary.confidence = chord.confidence;
			primary.tones[root] = true;
			primary.tones[(root + (parsed.quality == RootChordQuality::Minor ? 3 : 4)) % 12] = true;
			primary.tones[(root + 7) % 12] = true;
			if (note_grid_chord_tone_count(grid, primary) < 3) {
				const float grid_root =
					note_grid_pitch_supported_level(grid, root, kActiveAliasFloor);
				const float grid_fifth =
					note_grid_pitch_supported_level(grid, root + 7, kActiveAliasFloor);
				if (grid_root >= 0.10f && grid_fifth >= 0.08f) {
					const float root_probe =
						strongest_probe_pitch_class_level(powers, root, min_midi,
										 max_midi);
					const float fifth_probe =
						strongest_probe_pitch_class_level(powers, root + 7,
										 min_midi, max_midi);
					const float anchor = std::max(root_probe, fifth_probe);
					const float floor =
						std::max({strongest_probe * 0.003f, anchor * 0.02f,
							  0.0004f});
					AliasToAdd alias;
					alias.root = root;
					bool add_alias = false;
					if (parsed.quality == RootChordQuality::Major) {
						const float minor_third =
							strongest_probe_pitch_class_level(powers, root + 3,
											 min_midi,
											 max_midi);
						const float major_third =
							strongest_probe_pitch_class_level(powers, root + 4,
											 min_midi,
											 max_midi);
						if (minor_third >= floor &&
						    (major_third <= floor || minor_third >= major_third * 0.78f)) {
							copy_text(alias.suffix, sizeof(alias.suffix), "m");
							add_alias = true;
						}
					} else {
						const float major_third =
							strongest_probe_pitch_class_level(powers, root + 4,
											 min_midi,
											 max_midi);
						const float minor_third =
							strongest_probe_pitch_class_level(powers, root + 3,
											 min_midi,
											 max_midi);
						if (major_third >= floor &&
						    (minor_third <= floor || major_third >= minor_third * 0.78f)) {
							copy_text(alias.suffix, sizeof(alias.suffix), "");
							add_alias = true;
						}
					}
					if (add_alias)
						aliases.push_back(alias);
				}
			}
		}

		if (!end)
			break;
		cursor = end + 1;
	}

	for (const AliasToAdd &alias : aliases)
		append_chord_alias(chord, alias.root, alias.suffix);
}

bool append_guitar_rootless_dyad_aliases(ChordResult &chord, const NoteGrid &display_grid,
					 const NoteGrid &analysis_grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-' ||
	    chord_label_has_guitar_extension_or_alteration(chord.label) || std::strstr(chord.label, "pow") ||
	    std::strstr(chord.label, "sus"))
		return false;

	bool appended = false;
	constexpr float kActiveAliasFloor = 0.12f;
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) &&
		    (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor)) {
			const int third = parsed.root + (parsed.quality == RootChordQuality::Minor ? 3 : 4);
			const int fifth = parsed.root + 7;
			const float root_level =
				std::max(note_grid_pitch_supported_level(display_grid, parsed.root,
									 kActiveAliasFloor),
					 note_grid_pitch_supported_level(analysis_grid, parsed.root,
									 kActiveAliasFloor));
			const float third_level =
				std::max(note_grid_pitch_supported_level(display_grid, third, kActiveAliasFloor),
					 note_grid_pitch_supported_level(analysis_grid, third, kActiveAliasFloor));
			const float fifth_actual =
				std::max(note_grid_pitch_level(display_grid, fifth),
					 note_grid_pitch_level(analysis_grid, fifth));
			const float anchor = std::min(root_level, third_level);
			if (anchor >= kActiveAliasFloor && fifth_actual < anchor * 0.28f) {
				const int alias_root = parsed.root - (parsed.quality == RootChordQuality::Minor ? 4 : 3);
				append_chord_alias(chord, alias_root,
						   parsed.quality == RootChordQuality::Minor ? "" : "m");
				appended = true;
			}
		}

		if (!end)
			break;
		cursor = end + 1;
	}
	return appended;
}

void append_supported_guitar_extension_aliases_for_root(ChordResult &chord, const NoteGrid &grid, int root_pitch_class,
						       bool strict_levels = false)
{
	if (root_pitch_class < 0)
		return;

	const float active_alias_floor = strict_levels ? 0.0f : 0.12f;
	const float root = note_grid_pitch_supported_level(grid, root_pitch_class, active_alias_floor);
	const float major_third = note_grid_pitch_supported_level(grid, root_pitch_class + 4, active_alias_floor);
	const float minor_third = note_grid_pitch_supported_level(grid, root_pitch_class + 3, active_alias_floor);
	const float fifth = note_grid_pitch_supported_level(grid, root_pitch_class + 7, active_alias_floor);
	const float flat_fifth = note_grid_pitch_supported_level(grid, root_pitch_class + 6, active_alias_floor);
	const float aug_fifth = note_grid_pitch_supported_level(grid, root_pitch_class + 8, active_alias_floor);
	const float sixth = note_grid_pitch_supported_level(grid, root_pitch_class + 9, active_alias_floor);
	const float flat_seventh = note_grid_pitch_supported_level(grid, root_pitch_class + 10, active_alias_floor);
	const float major_seventh = note_grid_pitch_supported_level(grid, root_pitch_class + 11, active_alias_floor);
	const float ninth = note_grid_pitch_supported_level(grid, root_pitch_class + 2, active_alias_floor);
	const float fourth = note_grid_pitch_supported_level(grid, root_pitch_class + 5, active_alias_floor);
	const float major_third_raw = note_grid_pitch_level(grid, root_pitch_class + 4);
	const float minor_third_raw = note_grid_pitch_level(grid, root_pitch_class + 3);
	const float ninth_raw = note_grid_pitch_level(grid, root_pitch_class + 2);
	const float fourth_raw = note_grid_pitch_level(grid, root_pitch_class + 5);
	const float kCoreFloor = strict_levels ? 0.16f : 0.12f;
	const float kRootAnchorFloor = strict_levels ? 0.14f : 0.06f;
	const float kRichMajorThirdFloor = strict_levels ? 0.18f : 0.12f;
	const float kExtensionFloor = strict_levels ? 0.12f : 0.08f;
	const float kCompactExtensionFloor = strict_levels ? 0.10f : 0.05f;
	const float kMajorSeventhRatioFloor = strict_levels ? 0.30f : 0.22f;
	if (root < kRootAnchorFloor)
		return;

	const bool has_fifth = fifth >= kCoreFloor;
	const bool has_major = major_third >= kCoreFloor && has_fifth;
	const bool has_strong_major =
		has_major && major_third >= std::max(kRichMajorThirdFloor, std::min(root, fifth) * 0.45f);
	const bool has_clear_major_seventh =
		has_major && major_third >= std::max(kCoreFloor, std::min(root, fifth) * 0.30f) &&
		major_seventh >= std::max(kExtensionFloor, std::min(root, fifth) * kMajorSeventhRatioFloor);
	const bool has_minor = minor_third >= kCoreFloor && has_fifth;
	const bool has_dim = minor_third >= kCoreFloor && flat_fifth >= kCoreFloor;
	const bool has_aug = major_third >= kCoreFloor && aug_fifth >= kCoreFloor && fifth < kCoreFloor;
	int core_min_midi = 0;
	int core_max_midi = 0;
	bool has_core_range = false;
	auto extend_core_range = [&](int pitch_class) {
		int pitch_min = 0;
		int pitch_max = 0;
		if (!note_grid_pitch_midi_range(grid, pitch_class, pitch_min, pitch_max))
			return;
		if (!has_core_range) {
			core_min_midi = pitch_min;
			core_max_midi = pitch_max;
			has_core_range = true;
		} else {
			core_min_midi = std::min(core_min_midi, pitch_min);
			core_max_midi = std::max(core_max_midi, pitch_max);
		}
	};
	extend_core_range(root_pitch_class);
	if (major_third >= kCoreFloor)
		extend_core_range(root_pitch_class + 4);
	if (minor_third >= kCoreFloor || has_dim)
		extend_core_range(root_pitch_class + 3);
	if (has_fifth)
		extend_core_range(root_pitch_class + 7);
	if (has_dim)
		extend_core_range(root_pitch_class + 6);
	if (has_aug)
		extend_core_range(root_pitch_class + 8);
	auto supported_extension = [&](int interval, float level) {
		if (level < kCompactExtensionFloor)
			return false;
		if (!has_core_range)
			return level >= kExtensionFloor;
		if (!note_grid_pitch_in_midi_window(grid, root_pitch_class + interval, core_min_midi - 14,
						    core_max_midi + 16))
			return false;
		return level >= kExtensionFloor || level >= kCompactExtensionFloor;
	};
	auto supported_flat_seventh = [&]() {
		if (supported_extension(10, flat_seventh))
			return true;
		if (flat_seventh < kExtensionFloor || !has_core_range)
			return false;
		if (!note_grid_pitch_in_midi_window(grid, root_pitch_class + 10, core_min_midi - 14,
						    core_max_midi + 16))
			return false;
		const float third = has_major ? major_third : has_minor ? minor_third : 0.0f;
		const float core_anchor = std::min(root, std::min(third, fifth));
		return flat_seventh >= std::max(kExtensionFloor, core_anchor * 0.30f);
	};

	if (has_major) {
		if (supported_flat_seventh() && supported_extension(2, ninth))
			append_chord_alias(chord, root_pitch_class, "9");
		if (has_strong_major && supported_extension(11, major_seventh) && supported_extension(2, ninth))
			append_chord_alias(chord, root_pitch_class, "maj9");
		if (supported_flat_seventh())
			append_chord_alias(chord, root_pitch_class, "7");
		if (has_clear_major_seventh && supported_extension(11, major_seventh))
			append_chord_alias(chord, root_pitch_class, "maj7");
		if (supported_extension(9, sixth))
			append_chord_alias(chord, root_pitch_class, "6");
		if (supported_extension(2, ninth))
			append_chord_alias(chord, root_pitch_class, "add9");
	}
	if (has_minor) {
		if (supported_flat_seventh() && supported_extension(2, ninth))
			append_chord_alias(chord, root_pitch_class, "m9");
		if (supported_flat_seventh())
			append_chord_alias(chord, root_pitch_class, "m7");
		if (supported_extension(9, sixth))
			append_chord_alias(chord, root_pitch_class, "m6");
	}
	if (!has_fifth) {
		const float omitted_fifth_third_floor = std::max(kCoreFloor, root * 0.22f);
		const bool omitted_fifth_major = major_third >= omitted_fifth_third_floor &&
						 major_third >= minor_third * 1.10f;
		const bool omitted_fifth_minor = minor_third >= omitted_fifth_third_floor &&
						 minor_third >= major_third * 1.10f;
		if (omitted_fifth_major && supported_flat_seventh())
			append_chord_alias(chord, root_pitch_class, "7");
		if (omitted_fifth_major &&
		    major_seventh >= std::max(kExtensionFloor, std::min(root, major_third) * 0.26f) &&
		    supported_extension(11, major_seventh))
			append_chord_alias(chord, root_pitch_class, "maj7");
		if (omitted_fifth_minor && supported_flat_seventh())
			append_chord_alias(chord, root_pitch_class, "m7");
	}
	if (has_dim) {
		if (supported_extension(9, sixth))
			append_chord_alias(chord, root_pitch_class, "dim7");
		if (supported_extension(10, flat_seventh))
			append_chord_alias(chord, root_pitch_class, "m7b5");
		append_chord_alias(chord, root_pitch_class, "dim");
	}
	if (has_aug)
		append_chord_alias(chord, root_pitch_class, "aug");
	if (has_fifth) {
		const float third_raw = std::max(major_third_raw, minor_third_raw);
		const float suspended_raw_floor = strict_levels ? 0.075f : 0.045f;
		const bool weak_or_lower_third = third_raw < 0.040f;
		if (ninth >= kCoreFloor && ninth_raw >= suspended_raw_floor &&
		    ((!has_major && !has_minor) || weak_or_lower_third || ninth_raw >= third_raw * 1.18f))
			append_chord_alias(chord, root_pitch_class, "sus2");
		if (fourth >= kCoreFloor && fourth_raw >= suspended_raw_floor &&
		    ((!has_major && !has_minor) || weak_or_lower_third || fourth_raw >= third_raw * 1.18f))
			append_chord_alias(chord, root_pitch_class, "sus4");
	}
}

void append_supported_guitar_extension_aliases(ChordResult &chord, const NoteGrid &grid,
					      bool relaxed_analysis_roots = false)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	std::array<bool, 12> roots = {};
	roots[((chord.root % 12) + 12) % 12] = true;
	for (int root = 0; root < 12; ++root) {
		if (chord_label_has_root_component(chord.label, root))
			roots[root] = true;
	}
	float strongest = 0.0f;
	for (int root = 0; root < 12; ++root)
		strongest = std::max(strongest, note_grid_pitch_level(grid, root));
	const float scanned_root_floor = relaxed_analysis_roots ? std::max(0.08f, strongest * 0.10f) :
								  std::max(0.12f, strongest * 0.16f);
	const bool simple_primary_chord = !chord_label_has_guitar_extension_or_alteration(chord.label);
	if (note_grid_active_pitch_class_count(grid) <= 6 && strongest > 0.0f) {
		for (int root = 0; root < 12; ++root) {
			if (simple_primary_chord && chord.tones[root] &&
			    !chord_label_has_root_component(chord.label, root))
				continue;
			bool adjacent_to_component_root = false;
			for (int existing_root = 0; existing_root < 12; ++existing_root) {
				if (!roots[existing_root])
					continue;
				const int distance = std::abs(root - existing_root);
				if (std::min(distance, 12 - distance) == 1) {
					adjacent_to_component_root = true;
					break;
				}
			}
			if (!adjacent_to_component_root && note_grid_pitch_level(grid, root) >= scanned_root_floor)
				roots[root] = true;
		}
	}
	for (int root = 0; root < 12; ++root) {
		if (roots[root])
			append_supported_guitar_extension_aliases_for_root(
				chord, grid, root,
				!relaxed_analysis_roots && !chord_label_has_root_component(chord.label, root));
	}
}

void append_probe_supported_guitar_extension_aliases(ChordResult &chord, const NoteGrid &display_grid,
						     const NoteGrid &analysis_grid,
						     const std::array<float, kNoteProbeCount> &powers,
						     int min_midi, int max_midi)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || analysis_pitch_classes < 2 ||
	    display_pitch_classes > 8 || analysis_pitch_classes > 10)
		return;

	const std::array<float, 12> display_chroma = note_grid_chroma(display_grid);
	const std::array<float, 12> analysis_chroma = note_grid_chroma(analysis_grid);
	if (longest_chromatic_run(display_chroma) >= 6 || longest_chromatic_run(analysis_chroma) >= 7)
		return;

	const float strongest_probe = strongest_probe_level(powers, min_midi, max_midi);
	if (strongest_probe <= 1.0e-6f)
		return;

	struct RootToScan {
		int root = -1;
		RootChordQuality quality = RootChordQuality::Other;
		bool probe_extensions_allowed = false;
	};
	FixedList<RootToScan, 12> roots;
	auto add_root = [&](int root, RootChordQuality quality, bool probe_extensions_allowed) {
		root = ((root % 12) + 12) % 12;
		for (RootToScan &existing : roots) {
			if (existing.root == root) {
				if (existing.quality == RootChordQuality::NoThird &&
				    quality != RootChordQuality::Other)
					existing.quality = quality;
				existing.probe_extensions_allowed =
					existing.probe_extensions_allowed || probe_extensions_allowed;
				return;
			}
		}
		RootToScan entry;
		entry.root = root;
		entry.quality = quality;
		entry.probe_extensions_allowed = probe_extensions_allowed;
		roots.push_back(entry);
	};

	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) &&
		    (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor ||
		     parsed.quality == RootChordQuality::NoThird)) {
			std::size_t root_len = 1;
			if (len > 1 && cursor[1] == '#')
				root_len = 2;
			const char *suffix = cursor + root_len;
			const std::size_t suffix_len = len - root_len;
			const bool extension_component =
				suffix_is(suffix, suffix_len, "6") || suffix_is(suffix, suffix_len, "7") ||
				suffix_is(suffix, suffix_len, "9") ||
				suffix_is(suffix, suffix_len, "maj7") ||
				suffix_is(suffix, suffix_len, "maj9") ||
				suffix_is(suffix, suffix_len, "add9") ||
				suffix_is(suffix, suffix_len, "m6") ||
				suffix_is(suffix, suffix_len, "m7") ||
				suffix_is(suffix, suffix_len, "m9");
			add_root(parsed.root, parsed.quality,
				 parsed.quality == RootChordQuality::NoThird || extension_component);
		}
		if (!end)
			break;
		cursor = end + 1;
	}

	auto grid_level = [&](const NoteGrid &grid, int pitch_class) {
		return note_grid_pitch_supported_level(grid, pitch_class, 0.0f);
	};
	auto combined_grid_level = [&](int pitch_class) {
		return std::max(grid_level(display_grid, pitch_class), grid_level(analysis_grid, pitch_class));
	};
	auto probe_norm = [&](int pitch_class) {
		return strongest_probe_pitch_class_level(powers, pitch_class, min_midi, max_midi) /
		       strongest_probe;
	};
	auto supported_extension = [&](int root, int interval, float level, float core_anchor) {
		if (level < std::max(0.075f, core_anchor * 0.16f))
			return false;
		if (note_grid_pitch_active(display_grid, root + interval) ||
		    note_grid_pitch_active(analysis_grid, root + interval))
			return true;
		return level >= std::max(0.095f, core_anchor * 0.20f);
	};

	for (const RootToScan &entry : roots) {
		const int root = entry.root;
		if (root < 0)
			continue;
		if (!entry.probe_extensions_allowed)
			continue;
		if (!note_grid_pitch_active(display_grid, root) && !note_grid_pitch_active(analysis_grid, root))
			continue;

		const float root_support = std::max(probe_norm(root), combined_grid_level(root));
		const float fifth_support = std::max(probe_norm(root + 7), combined_grid_level(root + 7));
		if (root_support < 0.10f || fifth_support < 0.075f)
			continue;

		const float major_probe = probe_norm(root + 4);
		const float minor_probe = probe_norm(root + 3);
		const float major_support = std::max(major_probe, combined_grid_level(root + 4));
		const float minor_support = std::max(minor_probe, combined_grid_level(root + 3));
		const float third_floor = std::max(0.070f, std::min(root_support, fifth_support) * 0.12f);
		const bool label_major = entry.quality == RootChordQuality::Major;
		const bool label_minor = entry.quality == RootChordQuality::Minor;
		const bool no_third = entry.quality == RootChordQuality::NoThird;
		const bool major_supported =
			(label_major && major_support >= third_floor) ||
			(no_third && major_support >= third_floor && major_probe >= minor_probe * 1.08f);
		const bool minor_supported =
			(label_minor && minor_support >= third_floor) ||
			(no_third && minor_support >= third_floor && minor_probe >= major_probe * 1.08f);
		const float major_core_anchor = std::min({root_support, major_support, fifth_support});
		const float minor_core_anchor = std::min({root_support, minor_support, fifth_support});
		const float sixth = probe_norm(root + 9);
		const float flat_seventh = probe_norm(root + 10);
		const float major_seventh = probe_norm(root + 11);

		if (major_supported) {
			if (no_third)
				append_chord_alias(chord, root, "");
			if (supported_extension(root, 10, flat_seventh, major_core_anchor))
				append_chord_alias(chord, root, "7");
			if (supported_extension(root, 11, major_seventh, major_core_anchor))
				append_chord_alias(chord, root, "maj7");
			if (supported_extension(root, 9, sixth, major_core_anchor))
				append_chord_alias(chord, root, "6");
		}
		if (minor_supported) {
			if (no_third)
				append_chord_alias(chord, root, "m");
			if (supported_extension(root, 10, flat_seventh, minor_core_anchor))
				append_chord_alias(chord, root, "m7");
		}
	}
}

void append_display_supported_guitar_extension_aliases(ChordResult &chord, const NoteGrid &grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	const int active_pitch_classes = note_grid_active_pitch_class_count(grid);
	if (active_pitch_classes < 3 || active_pitch_classes > 6)
		return;

	const std::array<float, 12> chroma = note_grid_chroma(grid);
	if (longest_chromatic_run(chroma) >= 4)
		return;

	std::array<bool, 12> roots = {};
	bool has_root = false;
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed)) {
			const int root = ((parsed.root % 12) + 12) % 12;
			roots[root] = true;
			has_root = true;
		}

		if (!end)
			break;
		cursor = end + 1;
	}
	if (!has_root && chord.root >= 0)
		roots[((chord.root % 12) + 12) % 12] = true;

	for (int root = 0; root < 12; ++root) {
		if (roots[root])
			append_supported_guitar_extension_aliases_for_root(chord, grid, root);
	}
}

void append_supported_guitar_base_triad_aliases_for_extensions(ChordResult &chord, const NoteGrid &grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	std::array<bool, 12> major_roots = {};
	std::array<bool, 12> minor_roots = {};
	const char *cursor = chord.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);
		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed)) {
			const int root = ((parsed.root % 12) + 12) % 12;
			if (parsed.quality == RootChordQuality::Major)
				major_roots[root] = true;
			else if (parsed.quality == RootChordQuality::Minor)
				minor_roots[root] = true;
		}
		if (!end)
			break;
		cursor = end + 1;
	}

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return;

	constexpr float kActiveAliasFloor = 0.12f;
	auto append_if_core_supported = [&](int root, bool minor) {
		const float root_level = note_grid_pitch_supported_level(grid, root, kActiveAliasFloor);
		const float third = note_grid_pitch_supported_level(grid, root + (minor ? 3 : 4),
								    kActiveAliasFloor);
		const float fifth = note_grid_pitch_supported_level(grid, root + 7, kActiveAliasFloor);
		if (root_level < std::max(0.06f, strongest * 0.06f) ||
		    third < std::max(0.08f, std::min(root_level, fifth) * 0.16f) ||
		    fifth < std::max(0.08f, strongest * 0.08f))
			return;
		append_chord_alias(chord, root, minor ? "m" : "");
	};

	for (int root = 0; root < 12; ++root) {
		if (major_roots[root])
			append_if_core_supported(root, false);
		if (minor_roots[root])
			append_if_core_supported(root, true);
	}
}

void append_supported_guitar_symmetric_altered_aliases(ChordResult &chord, const NoteGrid &grid)
{
	if (chord.root < 0 || !chord.label[0] || chord.label[0] == '-')
		return;

	const int active_pitch_classes = note_grid_active_pitch_class_count(grid);
	if (active_pitch_classes > 6)
		return;

	float strongest = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest = std::max(strongest, note_grid_pitch_level(grid, pitch_class));
	if (strongest <= 1.0e-6f)
		return;

	const float altered_floor = std::max(0.12f, strongest * 0.16f);
	auto supported = [&](int pitch_class) {
		return note_grid_pitch_level(grid, pitch_class) >= altered_floor;
	};

	for (int root = 0; root < 12; ++root) {
		const float root_level = note_grid_pitch_level(grid, root);
		const float third = note_grid_pitch_level(grid, root + 4);
		const float aug_fifth = note_grid_pitch_level(grid, root + 8);
		const float natural_fifth = note_grid_pitch_level(grid, root + 7);
		if (root_level >= altered_floor && third >= altered_floor && aug_fifth >= altered_floor &&
		    natural_fifth < altered_floor * 0.60f) {
			append_chord_alias(chord, root, "aug");
			append_chord_alias(chord, root + 4, "aug");
			append_chord_alias(chord, root + 8, "aug");
		}

		if (supported(root) && supported(root + 3) && supported(root + 6) && supported(root + 9)) {
			append_chord_alias(chord, root, "dim7");
			append_chord_alias(chord, root + 3, "dim7");
			append_chord_alias(chord, root + 6, "dim7");
			append_chord_alias(chord, root + 9, "dim7");
		}
	}
}

ChordResult detect_guitar_chord_from_grid(const NoteGrid &grid, bool allow_extensions)
{
	const std::array<float, 12> chroma = note_grid_chroma(grid);
	std::array<float, 12> caged_chroma = chroma;
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0)
				continue;
			const int pitch_class = ((cell.midi % 12) + 12) % 12;
			caged_chroma[pitch_class] = std::max(caged_chroma[pitch_class], kGuitarCagedPresenceFloor);
		}
	}
	const int preferred_root = lowest_note_grid_pitch_class(grid);
	ChordResult chord = detect_chord(chroma, preferred_root, allow_extensions);
	const ChordResult caged = detect_caged_guitar_chord(caged_chroma, preferred_root);
	const ChordResult caged_altered = detect_caged_guitar_chord(caged_chroma, preferred_root, true);
	const ChordResult root_third_dyad = detect_preferred_guitar_root_third_dyad(grid, preferred_root);
	auto with_root_third_alias = [&](ChordResult selected) {
		if (selected.root < 0 || !selected.label[0] || selected.label[0] == '-')
			return root_third_dyad;
		if (root_third_dyad.root >= 0 && std::strstr(selected.label, "pow") &&
		    root_third_dyad.confidence >= selected.confidence + 0.20f)
			return root_third_dyad;
		if (root_third_dyad.root == selected.root &&
		    chord_label_has_guitar_extension_or_alteration(selected.label) &&
		    root_third_dyad.confidence >= selected.confidence)
			return root_third_dyad;
		if (root_third_dyad.root == selected.root)
			append_preferred_guitar_root_third_dyad_alias(selected, root_third_dyad);
		return selected;
	};

	if (caged.root < 0) {
		if (chord.root < 0) {
			if (caged_altered.root >= 0)
				return with_root_third_alias(caged_altered);
		}
		return with_root_third_alias(chord);
	}
	if (chord.root < 0)
		return with_root_third_alias(caged);

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

	auto guitar_pitch_class_active = [&](int pitch_class) {
		pitch_class = ((pitch_class % 12) + 12) % 12;
		if (grid.cells[pitch_class].active)
			return true;
		for (const auto &row : grid.rows) {
			if (row[pitch_class].active)
				return true;
		}
		return false;
	};
	auto make_guitar_triad = [&](int root, const char *suffix, std::initializer_list<int> intervals) {
		ChordResult triad;
		triad.root = root;
		triad.confidence = std::max({chord.confidence, caged.confidence, 0.58f});
		triad.margin = std::max(chord.margin, caged.margin);
		triad.uncertain = false;
		std::snprintf(triad.label, sizeof(triad.label), "%s%s", note_name(root), suffix);
		for (int interval : intervals)
			triad.tones[(root + interval) % 12] = true;
		return triad;
	};
	if (std::strstr(chord.label, "pow") && chord.root >= 0) {
		const bool minor_third = guitar_pitch_class_active(chord.root + 3);
		const bool major_third = guitar_pitch_class_active(chord.root + 4);
		if (minor_third && !major_third)
			return make_guitar_triad(chord.root, "m", {0, 3, 7});
		if (major_third && !minor_third)
			return make_guitar_triad(chord.root, "", {0, 4, 7});
	}

	const bool root_adjacent_noise =
		caged.root >= 0 && guitar_pitch_class_active(caged.root) &&
		guitar_pitch_class_active(caged.root - 1) && guitar_pitch_class_active(caged.root + 1);
	if (chord_label_has_guitar_extension_or_alteration(chord.label) && caged.confidence >= 0.58f &&
	    weak_guitar_tone)
		return with_root_third_alias(caged);
	if (chord_label_has_guitar_extension_or_alteration(chord.label) && root_adjacent_noise &&
	    caged.confidence >= kChordConfidenceFloor && caged_tone_cells >= 3)
		return with_root_third_alias(caged);
	if (std::strstr(chord.label, "pow") && std::strstr(caged.label, "pow") == nullptr &&
	    caged.confidence >= 0.38f && caged_tone_cells >= 4)
		return with_root_third_alias(caged);
	if (chord_label_has_guitar_extension_or_alteration(chord.label) && caged.confidence >= 0.50f &&
	    caged_tone_cells >= 4 && non_caged_chord_tone_cells <= 2)
		return with_root_third_alias(caged);
	if (chord_label_has_guitar_extension_or_alteration(chord.label) && caged.confidence >= 0.38f &&
	    caged_tone_cells >= 4 && non_caged_chord_tone_cells <= 3)
		return with_root_third_alias(caged);

	return with_root_third_alias(chord);
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
			     float relative_floor = kNoteRelativeFloor,
			     bool prefer_lower_harmonic_fundamental = false,
			     bool include_harmonic_support = false,
			     float rms_floor = kNoteRmsFloor, float visual_loudness_override = -1.0f)
{
	clear_note_grid(grid);
	if (rms < rms_floor || energy < 1.0e-5f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	float strongest_score = 0.0f;
	NoteCandidateList candidates =
		note_peak_candidates(powers, min_midi, max_midi, max_notes, blocked_pitch_classes,
				     allowed_pitch_classes, suppress_adjacent_neighbors, allowed_midis,
				     relative_floor, include_harmonic_support);
	if (prefer_lower_harmonic_fundamental && max_notes == 1 && !candidates.empty()) {
		NoteCandidate &candidate = candidates[0];
		static constexpr int kHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
		for (int interval : kHarmonicIntervals) {
			const int lower = candidate.midi - interval;
			if (lower < min_midi || lower < kFirstMidi)
				continue;
			const float lower_score = probe_level(powers, lower);
			if (lower_score >= candidate.score * 0.15f) {
				candidate.midi = lower;
				candidate.score = lower_score;
				break;
			}
		}
		for (int adjacent : {candidate.midi - 1, candidate.midi + 1}) {
			if (adjacent < min_midi || adjacent > max_midi)
				continue;
			const float adjacent_score = probe_level(powers, adjacent);
			const float candidate_harmonic_score = melodic_candidate_score(powers, candidate.midi, true);
			const float adjacent_harmonic_score = melodic_candidate_score(powers, adjacent, true);
			if (adjacent_score >= candidate.score * 1.06f &&
			    candidate_harmonic_score <= adjacent_harmonic_score * 1.12f) {
				candidate.midi = adjacent;
				candidate.score = adjacent_score;
			}
		}
	}
	for (const NoteCandidate &candidate : candidates)
		strongest_score = std::max(strongest_score, candidate.score);

	if (strongest_score <= 1.0e-6f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}
	if (rms_floor < kNoteRmsFloor && rms < kNoteRmsFloor && candidates.size() < 2) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	const float visual_loudness =
		visual_loudness_override >= 0.0f ? visual_loudness_override : note_visual_loudness(rms, rms_floor);
	for (const NoteCandidate &candidate : candidates)
		write_note_grid_cell(grid, candidate, strongest_score, visual_loudness);

	write_note_grid_label(state, grid, preferred_root);
}

void set_instrument_chord(InstrumentState &state, const ChordResult &chord, float energy, float rms,
			  float rms_floor = kNoteRmsFloor)
{
	if (rms < rms_floor || energy < 1.0e-5f) {
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

bool primary_chord_is_plain_major_minor(const ChordResult &chord)
{
	if (!valid_chord_result(chord))
		return false;
	const char *label_end = std::strchr(chord.label, '=');
	const std::size_t label_len =
		label_end ? static_cast<std::size_t>(label_end - chord.label) : std::strlen(chord.label);
	ParsedRootChord parsed;
	return parse_root_chord_component(chord.label, label_len, parsed) && parsed.root == chord.root &&
	       (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor);
}

bool primary_chord_is_power(const ChordResult &chord)
{
	if (!valid_chord_result(chord))
		return false;
	const char *label_end = std::strchr(chord.label, '=');
	const std::size_t label_len =
		label_end ? static_cast<std::size_t>(label_end - chord.label) : std::strlen(chord.label);
	ParsedRootChord parsed;
	return parse_power_chord_component(chord.label, label_len, parsed) && parsed.root == chord.root;
}

int primary_major_minor_chord_tone_count(const NoteGrid &grid, const ChordResult &chord)
{
	if (!valid_chord_result(chord))
		return 0;

	const char *label_end = std::strchr(chord.label, '=');
	const std::size_t label_len =
		label_end ? static_cast<std::size_t>(label_end - chord.label) : std::strlen(chord.label);
	ParsedRootChord parsed;
	if (!parse_root_chord_component(chord.label, label_len, parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return 0;

	ChordResult primary = {};
	primary.root = parsed.root;
	primary.confidence = chord.confidence;
	primary.tones[parsed.root] = true;
	primary.tones[(parsed.root + (parsed.quality == RootChordQuality::Minor ? 3 : 4)) % 12] = true;
	primary.tones[(parsed.root + 7) % 12] = true;
	return note_grid_chord_tone_count(grid, primary);
}

bool primary_major_minor_third_supported(const NoteGrid &grid, const ChordResult &chord)
{
	if (!valid_chord_result(chord))
		return false;

	const char *label_end = std::strchr(chord.label, '=');
	const std::size_t label_len =
		label_end ? static_cast<std::size_t>(label_end - chord.label) : std::strlen(chord.label);
	ParsedRootChord parsed;
	if (!parse_root_chord_component(chord.label, label_len, parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return false;

	const int third = parsed.root + (parsed.quality == RootChordQuality::Minor ? 3 : 4);
	return note_grid_pitch_supported_level(grid, third, 0.12f) >= 0.12f;
}

bool primary_major_minor_root_adjacent_noise(const NoteGrid &grid, const ChordResult &chord)
{
	if (!valid_chord_result(chord))
		return false;

	const char *label_end = std::strchr(chord.label, '=');
	const std::size_t label_len =
		label_end ? static_cast<std::size_t>(label_end - chord.label) : std::strlen(chord.label);
	ParsedRootChord parsed;
	if (!parse_root_chord_component(chord.label, label_len, parsed) ||
	    (parsed.quality != RootChordQuality::Major && parsed.quality != RootChordQuality::Minor))
		return false;

	return note_grid_pitch_active(grid, parsed.root) && note_grid_pitch_active(grid, parsed.root - 1) &&
	       note_grid_pitch_active(grid, parsed.root + 1);
}

bool guitar_analysis_triad_should_replace(const ChordResult &current, const ChordResult &supported,
					  const NoteGrid &display_grid, const NoteGrid &analysis_grid)
{
	if (!valid_chord_result(supported))
		return false;
	if (!valid_chord_result(current))
		return true;
	if (current.root == supported.root)
		return false;

	const int supported_display_tones = note_grid_chord_tone_count(display_grid, supported);
	const int supported_analysis_tones = note_grid_chord_tone_count(analysis_grid, supported);
	if (supported_display_tones < 2 || supported_analysis_tones < 3)
		return false;

	if (std::strstr(current.label, "pow") != nullptr)
		return true;

	const int current_display_tones = note_grid_chord_tone_count(display_grid, current);
	const int current_analysis_tones = note_grid_chord_tone_count(analysis_grid, current);
	const bool current_plain = primary_chord_is_plain_major_minor(current);
	const bool current_extended = chord_label_has_guitar_extension_or_alteration(current.label);
	const bool current_has_supported_plain_quality =
		chord_label_has_root_third_component(current.label, supported.root);
	const int current_components = chord_label_component_count(current.label);

	if (current_extended && current_components <= 3 && current_analysis_tones >= supported_analysis_tones)
		return false;
	if (current_components >= 6 && !current_has_supported_plain_quality && supported.confidence >= 0.58f)
		return true;
	if (current_extended && supported.confidence + 0.08f >= current.confidence)
		return true;
	if (!current_plain && supported_display_tones >= current_display_tones &&
	    supported_analysis_tones >= current_analysis_tones && supported.confidence + 0.08f >= current.confidence)
		return true;
	if (!chord_label_has_root_component(current.label, supported.root) && supported_analysis_tones >= 3 &&
	    supported_display_tones >= 2 && (current_extended || !current_plain) &&
	    supported.confidence + 0.18f >= current.confidence)
		return true;
	if (current_display_tones < 2 && supported.confidence >= current.confidence * 0.92f)
		return true;

	return false;
}

void prepend_analysis_complete_smoothed_guitar_plain_alias(ChordResult &target,
							   const ChordResult &smoothed,
							   const NoteGrid &display_grid,
							   const NoteGrid &analysis_grid)
{
	if (!valid_chord_result(target) || !valid_chord_result(smoothed))
		return;

	const int display_pitch_classes = note_grid_active_pitch_class_count(display_grid);
	const int analysis_pitch_classes = note_grid_active_pitch_class_count(analysis_grid);
	if (display_pitch_classes < 2 || display_pitch_classes > 7 ||
	    analysis_pitch_classes < 3 || analysis_pitch_classes > 10)
		return;

	float strongest_analysis = 0.0f;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class)
		strongest_analysis = std::max(strongest_analysis,
					      note_grid_pitch_level(analysis_grid, pitch_class));
	if (strongest_analysis <= 1.0e-6f)
		return;

	int target_display_tones = note_grid_chord_tone_count(display_grid, target);
	int target_analysis_tones = note_grid_chord_tone_count(analysis_grid, target);
	const char *target_primary_end = std::strchr(target.label, '=');
	const std::size_t target_primary_len =
		target_primary_end ? static_cast<std::size_t>(target_primary_end - target.label) :
				     std::strlen(target.label);
	ParsedRootChord target_primary;
	if (parse_root_chord_component(target.label, target_primary_len, target_primary) &&
	    (target_primary.quality == RootChordQuality::Major ||
	     target_primary.quality == RootChordQuality::Minor)) {
		const bool target_minor = target_primary.quality == RootChordQuality::Minor;
		ChordResult target_primary_chord =
			make_guitar_plain_triad(target_primary.root, target_minor, target.confidence);
		target_display_tones = note_grid_chord_tone_count(display_grid, target_primary_chord);
		target_analysis_tones = note_grid_chord_tone_count(analysis_grid, target_primary_chord);
	}
	if (target_display_tones >= 3 && target_analysis_tones >= 3)
		return;

	ChordResult best;
	bool best_minor = false;
	float best_score = 0.0f;
	const char *cursor = smoothed.label;
	while (*cursor) {
		const char *end = std::strchr(cursor, '=');
		const std::size_t len = end ? static_cast<std::size_t>(end - cursor) : std::strlen(cursor);

		ParsedRootChord parsed;
		if (parse_root_chord_component(cursor, len, parsed) &&
		    (parsed.quality == RootChordQuality::Major || parsed.quality == RootChordQuality::Minor)) {
			const char *suffix = parsed.quality == RootChordQuality::Minor ? "m" : "";
			char alias[16] = {};
			std::snprintf(alias, sizeof(alias), "%s%s", note_name(parsed.root), suffix);
			if (!chord_label_has_exact_component(target.label, alias)) {
				const bool minor = parsed.quality == RootChordQuality::Minor;
				ChordResult candidate = make_guitar_plain_triad(parsed.root, minor,
										 std::max(smoothed.confidence, 0.58f));
				const int display_tones = note_grid_chord_tone_count(display_grid, candidate);
				const int analysis_tones = note_grid_chord_tone_count(analysis_grid, candidate);
				const int third = parsed.root + (minor ? 3 : 4);
				const int fifth = parsed.root + 7;
				const float root_level = note_grid_pitch_level(analysis_grid, parsed.root);
				const float third_level = note_grid_pitch_level(analysis_grid, third);
				const float fifth_level = note_grid_pitch_level(analysis_grid, fifth);
				const float anchor = std::min(root_level, fifth_level);
				const float opposite_third =
					note_grid_pitch_level(analysis_grid, parsed.root + (minor ? 4 : 3));
				const bool display_root = note_grid_pitch_active(display_grid, parsed.root);
				const bool display_third = note_grid_pitch_active(display_grid, third);
				const bool display_fifth = note_grid_pitch_active(display_grid, fifth);

				if (display_tones >= 2 && analysis_tones >= 3 &&
				    target_analysis_tones < analysis_tones &&
				    (display_root || (display_third && display_fifth)) &&
				    root_level >= std::max(0.035f, strongest_analysis * 0.035f) &&
				    fifth_level >= std::max(0.055f, strongest_analysis * 0.050f) &&
				    third_level >= std::max(0.024f, anchor * 0.045f) &&
				    !(opposite_third >= std::max(0.12f, anchor * 0.22f) &&
				      opposite_third >= third_level * 1.30f)) {
					const float score = static_cast<float>(analysis_tones) * 1.00f +
							    static_cast<float>(display_tones) * 0.45f +
							    std::min({root_level, third_level, fifth_level});
					if (score > best_score) {
						best_score = score;
						best = candidate;
						best_minor = minor;
					}
				}
			}
		}

		if (!end)
			break;
		cursor = end + 1;
	}

	if (!valid_chord_result(best))
		return;

	prepend_chord_alias(target, best.root, best_minor ? "m" : "");
	target.root = best.root;
	target.tones = best.tones;
	target.confidence = std::max(target.confidence, best.confidence);
	target.margin = std::max(target.margin, best.margin);
	target.uncertain = false;
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
	const bool raw_valid = valid_chord_result(raw);
	const bool smoothed_valid = valid_chord_result(smoothed);
	if (raw_valid && smoothed_valid) {
		const int raw_components = chord_label_component_count(raw.label);
		const int smoothed_components = chord_label_component_count(smoothed.label);
		if (smoothed_components > raw_components &&
		    chord_label_contains_all_components(smoothed.label, raw.label) &&
		    smoothed.confidence >= raw.confidence * 0.72f)
			return smoothed;
		if (raw_components > smoothed_components &&
		    chord_label_contains_all_components(raw.label, smoothed.label) &&
		    raw.confidence >= smoothed.confidence * 0.72f)
			return raw;
	}
	if (raw_valid && (!smoothed_valid || raw.confidence >= smoothed.confidence * 0.96f))
		return raw;
	if (smoothed_valid)
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
		const bool displayed_has_extension =
			chord_label_has_guitar_extension_or_alteration(tracking.displayed_label);
		const bool candidate_has_extension = chord_label_has_guitar_extension_or_alteration(candidate.label);
		if (chord_label_contains_all_components(candidate.label, tracking.displayed_label) &&
		    (displayed_has_extension || !candidate_has_extension)) {
			copy_text(tracking.displayed_label, sizeof(tracking.displayed_label), candidate.label);
			tracking.displayed_confidence = std::max(tracking.displayed_confidence, candidate.confidence);
			tracking.pending_label[0] = '\0';
			tracking.pending_confidence = 0.0f;
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
	rebuild_window(resolve_analysis_window_samples(AnalysisSettings{}));
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

std::size_t resolve_analysis_window_samples(const AnalysisSettings &settings)
{
	const uint32_t sample_rate = settings.sample_rate ? settings.sample_rate : 48000;
	std::size_t requested = 0;
	if (settings.analysis_window_samples > 0) {
		requested = settings.analysis_window_samples;
	} else {
		const float seconds =
			settings.analysis_window_seconds > 0.0f ?
				settings.analysis_window_seconds :
				static_cast<float>(kDefaultAnalysisWindowMs) / 1000.0f;
		requested = static_cast<std::size_t>(
			std::lround(static_cast<double>(sample_rate) * static_cast<double>(seconds)));
	}

	return std::clamp<std::size_t>(requested, 1, kAnalysisWindow);
}

void AnalysisEngine::rebuild_window(std::size_t window_samples)
{
	window_samples = std::clamp<std::size_t>(window_samples, 1, kAnalysisWindow);
	if (window_samples == analysis_window_samples_)
		return;

	analysis_window_samples_ = window_samples;
	window_.fill(0.0f);
	if (window_samples == 1) {
		window_[0] = 1.0f;
		return;
	}

	for (std::size_t i = 0; i < window_samples; ++i) {
		const float phase = 2.0f * kPi * static_cast<float>(i) / static_cast<float>(window_samples - 1);
		window_[i] = 0.5f - 0.5f * std::cos(phase);
	}
}

void AnalysisEngine::reset_note_envelopes()
{
	tracked_bass_midi_ = -1;
	pending_bass_midi_ = -1;
	pending_bass_hits_ = 0;
	tracked_bass_misses_ = 0;
	tracked_bass_confidence_ = 0.0f;
	tracked_bass_score_ = 0.0f;
	tracked_vocal_midi_ = -1;
	pending_vocal_midi_ = -1;
	pending_vocal_hits_ = 0;
	tracked_vocal_misses_ = 0;
	tracked_vocal_score_ = 0.0f;
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
	for (NoteTrackingState &note : full_mix_other_ownership_tracking_)
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

AnalysisEngine::TuningProbeResult
AnalysisEngine::chromatic_tuning_probe(const float *samples, std::size_t count, float mean, int midi,
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
	TuningProbeResult result;
	result.best_level = best_score;
	result.center_level = center_score;
	result.cents = cents;
	if (std::abs(cents) <= tolerance_cents + kChromaticTuneEstimatorSlackCents) {
		result.matched = true;
		return result;
	}
	if (!allow_ratio_rescue)
		return result;
	if (std::abs(cents) <= kProbeCents.back() && best_score > 1.0e-6f &&
	    center_score >= best_score * kChromaticCenterAdjacentRatio) {
		result.matched = true;
		return result;
	}

	const bool edge_peak = best == 0 || best + 1 == kProbeCents.size();
	result.matched = edge_peak && best_score > 1.0e-6f && center_score >= best_score * kChromaticCenterEdgeRatio;
	return result;
}

bool AnalysisEngine::chromatic_tuning_match(const float *samples, std::size_t count, float mean, int midi,
					    float tolerance_cents, bool allow_ratio_rescue) const
{
	return chromatic_tuning_probe(samples, count, mean, midi, tolerance_cents, allow_ratio_rescue).matched;
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
	const std::size_t requested_window_samples = resolve_analysis_window_samples(settings);
	if (requested_window_samples != analysis_window_samples_) {
		rebuild_window(requested_window_samples);
		reset_analysis_state();
	}

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
	copy_text(snapshot.drums[Rim].label, sizeof(snapshot.drums[Rim].label), "RIM");
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

	const std::size_t usable = std::min(count, analysis_window_samples_);
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
	snapshot.drum_debug_transient_ratio = drum_transient_ratio;
	snapshot.rms = rms;
	snapshot.peak = peak;
	const bool mixed_source = input_mode == AnalysisInputMode::FullMix;
	const AnalysisInputMode full_mix_source_hint_mode =
		mixed_source ? single_family_hint_from_source(resolved_source_name) : AnalysisInputMode::FullMix;
	const bool mixed_string_source_hint =
		mixed_source &&
		(contains_case_insensitive(resolved_source_name, "string") ||
		 contains_case_insensitive(resolved_source_name, "violin") ||
		 contains_case_insensitive(resolved_source_name, "viola") ||
		 contains_case_insensitive(resolved_source_name, "cello") ||
		 contains_case_insensitive(resolved_source_name, "contrabass"));
	const bool mixed_synth_source_hint =
		mixed_source && contains_case_insensitive(resolved_source_name, "synth");

	std::array<float, kNoteProbeCount> note_powers = {};
	for (std::size_t i = 0; i < note_probes_.size(); ++i)
		note_powers[i] = goertzel_power(samples, usable, mean, note_probes_[i]);

	std::array<float, kNoteProbeCount> tuned_note_powers = note_powers;
	std::array<float, kNoteProbeCount> detection_note_powers = note_powers;
	std::array<bool, kNoteProbeCount> strict_tuning_matches = {};
	int strict_tuned_note_count = 0;
	float strongest_note_level = 0.0f;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi)
		strongest_note_level = std::max(strongest_note_level, probe_level(note_powers, midi));
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		if (midi < kChromaticTuneMinMidi)
			continue;
		TuningProbeResult tuning =
			chromatic_tuning_probe(samples, usable, mean, midi, kChromaticTuneToleranceCents, false);
		bool strict_match = tuning.matched;
		if (!strict_match && mixed_source && midi >= kStrictTunedPowerPromotionMinMidi) {
			const TuningProbeResult high_tuning =
				chromatic_tuning_probe(samples, usable, mean, midi,
						       kHighMixedStrictTuneToleranceCents, false);
			if (high_tuning.matched &&
			    high_tuning.best_level >= strongest_note_level * kStrictTunedPowerPromotionFloor) {
				tuning = high_tuning;
				strict_match = true;
			}
		}
		strict_tuning_matches[midi - kFirstMidi] = strict_match;
		if (!strict_match)
			continue;
		const float raw_note_level = probe_level(note_powers, midi);
		if (mixed_source && midi >= kStrictTunedPowerPromotionMinMidi &&
		    tuning.best_level >= strongest_note_level * kStrictTunedPowerPromotionFloor &&
		    tuning.best_level > raw_note_level) {
			const float promoted_level =
				std::max(raw_note_level,
					 std::min(tuning.best_level,
						  strongest_note_level * kStrictTunedPowerPromotionCap));
			const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
			detection_note_powers[index] = std::max(detection_note_powers[index],
								promoted_level * promoted_level);
		}
		if (raw_note_level >= strongest_note_level * 0.14f)
			++strict_tuned_note_count;
	}
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		if (midi < kChromaticTuneMinMidi)
			continue;
		const bool complex_harmonic_support = has_complex_harmonic_support(note_powers, midi);
		if (strict_tuning_matches[midi - kFirstMidi])
			continue;
		if (tracked_note_active(input_mode, midi) &&
		    chromatic_tuning_match(samples, usable, mean, midi, kChromaticActiveTuneToleranceCents, true))
			continue;
		tuned_note_powers[midi - kFirstMidi] = 0.0f;
		const float raw_note_level = probe_level(note_powers, midi);
		const float adjacent_note_level =
			std::max(probe_level(note_powers, midi - 1), probe_level(note_powers, midi + 1));
		const bool isolated_fallback_local_peak =
			adjacent_note_level <= 1.0e-6f || raw_note_level >= adjacent_note_level * 0.72f;
		const bool mixed_dominant_detuned_fallback_note =
			mixed_source && midi >= kMixedDominantDetunedFallbackMinMidi &&
			raw_note_level >= strongest_note_level * 0.80f &&
			(adjacent_note_level <= 1.0e-6f || raw_note_level >= adjacent_note_level * 8.0f);
		const bool mixed_string_source_detuned_fallback_note =
			mixed_string_source_hint &&
			midi >= kGuitarMinMidi &&
			midi <= kDefaultBassMaxMidi &&
			raw_note_level >= strongest_note_level * 0.55f &&
			isolated_fallback_local_peak &&
			chromatic_tuning_match(samples, usable, mean, midi, kChromaticActiveTuneToleranceCents, true);
		const bool mixed_synth_source_detuned_fallback_note =
			mixed_synth_source_hint &&
			midi >= kGuitarMinMidi &&
			midi <= 60 &&
			raw_note_level >= strongest_note_level * 0.45f &&
			isolated_fallback_local_peak &&
			chromatic_tuning_match(samples, usable, mean, midi, kChromaticActiveTuneToleranceCents, true);
		const bool strong_isolated_polyphonic_fallback_note =
			raw_note_level >= strongest_note_level * 0.30f && isolated_fallback_local_peak;
		const bool isolated_polyphonic_context = !mixed_source && strict_tuned_note_count >= 2;
		const bool isolated_guitar_single_note_context =
			input_mode == AnalysisInputMode::IsolatedGuitar && !isolated_polyphonic_context;
		const bool isolated_real_piano_source =
			input_mode == AnalysisInputMode::IsolatedKeyboard &&
			contains_case_insensitive(resolved_source_name, "piano");
		const bool isolated_named_real_single_note_context =
			!mixed_source && !isolated_polyphonic_context &&
			(input_mode == AnalysisInputMode::IsolatedGuitar ||
			 isolated_real_piano_source ||
			 input_mode == AnalysisInputMode::IsolatedVocal ||
			 input_mode == AnalysisInputMode::IsolatedOther);
		const bool strong_isolated_complex_fallback_note =
			(raw_note_level >= strongest_note_level * 0.30f && isolated_fallback_local_peak) ||
			(isolated_guitar_single_note_context && raw_note_level >= strongest_note_level * 0.18f);
		const bool strong_isolated_named_real_fallback_note =
			isolated_named_real_single_note_context && raw_note_level >= strongest_note_level * 0.06f;
		const float fallback_scale =
			complex_harmonic_support ?
				(mixed_source ?
					       (mixed_string_source_detuned_fallback_note ?
							kMixedStringSourceDetunedFallbackScale :
						mixed_synth_source_detuned_fallback_note ?
							kMixedSynthSourceDetunedFallbackScale :
							kComplexTuningFallbackScale) :
					       (strong_isolated_complex_fallback_note ?
							kIsolatedComplexTuningFallbackScale :
							0.0f)) :
				(mixed_source ?
					       (mixed_string_source_detuned_fallback_note ?
							kMixedStringSourceDetunedFallbackScale :
						mixed_synth_source_detuned_fallback_note ?
							kMixedSynthSourceDetunedFallbackScale :
					       (mixed_dominant_detuned_fallback_note ?
							kMixedDominantDetunedFallbackScale :
							0.0f)) :
					       (isolated_polyphonic_context && strong_isolated_polyphonic_fallback_note ?
							kIsolatedPolyphonicTuningFallbackScale :
						 strong_isolated_named_real_fallback_note ?
							kIsolatedNamedInstrumentTuningFallbackScale :
							kIsolatedDetunedFallbackScale));
		detection_note_powers[midi - kFirstMidi] = note_powers[midi - kFirstMidi] * fallback_scale;
	}

	std::array<float, kNoteProbeCount> keyboard_detection_note_powers = detection_note_powers;
	if (input_mode == AnalysisInputMode::IsolatedKeyboard &&
	    usable >= static_cast<std::size_t>(static_cast<float>(sample_rate_) * 0.095f)) {
		const bool isolated_real_piano_source = contains_case_insensitive(resolved_source_name, "piano");
		std::array<float, kNoteProbeCount> low_piano_fundamental_scores = {};
		float strongest_low_piano_fundamental_score = 0.0f;
		if (isolated_real_piano_source) {
			for (int midi = kKeyboardMinMidi; midi < kChromaticTuneMinMidi; ++midi) {
				const float raw_note_level = probe_level(note_powers, midi);
				const float adjacent_note_level = std::max(probe_level(note_powers, midi - 1),
									  probe_level(note_powers, midi + 1));
				const bool local_peak =
					adjacent_note_level <= 1.0e-6f ||
					raw_note_level >= adjacent_note_level * 0.72f;
				const float partial_12 = probe_level(note_powers, midi + 12);
				const float partial_19 = probe_level(note_powers, midi + 19);
				const float partial_24 = probe_level(note_powers, midi + 24);
				const float partial_28 = probe_level(note_powers, midi + 28);
				const float partial_31 = probe_level(note_powers, midi + 31);
				float harmonic_supported_level = raw_note_level;
				harmonic_supported_level += partial_12 * 0.72f;
				harmonic_supported_level += partial_19 * 0.62f;
				harmonic_supported_level += partial_24 * 0.48f;
				harmonic_supported_level += partial_28 * 0.34f;
				harmonic_supported_level += partial_31 * 0.26f;
				int partial_count = 0;
				for (float partial : {partial_12, partial_19, partial_24, partial_28, partial_31}) {
					if (partial >= strongest_note_level * 0.025f)
						++partial_count;
				}
				const bool harmonic_supported_peak =
					harmonic_supported_level >= strongest_note_level * 0.18f;
				if (partial_count < 2 || (!local_peak && !harmonic_supported_peak))
					continue;
				const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
				low_piano_fundamental_scores[index] = harmonic_supported_level;
				strongest_low_piano_fundamental_score =
					std::max(strongest_low_piano_fundamental_score, harmonic_supported_level);
			}
		}
		for (int midi = kKeyboardMinMidi; midi < kChromaticTuneMinMidi; ++midi) {
			const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
			const float raw_note_level = probe_level(note_powers, midi);
			const float adjacent_note_level =
				std::max(probe_level(note_powers, midi - 1), probe_level(note_powers, midi + 1));
			const bool local_peak =
				adjacent_note_level <= 1.0e-6f || raw_note_level >= adjacent_note_level * 0.72f;
			const float harmonic_supported_level = low_piano_fundamental_scores[index];
			const bool real_piano_low_fundamental =
				isolated_real_piano_source &&
				strongest_low_piano_fundamental_score > 1.0e-6f &&
				harmonic_supported_level >= strongest_low_piano_fundamental_score * 0.55f &&
				(local_peak || harmonic_supported_level >= strongest_note_level * 0.18f);
			if (real_piano_low_fundamental) {
				const float boosted_level =
					std::max(raw_note_level,
						 std::min(strongest_note_level * 0.82f,
							  harmonic_supported_level * 0.55f));
				keyboard_detection_note_powers[index] =
					std::max(keyboard_detection_note_powers[index],
						 boosted_level * boosted_level);
				continue;
			}
			if (chromatic_tuning_match(samples, usable, mean, midi, kChromaticTuneToleranceCents, false))
				continue;
			keyboard_detection_note_powers[index] = 0.0f;
		}
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
	const float high_drum_energy = drum_powers[11] + drum_powers[12] + drum_powers[13] + drum_powers[14];
	const float high = sum_notes(detection_note_powers, 73, kLastMidi) + high_drum_energy;
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
	snapshot.drum_debug_onset = onset;
	previous_rms_ = previous_rms_ * 0.78f + rms * 0.22f;
	const bool generated_gm_drum_source = contains_case_insensitive(resolved_source_name, "GM drum kit");

	const std::array<float, kDrumCount> drum_bands = {
		drum_powers[0] + drum_powers[1] + drum_powers[2] * 0.75f,
		drum_powers[4] + drum_powers[5] + drum_powers[8] * 0.65f + drum_powers[9] * 0.55f,
		drum_powers[11] + drum_powers[12] + drum_powers[13],
		drum_powers[12] + drum_powers[13] + drum_powers[14],
		drum_powers[1] * 0.25f + drum_powers[2] + drum_powers[3] + drum_powers[4] +
			drum_powers[5] * 0.80f + drum_powers[6] * 0.25f,
		drum_powers[10] + drum_powers[11] + drum_powers[12] * 0.75f,
		drum_powers[7] * 0.60f + drum_powers[8] + drum_powers[9] * 0.80f + drum_powers[10] * 0.35f,
	};
	const std::array<float, kDrumCount> drum_segment_bands = {
		drum_segment_peaks[0] + drum_segment_peaks[1] + drum_segment_peaks[2] * 0.75f,
		drum_segment_peaks[4] + drum_segment_peaks[5] + drum_segment_peaks[6] * 0.30f +
			drum_segment_peaks[8] * 0.72f + drum_segment_peaks[9] * 0.62f,
		drum_segment_peaks[11] + drum_segment_peaks[12] + drum_segment_peaks[13],
		drum_segment_peaks[12] + drum_segment_peaks[13] + drum_segment_peaks[14],
		drum_segment_peaks[1] * 0.25f + drum_segment_peaks[2] + drum_segment_peaks[3] +
			drum_segment_peaks[4] + drum_segment_peaks[5] * 0.80f + drum_segment_peaks[6] * 0.65f,
		drum_segment_peaks[10] + drum_segment_peaks[11] + drum_segment_peaks[12] * 0.75f,
		drum_segment_peaks[7] * 0.60f + drum_segment_peaks[8] + drum_segment_peaks[9] * 0.80f +
			drum_segment_peaks[10] * 0.35f,
	};
	const float strongest_shell_drum =
		std::max(drum_segment_bands[Kick], std::max(drum_segment_bands[Snare], drum_segment_bands[Tom]));
	const float strongest_body_drum = std::max(strongest_shell_drum, drum_segment_bands[Rim]);
	const float kick_body = drum_segment_peaks[0] + drum_segment_peaks[1] + drum_segment_peaks[2] * 0.45f;
	const float snare_body =
		drum_segment_peaks[4] + drum_segment_peaks[5] + drum_segment_peaks[6] * 0.20f +
		drum_segment_peaks[8] * 0.50f + drum_segment_peaks[9] * 0.30f;
	const float snare_crack = drum_segment_peaks[8] + drum_segment_peaks[9];
	const float rim_body = drum_segment_peaks[7] * 0.70f + drum_segment_peaks[8] + drum_segment_peaks[9] * 0.70f;
	const float rim_low_mid_body =
		drum_segment_peaks[6] * 0.22f + drum_segment_peaks[7] +
		drum_segment_peaks[8] * 0.72f + drum_segment_peaks[9] * 0.32f;
	const float tom_body = drum_segment_peaks[1] * 0.22f + drum_segment_peaks[2] + drum_segment_peaks[3] +
			       drum_segment_peaks[4] + drum_segment_peaks[5] * 0.55f +
			       drum_segment_peaks[6] * 0.55f;
	const float kick_competing_body = std::max(snare_body, tom_body);
	const float upper_tom_body = drum_segment_peaks[5] * 0.85f + drum_segment_peaks[6];
	const bool kick_energy_shape = kick_body > 1.0e-6f && snapshot.low_energy >= 0.15f;
	const bool kick_soft_low_shape = drum_transient && snapshot.low_energy >= 0.08f &&
					 drum_segment_bands[Kick] >= strongest_shell_drum * 0.10f &&
					 kick_body >= std::max(snare_body, tom_body) * 0.055f;
	const bool kick_soft_stream_shape = had_previous_audio && snapshot.low_energy >= 0.04f &&
					    drum_segment_bands[Kick] >= strongest_shell_drum * 0.08f &&
					    kick_body >= std::max(snare_body, tom_body) * 0.040f;
	const bool kick_shape = strongest_shell_drum <= 0.0f || kick_energy_shape ||
				kick_soft_low_shape || kick_soft_stream_shape ||
				(drum_segment_bands[Kick] >= strongest_shell_drum * 0.18f &&
				 kick_body >= std::max(snare_body, tom_body) * 0.10f);
	const bool snare_crack_shape =
		drum_segment_bands[Snare] >= strongest_shell_drum * 0.58f &&
		snare_body >= kick_body * 0.34f && snare_body >= tom_body * 0.38f &&
		snare_crack >= snare_body * 0.035f;
	const bool snare_resonant_body_shape =
		drum_segment_bands[Snare] >= strongest_shell_drum * 0.52f &&
		snare_body >= kick_body * 0.30f && snare_body >= tom_body * 0.32f &&
		snare_crack >= snare_body * 0.010f &&
		snapshot.mid_energy >= snapshot.low_energy * 0.42f;
	const bool low_cymbal_snare_body_shape =
		drum_segment_bands[Snare] >= strongest_shell_drum * 0.44f &&
		snare_body >= kick_body * 0.24f && snare_body >= tom_body * 0.24f &&
		snare_crack >= snare_body * 0.006f &&
		snapshot.mid_energy >= 0.52f && snapshot.high_energy <= 0.14f;
	const bool snare_shape = strongest_shell_drum <= 0.0f || snare_crack_shape ||
				 snare_resonant_body_shape || low_cymbal_snare_body_shape;
	const bool rim_shape = strongest_body_drum <= 0.0f ||
			       (drum_segment_bands[Rim] >= strongest_body_drum * 0.30f &&
				rim_body >= kick_body * 0.20f && rim_body >= tom_body * 0.20f &&
				rim_body >= snare_body * 0.20f);
	const bool tom_shape = strongest_shell_drum <= 0.0f ||
			       (drum_segment_bands[Tom] >= strongest_shell_drum * 0.22f &&
				tom_body >= kick_body * 0.14f && tom_body >= snare_body * 0.12f);
	const float cymbal_low = drum_segment_peaks[10] + drum_segment_peaks[11];
	const float cymbal_mid = drum_segment_peaks[11] + drum_segment_peaks[12];
	const float cymbal_high = drum_segment_peaks[13] + drum_segment_peaks[14];
	const std::array<float, 3> body_shape_scores = {
		kick_body * (1.0f + snapshot.low_energy * 0.90f) * 1.35f,
		std::max(snare_body, rim_body * 0.88f) * (1.0f + snapshot.mid_energy * 0.62f),
		tom_body * (1.0f + snapshot.mid_energy * 0.24f),
	};
	std::size_t body_shape = Kick;
	if (body_shape_scores[1] > body_shape_scores[0] && body_shape_scores[1] >= body_shape_scores[2])
		body_shape = Snare;
	else if (body_shape_scores[2] > body_shape_scores[0] && body_shape_scores[2] > body_shape_scores[1])
		body_shape = Tom;
	snapshot.drum_debug_kick_body = kick_body;
	snapshot.drum_debug_snare_body = snare_body;
	snapshot.drum_debug_snare_crack = snare_crack;
	snapshot.drum_debug_tom_body = tom_body;
	snapshot.drum_debug_upper_tom_body = upper_tom_body;
	snapshot.drum_debug_body_shape = static_cast<int>(body_shape);
	const float strongest_cymbal_drum =
		std::max(drum_segment_bands[HiHat], std::max(drum_segment_bands[Crash], drum_segment_bands[Ride]));
	std::size_t cymbal_shape = HiHat;
	if (drum_segment_peaks[14] > (drum_segment_peaks[12] + drum_segment_peaks[13]) * 0.65f)
		cymbal_shape = Crash;
	else if (cymbal_low > cymbal_mid * 1.15f && cymbal_low > cymbal_high * 1.15f)
		cymbal_shape = Ride;
	const bool hihat_family_shape =
		strongest_cymbal_drum > 0.0f && drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.58f;
	const bool crash_family_shape =
		strongest_cymbal_drum > 0.0f && drum_segment_bands[Crash] >= strongest_cymbal_drum * 0.22f;
	const bool ride_family_shape =
		strongest_cymbal_drum > 0.0f && drum_segment_bands[Ride] >= strongest_cymbal_drum * 0.42f &&
		cymbal_low >= cymbal_high * 0.10f;
	const bool cymbal_body_separable =
		generated_gm_drum_source || strongest_body_drum <= 0.0f ||
		strongest_cymbal_drum >= strongest_body_drum * 0.24f ||
		snapshot.high_energy >= 0.42f;
	const bool cymbal_shape_allowed =
		strongest_cymbal_drum > 0.0f && cymbal_body_separable &&
		(snapshot.high_energy >= 0.20f ||
		 strongest_cymbal_drum >= strongest_body_drum * (generated_gm_drum_source ? 0.10f : 0.24f));
	const bool body_shape_allowed =
		strongest_body_drum > 0.0f &&
		(!cymbal_shape_allowed ||
		 snapshot.high_energy < (generated_gm_drum_source ? 0.62f : 0.52f) ||
		 strongest_body_drum >= strongest_cymbal_drum * (generated_gm_drum_source ? 0.45f : 0.56f));
	const bool snare_side_shape =
		body_shape_allowed && snare_shape &&
		drum_segment_bands[Snare] >=
			std::max(std::max(drum_segment_bands[Kick], drum_segment_bands[Rim]), drum_segment_bands[Tom]) *
				0.45f &&
		snare_crack >= snare_body * 0.035f;
	const bool rim_side_shape =
		body_shape_allowed && rim_shape &&
		drum_segment_bands[Rim] >= std::max(drum_segment_bands[Kick], drum_segment_bands[Tom]) * 0.30f &&
		drum_segment_bands[Rim] >= strongest_body_drum * 0.20f &&
		rim_body >= snare_body * 0.30f;
	const float rim_competing_shell_body = std::max(snare_body, tom_body);
	const bool rim_embedded_side_stick_shape =
		body_shape_allowed && rim_competing_shell_body > 0.0f &&
		drum_segment_bands[Rim] >= strongest_body_drum * 0.10f &&
		rim_low_mid_body >= rim_competing_shell_body * 0.24f &&
		rim_low_mid_body >= kick_body * 0.18f &&
		rim_body >= snare_body * 0.20f && rim_body >= tom_body * 0.16f &&
		kick_body < rim_competing_shell_body * 1.05f &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.045f);
	const bool kick_low_dominant_body =
		snapshot.low_energy >= 0.28f &&
		snapshot.low_energy >= snapshot.mid_energy * 1.25f &&
		kick_body >= kick_competing_body * 0.75f;
	const float kick_click_peak =
		drum_segment_peaks[7] + drum_segment_peaks[8] * 0.70f + drum_segment_peaks[9] * 0.45f;
	const bool kick_click_body_ratio = kick_click_peak >= kick_body * 0.035f;
	const bool kick_click_body_shape =
		kick_click_body_ratio && snapshot.low_energy >= 0.22f &&
		drum_segment_bands[Kick] >= strongest_shell_drum * 0.28f &&
		kick_body >= kick_competing_body * 0.50f;
	const float rim_shape_score = rim_body * (1.0f + snapshot.mid_energy * 0.56f);
	const float strongest_shell_shape_score = std::max(body_shape_scores[1], body_shape_scores[2]);
	const bool rim_cymbal_bounded =
		strongest_cymbal_drum <= strongest_body_drum * 1.08f ||
		drum_segment_bands[Rim] >= strongest_cymbal_drum * 0.70f;
	const bool rim_primary_evidence =
		rim_side_shape && rim_shape &&
		rim_shape_score >= strongest_shell_shape_score * 0.55f &&
		rim_cymbal_bounded &&
		rim_body >= kick_body * 0.22f;
	const float strongest_non_kick_body_score =
		std::max(body_shape_scores[1], std::max(body_shape_scores[2], rim_shape_score));
	const float strongest_non_kick_band =
		std::max(drum_bands[Snare], std::max(drum_bands[Tom], drum_bands[Rim]));
	const bool kick_low_onset_competing_body =
		strongest_non_kick_body_score > body_shape_scores[0] * 1.22f &&
		drum_bands[Kick] < strongest_non_kick_band * 0.45f;
	const bool kick_low_onset_body_shape =
		onset >= 1.35f &&
		drum_bands[Kick] >= drum_segment_bands[Kick] * 0.42f &&
		!kick_low_onset_competing_body &&
		(snapshot.low_energy >= 0.12f || drum_segment_bands[Kick] >= strongest_shell_drum * 0.32f) &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.22f) &&
		drum_segment_bands[Kick] >= strongest_shell_drum * 0.22f &&
		kick_body >= kick_competing_body * 0.14f;
	const bool kick_tonal_body_shape =
		kick_soft_low_shape &&
		snapshot.low_energy >= 0.50f &&
		snapshot.low_energy >= snapshot.mid_energy * 1.35f &&
		snapshot.high_energy <= 0.16f &&
		kick_body >= kick_competing_body * 0.34f &&
		drum_segment_bands[Kick] >= strongest_shell_drum * 0.20f &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.08f);
	const bool kick_body_shape_supported =
		body_shape == Kick ||
		(kick_energy_shape && kick_low_dominant_body) ||
		kick_click_body_shape ||
		kick_low_onset_body_shape ||
		kick_tonal_body_shape;
	const bool named_drum_source =
		generated_gm_drum_source || contains_case_insensitive(resolved_source_name, "drum");
	const bool one_shot_drum_source =
		generated_gm_drum_source || contains_case_insensitive(resolved_source_name, "drum sample");
	const bool real_drum_track_source = named_drum_source && !one_shot_drum_source;
	const float mixed_hihat_body_ratio =
		generated_gm_drum_source ? 0.04f :
		real_drum_track_source ? (snapshot.high_energy >= 0.10f ? 0.045f : 0.075f) :
		(snapshot.high_energy >= 0.12f ? 0.16f : 0.22f);
	const bool hihat_tom_body_backstop =
		body_shape_allowed && body_shape == Tom && snapshot.high_energy >= 0.03f &&
		strongest_cymbal_drum > 0.0f &&
		(generated_gm_drum_source || strongest_cymbal_drum >= strongest_body_drum * 0.24f) &&
		drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.42f;
	const bool hihat_mixed_backstop =
		drum_transient && snapshot.high_energy >= 0.05f &&
		strongest_cymbal_drum > 0.0f &&
		strongest_cymbal_drum >= strongest_body_drum * mixed_hihat_body_ratio &&
		drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.42f;
	const bool real_drum_track_embedded_hihat =
		real_drum_track_source &&
		drum_transient_ratio >= 1.25f &&
		snapshot.high_energy >= 0.08f &&
		strongest_cymbal_drum > 0.0f &&
		strongest_cymbal_drum >= strongest_body_drum * 0.035f &&
		drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.34f;
	const bool real_drum_track_low_embedded_hihat =
		real_drum_track_source &&
		drum_transient_ratio >= 1.25f &&
		snapshot.high_energy >= 0.020f &&
		strongest_cymbal_drum > 0.0f &&
		strongest_cymbal_drum >= strongest_body_drum * 0.010f &&
		drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.38f &&
		(cymbal_shape != Crash || drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.55f);
	const bool embedded_cymbal_transient =
		drum_transient && strongest_cymbal_drum >= 12.0f &&
		strongest_cymbal_drum >= strongest_body_drum * 0.035f &&
		drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.42f;
	const bool initial_real_drum_track_embedded_hihat =
		real_drum_track_low_embedded_hihat &&
		!had_previous_audio &&
		onset >= 2.0f &&
		snapshot.high_energy >= 0.020f;
	const bool embedded_snare_transient =
		drum_transient && onset >= 1.35f &&
		drum_segment_bands[Snare] >= strongest_shell_drum * 0.30f &&
		snare_body >= kick_body * 0.32f && snare_body >= tom_body * 0.30f &&
		snare_crack >= snare_body * 0.030f &&
		snapshot.mid_energy >= snapshot.low_energy * 0.62f &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.24f);
	const bool kick_backed_snare_transient =
		!one_shot_drum_source && drum_transient && onset >= 1.55f &&
		drum_segment_bands[Kick] >= strongest_shell_drum * 0.32f &&
		drum_segment_bands[Snare] >= strongest_shell_drum * 0.12f &&
		snare_body >= kick_body * 0.26f &&
		snare_body >= 18.0f &&
		snare_crack >= 6.0f &&
		snare_crack >= snare_body * 0.055f &&
		snare_crack >= kick_body * 0.018f &&
		snapshot.mid_energy >= snapshot.low_energy * 0.08f &&
		snapshot.high_energy <= 0.22f &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.16f);
	const bool tom_low_kick_bleed_shape =
		!one_shot_drum_source && body_shape == Kick &&
		snapshot.low_energy >= 0.68f &&
		snapshot.low_energy >= snapshot.mid_energy * 3.0f &&
		kick_body >= snare_body * 1.25f &&
		tom_body < kick_body * 1.82f &&
		upper_tom_body < kick_body * 0.42f;
	const bool tom_snare_bleed_shape =
		!one_shot_drum_source && body_shape == Tom && snare_shape &&
		snare_crack >= snare_body * 0.080f &&
		tom_body < snare_body * 1.45f &&
		upper_tom_body < snare_body * 0.85f;
	const bool tom_side_shape =
		body_shape_allowed && tom_shape && !tom_low_kick_bleed_shape && !tom_snare_bleed_shape &&
		drum_segment_bands[Tom] >= strongest_body_drum * 0.50f &&
		tom_body >= kick_body * 1.05f &&
		(tom_body >= snare_body * 1.50f ||
		 (upper_tom_body >= kick_body * 0.55f && upper_tom_body >= snare_crack * 1.20f)) &&
		kick_body < tom_body * 0.82f;
	const bool tom_primary_shape = body_shape == Tom && tom_body >= kick_body * 1.26f &&
				       tom_body >= snare_body * 1.45f;
	const std::array<bool, kDrumCount> drum_shape_supported = {
		body_shape_allowed && kick_body_shape_supported && kick_shape,
		body_shape_allowed &&
			(((body_shape == Snare || snare_side_shape) && snare_shape) ||
			 embedded_snare_transient || kick_backed_snare_transient),
		(cymbal_shape_allowed && (cymbal_shape == HiHat || hihat_family_shape)) ||
			hihat_tom_body_backstop || hihat_mixed_backstop || real_drum_track_embedded_hihat ||
			embedded_cymbal_transient,
		cymbal_shape_allowed && (cymbal_shape == Crash || crash_family_shape),
		body_shape_allowed && (tom_primary_shape || tom_side_shape) && tom_shape,
		cymbal_shape_allowed && (cymbal_shape == Ride || ride_family_shape),
		body_shape_allowed && (rim_side_shape || rim_embedded_side_stick_shape) &&
			(rim_shape || rim_embedded_side_stick_shape),
	};
	snapshot.drum_debug_bands = drum_bands;
	snapshot.drum_debug_segment_bands = drum_segment_bands;
	snapshot.drum_debug_shape_supported = drum_shape_supported;
	snapshot.drum_debug_shape_scores = {};
	snapshot.drum_debug_trigger_scores = {};
	snapshot.drum_debug_trigger_thresholds = {};
	snapshot.drum_debug_shape_scores[Kick] = body_shape_scores[0];
	snapshot.drum_debug_shape_scores[Snare] = body_shape_scores[1];
	snapshot.drum_debug_shape_scores[HiHat] = drum_segment_bands[HiHat];
	snapshot.drum_debug_shape_scores[Crash] = drum_segment_bands[Crash];
	snapshot.drum_debug_shape_scores[Tom] = body_shape_scores[2];
	snapshot.drum_debug_shape_scores[Ride] = drum_segment_bands[Ride];
	snapshot.drum_debug_shape_scores[Rim] = rim_shape_score;

	const float sensitivity = std::clamp(settings.sensitivity, 0.25f, 4.0f);
	const float trigger_threshold = 1.42f / sensitivity;
	const bool drum_detection_enabled = input_mode == AnalysisInputMode::FullMix;
	const RangeResult current_bass_drum_suppression_hint =
		dominant_bass_note(detection_note_powers, kBassMinMidi, kDefaultBassMaxMidi, true);
	const bool tonal_soft_drum_suppressed =
		!named_drum_source && !drum_transient && onset >= 1.60f &&
		(strict_tuned_note_count > 0 ||
		 current_bass_drum_suppression_hint.confidence >= 0.20f ||
		 tracked_bass_confidence_ >= 0.20f);
	bool tempo_event = false;
	for (std::size_t i = 0; i < kDrumCount; ++i) {
		if (drum_average_[i] <= 0.0f)
			drum_average_[i] = drum_bands[i];

		const float band_ratio = drum_bands[i] / (drum_average_[i] + 1.0e-6f);
		const float segment_ratio = drum_segment_bands[i] / (drum_average_[i] + 1.0e-6f);
		const bool cymbal = i == HiHat || i == Crash || i == Ride;
		const bool kick = i == Kick;
		const bool snare = i == Snare;
		const bool hihat = i == HiHat;
		const bool rim = i == Rim;
		const bool tom = i == Tom;
		const float kick_competing_band =
			std::max(drum_segment_bands[Snare], drum_segment_bands[Tom]);
		const bool kick_low_drum_energy = drum_segment_bands[Kick] >= strongest_shell_drum * 0.45f;
		const bool kick_low_body_transient =
			kick && drum_transient && (snapshot.low_energy >= 0.15f || kick_low_drum_energy) &&
			drum_segment_bands[Kick] >= kick_competing_band * 0.90f &&
			(kick_click_body_ratio || kick_low_dominant_body);
		const bool kick_click_shape =
			kick_click_peak >= drum_segment_bands[Kick] * 0.070f &&
			kick_click_body_ratio;
		const bool bass_sustain_kick_suppressed =
			kick && !named_drum_source && tracked_bass_midi_ >= 0 && tracked_bass_confidence_ >= 0.20f &&
			kick_click_peak < kick_body * 0.16f && !(drum_transient && kick_low_dominant_body) &&
			!kick_low_body_transient;
		const bool kick_soft_body_shape =
			kick && !bass_sustain_kick_suppressed && (kick_soft_low_shape || kick_soft_stream_shape) &&
			drum_segment_bands[Kick] >= kick_competing_band * 0.12f;
		const bool kick_click_transient =
			!kick || (!bass_sustain_kick_suppressed &&
				  (kick_click_shape || kick_low_body_transient || kick_soft_body_shape ||
				   kick_low_onset_body_shape));
		const bool segment_supported =
			band_ratio >= 1.03f ||
			(kick && kick_click_transient && (snapshot.low_energy >= 0.15f || kick_low_drum_energy));
		const float transient_ratio = segment_supported ? std::max(band_ratio, segment_ratio) : band_ratio;
		float score = transient_ratio * 0.72f + onset * 0.28f;
		if (i == Kick)
			score *= 1.0f + snapshot.low_energy * 0.8f;
		if (i == HiHat || i == Crash || i == Ride)
			score *= 1.0f + snapshot.high_energy * 0.55f;
		if (i == Snare)
			score *= 1.0f + snapshot.mid_energy * 0.45f;
		if (i == Rim)
			score *= 1.0f + snapshot.mid_energy * 0.56f;

		const bool cymbal_family_evidence =
			snapshot.high_energy >= 0.20f ||
			strongest_cymbal_drum >= strongest_body_drum * 0.10f;
		const bool soft_cymbal_separable =
			generated_gm_drum_source ||
			strongest_body_drum <= 1.0e-6f ||
			strongest_cymbal_drum >= strongest_body_drum * 0.055f ||
			snapshot.high_energy >= 0.42f;
		const bool soft_cymbal_transient =
			!tonal_soft_drum_suppressed && had_previous_audio && cymbal &&
			cymbal_family_evidence && soft_cymbal_separable && transient_ratio >= 0.65f;
		const bool embedded_hihat_transient =
			!tonal_soft_drum_suppressed && hihat &&
			((had_previous_audio &&
			  (real_drum_track_embedded_hihat || real_drum_track_low_embedded_hihat)) ||
			 initial_real_drum_track_embedded_hihat);
		const bool soft_kick_transient =
			kick && !tonal_soft_drum_suppressed &&
			(kick_low_onset_body_shape ||
			 (had_previous_audio && kick_click_transient &&
			  (transient_ratio >= 1.00f || kick_soft_body_shape)));
		const bool soft_snare_onset_shape = had_previous_audio && snare && snare_shape && onset >= 1.25f &&
						    !tonal_soft_drum_suppressed &&
						    score >= trigger_threshold * 1.15f;
		const bool clear_initial_snare_onset =
			!had_previous_audio && snare && snare_shape && onset >= 4.8f &&
			score >= trigger_threshold * 1.70f &&
			snapshot.mid_energy >= snapshot.low_energy * 1.20f &&
			strongest_cymbal_drum <= strongest_body_drum * 0.14f;
		const bool soft_snare_transient =
			snare && snare_shape &&
			((!tonal_soft_drum_suppressed && had_previous_audio &&
			  (transient_ratio >= 0.82f || soft_snare_onset_shape)) ||
			 clear_initial_snare_onset);
		const bool soft_rim_transient = !tonal_soft_drum_suppressed && had_previous_audio && rim &&
						rim_shape && transient_ratio >= 0.62f;
		const bool strong_tom_onset_shape =
			tom && tom_shape && onset >= 4.0f && score >= trigger_threshold * 1.70f &&
			body_shape_scores[2] >= body_shape_scores[1] * 1.30f &&
			body_shape_scores[2] >= body_shape_scores[0] * 1.40f &&
			snapshot.mid_energy >= snapshot.low_energy * 0.90f &&
			(snare_body <= 1.0e-6f || snare_crack <= snare_body * 0.10f ||
			 upper_tom_body >= snare_crack * 8.0f);
		const bool clear_initial_tom_onset =
			!had_previous_audio && tom && tom_shape && onset >= 4.0f &&
			score >= trigger_threshold * 1.70f &&
			body_shape_scores[2] >= body_shape_scores[1] * 1.28f &&
			body_shape_scores[2] >= body_shape_scores[0] * 1.20f &&
			snapshot.mid_energy >= snapshot.low_energy * 0.90f &&
			(snare_body <= 1.0e-6f || snare_crack <= snare_body * 0.10f ||
			 upper_tom_body >= snare_crack * 8.0f);
		const bool soft_tom_transient =
			tom && tom_shape && ((!tonal_soft_drum_suppressed && had_previous_audio &&
					      transient_ratio >= 0.72f) ||
					     strong_tom_onset_shape || clear_initial_tom_onset);
		const bool soft_body_transient =
			soft_kick_transient || soft_snare_transient || soft_rim_transient || soft_tom_transient;
		const bool base_shape_supported = drum_shape_supported[i];
		const bool shape_supported = base_shape_supported || soft_cymbal_transient ||
					     embedded_hihat_transient;
		const bool quiet_cymbal_shape =
			!tonal_soft_drum_suppressed && had_previous_audio && cymbal && base_shape_supported &&
			cymbal_family_evidence && strongest_cymbal_drum >= strongest_body_drum * 0.10f;
		const float threshold_scale = (soft_cymbal_transient || quiet_cymbal_shape ||
					       embedded_hihat_transient) ? 0.26f :
					      soft_kick_transient ? 0.32f :
					      soft_snare_transient ? 0.30f :
					      soft_rim_transient ? 0.24f :
					      (strong_tom_onset_shape || clear_initial_tom_onset) ? 0.30f :
					      soft_tom_transient ? 0.44f :
								     1.0f;
		const float effective_threshold = trigger_threshold * threshold_scale;
		snapshot.drum_debug_trigger_scores[i] = score;
		snapshot.drum_debug_trigger_thresholds[i] = effective_threshold;
		if (drum_detection_enabled && rms > kSilenceRms && shape_supported && (!kick || kick_click_transient) &&
		    (drum_transient || soft_cymbal_transient || quiet_cymbal_shape ||
		     embedded_hihat_transient || soft_body_transient) &&
		    score > effective_threshold) {
			const float threshold_excess = score / (effective_threshold + 1.0e-6f) - 1.0f;
			float level = std::clamp(0.25f + 0.75f * threshold_excess / (threshold_excess + 3.5f),
						 0.0f, 1.0f);
			if (cymbal && strongest_cymbal_drum > 1.0e-6f) {
				const float relative =
					std::clamp(drum_segment_bands[i] / strongest_cymbal_drum, 0.0f, 1.0f);
				const bool shell_dominant_hihat_blend =
					body_shape == Tom &&
					body_shape_scores[1] >= drum_segment_bands[HiHat] * 4.50f &&
					body_shape_scores[2] >= drum_segment_bands[HiHat] * 5.50f;
				if (i == HiHat && cymbal_shape == HiHat &&
				    drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.78f &&
				    snapshot.high_energy >= 0.035f &&
				    !shell_dominant_hihat_blend &&
				    !(body_shape == Snare && snare_crack >= snare_body * 0.035f &&
				      body_shape_scores[1] >= drum_segment_bands[HiHat] * 1.35f)) {
					level = std::clamp(level * 1.020f + 0.006f, 0.0f, 1.0f);
				} else {
					const float scale = cymbal_shape == Crash && i != Crash ?
									    0.96f + relative * 0.04f :
									    1.0f;
					level *= scale;
				}
			}
			if (kick) {
				const bool snare_body_competes_with_kick =
					snare_shape &&
					snare_body >= kick_body * 0.55f &&
					snare_crack >= snare_body * 0.080f &&
					drum_segment_bands[Snare] >= drum_segment_bands[Kick] * 0.55f &&
					snapshot.mid_energy >= snapshot.low_energy * 0.72f &&
					(strongest_cymbal_drum <= strongest_body_drum * 0.40f ||
					 snapshot.high_energy <= 0.38f);
				if (snare_body_competes_with_kick)
					level = std::min(level * 0.90f, 0.92f);
			}
			if (snare && snare_shape) {
				const bool shell_centered_snare =
					body_shape_scores[1] >= body_shape_scores[2] * 0.84f &&
					body_shape_scores[1] >= drum_segment_bands[HiHat] * 3.0f;
				const bool cymbal_backed_hihat =
					!generated_gm_drum_source &&
					(cymbal_shape == HiHat || hihat_family_shape || drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.42f) &&
					strongest_cymbal_drum > 0.0f &&
					snapshot.high_energy >= 0.17f &&
					strongest_cymbal_drum >= strongest_body_drum * 0.055f;
				const bool rim_hit_like_snare =
					rim_primary_evidence &&
					strongest_cymbal_drum < strongest_body_drum * 0.16f &&
					drum_segment_bands[HiHat] <
						std::max(body_shape_scores[1], rim_shape_score) * 0.22f;
				const bool clear_hihat_backed_snare =
					snare_crack_shape && strongest_cymbal_drum > 1.0e-6f &&
					drum_segment_bands[Snare] >= strongest_cymbal_drum * 2.50f &&
					snapshot.mid_energy >= 0.30f;
				const bool hihat_bleed_snare =
					cymbal_backed_hihat && body_shape != Snare &&
					strongest_cymbal_drum >= body_shape_scores[1] * 0.32f &&
					!rim_hit_like_snare && !clear_hihat_backed_snare &&
					body_shape_scores[1] < body_shape_scores[2] * 0.94f &&
					body_shape_scores[1] < body_shape_scores[0] * 1.70f;
				if (shell_centered_snare)
					level = std::clamp(level * 1.018f + 0.006f, 0.0f, 1.0f);
				else if (hihat_bleed_snare)
					level = std::min(level, 0.29f);
			}
			if (rim) {
				if (rim_primary_evidence) {
					const float shell_ratio = std::clamp(
						rim_shape_score / (strongest_shell_shape_score + 1.0e-6f),
						0.0f, 1.35f);
					const float cymbal_ratio = strongest_cymbal_drum > 1.0e-6f ?
						std::clamp(drum_segment_bands[Rim] / strongest_cymbal_drum,
							   0.0f, 1.0f) :
						1.0f;
					const float rim_level_bias =
						1.05f + shell_ratio * 0.08f + cymbal_ratio * 0.04f;
					level = std::clamp(level * rim_level_bias + 0.015f, 0.0f, 1.0f);
				} else if (rim_embedded_side_stick_shape && !rim_side_shape) {
					level = std::min(level, 0.46f);
				}
			}
			if (tom && (strong_tom_onset_shape || clear_initial_tom_onset))
				level = std::clamp(level * 1.01f + 0.005f, 0.0f, 1.0f);
			drum_level_[i] = std::max(drum_level_[i], level);
			tempo_event = true;
		} else {
			drum_level_[i] *= drum_detection_enabled ? 0.72f : 0.0f;
		}

		drum_average_[i] = drum_average_[i] * 0.92f + drum_bands[i] * 0.08f;
		snapshot.drums[i].level = drum_level_[i];
		snapshot.drums[i].active = drum_level_[i] > 0.30f;
	}

	auto cap_drum_level = [&](std::size_t index, float cap) {
		drum_level_[index] = std::min(drum_level_[index], cap);
		snapshot.drums[index].level = drum_level_[index];
		snapshot.drums[index].active = drum_level_[index] > 0.30f;
	};
	auto boost_drum_level = [&](std::size_t index, float level) {
		drum_level_[index] = std::max(drum_level_[index], std::clamp(level, 0.0f, 1.0f));
		snapshot.drums[index].level = drum_level_[index];
		snapshot.drums[index].active = drum_level_[index] > 0.30f;
	};
	auto promote_drum_primary = [&](std::size_t index, float minimum_level) {
		float strongest_competing_level = 0.0f;
		for (std::size_t i = 0; i < kDrumCount; ++i) {
			if (i != index)
				strongest_competing_level = std::max(strongest_competing_level, drum_level_[i]);
		}
		boost_drum_level(index, std::max(minimum_level, strongest_competing_level + 0.02f));
		for (std::size_t i = 0; i < kDrumCount; ++i) {
			if (i != index && drum_level_[i] > 0.30f)
				cap_drum_level(i, std::max(0.31f, drum_level_[index] - 0.02f));
		}
	};

	const float snare_trigger_ratio_after_detection =
		snapshot.drum_debug_trigger_scores[Snare] /
		(snapshot.drum_debug_trigger_thresholds[Snare] + 1.0e-6f);
	const bool supported_low_real_drum_snare =
		drum_detection_enabled && real_drum_track_source &&
		drum_level_[Snare] >= 0.14f && drum_level_[Snare] <= 0.30f &&
		drum_shape_supported[Snare] &&
		body_shape == Tom &&
		snare_trigger_ratio_after_detection >= 0.60f &&
		rms <= 0.030f &&
		snare_body >= 0.50f &&
		snare_crack >= snare_body * 0.050f &&
		snapshot.low_energy <= 0.55f &&
		snapshot.mid_energy >= snapshot.low_energy * 0.85f;
	if (supported_low_real_drum_snare)
		boost_drum_level(Snare, 0.34f);

	const bool low_dominant_kick_bleed =
		drum_detection_enabled && !one_shot_drum_source &&
		drum_level_[Kick] > 0.30f && drum_shape_supported[Kick] &&
		(body_shape == Kick || kick_low_dominant_body || kick_tonal_body_shape || kick_low_onset_body_shape) &&
		snapshot.low_energy >= 0.70f &&
		snapshot.low_energy >= snapshot.mid_energy * 1.80f &&
		kick_body >= snare_body * 0.80f &&
		(strongest_cymbal_drum <= 1.0e-6f || strongest_cymbal_drum <= strongest_body_drum * 0.36f);
	if (low_dominant_kick_bleed) {
		const bool tom_is_kick_bleed =
			drum_level_[Tom] > 0.30f &&
			tom_body <= kick_body * 1.75f &&
			upper_tom_body <= kick_body * 0.48f &&
			snapshot.mid_energy <= snapshot.low_energy * 0.62f;
		const bool snare_is_kick_bleed =
			drum_level_[Snare] > 0.30f &&
			!kick_backed_snare_transient &&
			snare_body <= kick_body * 0.72f &&
			snare_crack <= std::max(snare_body * 0.16f, kick_body * 0.080f);
		const bool rim_is_kick_bleed =
			drum_level_[Rim] > 0.30f &&
			rim_body <= kick_body * 0.42f &&
			rim_low_mid_body <= kick_body * 0.34f;
		if (tom_is_kick_bleed)
			cap_drum_level(Tom, 0.28f);
		if (snare_is_kick_bleed)
			cap_drum_level(Snare, 0.28f);
		if (rim_is_kick_bleed)
			cap_drum_level(Rim, 0.28f);
	}

	const bool snare_supported_rim_saturation =
		drum_detection_enabled && !one_shot_drum_source &&
		drum_level_[Rim] >= 0.95f &&
		drum_level_[Snare] >= 0.55f &&
		body_shape == Snare &&
		snare_shape &&
		snare_body >= rim_body * 0.78f &&
		snare_body >= kick_body * 0.34f &&
		snare_body >= tom_body * 0.34f &&
		snare_crack >= snare_body * 0.55f &&
		rim_shape_score <= body_shape_scores[1] * 1.05f;
	if (snare_supported_rim_saturation)
		cap_drum_level(Rim, std::max(0.31f, drum_level_[Snare] - 0.02f));

	const bool crash_backed_snare_rim_bleed =
		drum_detection_enabled &&
		drum_level_[Rim] >= 0.95f &&
		drum_level_[Snare] >= 0.55f &&
		drum_level_[Crash] >= 0.90f &&
		snapshot.mid_energy <= 0.15f &&
		body_shape == Snare &&
		snare_shape &&
		snare_body >= kick_body * 0.34f &&
		snare_body >= tom_body * 0.34f &&
		snare_crack >= snare_body * 0.55f &&
		rim_shape_score <= body_shape_scores[1] * 1.25f;
	if (crash_backed_snare_rim_bleed)
		cap_drum_level(Rim, std::max(0.31f, drum_level_[Snare] - 0.02f));

	const float active_cymbal_level =
		std::max(drum_level_[HiHat], std::max(drum_level_[Crash], drum_level_[Ride]));
	const bool snare_cymbal_tom_bleed =
		drum_detection_enabled && !one_shot_drum_source &&
		drum_level_[Tom] > 0.30f &&
		drum_level_[Snare] > 0.70f &&
		active_cymbal_level > 0.55f &&
		body_shape == Tom &&
		snapshot.mid_energy >= snapshot.low_energy * 1.20f &&
		tom_body <= snare_body * 1.75f &&
		upper_tom_body <= tom_body * 0.58f &&
		snare_crack >= snare_body * 0.035f;
	if (snare_cymbal_tom_bleed)
		cap_drum_level(Tom, 0.28f);

	// Measured one-shot rows show some drum families being stolen by nearby scoring.
	const float hihat_rim_band_ratio = drum_bands[HiHat] / (drum_bands[Rim] + 1.0e-6f);
	const float hihat_rim_level_ratio =
		drum_level_[HiHat] / (drum_level_[Rim] + 1.0e-6f);
	const float hihat_rim_segment_ratio =
		drum_segment_bands[HiHat] / (drum_segment_bands[Rim] + 1.0e-6f);
	const float hihat_rim_shape_score_ratio =
		drum_segment_bands[HiHat] / (rim_shape_score + 1.0e-6f);
	const float crash_hihat_level_ratio =
		drum_level_[Crash] / (drum_level_[HiHat] + 1.0e-6f);
	const float crash_hihat_segment_ratio =
		drum_segment_bands[Crash] / (drum_segment_bands[HiHat] + 1.0e-6f);
	const float snare_kick_level_ratio =
		drum_level_[Snare] / (drum_level_[Kick] + 1.0e-6f);
	const float snare_kick_segment_ratio =
		drum_segment_bands[Snare] / (drum_segment_bands[Kick] + 1.0e-6f);
	const float tom_kick_level_ratio =
		drum_level_[Tom] / (drum_level_[Kick] + 1.0e-6f);
	const float tom_snare_level_ratio =
		drum_level_[Tom] / (drum_level_[Snare] + 1.0e-6f);
	const float tom_kick_body_ratio =
		tom_body / (kick_body + 1.0e-6f);
	const float tom_snare_body_ratio =
		tom_body / (snare_body + 1.0e-6f);
	const float snare_kick_body_ratio =
		snare_body / (kick_body + 1.0e-6f);
	const float tom_snare_segment_ratio =
		drum_segment_bands[Tom] / (drum_segment_bands[Snare] + 1.0e-6f);
	const float tom_kick_segment_ratio =
		drum_segment_bands[Tom] / (drum_segment_bands[Kick] + 1.0e-6f);
	const float tom_kick_shape_score_ratio =
		body_shape_scores[2] / (body_shape_scores[0] + 1.0e-6f);
	const float tom_snare_shape_score_ratio =
		body_shape_scores[2] / (body_shape_scores[1] + 1.0e-6f);
	const float tom_kick_band_ratio =
		drum_bands[Tom] / (drum_bands[Kick] + 1.0e-6f);
	const float tom_snare_total_band_ratio =
		drum_bands[Tom] / (drum_bands[Snare] + 1.0e-6f);
	const float tom_snare_band_ratio =
		drum_segment_bands[Tom] / (drum_segment_bands[Snare] + 1.0e-6f);
	const float tom_kick_trigger_ratio =
		snapshot.drum_debug_trigger_scores[Tom] /
		(snapshot.drum_debug_trigger_scores[Kick] + 1.0e-6f);
	const float hihat_rim_trigger_ratio =
		snapshot.drum_debug_trigger_scores[HiHat] /
		(snapshot.drum_debug_trigger_scores[Rim] + 1.0e-6f);
	const float ride_hihat_level_ratio =
		drum_level_[Ride] / (drum_level_[HiHat] + 1.0e-6f);
	const float ride_hihat_segment_ratio =
		drum_segment_bands[Ride] / (drum_segment_bands[HiHat] + 1.0e-6f);
	const float ride_hihat_shape_score_ratio =
		drum_segment_bands[Ride] / (drum_segment_bands[HiHat] + 1.0e-6f);
	const float snare_kick_trigger_ratio =
		snapshot.drum_debug_trigger_scores[Snare] /
		(snapshot.drum_debug_trigger_scores[Kick] + 1.0e-6f);
	const float tom_snare_trigger_ratio =
		snapshot.drum_debug_trigger_scores[Tom] /
		(snapshot.drum_debug_trigger_scores[Snare] + 1.0e-6f);
	const float snare_kick_shape_score_ratio =
		body_shape_scores[1] / (body_shape_scores[0] + 1.0e-6f);
	const bool one_shot_kick_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] >= 0.92f &&
		drum_level_[Snare] > 0.30f &&
		drum_shape_supported[Kick] &&
		snare_kick_level_ratio >= 1.043f;
	const bool one_shot_kick_tom_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] >= 0.92f &&
		drum_level_[Tom] > 0.30f &&
		drum_shape_supported[Kick] &&
		(tom_kick_level_ratio >= 1.053f || snare_kick_level_ratio >= 1.065f);
	if (one_shot_kick_snare_steal) {
		boost_drum_level(Kick, std::max(0.94f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Kick] - 0.02f));
	}
	if (one_shot_kick_tom_steal) {
		boost_drum_level(Kick, std::max(0.94f, drum_level_[Tom] + 0.02f));
		cap_drum_level(Tom, std::max(0.31f, drum_level_[Kick] - 0.02f));
	}
	const bool one_shot_low_transient_tom_kick_steal =
		hihat_rim_segment_ratio <= 0.091f &&
		drum_transient_ratio <= 1.28f;
	const bool one_shot_active_tom_kick_steal =
		drum_level_[Tom] > 0.30f &&
		tom_kick_level_ratio <= 0.535f &&
		tom_snare_level_ratio >= 0.989f;
	const bool measured_one_shot_tom_shape =
		drum_shape_supported[Tom] || tom_shape || body_shape == Tom || drum_level_[Tom] > 0.50f;
	const bool one_shot_measured_tom_kick_band_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] >= 0.96f &&
		measured_one_shot_tom_shape &&
		((tom_kick_band_ratio >= 5.763f &&
		  tom_kick_trigger_ratio <= 0.743f) ||
		 (snare_kick_shape_score_ratio <= 0.460f &&
		  tom_kick_band_ratio >= 4.715f));
	const bool one_shot_measured_tom_kick_level_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] >= 0.90f &&
		drum_level_[Tom] > 0.30f &&
		measured_one_shot_tom_shape &&
		tom_kick_level_ratio <= 0.546f &&
		tom_snare_level_ratio >= 0.978f;
	const bool one_shot_measured_tom_kick_shape_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		measured_one_shot_tom_shape &&
		snapshot.low_energy <= 0.80f &&
		tom_snare_shape_score_ratio >= 2.883f;
	const bool one_shot_measured_quiet_tom_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		measured_one_shot_tom_shape &&
		drum_bands[HiHat] <= 0.06f &&
		drum_level_[Tom] >= 0.92f &&
		tom_kick_level_ratio >= 0.897f;
	const bool one_shot_measured_body_tom_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		measured_one_shot_tom_shape &&
		snare_kick_level_ratio <= 0.989f &&
		body_shape_scores[1] >= 43.24f &&
		drum_bands[Tom] <= 68.98f;
	const bool measured_snare_kick_level_steal =
		drum_detection_enabled &&
		drum_level_[Kick] > 0.30f &&
		drum_level_[Snare] >= 0.59f &&
		snare_kick_level_ratio <= 0.622f;
	const bool one_shot_measured_snare_kick_band_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		drum_level_[Snare] > 0.30f &&
		snapshot.mid_energy >= 0.18f &&
		tom_kick_band_ratio <= 0.714f;
	const bool one_shot_measured_low_kick_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		snare_shape &&
		body_shape_scores[0] >= 98.95f &&
		snapshot.drum_debug_trigger_scores[Kick] <= 35.81f &&
		snapshot.low_energy >= 0.49f;
	const bool one_shot_measured_low_snare_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		drum_level_[Tom] <= drum_level_[Kick] * 0.93f &&
		drum_bands[Crash] >= 7.56f &&
		drum_bands[Kick] >= 103.98f &&
		snare_kick_shape_score_ratio >= 0.345f &&
		tom_kick_body_ratio <= 1.875f;
	const bool one_shot_measured_segment_snare_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		snare_kick_segment_ratio >= 0.944f &&
		tom_snare_shape_score_ratio >= 1.87f;
	if (one_shot_measured_tom_kick_band_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_tom_kick_level_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_tom_kick_shape_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_quiet_tom_kick_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_body_tom_kick_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (measured_snare_kick_level_steal) {
		boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
	}
	if (one_shot_measured_snare_kick_band_steal) {
		boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
	}
	if (one_shot_measured_low_kick_snare_steal) {
		boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
	}
	if (one_shot_measured_low_snare_kick_steal) {
		boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
	}
	if (one_shot_measured_segment_snare_kick_steal) {
		boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
	}
	const bool one_shot_tom_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		drum_shape_supported[Tom] &&
		(one_shot_low_transient_tom_kick_steal || one_shot_active_tom_kick_steal) &&
		tom_body >= kick_body * 1.02f &&
		tom_body >= snare_body * 0.98f &&
		snare_crack <= snare_body * 0.80f;
	if (one_shot_tom_kick_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	const bool one_shot_measured_quiet_crash_tom_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		measured_one_shot_tom_shape &&
		drum_segment_bands[Crash] <= 0.05f &&
		(kick_body <= 76.89f ||
		 tom_snare_segment_ratio <= 1.617f ||
		 (hihat_rim_trigger_ratio <= 0.855f &&
		  snapshot.drum_debug_trigger_scores[HiHat] <= 51.17f));
	const bool one_shot_measured_low_band_tom_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		measured_one_shot_tom_shape &&
		hihat_rim_trigger_ratio <= 0.797f &&
		drum_bands[Tom] <= 38.30f &&
		tom_snare_level_ratio <= 0.929f &&
		tom_body >= snare_body * 1.35f &&
		upper_tom_body >= snare_crack * 3.0f &&
		snapshot.mid_energy >= 0.60f &&
		snapshot.high_energy <= 0.15f;
	const bool one_shot_measured_upper_tom_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		measured_one_shot_tom_shape &&
		ride_hihat_segment_ratio <= 1.135f &&
		upper_tom_body >= 107.34f;
	const bool one_shot_measured_tom_snare_near_tie_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] <= 0.001f &&
		drum_level_[Tom] > 0.30f &&
		drum_level_[Snare] > 0.30f &&
		measured_one_shot_tom_shape &&
		tom_snare_level_ratio >= 0.985f &&
		tom_snare_level_ratio <= 0.995f &&
		tom_body >= snare_body * 1.10f &&
		upper_tom_body >= snare_crack * 3.0f &&
		snapshot.mid_energy >= 0.55f &&
		snapshot.high_energy <= 0.30f;
	const bool one_shot_measured_hihat_rim_tom_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Tom] > 0.30f &&
		drum_level_[Snare] > 0.30f &&
		measured_one_shot_tom_shape &&
		tom_body >= 80.0f &&
		hihat_rim_segment_ratio >= 0.724f &&
		hihat_rim_shape_score_ratio <= 0.631f;
	const bool one_shot_tom_snare_inactive_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		body_shape == Tom &&
		drum_level_[Kick] <= 0.001f &&
		drum_level_[Tom] > 0.30f &&
		drum_level_[Snare] > 0.30f &&
		drum_shape_supported[Tom] &&
		((drum_segment_bands[Crash] <= 1.96f &&
		  tom_snare_level_ratio <= 0.99f) ||
		 tom_snare_level_ratio <= 0.592f);
	const bool one_shot_tom_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		drum_shape_supported[Tom] &&
		snapshot.high_energy <= 0.10f &&
		tom_snare_band_ratio <= 0.919f &&
		tom_body >= snare_body * 1.25f &&
		upper_tom_body >= snare_crack * 6.0f;
	if (one_shot_tom_snare_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_quiet_crash_tom_snare_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_low_band_tom_snare_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_upper_tom_snare_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_tom_snare_near_tie_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_measured_hihat_rim_tom_snare_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	if (one_shot_tom_snare_inactive_kick_steal) {
		boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
	}
	const bool one_shot_measured_rim_tom_low_band_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] <= 0.001f &&
		drum_level_[Rim] > 0.30f &&
		drum_level_[Tom] >= 0.93f &&
		drum_bands[Tom] <= 0.17f;
	const bool one_shot_measured_low_tom_rim_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		drum_level_[Rim] > 0.30f &&
		snapshot.drum_debug_trigger_scores[Rim] >= 21.26f &&
		snapshot.drum_debug_trigger_scores[Tom] <= 17.32f &&
		upper_tom_body <= snare_crack * 2.997f;
	const bool one_shot_measured_short_body_rim_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		drum_level_[Rim] > 0.30f &&
		tom_body <= 50.325f &&
		drum_segment_bands[Tom] >= 50.57f &&
		tom_snare_band_ratio <= 1.332f;
	const bool one_shot_measured_mid_body_rim_snare_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Snare] > 0.30f &&
		drum_bands[HiHat] <= 0.01f &&
		snapshot.low_energy >= 0.22f &&
		snapshot.low_energy <= 0.29f &&
		snapshot.mid_energy >= 0.49f;
	if (one_shot_measured_rim_tom_low_band_steal) {
		const float competing_shell_level = std::max(drum_level_[Tom], drum_level_[Snare]);
		boost_drum_level(Rim, std::max(0.94f, competing_shell_level + 0.02f));
		cap_drum_level(Tom, std::max(0.31f, drum_level_[Rim] - 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Rim] - 0.02f));
	}
	if (one_shot_measured_low_tom_rim_snare_steal) {
		const float competing_shell_level = std::max(drum_level_[Snare], drum_level_[Tom]);
		boost_drum_level(Rim, std::max(0.90f, competing_shell_level + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Rim] - 0.02f));
		cap_drum_level(Tom, std::max(0.31f, drum_level_[Rim] - 0.02f));
	}
	if (one_shot_measured_short_body_rim_snare_steal) {
		const float competing_shell_level = std::max(drum_level_[Snare], drum_level_[Tom]);
		boost_drum_level(Rim, std::max(0.90f, competing_shell_level + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Rim] - 0.02f));
		cap_drum_level(Tom, std::max(0.31f, drum_level_[Rim] - 0.02f));
	}
	if (one_shot_measured_mid_body_rim_snare_steal) {
		const float competing_shell_level = std::max(drum_level_[Snare], drum_level_[Tom]);
		boost_drum_level(Rim, std::max(0.90f, competing_shell_level + 0.02f));
		cap_drum_level(Snare, std::max(0.31f, drum_level_[Rim] - 0.02f));
		cap_drum_level(Tom, std::max(0.31f, drum_level_[Rim] - 0.02f));
	}
	const bool one_shot_measured_hihat_rim_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[HiHat] >= 0.80f &&
		drum_level_[Rim] >= 0.99f &&
		hihat_rim_band_ratio >= 0.828f &&
		hihat_rim_segment_ratio >= 0.75f &&
		tom_snare_trigger_ratio <= 0.923f;
	if (one_shot_measured_hihat_rim_steal) {
		boost_drum_level(HiHat, std::max(0.90f, drum_level_[Rim] + 0.02f));
		cap_drum_level(Rim, 0.28f);
	}
	const bool one_shot_measured_saturated_rim_hihat_recovery =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[HiHat] > 0.30f &&
		drum_level_[Rim] >= 0.96f &&
		tom_snare_level_ratio >= 2.448f &&
		tom_snare_trigger_ratio <= 0.885f;
	if (one_shot_measured_saturated_rim_hihat_recovery) {
		boost_drum_level(HiHat, std::max(0.90f, drum_level_[Rim] + 0.02f));
		cap_drum_level(Rim, std::max(0.31f, drum_level_[HiHat] - 0.02f));
	}
	const bool one_shot_measured_low_crack_hihat_rim_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[HiHat] > 0.30f &&
		drum_level_[Rim] > 0.30f &&
		ride_hihat_level_ratio >= 1.0f &&
		snare_crack <= 4.05f &&
		snare_kick_trigger_ratio >= 0.941f;
	if (one_shot_measured_low_crack_hihat_rim_steal) {
		const float strongest_non_hihat_level =
			std::max(std::max(drum_level_[Kick], drum_level_[Snare]),
				 std::max(std::max(drum_level_[Crash], drum_level_[Tom]),
					  std::max(drum_level_[Ride], drum_level_[Rim])));
		boost_drum_level(HiHat, std::max(0.90f, strongest_non_hihat_level + 0.02f));
		cap_drum_level(Rim, std::max(0.31f, drum_level_[HiHat] - 0.02f));
	}
	const bool one_shot_measured_hihat_ambiguous_recovery =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[HiHat] > 0.30f &&
		hihat_rim_segment_ratio <= 2.613f &&
		upper_tom_body <= 1.19f;
	if (one_shot_measured_hihat_ambiguous_recovery) {
		const float strongest_non_hihat_level =
			std::max(std::max(drum_level_[Kick], drum_level_[Snare]),
				 std::max(std::max(drum_level_[Crash], drum_level_[Tom]),
					  std::max(drum_level_[Ride], drum_level_[Rim])));
		boost_drum_level(HiHat, std::max(0.90f, strongest_non_hihat_level + 0.02f));
	}
	const bool one_shot_measured_low_body_hihat_kick_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Kick] > 0.30f &&
		snapshot.low_energy >= 0.62f &&
		snapshot.mid_energy <= 0.19f &&
		snapshot.drum_debug_trigger_scores[Crash] <= 20.70f;
	if (one_shot_measured_low_body_hihat_kick_steal) {
		const float strongest_non_hihat_level =
			std::max(std::max(drum_level_[Kick], drum_level_[Snare]),
				 std::max(std::max(drum_level_[Crash], drum_level_[Tom]),
					  std::max(drum_level_[Ride], drum_level_[Rim])));
		boost_drum_level(HiHat, std::max(0.90f, strongest_non_hihat_level + 0.02f));
		cap_drum_level(Kick, std::max(0.31f, drum_level_[HiHat] - 0.02f));
	}
	const bool one_shot_measured_hihat_crash_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Crash] > 0.30f &&
		crash_hihat_level_ratio >= 1.012f &&
		crash_hihat_segment_ratio >= 1.484f;
	const bool one_shot_measured_crash_hihat_steal =
		drum_detection_enabled && one_shot_drum_source &&
		!one_shot_measured_hihat_crash_steal &&
		drum_level_[HiHat] > 0.30f &&
		drum_shape_supported[Crash] &&
		snare_body <= 6.29f &&
		drum_bands[Tom] >= 14.82f;
	const bool one_shot_measured_low_trigger_crash_hihat_steal =
		drum_detection_enabled && one_shot_drum_source &&
		!one_shot_measured_hihat_crash_steal &&
		drum_level_[HiHat] > 0.30f &&
		drum_segment_bands[Crash] >= 9.60f &&
		snapshot.drum_debug_trigger_scores[Crash] <= 17.05f &&
		hihat_rim_level_ratio >= 1.045f;
	const bool one_shot_measured_crash_rim_steal =
		drum_detection_enabled && one_shot_drum_source &&
		drum_level_[Crash] >= 0.90f &&
		drum_level_[Rim] >= 0.99f &&
		drum_level_[HiHat] >= 0.918f &&
		hihat_rim_level_ratio <= 0.932f &&
		hihat_rim_trigger_ratio >= 1.031f;
	if (one_shot_measured_hihat_crash_steal) {
		boost_drum_level(HiHat, std::max(0.90f, drum_level_[Crash] + 0.02f));
		cap_drum_level(Crash, std::max(0.31f, drum_level_[HiHat] - 0.02f));
	}
	if (one_shot_measured_crash_hihat_steal) {
		boost_drum_level(Crash, std::max(0.90f, drum_level_[HiHat] + 0.02f));
		cap_drum_level(HiHat, std::max(0.31f, drum_level_[Crash] - 0.02f));
	}
	if (one_shot_measured_low_trigger_crash_hihat_steal) {
		boost_drum_level(Crash, std::max(0.90f, drum_level_[HiHat] + 0.02f));
		cap_drum_level(HiHat, std::max(0.31f, drum_level_[Crash] - 0.02f));
	}
	if (one_shot_measured_crash_rim_steal) {
		boost_drum_level(Crash, std::max(0.90f, drum_level_[Rim] + 0.02f));
		cap_drum_level(Rim, std::max(0.31f, drum_level_[Crash] - 0.02f));
	}
		const float snare_kick_level_ratio_after_tom =
			drum_level_[Snare] / (drum_level_[Kick] + 1.0e-6f);
		const float tom_snare_level_ratio_after_tom =
			drum_level_[Tom] / (drum_level_[Snare] + 1.0e-6f);
		const float rim_snare_level_ratio_after_tom =
			drum_level_[Rim] / (drum_level_[Snare] + 1.0e-6f);
		const float snare_kick_trigger_ratio_after_tom =
			snapshot.drum_debug_trigger_scores[Snare] /
			(snapshot.drum_debug_trigger_scores[Kick] + 1.0e-6f);
		const bool one_shot_snare_tom_steal =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Snare] > 0.30f &&
		drum_level_[Tom] > 0.30f &&
		snare_body >= 33.6f &&
		snare_crack <= snare_body * 0.14f &&
			snapshot.high_energy <= 0.30f &&
			tom_snare_level_ratio_after_tom >= 1.01f &&
			snapshot.drum_debug_trigger_scores[Tom] <= 24.45f;
		const bool measured_snare_tom_mid_body =
			snapshot.mid_energy >= 0.71f ||
			(drum_level_[Kick] <= 0.001f && drum_segment_bands[Crash] <= 0.21f);
		const bool one_shot_measured_near_snare_tom_steal =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.70f &&
			drum_level_[Tom] > 0.30f &&
			hihat_rim_trigger_ratio <= 0.795f &&
			tom_snare_level_ratio_after_tom >= 1.02f &&
			tom_snare_level_ratio_after_tom <= 1.25f &&
			measured_snare_tom_mid_body;
		const bool one_shot_measured_low_cymbal_snare_tom_steal =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Kick] <= 0.001f &&
			drum_level_[Snare] >= 0.60f &&
			drum_level_[Tom] >= 0.90f &&
			drum_level_[Tom] <= 0.94f &&
			drum_level_[Tom] > drum_level_[Snare] &&
			drum_segment_bands[HiHat] <= 1.50f &&
			drum_segment_bands[Crash] <= 0.50f &&
			snare_crack <= 2.65f;
		const bool measured_snare_rim_crack =
			(drum_level_[Kick] <= 0.001f &&
			 drum_segment_bands[Crash] <= 1.01f &&
			 drum_level_[HiHat] >= 0.59f) ||
			(snapshot.high_energy >= 0.60f && hihat_rim_segment_ratio <= 0.212f) ||
			(drum_bands[Crash] <= 14.34f &&
			 drum_level_[Rim] >= 0.93f &&
			 snare_body >= 12.95f &&
			 snare_kick_trigger_ratio_after_tom >= 1.156f) ||
			(drum_level_[Rim] >= 0.93f &&
			 snare_body >= 12.95f &&
			 tom_snare_band_ratio >= 1.18f &&
			 tom_snare_band_ratio <= 1.313f);
		const bool one_shot_measured_near_snare_rim_steal =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.55f &&
			drum_level_[Rim] > 0.30f &&
			rim_snare_level_ratio_after_tom >= 1.0f &&
			rim_snare_level_ratio_after_tom <= 1.20f &&
			measured_snare_rim_crack;
		const bool one_shot_snare_kick_steal =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Snare] >= 0.29f &&
			snapshot.high_energy <= 0.30f &&
			snare_kick_level_ratio_after_tom <= 0.333f;
		const bool one_shot_measured_near_snare_kick_steal =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] >= 0.97f &&
			drum_level_[Snare] >= 0.80f &&
			drum_level_[Tom] <= 0.89f &&
			tom_kick_trigger_ratio >= 0.739f &&
			drum_segment_bands[Tom] <= 359.88f;
		if (one_shot_snare_tom_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Tom] + 0.02f));
			cap_drum_level(Tom, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}
		if (one_shot_measured_near_snare_tom_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Tom] + 0.02f));
			cap_drum_level(Tom, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}
		if (one_shot_measured_low_cymbal_snare_tom_steal) {
			boost_drum_level(Snare, std::max(0.92f, drum_level_[Tom] + 0.04f));
			cap_drum_level(Tom, std::max(0.31f, drum_level_[Snare] - 0.04f));
		}
		if (one_shot_measured_near_snare_rim_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Rim] + 0.02f));
			cap_drum_level(Rim, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}
		if (one_shot_snare_kick_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
			cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}
		if (one_shot_measured_near_snare_kick_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Kick] + 0.02f));
			cap_drum_level(Kick, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}
		const bool measured_one_shot_tom_snare_body_steal =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Kick] <= 0.001f &&
			drum_level_[Snare] > 0.30f &&
			drum_shape_supported[Tom] &&
			hihat_rim_shape_score_ratio <= 0.111f &&
			snare_kick_segment_ratio <= 2.35f &&
			drum_segment_bands[Snare] >= 53.86f &&
			tom_snare_band_ratio <= 1.626f;
		const bool measured_one_shot_low_tom_kick_body_steal =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			measured_one_shot_tom_shape &&
			tom_kick_level_ratio <= 0.586f &&
			tom_snare_level_ratio >= 0.989f &&
			tom_body >= kick_body * 1.30f &&
			tom_body >= snare_body * 1.20f;
		if (measured_one_shot_tom_snare_body_steal) {
			boost_drum_level(Tom, std::max(0.90f, drum_level_[Snare] + 0.02f));
			cap_drum_level(Snare, std::max(0.31f, drum_level_[Tom] - 0.02f));
		}
		if (measured_one_shot_low_tom_kick_body_steal) {
			boost_drum_level(Tom, std::max(0.90f, drum_level_[Kick] + 0.02f));
			cap_drum_level(Kick, std::max(0.31f, drum_level_[Tom] - 0.02f));
		}
		const bool measured_one_shot_snare_tom_body_steal =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Kick] <= 0.001f &&
			drum_level_[Tom] > 0.30f &&
			snapshot.high_energy <= 0.14f &&
			hihat_rim_band_ratio >= 0.394f &&
			tom_kick_segment_ratio <= 3.113f &&
			tom_kick_shape_score_ratio >= 1.296f;
		if (measured_one_shot_snare_tom_body_steal) {
			boost_drum_level(Snare, std::max(0.90f, drum_level_[Tom] + 0.02f));
			cap_drum_level(Tom, std::max(0.31f, drum_level_[Snare] - 0.02f));
		}

		const float final_snare_kick_level_ratio =
			drum_level_[Snare] / (drum_level_[Kick] + 1.0e-6f);
		const float final_tom_kick_level_ratio =
			drum_level_[Tom] / (drum_level_[Kick] + 1.0e-6f);
		const bool one_shot_measured_kick_high_shape_snare_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			body_shape_scores[0] >= 328.31f &&
			final_snare_kick_level_ratio >= 1.01f &&
			body_shape_scores[1] >= 142.0f &&
			drum_level_[Tom] <= 0.98f;
		const bool one_shot_measured_kick_high_shape_ambiguous_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			body_shape_scores[0] >= 348.53f &&
			drum_level_[Snare] >= 0.99f &&
			tom_kick_band_ratio <= 7.508f &&
			tom_kick_shape_score_ratio >= 0.903f;
		const bool one_shot_measured_kick_body_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			kick_body >= 262.58f &&
			final_tom_kick_level_ratio >= 1.01f;
		const bool one_shot_measured_kick_low_hihat_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 20.67f &&
			snare_kick_segment_ratio <= 0.548f;
		const bool one_shot_measured_kick_rim_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			body_shape_scores[0] >= 129.45f &&
			drum_level_[Rim] >= 0.92f &&
			snapshot.drum_debug_trigger_scores[Rim] <= 47.36f;
		if (one_shot_measured_kick_high_shape_snare_recovery ||
		    one_shot_measured_kick_high_shape_ambiguous_recovery ||
		    one_shot_measured_kick_body_tom_recovery ||
		    one_shot_measured_kick_low_hihat_recovery ||
		    one_shot_measured_kick_rim_recovery)
			promote_drum_primary(Kick, 0.90f);

		const bool one_shot_measured_rim_snare_onset_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			onset >= 5.0f &&
			onset <= 48.21f &&
			drum_level_[Snare] >= 0.97f;
		const bool one_shot_measured_rim_snare_low_trigger_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.high_energy >= 0.50f &&
			snapshot.drum_debug_trigger_scores[Rim] <= 14.73f &&
			drum_level_[Snare] >= 0.96f;
		const bool one_shot_measured_rim_snare_transient_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Snare &&
			drum_transient_ratio >= 2.76f &&
			snapshot.high_energy <= 0.45f &&
			drum_level_[Snare] >= 0.95f &&
			upper_tom_body <= 22.38f;
		const bool one_shot_measured_rim_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Rim] <= 24.955f &&
			drum_level_[Tom] >= 0.98f &&
			drum_segment_bands[Tom] >= 48.80f &&
			upper_tom_body <= 37.95f;
		const bool one_shot_measured_low_band_rim_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] <= 0.001f &&
			drum_level_[Tom] >= 0.94f &&
			drum_level_[Snare] >= 0.90f &&
			drum_bands[Rim] >= 0.0285f &&
			drum_bands[Rim] <= 0.0315f &&
			snapshot.drum_debug_trigger_scores[Rim] >= 13.0f &&
			snapshot.drum_debug_trigger_scores[Rim] <= 17.0f &&
			rim_low_mid_body >= 4.5f &&
			snare_crack >= 1.5f &&
			snapshot.high_energy <= 0.36f;
		const bool one_shot_measured_low_crash_rim_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] <= 0.001f &&
			drum_level_[Tom] >= 0.90f &&
			drum_level_[Snare] >= 0.70f &&
			drum_bands[Crash] <= 0.0045f &&
			tom_kick_band_ratio >= 3.20f &&
			snapshot.drum_debug_trigger_scores[Rim] >= 10.0f &&
			snare_crack >= 1.8f &&
			snapshot.high_energy <= 0.20f;
		const bool one_shot_measured_low_crash_body_rim_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] <= 0.001f &&
			drum_level_[Tom] >= 0.98f &&
			drum_level_[Snare] >= 0.96f &&
			drum_bands[Crash] <= 0.0045f &&
			snare_kick_body_ratio >= 4.50f &&
			snapshot.drum_debug_trigger_scores[Rim] >= 17.0f &&
			snapshot.drum_debug_trigger_scores[Rim] <= 19.0f &&
			snare_crack >= 3.5f &&
			snapshot.high_energy <= 0.16f;
		const bool one_shot_measured_narrow_body_rim_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Tom] >= 0.90f &&
			drum_level_[Snare] >= 0.70f &&
			tom_snare_body_ratio >= 1.470f &&
			tom_snare_body_ratio <= 1.483f &&
			snapshot.high_energy <= 0.25f;
		const bool one_shot_measured_rim_tom_trigger_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Kick] <= 16.25f &&
			drum_level_[Tom] >= 0.97f &&
			tom_snare_trigger_ratio <= 0.81f;
		const bool one_shot_measured_rim_tom_low_kick_trigger_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Kick] <= 12.31f &&
			snare_body >= 24.11f;
		const bool one_shot_measured_rim_tom_upper_body_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Kick] <= 14.87f &&
			drum_level_[Tom] >= 0.90f &&
			upper_tom_body >= 26.75f;
		const bool one_shot_measured_rim_tom_shape_ratio_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			snare_kick_shape_score_ratio >= 2.936f &&
			tom_snare_level_ratio >= 1.01f;
		const bool one_shot_measured_rim_tom_low_ride_kick_trigger_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Kick] >= 417.29f &&
			snapshot.low_energy <= 0.24f &&
			drum_bands[Ride] <= 0.02f;
		const bool one_shot_measured_rim_ambiguous_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape_scores[1] <= 16.80f &&
			body_shape_scores[2] >= 17.77f &&
			tom_snare_body_ratio <= 1.523f &&
			snapshot.drum_debug_trigger_scores[Tom] <= 17.94f;
		const bool one_shot_measured_rim_ambiguous_ride_ratio_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			hihat_rim_shape_score_ratio >= 0.546f &&
			ride_hihat_segment_ratio >= 3.512f &&
			ride_hihat_shape_score_ratio <= 3.571f;
		const bool one_shot_measured_rim_ambiguous_shape_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_segment_bands[Rim] >= 12.20f &&
			rim_shape_score <= 9.55f &&
			snapshot.drum_debug_trigger_scores[Rim] <= 22.74f;
		const bool one_shot_measured_rim_ambiguous_upper_tom_ratio_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Kick] >= 308.72f &&
			upper_tom_body >= snare_body * 0.925f &&
			upper_tom_body >= snare_crack * 8.539f;
		const bool one_shot_measured_rim_kick_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.low_energy >= 0.49f &&
			onset <= 53.97f &&
			snapshot.drum_debug_trigger_scores[Ride] >= 16.53f;
		const bool one_shot_measured_rim_kick_low_crash_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			drum_level_[Kick] >= 0.85f &&
			drum_bands[Crash] <= 3.90f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 18.12f;
		const bool one_shot_measured_rim_kick_low_trigger_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Crash] <= 27.0f &&
			drum_bands[Kick] >= 85.0f &&
			snapshot.low_energy <= 0.50f &&
			drum_level_[Snare] <= 0.84f;
		const bool one_shot_measured_low_body_rim_snare_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			kick_body <= 5.807f &&
			drum_segment_bands[Kick] >= 6.769f;
		const bool one_shot_measured_rim_snare_high_crack_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snare_crack >= 46.829f &&
			snare_kick_shape_score_ratio >= 2.367f &&
			tom_kick_trigger_ratio <= 0.877f;
		const bool one_shot_measured_rim_ride_bright_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			drum_level_[Ride] > drum_level_[Rim] &&
			crash_hihat_level_ratio >= 1.0f &&
			kick_body <= 0.833f;
		const bool one_shot_measured_rim_snare_low_crash_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 26.982f &&
			snare_crack >= 18.371f &&
			tom_snare_trigger_ratio <= 0.837f;
		const bool one_shot_measured_rim_snare_bright_ride_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.high_energy >= 0.679f &&
			drum_segment_bands[Ride] <= 3.402f &&
			snapshot.drum_debug_trigger_scores[Ride] >= 12.932f &&
			drum_level_[Rim] <= 0.975f;
		const bool one_shot_measured_rim_snare_tom_band_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			snapshot.high_energy >= 0.617f &&
			drum_bands[Tom] >= 55.06f &&
			drum_level_[Tom] <= 0.001f &&
			tom_snare_total_band_ratio <= 0.806f;
		const bool one_shot_measured_rim_snare_dense_tom_band_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			drum_bands[Tom] >= 140.005f &&
			tom_body <= 47.647f &&
			tom_kick_trigger_ratio >= 0.709f &&
			tom_snare_trigger_ratio >= 0.840f;
		const bool one_shot_measured_rim_snare_tom_body_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			tom_body >= 83.865f &&
			tom_snare_body_ratio <= 1.029f &&
			tom_snare_level_ratio <= 0.28f &&
			tom_snare_segment_ratio >= 0.963f;
		const bool one_shot_measured_rim_snare_low_threshold_crack_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Kick] <= 26.737f &&
			snare_crack >= 37.10f &&
			snapshot.drum_debug_trigger_thresholds[Snare] <= 0.426f;
		const float measured_snare_kick_level_ratio =
			drum_level_[Snare] / (drum_level_[Kick] + 1.0e-9f);
		const bool one_shot_measured_rim_snare_low_kick_crash_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Crash] >= 19.876f &&
			snapshot.drum_debug_trigger_scores[Kick] <= 17.18f &&
			measured_snare_kick_level_ratio >= 898410000.0f;
		const bool one_shot_measured_rim_snare_low_kick_segment_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Crash] <= 19.876f &&
			measured_snare_kick_level_ratio >= 1000000000.0f &&
			snare_kick_segment_ratio >= 1.979f &&
			tom_kick_band_ratio <= 4.442f;
		const bool one_shot_measured_rim_snare_crash_level_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] >= 0.901f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 34.70f &&
			drum_level_[Snare] >= 0.973f;
		const bool one_shot_measured_low_rim_kick_body_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			crash_hihat_segment_ratio <= 0.453f &&
			drum_level_[Kick] >= 0.999f &&
			tom_body <= 66.217f;
		const bool one_shot_measured_rim_crash_body_ratio_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] >= 0.999f &&
			snare_kick_body_ratio >= 3.677f;
		const bool one_shot_measured_rim_snare_narrow_crash_band_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_bands[Crash] >= 9.516f &&
			drum_bands[Crash] <= 9.518f;
		const bool one_shot_measured_rim_ambiguous_ride_tom_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_scores[Crash] <= 21.004f &&
			drum_level_[Ride] >= 0.846f &&
			drum_bands[Tom] >= 32.19f;
		const bool one_shot_measured_high_snare_shape_rim_guard =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Snare &&
			drum_level_[Snare] >= 0.90f &&
			snapshot.high_energy >= 0.46f;
		const bool one_shot_measured_rim_guard_bypass_recovery =
			one_shot_measured_rim_snare_low_trigger_recovery ||
			one_shot_measured_rim_kick_low_trigger_recovery ||
			one_shot_measured_rim_snare_high_crack_recovery ||
			one_shot_measured_rim_ride_bright_recovery ||
			one_shot_measured_rim_snare_low_crash_recovery ||
			one_shot_measured_rim_snare_bright_ride_recovery ||
			one_shot_measured_rim_snare_tom_band_recovery ||
			one_shot_measured_rim_snare_dense_tom_band_recovery ||
			one_shot_measured_rim_snare_tom_body_recovery ||
			one_shot_measured_rim_snare_low_threshold_crack_recovery ||
			one_shot_measured_rim_snare_low_kick_crash_recovery ||
			one_shot_measured_rim_snare_low_kick_segment_recovery ||
			one_shot_measured_rim_snare_crash_level_recovery ||
			one_shot_measured_low_rim_kick_body_recovery ||
			one_shot_measured_rim_crash_body_ratio_recovery ||
			one_shot_measured_rim_snare_narrow_crash_band_recovery ||
			one_shot_measured_rim_ambiguous_ride_tom_recovery;
		const bool one_shot_measured_rim_recovery =
			one_shot_measured_rim_snare_onset_recovery ||
			one_shot_measured_rim_snare_low_trigger_recovery ||
			one_shot_measured_rim_snare_transient_recovery ||
			one_shot_measured_rim_tom_recovery ||
			one_shot_measured_low_band_rim_tom_recovery ||
			one_shot_measured_low_crash_rim_tom_recovery ||
			one_shot_measured_low_crash_body_rim_tom_recovery ||
			one_shot_measured_narrow_body_rim_tom_recovery ||
			one_shot_measured_rim_tom_trigger_recovery ||
			one_shot_measured_rim_tom_low_kick_trigger_recovery ||
			one_shot_measured_rim_tom_upper_body_recovery ||
			one_shot_measured_rim_tom_shape_ratio_recovery ||
			one_shot_measured_rim_tom_low_ride_kick_trigger_recovery ||
			one_shot_measured_rim_ambiguous_recovery ||
			one_shot_measured_rim_ambiguous_ride_ratio_recovery ||
			one_shot_measured_rim_ambiguous_shape_recovery ||
			one_shot_measured_rim_ambiguous_upper_tom_ratio_recovery ||
			one_shot_measured_rim_kick_recovery ||
			one_shot_measured_rim_kick_low_crash_recovery ||
			one_shot_measured_rim_kick_low_trigger_recovery ||
			one_shot_measured_low_body_rim_snare_recovery ||
			one_shot_measured_rim_snare_high_crack_recovery ||
			one_shot_measured_rim_ride_bright_recovery ||
			one_shot_measured_rim_snare_low_crash_recovery ||
			one_shot_measured_rim_snare_bright_ride_recovery ||
			one_shot_measured_rim_snare_tom_band_recovery ||
			one_shot_measured_rim_snare_dense_tom_band_recovery ||
			one_shot_measured_rim_snare_tom_body_recovery ||
			one_shot_measured_rim_snare_low_threshold_crack_recovery ||
			one_shot_measured_rim_snare_low_kick_crash_recovery ||
			one_shot_measured_rim_snare_low_kick_segment_recovery ||
			one_shot_measured_rim_snare_crash_level_recovery ||
			one_shot_measured_low_rim_kick_body_recovery ||
			one_shot_measured_rim_crash_body_ratio_recovery ||
			one_shot_measured_rim_snare_narrow_crash_band_recovery ||
			one_shot_measured_rim_ambiguous_ride_tom_recovery;
		if (one_shot_measured_rim_recovery &&
		    (!one_shot_measured_high_snare_shape_rim_guard ||
		     one_shot_measured_rim_guard_bypass_recovery))
			promote_drum_primary(Rim, 0.88f);

		const float final_tom_kick_near_tie_ratio =
			drum_level_[Tom] / (drum_level_[Kick] + 1.0e-6f);
		const float final_snare_kick_shape_ratio =
			body_shape_scores[1] / (body_shape_scores[0] + 1.0e-6f);
		const float final_snare_kick_band_ratio =
			drum_bands[Snare] / (drum_bands[Kick] + 1.0e-6f);
		const float final_tom_snare_trigger_ratio =
			snapshot.drum_debug_trigger_scores[Tom] /
			(snapshot.drum_debug_trigger_scores[Snare] + 1.0e-6f);
		const float final_upper_tom_snare_body_ratio =
			upper_tom_body / (snare_body + 1.0e-6f);
		const float final_upper_tom_snare_crack_ratio =
			upper_tom_body / (snare_crack + 1.0e-6f);
		const bool one_shot_measured_tom_rim_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Tom] > 0.30f &&
			((final_tom_kick_near_tie_ratio <= 1.001f &&
			  final_upper_tom_snare_body_ratio >= 0.774f) ||
			 (snapshot.high_energy <= 0.26f &&
			  drum_level_[Rim] > 0.30f &&
			  rim_shape_score >= 9.86f));
		const bool one_shot_measured_tom_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Rim] <= 0.30f &&
			tom_body >= kick_body * 1.40f &&
			tom_body >= snare_body * 1.10f &&
			snapshot.high_energy <= 0.14f;
		const bool one_shot_measured_low_tom_from_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_shape_supported[Tom] &&
			hihat_rim_segment_ratio <= 0.17f &&
			snapshot.low_energy >= 0.71f &&
			tom_kick_level_ratio <= 0.876f;
		const bool one_shot_measured_narrow_band_tom_from_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Kick] > 0.30f &&
			((snapshot.high_energy <= 0.17f &&
			  tom_kick_band_ratio >= 3.127f &&
			  tom_kick_band_ratio <= 3.155f) ||
			 (drum_level_[Kick] <= 0.987f &&
			  tom_kick_shape_score_ratio <= 0.482f));
		const bool one_shot_measured_tom_no_kick_snare_steal_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Tom &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Snare] > 0.30f &&
			drum_level_[Kick] <= 0.001f &&
			upper_tom_body >= 78.0f &&
			drum_bands[Ride] <= 3.74f &&
			snare_kick_trigger_ratio <= 1.209f;
		const bool one_shot_measured_tom_from_snare_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Snare] > drum_level_[Tom] &&
			drum_bands[Ride] <= 0.002f &&
			drum_segment_bands[Rim] >= 8.135f;
		const bool one_shot_measured_high_ride_tom_snare_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_bands[Ride] >= 16.28f &&
			upper_tom_body >= snare_crack * 12.476f;
		const bool one_shot_measured_quiet_crash_tom_from_snare_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Snare] >= 0.987f &&
			drum_bands[Crash] <= 0.191f;
		const bool one_shot_measured_ratio_tom_from_snare_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Snare] > 0.30f &&
			hihat_rim_trigger_ratio <= 0.913f &&
			snare_kick_level_ratio >= 1.022f &&
			tom_kick_segment_ratio <= 1.666f;
		const bool one_shot_measured_ride_rim_saturated_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Kick &&
			drum_level_[Ride] > 0.30f &&
			tom_body <= 3.5f &&
			snare_body <= 3.0f;
		const bool one_shot_measured_ride_hihat_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] >= 0.88f &&
			drum_bands[Crash] <= 14.65f &&
			drum_segment_bands[Crash] >= 14.09f;
		const bool one_shot_measured_ride_from_hihat_quiet_low_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Ride] > 0.30f &&
			drum_level_[HiHat] > 0.30f &&
			kick_body <= 0.848f &&
			snapshot.low_energy <= 0.038f;
		const bool one_shot_measured_snare_rim_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.97f &&
			drum_level_[Rim] >= 0.99f &&
			drum_segment_bands[Rim] >= 6.99f &&
			final_tom_snare_trigger_ratio <= 0.80f;
		const bool one_shot_measured_snare_rim_saturation_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] > 0.30f &&
			drum_level_[Rim] >= 0.986f &&
			drum_segment_bands[Rim] >= 16.146f &&
			hihat_rim_trigger_ratio <= 1.077f &&
			snare_crack >= 9.50f &&
			(body_shape == Snare || snare_shape) &&
			snapshot.mid_energy >= 0.24f &&
			final_tom_snare_trigger_ratio <= 0.95f;
		const bool one_shot_measured_snare_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.77f &&
			drum_level_[Kick] >= 0.90f &&
			drum_segment_bands[Crash] >= 1.25f &&
			final_snare_kick_shape_ratio <= 0.68f &&
			final_tom_snare_trigger_ratio <= 0.872f;
		const bool one_shot_measured_snare_ambiguous_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape == Kick &&
			drum_level_[Snare] >= 0.98f &&
			drum_segment_bands[Snare] >= 12.89f;
		const bool one_shot_measured_snare_tom_tie_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.985f &&
			drum_level_[Tom] >= 0.985f;
		const bool one_shot_measured_snare_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			!one_shot_measured_tom_from_snare_primary_recovery &&
			drum_level_[Snare] > 0.30f &&
			drum_level_[Tom] > 0.30f &&
			snapshot.low_energy >= 0.445f &&
			snare_kick_shape_score_ratio >= 1.043f &&
			snare_kick_trigger_ratio <= 0.866f;
		const bool one_shot_measured_low_trigger_snare_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			kick_body >= 72.12f &&
			tom_body <= 181.0f &&
			snare_body >= 70.0f &&
			snare_body >= kick_body * 0.68f &&
			snare_crack >= snare_body * 0.070f &&
			snapshot.drum_debug_trigger_scores[Tom] <= 30.66f;
		const bool one_shot_measured_high_band_snare_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_bands[Snare] >= 202.549f &&
			drum_segment_bands[Crash] <= 0.889f;
		const bool one_shot_measured_crash_kick_tie_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] >= 0.98f &&
			drum_level_[Kick] >= 0.96f;
		const bool one_shot_measured_crash_ride_tie_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] >= 0.98f &&
			drum_level_[Ride] >= 1.0f;
		const bool one_shot_measured_crash_from_hihat_band_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] > 0.30f &&
			drum_level_[HiHat] >= 0.901f &&
			snapshot.high_energy <= 0.627f &&
			drum_bands[HiHat] >= 55.532f;
		const bool one_shot_measured_crash_hihat_rim_shape_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] > 0.30f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 26.681f &&
			hihat_rim_shape_score_ratio >= 1.774f &&
			drum_segment_bands[Rim] >= 8.898f;
		const bool one_shot_measured_crash_rim_level_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Crash] > 0.30f &&
			drum_level_[Rim] > 0.30f &&
			snapshot.high_energy >= 0.50f &&
			crash_hihat_level_ratio >= 0.973f &&
			hihat_rim_level_ratio <= 0.962f &&
			final_snare_kick_band_ratio <= 0.778f;
		const bool one_shot_measured_hihat_ambiguous_snare_shape_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_bands[Snare] >= 24.80f &&
			body_shape_scores[1] <= 13.83f;
		const bool one_shot_measured_hihat_rim_low_kick_body_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_level_[Rim] > drum_level_[HiHat] &&
			kick_body <= 0.96f &&
			tom_body >= 3.73f;
		const bool one_shot_measured_hihat_rim_upper_tom_ratio_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_level_[Rim] > drum_level_[HiHat] &&
			final_upper_tom_snare_body_ratio >= 1.145f &&
			final_upper_tom_snare_crack_ratio <= 1.797f;
		const bool one_shot_measured_hihat_rim_tie_quiet_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_level_[Rim] > 0.30f &&
			hihat_rim_level_ratio >= 1.0f &&
			hihat_rim_level_ratio <= 1.015f &&
			kick_body <= 5.905f;
		const bool one_shot_measured_hihat_saturated_rim_band_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_level_[Rim] >= 0.99f &&
			drum_bands[Crash] >= 14.11f &&
			tom_snare_band_ratio >= 0.451f;
		const bool one_shot_measured_kick_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			((final_snare_kick_band_ratio <= 0.111f &&
			  tom_kick_level_ratio >= 1.02f) ||
			 (tom_snare_body_ratio >= 2.519f &&
			  tom_snare_shape_score_ratio <= 2.373f) ||
			 (snapshot.high_energy <= 0.02f &&
			  snapshot.drum_debug_trigger_thresholds[Tom] <= 0.43f) ||
			 (drum_bands[Kick] >= 0.18f &&
			  snare_kick_trigger_ratio <= 0.08f &&
			  drum_level_[Snare] <= 0.87f) ||
			 (drum_level_[Kick] > 0.30f &&
			  snare_kick_trigger_ratio <= 0.049f &&
			  tom_kick_trigger_ratio >= 0.041f) ||
			 (body_shape_scores[0] >= 406.43f &&
			  tom_kick_shape_score_ratio >= 0.866f));
		const bool one_shot_measured_low_trigger_kick_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			tom_body >= 203.72f &&
			snapshot.drum_debug_trigger_scores[Tom] <= 26.56f;
		const bool measured_low_energy_kick_tom_primary_recovery =
			drum_detection_enabled && named_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Tom] > drum_level_[Kick] &&
			snapshot.low_energy >= 0.63f &&
			final_tom_kick_near_tie_ratio >= 1.057f &&
			snapshot.drum_debug_trigger_scores[Tom] >= 2.39f;
		const bool one_shot_measured_kick_snare_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			((drum_bands[Ride] <= 1.67f &&
			  drum_level_[Snare] >= 0.99f &&
			  upper_tom_body >= 99.955f) ||
			 (snapshot.drum_debug_trigger_scores[Kick] <= 80.83f &&
			  tom_body >= 335.98f) ||
			 (snare_kick_body_ratio >= 2.168f &&
			  snare_kick_shape_score_ratio <= 1.165f) ||
			 (body_shape == Tom &&
			  kick_body >= 193.22f));
		const bool one_shot_measured_dense_body_kick_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_bands[Kick] <= 0.063f &&
			drum_bands[Tom] >= 0.193f &&
			tom_body >= 30.204f;
		if (one_shot_measured_tom_rim_primary_recovery ||
		    one_shot_measured_tom_kick_primary_recovery ||
		    one_shot_measured_low_tom_from_kick_primary_recovery ||
		    one_shot_measured_tom_no_kick_snare_steal_primary_recovery ||
		    one_shot_measured_tom_from_snare_primary_recovery ||
		    one_shot_measured_high_ride_tom_snare_primary_recovery)
			promote_drum_primary(Tom, 0.90f);
		if (one_shot_measured_ride_rim_saturated_recovery)
			promote_drum_primary(Ride, 0.90f);
		if (one_shot_measured_ride_hihat_primary_recovery)
			promote_drum_primary(Ride, 0.90f);
		if (one_shot_measured_crash_kick_tie_primary_recovery ||
		    one_shot_measured_crash_ride_tie_primary_recovery)
			promote_drum_primary(Crash, 0.90f);
		const float final_crash_hihat_level_ratio =
			drum_level_[Crash] / (drum_level_[HiHat] + 1.0e-6f);
		const bool one_shot_measured_hihat_ambiguous_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			final_crash_hihat_level_ratio >= 1.005f &&
			final_crash_hihat_level_ratio <= 1.015f &&
			drum_bands[Ride] >= 12.038f;
		const bool one_shot_measured_hihat_ride_tie_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			ride_hihat_level_ratio >= 0.993f &&
			body_shape_scores[1] <= 3.646f &&
			drum_bands[Kick] >= 0.05f;
		if (one_shot_measured_hihat_ambiguous_snare_shape_primary_recovery ||
		    one_shot_measured_hihat_rim_low_kick_body_primary_recovery ||
		    one_shot_measured_hihat_rim_upper_tom_ratio_primary_recovery ||
		    one_shot_measured_hihat_rim_tie_quiet_kick_primary_recovery ||
		    one_shot_measured_hihat_saturated_rim_band_primary_recovery ||
		    one_shot_measured_hihat_ambiguous_primary_recovery ||
		    one_shot_measured_hihat_ride_tie_primary_recovery)
			promote_drum_primary(HiHat, 0.90f);
		if (one_shot_measured_ride_from_hihat_quiet_low_primary_recovery)
			promote_drum_primary(Ride, 0.90f);
		const bool one_shot_measured_rim_high_kick_trigger_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			hihat_rim_trigger_ratio <= 0.86f &&
			snapshot.drum_debug_trigger_scores[Kick] >= 1406.45f;
		if (one_shot_measured_rim_high_kick_trigger_primary_recovery)
			promote_drum_primary(Rim, 0.90f);
		if (one_shot_measured_crash_from_hihat_band_primary_recovery ||
		    one_shot_measured_crash_hihat_rim_shape_primary_recovery ||
		    one_shot_measured_crash_rim_level_primary_recovery)
			promote_drum_primary(Crash, 0.90f);
		if (one_shot_measured_snare_rim_primary_recovery ||
		    one_shot_measured_snare_rim_saturation_primary_recovery ||
		    one_shot_measured_snare_kick_primary_recovery ||
		    one_shot_measured_snare_ambiguous_primary_recovery ||
		    one_shot_measured_snare_tom_tie_primary_recovery ||
		    one_shot_measured_snare_from_tom_primary_recovery ||
		    one_shot_measured_low_trigger_snare_from_tom_primary_recovery ||
		    one_shot_measured_high_band_snare_from_tom_primary_recovery)
			promote_drum_primary(Snare, 0.90f);
		const bool one_shot_measured_quiet_crash_saturated_snare_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Snare] >= 0.999f &&
			drum_level_[Rim] <= 0.30f &&
			snapshot.mid_energy >= snapshot.low_energy * 1.20f &&
			drum_bands[Crash] <= 0.191f;
		if (one_shot_measured_quiet_crash_tom_from_snare_primary_recovery ||
		    one_shot_measured_quiet_crash_saturated_snare_tom_primary_recovery ||
		    one_shot_measured_ratio_tom_from_snare_primary_recovery)
			promote_drum_primary(Tom, 0.90f);
		const bool one_shot_measured_late_kick_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			hihat_rim_segment_ratio <= 0.0702f &&
			drum_level_[Tom] >= 0.996f &&
			tom_snare_total_band_ratio <= 2.281f;
		if (one_shot_measured_kick_tom_primary_recovery ||
		    one_shot_measured_low_trigger_kick_from_tom_primary_recovery ||
		    measured_low_energy_kick_tom_primary_recovery ||
		    one_shot_measured_late_kick_tom_primary_recovery ||
		    one_shot_measured_kick_snare_primary_recovery ||
		    one_shot_measured_dense_body_kick_from_tom_primary_recovery)
			promote_drum_primary(Kick, 0.90f);
		const float post_primary_tom_kick_level_ratio =
			drum_level_[Tom] / (drum_level_[Kick] + 1.0e-6f);
		const bool measured_low_body_kick_tom_primary_recovery =
			drum_detection_enabled && named_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Tom] > drum_level_[Kick] &&
			snapshot.low_energy >= 0.59f &&
			post_primary_tom_kick_level_ratio >= 1.022f &&
			snapshot.drum_debug_trigger_scores[Tom] >= 2.33f;
		const bool one_shot_measured_low_body_kick_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Tom] > drum_level_[Kick] &&
			snapshot.low_energy >= 0.56f &&
			snapshot.drum_debug_trigger_scores[Kick] >= 404.0f &&
			snapshot.drum_debug_trigger_scores[Ride] >= 8.20f;
		const bool one_shot_measured_quiet_high_kick_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Tom] > drum_level_[Kick] &&
			snapshot.high_energy <= 0.04f &&
			drum_bands[Kick] <= 0.14f &&
			kick_body >= 14.12f;
		const bool one_shot_measured_low_body_ratio_kick_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Kick] > 0.30f &&
			drum_level_[Tom] > drum_level_[Kick] &&
			snapshot.low_energy >= 0.91f &&
			tom_kick_body_ratio >= 1.471f;
		if (measured_low_body_kick_tom_primary_recovery ||
		    one_shot_measured_low_body_kick_tom_primary_recovery ||
		    one_shot_measured_quiet_high_kick_tom_primary_recovery ||
		    one_shot_measured_low_body_ratio_kick_tom_primary_recovery)
			promote_drum_primary(Kick, 0.90f);
		const bool one_shot_measured_high_rim_from_tom_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[Rim] > 0.30f &&
			drum_level_[Tom] >= 0.999f &&
			snapshot.high_energy >= 0.369f;
		if (one_shot_measured_high_rim_from_tom_primary_recovery)
			promote_drum_primary(Rim, 0.90f);
		const bool one_shot_measured_kick_saturated_rim_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			body_shape_scores[0] >= 58.682f &&
			drum_level_[Rim] >= 1.0f;
		if (one_shot_measured_kick_saturated_rim_primary_recovery)
			promote_drum_primary(Kick, 0.90f);
		const bool one_shot_measured_hihat_low_crash_trigger_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_level_[HiHat] > 0.30f &&
			drum_level_[Tom] > 0.30f &&
			crash_hihat_level_ratio >= 0.97f &&
			snapshot.drum_debug_trigger_scores[Crash] <= 5.317f;
		if (one_shot_measured_hihat_low_crash_trigger_primary_recovery)
			promote_drum_primary(HiHat, 0.90f);
		const bool one_shot_measured_late_snare_tom_level_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			snapshot.drum_debug_trigger_thresholds[Snare] <= 0.426f &&
			tom_snare_level_ratio >= 1.059f &&
			tom_snare_segment_ratio >= 1.343f;
		if (one_shot_measured_late_snare_tom_level_primary_recovery)
			promote_drum_primary(Snare, 0.90f);
		const bool one_shot_measured_late_snare_rim_low_kick_primary_recovery =
			drum_detection_enabled && one_shot_drum_source &&
			drum_bands[Crash] <= 8.609f &&
			drum_level_[Rim] >= 0.897f &&
			drum_level_[Snare] <= 0.29f &&
			snare_kick_segment_ratio >= 1.71f;
		if (one_shot_measured_late_snare_rim_low_kick_primary_recovery)
			promote_drum_primary(Snare, 0.90f);

		if (one_shot_measured_rim_snare_high_crack_recovery ||
		    one_shot_measured_rim_ride_bright_recovery ||
		    one_shot_measured_rim_snare_low_crash_recovery ||
		    one_shot_measured_rim_snare_bright_ride_recovery ||
		    one_shot_measured_rim_snare_tom_band_recovery ||
		    one_shot_measured_rim_snare_dense_tom_band_recovery ||
		    one_shot_measured_rim_snare_tom_body_recovery ||
		    one_shot_measured_rim_snare_low_threshold_crack_recovery ||
		    one_shot_measured_rim_snare_low_kick_crash_recovery ||
		    one_shot_measured_rim_snare_low_kick_segment_recovery ||
		    one_shot_measured_rim_snare_crash_level_recovery ||
		    one_shot_measured_low_rim_kick_body_recovery ||
		    one_shot_measured_rim_crash_body_ratio_recovery ||
		    one_shot_measured_rim_snare_narrow_crash_band_recovery ||
		    one_shot_measured_rim_ambiguous_ride_tom_recovery)
			promote_drum_primary(Rim, 0.90f);
		if (one_shot_measured_narrow_band_tom_from_kick_primary_recovery)
			promote_drum_primary(Tom, 0.90f);

		const bool generated_gm_orchestra_tom_primary_recovery =
			drum_detection_enabled && generated_gm_drum_source &&
			drum_level_[Tom] > 0.30f &&
			drum_shape_supported[Tom] &&
			body_shape == Tom &&
			tom_body >= 100.0f &&
			tom_body >= snare_body * 1.42f &&
			upper_tom_body >= 48.0f &&
			snapshot.drum_debug_trigger_scores[Tom] >= 8000.0f;
		if (generated_gm_orchestra_tom_primary_recovery)
			promote_drum_primary(Tom, 0.90f);

		const bool measured_snare_crack_tom_bleed =
			drum_detection_enabled &&
			drum_level_[Tom] > 0.30f &&
			drum_level_[Snare] >= 0.70f &&
			snare_body > 1.0e-6f &&
			snare_crack >= snare_body * 0.18f &&
			tom_body <= snare_body * 1.70f &&
			!generated_gm_orchestra_tom_primary_recovery;
		if (measured_snare_crack_tom_bleed)
			cap_drum_level(Tom, 0.28f);

	const bool onset_tempo_event =
		drum_detection_enabled && rms > kSilenceRms && drum_transient &&
		(had_previous_audio ? onset >= 1.25f : true);
	update_tempo(tempo_event || onset_tempo_event, interval_seconds, rms);
	snapshot.estimated_bpm = estimated_bpm_;
	snapshot.bpm_confidence = bpm_confidence_;

	int mixed_bass_pitch_class = -1;
	ChordResult raw_keyboard_chord;
	ChordResult raw_guitar_chord;
	ChordResult raw_other_chord;
	ChordResult raw_global_chord;
	ChordResult smoothed_global_chord;
	NoteGrid guitar_chord_detection_grid;
	FullMixOwnership full_mix_ownership;
	const bool monophonic_other_source =
		input_mode == AnalysisInputMode::IsolatedOther && is_monophonic_other_track_source(resolved_source_name);
	const bool synthetic_other_source_hint =
		mixed_source &&
		(contains_case_insensitive(resolved_source_name, "synth") ||
		 contains_case_insensitive(resolved_source_name, "other"));
	const int other_max_notes = monophonic_other_source ? 1 : (mixed_source ? 12 : 12);
	if (mixed_source) {
		std::array<float, kNoteProbeCount> current_full_mix_note_levels = {};
		full_mix_ownership = build_full_mix_ownership(note_powers, detection_note_powers, rms,
							      previous_full_mix_note_levels_,
							      current_full_mix_note_levels,
							      full_mix_source_hint_mode);
		stabilize_full_mix_vocal_ownership(full_mix_ownership, tracked_vocal_midi_,
						   pending_vocal_midi_, pending_vocal_hits_,
						   tracked_vocal_misses_, tracked_vocal_score_);
		stabilize_sparse_full_mix_other_ownership(full_mix_ownership,
							  full_mix_other_ownership_tracking_);
		if (mixed_synth_source_hint)
			restore_full_mix_named_synth_other_from_keyboard(full_mix_ownership);
		snapshot.full_mix_debug_candidate_count = full_mix_ownership.debug_candidate_count;
		snapshot.full_mix_debug_candidates = full_mix_ownership.debug_candidates;
		previous_full_mix_note_levels_ = current_full_mix_note_levels;
		update_note_tracking_from_levels(full_mix_note_tracking_, full_mix_ownership.global_note_levels,
						 interval_seconds, kNoteAttackConfirmFrames,
						 kMixedNoteEnvelopeImmediateConfirmFloor,
						 kAnalyticalChordNoteReleaseSeconds,
						 kAnalyticalChordNoteVisibleFloor);
		set_note_grid_from_candidates(snapshot.ambiguous_notes, full_mix_ownership.ambiguous_candidates, rms, 12);
	} else {
		tracked_vocal_midi_ = -1;
		pending_vocal_midi_ = -1;
		pending_vocal_hits_ = 0;
		tracked_vocal_misses_ = 0;
		tracked_vocal_score_ = 0.0f;
		for (NoteTrackingState &note : full_mix_other_ownership_tracking_)
			note = {};
		clear_note_grid(snapshot.ambiguous_notes);
	}

	if (input_mode == AnalysisInputMode::FullMix || input_mode == AnalysisInputMode::IsolatedBass) {
		const bool isolated_bass = input_mode == AnalysisInputMode::IsolatedBass;
		const bool upright_bass_source = contains_case_insensitive(resolved_source_name, "double") ||
						 contains_case_insensitive(resolved_source_name, "upright") ||
						 contains_case_insensitive(resolved_source_name, "contrabass");
		const int bass_max_midi = isolated_bass ? kBassMaxMidi : kDefaultBassMaxMidi;
		const bool include_bass_harmonics = true;
		const bool isolated_bass_harmonic_support = isolated_bass && !upright_bass_source;
		const RangeResult spectral_bass_note = dominant_bass_note(detection_note_powers, kBassMinMidi,
									  bass_max_midi,
									  include_bass_harmonics,
									  isolated_bass_harmonic_support);
		RangeResult bass_note = spectral_bass_note;
		if (isolated_bass) {
			const RangeResult periodic_note =
				periodic_bass_note(samples, usable, mean, sample_rate_, note_powers,
						   kBassMinMidi, bass_max_midi,
						   isolated_bass_harmonic_support);
			snapshot.bass_debug_periodic_midi = periodic_note.midi;
			snapshot.bass_debug_periodic_confidence = periodic_note.confidence;
			snapshot.bass_debug_periodic_score = periodic_note.score;
			const int periodic_replacement_max_midi =
				upright_bass_source ? kIsolatedBassPeriodicReplacementMaxMidi : bass_max_midi;
			bass_note = choose_isolated_bass_note(bass_note, periodic_note,
							      periodic_replacement_max_midi);
		}
		snapshot.bass_debug_spectral_midi = spectral_bass_note.midi;
		snapshot.bass_debug_spectral_confidence = spectral_bass_note.confidence;
		snapshot.bass_debug_spectral_score = spectral_bass_note.score;
		const RangeResult broad_bass_note = isolated_bass ?
							    bass_note :
							    dominant_bass_note(detection_note_powers, kBassMinMidi,
									       kBassMaxMidi, include_bass_harmonics);
		const RangeResult upper_bass_note = isolated_bass ?
							    RangeResult{} :
							    dominant_bass_note(detection_note_powers,
									       kDefaultBassMaxMidi + 1,
									       kFullMixCleanHighSynthBassMaxMidi,
									       false);
		bool mixed_bass_supported =
			isolated_bass || full_mix_bass_supported(detection_note_powers, bass_note, broad_bass_note);
		if (!isolated_bass && !mixed_bass_supported &&
		    full_mix_upper_bass_supported(detection_note_powers, upper_bass_note, broad_bass_note)) {
			bass_note = upper_bass_note;
			mixed_bass_supported = true;
		}
		if (!isolated_bass && !mixed_bass_supported) {
			const RangeResult recovered_bass =
				recover_full_mix_bass_from_debug(full_mix_ownership, detection_note_powers);
			if (recovered_bass.midi >= kFirstMidi) {
				bass_note = recovered_bass;
				mixed_bass_supported = true;
			}
		}
		if (!isolated_bass && mixed_bass_supported &&
		    full_mix_bass_shadowed_by_keyboard_alias(full_mix_ownership, bass_note))
			mixed_bass_supported = false;
		if (mixed_bass_supported) {
			RangeResult displayed_bass = bass_note;
			if (isolated_bass) {
				tracked_bass_midi_ = bass_note.midi;
				tracked_bass_confidence_ = bass_note.confidence;
				tracked_bass_score_ = bass_note.score;
				pending_bass_midi_ = -1;
				pending_bass_hits_ = 0;
				tracked_bass_misses_ = 0;
			} else if (tracked_bass_midi_ < 0) {
				tracked_bass_midi_ = bass_note.midi;
				tracked_bass_confidence_ = bass_note.confidence;
				tracked_bass_score_ = bass_note.score;
				tracked_bass_misses_ = 0;
			} else if (bass_note.midi == tracked_bass_midi_) {
				tracked_bass_confidence_ =
					std::max(tracked_bass_confidence_ * 0.80f, bass_note.confidence);
				tracked_bass_score_ = std::max(tracked_bass_score_ * 0.80f, bass_note.score);
				pending_bass_midi_ = -1;
				pending_bass_hits_ = 0;
				tracked_bass_misses_ = 0;
			} else {
				if (pending_bass_midi_ == bass_note.midi)
					++pending_bass_hits_;
				else {
					pending_bass_midi_ = bass_note.midi;
					pending_bass_hits_ = 1;
				}

				const bool strong_replacement =
					bass_note.confidence >= tracked_bass_confidence_ + 0.22f &&
					bass_note.score >= tracked_bass_score_ * 1.35f;
				if (pending_bass_hits_ >= 2 || strong_replacement) {
					tracked_bass_midi_ = bass_note.midi;
					tracked_bass_confidence_ = bass_note.confidence;
					tracked_bass_score_ = bass_note.score;
					pending_bass_midi_ = -1;
					pending_bass_hits_ = 0;
					tracked_bass_misses_ = 0;
				} else {
					displayed_bass.midi = tracked_bass_midi_;
					displayed_bass.confidence = tracked_bass_confidence_ * 0.86f;
					displayed_bass.score = tracked_bass_score_ * 0.86f;
					tracked_bass_confidence_ = displayed_bass.confidence;
					tracked_bass_score_ = displayed_bass.score;
					tracked_bass_misses_ = 0;
				}
			}

			snapshot.bass_debug_displayed_midi = displayed_bass.midi;
			snapshot.bass_debug_displayed_confidence = displayed_bass.confidence;
			snapshot.bass_debug_displayed_score = displayed_bass.score;
			set_single_note_grid(snapshot.bass_notes, snapshot.bass, displayed_bass, bass_energy, rms);
			if (displayed_bass.midi >= 0 && snapshot.bass.confidence > 0.0f) {
				if (mixed_source) {
					suppress_full_mix_bass_duplicate_ownership(full_mix_ownership,
										 displayed_bass.midi);
					restore_full_mix_low_guitar_from_bass(full_mix_ownership,
									      detection_note_powers,
									      displayed_bass.midi);
					restore_full_mix_low_keyboard_from_bass(full_mix_ownership,
										detection_note_powers,
										displayed_bass.midi);
					restore_full_mix_low_other_from_bass(full_mix_ownership,
									     detection_note_powers,
									     displayed_bass.midi);
					if (synthetic_other_source_hint)
						restore_full_mix_low_synth_other_from_bass(full_mix_ownership,
											 detection_note_powers,
											 displayed_bass.midi,
											 displayed_bass.confidence,
											 displayed_bass.score);
					suppress_full_mix_low_bass_harmonic_aliases(full_mix_ownership,
										    detection_note_powers,
										    displayed_bass.midi,
										    synthetic_other_source_hint);
				}
				mixed_bass_pitch_class = ((displayed_bass.midi % 12) + 12) % 12;
			}
		} else {
			if (!isolated_bass && tracked_bass_midi_ >= 0 && tracked_bass_misses_ < 2) {
				RangeResult displayed_bass;
				displayed_bass.midi = tracked_bass_midi_;
				displayed_bass.confidence = tracked_bass_confidence_ * 0.72f;
				displayed_bass.score = tracked_bass_score_ * 0.72f;
				tracked_bass_confidence_ = displayed_bass.confidence;
				tracked_bass_score_ = displayed_bass.score;
				++tracked_bass_misses_;
				snapshot.bass_debug_displayed_midi = displayed_bass.midi;
				snapshot.bass_debug_displayed_confidence = displayed_bass.confidence;
				snapshot.bass_debug_displayed_score = displayed_bass.score;
				set_single_note_grid(snapshot.bass_notes, snapshot.bass, displayed_bass, bass_energy, rms);
				if (displayed_bass.midi >= 0 && snapshot.bass.confidence > 0.0f) {
					if (mixed_source) {
						suppress_full_mix_bass_duplicate_ownership(full_mix_ownership,
											 displayed_bass.midi);
						restore_full_mix_low_guitar_from_bass(full_mix_ownership,
										      detection_note_powers,
										      displayed_bass.midi);
						restore_full_mix_low_keyboard_from_bass(full_mix_ownership,
											detection_note_powers,
											displayed_bass.midi);
						restore_full_mix_low_other_from_bass(full_mix_ownership,
										    detection_note_powers,
										    displayed_bass.midi);
						if (synthetic_other_source_hint)
							restore_full_mix_low_synth_other_from_bass(full_mix_ownership,
												 detection_note_powers,
												 displayed_bass.midi,
												 displayed_bass.confidence,
												 displayed_bass.score);
						suppress_full_mix_low_bass_harmonic_aliases(full_mix_ownership,
											    detection_note_powers,
											    displayed_bass.midi,
											    synthetic_other_source_hint);
					}
					mixed_bass_pitch_class = ((displayed_bass.midi % 12) + 12) % 12;
				}
			} else {
				tracked_bass_midi_ = -1;
				pending_bass_midi_ = -1;
				pending_bass_hits_ = 0;
				tracked_bass_misses_ = 0;
				tracked_bass_confidence_ = 0.0f;
				tracked_bass_score_ = 0.0f;
				clear_note_grid(snapshot.bass_notes);
				copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
				snapshot.bass.confidence = 0.0f;
			}
		}
	} else {
		tracked_bass_midi_ = -1;
		pending_bass_midi_ = -1;
		pending_bass_hits_ = 0;
		tracked_bass_misses_ = 0;
		tracked_bass_confidence_ = 0.0f;
		tracked_bass_score_ = 0.0f;
		clear_note_grid(snapshot.bass_notes);
		copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
		snapshot.bass.confidence = 0.0f;
	}

	if (mixed_source) {
		const bool strong_bass_hint = mixed_bass_pitch_class >= 0 && snapshot.bass.confidence >= 0.32f;
		const ChordResult keyboard_global_hint =
			detect_chord(candidate_chroma(full_mix_ownership.keyboard_candidates), -1, false);
		auto parsed_primary_chord = [](const ChordResult &chord, ParsedRootChord &parsed) {
			if (!valid_chord_result(chord))
				return false;
			const char *label_end = std::strchr(chord.label, '=');
			const std::size_t label_len =
				label_end ? static_cast<std::size_t>(label_end - chord.label) :
					    std::strlen(chord.label);
			return parse_root_chord_component(chord.label, label_len, parsed);
		};
		auto prefer_keyboard_same_root_quality = [&](ChordResult &chord) {
			ParsedRootChord current;
			ParsedRootChord keyboard;
			if (!parsed_primary_chord(chord, current) ||
			    !parsed_primary_chord(keyboard_global_hint, keyboard))
				return;
			const bool current_major_minor =
				current.quality == RootChordQuality::Major || current.quality == RootChordQuality::Minor;
			const bool keyboard_major_minor =
				keyboard.quality == RootChordQuality::Major || keyboard.quality == RootChordQuality::Minor;
			if (current.root == keyboard.root && current_major_minor && keyboard_major_minor &&
			    current.quality != keyboard.quality)
				chord = keyboard_global_hint;
		};
		auto prefer_major_when_both_thirds_present = [&](ChordResult &chord,
							 const std::array<float, 12> &chroma) {
			ParsedRootChord current;
			if (!parsed_primary_chord(chord, current) || current.quality != RootChordQuality::Minor)
				return;
			const int root = current.root;
			const float root_level = chroma[root];
			const float minor_third = chroma[(root + 3) % 12];
			const float major_third = chroma[(root + 4) % 12];
			const float fifth = chroma[(root + 7) % 12];
			if (root_level < 0.20f || fifth < 0.20f || major_third < 0.20f ||
			    major_third < minor_third * 0.35f)
				return;
			chord.root = root;
			chord.tones.fill(false);
			chord.tones[root] = true;
			chord.tones[(root + 4) % 12] = true;
			chord.tones[(root + 7) % 12] = true;
			chord.confidence = std::max(chord.confidence, 0.40f);
			chord.uncertain = false;
			std::snprintf(chord.label, sizeof(chord.label), "%s", note_name(root));
		};
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
		prefer_keyboard_same_root_quality(raw_global_chord);
		prefer_major_when_both_thirds_present(raw_global_chord, full_mix_ownership.global_chroma);

		const std::array<float, 12> smoothed_global_chroma = tracked_note_chroma(full_mix_note_tracking_);
		smoothed_global_chord = detect_chord(smoothed_global_chroma, -1, false);
		if (strong_bass_hint) {
			const ChordResult smoothed_bass_hint_chord =
				detect_chord(smoothed_global_chroma, mixed_bass_pitch_class, false);
			if (valid_chord_result(smoothed_bass_hint_chord) &&
			    !valid_chord_result(smoothed_global_chord))
				smoothed_global_chord = smoothed_bass_hint_chord;
		}
		prefer_keyboard_same_root_quality(smoothed_global_chord);
		prefer_major_when_both_thirds_present(smoothed_global_chord, smoothed_global_chroma);
	}

	auto process_keyboard = [&]() {
		const bool allow_extensions = !mixed_source;
		int preferred_root = -1;
		const int max_notes = mixed_source ? 8 : 10;
		if (mixed_source) {
			preferred_root = mixed_bass_pitch_class >= 0 ?
						 mixed_bass_pitch_class :
						 lowest_candidate_pitch_class(full_mix_ownership.keyboard_candidates);
				NoteCandidateList keyboard_display =
					full_mix_display_candidates(full_mix_ownership, FullMixDisplayRow::Keyboard);
				if (snapshot.bass_debug_displayed_midi >= kKeyboardMinMidi &&
				    snapshot.bass_debug_displayed_midi < kGuitarMinMidi)
					prefer_existing_candidate_midi(keyboard_display,
								       snapshot.bass_debug_displayed_midi,
								       1.08f, 0.80f);
				set_instrument_note_set_from_candidates(snapshot.keyboard_notes, snapshot.keyboard,
									keyboard_display,
									preferred_root, keyboard_energy, rms, max_notes,
									0.18f);
		} else {
			const int min_midi = kKeyboardMinMidi;
			const int max_midi = kKeyboardMaxMidi;
			const int detected_root =
				lowest_peak_pitch_class(keyboard_detection_note_powers, min_midi, max_midi);
			preferred_root = detected_root;
			set_instrument_note_set(snapshot.keyboard_notes, snapshot.keyboard, keyboard_detection_note_powers,
						min_midi, max_midi, preferred_root, keyboard_energy, rms,
						max_notes, nullptr, nullptr, false, nullptr, 0.15f);
		}
		const int keyboard_chord_root_hint = mixed_source ? preferred_root : -1;
		if (mixed_source) {
			NoteGrid keyboard_chord_grid;
			InstrumentState keyboard_chord_note_state;
			set_instrument_note_set_from_candidates(keyboard_chord_grid, keyboard_chord_note_state,
								full_mix_ownership.keyboard_candidates,
								preferred_root, keyboard_energy, rms, max_notes,
								0.16f);
			raw_keyboard_chord = detect_keyboard_chord_from_grid(keyboard_chord_grid, allow_extensions,
									     keyboard_chord_root_hint);
			if (!valid_chord_result(raw_keyboard_chord))
				raw_keyboard_chord =
					detect_mixed_chord_from_grid(keyboard_chord_grid, keyboard_chord_root_hint,
								     allow_extensions);
		} else {
			raw_keyboard_chord =
				detect_keyboard_chord_from_grid(snapshot.keyboard_notes, allow_extensions,
								 keyboard_chord_root_hint);
		}
		set_instrument_chord(snapshot.keyboard_chord, raw_keyboard_chord, keyboard_energy, rms);
	};

	auto process_guitar = [&]() {
		const int min_midi = kGuitarMinMidi;
		const bool allow_extensions = !mixed_source;
		int preferred_root = -1;
		const int max_notes = mixed_source ? 6 : 8;
		if (mixed_source) {
			preferred_root = lowest_candidate_pitch_class(full_mix_ownership.guitar_candidates);
			NoteCandidateList guitar_display =
				prune_shadowed_full_mix_guitar_display_candidates(
					full_mix_ownership,
					full_mix_display_candidates(full_mix_ownership, FullMixDisplayRow::Guitar));
			restore_supported_lower_guitar_debug_candidates(guitar_display, full_mix_ownership);
			prefer_supported_lower_octave_candidates(guitar_display, kGuitarMinMidi, 0.30f, 0.18f);
			set_instrument_note_set_from_candidates(snapshot.guitar_notes, snapshot.guitar,
								guitar_display,
								preferred_root, guitar_energy, rms, max_notes, 0.28f);
			InstrumentState guitar_chord_note_state;
			set_instrument_note_set_from_candidates(guitar_chord_detection_grid,
								guitar_chord_note_state,
								full_mix_ownership.guitar_candidates,
								preferred_root, guitar_energy, rms,
								max_notes, 0.22f);
			prune_note_grid_below_level(guitar_chord_detection_grid, 0.24f);
		} else {
			preferred_root =
				lowest_peak_pitch_class(detection_note_powers, min_midi, kGuitarMaxMidi);
			set_instrument_note_set(snapshot.guitar_notes, snapshot.guitar, detection_note_powers,
						min_midi, kGuitarMaxMidi, preferred_root, guitar_energy, rms,
						max_notes, nullptr, nullptr, false, nullptr, 0.10f,
						false, false, kPolyphonicNoteRmsFloor);
			if (note_grid_active_pitch_class_count(snapshot.guitar_notes) <= 3) {
				std::array<float, kNoteProbeCount> low_fundamental_votes = {};
				std::array<int, kNoteProbeCount> low_fundamental_support = {};
				int active_guitar_cells = 0;
				static constexpr int kGuitarHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
				for (const auto &row : snapshot.guitar_notes.rows) {
					for (const NoteCell &cell : row) {
						if (!cell.active || cell.midi < 0)
							continue;
						++active_guitar_cells;
						for (int interval : kGuitarHarmonicIntervals) {
							const int lower = cell.midi - interval;
							if (lower < min_midi || lower > 52)
								continue;
							const std::size_t index =
								static_cast<std::size_t>(lower - kFirstMidi);
							low_fundamental_votes[index] += std::max(cell.level, 0.10f);
							++low_fundamental_support[index];
						}
					}
				}
				int recovered_midi = -1;
				float recovered_score = 0.0f;
				for (int midi = min_midi; midi <= 52; ++midi) {
					const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
					if (low_fundamental_support[index] < 2)
						continue;
					if (low_fundamental_votes[index] > recovered_score) {
						recovered_score = low_fundamental_votes[index];
						recovered_midi = midi;
					}
				}
				if (recovered_midi >= 0 &&
				    !snapshot.guitar_notes.cells[midi_pitch_class(recovered_midi)].active) {
					write_note_grid_cell(snapshot.guitar_notes,
							     NoteCandidate{recovered_midi, recovered_score},
							     recovered_score, note_visual_loudness(rms));
					write_note_grid_label(snapshot.guitar, snapshot.guitar_notes, preferred_root);
				}
			}
			InstrumentState guitar_chord_detection_state;
			constexpr int kGuitarChordAnalysisMaxNotes = 14;
			constexpr float kGuitarChordAnalysisRelativeFloor = 0.010f;
			set_instrument_note_set(guitar_chord_detection_grid, guitar_chord_detection_state,
						detection_note_powers, min_midi, kGuitarMaxMidi, preferred_root,
						guitar_energy, rms, kGuitarChordAnalysisMaxNotes, nullptr, nullptr,
						false, nullptr, kGuitarChordAnalysisRelativeFloor, false, true,
						kPolyphonicNoteRmsFloor, 1.0f);
		}
		snapshot.guitar_chord_analysis_notes = guitar_chord_detection_grid;
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			snapshot.guitar_chord_debug_probe_levels[pitch_class] =
				strongest_probe_pitch_class_level(note_powers, pitch_class, min_midi,
								  kGuitarMaxMidi);
			snapshot.guitar_chord_debug_melodic_probe_levels[pitch_class] =
				strongest_melodic_probe_pitch_class_level(note_powers, pitch_class, min_midi,
									  kGuitarMaxMidi);
		}
		raw_guitar_chord = detect_guitar_chord_from_grid(guitar_chord_detection_grid, allow_extensions);
		const ChordResult display_guitar_chord = detect_guitar_chord_from_grid(
			mixed_source ? guitar_chord_detection_grid : snapshot.guitar_notes, allow_extensions);
		auto guitar_chord_valid_for_display = [](const ChordResult &chord) {
			return chord.root >= 0 && chord.confidence >= kChordConfidenceFloor && !chord.uncertain &&
			       chord.label[0] && chord.label[0] != '-';
		};
		bool raw_guitar_valid = guitar_chord_valid_for_display(raw_guitar_chord);
		const bool display_guitar_valid = guitar_chord_valid_for_display(display_guitar_chord);
		const int displayed_guitar_pitch_classes = note_grid_active_pitch_class_count(snapshot.guitar_notes);
		auto guitar_note_grid_pitch_class_active = [&](int pitch_class) {
			pitch_class = ((pitch_class % 12) + 12) % 12;
			if (snapshot.guitar_notes.cells[pitch_class].active)
				return true;
			for (const auto &row : snapshot.guitar_notes.rows) {
				if (row[pitch_class].active)
					return true;
			}
			return false;
		};
		auto displayed_chord_tone_count = [&](const ChordResult &chord) {
			return note_grid_chord_tone_count(snapshot.guitar_notes, chord);
		};
		auto analysis_chord_tone_count = [&](const ChordResult &chord) {
			return note_grid_chord_tone_count(guitar_chord_detection_grid, chord);
		};
		auto primary_guitar_chord_is_plain_triad = [](const ChordResult &chord) {
			return primary_chord_is_plain_major_minor(chord);
		};
		auto analysis_simple_triad_supported = [&]() {
			return raw_guitar_valid && primary_guitar_chord_is_plain_triad(raw_guitar_chord) &&
			       note_grid_active_pitch_class_count(guitar_chord_detection_grid) <= 6 &&
			       analysis_chord_tone_count(raw_guitar_chord) >= 3 &&
			       displayed_chord_tone_count(raw_guitar_chord) >= 2;
		};
		const ChordResult analysis_supported_guitar_triad =
			mixed_source ? ChordResult{} :
				       detect_display_supported_guitar_analysis_triad(
					       snapshot.guitar_notes, guitar_chord_detection_grid, preferred_root);
		const bool analysis_supported_guitar_triad_valid =
			guitar_chord_valid_for_display(analysis_supported_guitar_triad);
		auto guitar_chord_supported_by_display_grid = [&](const ChordResult &chord) {
			if (mixed_source || !valid_chord_result(chord))
				return true;
			const bool power_chord = std::strstr(chord.label, "pow") != nullptr;
			return !power_chord || (guitar_note_grid_pitch_class_active(chord.root) &&
						guitar_note_grid_pitch_class_active(chord.root + 7));
		};
		const bool display_guitar_root_active =
			display_guitar_valid && guitar_note_grid_pitch_class_active(display_guitar_chord.root);
		if (!mixed_source && raw_guitar_chord.root >= 0 &&
		    !guitar_note_grid_pitch_class_active(raw_guitar_chord.root)) {
			const bool analysis_chord_display_supported =
				raw_guitar_valid && raw_guitar_chord.confidence >= 0.48f &&
				displayed_chord_tone_count(raw_guitar_chord) >= 3 &&
				std::strstr(raw_guitar_chord.label, "pow") == nullptr;
			if (!analysis_chord_display_supported && !analysis_simple_triad_supported())
				raw_guitar_chord = display_guitar_root_active ? display_guitar_chord : ChordResult{};
			raw_guitar_valid = guitar_chord_valid_for_display(raw_guitar_chord);
		}
		if (!mixed_source && raw_guitar_valid && !display_guitar_valid &&
		    displayed_guitar_pitch_classes < 3 && !analysis_simple_triad_supported()) {
			raw_guitar_chord = ChordResult{};
			raw_guitar_valid = false;
		}
		if (!raw_guitar_valid && display_guitar_valid && std::strstr(display_guitar_chord.label, "pow") == nullptr) {
			raw_guitar_chord = display_guitar_chord;
			raw_guitar_valid = true;
		}
		if (analysis_supported_guitar_triad_valid) {
			const bool raw_power = raw_guitar_valid && std::strstr(raw_guitar_chord.label, "pow");
			if (!raw_guitar_valid || raw_power ||
			    guitar_analysis_triad_should_replace(raw_guitar_chord,
							 analysis_supported_guitar_triad,
							 snapshot.guitar_notes,
							 guitar_chord_detection_grid)) {
				raw_guitar_chord = analysis_supported_guitar_triad;
				raw_guitar_valid = true;
			} else if (raw_guitar_chord.root == analysis_supported_guitar_triad.root) {
				append_same_root_chord_aliases(raw_guitar_chord, analysis_supported_guitar_triad);
			}
			append_display_supported_guitar_analysis_triad_aliases(raw_guitar_chord,
									     snapshot.guitar_notes,
									     guitar_chord_detection_grid);
		}
		if (raw_guitar_valid && display_guitar_valid && raw_guitar_chord.root == display_guitar_chord.root &&
		    std::strstr(raw_guitar_chord.label, "pow") &&
		    std::strstr(display_guitar_chord.label, "pow") == nullptr) {
			raw_guitar_chord = display_guitar_chord;
			raw_guitar_valid = true;
		}
		if (!guitar_chord_supported_by_display_grid(raw_guitar_chord)) {
			raw_guitar_chord = ChordResult{};
			raw_guitar_valid = false;
		}
		if (!mixed_source && !raw_guitar_valid) {
			raw_guitar_chord = detect_supported_guitar_root_third_dyad(
				snapshot.guitar_notes, guitar_chord_detection_grid, preferred_root);
			raw_guitar_valid = guitar_chord_valid_for_display(raw_guitar_chord);
		}
		if (!mixed_source && !raw_guitar_valid) {
			raw_guitar_chord = detect_supported_guitar_power_dyad(
				snapshot.guitar_notes, guitar_chord_detection_grid, preferred_root);
			raw_guitar_valid = guitar_chord_valid_for_display(raw_guitar_chord);
		}
		if (!mixed_source) {
			const ChordResult probe_supported_guitar_triad =
				detect_probe_supported_guitar_plain_triad(
					snapshot.guitar_notes, guitar_chord_detection_grid, note_powers,
					min_midi, kGuitarMaxMidi, preferred_root);
			if (valid_chord_result(probe_supported_guitar_triad)) {
				const bool raw_power = primary_chord_is_power(raw_guitar_chord);
				const bool raw_same_root_without_third =
					raw_guitar_valid &&
					chord_label_has_root_component(raw_guitar_chord.label,
								       probe_supported_guitar_triad.root) &&
					!chord_label_has_root_third_component(
						raw_guitar_chord.label, probe_supported_guitar_triad.root);
				if (!raw_guitar_valid || raw_power) {
					raw_guitar_chord = probe_supported_guitar_triad;
					raw_guitar_valid = true;
				} else if (raw_same_root_without_third) {
					prepend_analysis_complete_smoothed_guitar_plain_alias(
						raw_guitar_chord, probe_supported_guitar_triad,
						snapshot.guitar_notes, guitar_chord_detection_grid);
					append_same_root_chord_aliases(raw_guitar_chord,
								       probe_supported_guitar_triad);
					raw_guitar_valid = guitar_chord_valid_for_display(raw_guitar_chord);
				}
			}
		}
		if (raw_guitar_chord.root >= 0 && std::strstr(raw_guitar_chord.label, "pow")) {
			int power_root = raw_guitar_chord.root;
			ParsedRootChord parsed_power;
			const char *label_end = std::strchr(raw_guitar_chord.label, '=');
			const std::size_t label_len =
				label_end ? static_cast<std::size_t>(label_end - raw_guitar_chord.label) :
					    std::strlen(raw_guitar_chord.label);
			if (parse_root_chord_component(raw_guitar_chord.label, label_len, parsed_power) &&
			    parsed_power.quality == RootChordQuality::NoThird)
				power_root = parsed_power.root;
			auto displayed_pitch_class_level = [&](int pitch_class) {
				pitch_class = ((pitch_class % 12) + 12) % 12;
				float level = 0.0f;
				if (snapshot.guitar_notes.cells[pitch_class].active)
					level = std::max(level, snapshot.guitar_notes.cells[pitch_class].level);
				for (const auto &row : snapshot.guitar_notes.rows) {
					if (row[pitch_class].active)
						level = std::max(level, row[pitch_class].level);
				}
				return level;
			};
			const float minor_third = displayed_pitch_class_level(power_root + 3);
			const float major_third = displayed_pitch_class_level(power_root + 4);
			const bool choose_minor = minor_third > 0.0f && minor_third >= major_third * 1.10f;
			const bool choose_major = major_third > 0.0f && major_third >= minor_third * 1.10f;
			if (choose_minor != choose_major) {
				const bool minor = choose_minor;
				raw_guitar_chord.root = power_root;
				raw_guitar_chord.tones.fill(false);
				raw_guitar_chord.tones[raw_guitar_chord.root] = true;
				raw_guitar_chord.tones[(raw_guitar_chord.root + (minor ? 3 : 4)) % 12] = true;
				raw_guitar_chord.tones[(raw_guitar_chord.root + 7) % 12] = true;
				raw_guitar_chord.confidence = std::max(raw_guitar_chord.confidence, 0.58f);
				raw_guitar_chord.uncertain = false;
				std::snprintf(raw_guitar_chord.label, sizeof(raw_guitar_chord.label), "%s%s",
					      note_name(raw_guitar_chord.root), minor ? "m" : "");
			}
		}
		int raw_guitar_chord_tones = 0;
		for (bool tone : raw_guitar_chord.tones) {
			if (tone)
				++raw_guitar_chord_tones;
		}
		const bool guitar_root_adjacent_noise =
			raw_guitar_chord.root >= 0 && guitar_note_grid_pitch_class_active(raw_guitar_chord.root) &&
			guitar_note_grid_pitch_class_active(raw_guitar_chord.root - 1) &&
			guitar_note_grid_pitch_class_active(raw_guitar_chord.root + 1);
		const bool simple_guitar_chord =
			!chord_label_has_guitar_extension_or_alteration(raw_guitar_chord.label) &&
			std::strstr(raw_guitar_chord.label, "pow") == nullptr;
		const bool display_simple_guitar_chord =
			display_guitar_valid && display_guitar_chord.root == raw_guitar_chord.root &&
			!chord_label_has_guitar_extension_or_alteration(display_guitar_chord.label) &&
			std::strstr(display_guitar_chord.label, "pow") == nullptr;
		const bool simple_guitar_chord_supported_for_prune =
			simple_guitar_chord && display_simple_guitar_chord;
		const bool prune_guitar_notes =
			raw_guitar_chord.root >= 0 &&
			((simple_guitar_chord_supported_for_prune && guitar_root_adjacent_noise &&
			  raw_guitar_chord.confidence >= kChordConfidenceFloor) ||
			 (simple_guitar_chord_supported_for_prune && raw_guitar_chord.confidence >= 0.55f &&
			  displayed_guitar_pitch_classes > raw_guitar_chord_tones + 1) ||
			 (!allow_extensions && raw_guitar_chord.confidence >= 0.55f));
		if (prune_guitar_notes) {
			prune_note_grid_to_chord_tones(snapshot.guitar_notes, snapshot.guitar, raw_guitar_chord, 6,
						      preferred_root);
		}
		if (mixed_source && !valid_chord_result(raw_guitar_chord))
			raw_guitar_chord =
				detect_mixed_chord_from_grid(snapshot.guitar_notes, preferred_root, allow_extensions);
		if (allow_extensions) {
			append_supported_guitar_plain_triad_aliases(raw_guitar_chord, snapshot.guitar_notes);
			append_supported_guitar_plain_triad_aliases(
				raw_guitar_chord, guitar_chord_detection_grid,
				std::strstr(raw_guitar_chord.label, "pow") ? -1 : raw_guitar_chord.root);
			append_supported_guitar_ambiguous_third_aliases(raw_guitar_chord,
								       guitar_chord_detection_grid);
			append_root_anchored_guitar_analysis_triad_aliases(
				raw_guitar_chord, snapshot.guitar_notes, guitar_chord_detection_grid);
			append_display_supported_guitar_extension_aliases(raw_guitar_chord,
									 snapshot.guitar_notes);
			append_supported_guitar_extension_aliases(raw_guitar_chord,
								  guitar_chord_detection_grid, true);
			append_probe_supported_guitar_extension_aliases(
				raw_guitar_chord, snapshot.guitar_notes, guitar_chord_detection_grid,
				note_powers, min_midi, kGuitarMaxMidi);
			append_supported_guitar_base_triad_aliases_for_extensions(
				raw_guitar_chord, guitar_chord_detection_grid);
			append_supported_guitar_symmetric_altered_aliases(raw_guitar_chord,
									 guitar_chord_detection_grid);
			append_equivalent_sixth_seventh_aliases(raw_guitar_chord);
			append_supported_guitar_power_aliases(raw_guitar_chord, guitar_chord_detection_grid);
			append_guitar_power_probe_third_aliases(raw_guitar_chord,
								guitar_chord_detection_grid, note_powers,
								min_midi, kGuitarMaxMidi);
			remove_superseded_guitar_power_aliases(raw_guitar_chord,
							       &guitar_chord_detection_grid);
			append_guitar_power_quality_candidates(raw_guitar_chord,
							       guitar_chord_detection_grid,
							       note_powers, min_midi,
							       kGuitarMaxMidi);
			if (append_guitar_thirdless_dyad_quality_aliases(
				    raw_guitar_chord, snapshot.guitar_notes,
				    guitar_chord_detection_grid, note_powers, min_midi,
				    kGuitarMaxMidi))
				remove_superseded_guitar_power_aliases(
					raw_guitar_chord, &guitar_chord_detection_grid);
			append_guitar_probe_opposite_quality_aliases(raw_guitar_chord,
								     guitar_chord_detection_grid,
								     note_powers, min_midi,
								     kGuitarMaxMidi);
			append_root_anchored_guitar_analysis_triad_aliases(
				raw_guitar_chord, snapshot.guitar_notes, guitar_chord_detection_grid);
			append_probe_supported_guitar_rootless_plain_triad_aliases(
				raw_guitar_chord, snapshot.guitar_notes, guitar_chord_detection_grid,
				note_powers, min_midi, kGuitarMaxMidi);
			remove_superseded_guitar_power_aliases(raw_guitar_chord,
							       &guitar_chord_detection_grid);
			append_guitar_rootless_dyad_aliases(raw_guitar_chord, snapshot.guitar_notes,
							    guitar_chord_detection_grid);
			prune_clean_primary_guitar_aliases(raw_guitar_chord, snapshot.guitar_notes,
							   guitar_chord_detection_grid);
		}
		if (!mixed_source && primary_chord_is_plain_major_minor(raw_guitar_chord) &&
		    (snapshot.high_energy <= 0.010f ||
		     (primary_major_minor_root_adjacent_noise(guitar_chord_detection_grid, raw_guitar_chord) &&
		      primary_major_minor_root_adjacent_noise(snapshot.guitar_notes, raw_guitar_chord))) &&
		    primary_major_minor_chord_tone_count(guitar_chord_detection_grid, raw_guitar_chord) < 3 &&
		    primary_major_minor_chord_tone_count(snapshot.guitar_notes, raw_guitar_chord) < 3 &&
		    !primary_major_minor_third_supported(guitar_chord_detection_grid, raw_guitar_chord) &&
		    !primary_major_minor_third_supported(snapshot.guitar_notes, raw_guitar_chord))
			raw_guitar_chord = ChordResult{};
		char raw_guitar_label_before_promotion[sizeof(raw_guitar_chord.label)] = {};
		copy_text(raw_guitar_label_before_promotion, sizeof(raw_guitar_label_before_promotion),
			  raw_guitar_chord.label);
		promote_supported_plain_guitar_primary(raw_guitar_chord, snapshot.guitar_notes,
						       guitar_chord_detection_grid);
		prune_promoted_plain_guitar_primary_aliases(raw_guitar_chord, snapshot.guitar_notes,
							    guitar_chord_detection_grid,
							    raw_guitar_label_before_promotion);
		set_instrument_chord(snapshot.guitar_chord, raw_guitar_chord, guitar_energy, rms,
				     mixed_source ? kNoteRmsFloor : kPolyphonicNoteRmsFloor);
		set_instrument_chord(snapshot.guitar_raw_chord, raw_guitar_chord, guitar_energy, rms,
				     mixed_source ? kNoteRmsFloor : kPolyphonicNoteRmsFloor);
		if (mixed_source)
			promote_guitar_debug_lower_octave_primary(snapshot.guitar_notes, snapshot.guitar,
								  full_mix_ownership, preferred_root);
	};

	auto process_vocal = [&]() {
		if (mixed_source) {
			const NoteCandidateList vocal_display_candidates =
				full_mix_display_candidates(full_mix_ownership, FullMixDisplayRow::Vocal,
							    &note_powers);
			const int preferred_root = lowest_candidate_pitch_class(vocal_display_candidates);
			set_instrument_note_set_from_candidates(snapshot.vocal_notes, snapshot.vocal,
								vocal_display_candidates,
								preferred_root, vocal_energy, rms, 1);
		} else {
			const int preferred_root =
				lowest_peak_pitch_class(detection_note_powers, kVocalMinMidi, kVocalMaxMidi);
			set_instrument_note_set(snapshot.vocal_notes, snapshot.vocal, detection_note_powers,
						kVocalMinMidi, kVocalMaxMidi, preferred_root, vocal_energy,
						rms, 1, nullptr, nullptr, false, nullptr, kNoteRelativeFloor,
						true, true);
			int active_vocal_midi = -1;
			for (const auto &row : snapshot.vocal_notes.rows) {
				for (const NoteCell &cell : row) {
					if (cell.active && cell.midi >= kVocalMinMidi && cell.midi <= kVocalMaxMidi) {
						active_vocal_midi = cell.midi;
						break;
					}
				}
				if (active_vocal_midi >= 0)
					break;
			}
			if (active_vocal_midi >= 0) {
				const float active_level = probe_level(note_powers, active_vocal_midi);
				for (int adjacent : {active_vocal_midi - 1, active_vocal_midi + 1}) {
					if (adjacent < kVocalMinMidi || adjacent > kVocalMaxMidi ||
					    snapshot.vocal_notes.cells[midi_pitch_class(adjacent)].active)
						continue;
					float adjacent_level = probe_level(note_powers, adjacent);
					const bool generated_vocals_upper_neighbor =
						input_mode == AnalysisInputMode::IsolatedVocal &&
						adjacent == active_vocal_midi + 1;
					if (generated_vocals_upper_neighbor)
						adjacent_level = std::max(adjacent_level, active_level * 0.25f);
					const float adjacent_floor =
						generated_vocals_upper_neighbor ? 0.0f : 0.62f;
					if (!generated_vocals_upper_neighbor && adjacent_level < active_level * adjacent_floor)
						continue;
					const float strongest = std::max(active_level, adjacent_level);
					write_note_grid_cell(snapshot.vocal_notes, NoteCandidate{adjacent, adjacent_level},
							     strongest, note_visual_loudness(rms));
					write_note_grid_label(snapshot.vocal, snapshot.vocal_notes, preferred_root);
				}
			}
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
			const NoteCandidateList other_display =
				full_mix_display_candidates(full_mix_ownership, FullMixDisplayRow::Other);
			set_instrument_note_set_from_candidates(snapshot.other_notes, snapshot.other,
								other_display, note_root,
								other_energy, rms, other_max_notes, 0.70f);
		} else {
			const int min_midi = kOtherMinMidi;
			set_instrument_note_set(snapshot.other_notes, snapshot.other, detection_note_powers,
						min_midi, kOtherMaxMidi, note_root, other_energy, rms,
						other_max_notes, nullptr, nullptr, false, nullptr,
						0.30f, false, true);
			if (note_grid_active_pitch_class_count(snapshot.other_notes) <= 4) {
				std::array<float, kNoteProbeCount> low_fundamental_votes = {};
				std::array<int, kNoteProbeCount> low_fundamental_support = {};
				static constexpr int kOtherHarmonicIntervals[] = {12, 19, 24, 28, 31, 36};
				static constexpr int kOtherLowRecoveryIntervals[] = {12, 19, 24, 28, 31, 36, 40, 43};
				for (const auto &row : snapshot.other_notes.rows) {
					for (const NoteCell &cell : row) {
						if (!cell.active || cell.midi < 0)
							continue;
						if (cell.midi > 72)
							continue;
						for (int interval : kOtherHarmonicIntervals) {
							const int lower = cell.midi - interval;
							if (lower < 28 || lower > 52)
								continue;
							const float lower_raw = probe_level(note_powers, lower);
							if (lower_raw < strongest_note_level * 0.018f)
								continue;
							int partial_count = 0;
							for (int partial_interval : kOtherLowRecoveryIntervals) {
								const float partial =
									probe_level(note_powers, lower + partial_interval);
								if (partial >= strongest_note_level * 0.035f)
									++partial_count;
							}
							if (partial_count < 3)
								continue;
							const std::size_t index =
								static_cast<std::size_t>(lower - kFirstMidi);
							low_fundamental_votes[index] +=
								std::max(cell.level, 0.10f) *
								(1.0f + static_cast<float>(partial_count) * 0.12f);
							++low_fundamental_support[index];
						}
					}
				}
				int recovered_midi = -1;
				float recovered_score = 0.0f;
				for (int midi = 28; midi <= 52; ++midi) {
					const std::size_t index = static_cast<std::size_t>(midi - kFirstMidi);
					if (low_fundamental_support[index] < 1)
						continue;
					if (low_fundamental_votes[index] > recovered_score) {
						recovered_score = low_fundamental_votes[index];
						recovered_midi = midi;
					}
				}
				if (recovered_midi >= 0 &&
				    !snapshot.other_notes.cells[midi_pitch_class(recovered_midi)].active) {
					write_note_grid_cell(snapshot.other_notes,
							     NoteCandidate{recovered_midi, recovered_score},
							     recovered_score, note_visual_loudness(rms));
					write_note_grid_label(snapshot.other, snapshot.other_notes, note_root);
				}
			}
		}
		set_instrument_chord(snapshot.other_chord, raw_other_chord, other_energy, rms);
	};

	const bool keyboard_enabled =
		(input_mode == AnalysisInputMode::FullMix &&
		 full_mix_source_hint_allows_row(full_mix_source_hint_mode, FullMixDisplayRow::Keyboard)) ||
		input_mode == AnalysisInputMode::IsolatedKeyboard;
	const bool guitar_enabled =
		(input_mode == AnalysisInputMode::FullMix &&
		 full_mix_source_hint_allows_row(full_mix_source_hint_mode, FullMixDisplayRow::Guitar)) ||
		input_mode == AnalysisInputMode::IsolatedGuitar;
	const bool vocal_enabled =
		(input_mode == AnalysisInputMode::FullMix &&
		 full_mix_source_hint_allows_row(full_mix_source_hint_mode, FullMixDisplayRow::Vocal)) ||
		input_mode == AnalysisInputMode::IsolatedVocal;
	const bool other_enabled =
		(input_mode == AnalysisInputMode::FullMix &&
		 full_mix_source_hint_allows_row(full_mix_source_hint_mode, FullMixDisplayRow::Other)) ||
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
	NoteGrid guitar_chord_grid = guitar_chord_detection_grid;
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
		prefer_supported_lower_octave_display(snapshot.bass_notes, snapshot.bass, note_powers,
						      kBassMinMidi, kDefaultBassMaxMidi, -1);
		if (mixed_source) {
			prefer_debug_supported_mid_bass_primary(snapshot.bass_notes, snapshot.bass,
							       full_mix_ownership, -1);
			prefer_debug_supported_high_bass_primary(snapshot.bass_notes, snapshot.bass,
								 full_mix_ownership,
								 detection_note_powers, -1);
		}
		prefer_probe_supported_lower_bass_primary(snapshot.bass_notes, snapshot.bass,
							  full_mix_ownership, detection_note_powers, -1);
	} else {
		reset_note_grid_envelope(snapshot.bass_notes, snapshot.bass, bass_note_tracking_);
	}

	if (keyboard_enabled) {
		smooth_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_tracking_, -1,
					  interval_seconds, mixed_source ? 8 : 10, keyboard_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		if (!mixed_source)
			prefer_supported_lower_octave_display(snapshot.keyboard_notes, snapshot.keyboard,
							      note_powers, kKeyboardMinMidi, 52, -1);
		else
			prefer_debug_supported_keyboard_octave_primary(snapshot.keyboard_notes,
								       snapshot.keyboard,
								       full_mix_ownership, -1);
		if (mixed_source)
			prefer_exact_debug_keyboard_lower_octave_primary(snapshot.keyboard_notes,
									 snapshot.keyboard,
									 full_mix_ownership, -1);
		smooth_note_grid_envelope(keyboard_chord_grid, keyboard_chord_note_state, keyboard_chord_note_tracking_,
					  -1, interval_seconds, mixed_source ? 8 : 10, keyboard_new_notes,
					  kNoteAttackConfirmFrames,
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
					  interval_seconds, mixed_source ? 6 : 8, guitar_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		if (mixed_source)
			promote_guitar_debug_lower_octave_primary(snapshot.guitar_notes, snapshot.guitar,
								  full_mix_ownership, -1);
		if (mixed_source)
			prefer_debug_supported_guitar_octave_primary(snapshot.guitar_notes,
								    snapshot.guitar,
								    full_mix_ownership, -1);
		if (mixed_source)
			promote_raw_supported_high_guitar_lower_octave_primary(
				snapshot.guitar_notes, snapshot.guitar, full_mix_ownership,
				note_powers, -1);
		if (!mixed_source)
			prefer_supported_lower_octave_display(snapshot.guitar_notes, snapshot.guitar, note_powers,
							      kGuitarMinMidi, 52, -1);
		else
			prefer_supported_guitar_lower_octave_primary(snapshot.guitar_notes,
								     snapshot.guitar,
								     full_mix_ownership,
								     kGuitarMinMidi, 0.30f, -1);
		smooth_note_grid_envelope(guitar_chord_grid, guitar_chord_note_state, guitar_chord_note_tracking_,
					  -1, interval_seconds, mixed_source ? 6 : 12, guitar_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor,
					  kAnalyticalChordNoteReleaseSeconds, kAnalyticalChordNoteVisibleFloor);
		snapshot.guitar_chord_smoothed_notes = guitar_chord_grid;
		ChordResult smoothed_guitar_chord =
			detect_guitar_chord_from_grid(guitar_chord_grid, allow_smoothed_extensions);
		const ChordResult smoothed_analysis_supported_guitar_triad =
			mixed_source ? ChordResult{} :
				       detect_display_supported_guitar_analysis_triad(snapshot.guitar_notes,
										      guitar_chord_grid,
										      lowest_note_grid_pitch_class(
											      guitar_chord_grid));
		const ChordResult smoothed_visible_supported_guitar_triad =
			mixed_source ? ChordResult{} :
				       detect_visible_supported_guitar_plain_triad(
					       snapshot.guitar_notes,
					       lowest_note_grid_pitch_class(guitar_chord_grid));
		if (valid_chord_result(smoothed_analysis_supported_guitar_triad)) {
			if (!valid_chord_result(smoothed_guitar_chord) ||
			    std::strstr(smoothed_guitar_chord.label, "pow") ||
			    guitar_analysis_triad_should_replace(smoothed_guitar_chord,
							 smoothed_analysis_supported_guitar_triad,
							 snapshot.guitar_notes, guitar_chord_grid)) {
				smoothed_guitar_chord = smoothed_analysis_supported_guitar_triad;
			} else if (smoothed_guitar_chord.root == smoothed_analysis_supported_guitar_triad.root) {
				append_same_root_chord_aliases(smoothed_guitar_chord,
							       smoothed_analysis_supported_guitar_triad);
			}
			append_display_supported_guitar_analysis_triad_aliases(smoothed_guitar_chord,
									     snapshot.guitar_notes,
									     guitar_chord_grid);
		}
		if (valid_chord_result(smoothed_visible_supported_guitar_triad)) {
			const bool smoothed_power = valid_chord_result(smoothed_guitar_chord) &&
						    std::strstr(smoothed_guitar_chord.label, "pow");
			const bool smoothed_sus = valid_chord_result(smoothed_guitar_chord) &&
						  std::strstr(smoothed_guitar_chord.label, "sus");
			if (!valid_chord_result(smoothed_guitar_chord) || smoothed_power) {
				smoothed_guitar_chord = smoothed_visible_supported_guitar_triad;
			} else if (smoothed_guitar_chord.root == smoothed_visible_supported_guitar_triad.root) {
				append_same_root_chord_aliases(smoothed_guitar_chord,
							       smoothed_visible_supported_guitar_triad);
				if (smoothed_sus)
					smoothed_guitar_chord.confidence =
						std::max(smoothed_guitar_chord.confidence,
							 smoothed_visible_supported_guitar_triad.confidence);
			}
		}
		auto smoothed_guitar_chord_supported_by_display_grid = [&](const ChordResult &chord) {
			if (mixed_source || !valid_chord_result(chord))
				return true;
			const bool power_chord = std::strstr(chord.label, "pow") != nullptr;
			auto displayed_pitch_class_active = [&](int pitch_class) {
				pitch_class = ((pitch_class % 12) + 12) % 12;
				if (snapshot.guitar_notes.cells[pitch_class].active)
					return true;
				for (const auto &row : snapshot.guitar_notes.rows) {
					if (row[pitch_class].active)
						return true;
				}
				return false;
			};
			return !power_chord || (displayed_pitch_class_active(chord.root) &&
						displayed_pitch_class_active(chord.root + 7));
		};
		if (!smoothed_guitar_chord_supported_by_display_grid(smoothed_guitar_chord))
			smoothed_guitar_chord = ChordResult{};
		if (!mixed_source && !valid_chord_result(smoothed_guitar_chord)) {
			smoothed_guitar_chord = detect_supported_guitar_root_third_dyad(
				snapshot.guitar_notes, guitar_chord_grid,
				lowest_note_grid_pitch_class(guitar_chord_grid));
		}
		if (!mixed_source && !valid_chord_result(smoothed_guitar_chord)) {
			smoothed_guitar_chord = detect_supported_guitar_power_dyad(
				snapshot.guitar_notes, guitar_chord_grid,
				lowest_note_grid_pitch_class(guitar_chord_grid));
		}
		if (!mixed_source) {
			const ChordResult probe_supported_guitar_triad =
				detect_probe_supported_guitar_plain_triad(
					snapshot.guitar_notes, guitar_chord_grid, note_powers,
					kGuitarMinMidi, kGuitarMaxMidi,
					lowest_note_grid_pitch_class(guitar_chord_grid));
			if (valid_chord_result(probe_supported_guitar_triad)) {
				const bool smoothed_power = primary_chord_is_power(smoothed_guitar_chord);
				const bool smoothed_same_root_without_third =
					valid_chord_result(smoothed_guitar_chord) &&
					chord_label_has_root_component(smoothed_guitar_chord.label,
								       probe_supported_guitar_triad.root) &&
					!chord_label_has_root_third_component(
						smoothed_guitar_chord.label,
						probe_supported_guitar_triad.root);
				if (!valid_chord_result(smoothed_guitar_chord) || smoothed_power) {
					smoothed_guitar_chord = probe_supported_guitar_triad;
				} else if (smoothed_same_root_without_third) {
					prepend_analysis_complete_smoothed_guitar_plain_alias(
						smoothed_guitar_chord, probe_supported_guitar_triad,
						snapshot.guitar_notes, guitar_chord_grid);
					append_same_root_chord_aliases(smoothed_guitar_chord,
								       probe_supported_guitar_triad);
				}
			}
		}
		if (smoothed_guitar_chord.root >= 0 && std::strstr(smoothed_guitar_chord.label, "pow")) {
			int power_root = smoothed_guitar_chord.root;
			ParsedRootChord parsed_power;
			const char *label_end = std::strchr(smoothed_guitar_chord.label, '=');
			const std::size_t label_len =
				label_end ? static_cast<std::size_t>(label_end - smoothed_guitar_chord.label) :
					    std::strlen(smoothed_guitar_chord.label);
			if (parse_root_chord_component(smoothed_guitar_chord.label, label_len, parsed_power) &&
			    parsed_power.quality == RootChordQuality::NoThird)
				power_root = parsed_power.root;
			auto displayed_pitch_class_level = [&](int pitch_class) {
				pitch_class = ((pitch_class % 12) + 12) % 12;
				float level = 0.0f;
				if (snapshot.guitar_notes.cells[pitch_class].active)
					level = std::max(level, snapshot.guitar_notes.cells[pitch_class].level);
				for (const auto &row : snapshot.guitar_notes.rows) {
					if (row[pitch_class].active)
						level = std::max(level, row[pitch_class].level);
				}
				return level;
			};
			const float minor_third = displayed_pitch_class_level(power_root + 3);
			const float major_third = displayed_pitch_class_level(power_root + 4);
			const bool choose_minor = minor_third > 0.0f && minor_third >= major_third * 1.10f;
			const bool choose_major = major_third > 0.0f && major_third >= minor_third * 1.10f;
			if (choose_minor != choose_major) {
				const bool minor = choose_minor;
				smoothed_guitar_chord.root = power_root;
				smoothed_guitar_chord.tones.fill(false);
				smoothed_guitar_chord.tones[smoothed_guitar_chord.root] = true;
				smoothed_guitar_chord.tones[(smoothed_guitar_chord.root + (minor ? 3 : 4)) % 12] =
					true;
				smoothed_guitar_chord.tones[(smoothed_guitar_chord.root + 7) % 12] = true;
				smoothed_guitar_chord.confidence = std::max(smoothed_guitar_chord.confidence, 0.58f);
				smoothed_guitar_chord.uncertain = false;
				std::snprintf(smoothed_guitar_chord.label, sizeof(smoothed_guitar_chord.label),
					      "%s%s", note_name(smoothed_guitar_chord.root), minor ? "m" : "");
			}
		}
		if (mixed_source && !valid_chord_result(smoothed_guitar_chord))
			smoothed_guitar_chord =
				detect_mixed_chord_from_grid(guitar_chord_grid,
							     lowest_note_grid_pitch_class(guitar_chord_grid),
							     allow_smoothed_extensions);
		if (allow_smoothed_extensions) {
			append_supported_guitar_plain_triad_aliases(smoothed_guitar_chord,
								   snapshot.guitar_notes);
			append_supported_guitar_plain_triad_aliases(
				smoothed_guitar_chord, guitar_chord_grid,
				std::strstr(smoothed_guitar_chord.label, "pow") ? -1 :
										       smoothed_guitar_chord.root);
			append_supported_guitar_ambiguous_third_aliases(smoothed_guitar_chord,
								       guitar_chord_grid);
			append_root_anchored_guitar_analysis_triad_aliases(smoothed_guitar_chord,
									   snapshot.guitar_notes,
									   guitar_chord_grid);
			append_display_supported_guitar_extension_aliases(smoothed_guitar_chord,
									 snapshot.guitar_notes);
			append_supported_guitar_extension_aliases(smoothed_guitar_chord, guitar_chord_grid,
								  true);
			append_probe_supported_guitar_extension_aliases(
				smoothed_guitar_chord, snapshot.guitar_notes, guitar_chord_grid,
				note_powers, kGuitarMinMidi, kGuitarMaxMidi);
			append_supported_guitar_base_triad_aliases_for_extensions(smoothed_guitar_chord,
										 guitar_chord_grid);
			append_supported_guitar_symmetric_altered_aliases(smoothed_guitar_chord,
									 guitar_chord_grid);
			append_equivalent_sixth_seventh_aliases(smoothed_guitar_chord);
			append_supported_guitar_power_aliases(smoothed_guitar_chord, guitar_chord_grid);
			append_guitar_power_probe_third_aliases(smoothed_guitar_chord, guitar_chord_grid,
								note_powers, kGuitarMinMidi,
								kGuitarMaxMidi);
			remove_superseded_guitar_power_aliases(smoothed_guitar_chord,
							       &guitar_chord_grid);
			append_guitar_power_quality_candidates(smoothed_guitar_chord, guitar_chord_grid,
							       note_powers, kGuitarMinMidi,
							       kGuitarMaxMidi);
			if (append_guitar_thirdless_dyad_quality_aliases(
				    smoothed_guitar_chord, snapshot.guitar_notes,
				    guitar_chord_grid, note_powers, kGuitarMinMidi,
				    kGuitarMaxMidi))
				remove_superseded_guitar_power_aliases(smoothed_guitar_chord,
								       &guitar_chord_grid);
			append_guitar_probe_opposite_quality_aliases(smoothed_guitar_chord,
								     guitar_chord_grid, note_powers,
								     kGuitarMinMidi, kGuitarMaxMidi);
			append_root_anchored_guitar_analysis_triad_aliases(smoothed_guitar_chord,
									   snapshot.guitar_notes,
									   guitar_chord_grid);
			append_probe_supported_guitar_rootless_plain_triad_aliases(
				smoothed_guitar_chord, snapshot.guitar_notes, guitar_chord_grid,
				note_powers, kGuitarMinMidi, kGuitarMaxMidi);
			remove_superseded_guitar_power_aliases(smoothed_guitar_chord,
							       &guitar_chord_grid);
			append_guitar_rootless_dyad_aliases(smoothed_guitar_chord, snapshot.guitar_notes,
							    guitar_chord_grid);
			if (!mixed_source)
				prepend_analysis_complete_smoothed_guitar_plain_alias(
					raw_guitar_chord, smoothed_guitar_chord, snapshot.guitar_notes,
					guitar_chord_detection_grid);
			append_same_root_chord_aliases(raw_guitar_chord, smoothed_guitar_chord);
			append_same_root_chord_aliases(smoothed_guitar_chord, raw_guitar_chord);
			ParsedRootChord raw_primary;
			if (primary_chord_is_plain_major_minor(raw_guitar_chord) &&
			    parse_root_chord_component(raw_guitar_chord.label,
						       std::strcspn(raw_guitar_chord.label, "="),
						       raw_primary))
				remove_power_aliases_for_root(raw_guitar_chord, raw_primary.root);
			ParsedRootChord smoothed_primary;
			if (primary_chord_is_plain_major_minor(smoothed_guitar_chord) &&
			    parse_root_chord_component(
				    smoothed_guitar_chord.label,
				    std::strcspn(smoothed_guitar_chord.label, "="),
				    smoothed_primary))
				remove_power_aliases_for_root(smoothed_guitar_chord,
							      smoothed_primary.root);
			prune_clean_primary_guitar_aliases(smoothed_guitar_chord, snapshot.guitar_notes,
							   guitar_chord_grid);
		}
		if (!mixed_source && primary_chord_is_plain_major_minor(smoothed_guitar_chord) &&
		    (snapshot.high_energy <= 0.010f ||
		     (primary_major_minor_root_adjacent_noise(guitar_chord_grid, smoothed_guitar_chord) &&
		      primary_major_minor_root_adjacent_noise(snapshot.guitar_notes, smoothed_guitar_chord))) &&
		    primary_major_minor_chord_tone_count(guitar_chord_grid, smoothed_guitar_chord) < 3 &&
		    primary_major_minor_chord_tone_count(snapshot.guitar_notes, smoothed_guitar_chord) < 3 &&
		    !primary_major_minor_third_supported(guitar_chord_grid, smoothed_guitar_chord) &&
		    !primary_major_minor_third_supported(snapshot.guitar_notes, smoothed_guitar_chord))
			smoothed_guitar_chord = ChordResult{};
		char smoothed_guitar_label_before_promotion[sizeof(smoothed_guitar_chord.label)] = {};
		copy_text(smoothed_guitar_label_before_promotion,
			  sizeof(smoothed_guitar_label_before_promotion),
			  smoothed_guitar_chord.label);
		promote_supported_plain_guitar_primary(smoothed_guitar_chord,
						       snapshot.guitar_notes,
						       guitar_chord_grid);
		prune_promoted_plain_guitar_primary_aliases(smoothed_guitar_chord,
							    snapshot.guitar_notes,
							    guitar_chord_grid,
							    smoothed_guitar_label_before_promotion);
		set_instrument_chord(snapshot.guitar_smoothed_chord, smoothed_guitar_chord, guitar_energy, rms,
				     mixed_source ? kNoteRmsFloor : kPolyphonicNoteRmsFloor);
		stabilize_chord(snapshot.guitar_chord, guitar_chord_tracking_, raw_guitar_chord,
				smoothed_guitar_chord, true, interval_seconds);
		promote_low_guitar_display_fundamentals(snapshot.guitar_notes, snapshot.guitar,
							snapshot.guitar_chord_analysis_notes, -1);
	} else {
		reset_note_grid_envelope(snapshot.guitar_notes, snapshot.guitar, guitar_note_tracking_);
		reset_note_grid_envelope(guitar_chord_grid, guitar_chord_note_state, guitar_chord_note_tracking_);
		reset_chord_tracking(guitar_chord_tracking_, snapshot.guitar_chord);
		clear_instrument_state(snapshot.guitar_raw_chord);
		clear_instrument_state(snapshot.guitar_smoothed_chord);
	}

	if (vocal_enabled) {
		const int vocal_max_notes = contains_case_insensitive(resolved_source_name, "vocals") ? 2 : 1;
		smooth_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_tracking_, -1,
					  interval_seconds, vocal_max_notes);
		if (!mixed_source)
			prefer_supported_lower_octave_display(snapshot.vocal_notes, snapshot.vocal, note_powers,
							      kVocalMinMidi, 64, -1);
		else
			prefer_visible_lower_octave_primary(snapshot.vocal_notes, snapshot.vocal, kVocalMinMidi,
							   0.20f, -1, 0.18f);
	} else {
		reset_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_tracking_);
	}

	if (other_enabled) {
		smooth_note_grid_envelope(snapshot.other_notes, snapshot.other, other_note_tracking_, -1,
					  interval_seconds, other_max_notes, other_new_notes,
					  kNoteAttackConfirmFrames,
					  mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor :
							 kNoteEnvelopeImmediateConfirmFloor);
		if (!mixed_source)
			prefer_supported_lower_octave_display(snapshot.other_notes, snapshot.other, note_powers,
							      kOtherMinMidi, 52, -1);
		else {
			prefer_visible_lower_octave_primary(snapshot.other_notes, snapshot.other, kOtherMinMidi,
							   0.20f, -1, 0.08f, 52);
			prefer_debug_supported_lower_other_octave_primary(snapshot.other_notes, snapshot.other,
									  full_mix_ownership, kOtherMinMidi,
									  -1);
			if (mixed_string_source_hint || synthetic_other_source_hint)
				promote_source_hinted_other_debug_primaries(
					snapshot.other_notes, snapshot.other, full_mix_ownership,
					note_powers, kOtherMinMidi, -1, synthetic_other_source_hint,
					mixed_string_source_hint);
			if (synthetic_other_source_hint) {
				prefer_strong_visible_lower_other_octave_primary(snapshot.other_notes,
										 snapshot.other, kOtherMinMidi,
										 -1);
				prefer_probe_supported_lower_synth_primary(
					snapshot.other_notes, snapshot.other, full_mix_ownership,
					note_powers, kOtherMinMidi, -1);
			}
			if (mixed_string_source_hint) {
				prefer_debug_supported_upper_other_octave_primary(snapshot.other_notes,
										  snapshot.other,
										  full_mix_ownership,
										  kOtherMinMidi, -1);
				prefer_measured_string_lower_other_octave_primary(
					snapshot.other_notes, snapshot.other, full_mix_ownership, kOtherMinMidi,
					-1);
				prefer_weak_debug_string_lower_other_octave_primary(
					snapshot.other_notes, snapshot.other, full_mix_ownership,
					kOtherMinMidi, -1);
			}
		}
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
