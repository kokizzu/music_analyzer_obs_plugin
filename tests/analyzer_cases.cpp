#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

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

mao::AnalysisSnapshot analyze_buffer(const mao_test::Buffer &buffer, const char *source = "cases")
{
	mao::AnalysisEngine engine;
	const mao::AnalysisSettings settings = mao_test::default_settings();
	return engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
}

void expect_label(Runner &runner, const char *actual, const std::string &expected, const std::string &context)
{
	runner.expect(std::strcmp(actual, expected.c_str()) == 0,
		      context + ": expected `" + expected + "`, got `" + actual + "`");
}

void expect_note_token(Runner &runner, const char *actual, const char *expected, const std::string &context)
{
	runner.expect(mao_test::has_note_token(actual, expected),
		      context + ": expected note token `" + expected + "`, got `" + actual + "`");
}

void expect_no_chord(Runner &runner, const mao::InstrumentState &chord, const std::string &context)
{
	runner.expect(std::strcmp(chord.label, "--") == 0, context + ": expected no chord, got `" + chord.label + "`");
}

void expect_no_drums(Runner &runner, const mao::AnalysisSnapshot &snapshot, const std::string &context)
{
	for (const mao::DrumState &drum : snapshot.drums) {
		runner.expect(!drum.active, context + ": expected " + drum.label + " inactive, level " +
					   std::to_string(drum.level));
	}
}

bool has_chord_label(const char *actual, const std::string &expected)
{
	if (!actual)
		return false;

	const char *cursor = actual;
	while (*cursor) {
		const char *end = cursor;
		while (*end && *end != '=')
			++end;
		if (static_cast<std::size_t>(end - cursor) == expected.size() &&
		    std::strncmp(cursor, expected.c_str(), expected.size()) == 0)
			return true;
		cursor = *end == '=' ? end + 1 : end;
	}

	return false;
}

void add_harmonic_note(mao_test::Buffer &buffer, int midi, float amp, const std::vector<float> &profile)
{
	const float base = mao_test::midi_frequency(midi);
	for (std::size_t harmonic = 0; harmonic < profile.size(); ++harmonic)
		mao_test::add_sine(buffer, base * static_cast<float>(harmonic + 1), amp * profile[harmonic]);
}

void add_decayed_sine(mao_test::Buffer &buffer, float freq, float amp, std::size_t samples = 900)
{
	samples = std::min(samples, buffer.size());
	for (std::size_t i = 0; i < samples; ++i) {
		const float decay = 1.0f - static_cast<float>(i) / static_cast<float>(samples);
		buffer[i] += amp * decay *
			     std::sin(2.0f * mao_test::kPi * freq * static_cast<float>(i) /
				      mao_test::kSampleRate);
	}
}

float detuned_midi_frequency(int midi, float cents)
{
	return mao_test::midi_frequency(midi) * std::pow(2.0f, cents / 1200.0f);
}

mao_test::Buffer make_harmonic_notes(const std::vector<int> &midis, float amp, const std::vector<float> &profile)
{
	mao_test::Buffer buffer = {};
	for (int midi : midis)
		add_harmonic_note(buffer, midi, amp, profile);
	return buffer;
}

bool grid_pitch_active(const mao::NoteGrid &grid, int pitch_class)
{
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return true;
	}
	return false;
}

bool grid_pitch_has_octave(const mao::NoteGrid &grid, int pitch_class, const char *octave)
{
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active && std::strcmp(row[pitch_class].label, octave) == 0)
			return true;
	}
	return false;
}

float grid_level_for_midi(const mao::NoteGrid &grid, int midi)
{
	float level = 0.0f;
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active && cell.midi == midi)
				level = std::max(level, cell.level);
		}
	}
	return level;
}

void check_bass_notes(Runner &runner)
{
	for (int midi = 23; midi <= 67; ++midi) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, midi, 0.70f);
		const auto snapshot = analyze_buffer(buffer, "bass");
		expect_label(runner, snapshot.bass.label, mao_test::note_label(midi),
			     "bass note " + mao_test::note_label(midi));
	}
}

void check_vocal_notes(Runner &runner)
{
	for (int midi = 40; midi <= 84; ++midi) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, midi, 0.48f);
		const auto snapshot = analyze_buffer(buffer, "vocal");
		expect_label(runner, snapshot.vocal.label, mao_test::note_label(midi),
			     "vocal note " + mao_test::note_label(midi));
	}
}

struct HarmonicInstrument {
	const char *name = "";
	int min_midi = 60;
	int max_midi = 88;
	int chord_base_midi = 60;
	const mao::InstrumentState &(*notes)(const mao::AnalysisSnapshot &) = nullptr;
	const mao::InstrumentState &(*chord)(const mao::AnalysisSnapshot &) = nullptr;
};

