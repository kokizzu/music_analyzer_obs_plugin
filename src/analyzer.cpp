#include "analyzer.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>

namespace mao {
namespace {

constexpr float kPi = 3.14159265358979323846f;
constexpr int kFirstMidi = 28;
constexpr int kLastMidi = 96;
constexpr float kSilenceRms = 0.0025f;

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
	const int octave = midi / 12 - 1;
	std::snprintf(dst, dst_size, "%s%d", note_name(midi), octave);
}

struct RangeResult {
	int midi = 0;
	float confidence = 0.0f;
	float score = 0.0f;
};

RangeResult dominant_note(const std::array<float, 69> &powers, int min_midi, int max_midi, bool include_harmonics)
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

std::array<float, 12> chroma_for_range(const std::array<float, 69> &powers, int min_midi, int max_midi)
{
	std::array<float, 12> chroma = {};
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);

	for (int midi = min_midi; midi <= max_midi; ++midi) {
		const float compressed = std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
		chroma[((midi % 12) + 12) % 12] += compressed;
	}

	const float max_value = *std::max_element(chroma.begin(), chroma.end());
	if (max_value > 0.0f) {
		for (float &value : chroma)
			value /= max_value;
	}

	return chroma;
}

struct ChordResult {
	char label[24] = {};
	int root = -1;
	float confidence = 0.0f;
};

ChordResult detect_chord(const std::array<float, 12> &chroma)
{
	ChordResult best;
	float best_score = 0.0f;

	for (int root = 0; root < 12; ++root) {
		const float root_power = chroma[root];
		const float fifth_power = chroma[(root + 7) % 12];
		const float major_score = root_power * 1.15f + chroma[(root + 4) % 12] + fifth_power * 0.9f -
					  chroma[(root + 3) % 12] * 0.35f;
		const float minor_score = root_power * 1.15f + chroma[(root + 3) % 12] + fifth_power * 0.9f -
					  chroma[(root + 4) % 12] * 0.35f;

		if (major_score > best_score) {
			best_score = major_score;
			best.root = root;
			std::snprintf(best.label, sizeof(best.label), "%s MAJ", note_name(root));
		}
		if (minor_score > best_score) {
			best_score = minor_score;
			best.root = root;
			std::snprintf(best.label, sizeof(best.label), "%s MIN", note_name(root));
		}
	}

	float chroma_sum = 0.0f;
	for (float value : chroma)
		chroma_sum += value;

	best.confidence = chroma_sum > 0.0f ? std::clamp(best_score / (chroma_sum + 1.0e-6f), 0.0f, 1.0f) : 0.0f;
	if (best.confidence < 0.34f) {
		best.root = -1;
		copy_text(best.label, sizeof(best.label), "--");
	}
	return best;
}

struct RootCandidate {
	std::array<float, 12> scores = {};
	int pitch_class = -1;
	float confidence = 0.0f;
	float total = 0.0f;
};

