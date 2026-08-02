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

	ChordResult medium_mixed = make_crowded_chord("A=A7=Amaj7=Am");
	prune_crowded_guitar_chord_label(medium_mixed, true);
	runner.expect(std::strcmp(medium_mixed.label, "A=Am") == 0,
		      std::string("mixed medium guitar prune: expected plain major/minor aliases only, got `") +
			      medium_mixed.label + "`");

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

	InstrumentState compact_supported_display = {};
	std::snprintf(compact_supported_display.label, sizeof(compact_supported_display.label),
		      "C=Cmaj7=Em");
	prune_crowded_guitar_display_label(compact_supported_display, compact_c_major_seventh,
					   compact_c_major_seventh);
	runner.expect(std::strcmp(compact_supported_display.label, "C=Cmaj7=Em") == 0,
		      std::string("display compact guitar prune: expected compact extension label preserved, got `") +
			      compact_supported_display.label + "`");
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

void check_displayed_supported_plain_guitar_primary(Runner &runner)
{
	InstrumentState state = {};
	std::snprintf(state.label, sizeof(state.label), "D#m=B");
	state.confidence = 0.62f;
	NoteGrid display_grid = {};
	set_pitch(display_grid, 3, 0.30f);
	set_pitch(display_grid, 6, 0.84f);
	set_pitch(display_grid, 11, 1.00f);
	NoteGrid analysis_grid = {};
	set_pitch(analysis_grid, 3, 0.26f);
	set_pitch(analysis_grid, 4, 0.06f);
	set_pitch(analysis_grid, 5, 0.08f);
	set_pitch(analysis_grid, 6, 0.73f);
	set_pitch(analysis_grid, 7, 0.11f);
	set_pitch(analysis_grid, 11, 1.00f);

	promote_displayed_supported_plain_guitar_primary(state, display_grid, analysis_grid);
	runner.expect(std::strcmp(state.label, "B=D#m") == 0,
		      std::string("displayed supported guitar primary: expected B promoted, got `") +
			      state.label + "`");

	InstrumentState protected_state = {};
	std::snprintf(protected_state.label, sizeof(protected_state.label), "Am=E");
	protected_state.confidence = 0.68f;
	NoteGrid protected_grid = {};
	set_pitch(protected_grid, 0, 0.84f);
	set_pitch(protected_grid, 4, 0.74f);
	set_pitch(protected_grid, 7, 0.62f);
	set_pitch(protected_grid, 9, 0.93f);
	promote_displayed_supported_plain_guitar_primary(protected_state, protected_grid,
							protected_grid);
	runner.expect(std::strcmp(protected_state.label, "Am=E") == 0,
			      std::string("displayed supported guitar primary: expected protected Am primary, got `") +
			      protected_state.label + "`");
}

void check_source_supported_plain_guitar_alias_recovery(Runner &runner)
{
	InstrumentState state = {};
	std::snprintf(state.label, sizeof(state.label), "B=Bmaj7");
	state.confidence = 0.58f;
	ChordResult source = make_crowded_chord("B=D#m=Bmaj7");
	source.root = 11;
	source.confidence = 0.64f;
	NoteGrid display_grid = {};
	set_pitch(display_grid, 3, 0.42f);
	set_pitch(display_grid, 6, 0.84f);
	set_pitch(display_grid, 11, 1.00f);
	NoteGrid analysis_grid = {};
	set_pitch(analysis_grid, 3, 0.38f);
	set_pitch(analysis_grid, 6, 0.82f);
	set_pitch(analysis_grid, 10, 0.54f);
	set_pitch(analysis_grid, 11, 1.00f);

	append_source_supported_plain_guitar_aliases_after_prune(state, source,
								 display_grid, analysis_grid);
	runner.expect(chord_label_has_exact_component(state.label, "D#m"),
		      std::string("source-supported guitar alias recovery: expected D#m appended, got `") +
			      state.label + "`");
	runner.expect(state.confidence >= source.confidence,
		      "source-supported guitar alias recovery: expected confidence updated from source");

	InstrumentState protected_state = {};
	std::snprintf(protected_state.label, sizeof(protected_state.label),
		      "E=Esus4=Asus2=Edim=Apow=Emaj7");
	protected_state.confidence = 0.62f;
	ChordResult protected_source = make_crowded_chord("E=Esus4=Asus2=Edim=Am=Apow");
	protected_source.root = 4;
	protected_source.confidence = 0.69f;
	NoteGrid protected_display = {};
	set_pitch(protected_display, 4, 0.88f);
	set_pitch(protected_display, 9, 0.71f);
	set_pitch(protected_display, 11, 0.56f);
	NoteGrid protected_analysis = protected_display;
	set_pitch(protected_analysis, 0, 0.37f);

	append_source_supported_plain_guitar_aliases_after_prune(protected_state, protected_source,
								 protected_display, protected_analysis);
	runner.expect(!chord_label_has_exact_component(protected_state.label, "Am"),
		      std::string("source-supported guitar alias recovery: expected root-fifth-only Am protected, got `") +
			      protected_state.label + "`");
}

void check_plain_guitar_voicing_rejects_crowded_root_fifth_quality(Runner &runner)
{
	ChordResult f_major = make_crowded_chord("F");
	f_major.root = 5;

	NoteGrid compact_root_fifth = {};
	set_midi(compact_root_fifth, 41, 0.95f);
	set_midi(compact_root_fifth, 48, 0.72f);

	NoteGrid compact_with_third = compact_root_fifth;
	set_midi(compact_with_third, 45, 0.28f);
	runner.expect(primary_guitar_chord_has_playable_voicing(f_major, compact_root_fifth,
								compact_with_third),
		      "plain guitar voicing: expected compact hidden-third F chord to remain playable");

	NoteGrid crowded_analysis = compact_with_third;
	set_midi(crowded_analysis, 46, 0.18f);
	set_midi(crowded_analysis, 50, 0.16f);
	set_midi(crowded_analysis, 53, 0.14f);
	set_midi(crowded_analysis, 55, 0.13f);
	set_midi(crowded_analysis, 56, 0.12f);
	runner.expect(!primary_guitar_chord_has_playable_voicing(f_major, compact_root_fifth,
								 crowded_analysis),
		      "plain guitar voicing: expected crowded root-fifth harmonics not to validate F");

	ChordResult c_minor = make_crowded_chord("Cm");
	c_minor.root = 0;
	NoteGrid single_visible_root = {};
	set_midi(single_visible_root, 48, 0.92f);
	NoteGrid analysis_only_minor = single_visible_root;
	set_midi(analysis_only_minor, 51, 0.44f);
	set_midi(analysis_only_minor, 55, 0.67f);
	set_midi(analysis_only_minor, 59, 0.22f);
	runner.expect(!primary_guitar_chord_has_playable_voicing(c_minor, single_visible_root,
								 analysis_only_minor),
		      "plain guitar voicing: expected one visible pitch class not to validate analysis-only Cm");

	NoteGrid visible_root_third = {};
	set_midi(visible_root_third, 41, 0.95f);
	set_midi(visible_root_third, 45, 0.52f);
	runner.expect(primary_guitar_chord_has_playable_voicing(f_major, visible_root_third,
								crowded_analysis),
		      "plain guitar voicing: expected visible root-third F chord to remain playable");

	ChordResult f_power = make_crowded_chord("Fpow");
	f_power.root = 5;
	runner.expect(primary_guitar_chord_has_playable_voicing(f_power, compact_root_fifth,
								crowded_analysis),
		      "plain guitar voicing: expected root-fifth power chord to remain playable");
}