const mao::InstrumentState &guitar_notes(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.guitar;
}

const mao::InstrumentState &guitar_chord(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.guitar_chord;
}

const mao::InstrumentState &keyboard_notes(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.keyboard;
}

const mao::InstrumentState &keyboard_chord(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.keyboard_chord;
}

const mao::InstrumentState &other_notes(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.other;
}

const mao::InstrumentState &other_chord(const mao::AnalysisSnapshot &snapshot)
{
	return snapshot.other_chord;
}

const std::vector<HarmonicInstrument> &harmonic_instruments()
{
	static const std::vector<HarmonicInstrument> kInstruments = {
		{"guitar", 40, 88, 60, guitar_notes, guitar_chord},
		{"keyboard", 21, 108, 60, keyboard_notes, keyboard_chord},
		{"other", 21, 108, 72, other_notes, other_chord},
	};
	return kInstruments;
}

int root_for_template(const HarmonicInstrument &instrument, int pitch_class, int max_interval)
{
	int root = instrument.chord_base_midi + pitch_class;
	while (root + max_interval > instrument.max_midi)
		root -= 12;
	while (root < instrument.min_midi)
		root += 12;
	return root;
}

void check_harmonic_single_notes(Runner &runner)
{
	for (const HarmonicInstrument &instrument : harmonic_instruments()) {
		for (int midi = instrument.min_midi; midi <= instrument.max_midi; ++midi) {
			mao_test::Buffer buffer = {};
			mao_test::add_midi_note(buffer, midi, 0.46f);
			const auto snapshot = analyze_buffer(buffer, instrument.name);
			const std::string context = std::string(instrument.name) + " single " + mao_test::note_label(midi);

			const std::string expected_note = mao_test::note_label(midi);
			expect_note_token(runner, instrument.notes(snapshot).label, expected_note.c_str(), context);
			runner.expect(!mao_test::contains(instrument.notes(snapshot).label, "MAJ") &&
					      !mao_test::contains(instrument.notes(snapshot).label, "MIN"),
				      context + ": notes field contains chord text `" + instrument.notes(snapshot).label + "`");
			expect_no_chord(runner, instrument.chord(snapshot), context);
		}
	}
}

void check_harmonic_chords(Runner &runner)
{
	for (const HarmonicInstrument &instrument : harmonic_instruments()) {
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			for (bool major : {true, false}) {
				const int root = root_for_template(instrument, pitch_class, 7);
				const int third = root + (major ? 4 : 3);
				const int fifth = root + 7;
				const auto buffer = mao_test::make_midi_notes({root, third, fifth}, 0.34f);
				const auto snapshot = analyze_buffer(buffer, instrument.name);
				const std::string expected_chord =
					std::string(mao_test::note_name(root)) + (major ? "" : "m");
				const std::string context = std::string(instrument.name) + " chord " + expected_chord;

				const std::string root_note = mao_test::note_label(root);
				const std::string third_note = mao_test::note_label(third);
				const std::string fifth_note = mao_test::note_label(fifth);
				expect_note_token(runner, instrument.notes(snapshot).label, root_note.c_str(), context);
				expect_note_token(runner, instrument.notes(snapshot).label, third_note.c_str(), context);
				expect_note_token(runner, instrument.notes(snapshot).label, fifth_note.c_str(), context);
				expect_label(runner, instrument.chord(snapshot).label, expected_chord, context);
			}
		}
	}
}

struct ChordTemplate {
	const char *suffix = "";
	std::vector<int> intervals;
};

void check_extended_chords(Runner &runner)
{
	const std::vector<ChordTemplate> templates = {
		{"pow", {0, 7}},
		{"sus2", {0, 2, 7}},
		{"sus4", {0, 5, 7}},
		{"dim", {0, 3, 6}},
		{"aug", {0, 4, 8}},
		{"7", {0, 4, 7, 10}},
		{"maj7", {0, 4, 7, 11}},
		{"m7", {0, 3, 7, 10}},
		{"dim7", {0, 3, 6, 9}},
		{"m7b5", {0, 3, 6, 10}},
		{"6", {0, 4, 7, 9}},
		{"m6", {0, 3, 7, 9}},
		{"add9", {0, 2, 4, 7}},
		{"9", {0, 2, 4, 7, 10}},
		{"maj9", {0, 2, 4, 7, 11}},
		{"m9", {0, 2, 3, 7, 10}},
	};

	for (const HarmonicInstrument &instrument : harmonic_instruments()) {
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			for (const ChordTemplate &chord_template : templates) {
				const int max_interval = chord_template.intervals.back();
				const int root = root_for_template(instrument, pitch_class, max_interval);
				std::vector<int> midis;
				for (int interval : chord_template.intervals)
					midis.push_back(root + interval);

				const auto buffer = mao_test::make_midi_notes(midis, 0.31f);
				const auto snapshot = analyze_buffer(buffer, instrument.name);
				const std::string expected_chord =
					std::string(mao_test::note_name(root)) + chord_template.suffix;
				const std::string context = std::string(instrument.name) + " chord " + expected_chord;

				for (int midi : midis) {
					const std::string expected_note = mao_test::note_label(midi);
					expect_note_token(runner, instrument.notes(snapshot).label, expected_note.c_str(),
							  context);
				}
				runner.expect(has_chord_label(instrument.chord(snapshot).label, expected_chord),
					      context + ": expected chord label `" + expected_chord + "`, got `" +
						      instrument.chord(snapshot).label + "`");
			}
		}
	}
}

