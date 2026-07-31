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

	InstrumentState displayed = {};
	std::snprintf(displayed.label, sizeof(displayed.label),
		      "C=Cmaj7=C7=C6=C13=Csus4=Gsus4=Em");
	NoteGrid display_grid = {};
	set_pitch(display_grid, 0, 0.92f);
	set_pitch(display_grid, 4, 0.81f);
	set_pitch(display_grid, 7, 0.76f);
	set_pitch(display_grid, 10, 0.70f);
	NoteGrid analysis_grid = display_grid;
	prune_crowded_guitar_display_label(displayed, display_grid, analysis_grid);
	runner.expect(std::strcmp(displayed.label, "C=C7=Em") == 0,
		      std::string("display crowded guitar prune: expected supported common aliases only, got `") +
			      displayed.label + "`");
	runner.expect(!chord_label_has_exact_component(displayed.label, "C13"),
		      std::string("display crowded guitar prune: expected unknown suffix pruned, got `") +
			      displayed.label + "`");

	InstrumentState unsupported_display = {};
	std::snprintf(unsupported_display.label, sizeof(unsupported_display.label),
		      "C=Cmaj7=F#7=G#7=A#7=Em=Csus4=C13");
	NoteGrid compact_c_major_seventh = {};
	set_midi(compact_c_major_seventh, 48, 0.92f);
	set_midi(compact_c_major_seventh, 52, 0.81f);
	set_midi(compact_c_major_seventh, 55, 0.76f);
	set_midi(compact_c_major_seventh, 59, 0.70f);
	prune_crowded_guitar_display_label(unsupported_display, compact_c_major_seventh,
					   compact_c_major_seventh);
	runner.expect(std::strcmp(unsupported_display.label, "C=Cmaj7=Em") == 0,
		      std::string("display crowded guitar prune: expected unsupported aliases pruned, got `") +
			      unsupported_display.label + "`");

	InstrumentState medium_unsupported_display = {};
	std::snprintf(medium_unsupported_display.label, sizeof(medium_unsupported_display.label),
		      "C=C13=Cmaj7=Cpow=Em");
	NoteGrid compact_c_major = {};
	set_midi(compact_c_major, 48, 0.92f);
	set_midi(compact_c_major, 52, 0.81f);
	set_midi(compact_c_major, 55, 0.76f);
	prune_crowded_guitar_display_label(medium_unsupported_display, compact_c_major,
					   compact_c_major);
	runner.expect(std::strcmp(medium_unsupported_display.label, "C=Cpow=Em") == 0,
		      std::string("display medium guitar prune: expected unsupported extensions pruned, got `") +
			      medium_unsupported_display.label + "`");
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

FullMixDebugCandidate make_keyboard_vocal_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Keyboard;
	debug.ownership_confidence = 0.80f;
	debug.vocal_score = 0.00f;
	debug.keyboard_score = 0.20f;
	debug.spectral_level = 0.90f;
	debug.pitch_confidence = 0.85f;
	debug.periodicity = 0.76f;
	debug.harmonic_fit_error = 0.05f;
	debug.local_noise_level = 0.05f;
	return debug;
}

