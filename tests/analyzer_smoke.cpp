#include "analyzer.hpp"

#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>

namespace {

constexpr float kPi = 3.14159265358979323846f;

void add_sine(std::array<float, mao::kAnalysisWindow> &buffer, float freq, float amp, float sample_rate)
{
	for (std::size_t i = 0; i < buffer.size(); ++i)
		buffer[i] += amp * std::sin(2.0f * kPi * freq * static_cast<float>(i) / sample_rate);
}

bool contains(const char *text, const char *needle)
{
	return std::strstr(text, needle) != nullptr;
}

bool has_note_token(const char *text, const char *note)
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

bool is_root(const mao::AnalysisSnapshot &snapshot, const char *root)
{
	return std::strcmp(snapshot.root.label, root) == 0;
}

} // namespace

int main()
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings;
	settings.sample_rate = 48000;
	settings.sensitivity = 1.0f;
	settings.analysis_interval_seconds = 0.25f;
	settings.root_window_seconds = 15.0f;

	std::array<float, mao::kAnalysisWindow> bass = {};
	add_sine(bass, 110.0f, 0.7f, 48000.0f);
	auto bass_snapshot = engine.analyze(bass.data(), bass.size(), settings, "test", 0);
	if (!contains(bass_snapshot.bass.label, "A2")) {
		std::fprintf(stderr, "expected bass A2, got %s\n", bass_snapshot.bass.label);
		return 1;
	}
	if (!contains(bass_snapshot.root.label, "A")) {
		std::fprintf(stderr, "expected root A, got %s\n", bass_snapshot.root.label);
		return 1;
	}

	std::array<float, mao::kAnalysisWindow> chord = {};
	add_sine(chord, 261.6256f, 0.35f, 48000.0f);
	add_sine(chord, 329.6276f, 0.35f, 48000.0f);
	add_sine(chord, 391.9954f, 0.35f, 48000.0f);
	auto chord_snapshot = engine.analyze(chord.data(), chord.size(), settings, "test", 0);
	if (contains(chord_snapshot.keyboard.label, "MAJ") || contains(chord_snapshot.keyboard.label, "MIN")) {
		std::fprintf(stderr, "expected keyboard notes field without chord text, got %s\n",
			     chord_snapshot.keyboard.label);
		return 1;
	}
	if (!has_note_token(chord_snapshot.keyboard.label, "C") || !has_note_token(chord_snapshot.keyboard.label, "E") ||
	    !has_note_token(chord_snapshot.keyboard.label, "G")) {
		std::fprintf(stderr, "expected keyboard notes C E G, got %s\n", chord_snapshot.keyboard.label);
		return 1;
	}
	if (!contains(chord_snapshot.keyboard_chord.label, "C MAJ")) {
		std::fprintf(stderr, "expected C MAJ keyboard chord, got %s\n", chord_snapshot.keyboard_chord.label);
		return 1;
	}
	if (!is_root(chord_snapshot, "A")) {
		std::fprintf(stderr, "expected short chord change to preserve root A, got %s\n", chord_snapshot.root.label);
		return 1;
	}

	for (int i = 0; i < 20; ++i)
		chord_snapshot = engine.analyze(chord.data(), chord.size(), settings, "test", 0);
	if (!is_root(chord_snapshot, "A")) {
		std::fprintf(stderr, "expected root A before sustained modulation, got %s\n", chord_snapshot.root.label);
		return 1;
	}
	if (!contains(chord_snapshot.root_candidates, "C ")) {
		std::fprintf(stderr, "expected root candidates to include C during modulation, got %s\n",
			     chord_snapshot.root_candidates);
		return 1;
	}

	for (int i = 0; i < 120; ++i)
		chord_snapshot = engine.analyze(chord.data(), chord.size(), settings, "test", 0);
	if (!is_root(chord_snapshot, "C")) {
		std::fprintf(stderr, "expected sustained C modulation to switch root, got %s\n", chord_snapshot.root.label);
		return 1;
	}
	if (!contains(chord_snapshot.root_candidates, "C ")) {
		std::fprintf(stderr, "expected sustained root candidates to include C, got %s\n",
			     chord_snapshot.root_candidates);
		return 1;
	}
	if (chord_snapshot.root.confidence < 0.40f) {
		std::fprintf(stderr, "expected C root confidence >= 40%%, got %.0f%%\n",
			     chord_snapshot.root.confidence * 100.0f);
		return 1;
	}

	std::array<float, mao::kAnalysisWindow> silence = {};
	for (int i = 0; i < 20; ++i)
		chord_snapshot = engine.analyze(silence.data(), silence.size(), settings, "test", 0);
	if (!is_root(chord_snapshot, "--")) {
		std::fprintf(stderr, "expected silence to clear root, got %s\n", chord_snapshot.root.label);
		return 1;
	}

	std::array<float, mao::kAnalysisWindow> kick = {};
	for (std::size_t i = 0; i < 900; ++i) {
		const float decay = 1.0f - static_cast<float>(i) / 900.0f;
		kick[i] = 0.85f * decay * std::sin(2.0f * kPi * 65.0f * static_cast<float>(i) / 48000.0f);
	}
	auto kick_snapshot = engine.analyze(kick.data(), kick.size(), settings, "test", 0);
	if (!kick_snapshot.drums[mao::Kick].active) {
		std::fprintf(stderr, "expected kick active, got %.3f\n", kick_snapshot.drums[mao::Kick].level);
		return 1;
	}

	return 0;
}
