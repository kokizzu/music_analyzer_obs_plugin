#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>

namespace {

bool is_root(const mao::AnalysisSnapshot &snapshot, const char *root)
{
	return std::strcmp(snapshot.root.label, root) == 0;
}

} // namespace

int main()
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();

	mao_test::Buffer bass = {};
	mao_test::add_sine(bass, 110.0f, 0.7f);
	auto bass_snapshot = engine.analyze(bass.data(), bass.size(), settings, "test", 0);
	if (!mao_test::contains(bass_snapshot.bass.label, "A2")) {
		std::fprintf(stderr, "expected bass A2, got %s\n", bass_snapshot.bass.label);
		return 1;
	}
	if (!mao_test::contains(bass_snapshot.root.label, "A")) {
		std::fprintf(stderr, "expected root A, got %s\n", bass_snapshot.root.label);
		return 1;
	}

	mao_test::Buffer chord = {};
	mao_test::add_sine(chord, 261.6256f, 0.35f);
	mao_test::add_sine(chord, 329.6276f, 0.35f);
	mao_test::add_sine(chord, 391.9954f, 0.35f);
	auto chord_snapshot = engine.analyze(chord.data(), chord.size(), settings, "test", 0);
	if (mao_test::contains(chord_snapshot.keyboard.label, "MAJ") ||
	    mao_test::contains(chord_snapshot.keyboard.label, "MIN")) {
		std::fprintf(stderr, "expected keyboard notes field without chord text, got %s\n",
			     chord_snapshot.keyboard.label);
		return 1;
	}
	if (!mao_test::has_note_token(chord_snapshot.keyboard.label, "C4") ||
	    !mao_test::has_note_token(chord_snapshot.keyboard.label, "E4") ||
	    !mao_test::has_note_token(chord_snapshot.keyboard.label, "G4")) {
		std::fprintf(stderr, "expected keyboard notes C4 E4 G4, got %s\n", chord_snapshot.keyboard.label);
		return 1;
	}
	if (std::strcmp(chord_snapshot.keyboard_chord.label, "C") != 0) {
		std::fprintf(stderr, "expected C keyboard chord, got %s\n", chord_snapshot.keyboard_chord.label);
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
	if (!mao_test::contains(chord_snapshot.root_candidates, "C ")) {
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
	if (!mao_test::contains(chord_snapshot.root_candidates, "C ")) {
		std::fprintf(stderr, "expected sustained root candidates to include C, got %s\n",
			     chord_snapshot.root_candidates);
		return 1;
	}
	if (chord_snapshot.root.confidence < 0.40f) {
		std::fprintf(stderr, "expected C root confidence >= 40%%, got %.0f%%\n",
			     chord_snapshot.root.confidence * 100.0f);
		return 1;
	}

	mao_test::Buffer silence = {};
	for (int i = 0; i < 20; ++i)
		chord_snapshot = engine.analyze(silence.data(), silence.size(), settings, "test", 0);
	if (!is_root(chord_snapshot, "--")) {
		std::fprintf(stderr, "expected silence to clear root, got %s\n", chord_snapshot.root.label);
		return 1;
	}

	mao_test::Buffer drum_background = mao_test::make_midi_notes({60, 64, 67}, 0.03f);
	for (int i = 0; i < 4; ++i)
		(void)engine.analyze(drum_background.data(), drum_background.size(), settings, "test", 0);

	mao_test::Buffer kick = drum_background;
	for (std::size_t i = 0; i < 900; ++i) {
		const float decay = 1.0f - static_cast<float>(i) / 900.0f;
		kick[i] += 0.85f * decay *
			   std::sin(2.0f * mao_test::kPi * 65.0f * static_cast<float>(i) / mao_test::kSampleRate);
		kick[i] += 0.24f * decay *
			   std::sin(2.0f * mao_test::kPi * 1100.0f * static_cast<float>(i) / mao_test::kSampleRate);
	}
	auto kick_snapshot = engine.analyze(kick.data(), kick.size(), settings, "test", 0);
	if (!kick_snapshot.drums[mao::Kick].active) {
		std::fprintf(stderr, "expected kick active, got %.3f\n", kick_snapshot.drums[mao::Kick].level);
		return 1;
	}

	return 0;
}
