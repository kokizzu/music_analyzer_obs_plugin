#include "analyzer.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include <vector>

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
constexpr float kNoteRmsFloor = 0.012f;
constexpr float kFullNoteRms = 0.080f;
constexpr float kNoteRelativeFloor = 0.40f;
constexpr float kHarmonicMaskRatio = 0.62f;
constexpr int kChromaticTuneMinMidi = kGuitarMinMidi;
constexpr float kChromaticTuneToleranceCents = 9.0f;
constexpr float kChromaticTuneEstimatorSlackCents = 0.5f;
constexpr float kChromaticCenterAdjacentRatio = 0.985f;
constexpr float kChromaticCenterEdgeRatio = 0.90f;
constexpr float kNoteEnvelopeReleaseSeconds = 3.0f;
constexpr float kNoteEnvelopeVisibleFloor = 0.015f;
constexpr float kNoteEnvelopeNewNoteFloor = 0.025f;
constexpr std::size_t kDrumTransientSegments = 8;
constexpr float kDrumTransientRatio = 1.55f;

enum class SourceHint {
	None,
	Bass,
	Keyboard,
	Guitar,
	Vocal,
	Other,
};

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

SourceHint infer_source_hint(const char *source_name)
{
	if (contains_case_insensitive(source_name, "bass"))
		return SourceHint::Bass;
	if (contains_case_insensitive(source_name, "synth") || contains_case_insensitive(source_name, "brass") ||
	    contains_case_insensitive(source_name, "horn") || contains_case_insensitive(source_name, "violin") ||
	    contains_case_insensitive(source_name, "string"))
		return SourceHint::Other;
	if (contains_case_insensitive(source_name, "key") || contains_case_insensitive(source_name, "piano") ||
	    contains_case_insensitive(source_name, "organ"))
		return SourceHint::Keyboard;
	if (contains_case_insensitive(source_name, "guitar"))
		return SourceHint::Guitar;
	if (contains_case_insensitive(source_name, "vocal") || contains_case_insensitive(source_name, "voice") ||
	    contains_case_insensitive(source_name, "sing"))
		return SourceHint::Vocal;
	if (contains_case_insensitive(source_name, "other"))
		return SourceHint::Other;
	return SourceHint::None;
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

RangeResult dominant_note(const std::array<float, kNoteProbeCount> &powers, int min_midi, int max_midi, bool include_harmonics)
{
	float total = 0.0f;
	RangeResult result;

	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const int idx = midi - kFirstMidi;
		float score = powers[idx];
		if (include_harmonics) {
			if (midi + 12 <= kLastMidi)
				score += powers[midi + 12 - kFirstMidi] * 0.35f;
			if (midi + 24 <= kLastMidi)
				score += powers[midi + 24 - kFirstMidi] * 0.18f;
		}
		total += std::max(score, 0.0f);
		if (score > result.score) {
			result.score = score;
			result.midi = midi;
		}
	}

	result.confidence = total > 1.0e-9f ? std::clamp(result.score / total, 0.0f, 1.0f) : 0.0f;
	return result;
}

struct NoteCandidate {
	int midi = -1;
	float score = 0.0f;
};

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

bool timbre_supports_kind(const std::array<float, kNoteProbeCount> &powers, int midi, TimbreKind kind)
{
	const TimbreMix mix = timbre_mix_for_midi(powers, midi);
	const float fundamental = mix.bands[0];
	if (fundamental <= 1.0e-6f)
		return false;

	const std::size_t kind_index = static_cast<std::size_t>(kind);
	const float weight = mix.weights[kind_index];
	const float relative_weight = weight / fundamental;
	const float second = mix.bands[1] / fundamental;
	const float third = mix.bands[2] / fundamental;
	const float fourth = mix.bands[3] / fundamental;
	const float fifth = mix.bands[4] / fundamental;

	switch (kind) {
	case TimbreKind::Keyboard:
		return relative_weight >= 0.14f && second <= 0.48f;
	case TimbreKind::Guitar:
		return relative_weight >= 0.14f && second >= 0.20f && third >= 0.08f;
	case TimbreKind::Other:
		return relative_weight >= 0.17f && second >= 0.26f && (fourth >= 0.07f || fifth >= 0.04f);
	}

	return false;
}

