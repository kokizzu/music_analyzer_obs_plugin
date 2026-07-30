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

void set_midi(NoteGrid &grid, int midi, float level)
{
	const int pitch_class = midi_pitch_class(midi);
	NoteCell &cell = grid.cells[static_cast<std::size_t>(pitch_class)];
	cell.active = true;
	cell.level = level;
	cell.visual_level = level;
	cell.midi = midi;
	std::snprintf(cell.label, sizeof(cell.label), "%d", midi);
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

void check_supported_guitar_candidate_alias_merge(Runner &runner)
{
	InstrumentState state = {};
	std::snprintf(state.label, sizeof(state.label), "D=Bm");
	state.confidence = 0.55f;
	ChordResult source = make_crowded_chord("D=Bm=D6=Bm7");
	source.root = 2;
	source.confidence = 0.62f;

	NoteGrid display_grid = {};
	set_pitch(display_grid, 2, 0.88f);
	set_pitch(display_grid, 6, 0.74f);
	set_pitch(display_grid, 9, 0.69f);
	set_pitch(display_grid, 11, 0.64f);
	NoteGrid analysis_grid = {};
	set_pitch(analysis_grid, 2, 0.91f);
	set_pitch(analysis_grid, 6, 0.80f);
	set_pitch(analysis_grid, 9, 0.71f);
	set_pitch(analysis_grid, 11, 0.67f);

	append_supported_guitar_candidate_aliases_to_display(state, source,
							     display_grid, analysis_grid);
	runner.expect(chord_label_has_exact_component(state.label, "D6"),
		      std::string("supported guitar alias merge: expected D6 appended, got `") +
			      state.label + "`");
	runner.expect(chord_label_has_exact_component(state.label, "Bm7"),
		      std::string("supported guitar alias merge: expected Bm7 appended, got `") +
			      state.label + "`");
	runner.expect(state.confidence >= source.confidence,
		      "supported guitar alias merge: expected confidence updated from source");

	InstrumentState protected_state = {};
	std::snprintf(protected_state.label, sizeof(protected_state.label), "D");
	protected_state.confidence = 0.55f;
	ChordResult unsupported = make_crowded_chord("D=Dmaj7");
	unsupported.root = 2;
	unsupported.confidence = 0.62f;
	NoteGrid triad_grid = {};
	set_pitch(triad_grid, 2, 0.90f);
	set_pitch(triad_grid, 6, 0.76f);
	set_pitch(triad_grid, 9, 0.70f);

	append_supported_guitar_candidate_aliases_to_display(protected_state, unsupported,
							     triad_grid, triad_grid);
	runner.expect(!chord_label_has_exact_component(protected_state.label, "Dmaj7"),
		      std::string("supported guitar alias merge: expected missing maj7 tone pruned, got `") +
			      protected_state.label + "`");

	InstrumentState clean_primary_state = {};
	std::snprintf(clean_primary_state.label, sizeof(clean_primary_state.label), "C");
	clean_primary_state.confidence = 0.64f;
	ChordResult relative_minor = make_crowded_chord("C=Em");
	relative_minor.root = 0;
	relative_minor.confidence = 0.64f;
	NoteGrid clean_display = {};
	set_pitch(clean_display, 0, 0.90f);
	set_pitch(clean_display, 4, 0.82f);
	set_pitch(clean_display, 7, 0.74f);
	NoteGrid analysis_with_relative_minor = clean_display;
	set_pitch(analysis_with_relative_minor, 11, 0.35f);

	append_supported_guitar_candidate_aliases_to_display(clean_primary_state, relative_minor,
							     clean_display,
							     analysis_with_relative_minor);
	runner.expect(std::strcmp(clean_primary_state.label, "C") == 0,
		      std::string("supported guitar alias merge: expected clean C primary protected, got `") +
			      clean_primary_state.label + "`");
}

void check_supported_guitar_display_extension_aliases(Runner &runner)
{
	InstrumentState state = {};
	std::snprintf(state.label, sizeof(state.label), "Gmaj7=G=Bm=Gmaj9");
	state.confidence = 0.58f;
	NoteGrid display_grid = {};
	for (int pitch_class : {2, 6, 7, 8, 9, 11})
		set_pitch(display_grid, pitch_class, 0.70f);
	NoteGrid analysis_grid = display_grid;

	append_supported_guitar_display_extension_aliases(state, display_grid, analysis_grid);
	runner.expect(chord_label_has_exact_component(state.label, "Gadd9"),
		      std::string("supported guitar display extensions: expected Gadd9 appended, got `") +
			      state.label + "`");
	runner.expect(chord_label_has_exact_component(state.label, "Bm7"),
		      std::string("supported guitar display extensions: expected Bm7 appended, got `") +
			      state.label + "`");
	runner.expect(!chord_label_has_exact_component(state.label, "Bm6"),
		      std::string("supported guitar display extensions: expected alias cap before Bm6, got `") +
			      state.label + "`");

	InstrumentState triad_state = {};
	std::snprintf(triad_state.label, sizeof(triad_state.label), "D");
	triad_state.confidence = 0.62f;
	NoteGrid triad_grid = {};
	set_pitch(triad_grid, 2, 0.86f);
	set_pitch(triad_grid, 6, 0.74f);
	set_pitch(triad_grid, 9, 0.69f);

	append_supported_guitar_display_extension_aliases(triad_state, triad_grid, triad_grid);
	runner.expect(std::strcmp(triad_state.label, "D") == 0,
		      std::string("supported guitar display extensions: expected missing extension tones ignored, got `") +
			      triad_state.label + "`");

	char small[7] = "C";
	append_chord_label_component(small, sizeof(small), "Dmaj7", 5);
	runner.expect(std::strcmp(small, "C") == 0,
		      std::string("chord label append: expected partial component skipped, got `") +
			      small + "`");
}

void check_same_pitch_guitar_bass_shadow_uses_any_matching_debug(Runner &runner)
{
	static constexpr int kMidi = 52;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kMidi, 0.64f);
	InstrumentState bass_state = {};
	NoteGrid guitar_grid = {};
	set_midi(guitar_grid, kMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 2;
	ownership.debug_candidates[0].midi = kMidi;
	ownership.debug_candidates[0].owner = InstrumentKind::Keyboard;
	ownership.debug_candidates[0].ownership_confidence = 0.80f;
	ownership.debug_candidates[0].guitar_score = 0.70f;
	ownership.debug_candidates[0].bass_score = 0.00f;
	ownership.debug_candidates[0].local_noise_level = 0.05f;
	ownership.debug_candidates[1].midi = kMidi;
	ownership.debug_candidates[1].owner = InstrumentKind::Guitar;
	ownership.debug_candidates[1].guitar_score = 0.30f;
	ownership.debug_candidates[1].bass_score = 0.00f;
	ownership.debug_candidates[1].local_noise_level = 0.05f;

	suppress_guitar_dominant_same_pitch_bass_shadows(bass_grid, bass_state, guitar_grid, ownership,
							 -1, false);
	runner.expect(note_grid_midi_visual_level(bass_grid, kMidi) <= 0.0f,
		      "same-pitch guitar bass shadow: expected non-best guitar-owned debug candidate "
		      "to clear bass E3");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kMidi, 0.76f);
	InstrumentState protected_bass_state = {};
	suppress_guitar_dominant_same_pitch_bass_shadows(protected_bass_grid,
							 protected_bass_state, guitar_grid, ownership,
							 -1, false);
	runner.expect(note_grid_midi_visual_level(protected_bass_grid, kMidi) > 0.0f,
		      "same-pitch guitar bass shadow: expected strong bass E3 to stay visible");
}