void check_keyboard_owned_same_pitch_vocal_shadow_uses_weak_target_guard(Runner &runner)
{
	static constexpr int kShadowMidi = 64;
	static constexpr int kProtectedMidi = 65;

	NoteGrid vocal_grid = {};
	set_midi(vocal_grid, kShadowMidi, 0.20f);
	InstrumentState vocal_state = {};
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kShadowMidi, 0.10f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_keyboard_vocal_shadow_debug(kShadowMidi);

	suppress_named_owned_same_pitch_vocal_shadows(vocal_grid, vocal_state, keyboard_grid,
						      ownership, InstrumentKind::Keyboard, -1);
	runner.expect(note_grid_midi_visual_level(vocal_grid, kShadowMidi) <= 0.0f,
		      "same-pitch keyboard vocal shadow: expected weak keyboard-owned vocal mirror to clear");

	NoteGrid protected_vocal_grid = {};
	set_midi(protected_vocal_grid, kProtectedMidi, 0.20f);
	InstrumentState protected_vocal_state = {};
	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kProtectedMidi, 0.10f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] = make_keyboard_vocal_shadow_debug(kProtectedMidi);
	protected_ownership.debug_candidates[0].owner = InstrumentKind::Vocal;
	protected_ownership.debug_candidates[0].vocal_score = 0.24f;
	protected_ownership.debug_candidates[0].keyboard_score = 0.20f;
	suppress_named_owned_same_pitch_vocal_shadows(protected_vocal_grid,
						      protected_vocal_state,
						      protected_keyboard_grid,
						      protected_ownership,
						      InstrumentKind::Keyboard, -1);
	runner.expect(note_grid_midi_visual_level(protected_vocal_grid, kProtectedMidi) > 0.0f,
		      "same-pitch keyboard vocal shadow: expected vocal-owned note to stay visible");
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
	set_midi(protected_vocal_grid, kProtectedMidi, 0.34f);
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

FullMixDebugCandidate make_vocal_bass_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Vocal;
	debug.ownership_confidence = 0.82f;
	debug.bass_score = 0.08f;
	debug.vocal_score = 0.70f;
	debug.spectral_level = 1.00f;
	debug.pitch_confidence = 0.87f;
	debug.periodicity = 0.76f;
	debug.harmonic_fit_error = 0.04f;
	debug.local_noise_level = 0.17f;
	return debug;
}

void check_vocal_owned_same_pitch_bass_shadow_uses_measured_ratio(Runner &runner)
{
	static constexpr int kShadowMidi = 59;
	static constexpr int kProtectedMidi = 58;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kShadowMidi, 0.70f);
	InstrumentState bass_state = {};
	NoteGrid vocal_grid = {};
	set_midi(vocal_grid, kShadowMidi, 0.80f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_vocal_bass_shadow_debug(kShadowMidi);

	suppress_vocal_owned_same_pitch_bass_shadows(bass_grid, bass_state, vocal_grid,
						     ownership, -1);
	runner.expect(note_grid_midi_visual_level(bass_grid, kShadowMidi) <= 0.0f,
		      "same-pitch vocal bass shadow: expected vocal-owned bass mirror to clear");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kProtectedMidi, 0.77f);
	InstrumentState protected_bass_state = {};
	NoteGrid protected_vocal_grid = {};
	set_midi(protected_vocal_grid, kProtectedMidi, 0.80f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] = make_vocal_bass_shadow_debug(kProtectedMidi);

	suppress_vocal_owned_same_pitch_bass_shadows(protected_bass_grid,
						     protected_bass_state,
						     protected_vocal_grid,
						     protected_ownership, -1);
	runner.expect(note_grid_midi_visual_level(protected_bass_grid, kProtectedMidi) > 0.0f,
		      "same-pitch vocal bass shadow: expected stronger bass to stay visible");
}

FullMixDebugCandidate make_other_bass_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.86f;
	debug.bass_score = 0.00f;
	debug.other_score = 0.82f;
	debug.spectral_level = 0.90f;
	debug.pitch_confidence = 0.84f;
	debug.periodicity = 0.74f;
	debug.harmonic_fit_error = 0.05f;
	debug.local_noise_level = 0.12f;
	return debug;
}

void check_other_owned_same_pitch_bass_shadow_uses_measured_ratio(Runner &runner)
{
	static constexpr int kShadowMidi = 52;
	static constexpr int kProtectedMidi = 53;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kShadowMidi, 0.88f);
	InstrumentState bass_state = {};
	NoteGrid other_grid = {};
	set_midi(other_grid, kShadowMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_other_bass_shadow_debug(kShadowMidi);

	suppress_other_dominant_same_pitch_bass_shadows(bass_grid, bass_state, other_grid,
							ownership, -1);
	runner.expect(note_grid_midi_visual_level(bass_grid, kShadowMidi) <= 0.0f,
		      "same-pitch other bass shadow: expected other-owned 90% bass mirror to clear");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kProtectedMidi, 0.88f);
	InstrumentState protected_bass_state = {};
	NoteGrid protected_other_grid = {};
	set_midi(protected_other_grid, kProtectedMidi, 1.00f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] = make_other_bass_shadow_debug(kProtectedMidi);
	protected_ownership.debug_candidates[0].owner = InstrumentKind::Keyboard;
	suppress_other_dominant_same_pitch_bass_shadows(protected_bass_grid,
							protected_bass_state,
							protected_other_grid,
							protected_ownership, -1);
	runner.expect(note_grid_midi_visual_level(protected_bass_grid, kProtectedMidi) > 0.0f,
		      "same-pitch other bass shadow: expected non-other-owned 90% bass note to stay visible");
}