void check_equivalent_chord_labels(Runner &runner)
{
	{
		const auto snapshot = analyze_buffer(mao_test::make_midi_notes({60, 62, 67}, 0.31f), "keyboard");
		const std::string context = "equivalent chord labels Csus2 Gsus4";
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "Csus2"),
			      context + ": expected Csus2, got `" + snapshot.keyboard_chord.label + "`");
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "Gsus4"),
			      context + ": expected Gsus4, got `" + snapshot.keyboard_chord.label + "`");
		runner.expect(mao_test::contains(snapshot.keyboard_chord.label, "="),
			      context + ": expected multiple labels, got `" + snapshot.keyboard_chord.label + "`");
	}

	{
		const auto snapshot = analyze_buffer(mao_test::make_midi_notes({62, 67, 69}, 0.31f), "keyboard");
		const std::string context = "equivalent chord labels Dsus4 Gsus2";
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "Dsus4"),
			      context + ": expected Dsus4, got `" + snapshot.keyboard_chord.label + "`");
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "Gsus2"),
			      context + ": expected Gsus2, got `" + snapshot.keyboard_chord.label + "`");
		runner.expect(mao_test::contains(snapshot.keyboard_chord.label, "="),
			      context + ": expected multiple labels, got `" + snapshot.keyboard_chord.label + "`");
	}
}

void check_quiet_note_rejection(Runner &runner)
{
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 60, 0.34f);
	mao_test::add_midi_note(buffer, 64, 0.34f);
	mao_test::add_midi_note(buffer, 67, 0.34f);
	mao_test::add_midi_note(buffer, 66, 0.12f);

	const auto snapshot = analyze_buffer(buffer, "keyboard");
	runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "F#4"),
		      std::string("quiet note rejection: expected no F#4 token, got `") + snapshot.keyboard.label + "`");
	runner.expect(!snapshot.keyboard_notes.cells[6].active,
		      "quiet note rejection: expected F# cell inactive for low-velocity note");
	expect_label(runner, snapshot.keyboard_chord.label, "C", "quiet note rejection chord");
}

void check_quiet_standalone_rejection(Runner &runner)
{
	struct QuietCase {
		const char *name;
		int midi;
		const mao::InstrumentState &(*notes)(const mao::AnalysisSnapshot &);
		const mao::InstrumentState &(*chord)(const mao::AnalysisSnapshot &);
	};

	const std::vector<QuietCase> cases = {
		{"bass", 40, [](const mao::AnalysisSnapshot &snapshot) -> const mao::InstrumentState & {
			 return snapshot.bass;
		 }, nullptr},
		{"keyboard", 60, keyboard_notes, keyboard_chord},
		{"guitar", 52, guitar_notes, guitar_chord},
		{"vocal", 60, [](const mao::AnalysisSnapshot &snapshot) -> const mao::InstrumentState & {
			 return snapshot.vocal;
		 }, nullptr},
		{"other", 72, other_notes, other_chord},
	};

	for (const QuietCase &quiet_case : cases) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, quiet_case.midi, 0.015f);
		const auto snapshot = analyze_buffer(buffer, quiet_case.name);
		const std::string context = std::string("quiet standalone ") + quiet_case.name;
		expect_label(runner, quiet_case.notes(snapshot).label, "--", context);
		if (quiet_case.chord)
			expect_no_chord(runner, quiet_case.chord(snapshot), context);
	}
}