RootCandidate detect_root_candidate(const std::array<float, 69> &powers, float rms)
{
	RootCandidate candidate;
	if (rms < kSilenceRms)
		return candidate;

	for (int midi = 28; midi <= 84; ++midi) {
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

	const ChordResult chord = detect_chord(chroma_for_range(powers, 40, 84));
	if (chord.root >= 0 && chord.confidence >= 0.36f) {
		float seed_total = 0.0f;
		for (float score : candidate.scores)
			seed_total += score;
		candidate.scores[chord.root] += seed_total * chord.confidence * 0.55f;
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

float sum_notes(const std::array<float, 69> &powers, int min_midi, int max_midi)
{
	float sum = 0.0f;
	min_midi = std::max(min_midi, kFirstMidi);
	max_midi = std::min(max_midi, kLastMidi);
	for (int midi = min_midi; midi <= max_midi; ++midi)
		sum += std::sqrt(std::max(powers[midi - kFirstMidi], 0.0f));
	return sum;
}

void set_instrument_note(InstrumentState &state, const RangeResult &note, float energy, float rms)
{
	if (rms < kSilenceRms || energy < 1.0e-5f || note.confidence < 0.08f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	write_note(state.label, sizeof(state.label), note.midi);
	state.confidence = std::clamp(note.confidence * 1.8f, 0.0f, 1.0f);
}

void set_instrument_note_set(InstrumentState &state, const std::array<float, 12> &chroma, int preferred_root,
			     float energy, float rms)
{
	if (rms < kSilenceRms || energy < 1.0e-5f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	int strongest = -1;
	float strongest_score = 0.0f;
	for (int i = 0; i < 12; ++i) {
		if (chroma[i] > strongest_score) {
			strongest = i;
			strongest_score = chroma[i];
		}
	}

	if (strongest < 0 || strongest_score < 0.18f) {
		copy_text(state.label, sizeof(state.label), "--");
		state.confidence = 0.0f;
		return;
	}

	const int start = preferred_root >= 0 ? preferred_root % 12 : strongest;
	char label[24] = {};
	for (int offset = 0, written = 0; offset < 12 && written < 5; ++offset) {
		const int pitch_class = (start + offset) % 12;
		if (chroma[pitch_class] < 0.36f)
			continue;

		const char *name = note_name(pitch_class);
		const std::size_t used = std::strlen(label);
		const std::size_t needed = std::strlen(name) + (used > 0 ? 1 : 0);
		if (used + needed + 1 > sizeof(label))
			break;

		std::size_t cursor = used;
		if (cursor > 0)
			label[cursor++] = ' ';
		for (const char *p = name; *p && cursor + 1 < sizeof(label); ++p)
			label[cursor++] = *p;
		label[cursor] = '\0';
		++written;
	}

	if (!label[0])
		copy_text(label, sizeof(label), note_name(strongest));

	copy_text(state.label, sizeof(state.label), label);
	state.confidence = std::clamp(strongest_score, 0.0f, 1.0f);
}

void set_instrument_chord(InstrumentState &state, const ChordResult &chord, float energy, float rms)
{
	if (rms < kSilenceRms || energy < 1.0e-5f) {
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
	if (sample_rate != sample_rate_)
		rebuild_plans(sample_rate);
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

InstrumentState AnalysisEngine::track_root(const std::array<float, 69> &powers, float rms)
{
	constexpr uint32_t kSilenceResetWindows = 18;
	constexpr uint32_t kModulationWindows = 48;
	constexpr float kRootMemoryDecay = 0.996f;
	constexpr float kModulationLead = 1.35f;

	InstrumentState state;
	const RootCandidate candidate = detect_root_candidate(powers, rms);

	if (rms < kSilenceRms || candidate.pitch_class < 0) {
		if (++silence_windows_ >= kSilenceResetWindows) {
			root_memory_.fill(0.0f);
			locked_root_ = -1;
			pending_root_ = -1;
			pending_root_windows_ = 0;
		}

		if (locked_root_ >= 0) {
			copy_text(state.label, sizeof(state.label), note_name(locked_root_));
			state.confidence = 0.15f;
		} else {
			copy_text(state.label, sizeof(state.label), "--");
		}
		return state;
	}

	silence_windows_ = 0;

	for (int i = 0; i < 12; ++i)
		root_memory_[i] = root_memory_[i] * kRootMemoryDecay + candidate.scores[i] * candidate.confidence;

	int best = -1;
	float best_score = 0.0f;
	float total = 0.0f;
	for (int i = 0; i < 12; ++i) {
		total += root_memory_[i];
		if (root_memory_[i] > best_score) {
			best = i;
			best_score = root_memory_[i];
		}
	}

	if (locked_root_ < 0 && best >= 0 && total > 1.0e-6f) {
		locked_root_ = best;
		pending_root_ = -1;
		pending_root_windows_ = 0;
	}

	if (locked_root_ >= 0 && best >= 0 && best != locked_root_) {
		const float locked_score = root_memory_[locked_root_];
		const bool modulation =
			candidate.pitch_class == best && best_score > locked_score * kModulationLead && candidate.confidence > 0.42f;
		if (modulation) {
			if (pending_root_ != best) {
				pending_root_ = best;
				pending_root_windows_ = 1;
			} else {
				++pending_root_windows_;
			}

			if (pending_root_windows_ >= kModulationWindows) {
				locked_root_ = best;
				pending_root_ = -1;
				pending_root_windows_ = 0;
			}
		} else {
			pending_root_ = -1;
			pending_root_windows_ = 0;
		}
	} else {
		pending_root_ = -1;
		pending_root_windows_ = 0;
	}

	if (locked_root_ >= 0) {
		const float confidence = total > 1.0e-6f ? root_memory_[locked_root_] / total : 0.0f;
		copy_text(state.label, sizeof(state.label), note_name(locked_root_));
		state.confidence = std::clamp(confidence * 2.6f, 0.0f, 1.0f);
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
	copy_text(snapshot.drums[Kick].label, sizeof(snapshot.drums[Kick].label), "BASSDRUM");
	copy_text(snapshot.drums[Snare].label, sizeof(snapshot.drums[Snare].label), "SNARE");
	copy_text(snapshot.drums[HiHat].label, sizeof(snapshot.drums[HiHat].label), "HIHAT");
	copy_text(snapshot.drums[Crash].label, sizeof(snapshot.drums[Crash].label), "CRASH");
	copy_text(snapshot.drums[Tom].label, sizeof(snapshot.drums[Tom].label), "TOM");
	copy_text(snapshot.drums[Ride].label, sizeof(snapshot.drums[Ride].label), "RIDE");
	snapshot.dropped_windows = dropped_windows;

	if (!samples || count == 0) {
		copy_text(snapshot.bass.label, sizeof(snapshot.bass.label), "--");
		copy_text(snapshot.root.label, sizeof(snapshot.root.label), "--");
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
	float peak = 0.0f;
	for (std::size_t i = 0; i < usable; ++i) {
		const float sample = std::clamp(samples[i], -4.0f, 4.0f);
		sum += sample;
		square_sum += static_cast<double>(sample) * sample;
		peak = std::max(peak, std::abs(sample));
	}

	const float mean = static_cast<float>(sum / static_cast<double>(usable));
	const float rms = std::sqrt(static_cast<float>(square_sum / static_cast<double>(usable)));
	snapshot.rms = rms;
	snapshot.peak = peak;

	std::array<float, 69> note_powers = {};
	for (std::size_t i = 0; i < note_probes_.size(); ++i)
		note_powers[i] = goertzel_power(samples, usable, mean, note_probes_[i]);

	std::array<float, 15> drum_powers = {};
	for (std::size_t i = 0; i < drum_probes_.size(); ++i)
		drum_powers[i] = std::sqrt(goertzel_power(samples, usable, mean, drum_probes_[i]));

	const float low = sum_notes(note_powers, 28, 47);
	const float mid = sum_notes(note_powers, 48, 72);
	const float high = sum_notes(note_powers, 73, 96) + drum_powers[11] + drum_powers[12] + drum_powers[13];
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

		if (rms > kSilenceRms && score > trigger_threshold) {
			const float level = std::clamp((score - trigger_threshold) * 0.85f, 0.35f, 1.0f);
			drum_level_[i] = std::max(drum_level_[i], level);
		} else {
			drum_level_[i] *= 0.72f;
		}

		drum_average_[i] = drum_average_[i] * 0.92f + drum_bands[i] * 0.08f;
		snapshot.drums[i].level = drum_level_[i];
		snapshot.drums[i].active = drum_level_[i] > 0.30f;
	}

	const RangeResult bass_note = dominant_note(note_powers, 28, 52, true);
	const RangeResult guitar_note = dominant_note(note_powers, 40, 76, true);
	const RangeResult keyboard_note = dominant_note(note_powers, 48, 88, true);
	const RangeResult vocal_note = dominant_note(note_powers, 48, 84, false);
	const RangeResult other_note = dominant_note(note_powers, 60, 96, false);

	const std::array<float, 12> guitar_chroma = chroma_for_range(note_powers, 40, 76);
	const std::array<float, 12> keyboard_chroma = chroma_for_range(note_powers, 48, 88);
	const std::array<float, 12> other_chroma = chroma_for_range(note_powers, 60, 96);
	const ChordResult guitar_chord = detect_chord(guitar_chroma);
	const ChordResult keyboard_chord = detect_chord(keyboard_chroma);
	const ChordResult other_chord = detect_chord(other_chroma);

	snapshot.root = track_root(note_powers, rms);
	set_instrument_note(snapshot.bass, bass_note, low, rms);
	set_instrument_note_set(snapshot.guitar, guitar_chroma,
				guitar_chord.root >= 0 ? guitar_chord.root :
							 (guitar_note.confidence >= 0.08f ? guitar_note.midi : -1),
				mid, rms);
	set_instrument_chord(snapshot.guitar_chord, guitar_chord, mid, rms);
	set_instrument_note_set(snapshot.keyboard, keyboard_chroma,
				keyboard_chord.root >= 0 ? keyboard_chord.root :
							   (keyboard_note.confidence >= 0.08f ? keyboard_note.midi : -1),
				mid + low * 0.25f, rms);
	set_instrument_chord(snapshot.keyboard_chord, keyboard_chord, mid + low * 0.25f, rms);
	set_instrument_note(snapshot.vocal, vocal_note, mid, rms);
	set_instrument_note_set(snapshot.other, other_chroma,
				other_chord.root >= 0 ? other_chord.root :
							 (other_note.confidence >= 0.08f ? other_note.midi : -1),
				high, rms);
	set_instrument_chord(snapshot.other_chord, other_chord, high, rms);

	return snapshot;
}

} // namespace mao