void claim_note_grid_midis(const NoteGrid &grid, std::array<bool, kNoteProbeCount> &claimed_midis)
{
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < kFirstMidi || cell.midi > kLastMidi)
				continue;
			claimed_midis[cell.midi - kFirstMidi] = true;
		}
	}
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
			   const std::array<bool, 12> *allowed_pitch_classes)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	if (blocked_pitch_classes && (*blocked_pitch_classes)[pitch_class])
		return false;
	if (allowed_pitch_classes && !(*allowed_pitch_classes)[pitch_class])
		return false;
	return true;
}

std::vector<NoteCandidate> note_peak_candidates(const std::array<float, kNoteProbeCount> &powers, int min_midi,
						int max_midi, int max_notes,
						const std::array<bool, 12> *blocked_pitch_classes = nullptr,
						const std::array<bool, 12> *allowed_pitch_classes = nullptr,
						bool suppress_adjacent_neighbors = false)
{
	std::array<float, kNoteProbeCount> scores = {};
	float strongest_score = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (!pitch_class_available(midi, blocked_pitch_classes, allowed_pitch_classes))
			continue;
		const float score = std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
		scores[midi - kFirstMidi] = score;
		strongest_score = std::max(strongest_score, score);
	}

	std::vector<NoteCandidate> candidates;
	if (strongest_score <= 1.0e-6f)
		return candidates;

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float score = scores[midi - kFirstMidi];
		if (score >= strongest_score * kNoteRelativeFloor &&
		    !likely_lower_harmonic(scores, min_midi, midi, score))
			candidates.push_back(NoteCandidate{midi, score});
	}

	std::sort(candidates.begin(), candidates.end(),
		  [](const NoteCandidate &a, const NoteCandidate &b) { return a.score > b.score; });

	std::vector<NoteCandidate> selected;
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
					    bool suppress_adjacent_neighbors = false)
{
	std::array<float, 12> chroma = {};
	for (const NoteCandidate &candidate : note_peak_candidates(powers, min_midi, max_midi, 6,
								   blocked_pitch_classes, nullptr,
								   suppress_adjacent_neighbors)) {
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
			    bool suppress_adjacent_neighbors = false)
{
	const std::vector<NoteCandidate> candidates =
		note_peak_candidates(powers, min_midi, max_midi, 6, blocked_pitch_classes, nullptr,
				     suppress_adjacent_neighbors);
	if (candidates.empty())
		return -1;

	int lowest_midi = candidates.front().midi;
	for (const NoteCandidate &candidate : candidates)
		lowest_midi = std::min(lowest_midi, candidate.midi);
	return ((lowest_midi % 12) + 12) % 12;
}

struct ChordResult {
	char label[64] = {};
	std::array<bool, 12> tones = {};
	int root = -1;
	float confidence = 0.0f;
};

struct ChordCandidate {
	char label[16] = {};
	std::array<bool, 12> tones = {};
	uint16_t mask = 0;
	int root = -1;
	float score = 0.0f;
};

ChordResult detect_chord(const std::array<float, 12> &chroma, int bass_pitch_class = -1, bool allow_extensions = true)
{
	ChordResult best;
	float best_score = 0.0f;
	uint16_t best_mask = 0;
	std::vector<ChordCandidate> candidates;
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
		candidates.push_back(candidate);

		if (score > best_score) {
			best_score = score;
			best_mask = candidate.mask;
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

	best.confidence = chroma_sum > 0.0f ? std::clamp(best_score / (chroma_sum + 1.0e-6f), 0.0f, 1.0f) : 0.0f;
	if (best.confidence < 0.34f) {
		best.root = -1;
		best.tones.fill(false);
		copy_text(best.label, sizeof(best.label), "--");
		return best;
	}

	std::vector<ChordCandidate> aliases;
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

void clear_note_grid_pitch_class(NoteGrid &grid, int pitch_class)
{
	if (pitch_class < 0)
		return;
	pitch_class %= 12;
	grid.cells[pitch_class] = {};
	for (auto &row : grid.rows)
		row[pitch_class] = {};
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

float strongest_note_grid_level(const NoteGrid &grid)
{
	float strongest = 0.0f;
	for (const NoteCell &cell : grid.cells)
		strongest = std::max(strongest, cell.level);
	return strongest;
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

void smooth_note_grid_envelope(NoteGrid &grid, InstrumentState &state, std::array<float, kNoteProbeCount> &envelope,
			       int preferred_root, float interval_seconds, int max_notes,
			       const std::array<bool, kNoteProbeCount> *new_note_midi_filter = nullptr)
{
	std::array<float, kNoteProbeCount> raw_levels = {};
	collect_note_grid_levels(grid, raw_levels);

	const float release_step =
		std::clamp(interval_seconds, 0.01f, 1.0f) / std::max(kNoteEnvelopeReleaseSeconds, 0.01f);
	for (std::size_t i = 0; i < envelope.size(); ++i) {
		float raw_level = std::clamp(raw_levels[i], 0.0f, 1.0f);
		if (envelope[i] <= 0.0f && raw_level > 0.0f && new_note_midi_filter &&
		    !(*new_note_midi_filter)[i])
			raw_level = 0.0f;
		if (envelope[i] <= 0.0f && raw_level > 0.0f && raw_level < kNoteEnvelopeNewNoteFloor)
			raw_level = 0.0f;

		float level = raw_level >= envelope[i] ? raw_level : std::max(raw_level, envelope[i] - release_step);
		if (level < kNoteEnvelopeVisibleFloor)
			level = 0.0f;
		envelope[i] = std::clamp(level, 0.0f, 1.0f);
	}

	clear_note_grid(grid);
	std::vector<NoteCandidate> candidates;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		const float level = envelope[midi - kFirstMidi];
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

void reset_note_grid_envelope(NoteGrid &grid, InstrumentState &state,
			      std::array<float, kNoteProbeCount> &envelope)
{
	envelope.fill(0.0f);
	clear_instrument_note_grid(grid, state);
}

std::array<bool, kNoteProbeCount> mixed_note_seed_filter(const NoteGrid &grid,
							 const ChordResult &seed_chord,
							 const std::array<float, kNoteProbeCount> &powers,
							 TimbreKind kind)
{
	std::array<bool, kNoteProbeCount> allowed = {};
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < kFirstMidi || cell.midi > kLastMidi)
				continue;

			const int pitch_class = ((cell.midi % 12) + 12) % 12;
			const bool chord_tone = seed_chord.root >= 0 && seed_chord.tones[pitch_class];
			if (chord_tone || timbre_supports_kind(powers, cell.midi, kind))
				allowed[cell.midi - kFirstMidi] = true;
		}
	}
	return allowed;
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

void set_chord_from_smoothed_grid(InstrumentState &state, const NoteGrid &grid, bool allow_extensions)
{
	const ChordResult chord = detect_chord(note_grid_chroma(grid), lowest_note_grid_pitch_class(grid), allow_extensions);
	if (chord.confidence >= 0.36f) {
		copy_text(state.label, sizeof(state.label), chord.label);
		state.confidence = chord.confidence;
		return;
	}

	clear_instrument_state(state);
}

void add_shared_timbre_notes(NoteGrid &grid, InstrumentState &state, const std::array<float, kNoteProbeCount> &powers,
			     const std::array<float, kNoteProbeCount> &tuned_powers, int min_midi, int max_midi,
			     int preferred_root,
			     const std::array<bool, kNoteProbeCount> &claimed_midis,
			     TimbreKind kind, float rms)
{
	const float visual_loudness = note_visual_loudness(rms);
	if (visual_loudness <= 0.0f)
		return;

	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi) {
		if (!claimed_midis[midi - kFirstMidi])
			continue;
		const int pitch_class = ((midi % 12) + 12) % 12;
		if (grid.cells[pitch_class].active)
			continue;
		if (!timbre_supports_kind(powers, midi, kind))
			continue;
		const float score = std::sqrt(std::max(tuned_powers[midi - kFirstMidi], 0.0f));
		if (score <= 1.0e-6f)
			continue;

		for (int neighbor : {midi - 1, midi + 1}) {
			if (neighbor >= min_midi && neighbor <= max_midi)
				clear_note_grid_pitch_class(grid, ((neighbor % 12) + 12) % 12);
		}
		write_note_grid_cell(grid, NoteCandidate{midi, score}, score, visual_loudness);
	}

	if (strongest_note_grid_level(grid) > 0.0f)
		write_note_grid_label(state, grid, preferred_root);
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
			     bool suppress_adjacent_neighbors = false)
{
	clear_note_grid(grid);
	if (rms < kNoteRmsFloor || energy < 1.0e-5f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	float strongest_score = 0.0f;
	const std::vector<NoteCandidate> candidates =
		note_peak_candidates(powers, min_midi, max_midi, max_notes, blocked_pitch_classes,
				     allowed_pitch_classes, suppress_adjacent_neighbors);
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

	if (chord.confidence >= 0.36f) {
		copy_text(state.label, sizeof(state.label), chord.label);
		state.confidence = chord.confidence;
		return;
	}

	copy_text(state.label, sizeof(state.label), "--");
	state.confidence = 0.0f;
}

void claim_note_grid_pitch_classes(const NoteGrid &grid, std::array<bool, 12> &claimed_pitch_classes)
{
	for (const auto &row : grid.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0)
				continue;
			const int pitch_class = ((cell.midi % 12) + 12) % 12;
			claimed_pitch_classes[pitch_class] = true;
		}
	}
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
		reset_note_envelopes();
	}
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
	bass_note_envelope_.fill(0.0f);
	guitar_note_envelope_.fill(0.0f);
	keyboard_note_envelope_.fill(0.0f);
	vocal_note_envelope_.fill(0.0f);
	other_note_envelope_.fill(0.0f);
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

bool AnalysisEngine::chromatic_tuning_match(const float *samples, std::size_t count, float mean, int midi) const
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
	if (std::abs(cents) <= kChromaticTuneToleranceCents + kChromaticTuneEstimatorSlackCents)
		return true;
	if (std::abs(cents) <= kProbeCents.back() && best_score > 1.0e-6f &&
	    center_score >= best_score * kChromaticCenterAdjacentRatio)
		return true;

	const bool edge_peak = best == 0 || best + 1 == kProbeCents.size();
	return edge_peak && best_score > 1.0e-6f && center_score >= best_score * kChromaticCenterEdgeRatio;
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
					   std::size_t root_candidates_size)
{
	constexpr float kMinimumRootWindowSeconds = 15.0f;
	constexpr float kSilenceResetSeconds = 2.0f;
	constexpr float kModulationLead = 1.12f;

	InstrumentState state;
	const float interval_seconds = std::clamp(settings.analysis_interval_seconds, 0.01f, 1.0f);
	const float requested_window_seconds = std::max(settings.root_window_seconds, kMinimumRootWindowSeconds);
	const std::size_t target_votes = std::clamp<std::size_t>(
		static_cast<std::size_t>(std::ceil(requested_window_seconds / interval_seconds)), 1, kMaxRootVotes);

	if (target_votes != root_vote_target_) {
		root_vote_target_ = target_votes;
		reset_root_window();
	}

	const RootCandidate candidate = detect_root_candidate(powers, rms);

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
		if (window_ready && confidence >= 0.34f && best_score > locked_score * kModulationLead)
			locked_root_ = best;
	}

	if (locked_root_ >= 0) {
		const float confidence = total > 1.0e-6f ? std::max(root_sum_[locked_root_], 0.0f) / total : 0.0f;
		copy_text(state.label, sizeof(state.label), note_name(locked_root_));
		state.confidence = std::clamp(confidence, 0.0f, 1.0f);
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
	copy_text(snapshot.source, sizeof(snapshot.source), source_name && *source_name ? source_name : "Music");
	copy_text(snapshot.drums[Kick].label, sizeof(snapshot.drums[Kick].label), "BASS DRUM");
	copy_text(snapshot.drums[Snare].label, sizeof(snapshot.drums[Snare].label), "SNARE");
	copy_text(snapshot.drums[HiHat].label, sizeof(snapshot.drums[HiHat].label), "HIHAT");
	copy_text(snapshot.drums[Crash].label, sizeof(snapshot.drums[Crash].label), "CRASH");
	copy_text(snapshot.drums[Tom].label, sizeof(snapshot.drums[Tom].label), "TOMS");
	copy_text(snapshot.drums[Ride].label, sizeof(snapshot.drums[Ride].label), "RIDE");
	snapshot.dropped_windows = dropped_windows;

	if (!samples || count == 0) {
		reset_note_envelopes();
		copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
		copy_text(snapshot.root.label, sizeof(snapshot.root.label), "--");
		copy_text(snapshot.root_candidates, sizeof(snapshot.root_candidates), "-- 0%");
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

	std::array<float, kNoteProbeCount> note_powers = {};
	for (std::size_t i = 0; i < note_probes_.size(); ++i)
		note_powers[i] = goertzel_power(samples, usable, mean, note_probes_[i]);

	std::array<float, kNoteProbeCount> tuned_note_powers = note_powers;
	for (int midi = kFirstMidi; midi <= kLastMidi; ++midi) {
		if (midi >= kChromaticTuneMinMidi && !chromatic_tuning_match(samples, usable, mean, midi))
			tuned_note_powers[midi - kFirstMidi] = 0.0f;
	}

	std::array<float, 15> drum_powers = {};
	for (std::size_t i = 0; i < drum_probes_.size(); ++i)
		drum_powers[i] = std::sqrt(goertzel_power(samples, usable, mean, drum_probes_[i]));

	const float low = sum_notes(tuned_note_powers, kBassMinMidi, 47);
	const float mid = sum_notes(tuned_note_powers, 48, 72);
	const float high = sum_notes(tuned_note_powers, 73, kLastMidi) + drum_powers[11] + drum_powers[12] + drum_powers[13];
	const float bass_energy = sum_notes(tuned_note_powers, kBassMinMidi, kBassMaxMidi);
	const float guitar_energy = sum_notes(tuned_note_powers, kGuitarMinMidi, kGuitarMaxMidi);
	const float keyboard_energy = sum_notes(tuned_note_powers, kKeyboardMinMidi, kKeyboardMaxMidi);
	const float vocal_energy = sum_notes(tuned_note_powers, kVocalMinMidi, kVocalMaxMidi);
	const float other_energy = sum_notes(tuned_note_powers, kOtherMinMidi, kOtherMaxMidi);
	const float total = low + mid + high + 1.0e-6f;
	snapshot.low_energy = low / total;
	snapshot.mid_energy = mid / total;
	snapshot.high_energy = high / total;

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

	const float sensitivity = std::clamp(settings.sensitivity, 0.25f, 4.0f);
	const float trigger_threshold = 1.42f / sensitivity;
	for (std::size_t i = 0; i < kDrumCount; ++i) {
		if (drum_average_[i] <= 0.0f)
			drum_average_[i] = drum_bands[i];

		const float band_ratio = drum_bands[i] / (drum_average_[i] + 1.0e-6f);
		float score = band_ratio * 0.72f + onset * 0.28f;
		if (i == Kick)
			score *= 1.0f + snapshot.low_energy * 0.8f;
		if (i == HiHat || i == Crash || i == Ride)
			score *= 1.0f + snapshot.high_energy * 0.55f;
		if (i == Snare)
			score *= 1.0f + snapshot.mid_energy * 0.45f;

		if (rms > kSilenceRms && drum_transient && score > trigger_threshold) {
			const float level = std::clamp((score - trigger_threshold) * 0.85f, 0.35f, 1.0f);
			drum_level_[i] = std::max(drum_level_[i], level);
		} else {
			drum_level_[i] *= 0.72f;
		}

		drum_average_[i] = drum_average_[i] * 0.92f + drum_bands[i] * 0.08f;
		snapshot.drums[i].level = drum_level_[i];
		snapshot.drums[i].active = drum_level_[i] > 0.30f;
	}

	snapshot.root = track_root(tuned_note_powers, rms, settings, snapshot.root_candidates, sizeof(snapshot.root_candidates));

	std::array<bool, 12> claimed_pitch_classes = {};
	std::array<bool, kNoteProbeCount> claimed_midis = {};
	const SourceHint source_hint = infer_source_hint(source_name);
	const bool mixed_source = source_hint == SourceHint::None || source_hint == SourceHint::Bass;

	if (source_hint == SourceHint::None || source_hint == SourceHint::Bass) {
		const RangeResult bass_note = dominant_note(tuned_note_powers, kBassMinMidi, kBassMaxMidi, true);
		if (source_hint == SourceHint::Bass || bass_note.midi <= kDefaultBassMaxMidi) {
			set_single_note_grid(snapshot.bass_notes, snapshot.bass, bass_note, bass_energy, rms);
			claim_note_grid_pitch_classes(snapshot.bass_notes, claimed_pitch_classes);
			claim_note_grid_midis(snapshot.bass_notes, claimed_midis);
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

	auto process_keyboard = [&]() {
		const int min_midi = mixed_source ? 48 : kKeyboardMinMidi;
		const int max_midi = mixed_source ? 83 : kKeyboardMaxMidi;
		const bool allow_extensions = !mixed_source;
		const bool suppress_adjacent = mixed_source;
		const std::array<bool, 12> blocked_pitch_classes = claimed_pitch_classes;
		const std::array<float, 12> chroma =
			peak_chroma_for_range(tuned_note_powers, min_midi, max_midi, &blocked_pitch_classes,
					      suppress_adjacent);
		const int preferred_root =
			lowest_peak_pitch_class(tuned_note_powers, min_midi, max_midi, &blocked_pitch_classes,
						suppress_adjacent);
		const ChordResult chord = detect_chord(chroma, preferred_root, allow_extensions);
		const std::array<bool, 12> *allowed = mixed_source && chord.root >= 0 ? &chord.tones : nullptr;
		const int max_notes = mixed_source && !allowed ? 4 : 10;
		set_instrument_note_set(snapshot.keyboard_notes, snapshot.keyboard, tuned_note_powers, min_midi, max_midi,
					chord.root >= 0 ? chord.root : preferred_root, keyboard_energy, rms,
					max_notes, &blocked_pitch_classes, allowed, suppress_adjacent);
		set_instrument_chord(snapshot.keyboard_chord, chord, keyboard_energy, rms);
		claim_note_grid_pitch_classes(snapshot.keyboard_notes, claimed_pitch_classes);
		claim_note_grid_midis(snapshot.keyboard_notes, claimed_midis);
	};

	auto process_guitar = [&]() {
		const bool allow_extensions = !mixed_source;
		const bool suppress_adjacent = mixed_source;
		const std::array<bool, 12> blocked_pitch_classes = claimed_pitch_classes;
		const std::array<float, 12> chroma =
			peak_chroma_for_range(tuned_note_powers, kGuitarMinMidi, kGuitarMaxMidi, &blocked_pitch_classes,
					      suppress_adjacent);
		const int preferred_root =
			lowest_peak_pitch_class(tuned_note_powers, kGuitarMinMidi, kGuitarMaxMidi,
						&blocked_pitch_classes, suppress_adjacent);
		const ChordResult chord = detect_chord(chroma, preferred_root, allow_extensions);
		const std::array<bool, 12> *allowed = mixed_source && chord.root >= 0 ? &chord.tones : nullptr;
		const int max_notes = mixed_source && !allowed ? 2 : 8;
		set_instrument_note_set(snapshot.guitar_notes, snapshot.guitar, tuned_note_powers, kGuitarMinMidi,
					kGuitarMaxMidi, chord.root >= 0 ? chord.root : preferred_root, guitar_energy, rms,
					max_notes, &blocked_pitch_classes, allowed, suppress_adjacent);
		if (mixed_source) {
			add_shared_timbre_notes(snapshot.guitar_notes, snapshot.guitar, note_powers, tuned_note_powers,
						kGuitarMinMidi,
						kGuitarMaxMidi, chord.root >= 0 ? chord.root : preferred_root,
						claimed_midis, TimbreKind::Guitar, rms);
		}
		set_instrument_chord(snapshot.guitar_chord, chord, guitar_energy, rms);
		claim_note_grid_pitch_classes(snapshot.guitar_notes, claimed_pitch_classes);
		claim_note_grid_midis(snapshot.guitar_notes, claimed_midis);
	};

	auto process_vocal = [&]() {
		const int min_midi = mixed_source ? 60 : kVocalMinMidi;
		const bool suppress_adjacent = mixed_source;
		const std::array<bool, 12> blocked_pitch_classes = claimed_pitch_classes;
		const int preferred_root =
			lowest_peak_pitch_class(tuned_note_powers, min_midi, kVocalMaxMidi, &blocked_pitch_classes,
						suppress_adjacent);
		set_instrument_note_set(snapshot.vocal_notes, snapshot.vocal, tuned_note_powers, min_midi,
					kVocalMaxMidi, preferred_root, vocal_energy, rms, 1, &blocked_pitch_classes,
					nullptr, suppress_adjacent);
		claim_note_grid_pitch_classes(snapshot.vocal_notes, claimed_pitch_classes);
		claim_note_grid_midis(snapshot.vocal_notes, claimed_midis);
	};

	auto process_other = [&]() {
		const int min_midi = mixed_source ? 72 : kOtherMinMidi;
		const bool allow_extensions = !mixed_source;
		const bool suppress_adjacent = mixed_source;
		const std::array<bool, 12> blocked_pitch_classes = claimed_pitch_classes;
		const std::array<float, 12> chroma =
			peak_chroma_for_range(tuned_note_powers, min_midi, kOtherMaxMidi, &blocked_pitch_classes,
					      suppress_adjacent);
		const int preferred_root =
			lowest_peak_pitch_class(tuned_note_powers, min_midi, kOtherMaxMidi, &blocked_pitch_classes,
						suppress_adjacent);
		const ChordResult chord = detect_chord(chroma, preferred_root, allow_extensions);
		set_instrument_note_set(snapshot.other_notes, snapshot.other, tuned_note_powers, min_midi, kOtherMaxMidi,
					chord.root >= 0 ? chord.root : preferred_root, other_energy, rms, 8,
					&blocked_pitch_classes, nullptr, suppress_adjacent);
		if (mixed_source) {
			add_shared_timbre_notes(snapshot.other_notes, snapshot.other, note_powers, tuned_note_powers, 60,
						min_midi - 1,
						chord.root >= 0 ? chord.root : preferred_root, claimed_midis,
						TimbreKind::Other, rms);
		}
		set_instrument_chord(snapshot.other_chord, chord, other_energy, rms);
		claim_note_grid_pitch_classes(snapshot.other_notes, claimed_pitch_classes);
		claim_note_grid_midis(snapshot.other_notes, claimed_midis);
	};

	switch (source_hint) {
	case SourceHint::Guitar:
		process_guitar();
		process_keyboard();
		process_vocal();
		process_other();
		break;
	case SourceHint::Vocal:
		process_vocal();
		process_keyboard();
		process_guitar();
		process_other();
		break;
	case SourceHint::Other:
		process_other();
		clear_instrument_note_grid(snapshot.keyboard_notes, snapshot.keyboard);
		clear_instrument_state(snapshot.keyboard_chord);
		clear_instrument_note_grid(snapshot.guitar_notes, snapshot.guitar);
		clear_instrument_state(snapshot.guitar_chord);
		clear_instrument_note_grid(snapshot.vocal_notes, snapshot.vocal);
		break;
	case SourceHint::None:
	case SourceHint::Bass:
	case SourceHint::Keyboard:
	default:
		process_keyboard();
		process_guitar();
		process_vocal();
		process_other();
		break;
	}

	const float interval_seconds = std::clamp(settings.analysis_interval_seconds, 0.01f, 1.0f);
	const bool bass_processed = source_hint == SourceHint::None || source_hint == SourceHint::Bass;
	const bool harmonic_processed = source_hint != SourceHint::Other;
	const bool allow_smoothed_extensions = !mixed_source;
	const ChordResult keyboard_seed_chord =
		detect_chord(note_grid_chroma(snapshot.keyboard_notes),
			     lowest_note_grid_pitch_class(snapshot.keyboard_notes), allow_smoothed_extensions);
	const ChordResult guitar_seed_chord =
		detect_chord(note_grid_chroma(snapshot.guitar_notes),
			     lowest_note_grid_pitch_class(snapshot.guitar_notes), allow_smoothed_extensions);
	const ChordResult other_seed_chord =
		detect_chord(note_grid_chroma(snapshot.other_notes),
			     lowest_note_grid_pitch_class(snapshot.other_notes), allow_smoothed_extensions);
	const bool keyboard_raw_chord = keyboard_seed_chord.root >= 0 && snapshot.keyboard_chord.label[0] != '-';
	const bool guitar_raw_chord = guitar_seed_chord.root >= 0 && snapshot.guitar_chord.label[0] != '-';
	const bool other_raw_chord = other_seed_chord.root >= 0 && snapshot.other_chord.label[0] != '-';
	const bool keyboard_raw_notes = strongest_note_grid_level(snapshot.keyboard_notes) > 0.0f;
	const bool guitar_raw_notes = strongest_note_grid_level(snapshot.guitar_notes) > 0.0f;
	const bool other_raw_notes = strongest_note_grid_level(snapshot.other_notes) > 0.0f;
	const std::array<bool, kNoteProbeCount> keyboard_seed_filter =
		mixed_note_seed_filter(snapshot.keyboard_notes, keyboard_seed_chord, note_powers, TimbreKind::Keyboard);
	const std::array<bool, kNoteProbeCount> *keyboard_new_notes = mixed_source ? &keyboard_seed_filter : nullptr;
	const std::array<bool, kNoteProbeCount> *guitar_new_notes = nullptr;
	const std::array<bool, kNoteProbeCount> *other_new_notes = nullptr;

	if (bass_processed) {
		smooth_note_grid_envelope(snapshot.bass_notes, snapshot.bass, bass_note_envelope_, -1,
					  interval_seconds, 1);
	} else {
		reset_note_grid_envelope(snapshot.bass_notes, snapshot.bass, bass_note_envelope_);
	}

	if (harmonic_processed) {
		smooth_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_envelope_, -1,
					  interval_seconds, mixed_source ? 4 : 10, keyboard_new_notes);
		smooth_note_grid_envelope(snapshot.guitar_notes, snapshot.guitar, guitar_note_envelope_, -1,
					  interval_seconds, mixed_source ? 4 : 8, guitar_new_notes);
		smooth_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_envelope_, -1,
					  interval_seconds, 1);
		if (!keyboard_raw_notes)
			set_chord_from_smoothed_grid(snapshot.keyboard_chord, snapshot.keyboard_notes,
						    allow_smoothed_extensions);
		else if (!keyboard_raw_chord)
			clear_instrument_state(snapshot.keyboard_chord);
		if (!guitar_raw_notes)
			set_chord_from_smoothed_grid(snapshot.guitar_chord, snapshot.guitar_notes,
						    allow_smoothed_extensions);
		else if (!guitar_raw_chord)
			clear_instrument_state(snapshot.guitar_chord);
	} else {
		reset_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_envelope_);
		clear_instrument_state(snapshot.keyboard_chord);
		reset_note_grid_envelope(snapshot.guitar_notes, snapshot.guitar, guitar_note_envelope_);
		clear_instrument_state(snapshot.guitar_chord);
		reset_note_grid_envelope(snapshot.vocal_notes, snapshot.vocal, vocal_note_envelope_);
	}

	smooth_note_grid_envelope(snapshot.other_notes, snapshot.other, other_note_envelope_, -1,
				  interval_seconds, 8, other_new_notes);
	if (!other_raw_notes)
		set_chord_from_smoothed_grid(snapshot.other_chord, snapshot.other_notes, allow_smoothed_extensions);
	else if (!other_raw_chord)
		clear_instrument_state(snapshot.other_chord);

	return snapshot;
}

} // namespace mao
