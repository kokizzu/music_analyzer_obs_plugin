#pragma once

#include "analyzer.hpp"

#include <array>
#include <cmath>
#include <cstring>
#include <string>
#include <vector>

namespace mao_test {

constexpr float kPi = 3.14159265358979323846f;
constexpr float kSampleRate = 48000.0f;

using Buffer = std::array<float, mao::kAnalysisWindow>;

inline const char *note_name(int midi)
{
	static constexpr const char *kNames[12] = {"C", "C#", "D", "D#", "E", "F",
						   "F#", "G", "G#", "A", "A#", "B"};
	return kNames[((midi % 12) + 12) % 12];
}

inline float midi_frequency(int midi)
{
	return 440.0f * std::pow(2.0f, (static_cast<float>(midi) - 69.0f) / 12.0f);
}

inline std::string note_label(int midi)
{
	return std::string(note_name(midi)) + std::to_string(midi / 12 - 1);
}

inline void add_sine(Buffer &buffer, float freq, float amp, float sample_rate = kSampleRate)
{
	for (std::size_t i = 0; i < buffer.size(); ++i)
		buffer[i] += amp * std::sin(2.0f * kPi * freq * static_cast<float>(i) / sample_rate);
}

inline void add_midi_note(Buffer &buffer, int midi, float amp = 0.35f, float sample_rate = kSampleRate)
{
	add_sine(buffer, midi_frequency(midi), amp, sample_rate);
}

inline Buffer make_midi_notes(const std::vector<int> &midis, float amp = 0.35f)
{
	Buffer buffer = {};
	for (int midi : midis)
		add_midi_note(buffer, midi, amp);
	return buffer;
}

inline bool contains(const char *text, const char *needle)
{
	return text && needle && std::strstr(text, needle) != nullptr;
}

inline bool has_note_token(const char *text, const char *note)
{
	if (!text || !note)
		return false;

	const std::size_t note_len = std::strlen(note);
	const char *cursor = text;
	while (*cursor) {
		while (*cursor == ' ')
			++cursor;
		const char *end = cursor;
		while (*end && *end != ' ')
			++end;
		if (static_cast<std::size_t>(end - cursor) == note_len && std::strncmp(cursor, note, note_len) == 0)
			return true;
		cursor = end;
	}

	return false;
}

inline mao::AnalysisSettings default_settings()
{
	mao::AnalysisSettings settings;
	settings.sample_rate = static_cast<uint32_t>(kSampleRate);
	settings.sensitivity = 1.0f;
	settings.analysis_interval_seconds = 0.25f;
	settings.analysis_window_samples = static_cast<uint32_t>(mao::kLegacyAnalysisWindow);
	settings.root_window_seconds = 15.0f;
	return settings;
}

} // namespace mao_test