void check_note_level_fade(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 60, 0.34f);
		mao_test::add_midi_note(buffer, 64, 0.20f);
		mao_test::add_midi_note(buffer, 67, 0.34f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		const float c_level = grid_level_for_midi(snapshot.keyboard_notes, 60);
		const float e_level = grid_level_for_midi(snapshot.keyboard_notes, 64);
		const float g_level = grid_level_for_midi(snapshot.keyboard_notes, 67);
		runner.expect(c_level > 0.90f && g_level > 0.90f,
			      "note level fade: expected strong chord tones near full level");
		runner.expect(e_level > 0.20f && e_level < c_level * 0.80f,
			      "note level fade: expected lower velocity E4 to remain detected but faded");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 60, 0.035f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		const float c_level = grid_level_for_midi(snapshot.keyboard_notes, 60);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "quiet sustained keyboard note");
		runner.expect(c_level > 0.0f && c_level < 0.45f,
			      "note level fade: expected quiet sustained C4 to be visible but not full level");
	}
}

void check_sustained_note_envelope(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.25f;

	mao_test::Buffer g_chord = {};
	mao_test::add_midi_note(g_chord, 55, 0.34f);
	mao_test::add_midi_note(g_chord, 59, 0.34f);
	mao_test::add_midi_note(g_chord, 62, 0.34f);
	auto snapshot = engine.analyze(g_chord.data(), g_chord.size(), settings, "guitar", 0);
	const float initial_g = grid_level_for_midi(snapshot.guitar_notes, 55);
	runner.expect(initial_g > 0.90f, "sustained note envelope: expected initial G3 near full level");
	expect_note_token(runner, snapshot.guitar.label, "G3", "sustained note envelope initial");
	expect_note_token(runner, snapshot.guitar.label, "B3", "sustained note envelope initial");
	expect_note_token(runner, snapshot.guitar.label, "D4", "sustained note envelope initial");
	expect_label(runner, snapshot.guitar_chord.label, "G", "sustained note envelope initial chord");

	mao_test::Buffer missed_window = {};
	snapshot = engine.analyze(missed_window.data(), missed_window.size(), settings, "guitar", 0);
	const float held_g = grid_level_for_midi(snapshot.guitar_notes, 55);
	runner.expect(held_g > 0.75f && held_g < initial_g,
		      "sustained note envelope: expected missed frame to dim G3 instead of clearing it");
	expect_note_token(runner, snapshot.guitar.label, "G3", "sustained note envelope missed frame");
	expect_note_token(runner, snapshot.guitar.label, "B3", "sustained note envelope missed frame");
	expect_note_token(runner, snapshot.guitar.label, "D4", "sustained note envelope missed frame");
	expect_label(runner, snapshot.guitar_chord.label, "G", "sustained note envelope missed frame chord");

	float previous_g = held_g;
	for (int i = 0; i < 4; ++i) {
		snapshot = engine.analyze(missed_window.data(), missed_window.size(), settings, "guitar", 0);
		const float current_g = grid_level_for_midi(snapshot.guitar_notes, 55);
		runner.expect(current_g <= previous_g + 0.001f,
			      "sustained note envelope: expected G3 release to be monotonic");
		previous_g = current_g;
	}
	runner.expect(previous_g > 0.40f, "sustained note envelope: expected G3 visible through short gaps");

	for (int i = 0; i < 12; ++i)
		snapshot = engine.analyze(missed_window.data(), missed_window.size(), settings, "guitar", 0);
	expect_label(runner, snapshot.guitar.label, "--", "sustained note envelope release");
	expect_no_chord(runner, snapshot.guitar_chord, "sustained note envelope release chord");
}

void check_low_level_mixed_notes(Runner &runner)
{
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 60, 0.016f);
	mao_test::add_midi_note(buffer, 64, 0.016f);
	mao_test::add_midi_note(buffer, 67, 0.016f);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	const float c_level = grid_level_for_midi(snapshot.keyboard_notes, 60);
	const float e_level = grid_level_for_midi(snapshot.keyboard_notes, 64);
	const float g_level = grid_level_for_midi(snapshot.keyboard_notes, 67);
	expect_note_token(runner, snapshot.keyboard.label, "C4", "low-level mixed notes");
	expect_note_token(runner, snapshot.keyboard.label, "E4", "low-level mixed notes");
	expect_note_token(runner, snapshot.keyboard.label, "G4", "low-level mixed notes");
	runner.expect(c_level > 0.0f && c_level < 0.25f,
		      "low-level mixed notes: expected C4 visible but dim");
	runner.expect(e_level > 0.0f && e_level < 0.25f,
		      "low-level mixed notes: expected E4 visible but dim");
	runner.expect(g_level > 0.0f && g_level < 0.25f,
		      "low-level mixed notes: expected G4 visible but dim");
}

