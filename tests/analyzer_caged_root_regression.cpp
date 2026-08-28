#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <cstdio>
#include <vector>

namespace {

void add_harmonic_note(mao_test::Buffer &buffer, int midi, float amplitude,
                       const std::vector<float> &profile)
{
	const float base = mao_test::midi_frequency(midi);
	for (std::size_t harmonic = 0; harmonic < profile.size(); ++harmonic)
		mao_test::add_sine(buffer, base * static_cast<float>(harmonic + 1),
				   amplitude * profile[harmonic]);
}

void print_grid(const char *name, const mao::NoteGrid &grid)
{
	std::printf(" %s=", name);
	for (const mao::NoteCell &cell : grid.cells) {
		if (cell.active)
			std::printf("%s(%.2f)", cell.label, cell.level);
	}
}

} // namespace

int main()
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> keyboard_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	add_harmonic_note(buffer, 31, 0.42f, bass_profile);
	for (int midi : {55, 59, 62})
		add_harmonic_note(buffer, midi, 0.22f, keyboard_profile);
	for (int midi : {48, 52, 55, 60, 64})
		add_harmonic_note(buffer, midi, 0.20f, guitar_profile);

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 8; ++frame) {
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);
		std::printf("frame=%d bass=%s global=%s guitar=%s raw=%s smooth=%s\n", frame + 1,
			snapshot.bass.label, snapshot.global_chord.label, snapshot.guitar_chord.label,
			snapshot.guitar_raw_chord.label, snapshot.guitar_smoothed_chord.label);
		print_grid("guitar", snapshot.guitar_notes);
		print_grid("analysis", snapshot.guitar_chord_analysis_notes);
		print_grid("smooth", snapshot.guitar_chord_smoothed_notes);
		std::printf(" chroma=");
		for (float value : snapshot.global_chord_debug_chroma)
			std::printf("%.2f,", value);
		std::printf("\n");
		if (frame == 7) {
			for (std::size_t index = 0; index < snapshot.full_mix_debug_candidate_count; ++index) {
				const mao::FullMixDebugCandidate &candidate = snapshot.full_mix_debug_candidates[index];
				std::printf("candidate midi=%d owner=%d level=%.2f conf=%.2f harmonic=%.2f fit=%.2f\n",
					candidate.midi, static_cast<int>(candidate.owner), candidate.spectral_level,
					candidate.pitch_confidence, candidate.harmonicity, candidate.harmonic_fit_error);
			}
		}
	}

	mao_test::Buffer suspension = {};
	for (int midi : {55, 60, 62})
		add_harmonic_note(suspension, midi, 0.22f, guitar_profile);
	mao::AnalysisEngine suspension_engine;
	for (int frame = 0; frame < 4; ++frame) {
		const mao::AnalysisSnapshot suspension_snapshot = suspension_engine.analyze(
			suspension.data(), suspension.size(), settings, "full mix", 0);
		std::printf("sus-frame=%d global=%s guitar=%s raw=%s\n", frame + 1,
			suspension_snapshot.global_chord.label, suspension_snapshot.guitar_chord.label,
			suspension_snapshot.guitar_raw_chord.label);
	}
	return 0;
}
