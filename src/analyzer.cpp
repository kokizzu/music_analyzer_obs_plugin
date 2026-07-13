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
			std::snprintf(best.label, sizeof(best.label), "%s MAJ", note_name(root));
		}
		if (minor_score > best_score) {
			best_score = minor_score;
			std::snprintf(best.label, sizeof(best.label), "%s MIN", note_name(root));
		}
	}

	float chroma_sum = 0.0f;
	for (float value : chroma)
		chroma_sum += value;

	best.confidence = chroma_sum > 0.0f ? std::clamp(best_score / (chroma_sum + 1.0e-6f), 0.0f, 1.0f) : 0.0f;
	if (best.confidence < 0.34f)
		copy_text(best.label, sizeof(best.label), "--");
	return best;
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

void set_instrument_chord_or_note(InstrumentState &state, const ChordResult &chord, const RangeResult &note,
				  float energy, float rms)
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

	set_instrument_note(state, note, energy, rms);
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
		copy_text(snapshot.guitar.label, sizeof(snapshot.guitar.label), "--");
		copy_text(snapshot.keyboard.label, sizeof(snapshot.keyboard.label), "--");
		copy_text(snapshot.vocal.label, sizeof(snapshot.vocal.label), "--");
		copy_text(snapshot.other.label, sizeof(snapshot.other.label), "--");
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

	const ChordResult guitar_chord = detect_chord(chroma_for_range(note_powers, 40, 76));
	const ChordResult keyboard_chord = detect_chord(chroma_for_range(note_powers, 48, 88));
	const ChordResult other_chord = detect_chord(chroma_for_range(note_powers, 60, 96));

	set_instrument_note(snapshot.bass, bass_note, low, rms);
	set_instrument_chord_or_note(snapshot.guitar, guitar_chord, guitar_note, mid, rms);
	set_instrument_chord_or_note(snapshot.keyboard, keyboard_chord, keyboard_note, mid + low * 0.25f, rms);
	set_instrument_note(snapshot.vocal, vocal_note, mid, rms);
	set_instrument_chord_or_note(snapshot.other, other_chord, other_note, high, rms);

	return snapshot;
}

} // namespace mao