void check_melodic_sources_do_not_trigger_drums(Runner &runner)
{
	{
		const auto buffer = mao_test::make_midi_notes({48, 52, 55, 60, 64, 67, 72, 76, 79}, 0.24f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_no_drums(runner, snapshot, "layered keyboard no drums");
	}

	{
		const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
		const auto buffer = make_harmonic_notes({43, 47, 50, 55, 59, 62}, 0.20f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_no_drums(runner, snapshot, "layered guitar no drums");
	}

	{
		const std::vector<float> other_profile = {1.0f, 0.55f, 0.36f, 0.20f, 0.11f};
		const auto buffer = make_harmonic_notes({55, 59, 62, 65, 67, 71, 74, 77}, 0.16f, other_profile);
		const auto snapshot = analyze_buffer(buffer, "synth pad");
		expect_no_drums(runner, snapshot, "layered other no drums");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
		const std::vector<float> guitar_profile = {1.0f, 0.24f, 0.10f};
		add_harmonic_note(buffer, 60, 0.28f, key_profile);
		add_harmonic_note(buffer, 64, 0.28f, key_profile);
		add_harmonic_note(buffer, 67, 0.28f, key_profile);
		add_harmonic_note(buffer, 54, 0.18f, guitar_profile);
		add_harmonic_note(buffer, 58, 0.18f, guitar_profile);
		mao_test::add_midi_note(buffer, 74, 0.12f);
		const auto snapshot = analyze_buffer(buffer, "full mix");
		expect_no_drums(runner, snapshot, "melodic full mix no drums");
	}
}

void check_layered_midi_instrument_voices(Runner &runner)
{
	{
		const auto buffer = mao_test::make_midi_notes({48, 52, 55, 60, 64, 67, 72, 76, 79}, 0.24f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "layered keyboard voices chord");
		for (const char *note : {"C3", "E3", "G3", "C4", "E4", "G4", "C5", "E5", "G5"})
			expect_note_token(runner, snapshot.keyboard.label, note, "layered keyboard voices");
		runner.expect(grid_pitch_has_octave(snapshot.keyboard_notes, 0, "3") &&
				      grid_pitch_has_octave(snapshot.keyboard_notes, 0, "4") &&
				      grid_pitch_has_octave(snapshot.keyboard_notes, 0, "5"),
			      "layered keyboard voices: expected C across three octaves");
	}

	{
		const auto buffer = mao_test::make_midi_notes({55, 59, 62, 67, 71, 74}, 0.26f);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_label(runner, snapshot.guitar_chord.label, "G", "layered guitar voices chord");
		for (const char *note : {"G3", "B3", "D4", "G4", "B4", "D5"})
			expect_note_token(runner, snapshot.guitar.label, note, "layered guitar voices");
		runner.expect(grid_pitch_has_octave(snapshot.guitar_notes, 7, "3") &&
				      grid_pitch_has_octave(snapshot.guitar_notes, 7, "4"),
			      "layered guitar voices: expected G across two octaves");
	}

	{
		const std::vector<float> other_profile = {1.0f, 0.55f, 0.36f, 0.20f, 0.11f};
		const auto buffer = make_harmonic_notes({55, 59, 62, 65, 67, 71, 74, 77}, 0.16f, other_profile);
		const auto snapshot = analyze_buffer(buffer, "synth pad");
		expect_label(runner, snapshot.other_chord.label, "G7", "layered other voices chord");
		for (const char *note : {"G3", "B3", "D4", "F4", "G4", "B4", "D5", "F5"})
			expect_note_token(runner, snapshot.other.label, note, "layered other voices");
	}
}

void check_drum_hit_with_melodic_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	add_decayed_sine(buffer, 65.0f, 0.85f);
	add_harmonic_note(buffer, 60, 0.20f, {1.0f, 0.16f, 0.08f});
	add_harmonic_note(buffer, 64, 0.20f, {1.0f, 0.16f, 0.08f});
	add_harmonic_note(buffer, 67, 0.20f, {1.0f, 0.16f, 0.08f});

	const auto snapshot = analyze_buffer(buffer, "full mix");
	runner.expect(snapshot.drums[mao::Kick].active,
		      "drum hit with melodic mix: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	expect_note_token(runner, snapshot.keyboard.label, "C4", "drum hit with melodic mix");
	expect_note_token(runner, snapshot.keyboard.label, "E4", "drum hit with melodic mix");
	expect_note_token(runner, snapshot.keyboard.label, "G4", "drum hit with melodic mix");
}

void check_detuned_note_tolerance(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, 0.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_note_token(runner, snapshot.keyboard.label, "A4", "detuned note tolerance: exact A440");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "A#4"),
			      std::string("detuned note tolerance: exact A440 should not report A#4, got `") +
				      snapshot.keyboard.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, 9.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_note_token(runner, snapshot.keyboard.label, "A4", "detuned note tolerance: A4 plus 9 cents");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "A#4"),
			      std::string("detuned note tolerance: +9 cents should stay A4 only, got `") +
				      snapshot.keyboard.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, 10.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "A4") &&
				      !mao_test::has_note_token(snapshot.keyboard.label, "A#4"),
			      std::string("detuned note tolerance: +10 cents should be ignored, got `") +
				      snapshot.keyboard.label + "`");
		runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 9) &&
				      !grid_pitch_active(snapshot.keyboard_notes, 10),
			      "detuned note tolerance: +10 cents should not light A or A# keys");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, 20.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "A4") &&
				      !mao_test::has_note_token(snapshot.keyboard.label, "A#4"),
			      std::string("detuned note tolerance: +20 cents should be ignored, got `") +
				      snapshot.keyboard.label + "`");
		runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 9) &&
				      !grid_pitch_active(snapshot.keyboard_notes, 10),
			      "detuned note tolerance: +20 cents should not light A or A# keys");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, 50.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "A4") &&
				      !mao_test::has_note_token(snapshot.keyboard.label, "A#4"),
			      std::string("detuned note tolerance: +50 cents should be ambiguous, got `") +
				      snapshot.keyboard.label + "`");
		runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 9) &&
				      !grid_pitch_active(snapshot.keyboard_notes, 10),
			      "detuned note tolerance: +50 cents should not light A or A# keys");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, -10.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "G#4") &&
				      !mao_test::has_note_token(snapshot.keyboard.label, "A4"),
			      std::string("detuned note tolerance: -10 cents should be ignored, got `") +
				      snapshot.keyboard.label + "`");
		runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 8) &&
				      !grid_pitch_active(snapshot.keyboard_notes, 9),
			      "detuned note tolerance: -10 cents should not light G# or A keys");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_sine(buffer, detuned_midi_frequency(69, -50.0f), 0.42f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "G#4") &&
				      !mao_test::has_note_token(snapshot.keyboard.label, "A4"),
			      std::string("detuned note tolerance: -50 cents should be ambiguous, got `") +
				      snapshot.keyboard.label + "`");
		runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 8) &&
				      !grid_pitch_active(snapshot.keyboard_notes, 9),
			      "detuned note tolerance: -50 cents should not light G# or A keys");
	}
}