FullMixDebugCandidate make_adjacent_other_vocal_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.82f;
	debug.vocal_score = 0.00f;
	debug.other_score = 0.82f;
	debug.spectral_level = 0.75f;
	debug.pitch_confidence = 0.70f;
	debug.periodicity = 0.72f;
	debug.harmonic_fit_error = 0.10f;
	debug.local_noise_level = 0.10f;
	debug.adjacent_lower_ratio = 0.04f;
	debug.harmonic_ratios[1] = 0.40f;
	debug.harmonic_ratios[2] = 0.20f;
	return debug;
}

void check_other_owned_same_pitch_vocal_shadow_uses_measured_threshold(Runner &runner)
{
	static constexpr int kShadowMidi = 60;
	static constexpr int kProtectedMidi = 62;

	NoteGrid vocal_grid = {};
	set_midi(vocal_grid, kShadowMidi, 0.20f);
	InstrumentState vocal_state = {};
	NoteGrid other_grid = {};
	set_midi(other_grid, kShadowMidi, 0.67f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_adjacent_other_vocal_shadow_debug(kShadowMidi);
	runner.expect(measured_adjacent_vocal_display_supported(ownership.debug_candidates[0]),
		      "same-pitch other vocal shadow: expected fixture to exercise adjacent-vocal guard");

	suppress_named_owned_same_pitch_vocal_shadows(vocal_grid, vocal_state, other_grid, ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(vocal_grid, kShadowMidi) <= 0.0f,
		      "same-pitch other vocal shadow: expected measured low-level vocal mirror to clear");

	NoteGrid protected_vocal_grid = {};
	set_midi(protected_vocal_grid, kProtectedMidi, 0.30f);
	InstrumentState protected_vocal_state = {};
	NoteGrid protected_other_grid = {};
	set_midi(protected_other_grid, kProtectedMidi, 0.67f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] =
		make_adjacent_other_vocal_shadow_debug(kProtectedMidi);
	suppress_named_owned_same_pitch_vocal_shadows(protected_vocal_grid,
						      protected_vocal_state,
						      protected_other_grid,
						      protected_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(protected_vocal_grid, kProtectedMidi) > 0.0f,
		      "same-pitch other vocal shadow: expected stronger protected vocal to stay visible");
}

int run()
{
	Runner runner;
	check_crowded_guitar_prune_modes(runner);
	check_displayed_same_root_plain_guitar_primary(runner);
	check_supported_guitar_candidate_alias_merge(runner);
	check_supported_guitar_display_extension_aliases(runner);
	check_same_pitch_guitar_bass_shadow_uses_any_matching_debug(runner);
	check_other_owned_same_pitch_vocal_shadow_uses_measured_threshold(runner);
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