FullMixDebugCandidate make_other_keyboard_pitch_class_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.84f;
	debug.pitch_confidence = 0.62f;
	debug.keyboard_score = 0.04f;
	debug.other_score = 0.84f;
	debug.spectral_slope = 0.92f;
	return debug;
}

void check_other_owned_pitch_class_keyboard_shadow_is_attenuated(Runner &runner)
{
	static constexpr int kOtherMidi = 49;
	static constexpr int kKeyboardAliasMidi = kOtherMidi + 36;
	static constexpr int kProtectedNearbyAliasMidi = kOtherMidi + 12;

	NoteGrid other_grid = {};
	set_midi(other_grid, kOtherMidi, 1.00f);
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kKeyboardAliasMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_other_keyboard_pitch_class_shadow_debug(kOtherMidi);

	attenuate_other_dominant_pitch_class_keyboard_shadows(keyboard_grid, other_grid, ownership);
	const float keyboard_level = note_grid_midi_visual_level(keyboard_grid, kKeyboardAliasMidi);
	const float other_level = note_grid_midi_visual_level(other_grid, kOtherMidi);
	runner.expect(keyboard_level < other_level,
		      "other pitch-class keyboard shadow: expected keyboard octave alias below other note");
	runner.expect(keyboard_level > 0.0f,
		      "other pitch-class keyboard shadow: expected keyboard octave alias attenuated, not removed");

	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kProtectedNearbyAliasMidi, 1.00f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] =
		make_other_keyboard_pitch_class_shadow_debug(kOtherMidi);
	attenuate_other_dominant_pitch_class_keyboard_shadows(protected_keyboard_grid,
							      other_grid,
							      protected_ownership);
	runner.expect(note_grid_midi_visual_level(protected_keyboard_grid, kProtectedNearbyAliasMidi) > 0.99f,
		      "other pitch-class keyboard shadow: expected nearby keyboard alias to stay bright");
}

FullMixDebugCandidate make_electronic_keyboard_other_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.90f;
	debug.pitch_confidence = 0.76f;
	debug.periodicity = 0.88f;
	debug.keyboard_score = 0.0f;
	debug.other_score = 0.90f;
	debug.harmonicity = 2.0f;
	debug.spectral_slope = 0.40f;
	debug.local_noise_level = 0.001f;
	debug.harmonic_ratios[2] = 0.20f;
	return debug;
}

void check_electronic_keyboard_other_shadow_is_attenuated(Runner &runner)
{
	static constexpr int kKeyboardMidi = 53;
	static constexpr int kOtherAliasMidi = kKeyboardMidi + 24;

	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kKeyboardMidi, 0.66f);
	NoteGrid other_grid = {};
	set_midi(other_grid, kOtherAliasMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] =
		make_electronic_keyboard_other_shadow_debug(kOtherAliasMidi);

	attenuate_measured_electronic_keyboard_other_shadows(other_grid, keyboard_grid, ownership);
	runner.expect(note_grid_midi_visual_level(other_grid, kOtherAliasMidi) < 0.66f,
		      "electronic keyboard other shadow: expected synthetic other octave alias below keyboard support");
	runner.expect(note_grid_midi_visual_level(other_grid, kOtherAliasMidi) > 0.0f,
		      "electronic keyboard other shadow: expected alias attenuated, not removed");

	NoteGrid protected_other_grid = {};
	set_midi(protected_other_grid, kOtherAliasMidi, 1.00f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] =
		make_electronic_keyboard_other_shadow_debug(kOtherAliasMidi);
	protected_ownership.debug_candidates[0].spectral_slope = 1.30f;
	protected_ownership.debug_candidates[0].harmonic_ratios[2] = 0.90f;
	attenuate_measured_electronic_keyboard_other_shadows(protected_other_grid, keyboard_grid,
							     protected_ownership);
	runner.expect(note_grid_midi_visual_level(protected_other_grid, kOtherAliasMidi) > 0.99f,
		      "electronic keyboard other shadow: expected noisy protected other note to stay bright");
}