void check_realistic_instrument_chords(Runner &runner)
{
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const auto guitar_buffer = make_harmonic_notes({48, 52, 55, 60, 64}, 0.17f, guitar_profile);
	const auto guitar_snapshot = analyze_buffer(guitar_buffer, "guitar");
	expect_label(runner, guitar_snapshot.guitar_chord.label, "C", "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "C3", "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "E3", "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "G3", "realistic guitar C chord");

	const std::vector<float> keyboard_profile = {1.0f, 0.18f, 0.08f};
	const auto keyboard_buffer = make_harmonic_notes({50, 53, 57, 60}, 0.20f, keyboard_profile);
	const auto keyboard_snapshot = analyze_buffer(keyboard_buffer, "keyboard");
	runner.expect(has_chord_label(keyboard_snapshot.keyboard_chord.label, "Dm7"),
		      std::string("realistic keyboard Dm7 chord: expected Dm7, got `") +
			      keyboard_snapshot.keyboard_chord.label + "`");
	expect_note_token(runner, keyboard_snapshot.keyboard.label, "D3", "realistic keyboard Dm7 chord");
	expect_note_token(runner, keyboard_snapshot.keyboard.label, "F3", "realistic keyboard Dm7 chord");
	expect_note_token(runner, keyboard_snapshot.keyboard.label, "A3", "realistic keyboard Dm7 chord");
	expect_note_token(runner, keyboard_snapshot.keyboard.label, "C4", "realistic keyboard Dm7 chord");

	const std::vector<float> other_profile = {1.0f, 0.24f, 0.12f, 0.06f};
	const auto other_buffer = make_harmonic_notes({55, 59, 62, 65}, 0.18f, other_profile);
	const auto other_snapshot = analyze_buffer(other_buffer, "other");
	expect_label(runner, other_snapshot.other_chord.label, "G7", "realistic other G7 chord");
	expect_note_token(runner, other_snapshot.other.label, "G3", "realistic other G7 chord");
	expect_note_token(runner, other_snapshot.other.label, "B3", "realistic other G7 chord");
	expect_note_token(runner, other_snapshot.other.label, "D4", "realistic other G7 chord");
	expect_note_token(runner, other_snapshot.other.label, "F4", "realistic other G7 chord");
}

void check_same_note_timbre_split(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
	const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	add_harmonic_note(buffer, 60, 0.28f, piano_profile);
	add_harmonic_note(buffer, 60, 0.22f, guitar_profile);
	add_harmonic_note(buffer, 60, 0.18f, other_profile);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_note_token(runner, snapshot.keyboard.label, "C4", "same-note timbre split keyboard");
	expect_note_token(runner, snapshot.guitar.label, "C4", "same-note timbre split guitar");
	expect_note_token(runner, snapshot.other.label, "C4", "same-note timbre split other");
	runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 60) > 0.0f,
		      "same-note timbre split: expected C4 in keyboard grid");
	runner.expect(grid_level_for_midi(snapshot.guitar_notes, 60) > 0.0f,
		      "same-note timbre split: expected C4 in guitar grid");
	runner.expect(grid_level_for_midi(snapshot.other_notes, 60) > 0.0f,
		      "same-note timbre split: expected C4 in other grid");
}

