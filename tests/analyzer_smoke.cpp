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

} // namespace

int main()
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings;
	settings.sample_rate = 48000;
	settings.sensitivity = 1.0f;

	std::array<float, mao::kAnalysisWindow> bass = {};
	add_sine(bass, 110.0f, 0.7f, 48000.0f);
	auto bass_snapshot = engine.analyze(bass.data(), bass.size(), settings, "test", 0);
	if (!contains(bass_snapshot.bass.label, "A2")) {
		std::fprintf(stderr, "expected bass A2, got %s\n", bass_snapshot.bass.label);
		return 1;
	}

	std::array<float, mao::kAnalysisWindow> chord = {};
	add_sine(chord, 261.6256f, 0.35f, 48000.0f);
	add_sine(chord, 329.6276f, 0.35f, 48000.0f);
	add_sine(chord, 391.9954f, 0.35f, 48000.0f);
	auto chord_snapshot = engine.analyze(chord.data(), chord.size(), settings, "test", 0);
	if (!contains(chord_snapshot.keyboard.label, "C")) {
		std::fprintf(stderr, "expected C keyboard chord/note, got %s\n", chord_snapshot.keyboard.label);
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