FullMixDebugCandidate make_high_electronic_keyboard_alias_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Keyboard;
	debug.ownership_confidence = 1.0f;
	debug.keyboard_score = 1.0f;
	debug.spectral_level = 0.80f;
	debug.pitch_confidence = 0.70f;
	debug.periodicity = 0.72f;
	debug.harmonic_fit_error = 0.12f;
	debug.local_noise_level = 0.01f;
	debug.spectral_centroid = 0.28f;
	debug.spectral_slope = 0.05f;
	debug.harmonic_ratios[1] = 1.50f;
	debug.harmonic_ratios[2] = 0.20f;
	debug.harmonic_ratios[3] = 0.02f;
	debug.harmonic_ratios[4] = 0.01f;
	return debug;
}

void check_lower_other_pitch_class_keyboard_octave_shadow_is_attenuated(Runner &runner)
{
	static constexpr int kOtherMidi = 60;
	static constexpr int kKeyboardAliasMidi = kOtherMidi + 24;

	NoteGrid other_grid = {};
	set_midi(other_grid, kOtherMidi, 0.70f);
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kKeyboardAliasMidi, 1.00f);
	InstrumentState keyboard_state = {};
	FullMixOwnership ownership = {};

	attenuate_lower_other_pitch_class_keyboard_octave_shadows(
		keyboard_grid, keyboard_state, other_grid, ownership, -1);
	runner.expect(note_grid_midi_visual_level(keyboard_grid, kKeyboardAliasMidi) <
			      note_grid_midi_visual_level(other_grid, kOtherMidi),
		      "lower other keyboard octave shadow: expected keyboard alias below lower other support");

	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kKeyboardAliasMidi, 1.00f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] =
		make_high_electronic_keyboard_alias_debug(kKeyboardAliasMidi);
	attenuate_lower_other_pitch_class_keyboard_octave_shadows(
		protected_keyboard_grid, keyboard_state, other_grid, protected_ownership, -1);
	runner.expect(note_grid_midi_visual_level(protected_keyboard_grid, kKeyboardAliasMidi) > 0.99f,
		      "lower other keyboard octave shadow: expected electronic keyboard alias to stay bright");
}