void check_other_source_hints(Runner &runner)
{
	for (const char *source : {"synth lead", "brass section", "violin bus"}) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 60, 0.42f);
		const auto snapshot = analyze_buffer(buffer, source);
		const std::string context = std::string("other source hint ") + source;
		expect_note_token(runner, snapshot.other.label, "C4", context);
		expect_label(runner, snapshot.keyboard.label, "--", context + " keyboard");
		expect_label(runner, snapshot.guitar.label, "--", context + " guitar");
	}
}

void check_note_sub_rows(Runner &runner)
{
	const auto buffer = mao_test::make_midi_notes({48, 60, 64, 67}, 0.32f);
	const auto snapshot = analyze_buffer(buffer, "keyboard");
	runner.expect(grid_pitch_has_octave(snapshot.keyboard_notes, 0, "3"),
		      "note sub rows: expected keyboard C column to contain octave 3");
	runner.expect(grid_pitch_has_octave(snapshot.keyboard_notes, 0, "4"),
		      "note sub rows: expected keyboard C column to contain octave 4");
}

void check_bass_priority_suppresses_overlap(Runner &runner)
{
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 40, 0.70f);
	const auto snapshot = analyze_buffer(buffer, "mix");
	expect_label(runner, snapshot.bass.label, "E2", "bass priority");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 4),
		      std::string("bass priority: expected keyboard E column inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 4),
		      std::string("bass priority: expected guitar E column inactive, got `") + snapshot.guitar.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.vocal_notes, 4),
		      std::string("bass priority: expected vocal E column inactive, got `") + snapshot.vocal.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.other_notes, 4),
		      std::string("bass priority: expected other E column inactive, got `") + snapshot.other.label +
			      "`");
}

void check_multi_instrument_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.24f, 0.10f};

	add_harmonic_note(buffer, 35, 0.52f, bass_profile);
	add_harmonic_note(buffer, 60, 0.34f, key_profile);
	add_harmonic_note(buffer, 64, 0.34f, key_profile);
	add_harmonic_note(buffer, 67, 0.34f, key_profile);
	add_harmonic_note(buffer, 54, 0.20f, guitar_profile);
	add_harmonic_note(buffer, 58, 0.20f, guitar_profile);
	mao_test::add_midi_note(buffer, 74, 0.15f);
	mao_test::add_midi_note(buffer, 80, 0.13f);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_label(runner, snapshot.bass.label, "B1", "multi-instrument mix bass");

	expect_label(runner, snapshot.keyboard_chord.label, "C", "multi-instrument mix keyboard chord");
	expect_note_token(runner, snapshot.keyboard.label, "C4", "multi-instrument mix keyboard");
	expect_note_token(runner, snapshot.keyboard.label, "E4", "multi-instrument mix keyboard");
	expect_note_token(runner, snapshot.keyboard.label, "G4", "multi-instrument mix keyboard");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 6),
		      std::string("multi-instrument mix: expected keyboard F# inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 10),
		      std::string("multi-instrument mix: expected keyboard A# inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 2),
		      std::string("multi-instrument mix: expected keyboard D inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 8),
		      std::string("multi-instrument mix: expected keyboard G# inactive, got `") +
			      snapshot.keyboard.label + "`");

	expect_note_token(runner, snapshot.guitar.label, "F#3", "multi-instrument mix guitar");
	expect_note_token(runner, snapshot.guitar.label, "A#3", "multi-instrument mix guitar");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 0),
		      std::string("multi-instrument mix: expected guitar C inactive, got `") + snapshot.guitar.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 4),
		      std::string("multi-instrument mix: expected guitar E inactive, got `") + snapshot.guitar.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 7),
		      std::string("multi-instrument mix: expected guitar G inactive, got `") + snapshot.guitar.label +
			      "`");

	expect_label(runner, snapshot.vocal.label, "D5", "multi-instrument mix vocal");
	expect_note_token(runner, snapshot.other.label, "G#5", "multi-instrument mix other");
}

