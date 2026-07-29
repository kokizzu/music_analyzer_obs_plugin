#include "../src/analyzer.cpp"

#include <cstdio>
#include <cstring>
#include <string>

namespace mao {
namespace test_internal {

struct Runner {
	int checks = 0;
	int failures = 0;

	void expect(bool ok, const std::string &message)
	{
		++checks;
		if (!ok) {
			++failures;
			std::fprintf(stderr, "%s\n", message.c_str());
		}
	}
};

ChordResult make_crowded_chord(const char *label)
{
	ChordResult chord;
	std::snprintf(chord.label, sizeof(chord.label), "%s", label);
	chord.root = 0;
	chord.confidence = 0.80f;
	chord.uncertain = false;
	return chord;
}

void set_pitch(NoteGrid &grid, int pitch_class, float level)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	NoteCell &cell = grid.cells[static_cast<std::size_t>(pitch_class)];
	cell.active = true;
	cell.level = level;
	cell.visual_level = level;
	cell.midi = 60 + pitch_class;
}

void set_probe_level(std::array<float, kNoteProbeCount> &powers, int midi, float level)
{
	if (midi < kFirstMidi || midi > kLastMidi)
		return;
	powers[static_cast<std::size_t>(midi - kFirstMidi)] = level * level;
}

void check_crowded_guitar_prune_modes(Runner &runner)
{
	static constexpr const char *kCrowdedLabel = "Csus2=Gsus4=C=Cm=Cmaj7=Cpow=Caug";

	ChordResult isolated = make_crowded_chord(kCrowdedLabel);
	prune_crowded_guitar_chord_label(isolated, false);
	runner.expect(chord_label_has_exact_component(isolated.label, "Csus2"),
		      std::string("isolated crowded guitar prune: expected primary, got `") + isolated.label +
			      "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Gsus4"),
		      std::string("isolated crowded guitar prune: expected equivalent sus alias, got `") +
			      isolated.label + "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Cpow"),
		      std::string("isolated crowded guitar prune: expected no-third alias, got `") +
			      isolated.label + "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Caug"),
		      std::string("isolated crowded guitar prune: expected same-root altered alias, got `") +
			      isolated.label + "`");

	ChordResult mixed = make_crowded_chord(kCrowdedLabel);
	prune_crowded_guitar_chord_label(mixed, true);
	runner.expect(std::strcmp(mixed.label, "Csus2=Gsus4=C=Cm") == 0,
		      std::string("mixed crowded guitar prune: expected strict primary/equivalent/plain label, got `") +
			      mixed.label + "`");
	runner.expect(chord_label_component_count(mixed.label) < chord_label_component_count(isolated.label),
		      std::string("mixed crowded guitar prune: expected fewer components than isolated, got mixed `") +
			      mixed.label + "` isolated `" + isolated.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Cpow"),
		      std::string("mixed crowded guitar prune: expected no-third alias pruned, got `") +
			      mixed.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Caug"),
		      std::string("mixed crowded guitar prune: expected altered alias pruned, got `") +
			      mixed.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Cmaj7"),
		      std::string("mixed crowded guitar prune: expected extension alias pruned, got `") +
			      mixed.label + "`");
}

void check_displayed_same_root_plain_guitar_primary(Runner &runner)
{
	InstrumentState state = {};
	std::snprintf(state.label, sizeof(state.label), "Cm=G=Cpow=C");
	state.confidence = 0.55f;
	NoteGrid display_grid = {};
	set_pitch(display_grid, 0, 1.00f);
	set_pitch(display_grid, 7, 0.47f);
	set_pitch(display_grid, 11, 0.76f);
	NoteGrid analysis_grid = {};
	set_pitch(analysis_grid, 0, 1.00f);
	set_pitch(analysis_grid, 2, 0.01f);
	set_pitch(analysis_grid, 4, 0.01f);
	set_pitch(analysis_grid, 7, 0.59f);
	set_pitch(analysis_grid, 8, 0.05f);
	set_pitch(analysis_grid, 11, 0.61f);
	std::array<float, kNoteProbeCount> powers = {};
	set_probe_level(powers, 51, 0.002f);
	set_probe_level(powers, 52, 0.010f);

	promote_displayed_same_root_plain_guitar_primary(state, display_grid, analysis_grid,
							 powers, kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(std::strcmp(state.label, "C=Cm=G=Cpow") == 0,
		      std::string("displayed same-root guitar primary: expected C promoted, got `") +
			      state.label + "`");

	InstrumentState protected_state = {};
	std::snprintf(protected_state.label, sizeof(protected_state.label), "C=Cm");
	protected_state.confidence = 0.62f;
	NoteGrid protected_grid = {};
	set_pitch(protected_grid, 0, 1.00f);
	set_pitch(protected_grid, 4, 0.80f);
	set_pitch(protected_grid, 7, 0.70f);
	std::array<float, kNoteProbeCount> protected_powers = {};
	set_probe_level(protected_powers, 63, 0.002f);
	set_probe_level(protected_powers, 64, 0.024f);

	promote_displayed_same_root_plain_guitar_primary(protected_state, protected_grid,
							 protected_grid, protected_powers,
							 kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(std::strcmp(protected_state.label, "C=Cm") == 0,
		      std::string("displayed same-root guitar primary: expected protected C primary, got `") +
			      protected_state.label + "`");
}

int run()
{
	Runner runner;
	check_crowded_guitar_prune_modes(runner);
	check_displayed_same_root_plain_guitar_primary(runner);
	if (runner.failures) {
		std::fprintf(stderr, "analyzer_internal: %d/%d checks failed\n", runner.failures,
			     runner.checks);
		return 1;
	}
	std::printf("analyzer_internal: %d checks passed\n", runner.checks);
	return 0;
}

} // namespace test_internal
} // namespace mao

int main()
{
	return mao::test_internal::run();
}