void check_displayed_guitar_single_note_probe_profile(Runner &runner)
{
	InstrumentState displayed = {};
	std::snprintf(displayed.label, sizeof(displayed.label), "Fm=Fpow");
	displayed.confidence = 1.00f;
	InstrumentState empty_smoothed = {};
	std::snprintf(empty_smoothed.label, sizeof(empty_smoothed.label), "--");
	empty_smoothed.confidence = 0.0f;

	std::array<float, kNoteProbeCount> weak_third_powers = {};
	set_probe_level(weak_third_powers, 53, 0.95f);
	set_probe_level(weak_third_powers, 56, 0.20f);
	set_probe_level(weak_third_powers, 60, 0.52f);
	runner.expect(displayed_guitar_chord_has_single_note_probe_profile(
			      displayed, empty_smoothed, weak_third_powers, kGuitarMinMidi,
			      kGuitarMaxMidi),
		      "displayed guitar single-note profile: expected weak-third Fm probe profile to suppress");

	InstrumentState smoothed = displayed;
	runner.expect(!displayed_guitar_chord_has_single_note_probe_profile(
			      displayed, smoothed, weak_third_powers, kGuitarMinMidi, kGuitarMaxMidi),
		      "displayed guitar single-note profile: expected valid smoothed chord to be preserved");

	std::array<float, kNoteProbeCount> strong_third_powers = weak_third_powers;
	set_probe_level(strong_third_powers, 56, 0.44f);
	runner.expect(!displayed_guitar_chord_has_single_note_probe_profile(
			      displayed, empty_smoothed, strong_third_powers, kGuitarMinMidi,
			      kGuitarMaxMidi),
		      "displayed guitar single-note profile: expected strong third probe to be preserved");
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

void check_ambiguous_guitar_power_quality_keeps_both_plain_aliases(Runner &runner)
{
	ChordResult ambiguous = make_crowded_chord("Am=Apow");
	ambiguous.root = 9;
	NoteGrid power_grid = {};
	set_pitch(power_grid, 9, 1.00f);
	set_pitch(power_grid, 4, 0.52f);
	std::array<float, kNoteProbeCount> powers = {};
	set_probe_level(powers, 45, 0.40f);
	set_probe_level(powers, 52, 0.32f);

	append_guitar_probe_opposite_quality_aliases(ambiguous, power_grid, powers,
						     kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(ambiguous.label, "A"),
		      std::string("ambiguous guitar power quality: expected opposite major alias, got `") +
			      ambiguous.label + "`");
	runner.expect(chord_label_has_exact_component(ambiguous.label, "Am"),
		      std::string("ambiguous guitar power quality: expected existing minor alias kept, got `") +
			      ambiguous.label + "`");

	ChordResult protected_major = make_crowded_chord("C=Cpow");
	protected_major.root = 0;
	NoteGrid major_grid = {};
	set_pitch(major_grid, 0, 1.00f);
	set_pitch(major_grid, 4, 0.62f);
	set_pitch(major_grid, 7, 0.55f);
	std::array<float, kNoteProbeCount> protected_powers = {};
	set_probe_level(protected_powers, 48, 0.40f);
	set_probe_level(protected_powers, 52, 0.30f);
	set_probe_level(protected_powers, 55, 0.28f);

	append_guitar_probe_opposite_quality_aliases(protected_major, major_grid,
						     protected_powers, kGuitarMinMidi,
						     kGuitarMaxMidi);
	runner.expect(!chord_label_has_exact_component(protected_major.label, "Cm"),
			      std::string("ambiguous guitar power quality: expected clear major triad protected, got `") +
			      protected_major.label + "`");

	ChordResult power_only = make_crowded_chord("A=Apow");
	power_only.root = 9;
	NoteGrid power_only_grid = {};
	set_pitch(power_only_grid, 9, 1.00f);
	set_pitch(power_only_grid, 4, 0.55f);
	std::array<float, kNoteProbeCount> power_only_powers = {};
	set_probe_level(power_only_powers, 45, 0.48f);
	set_probe_level(power_only_powers, 52, 0.36f);

	append_guitar_power_quality_candidates(power_only, power_only_grid,
					       power_only_powers, kGuitarMinMidi,
					       kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(power_only.label, "A"),
		      std::string("ambiguous guitar power quality: expected major alias kept, got `") +
			      power_only.label + "`");
	runner.expect(chord_label_has_exact_component(power_only.label, "Am"),
		      std::string("ambiguous guitar power quality: expected minor alias appended, got `") +
			      power_only.label + "`");
	runner.expect(chord_label_has_exact_component(power_only.label, "Apow"),
		      std::string("ambiguous guitar power quality: expected power alias kept, got `") +
			      power_only.label + "`");

	ChordResult clear_power_major = make_crowded_chord("C=Cpow");
	clear_power_major.root = 0;
	append_guitar_power_quality_candidates(clear_power_major, major_grid,
					       protected_powers, kGuitarMinMidi,
					       kGuitarMaxMidi);
	runner.expect(!chord_label_has_exact_component(clear_power_major.label, "Cm"),
		      std::string("ambiguous guitar power quality: expected clear major power alias protected, got `") +
			      clear_power_major.label + "`");
}

void check_compact_guitar_power_raw_profile_third_aliases(Runner &runner)
{
	InstrumentState measured_major = {};
	std::snprintf(measured_major.label, sizeof(measured_major.label),
		      "E=Esus4=Edim=Apow=Emaj7");
	measured_major.confidence = 0.68f;
	NoteGrid major_display_grid = {};
	set_pitch(major_display_grid, 9, 1.00f);
	set_pitch(major_display_grid, 4, 0.91f);
	set_pitch(major_display_grid, 11, 0.34f);
	NoteGrid major_analysis_grid = {};
	for (int pitch_class : {3, 4, 5, 7, 8, 9, 10, 11})
		set_pitch(major_analysis_grid, pitch_class, pitch_class == 9 ? 1.00f : 0.24f);
	std::array<float, kNoteProbeCount> major_powers = {};
	set_probe_level(major_powers, 45, 1.000f);
	set_probe_level(major_powers, 49, 0.015f);
	set_probe_level(major_powers, 52, 0.665f);

	bool major_minor = false;
	float major_score = 0.0f;
	runner.expect(compact_guitar_raw_profile_third_quality(
			      major_display_grid, major_analysis_grid, major_powers,
			      kGuitarMinMidi, kGuitarMaxMidi, 9, false, major_minor,
			      major_score) &&
		      !major_minor,
		      std::string("compact guitar power raw-profile predicate: expected A major, "
				  "root=") +
			      std::to_string(strongest_probe_pitch_class_level(
				      major_powers, 9, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " third=" +
			      std::to_string(strongest_probe_pitch_class_level(
				      major_powers, 1, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " fifth=" +
			      std::to_string(strongest_probe_pitch_class_level(
				      major_powers, 4, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " display=" + std::to_string(note_grid_pitch_active(major_display_grid, 9)) +
			      "/" + std::to_string(note_grid_pitch_active(major_display_grid, 4)) +
			      " analysis=" + std::to_string(note_grid_pitch_active(major_analysis_grid, 9)) +
			      "/" + std::to_string(note_grid_pitch_active(major_analysis_grid, 4)));

	append_compact_guitar_power_raw_profile_aliases_to_display(
		measured_major, major_display_grid, major_analysis_grid, major_powers,
		kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(measured_major.label, "A"),
		      std::string("compact guitar power raw-profile display: expected A alias, got `") +
			      measured_major.label + "`");

	InstrumentState measured_minor = {};
	std::snprintf(measured_minor.label, sizeof(measured_minor.label), "--");
	NoteGrid minor_display_grid = {};
	set_pitch(minor_display_grid, 10, 0.21f);
	set_pitch(minor_display_grid, 5, 1.00f);
	NoteGrid minor_analysis_grid = {};
	set_pitch(minor_analysis_grid, 1, 0.01f);
	set_pitch(minor_analysis_grid, 5, 1.00f);
	set_pitch(minor_analysis_grid, 8, 0.01f);
	set_pitch(minor_analysis_grid, 10, 0.16f);
	std::array<float, kNoteProbeCount> minor_powers = {};
	set_probe_level(minor_powers, 46, 0.195f);
	set_probe_level(minor_powers, 49, 0.007f);
	set_probe_level(minor_powers, 50, 0.005f);
	set_probe_level(minor_powers, 53, 1.000f);

	bool minor_is_minor = false;
	float minor_score = 0.0f;
	runner.expect(compact_guitar_raw_profile_third_quality(
			      minor_display_grid, minor_analysis_grid, minor_powers,
			      kGuitarMinMidi, kGuitarMaxMidi, 10, true, minor_is_minor,
			      minor_score) &&
		      minor_is_minor,
		      std::string("compact guitar root-fifth raw-profile predicate: expected A#m, "
				  "root=") +
			      std::to_string(strongest_probe_pitch_class_level(
				      minor_powers, 10, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " third=" +
			      std::to_string(strongest_probe_pitch_class_level(
				      minor_powers, 1, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " fifth=" +
			      std::to_string(strongest_probe_pitch_class_level(
				      minor_powers, 5, kGuitarMinMidi, kGuitarMaxMidi)) +
			      " display=" + std::to_string(note_grid_pitch_active(minor_display_grid, 10)) +
			      "/" + std::to_string(note_grid_pitch_active(minor_display_grid, 5)) +
			      " analysis=" + std::to_string(note_grid_pitch_active(minor_analysis_grid, 10)) +
			      "/" + std::to_string(note_grid_pitch_active(minor_analysis_grid, 5)) +
			      "/" + std::to_string(note_grid_pitch_active(minor_analysis_grid, 1)));

	recover_compact_guitar_root_fifth_raw_profile_chord(
		measured_minor, minor_display_grid, minor_analysis_grid, minor_powers,
		kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(measured_minor.label, "A#m"),
		      std::string("compact guitar root-fifth raw-profile display: expected A#m alias, got `") +
			      measured_minor.label + "`");

	InstrumentState crowded_power = {};
	std::snprintf(crowded_power.label, sizeof(crowded_power.label),
		      "E=Esus4=Asus2=Edim=Apow=Emaj7");
	crowded_power.confidence = 0.68f;
	NoteGrid crowded_display_grid = {};
	set_pitch(crowded_display_grid, 4, 1.00f);
	set_pitch(crowded_display_grid, 9, 0.93f);
	set_pitch(crowded_display_grid, 11, 0.42f);
	NoteGrid crowded_analysis_grid = {};
	for (int pitch_class : {3, 4, 5, 7, 8, 9, 10, 11})
		set_pitch(crowded_analysis_grid, pitch_class, pitch_class == 4 ? 1.00f : 0.24f);
	std::array<float, kNoteProbeCount> crowded_powers = {};
	set_probe_level(crowded_powers, 45, 0.914f);
	set_probe_level(crowded_powers, 48, 0.046f);
	set_probe_level(crowded_powers, 49, 0.027f);
	set_probe_level(crowded_powers, 52, 1.000f);

	append_compact_guitar_power_raw_profile_aliases_to_display(
		crowded_power, crowded_display_grid, crowded_analysis_grid, crowded_powers,
		kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(crowded_power.label, "Am"),
		      std::string("compact crowded guitar power raw-profile display: expected Am alias, got `") +
			      crowded_power.label + "`");

	InstrumentState short_power = {};
	std::snprintf(short_power.label, sizeof(short_power.label),
		      "E=Esus4=Asus2=Edim=Apow");
	short_power.confidence = 0.68f;
	std::array<float, kNoteProbeCount> short_powers = {};
	set_probe_level(short_powers, 45, 0.928f);
	set_probe_level(short_powers, 48, 0.202f);
	set_probe_level(short_powers, 49, 0.027f);
	set_probe_level(short_powers, 52, 1.000f);
	append_compact_guitar_power_raw_profile_aliases_to_display(
		short_power, crowded_display_grid, crowded_analysis_grid, short_powers,
		kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(chord_label_has_exact_component(short_power.label, "Am"),
		      std::string("compact short guitar power raw-profile display: expected Am alias, got `") +
			      short_power.label + "`");

	InstrumentState flanked_power = {};
	std::snprintf(flanked_power.label, sizeof(flanked_power.label), "G=Cpow");
	flanked_power.confidence = 0.60f;
	NoteGrid flanked_display_grid = {};
	for (int pitch_class : {11, 0, 1, 7})
		set_pitch(flanked_display_grid, pitch_class, pitch_class == 0 ? 1.00f : 0.68f);
	NoteGrid flanked_analysis_grid = flanked_display_grid;
	set_pitch(flanked_analysis_grid, 10, 0.20f);
	std::array<float, kNoteProbeCount> flanked_powers = {};
	set_probe_level(flanked_powers, 48, 0.94f);
	set_probe_level(flanked_powers, 51, 0.054f);
	set_probe_level(flanked_powers, 52, 0.012f);
	set_probe_level(flanked_powers, 55, 1.000f);
	set_probe_level(flanked_powers, 59, 0.73f);
	append_compact_guitar_power_raw_profile_aliases_to_display(
		flanked_power, flanked_display_grid, flanked_analysis_grid, flanked_powers,
		kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(!chord_label_has_exact_component(flanked_power.label, "Cm"),
		      std::string("compact flanked guitar power raw-profile display: expected Cm blocked, got `") +
			      flanked_power.label + "`");

	InstrumentState protected_plain = {};
	std::snprintf(protected_plain.label, sizeof(protected_plain.label),
		      "D=Cm=Csus2=C#pow=D7=Dmaj7");
	protected_plain.confidence = 0.62f;
	NoteGrid protected_display_grid = {};
	set_pitch(protected_display_grid, 2, 1.00f);
	set_pitch(protected_display_grid, 6, 0.62f);
	set_pitch(protected_display_grid, 1, 0.35f);
	set_pitch(protected_display_grid, 8, 0.24f);
	NoteGrid protected_analysis_grid = protected_display_grid;
	std::array<float, kNoteProbeCount> protected_crowded_powers = {};
	set_probe_level(protected_crowded_powers, 49, 0.45f);
	set_probe_level(protected_crowded_powers, 52, 0.030f);
	set_probe_level(protected_crowded_powers, 56, 0.42f);

	append_compact_guitar_power_raw_profile_aliases_to_display(
		protected_plain, protected_display_grid, protected_analysis_grid,
		protected_crowded_powers, kGuitarMinMidi, kGuitarMaxMidi);
	runner.expect(!chord_label_has_exact_component(protected_plain.label, "C#m"),
		      std::string("compact crowded guitar power raw-profile display: expected supported D protected, got `") +
			      protected_plain.label + "`");
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

	auto make_formant_shadow = [](int midi) {
		FullMixDebugCandidate debug = make_adjacent_other_vocal_shadow_debug(midi);
		debug.other_score = 0.88f;
		debug.spectral_level = 0.81f;
		debug.pitch_confidence = 0.65f;
		debug.periodicity = 0.82f;
		debug.harmonic_fit_error = 0.35f;
		debug.local_noise_level = 0.09f;
		debug.spectral_centroid = 0.504f;
		debug.spectral_slope = 1.19f;
		debug.adjacent_lower_ratio = 0.108f;
		debug.adjacent_upper_ratio = 0.303f;
		debug.harmonic_ratios[1] = 0.77f;
		debug.harmonic_ratios[2] = 1.23f;
		debug.harmonic_ratios[3] = 0.59f;
		debug.harmonic_ratios[4] = 0.28f;
		return debug;
	};

	static constexpr int kMeasuredFormantShadowMidi = 65;
	NoteGrid measured_formant_vocal_grid = {};
	set_midi(measured_formant_vocal_grid, kMeasuredFormantShadowMidi, 0.42f);
	InstrumentState measured_formant_vocal_state = {};
	NoteGrid measured_formant_other_grid = {};
	set_midi(measured_formant_other_grid, kMeasuredFormantShadowMidi, 0.88f);
	FullMixOwnership measured_formant_ownership = {};
	measured_formant_ownership.debug_candidate_count = 1;
	measured_formant_ownership.debug_candidates[0] = make_formant_shadow(kMeasuredFormantShadowMidi);
	suppress_named_owned_same_pitch_vocal_shadows(measured_formant_vocal_grid,
						      measured_formant_vocal_state,
						      measured_formant_other_grid,
						      measured_formant_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(measured_formant_vocal_grid,
						  kMeasuredFormantShadowMidi) <= 0.0f,
		      "same-pitch other vocal shadow: expected measured formant shadow to clear");

	static constexpr int kSparseOtherShadowMidi = 64;
	NoteGrid sparse_other_vocal_grid = {};
	set_midi(sparse_other_vocal_grid, kSparseOtherShadowMidi, 0.33f);
	InstrumentState sparse_other_vocal_state = {};
	NoteGrid sparse_other_grid = {};
	set_midi(sparse_other_grid, kSparseOtherShadowMidi, 0.84f);
	FullMixOwnership sparse_other_ownership = {};
	sparse_other_ownership.debug_candidate_count = 1;
	sparse_other_ownership.debug_candidates[0] =
		make_adjacent_other_vocal_shadow_debug(kSparseOtherShadowMidi);
	sparse_other_ownership.debug_candidates[0].other_score = 0.84f;
	sparse_other_ownership.debug_candidates[0].vocal_score = 0.0f;
	sparse_other_ownership.debug_candidates[0].spectral_centroid = 0.50f;
	sparse_other_ownership.debug_candidates[0].spectral_slope = 0.93f;
	sparse_other_ownership.debug_candidates[0].local_noise_level = 0.164f;
	sparse_other_ownership.debug_candidates[0].adjacent_lower_ratio = 0.10f;
	sparse_other_ownership.debug_candidates[0].harmonic_ratios[2] = 2.20f;
	sparse_other_ownership.debug_candidates[0].harmonic_ratios[3] = 0.65f;
	sparse_other_ownership.debug_candidates[0].harmonic_ratios[4] = 0.02f;
	runner.expect(measured_owned_formant_vocal_partial_supported(
			      sparse_other_ownership.debug_candidates[0]),
		      "same-pitch other vocal shadow: expected sparse fixture to exercise formant guard");
	suppress_named_owned_same_pitch_vocal_shadows(sparse_other_vocal_grid,
						      sparse_other_vocal_state,
						      sparse_other_grid,
						      sparse_other_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(sparse_other_vocal_grid,
						  kSparseOtherShadowMidi) <= 0.0f,
		      "same-pitch other vocal shadow: expected strong sparse other-owned mirror to clear");

	static constexpr int kSparseProtectedVocalMidi = 67;
	NoteGrid sparse_protected_vocal_grid = {};
	set_midi(sparse_protected_vocal_grid, kSparseProtectedVocalMidi, 0.10f);
	InstrumentState sparse_protected_vocal_state = {};
	NoteGrid sparse_protected_other_grid = {};
	set_midi(sparse_protected_other_grid, kSparseProtectedVocalMidi, 0.21f);
	FullMixOwnership sparse_protected_ownership = {};
	sparse_protected_ownership.debug_candidate_count = 1;
	sparse_protected_ownership.debug_candidates[0] =
		make_adjacent_other_vocal_shadow_debug(kSparseProtectedVocalMidi);
	sparse_protected_ownership.debug_candidates[0].other_score = 0.86f;
	sparse_protected_ownership.debug_candidates[0].vocal_score = 0.0f;
	sparse_protected_ownership.debug_candidates[0].spectral_centroid = 0.485f;
	sparse_protected_ownership.debug_candidates[0].spectral_slope = 0.93f;
	sparse_protected_ownership.debug_candidates[0].local_noise_level = 0.168f;
	sparse_protected_ownership.debug_candidates[0].adjacent_lower_ratio = 0.05f;
	sparse_protected_ownership.debug_candidates[0].harmonic_ratios[2] = 1.35f;
	sparse_protected_ownership.debug_candidates[0].harmonic_ratios[3] = 0.43f;
	sparse_protected_ownership.debug_candidates[0].harmonic_ratios[4] = 0.25f;
	suppress_named_owned_same_pitch_vocal_shadows(sparse_protected_vocal_grid,
						      sparse_protected_vocal_state,
						      sparse_protected_other_grid,
						      sparse_protected_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(sparse_protected_vocal_grid,
						  kSparseProtectedVocalMidi) > 0.0f,
		      "same-pitch other vocal shadow: expected low-level protected vocal ratio to stay visible");

	static constexpr int kFormantProtectedMidi = 66;
	NoteGrid formant_vocal_grid = {};
	set_midi(formant_vocal_grid, kFormantProtectedMidi, 0.42f);
	InstrumentState formant_vocal_state = {};
	NoteGrid formant_other_grid = {};
	set_midi(formant_other_grid, kFormantProtectedMidi, 0.88f);
	FullMixOwnership formant_ownership = {};
	formant_ownership.debug_candidate_count = 1;
	formant_ownership.debug_candidates[0] = make_formant_shadow(kFormantProtectedMidi);
	formant_ownership.debug_candidates[0].local_noise_level = 0.09f;
	formant_ownership.debug_candidates[0].spectral_centroid = 0.52f;
	formant_ownership.debug_candidates[0].harmonic_ratios[2] = 1.35f;
	suppress_named_owned_same_pitch_vocal_shadows(formant_vocal_grid,
						      formant_vocal_state,
						      formant_other_grid,
						      formant_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(formant_vocal_grid, kFormantProtectedMidi) > 0.0f,
		      "same-pitch other vocal shadow: expected protected formant-like vocal body to stay visible");

	static constexpr int kDenseVocalBodyMidi = 63;
	NoteGrid dense_vocal_grid = {};
	set_midi(dense_vocal_grid, kDenseVocalBodyMidi, 0.42f);
	InstrumentState dense_vocal_state = {};
	NoteGrid dense_other_grid = {};
	set_midi(dense_other_grid, kDenseVocalBodyMidi, 1.00f);
	FullMixOwnership dense_ownership = {};
	dense_ownership.debug_candidate_count = 1;
	dense_ownership.debug_candidates[0] = make_adjacent_other_vocal_shadow_debug(kDenseVocalBodyMidi);
	dense_ownership.debug_candidates[0].other_score = 0.88f;
	dense_ownership.debug_candidates[0].pitch_confidence = 0.57f;
	dense_ownership.debug_candidates[0].periodicity = 0.73f;
	dense_ownership.debug_candidates[0].harmonic_fit_error = 0.46f;
	dense_ownership.debug_candidates[0].spectral_centroid = 0.56f;
	dense_ownership.debug_candidates[0].spectral_slope = 1.64f;
	dense_ownership.debug_candidates[0].local_noise_level = 0.22f;
	dense_ownership.debug_candidates[0].harmonic_ratios[1] = 0.51f;
	dense_ownership.debug_candidates[0].harmonic_ratios[2] = 0.83f;
	dense_ownership.debug_candidates[0].harmonic_ratios[3] = 1.24f;
	dense_ownership.debug_candidates[0].harmonic_ratios[4] = 0.40f;
	suppress_named_owned_same_pitch_vocal_shadows(dense_vocal_grid,
						      dense_vocal_state,
						      dense_other_grid,
						      dense_ownership,
						      InstrumentKind::Other, -1);
	runner.expect(note_grid_midi_visual_level(dense_vocal_grid, kDenseVocalBodyMidi) > 0.0f,
		      "same-pitch other vocal shadow: expected dense vocal body to stay visible");
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
	static constexpr int kStrongBassMidi = 54;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kShadowMidi, 0.933f);
	InstrumentState bass_state = {};
	NoteGrid other_grid = {};
	set_midi(other_grid, kShadowMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_other_bass_shadow_debug(kShadowMidi);

	suppress_other_dominant_same_pitch_bass_shadows(bass_grid, bass_state, other_grid,
							ownership, -1);
	runner.expect(note_grid_midi_visual_level(bass_grid, kShadowMidi) <= 0.0f,
		      "same-pitch other bass shadow: expected other-owned 93.5% bass mirror to clear");

	static constexpr int kMeasuredEdgeMidi = 48;
	NoteGrid measured_edge_bass_grid = {};
	set_midi(measured_edge_bass_grid, kMeasuredEdgeMidi, 0.659514f);
	InstrumentState measured_edge_bass_state = {};
	NoteGrid measured_edge_other_grid = {};
	set_midi(measured_edge_other_grid, kMeasuredEdgeMidi, 0.7052f);
	FullMixOwnership measured_edge_ownership = {};
	measured_edge_ownership.debug_candidate_count = 1;
	measured_edge_ownership.debug_candidates[0] = make_other_bass_shadow_debug(kMeasuredEdgeMidi);
	measured_edge_ownership.debug_candidates[0].other_score = 0.88389f;
	suppress_other_dominant_same_pitch_bass_shadows(measured_edge_bass_grid,
							measured_edge_bass_state,
							measured_edge_other_grid,
							measured_edge_ownership, -1);
	runner.expect(note_grid_midi_visual_level(measured_edge_bass_grid, kMeasuredEdgeMidi) <= 0.0f,
		      "same-pitch other bass shadow: expected measured guitar C3 bass mirror to clear");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kProtectedMidi, 0.933f);
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
		      "same-pitch other bass shadow: expected non-other-owned 93.5% bass note to stay visible");

	NoteGrid strong_bass_grid = {};
	set_midi(strong_bass_grid, kStrongBassMidi, 0.95f);
	InstrumentState strong_bass_state = {};
	NoteGrid strong_other_grid = {};
	set_midi(strong_other_grid, kStrongBassMidi, 1.00f);
	FullMixOwnership strong_ownership = {};
	strong_ownership.debug_candidate_count = 1;
	strong_ownership.debug_candidates[0] = make_other_bass_shadow_debug(kStrongBassMidi);
	suppress_other_dominant_same_pitch_bass_shadows(strong_bass_grid,
							strong_bass_state,
							strong_other_grid,
							strong_ownership, -1);
	runner.expect(note_grid_midi_visual_level(strong_bass_grid, kStrongBassMidi) > 0.0f,
		      "same-pitch other bass shadow: expected strong owned bass note above 93.5% to stay visible");

	static constexpr int kBlendMidi = 41;
	NoteGrid blend_bass_grid = {};
	set_midi(blend_bass_grid, kBlendMidi, 0.82f);
	InstrumentState blend_bass_state = {};
	NoteGrid blend_other_grid = {};
	set_midi(blend_other_grid, kBlendMidi, 1.00f);
	FullMixOwnership blend_ownership = {};
	blend_ownership.debug_candidate_count = 1;
	FullMixDebugCandidate blend_debug = make_other_bass_shadow_debug(kBlendMidi);
	blend_debug.guitar_score = 0.13f;
	blend_debug.other_score = 0.87f;
	blend_debug.spectral_level = 1.0f;
	blend_debug.pitch_confidence = 0.58f;
	blend_debug.periodicity = 0.61f;
	blend_debug.harmonic_fit_error = 0.41f;
	blend_debug.spectral_centroid = 0.57f;
	blend_debug.spectral_slope = 1.32f;
	blend_debug.local_noise_level = 0.59f;
	blend_debug.adjacent_lower_ratio = 0.88f;
	blend_debug.adjacent_upper_ratio = 0.88f;
	blend_debug.third_octave_ratio = 0.51f;
	blend_debug.harmonic_ratios[1] = 0.85f;
	blend_debug.harmonic_ratios[2] = 0.69f;
	blend_debug.harmonic_ratios[3] = 0.88f;
	blend_debug.harmonic_ratios[4] = 0.88f;
	blend_ownership.debug_candidates[0] = blend_debug;
	suppress_other_dominant_same_pitch_bass_shadows(blend_bass_grid,
							blend_bass_state,
							blend_other_grid,
							blend_ownership, -1);
	runner.expect(note_grid_midi_visual_level(blend_bass_grid, kBlendMidi) > 0.0f,
		      "same-pitch other bass shadow: expected dense low bass blend to preserve bass");
}

FullMixDebugCandidate make_keyboard_bass_shadow_debug(int midi)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = InstrumentKind::Keyboard;
	debug.ownership_confidence = 0.84f;
	debug.bass_score = 0.08f;
	debug.keyboard_score = 0.25f;
	debug.spectral_level = 0.65f;
	debug.pitch_confidence = 0.83f;
	debug.periodicity = 0.73f;
	debug.harmonic_fit_error = 0.05f;
	debug.local_noise_level = 0.16f;
	return debug;
}

void check_keyboard_owned_same_pitch_bass_shadow_uses_weak_ceiling(Runner &runner)
{
	static constexpr int kShadowMidi = 52;
	static constexpr int kProtectedMidi = 53;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kShadowMidi, 0.455f);
	InstrumentState bass_state = {};
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kShadowMidi, 0.25f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_keyboard_bass_shadow_debug(kShadowMidi);

	suppress_keyboard_owned_same_pitch_bass_shadows(bass_grid, bass_state, keyboard_grid,
						       ownership, -1, false);
	runner.expect(note_grid_midi_visual_level(bass_grid, kShadowMidi) <= 0.0f,
		      "same-pitch keyboard bass shadow: expected weak keyboard-owned 46% bass mirror to clear");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kProtectedMidi, 0.47f);
	InstrumentState protected_bass_state = {};
	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kProtectedMidi, 0.25f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] = make_keyboard_bass_shadow_debug(kProtectedMidi);

	suppress_keyboard_owned_same_pitch_bass_shadows(protected_bass_grid,
						       protected_bass_state,
						       protected_keyboard_grid,
						       protected_ownership, -1,
						       false);
	runner.expect(note_grid_midi_visual_level(protected_bass_grid, kProtectedMidi) > 0.0f,
		      "same-pitch keyboard bass shadow: expected bass note above 46% to stay visible");
}

void check_keyboard_owned_same_pitch_bass_shadow_uses_dominant_ratio(Runner &runner)
{
	static constexpr int kShadowMidi = 50;
	static constexpr int kDisabledMidi = 51;
	static constexpr int kProtectedMidi = 52;

	NoteGrid bass_grid = {};
	set_midi(bass_grid, kShadowMidi, 0.693f);
	InstrumentState bass_state = {};
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kShadowMidi, 1.00f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] = make_keyboard_bass_shadow_debug(kShadowMidi);
	ownership.debug_candidates[0].keyboard_score = 1.00f;
	ownership.debug_candidates[0].bass_score = 0.00f;
	ownership.keyboard[static_cast<std::size_t>(kShadowMidi - kFirstMidi)] = true;

	suppress_keyboard_owned_same_pitch_bass_shadows(bass_grid, bass_state, keyboard_grid,
						       ownership, -1, true);
	runner.expect(note_grid_midi_visual_level(bass_grid, kShadowMidi) <= 0.0f,
		      "same-pitch keyboard bass shadow: expected dominant keyboard-owned 69.5% bass mirror to clear");

	NoteGrid disabled_bass_grid = {};
	set_midi(disabled_bass_grid, kDisabledMidi, 0.685f);
	InstrumentState disabled_bass_state = {};
	NoteGrid disabled_keyboard_grid = {};
	set_midi(disabled_keyboard_grid, kDisabledMidi, 1.00f);
	FullMixOwnership disabled_ownership = {};
	disabled_ownership.debug_candidate_count = 1;
	disabled_ownership.debug_candidates[0] = make_keyboard_bass_shadow_debug(kDisabledMidi);
	disabled_ownership.debug_candidates[0].keyboard_score = 1.00f;
	disabled_ownership.debug_candidates[0].bass_score = 0.00f;
	disabled_ownership.keyboard[static_cast<std::size_t>(kDisabledMidi - kFirstMidi)] = true;

	suppress_keyboard_owned_same_pitch_bass_shadows(disabled_bass_grid,
						       disabled_bass_state,
						       disabled_keyboard_grid,
						       disabled_ownership, -1,
						       false);
	runner.expect(note_grid_midi_visual_level(disabled_bass_grid, kDisabledMidi) > 0.0f,
		      "same-pitch keyboard bass shadow: expected dominant cleanup disabled bass mirror to stay visible");

	NoteGrid high_pure_bass_grid = {};
	set_midi(high_pure_bass_grid, 55, 1.00f);
	InstrumentState high_pure_bass_state = {};
	NoteGrid high_pure_keyboard_grid = {};
	set_midi(high_pure_keyboard_grid, 55, 0.20f);
	FullMixOwnership high_pure_ownership = {};
	high_pure_ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &high_pure_debug = high_pure_ownership.debug_candidates[0];
	high_pure_debug = make_keyboard_bass_shadow_debug(55);
	high_pure_debug.bass_score = 0.0f;
	high_pure_debug.keyboard_score = 1.0f;
	high_pure_debug.pitch_confidence = 0.88f;
	high_pure_debug.harmonic_fit_error = 0.052f;
	high_pure_debug.spectral_centroid = 0.057f;
	high_pure_debug.harmonic_ratios[2] = 0.078f;
	high_pure_debug.harmonic_ratios[3] = 0.006f;
	high_pure_ownership.keyboard[static_cast<std::size_t>(55 - kFirstMidi)] = true;

	suppress_keyboard_owned_same_pitch_bass_shadows(high_pure_bass_grid,
						       high_pure_bass_state,
						       high_pure_keyboard_grid,
						       high_pure_ownership, -1,
						       true);
	runner.expect(note_grid_midi_visual_level(high_pure_bass_grid, 55) <= 0.0f,
		      "same-pitch keyboard bass shadow: expected high pure keyboard bass mirror to clear");

	NoteGrid protected_bass_grid = {};
	set_midi(protected_bass_grid, kProtectedMidi, 0.70f);
	InstrumentState protected_bass_state = {};
	NoteGrid protected_keyboard_grid = {};
	set_midi(protected_keyboard_grid, kProtectedMidi, 1.00f);
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] = make_keyboard_bass_shadow_debug(kProtectedMidi);
	protected_ownership.debug_candidates[0].keyboard_score = 1.00f;
	protected_ownership.debug_candidates[0].bass_score = 0.00f;
	protected_ownership.debug_candidates[0].local_noise_level = 0.50f;
	protected_ownership.keyboard[static_cast<std::size_t>(kProtectedMidi - kFirstMidi)] = true;

	suppress_keyboard_owned_same_pitch_bass_shadows(protected_bass_grid,
						       protected_bass_state,
						       protected_keyboard_grid,
						       protected_ownership, -1,
						       true);
	runner.expect(note_grid_midi_visual_level(protected_bass_grid, kProtectedMidi) > 0.0f,
		      "same-pitch keyboard bass shadow: expected bass note above 69.5% to stay visible");
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

	NoteGrid fundamental_other_grid = {};
	set_midi(fundamental_other_grid, kOtherMidi, 1.00f);
	NoteGrid fundamental_keyboard_grid = {};
	set_midi(fundamental_keyboard_grid, kProtectedNearbyAliasMidi, 1.00f);
	FullMixOwnership fundamental_ownership = {};
	fundamental_ownership.debug_candidate_count = 1;
	fundamental_ownership.debug_candidates[0] =
		make_other_keyboard_pitch_class_shadow_debug(kOtherMidi);
	fundamental_ownership.debug_candidates[0].harmonicity = 1.20f;
	attenuate_other_dominant_pitch_class_keyboard_shadows(fundamental_keyboard_grid,
							      fundamental_other_grid,
							      fundamental_ownership);
	const float fundamental_keyboard_level =
		note_grid_midi_visual_level(fundamental_keyboard_grid, kProtectedNearbyAliasMidi);
	runner.expect(fundamental_keyboard_level < 1.00f && fundamental_keyboard_level > 0.0f,
		      "other pitch-class keyboard shadow: expected measured one-octave alias attenuation");

	static constexpr int kLowerKeyboardAliasMidi = kOtherMidi - 12;
	NoteGrid lower_alias_keyboard_grid = {};
	set_midi(lower_alias_keyboard_grid, kLowerKeyboardAliasMidi, 1.00f);
	attenuate_other_dominant_pitch_class_keyboard_shadows(lower_alias_keyboard_grid,
							      fundamental_other_grid,
							      fundamental_ownership);
	const float lower_alias_level =
		note_grid_midi_visual_level(lower_alias_keyboard_grid, kLowerKeyboardAliasMidi);
	runner.expect(lower_alias_level < 1.00f && lower_alias_level > 0.0f,
		      "other pitch-class keyboard shadow: expected measured lower-octave alias attenuation");

	NoteGrid debug_only_keyboard_grid = {};
	set_midi(debug_only_keyboard_grid, kOtherMidi, 1.00f);
	set_midi(debug_only_keyboard_grid, kProtectedNearbyAliasMidi, 0.95f);
	InstrumentState debug_only_keyboard_state = {};
	FullMixOwnership debug_only_ownership = {};
	debug_only_ownership.debug_candidate_count = 1;
	debug_only_ownership.debug_candidates[0] =
		make_other_keyboard_pitch_class_shadow_debug(kOtherMidi);
	debug_only_ownership.debug_candidates[0].harmonicity = 1.20f;
	debug_only_ownership.debug_candidates[0].spectral_level = 0.45f;
	attenuate_measured_other_debug_pitch_class_keyboard_shadows(debug_only_keyboard_grid,
								    debug_only_keyboard_state,
								    debug_only_ownership, -1);
	runner.expect(note_grid_midi_visual_level(debug_only_keyboard_grid, kOtherMidi) < 1.00f,
		      "other pitch-class keyboard shadow: expected debug-only exact keyboard note attenuation");
	runner.expect(note_grid_midi_visual_level(debug_only_keyboard_grid, kProtectedNearbyAliasMidi) <
			      0.95f,
		      "other pitch-class keyboard shadow: expected debug-only keyboard alias attenuation");

	NoteGrid weak_debug_keyboard_grid = {};
	set_midi(weak_debug_keyboard_grid, kOtherMidi, 1.00f);
	InstrumentState weak_debug_keyboard_state = {};
	FullMixOwnership weak_debug_ownership = debug_only_ownership;
	weak_debug_ownership.debug_candidates[0].harmonicity = 0.0f;
	weak_debug_ownership.debug_candidates[0].harmonic_fit_error = 0.0f;
	weak_debug_ownership.debug_candidates[0].harmonic_ratios[1] = 0.0f;
	weak_debug_ownership.debug_candidates[0].local_noise_level = 0.0f;
	attenuate_measured_other_debug_pitch_class_keyboard_shadows(weak_debug_keyboard_grid,
								    weak_debug_keyboard_state,
								    weak_debug_ownership, -1);
	runner.expect(note_grid_midi_visual_level(weak_debug_keyboard_grid, kOtherMidi) > 0.99f,
		      "other pitch-class keyboard shadow: expected weak debug-only fundamental to keep keyboard note");
}

void check_measured_other_fundamental_display_level_boost(Runner &runner)
{
	static constexpr int kMidi = 62;
	NoteGrid grid = {};
	set_midi(grid, kMidi, 0.21f);
	InstrumentState state = {};
	write_note_grid_label(state, grid, -1);

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.global_note_levels[static_cast<std::size_t>(kMidi - kFirstMidi)] = 0.64f;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kMidi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.84f;
	debug.other_score = 0.84f;
	debug.spectral_level = 0.70f;
	debug.pitch_confidence = 0.74f;
	debug.periodicity = 0.70f;
	debug.harmonicity = 1.20f;

	boost_measured_other_fundamental_display_level(grid, state, ownership, -1);
	runner.expect(note_grid_midi_level(grid, kMidi) >= 0.78f,
		      "measured other fundamental boost: expected existing note to brighten");

	NoteGrid missing_grid = {};
	InstrumentState missing_state = {};
	boost_measured_other_fundamental_display_level(missing_grid, missing_state, ownership, -1);
	runner.expect(note_grid_midi_level(missing_grid, kMidi) <= 0.0f,
		      "measured other fundamental boost: expected missing note not to be created");
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
	InstrumentState other_state = {};
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0] =
		make_electronic_keyboard_other_shadow_debug(kOtherAliasMidi);

	attenuate_measured_electronic_keyboard_other_shadows(other_grid, other_state, keyboard_grid,
							     ownership, -1);
	runner.expect(note_grid_midi_visual_level(other_grid, kOtherAliasMidi) < 0.66f,
		      "electronic keyboard other shadow: expected synthetic other octave alias below keyboard support");
	runner.expect(note_grid_midi_level(other_grid, kOtherAliasMidi) < 0.66f,
		      "electronic keyboard other shadow: expected row level below keyboard support");
	runner.expect(note_grid_midi_visual_level(other_grid, kOtherAliasMidi) > 0.0f,
		      "electronic keyboard other shadow: expected alias attenuated, not removed");

	NoteGrid high_keyboard_grid = {};
	set_midi(high_keyboard_grid, 89, 0.72f);
	NoteGrid high_other_grid = {};
	set_midi(high_other_grid, 77, 1.00f);
	InstrumentState high_other_state = {};
	FullMixOwnership high_ownership = {};
	high_ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &high_debug = high_ownership.debug_candidates[0];
	high_debug.midi = 77;
	high_debug.owner = InstrumentKind::Other;
	high_debug.other_score = 0.86f;
	high_debug.pitch_confidence = 0.08f;
	high_debug.periodicity = 0.44f;
	high_debug.harmonic_fit_error = 2.50f;
	high_debug.spectral_level = 0.20f;
	high_debug.spectral_centroid = 0.59f;
	high_debug.spectral_slope = 0.90f;
	high_debug.harmonic_ratios[1] = 4.0f;
	high_debug.harmonic_ratios[3] = 4.5f;
	attenuate_measured_electronic_keyboard_other_shadows(high_other_grid, high_other_state,
							     high_keyboard_grid,
							     high_ownership, -1);
	runner.expect(note_grid_midi_visual_level(high_other_grid, 77) < 0.72f,
		      "electronic keyboard other shadow: expected weak high organ alias below keyboard support");

	NoteGrid protected_other_grid = {};
	set_midi(protected_other_grid, kOtherAliasMidi, 1.00f);
	InstrumentState protected_other_state = {};
	FullMixOwnership protected_ownership = {};
	protected_ownership.debug_candidate_count = 1;
	protected_ownership.debug_candidates[0] =
		make_electronic_keyboard_other_shadow_debug(kOtherAliasMidi);
	protected_ownership.debug_candidates[0].spectral_slope = 1.30f;
	protected_ownership.debug_candidates[0].harmonic_ratios[2] = 0.90f;
	attenuate_measured_electronic_keyboard_other_shadows(protected_other_grid,
							     protected_other_state,
							     keyboard_grid,
							     protected_ownership, -1);
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

void check_low_electronic_bass_alias_promotes_fundamental_display(Runner &runner)
{
	static constexpr int kBassMidi = 28;
	static constexpr int kAliasMidi = kBassMidi + 12;

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kAliasMidi;
	debug.owner = InstrumentKind::Ambiguous;
	debug.ownership_confidence = 0.0f;
	debug.spectral_level = 0.68f;
	debug.pitch_confidence = 0.58f;
	debug.periodicity = 0.56f;
	debug.harmonic_ratios[3] = 0.0005f;
	debug.harmonic_ratios[4] = 0.018f;
	ownership.global_note_levels[static_cast<std::size_t>(kBassMidi - kFirstMidi)] = 0.04f;

	NoteGrid bass_grid = {};
	write_note_grid_cell(bass_grid, NoteCandidate{kBassMidi, 0.04f}, 1.0f, 1.0f);
	write_note_grid_cell(bass_grid, NoteCandidate{kAliasMidi, 0.54f}, 1.0f, 1.0f);
	InstrumentState bass_state = {};
	NoteGrid keyboard_grid = {};
	promote_low_electronic_bass_alias_display(bass_grid, bass_state, keyboard_grid, ownership, -1);
	runner.expect(note_grid_midi_visual_level(bass_grid, kBassMidi) >= 0.90f,
		      "low electronic bass alias display: expected E1 fundamental to be promoted");
	const NoteCell primary =
		note_grid_primary_cell_for_pitch_class(bass_grid, midi_pitch_class(kBassMidi));
	runner.expect(primary.active && primary.midi == kBassMidi,
		      "low electronic bass alias display: expected E1 to become primary");
	runner.expect(note_grid_midi_visual_level(bass_grid, kAliasMidi) <= 0.0f,
		      "low electronic bass alias display: expected octave alias to be hidden after promotion");

	NoteGrid no_lower_grid = {};
	set_midi(no_lower_grid, kAliasMidi, 0.54f);
	FullMixOwnership no_lower = ownership;
	no_lower.global_note_levels[static_cast<std::size_t>(kBassMidi - kFirstMidi)] = 0.0f;
	InstrumentState no_lower_state = {};
	promote_low_electronic_bass_alias_display(no_lower_grid, no_lower_state, keyboard_grid,
						  no_lower, -1);
	runner.expect(note_grid_midi_visual_level(no_lower_grid, kBassMidi) <= 0.0f,
		      "low electronic bass alias display: expected alias without lower support to stay unchanged");

	NoteGrid keyboard_supported_grid = {};
	set_midi(keyboard_supported_grid, kBassMidi, 0.80f);
	NoteGrid cross_row_grid = {};
	set_midi(cross_row_grid, kAliasMidi, 0.54f);
	FullMixOwnership cross_row_ownership = ownership;
	cross_row_ownership.global_note_levels[static_cast<std::size_t>(kBassMidi - kFirstMidi)] = 0.0f;
	InstrumentState cross_row_state = {};
	promote_low_electronic_bass_alias_display(cross_row_grid, cross_row_state,
						  keyboard_supported_grid, cross_row_ownership,
						  -1);
	runner.expect(note_grid_midi_visual_level(cross_row_grid, kBassMidi) >= 0.90f,
		      "low electronic bass alias display: expected keyboard-supported lower bass to promote");

	NoteGrid unsupported_grid = {};
	write_note_grid_cell(unsupported_grid, NoteCandidate{kBassMidi, 0.04f}, 1.0f, 1.0f);
	write_note_grid_cell(unsupported_grid, NoteCandidate{kAliasMidi, 0.54f}, 1.0f, 1.0f);
	FullMixOwnership unsupported = ownership;
	unsupported.debug_candidates[0].harmonic_ratios[3] = 0.010f;
	InstrumentState unsupported_state = {};
	promote_low_electronic_bass_alias_display(unsupported_grid, unsupported_state, keyboard_grid,
						  unsupported, -1);
	runner.expect(note_grid_midi_visual_level(unsupported_grid, kBassMidi) < 0.90f,
		      "low electronic bass alias display: expected non-matching evidence to stay unchanged");

	NoteGrid weak_alias_grid = {};
	write_note_grid_cell(weak_alias_grid, NoteCandidate{kBassMidi, 0.04f}, 1.0f, 1.0f);
	write_note_grid_cell(weak_alias_grid, NoteCandidate{kAliasMidi, 0.40f}, 1.0f, 1.0f);
	InstrumentState weak_alias_state = {};
	promote_low_electronic_bass_alias_display(weak_alias_grid, weak_alias_state, keyboard_grid,
						  ownership, -1);
	runner.expect(note_grid_midi_visual_level(weak_alias_grid, kBassMidi) < 0.90f,
		      "low electronic bass alias display: expected weak alias to stay hidden");
}

void check_ambiguous_electronic_keyboard_promotes_exact_lower_octave(Runner &runner)
{
	static constexpr int kLowerMidi = 48;
	static constexpr int kAliasMidi = kLowerMidi + 12;

	NoteGrid grid = {};
	write_note_grid_cell(grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	write_note_grid_cell(grid, NoteCandidate{kLowerMidi, 0.25f}, 1.0f, 1.0f);
	InstrumentState state = {};
	write_note_grid_label(state, grid, -1);

	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 1.0f;
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kLowerMidi;
	debug.owner = InstrumentKind::Ambiguous;
	debug.ownership_confidence = 0.55f;
	debug.keyboard_score = 0.55f;
	debug.guitar_score = 0.45f;
	debug.spectral_level = 1.0f;
	debug.pitch_confidence = 0.74f;
	debug.periodicity = 0.77f;
	debug.harmonic_fit_error = 0.29f;
	debug.local_noise_level = 0.29f;
	debug.harmonic_ratios[1] = 0.28f;
	debug.harmonic_ratios[2] = 0.83f;
	debug.harmonic_ratios[3] = 0.49f;
	debug.harmonic_ratios[4] = 0.44f;

	prefer_exact_debug_keyboard_lower_octave_primary(grid, state, ownership, -1);
	const NoteCell primary = note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kLowerMidi));
	runner.expect(primary.active && primary.midi == kLowerMidi,
		      "ambiguous electronic keyboard octave: expected measured lower octave primary");

	NoteGrid guitar_dominant_grid = {};
	write_note_grid_cell(guitar_dominant_grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	write_note_grid_cell(guitar_dominant_grid, NoteCandidate{kLowerMidi, 0.25f}, 1.0f, 1.0f);
	InstrumentState guitar_dominant_state = {};
	write_note_grid_label(guitar_dominant_state, guitar_dominant_grid, -1);
	FullMixOwnership guitar_dominant = ownership;
	guitar_dominant.debug_candidates[0].keyboard_score = 0.34f;
	guitar_dominant.debug_candidates[0].guitar_score = 0.80f;
	prefer_exact_debug_keyboard_lower_octave_primary(guitar_dominant_grid, guitar_dominant_state,
							 guitar_dominant, -1);
	const NoteCell guarded_primary =
		note_grid_primary_cell_for_pitch_class(guitar_dominant_grid, midi_pitch_class(kLowerMidi));
	runner.expect(guarded_primary.active && guarded_primary.midi == kAliasMidi,
		      "ambiguous electronic keyboard octave: expected guitar-dominant alias to stay primary");
}

void check_raw_supported_mid_keyboard_lower_octave_promotes_alias(Runner &runner)
{
	static constexpr int kLowerMidi = 59;
	static constexpr int kAliasMidi = kLowerMidi + 24;

	NoteGrid grid = {};
	write_note_grid_cell(grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState state = {};
	write_note_grid_label(state, grid, -1);

	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.64f;
	ownership.global_note_levels[static_cast<std::size_t>(kAliasMidi - kFirstMidi)] = 0.80f;
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kAliasMidi;
	debug.owner = InstrumentKind::Keyboard;
	debug.ownership_confidence = 0.90f;
	debug.keyboard_score = 0.90f;
	debug.spectral_level = 0.95f;
	debug.pitch_confidence = 0.88f;
	debug.periodicity = 0.74f;

	std::array<float, kNoteProbeCount> powers = {};
	std::array<float, kNoteProbeCount> raw_powers = {};
	set_probe_level(powers, kLowerMidi, 0.64f);
	set_probe_level(powers, kAliasMidi, 0.82f);
	set_probe_level(raw_powers, kLowerMidi, 0.64f);
	set_probe_level(raw_powers, kLowerMidi + 12, 0.78f);
	set_probe_level(raw_powers, kAliasMidi, 0.82f);

	prefer_raw_supported_mid_keyboard_lower_octave_primary(grid, state, ownership, powers,
							       raw_powers, -1);
	const NoteCell primary =
		note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kLowerMidi));
	runner.expect(primary.active && primary.midi == kLowerMidi,
		      "mid keyboard lower octave: expected raw-supported B3 to replace B5 alias");

	{
		static constexpr int kAdjacentLowerMidi = 41;
		static constexpr int kAdjacentAliasMidi = kAdjacentLowerMidi + 12;
		NoteGrid adjacent_grid = {};
		write_note_grid_cell(adjacent_grid, NoteCandidate{kAdjacentAliasMidi, 0.90f}, 1.0f, 1.0f);
		InstrumentState adjacent_state = {};
		write_note_grid_label(adjacent_state, adjacent_grid, -1);

		FullMixOwnership adjacent_ownership = {};
		adjacent_ownership.global_note_levels[static_cast<std::size_t>(kAdjacentLowerMidi -
											kFirstMidi)] = 0.58f;
		adjacent_ownership.global_note_levels[static_cast<std::size_t>(kAdjacentAliasMidi -
											kFirstMidi)] = 0.72f;
		adjacent_ownership.debug_candidate_count = 1;
		FullMixDebugCandidate &adjacent_debug = adjacent_ownership.debug_candidates[0];
		adjacent_debug.midi = kAdjacentAliasMidi;
		adjacent_debug.owner = InstrumentKind::Keyboard;
		adjacent_debug.ownership_confidence = 0.88f;
		adjacent_debug.keyboard_score = 0.90f;
		adjacent_debug.spectral_level = 0.84f;
		adjacent_debug.pitch_confidence = 0.80f;
		adjacent_debug.periodicity = 0.70f;
		adjacent_debug.harmonic_fit_error = 0.09f;
		adjacent_debug.local_noise_level = 0.24f;
		adjacent_debug.harmonic_ratios[1] = 0.20f;

		std::array<float, kNoteProbeCount> adjacent_powers = {};
		std::array<float, kNoteProbeCount> adjacent_raw_powers = {};
		set_probe_level(adjacent_powers, kAdjacentLowerMidi, 0.58f);
		set_probe_level(adjacent_powers, kAdjacentAliasMidi, 0.72f);
		set_probe_level(adjacent_raw_powers, kAdjacentLowerMidi, 0.60f);
		set_probe_level(adjacent_raw_powers, kAdjacentAliasMidi, 0.72f);

		prefer_raw_supported_mid_keyboard_lower_octave_primary(
			adjacent_grid, adjacent_state, adjacent_ownership, adjacent_powers,
			adjacent_raw_powers, -1);
		const NoteCell adjacent_primary = note_grid_primary_cell_for_pitch_class(
			adjacent_grid, midi_pitch_class(kAdjacentLowerMidi));
		runner.expect(adjacent_primary.active && adjacent_primary.midi == kAdjacentLowerMidi,
			      "mid keyboard lower octave: expected raw-supported F2 to replace F3 alias");

		NoteGrid weak_adjacent_grid = {};
		write_note_grid_cell(weak_adjacent_grid, NoteCandidate{kAdjacentAliasMidi, 0.90f}, 1.0f,
				     1.0f);
		InstrumentState weak_adjacent_state = {};
		write_note_grid_label(weak_adjacent_state, weak_adjacent_grid, -1);
		FullMixOwnership weak_adjacent_ownership = adjacent_ownership;
		weak_adjacent_ownership.global_note_levels[static_cast<std::size_t>(
			kAdjacentLowerMidi - kFirstMidi)] = 0.20f;
		std::array<float, kNoteProbeCount> weak_adjacent_powers = {};
		std::array<float, kNoteProbeCount> weak_adjacent_raw_powers = {};
		set_probe_level(weak_adjacent_powers, kAdjacentLowerMidi, 0.20f);
		set_probe_level(weak_adjacent_powers, kAdjacentAliasMidi, 0.72f);
		set_probe_level(weak_adjacent_raw_powers, kAdjacentLowerMidi, 0.20f);
		set_probe_level(weak_adjacent_raw_powers, kAdjacentAliasMidi, 0.72f);
		prefer_raw_supported_mid_keyboard_lower_octave_primary(
			weak_adjacent_grid, weak_adjacent_state, weak_adjacent_ownership,
			weak_adjacent_powers, weak_adjacent_raw_powers, -1);
		const NoteCell weak_adjacent_primary = note_grid_primary_cell_for_pitch_class(
			weak_adjacent_grid, midi_pitch_class(kAdjacentLowerMidi));
		runner.expect(weak_adjacent_primary.active &&
				      weak_adjacent_primary.midi == kAdjacentAliasMidi,
			      "mid keyboard lower octave: expected weak adjacent lower support to keep alias");

		NoteGrid guitar_adjacent_grid = {};
		write_note_grid_cell(guitar_adjacent_grid, NoteCandidate{kAdjacentAliasMidi, 0.90f},
				     1.0f, 1.0f);
		InstrumentState guitar_adjacent_state = {};
		write_note_grid_label(guitar_adjacent_state, guitar_adjacent_grid, -1);
		FullMixOwnership guitar_adjacent_ownership = adjacent_ownership;
		FullMixDebugCandidate &guitar_adjacent_debug =
			guitar_adjacent_ownership.debug_candidates[0];
		guitar_adjacent_debug.owner = InstrumentKind::Guitar;
		guitar_adjacent_debug.keyboard_score = 0.0f;
		guitar_adjacent_debug.guitar_score = 0.95f;
		guitar_adjacent_debug.harmonic_ratios[1] = 0.0f;
		guitar_adjacent_debug.harmonic_ratios[3] = 0.0f;
		guitar_adjacent_debug.spectral_centroid = 0.0f;
		prefer_raw_supported_mid_keyboard_lower_octave_primary(
			guitar_adjacent_grid, guitar_adjacent_state, guitar_adjacent_ownership,
			adjacent_powers, adjacent_raw_powers, -1);
		const NoteCell guitar_adjacent_primary = note_grid_primary_cell_for_pitch_class(
			guitar_adjacent_grid, midi_pitch_class(kAdjacentLowerMidi));
		runner.expect(guitar_adjacent_primary.active &&
				      guitar_adjacent_primary.midi == kAdjacentAliasMidi,
			      "mid keyboard lower octave: expected unsupported adjacent guitar alias to stay primary");
	}

	NoteGrid weak_grid = {};
	write_note_grid_cell(weak_grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState weak_state = {};
	write_note_grid_label(weak_state, weak_grid, -1);
	FullMixOwnership weak_ownership = ownership;
	weak_ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.18f;
	std::array<float, kNoteProbeCount> weak_powers = {};
	std::array<float, kNoteProbeCount> weak_raw_powers = {};
	set_probe_level(weak_powers, kLowerMidi, 0.18f);
	set_probe_level(weak_powers, kAliasMidi, 0.82f);
	set_probe_level(weak_raw_powers, kLowerMidi, 0.18f);
	set_probe_level(weak_raw_powers, kLowerMidi + 12, 0.78f);
	set_probe_level(weak_raw_powers, kAliasMidi, 0.82f);
	prefer_raw_supported_mid_keyboard_lower_octave_primary(weak_grid, weak_state, weak_ownership,
							       weak_powers, weak_raw_powers, -1);
	const NoteCell weak_primary =
		note_grid_primary_cell_for_pitch_class(weak_grid, midi_pitch_class(kLowerMidi));
	runner.expect(weak_primary.active && weak_primary.midi == kAliasMidi,
		      "mid keyboard lower octave: expected weak lower support to keep high alias");

	NoteGrid non_keyboard_alias_grid = {};
	write_note_grid_cell(non_keyboard_alias_grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState non_keyboard_alias_state = {};
	write_note_grid_label(non_keyboard_alias_state, non_keyboard_alias_grid, -1);
	FullMixOwnership non_keyboard_alias = ownership;
	FullMixDebugCandidate &non_keyboard_debug = non_keyboard_alias.debug_candidates[0];
	non_keyboard_debug.owner = InstrumentKind::Guitar;
	non_keyboard_debug.keyboard_score = 0.0f;
	non_keyboard_debug.guitar_score = 1.0f;
	non_keyboard_debug.spectral_level = 1.0f;
	non_keyboard_debug.pitch_confidence = 0.92f;
	non_keyboard_debug.periodicity = 0.86f;
	non_keyboard_debug.harmonic_fit_error = 0.14f;
	non_keyboard_debug.local_noise_level = 0.005f;
	non_keyboard_debug.spectral_centroid = 0.20f;
	non_keyboard_debug.spectral_slope = 0.06f;
	non_keyboard_debug.harmonic_ratios[1] = 0.66f;
	non_keyboard_debug.harmonic_ratios[2] = 0.035f;
	non_keyboard_debug.harmonic_ratios[3] = 0.009f;
	non_keyboard_debug.harmonic_ratios[4] = 0.001f;
	prefer_raw_supported_mid_keyboard_lower_octave_primary(
		non_keyboard_alias_grid, non_keyboard_alias_state, non_keyboard_alias, powers, raw_powers,
		-1);
	const NoteCell non_keyboard_primary =
		note_grid_primary_cell_for_pitch_class(non_keyboard_alias_grid,
						       midi_pitch_class(kLowerMidi));
	runner.expect(non_keyboard_primary.active && non_keyboard_primary.midi == kLowerMidi,
		      "mid keyboard lower octave: expected display-supported non-keyboard alias to fold to raw lower note");

	NoteGrid unsupported_grid = {};
	write_note_grid_cell(unsupported_grid, NoteCandidate{kAliasMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState unsupported_state = {};
	write_note_grid_label(unsupported_state, unsupported_grid, -1);
	FullMixOwnership unsupported_ownership = ownership;
	unsupported_ownership.debug_candidates[0].owner = InstrumentKind::Guitar;
	unsupported_ownership.debug_candidates[0].keyboard_score = 0.0f;
	unsupported_ownership.debug_candidates[0].guitar_score = 0.95f;
	prefer_raw_supported_mid_keyboard_lower_octave_primary(
		unsupported_grid, unsupported_state, unsupported_ownership, powers, raw_powers, -1);
	const NoteCell unsupported_primary =
		note_grid_primary_cell_for_pitch_class(unsupported_grid, midi_pitch_class(kLowerMidi));
	runner.expect(unsupported_primary.active && unsupported_primary.midi == kAliasMidi,
		      "mid keyboard lower octave: expected unsupported guitar alias to stay primary");
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
	runner.expect(note_grid_midi_level(guitar_grid, kGuitarAliasMidi) < 0.50f,
		      "lower non-guitar guitar octave shadow: expected row level to attenuate");

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

FullMixDebugCandidate make_non_guitar_owned_guitar_alias_debug(int midi, InstrumentKind owner)
{
	FullMixDebugCandidate debug = {};
	debug.midi = midi;
	debug.owner = owner;
	debug.ownership_confidence = 0.88f;
	debug.guitar_score = owner == InstrumentKind::Guitar ? 0.88f : 0.12f;
	debug.other_score = owner == InstrumentKind::Guitar ? 0.00f : 0.88f;
	debug.spectral_level = 0.70f;
	debug.pitch_confidence = 0.83f;
	debug.periodicity = 0.85f;
	debug.harmonicity = 1.80f;
	debug.harmonic_fit_error = 0.12f;
	debug.local_noise_level = 0.25f;
	debug.spectral_centroid = 0.32f;
	debug.spectral_slope = 0.10f;
	return debug;
}

void check_non_guitar_owned_guitar_octave_alias_display_is_suppressed(Runner &runner)
{
	static constexpr int kLowerMidi = 45;
	static constexpr int kAliasMidi = kLowerMidi + 12;

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 2;
	ownership.debug_candidates[0] =
		make_non_guitar_owned_guitar_alias_debug(kAliasMidi, InstrumentKind::Other);
	ownership.debug_candidates[1] =
		make_non_guitar_owned_guitar_alias_debug(kLowerMidi, InstrumentKind::Other);
	ownership.global_note_levels[static_cast<std::size_t>(kAliasMidi - kFirstMidi)] = 0.70f;
	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.56f;
	NoteCandidate alias = {};
	alias.midi = kAliasMidi;
	alias.score = 0.70f;
	alias.ownership_confidence = 0.82f;

	runner.expect(guitar_display_candidate_shadowed_by_non_guitar_pitch(ownership, alias),
		      "non-guitar-owned guitar octave alias: expected upper other-owned alias to suppress");

	FullMixOwnership guitar_owned = ownership;
	guitar_owned.debug_candidates[0] =
		make_non_guitar_owned_guitar_alias_debug(kAliasMidi, InstrumentKind::Guitar);
	runner.expect(!guitar_display_candidate_shadowed_by_non_guitar_pitch(guitar_owned, alias),
		      "non-guitar-owned guitar octave alias: expected guitar-owned upper note to stay visible");

	FullMixOwnership weak_lower = ownership;
	weak_lower.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.44f;
	runner.expect(!guitar_display_candidate_shadowed_by_non_guitar_pitch(weak_lower, alias),
		      "non-guitar-owned guitar octave alias: expected weak lower support to leave alias visible");
}

void check_other_dominant_same_pitch_guitar_display_is_pruned(Runner &runner)
{
	static constexpr int kMidi = 51;

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	ownership.debug_candidates[0].midi = kMidi;
	ownership.debug_candidates[0].owner = InstrumentKind::Other;
	ownership.debug_candidates[0].ownership_confidence = 0.86f;
	ownership.debug_candidates[0].other_score = 0.873f;
	ownership.debug_candidates[0].guitar_score = 0.127f;
	ownership.debug_candidates[0].keyboard_score = 0.0f;
	ownership.debug_candidates[0].spectral_level = 0.52f;
	ownership.debug_candidates[0].pitch_confidence = 0.36f;
	ownership.debug_candidates[0].periodicity = 0.70f;
	ownership.debug_candidates[0].harmonic_fit_error = 0.52f;
	ownership.debug_candidates[0].local_noise_level = 0.23f;
	ownership.global_note_levels[static_cast<std::size_t>(kMidi - kFirstMidi)] = 0.70f;

	NoteCandidateList candidates;
	candidates.push_back(NoteCandidate{kMidi, 1.0f, 0.86f});
	const NoteCandidateList pruned =
		prune_shadowed_full_mix_guitar_display_candidates(ownership, candidates);
	runner.expect(!candidate_list_has_midi(pruned, kMidi),
		      "other-dominant same-pitch guitar display: expected measured other-owned row to prune guitar");

	FullMixOwnership protected_by_keyboard = ownership;
	protected_by_keyboard.debug_candidates[0].keyboard_score = 0.02f;
	const NoteCandidateList keyboard_protected =
		prune_shadowed_full_mix_guitar_display_candidates(protected_by_keyboard, candidates);
	runner.expect(candidate_list_has_midi(keyboard_protected, kMidi),
		      "other-dominant same-pitch guitar display: expected keyboard-supported candidate to stay");

	FullMixOwnership protected_by_guitar_score = ownership;
	protected_by_guitar_score.debug_candidates[0].guitar_score = 0.18f;
	const NoteCandidateList guitar_score_protected =
		prune_shadowed_full_mix_guitar_display_candidates(protected_by_guitar_score, candidates);
	runner.expect(candidate_list_has_midi(guitar_score_protected, kMidi),
		      "other-dominant same-pitch guitar display: expected stronger guitar score to stay");
}

void check_other_dominant_octave_alias_guitar_display_is_pruned(Runner &runner)
{
	static constexpr int kLowerMidi = 51;
	static constexpr int kAlias12 = kLowerMidi + 12;
	static constexpr int kAlias24 = kLowerMidi + 24;

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 3;
	ownership.debug_candidates[0].midi = kAlias12;
	ownership.debug_candidates[0].owner = InstrumentKind::Guitar;
	ownership.debug_candidates[0].ownership_confidence = 0.88f;
	ownership.debug_candidates[0].guitar_score = 0.42f;
	ownership.debug_candidates[0].spectral_level = 0.52f;
	ownership.debug_candidates[0].pitch_confidence = 0.32f;
	ownership.debug_candidates[0].periodicity = 0.70f;
	ownership.debug_candidates[0].harmonicity = 0.70f;
	ownership.debug_candidates[0].harmonic_fit_error = 0.52f;
	ownership.debug_candidates[0].local_noise_level = 0.22f;
	ownership.debug_candidates[0].spectral_centroid = 0.50f;
	ownership.debug_candidates[0].spectral_slope = 0.64f;
	ownership.debug_candidates[1] = ownership.debug_candidates[0];
	ownership.debug_candidates[1].midi = kAlias24;
	ownership.debug_candidates[2].midi = kLowerMidi;
	ownership.debug_candidates[2].owner = InstrumentKind::Other;
	ownership.debug_candidates[2].ownership_confidence = 0.86f;
	ownership.debug_candidates[2].other_score = 0.90f;
	ownership.debug_candidates[2].guitar_score = 0.10f;
	ownership.debug_candidates[2].keyboard_score = 0.0f;
	ownership.debug_candidates[2].spectral_level = 0.78f;
	ownership.debug_candidates[2].pitch_confidence = 0.51f;
	ownership.debug_candidates[2].periodicity = 0.72f;
	ownership.debug_candidates[2].harmonic_fit_error = 0.30f;
	ownership.debug_candidates[2].local_noise_level = 0.24f;

	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 1.0f;
	ownership.global_note_levels[static_cast<std::size_t>(kAlias12 - kFirstMidi)] = 0.70f;
	ownership.global_note_levels[static_cast<std::size_t>(kAlias24 - kFirstMidi)] = 0.62f;

	NoteCandidateList candidates;
	candidates.push_back(NoteCandidate{kAlias12, 0.70f, 0.88f});
	candidates.push_back(NoteCandidate{kAlias24, 0.62f, 0.88f});
	const NoteCandidateList pruned =
		prune_shadowed_full_mix_guitar_display_candidates(ownership, candidates);
	runner.expect(candidate_list_has_midi(pruned, kAlias12),
		      "other-dominant octave alias guitar display: expected +12 alias to stay");
	runner.expect(!candidate_list_has_midi(pruned, kAlias24),
		      "other-dominant octave alias guitar display: expected +24 alias to prune");

	FullMixOwnership keyboard_supported_lower = ownership;
	keyboard_supported_lower.debug_candidates[2].keyboard_score = 0.02f;
	const NoteCandidateList keyboard_protected =
		prune_shadowed_full_mix_guitar_display_candidates(keyboard_supported_lower, candidates);
	runner.expect(candidate_list_has_midi(keyboard_protected, kAlias12),
		      "other-dominant octave alias guitar display: expected keyboard-supported lower pitch to keep +12");
	runner.expect(candidate_list_has_midi(keyboard_protected, kAlias24),
		      "other-dominant octave alias guitar display: expected keyboard-supported lower pitch to protect +24");

	FullMixOwnership guitar_supported_lower = ownership;
	guitar_supported_lower.debug_candidates[2].guitar_score = 0.18f;
	const NoteCandidateList guitar_protected =
		prune_shadowed_full_mix_guitar_display_candidates(guitar_supported_lower, candidates);
	runner.expect(candidate_list_has_midi(guitar_protected, kAlias12),
		      "other-dominant octave alias guitar display: expected guitar-supported lower pitch to keep +12");
	runner.expect(candidate_list_has_midi(guitar_protected, kAlias24),
		      "other-dominant octave alias guitar display: expected guitar-supported lower pitch to protect +24");

	FullMixOwnership confident_upper = ownership;
	confident_upper.debug_candidates[0].guitar_score = 0.92f;
	confident_upper.debug_candidates[0].pitch_confidence = 0.90f;
	confident_upper.debug_candidates[0].periodicity = 0.84f;
	confident_upper.debug_candidates[1] = confident_upper.debug_candidates[0];
	confident_upper.debug_candidates[1].midi = kAlias24;
	const NoteCandidateList confident_protected =
		prune_shadowed_full_mix_guitar_display_candidates(confident_upper, candidates);
	runner.expect(candidate_list_has_midi(confident_protected, kAlias12),
		      "other-dominant octave alias guitar display: expected confident guitar upper to protect +12");
	runner.expect(candidate_list_has_midi(confident_protected, kAlias24),
		      "other-dominant octave alias guitar display: expected confident guitar upper to protect +24");
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

void check_low_confidence_mirror_cell_uses_visual_floor_without_changing_level(Runner &runner)
{
	static constexpr int kMidi = 60;

	NoteGrid grid = {};
	write_note_grid_cell(grid, NoteCandidate{kMidi, 1.0f, 0.20f}, 1.0f, 1.0f);
	const NoteCell primary = note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kMidi));
	runner.expect(std::fabs(primary.level - 0.20f) < 0.001f,
		      "low confidence mirror visual floor: expected analytic level to stay ownership-scaled");
	runner.expect(std::fabs(note_grid_midi_visual_level(grid, kMidi) - 0.25f) < 0.001f,
		      "low confidence mirror visual floor: expected full-strength mirror to render at floor");

	NoteGrid weak_score_grid = {};
	write_note_grid_cell(weak_score_grid, NoteCandidate{kMidi, 0.50f, 0.20f}, 1.0f, 1.0f);
	const NoteCell weak_score_primary =
		note_grid_primary_cell_for_pitch_class(weak_score_grid, midi_pitch_class(kMidi));
	runner.expect(std::fabs(weak_score_primary.level - 0.10f) < 0.001f,
		      "low confidence mirror visual floor: expected weak analytic level to stay relative");
	runner.expect(std::fabs(note_grid_midi_visual_level(weak_score_grid, kMidi) - 0.125f) < 0.001f,
		      "low confidence mirror visual floor: expected visual floor to preserve relative score");
}

void check_low_acoustic_guitar_display_mirror_gets_bright_score_floor(Runner &runner)
{
	static constexpr int kMidi = 45;
	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kMidi - kFirstMidi)] = 1.0f;

	FullMixDebugCandidate debug = {};
	debug.midi = kMidi;
	debug.owner = InstrumentKind::Guitar;
	debug.ownership_confidence = 0.96f;
	debug.guitar_score = 0.96f;
	debug.spectral_level = 0.90f;
	debug.pitch_confidence = 0.78f;
	debug.periodicity = 0.74f;
	debug.harmonic_fit_error = 0.060f;
	debug.local_noise_level = 0.38f;
	debug.harmonic_ratios[1] = 0.36f;
	debug.harmonic_ratios[2] = 0.12f;
	debug.harmonic_ratios[3] = 0.080f;
	debug.harmonic_ratios[4] = 0.060f;

	NoteCandidateList candidates;
	candidates.push_back(NoteCandidate{64, 1.0f, 0.90f});
	add_full_mix_display_mirror(candidates, ownership, debug, FullMixDisplayRow::Guitar);
	runner.expect(candidate_score_for_midi(candidates, kMidi) >= 0.739f,
		      "low acoustic guitar display mirror: expected supported low string to get bright score floor");

	FullMixDebugCandidate bass_like = debug;
	bass_like.bass_score = 0.80f;
	NoteCandidateList bass_like_candidates;
	bass_like_candidates.push_back(NoteCandidate{64, 1.0f, 0.90f});
	add_full_mix_display_mirror(bass_like_candidates, ownership, bass_like, FullMixDisplayRow::Guitar);
	runner.expect(candidate_score_for_midi(bass_like_candidates, kMidi) < 0.60f,
		      "low acoustic guitar display mirror: expected bass-like candidate to keep conservative score");
}

void check_high_clean_acoustic_guitar_display_mirror_gets_bright_score_floor(Runner &runner)
{
	static constexpr int kMidi = 69;
	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kMidi - kFirstMidi)] = 0.06f;

	FullMixDebugCandidate debug = {};
	debug.midi = kMidi;
	debug.owner = InstrumentKind::Keyboard;
	debug.ownership_confidence = 1.0f;
	debug.keyboard_score = 1.0f;
	debug.spectral_level = 1.0f;
	debug.pitch_confidence = 0.95f;
	debug.periodicity = 0.75f;
	debug.harmonic_fit_error = 0.018f;
	debug.spectral_slope = 0.032f;
	debug.local_noise_level = 0.009f;
	debug.adjacent_lower_ratio = 0.001f;
	debug.adjacent_upper_ratio = 0.001f;
	debug.harmonic_ratios[1] = 0.10f;
	debug.harmonic_ratios[2] = 0.020f;
	debug.harmonic_ratios[3] = 0.020f;
	debug.harmonic_ratios[4] = 0.001f;

	NoteCandidateList candidates;
	candidates.push_back(NoteCandidate{64, 1.0f, 0.90f});
	add_full_mix_display_mirror(candidates, ownership, debug, FullMixDisplayRow::Guitar);
	runner.expect(candidate_score_for_midi(candidates, kMidi) >= 0.739f,
		      "high clean acoustic guitar display mirror: expected weak exact high string to get bright score floor");

	FullMixDebugCandidate noisy = debug;
	noisy.local_noise_level = 0.030f;
	NoteCandidateList noisy_candidates;
	noisy_candidates.push_back(NoteCandidate{64, 1.0f, 0.90f});
	add_full_mix_display_mirror(noisy_candidates, ownership, noisy, FullMixDisplayRow::Guitar);
	runner.expect(!candidate_list_has_midi(noisy_candidates, kMidi),
		      "high clean acoustic guitar display mirror: expected noisy high candidate to stay suppressed");
}

void check_existing_upper_clean_guitar_visual_note_is_brightened(Runner &runner)
{
	static constexpr int kMidi = 86;

	NoteGrid guitar_grid = {};
	set_midi(guitar_grid, kMidi, 1.0f);
	guitar_grid.cells[static_cast<std::size_t>(midi_pitch_class(kMidi))].visual_level = 0.36f;
	NoteGrid keyboard_grid = {};
	set_midi(keyboard_grid, kMidi, 1.0f);

	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kMidi;
	debug.owner = InstrumentKind::Keyboard;
	debug.keyboard_score = 1.0f;
	debug.spectral_level = 1.0f;
	debug.pitch_confidence = 0.94f;
	debug.periodicity = 0.72f;
	debug.harmonic_fit_error = 0.055f;
	debug.local_noise_level = 0.004f;
	debug.spectral_slope = 0.001f;
	debug.adjacent_lower_ratio = 0.002f;
	debug.adjacent_upper_ratio = 0.002f;
	debug.harmonic_ratios[1] = 0.010f;
	debug.harmonic_ratios[2] = 0.001f;
	debug.harmonic_ratios[3] = 0.0f;
	debug.harmonic_ratios[4] = 0.0f;

	boost_existing_upper_clean_guitar_visual_notes(guitar_grid, keyboard_grid, ownership);
	runner.expect(note_grid_midi_visual_level(guitar_grid, kMidi) >= 0.739f,
		      "existing upper clean guitar visual: expected D6 visual level to be brightened");
	runner.expect(note_grid_midi_level(guitar_grid, kMidi) > 0.99f,
		      "existing upper clean guitar visual: expected analytic guitar level to stay unchanged");
	runner.expect(note_grid_midi_visual_level(keyboard_grid, kMidi) > 0.99f,
		      "existing upper clean guitar visual: expected keyboard visual level to stay unchanged");

	NoteGrid weak_guitar_grid = {};
	set_midi(weak_guitar_grid, kMidi, 0.50f);
	weak_guitar_grid.cells[static_cast<std::size_t>(midi_pitch_class(kMidi))].visual_level = 0.20f;
	boost_existing_upper_clean_guitar_visual_notes(weak_guitar_grid, keyboard_grid, ownership);
	runner.expect(note_grid_midi_visual_level(weak_guitar_grid, kMidi) < 0.21f,
		      "existing upper clean guitar visual: expected weak guitar cell to stay dim");
}

void check_existing_reed_brass_other_visual_note_is_brightened(Runner &runner)
{
	static constexpr int kMidi = 67;

	NoteGrid other_grid = {};
	set_midi(other_grid, kMidi, 0.21f);
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kMidi;
	debug.owner = InstrumentKind::Guitar;
	debug.guitar_score = 0.90f;
	debug.spectral_level = 1.0f;
	debug.pitch_confidence = 0.91f;
	debug.periodicity = 0.77f;
	debug.harmonic_fit_error = 0.049f;
	debug.local_noise_level = 0.011f;
	debug.spectral_centroid = 0.24f;
	debug.spectral_slope = 0.19f;
	debug.harmonic_ratios[1] = 0.49f;
	debug.harmonic_ratios[2] = 0.21f;
	debug.harmonic_ratios[3] = 0.033f;
	debug.harmonic_ratios[4] = 0.035f;

	boost_existing_reed_brass_other_visual_notes(other_grid, ownership);
	runner.expect(note_grid_midi_visual_level(other_grid, kMidi) >= 0.579f,
		      "existing reed/brass other visual: expected existing other note to be brightened");
	runner.expect(note_grid_midi_level(other_grid, kMidi) < 0.22f,
		      "existing reed/brass other visual: expected analytic other level to stay unchanged");

	NoteGrid weak_other_grid = {};
	set_midi(weak_other_grid, kMidi, 0.10f);
	boost_existing_reed_brass_other_visual_notes(weak_other_grid, ownership);
	runner.expect(note_grid_midi_visual_level(weak_other_grid, kMidi) < 0.11f,
		      "existing reed/brass other visual: expected weak other cell to stay dim");

	NoteGrid noisy_other_grid = {};
	set_midi(noisy_other_grid, kMidi, 0.21f);
	FullMixOwnership noisy_ownership = ownership;
	noisy_ownership.debug_candidates[0].local_noise_level = 0.25f;
	noisy_ownership.debug_candidates[0].spectral_centroid = 0.42f;
	boost_existing_reed_brass_other_visual_notes(noisy_other_grid, noisy_ownership);
	runner.expect(note_grid_midi_visual_level(noisy_other_grid, kMidi) < 0.22f,
		      "existing reed/brass other visual: expected noisy keyboard-like body to stay dim");
}

void check_other_owned_low_wind_alias_maps_to_lower_octave(Runner &runner)
{
	static constexpr int kLowerMidi = 38;
	static constexpr int kAliasMidi = kLowerMidi + 12;

	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.26f;
	ownership.global_note_levels[static_cast<std::size_t>(kAliasMidi - kFirstMidi)] = 0.82f;

	FullMixDebugCandidate debug = {};
	debug.midi = kAliasMidi;
	debug.owner = InstrumentKind::Other;
	debug.other_score = 0.86f;
	debug.guitar_score = 0.13f;
	debug.keyboard_score = 0.02f;
	debug.spectral_level = 0.31f;
	debug.pitch_confidence = 0.18f;
	debug.periodicity = 0.64f;
	debug.harmonicity = 3.8f;
	debug.local_noise_level = 0.27f;
	debug.spectral_centroid = 0.53f;
	debug.spectral_slope = 1.44f;
	debug.harmonic_ratios[1] = 0.96f;
	debug.harmonic_ratios[2] = 2.02f;
	debug.harmonic_ratios[3] = 0.26f;
	debug.harmonic_ratios[4] = 0.55f;

	NoteCandidateList candidates;
	add_full_mix_display_mirror(candidates, ownership, debug, FullMixDisplayRow::Other);
	runner.expect(candidate_list_has_midi(candidates, kLowerMidi),
		      "other low wind octave alias: expected supported first-overtone candidate to map down");
	runner.expect(!candidate_list_has_midi(candidates, kAliasMidi),
		      "other low wind octave alias: expected alias octave not to be emitted");

	FullMixOwnership weak_lower = ownership;
	weak_lower.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.05f;
	NoteCandidateList weak_candidates;
	add_full_mix_display_mirror(weak_candidates, weak_lower, debug, FullMixDisplayRow::Other);
	runner.expect(!candidate_list_has_midi(weak_candidates, kLowerMidi),
		      "other low wind octave alias: expected weak lower support not to map down");

	FullMixDebugCandidate bass_shaped = debug;
	bass_shaped.bass_score = 0.24f;
	NoteCandidateList bass_shaped_candidates;
	add_full_mix_display_mirror(bass_shaped_candidates, ownership, bass_shaped, FullMixDisplayRow::Other);
	runner.expect(!candidate_list_has_midi(bass_shaped_candidates, kLowerMidi),
		      "other low wind octave alias: expected bass-shaped alias not to map down");
}

void check_vocal_owned_upper_alias_promotes_supported_lower_primary(Runner &runner)
{
	static constexpr int kLowerMidi = 50;
	static constexpr int kUpperMidi = kLowerMidi + 12;

	NoteGrid grid = {};
	write_note_grid_cell(grid, NoteCandidate{kUpperMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState state = {};
	write_note_grid_label(state, grid, -1);

	FullMixOwnership ownership = {};
	ownership.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 1.0f;
	ownership.global_note_levels[static_cast<std::size_t>(kUpperMidi - kFirstMidi)] = 0.72f;
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kUpperMidi;
	debug.owner = InstrumentKind::Vocal;
	debug.ownership_confidence = 0.80f;
	debug.keyboard_score = 0.20f;
	debug.vocal_score = 0.80f;
	debug.spectral_level = 1.0f;
	debug.pitch_confidence = 0.93f;
	debug.periodicity = 0.74f;
	debug.harmonic_fit_error = 0.02f;
	debug.local_noise_level = 0.05f;

	std::array<float, kNoteProbeCount> powers = {};
	set_probe_level(powers, kLowerMidi, 1.0f);
	set_probe_level(powers, kUpperMidi, 0.70f);

	prefer_debug_supported_vocal_lower_octave_primary(grid, state, ownership, powers,
							  kFullMixVocalMinMidi, -1);
	const NoteCell primary =
		note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kLowerMidi));
	runner.expect(primary.active && primary.midi == kLowerMidi,
		      "vocal lower octave primary: expected supported D3 to replace vocal-owned D4 alias");

	NoteGrid keyboard_like_grid = {};
	write_note_grid_cell(keyboard_like_grid, NoteCandidate{kUpperMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState keyboard_like_state = {};
	write_note_grid_label(keyboard_like_state, keyboard_like_grid, -1);
	FullMixOwnership keyboard_like = ownership;
	keyboard_like.debug_candidates[0].keyboard_score = 0.40f;
	prefer_debug_supported_vocal_lower_octave_primary(keyboard_like_grid, keyboard_like_state,
							  keyboard_like, powers,
							  kFullMixVocalMinMidi, -1);
	const NoteCell keyboard_like_primary =
		note_grid_primary_cell_for_pitch_class(keyboard_like_grid, midi_pitch_class(kLowerMidi));
	runner.expect(keyboard_like_primary.active && keyboard_like_primary.midi == kUpperMidi,
		      "vocal lower octave primary: expected keyboard-heavy upper alias to stay primary");

	NoteGrid weak_lower_grid = {};
	write_note_grid_cell(weak_lower_grid, NoteCandidate{kUpperMidi, 1.0f}, 1.0f, 1.0f);
	InstrumentState weak_lower_state = {};
	write_note_grid_label(weak_lower_state, weak_lower_grid, -1);
	FullMixOwnership weak_lower = ownership;
	weak_lower.global_note_levels[static_cast<std::size_t>(kLowerMidi - kFirstMidi)] = 0.08f;
	std::array<float, kNoteProbeCount> weak_powers = {};
	set_probe_level(weak_powers, kLowerMidi, 0.08f);
	set_probe_level(weak_powers, kUpperMidi, 0.70f);
	prefer_debug_supported_vocal_lower_octave_primary(weak_lower_grid, weak_lower_state, weak_lower,
							  weak_powers, kFullMixVocalMinMidi, -1);
	const NoteCell weak_lower_primary =
		note_grid_primary_cell_for_pitch_class(weak_lower_grid, midi_pitch_class(kLowerMidi));
	runner.expect(weak_lower_primary.active && weak_lower_primary.midi == kUpperMidi,
		      "vocal lower octave primary: expected weak lower support to keep upper alias primary");
}

void check_low_wind_other_octave_alias_promotes_raw_fundamental(Runner &runner)
{
	static constexpr int kLowerMidi = 40;
	static constexpr int kPrimaryMidi = kLowerMidi + 12;
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kPrimaryMidi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.86f;
	debug.other_score = 0.86f;
	debug.guitar_score = 0.14f;
	debug.keyboard_score = 0.0f;
	debug.vocal_score = 0.0f;
	debug.spectral_level = 0.62f;
	debug.pitch_confidence = 0.48f;
	debug.periodicity = 0.75f;
	debug.harmonic_fit_error = 0.24f;
	debug.local_noise_level = 0.20f;

	NoteGrid grid = {};
	InstrumentState state = {};
	set_midi(grid, kPrimaryMidi, 0.82f);
	write_note_grid_label(state, grid, -1);

	std::array<float, kNoteProbeCount> powers = {};
	set_probe_level(powers, kLowerMidi, 0.46f);
	set_probe_level(powers, kPrimaryMidi, 1.00f);
	set_probe_level(powers, kLowerMidi + 19, 0.32f);
	set_probe_level(powers, kLowerMidi + 24, 0.76f);
	set_probe_level(powers, kLowerMidi + 31, 0.76f);
	set_probe_level(powers, kLowerMidi + 36, 0.48f);

	prefer_probe_supported_low_wind_other_primary(grid, state, ownership, powers, kOtherMinMidi, -1);
	const NoteCell primary = note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kLowerMidi));
	runner.expect(primary.active && primary.midi == kLowerMidi,
		      "low wind other alias: expected raw lower fundamental promoted over octave alias");
	runner.expect(std::strstr(state.label, "E2") != nullptr,
		      std::string("low wind other alias: expected E2 label, got `") + state.label + "`");
}

void check_low_wind_other_octave_alias_requires_upper_stack(Runner &runner)
{
	static constexpr int kLowerMidi = 40;
	static constexpr int kPrimaryMidi = kLowerMidi + 12;
	FullMixOwnership ownership = {};
	ownership.debug_candidate_count = 1;
	FullMixDebugCandidate &debug = ownership.debug_candidates[0];
	debug.midi = kPrimaryMidi;
	debug.owner = InstrumentKind::Other;
	debug.ownership_confidence = 0.86f;
	debug.other_score = 0.86f;
	debug.spectral_level = 0.62f;
	debug.pitch_confidence = 0.48f;
	debug.periodicity = 0.75f;
	debug.harmonic_fit_error = 0.24f;
	debug.local_noise_level = 0.20f;

	NoteGrid grid = {};
	InstrumentState state = {};
	set_midi(grid, kPrimaryMidi, 0.82f);
	write_note_grid_label(state, grid, -1);

	std::array<float, kNoteProbeCount> powers = {};
	set_probe_level(powers, kLowerMidi, 0.46f);
	set_probe_level(powers, kPrimaryMidi, 1.00f);
	set_probe_level(powers, kLowerMidi + 19, 0.08f);
	set_probe_level(powers, kLowerMidi + 24, 0.12f);
	set_probe_level(powers, kLowerMidi + 31, 0.08f);
	set_probe_level(powers, kLowerMidi + 36, 0.10f);

	prefer_probe_supported_low_wind_other_primary(grid, state, ownership, powers, kOtherMinMidi, -1);
	const NoteCell primary = note_grid_primary_cell_for_pitch_class(grid, midi_pitch_class(kLowerMidi));
	runner.expect(primary.active && primary.midi == kPrimaryMidi,
		      "low wind other alias guard: expected weak upper stack to keep original primary");
}

int run()
{
	Runner runner;
	check_crowded_guitar_prune_modes(runner);
	check_displayed_same_root_plain_guitar_primary(runner);
	check_displayed_supported_plain_guitar_primary(runner);
	check_source_supported_plain_guitar_alias_recovery(runner);
	check_plain_guitar_voicing_rejects_crowded_root_fifth_quality(runner);
	check_displayed_guitar_single_note_probe_profile(runner);
	check_supported_guitar_candidate_alias_merge(runner);
	check_supported_guitar_display_extension_aliases(runner);
	check_ambiguous_guitar_power_quality_keeps_both_plain_aliases(runner);
	check_compact_guitar_power_raw_profile_third_aliases(runner);
	check_same_pitch_guitar_bass_shadow_uses_any_matching_debug(runner);
	check_keyboard_owned_same_pitch_vocal_shadow_uses_weak_target_guard(runner);
	check_other_owned_same_pitch_vocal_shadow_uses_measured_threshold(runner);
	check_vocal_owned_same_pitch_bass_shadow_uses_measured_ratio(runner);
	check_other_owned_same_pitch_bass_shadow_uses_measured_ratio(runner);
	check_keyboard_owned_same_pitch_bass_shadow_uses_weak_ceiling(runner);
	check_keyboard_owned_same_pitch_bass_shadow_uses_dominant_ratio(runner);
	check_other_owned_pitch_class_keyboard_shadow_is_attenuated(runner);
	check_measured_other_fundamental_display_level_boost(runner);
	check_electronic_keyboard_other_shadow_is_attenuated(runner);
	check_lower_other_pitch_class_keyboard_octave_shadow_is_attenuated(runner);
	check_low_electronic_bass_alias_promotes_fundamental_display(runner);
	check_ambiguous_electronic_keyboard_promotes_exact_lower_octave(runner);
	check_raw_supported_mid_keyboard_lower_octave_promotes_alias(runner);
	check_lower_non_guitar_pitch_class_guitar_octave_shadow_uses_measured_levels(runner);
	check_non_guitar_owned_guitar_octave_alias_display_is_suppressed(runner);
	check_other_dominant_same_pitch_guitar_display_is_pruned(runner);
	check_other_dominant_octave_alias_guitar_display_is_pruned(runner);
	check_display_ownership_scale_keeps_confirmed_mid_confidence_visible(runner);
	check_low_confidence_mirror_cell_uses_visual_floor_without_changing_level(runner);
	check_low_acoustic_guitar_display_mirror_gets_bright_score_floor(runner);
	check_high_clean_acoustic_guitar_display_mirror_gets_bright_score_floor(runner);
	check_existing_upper_clean_guitar_visual_note_is_brightened(runner);
	check_existing_reed_brass_other_visual_note_is_brightened(runner);
	check_other_owned_low_wind_alias_maps_to_lower_octave(runner);
	check_vocal_owned_upper_alias_promotes_supported_lower_primary(runner);
	check_low_wind_other_octave_alias_promotes_raw_fundamental(runner);
	check_low_wind_other_octave_alias_requires_upper_stack(runner);
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