void check_lower_non_guitar_pitch_class_guitar_octave_shadow_uses_measured_levels(Runner &runner)
{
	static constexpr int kKeyboardMidi = 45;
	static constexpr int kGuitarAliasMidi = kKeyboardMidi + 12;

	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kKeyboardMidi, 0.50f);
	NoteGrid other_grid = {};
	NoteGrid guitar_grid = {};
	set_midi(guitar_grid, kGuitarAliasMidi, 0.70f);
	InstrumentState guitar_state = {};
	FullMixOwnership ownership = {};

	attenuate_lower_non_guitar_pitch_class_guitar_octave_shadows(
		guitar_grid, guitar_state, keyboard_grid, other_grid, ownership, -1);
	runner.expect(note_grid_midi_visual_level(guitar_grid, kGuitarAliasMidi) < 0.50f,
		      "lower non-guitar guitar octave shadow: expected measured alias level to attenuate");

	NoteGrid measured_threshold_keyboard_grid = {};
	set_midi(measured_threshold_keyboard_grid, kKeyboardMidi, 0.50f);
	NoteGrid measured_threshold_guitar_grid = {};
	set_midi(measured_threshold_guitar_grid, kGuitarAliasMidi, 0.66f);
	attenuate_lower_non_guitar_pitch_class_guitar_octave_shadows(
		measured_threshold_guitar_grid, guitar_state, measured_threshold_keyboard_grid, other_grid,
		ownership, -1);
	runner.expect(note_grid_midi_visual_level(measured_threshold_guitar_grid, kGuitarAliasMidi) < 0.50f,
		      "lower non-guitar guitar octave shadow: expected measured 66% alias to attenuate");

	NoteGrid below_threshold_guitar_grid = {};
	set_midi(below_threshold_guitar_grid, kGuitarAliasMidi, 0.65f);
	attenuate_lower_non_guitar_pitch_class_guitar_octave_shadows(
		below_threshold_guitar_grid, guitar_state, measured_threshold_keyboard_grid, other_grid,
		ownership, -1);
	runner.expect(note_grid_midi_visual_level(below_threshold_guitar_grid, kGuitarAliasMidi) > 0.64f,
		      "lower non-guitar guitar octave shadow: expected sub-threshold alias to stay bright");

	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kKeyboardMidi, 0.44f);
	NoteGrid protected_guitar_grid = {};
	set_midi(protected_guitar_grid, kGuitarAliasMidi, 0.70f);
	attenuate_lower_non_guitar_pitch_class_guitar_octave_shadows(
		protected_guitar_grid, guitar_state, protected_keyboard_grid, other_grid, ownership, -1);
	runner.expect(note_grid_midi_visual_level(protected_guitar_grid, kGuitarAliasMidi) > 0.69f,
		      "lower non-guitar guitar octave shadow: expected weak support to leave alias bright");
}

void check_display_ownership_scale_keeps_confirmed_mid_confidence_visible(Runner &runner)
{
	NoteCandidate weak = {};
	weak.ownership_confidence = 0.20f;
	runner.expect(note_candidate_display_ownership_scale(weak) == 1.0f,
		      "display ownership scale: expected weak mirror scale to stay raw-level controlled");

	NoteCandidate mid = {};
	mid.ownership_confidence = 0.36f;
	const float mid_scale = note_candidate_display_ownership_scale(mid);
	runner.expect(mid_scale >= 0.25f && mid_scale < 0.37f,
		      "display ownership scale: expected mid-confidence candidate to remain visibly lit");

	NoteCandidate high = {};
	high.ownership_confidence = 0.70f;
	runner.expect(std::fabs(note_candidate_display_ownership_scale(high) - 0.70f) < 0.001f,
		      "display ownership scale: expected high-confidence candidate to use linear display scale");

	NoteCandidate strong = {};
	strong.ownership_confidence = 0.90f;
	runner.expect(note_candidate_display_ownership_scale(strong) == 1.0f,
		      "display ownership scale: expected strong ownership to render at full scale");
}

int run()
{
	Runner runner;
	check_crowded_guitar_prune_modes(runner);
	check_displayed_same_root_plain_guitar_primary(runner);
	check_supported_guitar_candidate_alias_merge(runner);
	check_supported_guitar_display_extension_aliases(runner);
	check_same_pitch_guitar_bass_shadow_uses_any_matching_debug(runner);
	check_keyboard_owned_same_pitch_vocal_shadow_uses_weak_target_guard(runner);
	check_other_owned_same_pitch_vocal_shadow_uses_measured_threshold(runner);
	check_vocal_owned_same_pitch_bass_shadow_uses_measured_ratio(runner);
	check_other_owned_same_pitch_bass_shadow_uses_measured_ratio(runner);
	check_other_owned_pitch_class_keyboard_shadow_is_attenuated(runner);
	check_electronic_keyboard_other_shadow_is_attenuated(runner);
	check_lower_other_pitch_class_keyboard_octave_shadow_is_attenuated(runner);
	check_lower_non_guitar_pitch_class_guitar_octave_shadow_uses_measured_levels(runner);
	check_display_ownership_scale_keeps_confirmed_mid_confidence_visible(runner);
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
