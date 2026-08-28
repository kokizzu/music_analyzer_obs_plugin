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

} // namespace

int main()
{
	mao_test::Buffer buffer = {};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.24f, 0.10f};
	for (int midi : {60, 64, 67})
		add_harmonic_note(buffer, midi, 0.28f, key_profile);
	for (int midi : {54, 58})
		add_harmonic_note(buffer, midi, 0.18f, guitar_profile);
	mao_test::add_midi_note(buffer, 74, 0.12f);

	mao::AnalysisEngine engine;
	const mao::AnalysisSettings settings = mao_test::default_settings();
	const mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);
	const std::size_t hihat = static_cast<std::size_t>(mao::HiHat);
	std::printf(
		"hihat active=%d level=%.6f band=%.6f segment=%.6f trigger=%.6f threshold=%.6f "
		"onset=%.6f transient=%.6f energy=%.6f/%.6f/%.6f flags=%llu\n",
		snapshot.drums[hihat].active ? 1 : 0, snapshot.drums[hihat].level,
		snapshot.drum_debug_bands[hihat], snapshot.drum_debug_segment_bands[hihat],
		snapshot.drum_debug_trigger_scores[hihat], snapshot.drum_debug_trigger_thresholds[hihat],
		snapshot.drum_debug_onset, snapshot.drum_debug_transient_ratio, snapshot.low_energy,
		snapshot.mid_energy, snapshot.high_energy,
		static_cast<unsigned long long>(snapshot.drum_debug_rule_flags));
	return snapshot.drums[hihat].active ? 1 : 0;
}