void check_dense_multi_instrument_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.24f, 0.10f};

	add_harmonic_note(buffer, 37, 0.50f, bass_profile);
	add_harmonic_note(buffer, 62, 0.32f, key_profile);
	add_harmonic_note(buffer, 66, 0.32f, key_profile);
	add_harmonic_note(buffer, 69, 0.32f, key_profile);
	add_harmonic_note(buffer, 56, 0.20f, guitar_profile);
	add_harmonic_note(buffer, 60, 0.20f, guitar_profile);
	add_harmonic_note(buffer, 63, 0.20f, guitar_profile);
	mao_test::add_midi_note(buffer, 76, 0.15f);
	mao_test::add_midi_note(buffer, 82, 0.13f);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_label(runner, snapshot.bass.label, "C#2", "dense multi-instrument mix bass");
	expect_label(runner, snapshot.keyboard_chord.label, "D", "dense multi-instrument mix keyboard chord");
	expect_note_token(runner, snapshot.keyboard.label, "D4", "dense multi-instrument mix keyboard");
	expect_note_token(runner, snapshot.keyboard.label, "F#4", "dense multi-instrument mix keyboard");
	expect_note_token(runner, snapshot.keyboard.label, "A4", "dense multi-instrument mix keyboard");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 8),
		      std::string("dense multi-instrument mix: expected keyboard G# inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 0),
		      std::string("dense multi-instrument mix: expected keyboard C inactive, got `") +
			      snapshot.keyboard.label + "`");

	expect_note_token(runner, snapshot.guitar.label, "G#3", "dense multi-instrument mix guitar");
	expect_note_token(runner, snapshot.guitar.label, "C4", "dense multi-instrument mix guitar");
	expect_note_token(runner, snapshot.guitar.label, "D#4", "dense multi-instrument mix guitar");
	expect_label(runner, snapshot.vocal.label, "E5", "dense multi-instrument mix vocal");
	expect_note_token(runner, snapshot.other.label, "A#5", "dense multi-instrument mix other");
}

void check_root_candidates(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();

	auto a_buffer = mao_test::make_midi_notes({45}, 0.70f);
	auto c_buffer = mao_test::make_midi_notes({60, 64, 67}, 0.34f);

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 12; ++i)
		snapshot = engine.analyze(a_buffer.data(), a_buffer.size(), settings, "root", 0);
	for (int i = 0; i < 24; ++i)
		snapshot = engine.analyze(c_buffer.data(), c_buffer.size(), settings, "root", 0);

	runner.expect(std::strcmp(snapshot.root.label, "A") == 0,
		      std::string("root candidates: expected locked root A before full window, got `") +
			      snapshot.root.label + "`");
	runner.expect(mao_test::contains(snapshot.root_candidates, "C "),
		      std::string("root candidates: expected C candidate, got `") + snapshot.root_candidates + "`");

	for (int i = 0; i < 96; ++i)
		snapshot = engine.analyze(c_buffer.data(), c_buffer.size(), settings, "root", 0);

	runner.expect(std::strcmp(snapshot.root.label, "C") == 0,
		      std::string("root candidates: expected locked root C after sustained change, got `") +
			      snapshot.root.label + "`");
	runner.expect(mao_test::contains(snapshot.root_candidates, "C "),
		      std::string("root candidates: expected sustained C candidate, got `") + snapshot.root_candidates +
			      "`");
}

} // namespace

int main()
{
	Runner runner;
	check_bass_notes(runner);
	check_vocal_notes(runner);
	check_harmonic_single_notes(runner);
	check_harmonic_chords(runner);
	check_extended_chords(runner);
	check_equivalent_chord_labels(runner);
	check_quiet_note_rejection(runner);
	check_quiet_standalone_rejection(runner);
	check_note_level_fade(runner);
	check_sustained_note_envelope(runner);
	check_low_level_mixed_notes(runner);
	check_melodic_sources_do_not_trigger_drums(runner);
	check_layered_midi_instrument_voices(runner);
	check_drum_hit_with_melodic_mix(runner);
	check_detuned_note_tolerance(runner);
	check_realistic_instrument_chords(runner);
	check_same_note_timbre_split(runner);
	check_other_source_hints(runner);
	check_note_sub_rows(runner);
	check_bass_priority_suppresses_overlap(runner);
	check_multi_instrument_mix(runner);
	check_dense_multi_instrument_mix(runner);
	check_root_candidates(runner);

	if (runner.failures != 0) {
		std::fprintf(stderr, "analyzer_cases: %d/%d checks failed\n", runner.failures, runner.checks);
		return 1;
	}

	std::printf("analyzer_cases: %d checks passed\n", runner.checks);
	return 0;
}
