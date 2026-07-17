#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
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

mao::AnalysisSnapshot analyze_buffer_with_mode(const mao_test::Buffer &buffer, mao::AnalysisInputMode input_mode,
					       const char *source = "cases", int frames = 1)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = input_mode;
	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < std::max(1, frames); ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
	return snapshot;
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

void expect_float_close(Runner &runner, float lhs, float rhs, float tolerance, const std::string &context)
{
	runner.expect(std::fabs(lhs - rhs) <= tolerance,
		      context + ": expected " + std::to_string(lhs) + " close to " + std::to_string(rhs));
}

void expect_instrument_equal(Runner &runner, const mao::InstrumentState &lhs, const mao::InstrumentState &rhs,
			     const std::string &context)
{
	runner.expect(std::strcmp(lhs.label, rhs.label) == 0,
		      context + ": expected labels equal, got `" + lhs.label + "` and `" + rhs.label + "`");
	expect_float_close(runner, lhs.confidence, rhs.confidence, 1.0e-6f, context + " confidence");
}

void expect_note_cell_equal(Runner &runner, const mao::NoteCell &lhs, const mao::NoteCell &rhs,
			    const std::string &context)
{
	runner.expect(lhs.active == rhs.active, context + ": expected active flags equal");
	runner.expect(lhs.midi == rhs.midi,
		      context + ": expected MIDI " + std::to_string(lhs.midi) + " == " + std::to_string(rhs.midi));
	runner.expect(std::strcmp(lhs.label, rhs.label) == 0,
		      context + ": expected labels equal, got `" + lhs.label + "` and `" + rhs.label + "`");
	expect_float_close(runner, lhs.level, rhs.level, 1.0e-6f, context + " level");
}

void expect_note_grid_equal(Runner &runner, const mao::NoteGrid &lhs, const mao::NoteGrid &rhs,
			    const std::string &context)
{
	for (std::size_t pitch = 0; pitch < lhs.cells.size(); ++pitch)
		expect_note_cell_equal(runner, lhs.cells[pitch], rhs.cells[pitch],
				       context + " cell " + std::to_string(pitch));
	for (std::size_t row = 0; row < lhs.rows.size(); ++row) {
		for (std::size_t pitch = 0; pitch < lhs.rows[row].size(); ++pitch) {
			expect_note_cell_equal(runner, lhs.rows[row][pitch], rhs.rows[row][pitch],
					       context + " row " + std::to_string(row) + " pitch " +
						       std::to_string(pitch));
		}
	}
}

void expect_drum_equal(Runner &runner, const mao::DrumState &lhs, const mao::DrumState &rhs,
		       const std::string &context)
{
	runner.expect(lhs.active == rhs.active, context + ": expected active flags equal");
	runner.expect(std::strcmp(lhs.label, rhs.label) == 0,
		      context + ": expected labels equal, got `" + lhs.label + "` and `" + rhs.label + "`");
	expect_float_close(runner, lhs.level, rhs.level, 1.0e-6f, context + " level");
}

void expect_frontend_equivalent_snapshot(Runner &runner, const mao::AnalysisSnapshot &obs,
					 const mao::AnalysisSnapshot &standalone, const std::string &context)
{
	expect_float_close(runner, obs.rms, standalone.rms, 1.0e-6f, context + " rms");
	expect_float_close(runner, obs.peak, standalone.peak, 1.0e-6f, context + " peak");
	expect_float_close(runner, obs.low_energy, standalone.low_energy, 1.0e-6f, context + " low");
	expect_float_close(runner, obs.mid_energy, standalone.mid_energy, 1.0e-6f, context + " mid");
	expect_float_close(runner, obs.high_energy, standalone.high_energy, 1.0e-6f, context + " high");
	expect_float_close(runner, obs.estimated_bpm, standalone.estimated_bpm, 1.0e-6f, context + " bpm");
	expect_float_close(runner, obs.bpm_confidence, standalone.bpm_confidence, 1.0e-6f,
			   context + " bpm confidence");
	for (std::size_t i = 0; i < obs.drums.size(); ++i)
		expect_drum_equal(runner, obs.drums[i], standalone.drums[i], context + " drum " + std::to_string(i));
	expect_instrument_equal(runner, obs.root, standalone.root, context + " root");
	runner.expect(std::strcmp(obs.root_candidates, standalone.root_candidates) == 0,
		      context + ": expected root candidates equal, got `" + obs.root_candidates + "` and `" +
			      standalone.root_candidates + "`");
	expect_instrument_equal(runner, obs.global_chord, standalone.global_chord, context + " global chord");
	expect_note_grid_equal(runner, obs.ambiguous_notes, standalone.ambiguous_notes, context + " ambiguous notes");
	expect_instrument_equal(runner, obs.bass, standalone.bass, context + " bass");
	expect_note_grid_equal(runner, obs.bass_notes, standalone.bass_notes, context + " bass notes");
	expect_instrument_equal(runner, obs.guitar, standalone.guitar, context + " guitar");
	expect_note_grid_equal(runner, obs.guitar_notes, standalone.guitar_notes, context + " guitar notes");
	expect_instrument_equal(runner, obs.guitar_chord, standalone.guitar_chord, context + " guitar chord");
	expect_instrument_equal(runner, obs.keyboard, standalone.keyboard, context + " keyboard");
	expect_note_grid_equal(runner, obs.keyboard_notes, standalone.keyboard_notes, context + " keyboard notes");
	expect_instrument_equal(runner, obs.keyboard_chord, standalone.keyboard_chord, context + " keyboard chord");
	expect_instrument_equal(runner, obs.vocal, standalone.vocal, context + " vocal");
	expect_note_grid_equal(runner, obs.vocal_notes, standalone.vocal_notes, context + " vocal notes");
	expect_instrument_equal(runner, obs.other, standalone.other, context + " other");
	expect_note_grid_equal(runner, obs.other_notes, standalone.other_notes, context + " other notes");
	expect_instrument_equal(runner, obs.other_chord, standalone.other_chord, context + " other chord");
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

void expect_no_chord_label(Runner &runner, const char *actual, const std::string &unexpected,
			   const std::string &context)
{
	runner.expect(!has_chord_label(actual, unexpected),
		      context + ": expected no chord label `" + unexpected + "`, got `" + actual + "`");
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

void add_sine_at_offset(mao_test::Buffer &buffer, float freq, float amp, uint64_t sample_offset)
{
	for (std::size_t i = 0; i < buffer.size(); ++i) {
		const float sample = static_cast<float>(sample_offset + i);
		buffer[i] += amp * std::sin(2.0f * mao_test::kPi * freq * sample / mao_test::kSampleRate);
	}
}

void add_harmonic_note_at_offset(mao_test::Buffer &buffer, int midi, float amp,
				 const std::vector<float> &profile, uint64_t sample_offset)
{
	const float base = mao_test::midi_frequency(midi);
	for (std::size_t harmonic = 0; harmonic < profile.size(); ++harmonic)
		add_sine_at_offset(buffer, base * static_cast<float>(harmonic + 1), amp * profile[harmonic],
				   sample_offset);
}

void add_detuned_harmonic_note_at_offset(mao_test::Buffer &buffer, int midi, float amp,
					 const std::vector<float> &profile, float cents,
					 uint64_t sample_offset)
{
	const float base = mao_test::midi_frequency(midi) * std::pow(2.0f, cents / 1200.0f);
	for (std::size_t harmonic = 0; harmonic < profile.size(); ++harmonic)
		add_sine_at_offset(buffer, base * static_cast<float>(harmonic + 1), amp * profile[harmonic],
				   sample_offset);
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

bool grid_has_any_active(const mao::NoteGrid &grid)
{
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active)
				return true;
		}
	}
	return false;
}

int grid_active_cell_count(const mao::NoteGrid &grid)
{
	int count = 0;
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active)
				++count;
		}
	}
	return count;
}

bool snapshot_global_pitch_active(const mao::AnalysisSnapshot &snapshot, int pitch_class)
{
	return grid_pitch_active(snapshot.bass_notes, pitch_class) ||
	       grid_pitch_active(snapshot.keyboard_notes, pitch_class) ||
	       grid_pitch_active(snapshot.guitar_notes, pitch_class) ||
	       grid_pitch_active(snapshot.vocal_notes, pitch_class) ||
	       grid_pitch_active(snapshot.other_notes, pitch_class) ||
	       grid_pitch_active(snapshot.ambiguous_notes, pitch_class);
}

int full_mix_owned_midi_count(const mao::AnalysisSnapshot &snapshot, int midi)
{
	auto grid_has_midi = [midi](const mao::NoteGrid &grid) {
		for (const auto &row : grid.rows) {
			for (const mao::NoteCell &cell : row) {
				if (cell.active && cell.midi == midi)
					return true;
			}
		}
		return false;
	};

	int count = 0;
	if (grid_has_midi(snapshot.keyboard_notes))
		++count;
	if (grid_has_midi(snapshot.guitar_notes))
		++count;
	if (grid_has_midi(snapshot.vocal_notes))
		++count;
	if (grid_has_midi(snapshot.other_notes))
		++count;
	return count;
}

int full_mix_confident_midi_count(const mao::AnalysisSnapshot &snapshot, int midi)
{
	auto grid_has_midi = [midi](const mao::NoteGrid &grid) {
		for (const auto &row : grid.rows) {
			for (const mao::NoteCell &cell : row) {
				if (cell.active && cell.midi == midi)
					return true;
			}
		}
		return false;
	};

	int count = 0;
	if (grid_has_midi(snapshot.bass_notes))
		++count;
	if (grid_has_midi(snapshot.keyboard_notes))
		++count;
	if (grid_has_midi(snapshot.guitar_notes))
		++count;
	if (grid_has_midi(snapshot.vocal_notes))
		++count;
	if (grid_has_midi(snapshot.other_notes))
		++count;
	return count;
}

void expect_pitch_class(Runner &runner, const mao::NoteGrid &grid, int pitch_class, const std::string &context)
{
	runner.expect(grid_pitch_active(grid, pitch_class),
		      context + ": expected pitch class " + mao_test::note_name(pitch_class) + " active");
}

void expect_global_pitch_class(Runner &runner, const mao::AnalysisSnapshot &snapshot, int pitch_class,
			       const std::string &context)
{
	runner.expect(snapshot_global_pitch_active(snapshot, pitch_class),
		      context + ": expected global pitch class " + mao_test::note_name(pitch_class) +
			      " active");
}

void expect_midi_not_duplicated_across_rows(Runner &runner, const mao::AnalysisSnapshot &snapshot, int midi,
					    const std::string &context)
{
	const int count = full_mix_owned_midi_count(snapshot, midi);
	runner.expect(count <= 1, context + ": expected " + mao_test::note_label(midi) +
				   " in at most one confident row, got " + std::to_string(count));
}

void expect_midi_not_duplicated_across_instruments(Runner &runner, const mao::AnalysisSnapshot &snapshot, int midi,
						   const std::string &context)
{
	const int count = full_mix_confident_midi_count(snapshot, midi);
	runner.expect(count <= 1, context + ": expected " + mao_test::note_label(midi) +
				   " in at most one confident instrument, got " + std::to_string(count));
}

void expect_no_pitch_class(Runner &runner, const mao::NoteGrid &grid, int pitch_class, const std::string &context)
{
	runner.expect(!grid_pitch_active(grid, pitch_class),
		      context + ": expected pitch class " + mao_test::note_name(pitch_class) + " inactive");
}

void expect_empty_note_grid(Runner &runner, const mao::NoteGrid &grid, const std::string &context)
{
	runner.expect(!grid_has_any_active(grid), context + ": expected no active notes");
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

float snapshot_owned_level_for_midi(const mao::AnalysisSnapshot &snapshot, int midi)
{
	float level = grid_level_for_midi(snapshot.bass_notes, midi);
	level = std::max(level, grid_level_for_midi(snapshot.keyboard_notes, midi));
	level = std::max(level, grid_level_for_midi(snapshot.guitar_notes, midi));
	level = std::max(level, grid_level_for_midi(snapshot.vocal_notes, midi));
	level = std::max(level, grid_level_for_midi(snapshot.other_notes, midi));
	return level;
}

void expect_midi_ambiguous_only(Runner &runner, const mao::AnalysisSnapshot &snapshot, int midi,
				const std::string &context)
{
	runner.expect(grid_level_for_midi(snapshot.ambiguous_notes, midi) > 0.0f,
		      context + ": expected " + mao_test::note_label(midi) + " ambiguous, got keyboard `" +
			      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
			      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`");
	runner.expect(full_mix_owned_midi_count(snapshot, midi) == 0,
		      context + ": expected no confident owner for " + mao_test::note_label(midi) + ", got " +
			      std::to_string(full_mix_owned_midi_count(snapshot, midi)) + " owner rows");
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

void check_bass_octave_suppression(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> hollow_bass_profile = {0.22f, 1.0f, 0.25f, 0.10f};
	add_harmonic_note(buffer, 35, 0.34f, hollow_bass_profile);
	const auto snapshot = analyze_buffer(buffer, "bass");
	expect_label(runner, snapshot.bass.label, "B1", "bass octave suppression");
}

void check_full_mix_bass_conservative_switching(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	mao_test::Buffer b1 = {};
	mao_test::Buffer e2 = {};
	add_harmonic_note(b1, 35, 0.18f, bass_profile);
	add_harmonic_note(e2, 40, 0.18f, bass_profile);

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 2; ++i)
		snapshot = engine.analyze(b1.data(), b1.size(), settings, "Mic/Aux", 0);
	expect_label(runner, snapshot.bass.label, "B1", "full-mix bass switching seed");

	snapshot = engine.analyze(e2.data(), e2.size(), settings, "Mic/Aux", 0);
	expect_label(runner, snapshot.bass.label, "B1", "full-mix bass switching one-frame reject");

	snapshot = engine.analyze(e2.data(), e2.size(), settings, "Mic/Aux", 0);
	expect_label(runner, snapshot.bass.label, "E2", "full-mix bass switching confirmed");
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

void check_guitar_supported_extension_aliases(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	for (int midi : {48, 52, 55})
		add_harmonic_note(buffer, midi, 0.24f, guitar_profile);
	add_harmonic_note(buffer, 59, 0.065f, guitar_profile);

	const auto snapshot = analyze_buffer(buffer, "guitar");
	runner.expect(has_chord_label(snapshot.guitar_chord.label, "C"),
		      std::string("guitar supported extension aliases: expected C, got `") +
			      snapshot.guitar_chord.label + "`");
	runner.expect(has_chord_label(snapshot.guitar_chord.label, "Cmaj7"),
		      std::string("guitar supported extension aliases: expected Cmaj7 alias, got `") +
			      snapshot.guitar_chord.label + "`");
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
		mao_test::add_midi_note(buffer, quiet_case.midi, 0.008f);
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
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = mao_test::default_settings();
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 60, 0.035f);
		(void)engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		const float c_level = grid_level_for_midi(snapshot.keyboard_notes, 60);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "quiet sustained keyboard note");
		runner.expect(c_level > 0.0f && c_level < 0.80f,
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
	runner.expect(held_g > 0.55f && held_g < initial_g,
		      "sustained note envelope: expected missed frame to dim G3 instead of clearing it");
	expect_note_token(runner, snapshot.guitar.label, "G3", "sustained note envelope missed frame");
	expect_note_token(runner, snapshot.guitar.label, "B3", "sustained note envelope missed frame");
	expect_note_token(runner, snapshot.guitar.label, "D4", "sustained note envelope missed frame");
	expect_label(runner, snapshot.guitar_chord.label, "G", "sustained note envelope missed frame chord");

	float previous_g = held_g;
	for (int i = 0; i < 2; ++i) {
		snapshot = engine.analyze(missed_window.data(), missed_window.size(), settings, "guitar", 0);
		const float current_g = grid_level_for_midi(snapshot.guitar_notes, 55);
		runner.expect(current_g <= previous_g + 0.001f,
			      "sustained note envelope: expected G3 release to be monotonic");
		previous_g = current_g;
	}
	runner.expect(previous_g <= 0.40f, "sustained note envelope: expected G3 to decay within short release");

	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(missed_window.data(), missed_window.size(), settings, "guitar", 0);
	expect_label(runner, snapshot.guitar.label, "--", "sustained note envelope release");
	expect_no_chord(runner, snapshot.guitar_chord, "sustained note envelope release chord");
}

void check_temporal_note_stability(Runner &runner)
{
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;

	{
		mao::AnalysisEngine engine;
		mao_test::Buffer c = {};
		mao_test::add_midi_note(c, 60, 0.018f);
		auto snapshot = engine.analyze(c.data(), c.size(), settings, "keyboard", 0);
		expect_label(runner, snapshot.keyboard.label, "--", "temporal note one-frame rejection");

		snapshot = engine.analyze(c.data(), c.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "temporal note two-frame confirmation");

		mao_test::Buffer silence = {};
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "temporal note missed-frame grace");

		for (int i = 0; i < 20; ++i)
			snapshot = engine.analyze(silence.data(), silence.size(), settings, "keyboard", 0);
		expect_label(runner, snapshot.keyboard.label, "--", "temporal note short release");
	}

	{
		mao::AnalysisEngine engine;
		mao_test::Buffer tuned = {};
		mao_test::add_midi_note(tuned, 60, 0.20f);
		auto snapshot = engine.analyze(tuned.data(), tuned.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "temporal note tuning seed");

		mao_test::Buffer detuned = {};
		mao_test::add_sine(detuned, detuned_midi_frequency(60, 16.0f), 0.20f);
		snapshot = engine.analyze(detuned.data(), detuned.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "temporal note tuning hysteresis");
	}

	{
		mao::AnalysisEngine engine;
		mao_test::Buffer c = {};
		mao_test::Buffer d = {};
		mao_test::add_midi_note(c, 60, 0.035f);
		mao_test::add_midi_note(d, 62, 0.035f);
		(void)engine.analyze(c.data(), c.size(), settings, "keyboard", 0);
		auto snapshot = engine.analyze(c.data(), c.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "C4", "temporal note replacement seed");

		(void)engine.analyze(d.data(), d.size(), settings, "keyboard", 0);
		snapshot = engine.analyze(d.data(), d.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "D4", "temporal note replacement confirmed");
		for (int i = 0; i < 12; ++i)
			snapshot = engine.analyze(d.data(), d.size(), settings, "keyboard", 0);
		runner.expect(!mao_test::has_note_token(snapshot.keyboard.label, "C4"),
			      std::string("temporal note replacement: expected old C4 released, got `") +
				      snapshot.keyboard.label + "`");
		expect_note_token(runner, snapshot.keyboard.label, "D4", "temporal note replacement final");
	}
}

void check_full_mix_tuning_hysteresis_uses_global_tracking(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	constexpr int kMidi = 69;
	mao_test::Buffer tuned = {};
	mao_test::add_midi_note(tuned, kMidi, 0.28f);
	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 3; ++i)
		snapshot = engine.analyze(tuned.data(), tuned.size(), settings, "full mix", 0);
	runner.expect(snapshot_owned_level_for_midi(snapshot, kMidi) > 0.85f,
		      "full-mix tuning hysteresis: expected strong seeded A4 level, got " +
			      std::to_string(snapshot_owned_level_for_midi(snapshot, kMidi)));

	mao_test::Buffer detuned = {};
	mao_test::add_sine(detuned, detuned_midi_frequency(kMidi, 16.0f), 0.28f);
	{
		mao::AnalysisEngine fresh_engine;
		const mao::AnalysisSnapshot fresh =
			fresh_engine.analyze(detuned.data(), detuned.size(), settings, "full mix", 0);
		runner.expect(snapshot_owned_level_for_midi(fresh, kMidi) < 0.85f,
			      "full-mix tuning hysteresis: fresh detuned A4 should not start at full level, got " +
				      std::to_string(snapshot_owned_level_for_midi(fresh, kMidi)));
	}
	snapshot = engine.analyze(detuned.data(), detuned.size(), settings, "full mix", 0);
	runner.expect(snapshot_owned_level_for_midi(snapshot, kMidi) > 0.85f,
		      "full-mix tuning hysteresis: fresh global evidence should keep detuned A4 strong, got " +
			      std::to_string(snapshot_owned_level_for_midi(snapshot, kMidi)));

	mao_test::Buffer silence = {};
	for (int i = 0; i < 10; ++i)
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "full mix", 0);
	const float faded_visual_level = snapshot_owned_level_for_midi(snapshot, kMidi);
	runner.expect(faded_visual_level > 0.0f && faded_visual_level < 0.85f,
		      "full-mix tuning hysteresis: expected visual fade without fresh global evidence, got " +
			      std::to_string(faded_visual_level));

	snapshot = engine.analyze(detuned.data(), detuned.size(), settings, "full mix", 0);
	runner.expect(snapshot_owned_level_for_midi(snapshot, kMidi) < 0.85f,
		      "full-mix tuning hysteresis: visual row fade must not restore active tuning, got " +
			      std::to_string(snapshot_owned_level_for_midi(snapshot, kMidi)));
}

void check_temporal_chord_stability(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	const auto c_major = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
	const auto c_without_e = mao_test::make_midi_notes({60, 67}, 0.34f);
	const auto c_without_c = mao_test::make_midi_notes({64, 67}, 0.34f);
	const auto g_major = mao_test::make_midi_notes({67, 71, 74}, 0.34f);
	mao_test::Buffer silence = {};

	auto snapshot = engine.analyze(c_major.data(), c_major.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "temporal chord initial C");

	snapshot = engine.analyze(c_without_e.data(), c_without_e.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "temporal chord survives missing E");

	snapshot = engine.analyze(c_without_c.data(), c_without_c.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "temporal chord survives incomplete raw notes");

	snapshot = engine.analyze(c_major.data(), c_major.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "temporal chord no C/-- blinking");

	snapshot = engine.analyze(g_major.data(), g_major.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "temporal chord rejects one-frame replacement");

	snapshot = engine.analyze(g_major.data(), g_major.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "G", "temporal chord switches after confirmation");

	for (int i = 0; i < 20; ++i)
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "keyboard", 0);
	expect_no_chord(runner, snapshot.keyboard_chord, "temporal chord silence clear");
}

void check_full_mix_global_chord_uses_analytical_tracking(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	const auto c_major = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
	const auto c_without_e = mao_test::make_midi_notes({60, 67}, 0.34f);
	mao_test::Buffer silence = {};

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 2; ++i)
		snapshot = engine.analyze(c_major.data(), c_major.size(), settings, "full mix", 0);
	expect_label(runner, snapshot.global_chord.label, "C", "full-mix analytical chord seed");

	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(c_without_e.data(), c_without_e.size(), settings, "full mix", 0);
	expect_label(runner, snapshot.global_chord.label, "C",
		     "full-mix analytical chord survives repeated incomplete raw frames");

	for (int i = 0; i < 14; ++i)
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "full mix", 0);
	expect_no_chord(runner, snapshot.global_chord, "full-mix analytical chord silence clear");
}

mao_test::Buffer make_interval_chord(int root_midi, const std::vector<int> &intervals, float amp = 0.34f)
{
	mao_test::Buffer buffer = {};
	for (int interval : intervals)
		mao_test::add_midi_note(buffer, root_midi + interval, amp);
	return buffer;
}

void expect_chord_label_present(Runner &runner, const char *actual, const std::string &expected,
				const std::string &context)
{
	runner.expect(has_chord_label(actual, expected),
		      context + ": expected chord label `" + expected + "`, got `" + actual + "`");
}

void expect_no_false_transition_labels(Runner &runner, const char *actual, const std::vector<std::string> &forbidden,
				       const std::string &context)
{
	for (const std::string &label : forbidden)
		expect_no_chord_label(runner, actual, label, context);
}

void expect_keyboard_chord_transition(Runner &runner, const std::string &name, const mao_test::Buffer &from,
				      const std::string &from_label, const mao_test::Buffer &to,
				      const std::string &to_label, const std::vector<std::string> &forbidden)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;

	auto snapshot = engine.analyze(from.data(), from.size(), settings, "keyboard", 0);
	expect_chord_label_present(runner, snapshot.keyboard_chord.label, from_label, name + " seed");

	snapshot = engine.analyze(from.data(), from.size(), settings, "keyboard", 0);
	expect_chord_label_present(runner, snapshot.keyboard_chord.label, from_label, name + " stable source");

	snapshot = engine.analyze(to.data(), to.size(), settings, "keyboard", 0);
	expect_chord_label_present(runner, snapshot.keyboard_chord.label, from_label,
				  name + " rejects one-frame replacement");

	snapshot = engine.analyze(to.data(), to.size(), settings, "keyboard", 0);
	expect_chord_label_present(runner, snapshot.keyboard_chord.label, to_label, name + " confirmed target");
	expect_no_false_transition_labels(runner, snapshot.keyboard_chord.label, forbidden, name + " confirmed target");

	snapshot = engine.analyze(to.data(), to.size(), settings, "keyboard", 0);
	expect_chord_label_present(runner, snapshot.keyboard_chord.label, to_label, name + " stable target");
	expect_no_false_transition_labels(runner, snapshot.keyboard_chord.label, forbidden, name + " stable target");
}

void expect_full_mix_global_chord_transition(Runner &runner, const std::string &name, const mao_test::Buffer &from,
					     const std::string &from_label, const mao_test::Buffer &to,
					     const std::string &to_label,
					     const std::vector<std::string> &forbidden)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	auto snapshot = engine.analyze(from.data(), from.size(), settings, "speaker mix", 0);
	(void)snapshot;
	snapshot = engine.analyze(from.data(), from.size(), settings, "speaker mix", 0);
	expect_chord_label_present(runner, snapshot.global_chord.label, from_label, name + " full-mix seed");

	snapshot = engine.analyze(to.data(), to.size(), settings, "speaker mix", 0);
	expect_chord_label_present(runner, snapshot.global_chord.label, from_label,
				  name + " full-mix rejects one-frame replacement");

	snapshot = engine.analyze(to.data(), to.size(), settings, "speaker mix", 0);
	expect_chord_label_present(runner, snapshot.global_chord.label, to_label,
				  name + " full-mix confirmed target");
	expect_no_false_transition_labels(runner, snapshot.global_chord.label, forbidden,
					  name + " full-mix confirmed target");

	snapshot = engine.analyze(to.data(), to.size(), settings, "speaker mix", 0);
	expect_chord_label_present(runner, snapshot.global_chord.label, to_label,
				  name + " full-mix stable target");
	expect_no_false_transition_labels(runner, snapshot.global_chord.label, forbidden,
					  name + " full-mix stable target");
}

void check_required_chord_transitions(Runner &runner)
{
	const auto c = make_interval_chord(60, {0, 4, 7});
	const auto g = make_interval_chord(67, {0, 4, 7});
	const auto am = make_interval_chord(69, {0, 3, 7});
	const auto dm7 = make_interval_chord(62, {0, 3, 7, 10});
	const auto g7 = make_interval_chord(67, {0, 4, 7, 10});
	const auto csus4 = make_interval_chord(60, {0, 5, 7});
	const auto cmaj7 = make_interval_chord(60, {0, 4, 7, 11});
	const auto em = make_interval_chord(64, {0, 3, 7});

	expect_keyboard_chord_transition(runner, "required transition C to G", c, "C", g, "G",
					 {"Cmaj7", "C7", "Cadd9", "C9", "Gadd9", "Gmaj9", "Gaug", "Gdim"});
	expect_keyboard_chord_transition(runner, "required transition C to Am", c, "C", am, "Am",
					 {"C6", "Cmaj7", "C7", "Cadd9", "Am7", "Am9", "Aaug", "Adim"});
	expect_keyboard_chord_transition(runner, "required transition Dm7 to G7", dm7, "Dm7", g7, "G7",
					 {"Dm9", "Ddim", "Daug", "G9", "Gmaj7", "Gdim", "Gaug"});
	expect_keyboard_chord_transition(runner, "required transition Csus4 to C", csus4, "Csus4", c, "C",
					 {"C7", "Cmaj7", "Cadd9", "C9", "Cdim", "Caug"});
	expect_keyboard_chord_transition(runner, "required transition C to Cmaj7", c, "C", cmaj7, "Cmaj7",
					 {"C7", "C9", "Cadd9", "Cdim", "Caug"});
	expect_keyboard_chord_transition(runner, "required transition Cmaj7 to C", cmaj7, "Cmaj7", c, "C",
					 {"Cmaj7", "C7", "C9", "Cadd9", "Cdim", "Caug"});
	expect_keyboard_chord_transition(runner, "required transition G to Em", g, "G", em, "Em",
					 {"G6", "Gmaj7", "G7", "Gadd9", "Em7", "Em9", "Edim", "Eaug"});
}

void check_full_mix_global_chord_transitions(Runner &runner)
{
	const auto c = make_interval_chord(60, {0, 4, 7});
	const auto g = make_interval_chord(67, {0, 4, 7});
	const auto am = make_interval_chord(69, {0, 3, 7});
	const auto dm7 = make_interval_chord(62, {0, 3, 7, 10});
	const auto g7 = make_interval_chord(67, {0, 4, 7, 10});
	const auto csus4 = make_interval_chord(60, {0, 5, 7});
	const auto cmaj7 = make_interval_chord(60, {0, 4, 7, 11});
	const auto em = make_interval_chord(64, {0, 3, 7});

	expect_full_mix_global_chord_transition(runner, "required transition C to G", c, "C", g, "G",
						{"Cmaj7", "C7", "Cadd9", "C9", "Gadd9", "Gmaj9", "Gaug",
						 "Gdim"});
	expect_full_mix_global_chord_transition(runner, "required transition C to Am", c, "C", am, "Am",
						{"C6", "Cmaj7", "C7", "Cadd9", "Am7", "Am9", "Aaug",
						 "Adim"});
	expect_full_mix_global_chord_transition(runner, "required transition Dm7 to G7", dm7, "Dm", g7,
						"G", {"Dm7", "Dm9", "Ddim", "Daug", "G7", "G9",
						      "Gmaj7", "Gdim", "Gaug"});
	expect_full_mix_global_chord_transition(runner, "required transition Csus4 to C", csus4,
						"Csus4", c, "C",
						{"C7", "Cmaj7", "Cadd9", "C9", "Cdim", "Caug"});
	expect_full_mix_global_chord_transition(runner, "required transition C to Cmaj7", c, "C",
						cmaj7, "C", {"Cmaj7", "C7", "C9", "Cadd9", "Cdim", "Caug"});
	expect_full_mix_global_chord_transition(runner, "required transition Cmaj7 to C", cmaj7,
						"C", c, "C",
						{"Cmaj7", "C7", "C9", "Cadd9", "Cdim", "Caug"});
	expect_full_mix_global_chord_transition(runner, "required transition G to Em", g, "G", em, "Em",
						{"G6", "Gmaj7", "G7", "Gadd9", "Em7", "Em9", "Edim",
						 "Eaug"});
}

void check_chord_margin_and_simplification(Runner &runner)
{
	{
		mao_test::Buffer weak_ninth = {};
		mao_test::add_midi_note(weak_ninth, 60, 0.34f);
		mao_test::add_midi_note(weak_ninth, 64, 0.34f);
		mao_test::add_midi_note(weak_ninth, 67, 0.34f);
		mao_test::add_midi_note(weak_ninth, 62, 0.09f);
		const auto snapshot = analyze_buffer(weak_ninth, "keyboard");
		expect_label(runner, snapshot.keyboard_chord.label, "C",
			     "chord simplification: weak ninth keeps simple triad");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "Cadd9",
				      "chord simplification: weak ninth");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "C9",
				      "chord simplification: weak ninth");
	}
}

void check_chord_evidence_separate_from_visual_fade(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	const auto c_major = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
	mao_test::Buffer silence = {};

	(void)engine.analyze(c_major.data(), c_major.size(), settings, "keyboard", 0);
	auto snapshot = engine.analyze(c_major.data(), c_major.size(), settings, "keyboard", 0);
	expect_label(runner, snapshot.keyboard_chord.label, "C", "chord evidence visual separation seed");

	for (int i = 0; i < 12; ++i)
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "keyboard", 0);

	const float visual_c = grid_level_for_midi(snapshot.keyboard_notes, 60);
	runner.expect(visual_c > 0.0f,
		      "chord evidence visual separation: expected visual C4 fade to remain visible");
	expect_no_chord(runner, snapshot.keyboard_chord,
			"chord evidence visual separation: chord should expire before visual notes");
}

void check_low_level_mixed_notes(Runner &runner)
{
	mao::AnalysisEngine engine;
	const mao::AnalysisSettings settings = mao_test::default_settings();
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 60, 0.016f);
	mao_test::add_midi_note(buffer, 64, 0.016f);
	mao_test::add_midi_note(buffer, 67, 0.016f);

	(void)engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);
	const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);
	const float c_level = grid_level_for_midi(snapshot.keyboard_notes, 60);
	const float e_level = grid_level_for_midi(snapshot.keyboard_notes, 64);
	const float g_level = grid_level_for_midi(snapshot.keyboard_notes, 67);
	expect_note_token(runner, snapshot.keyboard.label, "C4", "low-level mixed notes");
	expect_note_token(runner, snapshot.keyboard.label, "E4", "low-level mixed notes");
	expect_note_token(runner, snapshot.keyboard.label, "G4", "low-level mixed notes");
	runner.expect(c_level > 0.0f && c_level < 0.70f,
		      "low-level mixed notes: expected C4 visible but dim");
	runner.expect(e_level > 0.0f && e_level < 0.70f,
		      "low-level mixed notes: expected E4 visible but dim");
	runner.expect(g_level > 0.0f && g_level < 0.70f,
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

void check_same_instrument_timbre_variants(Runner &runner)
{
	{
		const std::vector<std::vector<float>> keyboard_profiles = {
			{1.0f, 0.10f, 0.04f, 0.02f},
			{1.0f, 0.18f, 0.06f, 0.03f},
			{1.0f, 0.24f, 0.08f, 0.04f},
		};
		for (std::size_t i = 0; i < keyboard_profiles.size(); ++i) {
			const auto buffer = make_harmonic_notes({60, 64, 67}, 0.20f, keyboard_profiles[i]);
			const auto snapshot = analyze_buffer(buffer, "keyboard");
			const std::string context = "keyboard timbre variant " + std::to_string(i);
			expect_note_token(runner, snapshot.keyboard.label, "C4", context);
			expect_note_token(runner, snapshot.keyboard.label, "E4", context);
			expect_note_token(runner, snapshot.keyboard.label, "G4", context);
		}
	}

	{
		const std::vector<std::vector<float>> guitar_profiles = {
			{1.0f, 0.28f, 0.12f, 0.05f},
			{1.0f, 0.34f, 0.16f, 0.08f},
			{1.0f, 0.54f, 0.30f, 0.18f, 0.10f},
		};
		for (std::size_t i = 0; i < guitar_profiles.size(); ++i) {
			const auto buffer = make_harmonic_notes({58, 62, 65}, 0.20f, guitar_profiles[i]);
			const auto snapshot = analyze_buffer(buffer, "guitar");
			const std::string context = "guitar timbre variant " + std::to_string(i);
			expect_note_token(runner, snapshot.guitar.label, "D4", context);
			expect_note_token(runner, snapshot.guitar.label, "F4", context);
			expect_no_drums(runner, snapshot, context);
		}
	}

	{
		const std::vector<std::vector<float>> other_profiles = {
			{1.0f, 0.52f, 0.30f, 0.18f, 0.10f},
			{1.0f, 0.62f, 0.42f, 0.27f, 0.16f},
			{1.0f, 0.70f, 0.48f, 0.30f, 0.18f},
		};
		for (std::size_t i = 0; i < other_profiles.size(); ++i) {
			const auto buffer = make_harmonic_notes({60, 64, 67}, 0.18f, other_profiles[i]);
			const auto snapshot = analyze_buffer(buffer, "synth lead");
			const std::string context = "other timbre variant " + std::to_string(i);
			expect_note_token(runner, snapshot.other.label, "C4", context);
			expect_note_token(runner, snapshot.other.label, "E4", context);
			expect_note_token(runner, snapshot.other.label, "G4", context);
		}
	}
}

void check_distorted_midi_guitar_timbre(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> distorted_guitar_profile = {1.0f, 0.54f, 0.30f, 0.18f, 0.10f};

	add_harmonic_note(buffer, 55, 0.22f, distorted_guitar_profile);
	add_harmonic_note(buffer, 59, 0.22f, distorted_guitar_profile);
	add_harmonic_note(buffer, 62, 0.22f, distorted_guitar_profile);

	const auto snapshot = analyze_buffer(buffer, "distorted guitar");
	expect_note_token(runner, snapshot.guitar.label, "G3", "distorted MIDI guitar timbre");
	expect_note_token(runner, snapshot.guitar.label, "B3", "distorted MIDI guitar timbre");
	expect_note_token(runner, snapshot.guitar.label, "D4", "distorted MIDI guitar timbre");
	expect_label(runner, snapshot.guitar_chord.label, "G", "distorted MIDI guitar timbre chord");
	expect_no_pitch_class(runner, snapshot.keyboard_notes, 7, "distorted MIDI guitar timbre keyboard spillover");
	expect_no_drums(runner, snapshot, "distorted MIDI guitar timbre");
}

void check_spillover_regressions(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.14f, 0.05f, 0.02f};
		for (int midi : {60, 64, 67})
			add_harmonic_note(buffer, midi, 0.24f, piano_profile);

		const auto snapshot = analyze_buffer(buffer, "piano");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "spillover piano-only keyboard chord");
		for (int pitch_class : {0, 4, 7}) {
			expect_pitch_class(runner, snapshot.keyboard_notes, pitch_class, "spillover piano-only keyboard");
			expect_no_pitch_class(runner, snapshot.guitar_notes, pitch_class, "spillover piano-only guitar");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class, "spillover piano-only vocal");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class, "spillover piano-only other");
		}
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
		for (int midi : {55, 59, 62})
			add_harmonic_note(buffer, midi, 0.24f, guitar_profile);

		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_label(runner, snapshot.guitar_chord.label, "G", "spillover guitar-only guitar chord");
		for (int pitch_class : {7, 11, 2}) {
			expect_pitch_class(runner, snapshot.guitar_notes, pitch_class, "spillover guitar-only guitar");
			expect_no_pitch_class(runner, snapshot.keyboard_notes, pitch_class, "spillover guitar-only keyboard");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class, "spillover guitar-only vocal");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class, "spillover guitar-only other");
		}
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.015f};
		for (int midi : {84, 88, 91})
			add_harmonic_note(buffer, midi, 0.22f, piano_profile);

		const auto snapshot = analyze_buffer(buffer, "piano");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "spillover high piano keyboard chord");
		for (int pitch_class : {0, 4, 7}) {
			expect_pitch_class(runner, snapshot.keyboard_notes, pitch_class, "spillover high piano keyboard");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class, "spillover high piano vocal");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class, "spillover high piano other");
		}
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> keyboard_profile = {1.0f, 0.16f, 0.08f};
		const std::vector<float> bass_profile = {1.0f, 0.28f, 0.12f};
		for (int midi : {60, 64, 67})
			add_harmonic_note(buffer, midi, 0.28f, keyboard_profile);
		add_harmonic_note(buffer, 31, 0.035f, bass_profile);

		const auto snapshot = analyze_buffer(buffer, "full mix");
		expect_label(runner, snapshot.bass.label, "--", "spillover weak bass root bass candidate");
		expect_label(runner, snapshot.global_chord.label, "C", "spillover weak bass root global chord");
		expect_no_chord_label(runner, snapshot.global_chord.label, "G", "spillover weak bass root global chord");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.analysis_interval_seconds = 0.05f;
		const std::vector<float> keyboard_profile = {1.0f, 0.16f, 0.08f};
		mao_test::Buffer c = {};
		mao_test::Buffer g = {};
		for (int midi : {60, 64, 67})
			add_harmonic_note(c, midi, 0.24f, keyboard_profile);
		for (int midi : {55, 59, 62})
			add_harmonic_note(g, midi, 0.24f, keyboard_profile);

		mao::AnalysisSnapshot snapshot = {};
		for (int i = 0; i < 3; ++i)
			snapshot = engine.analyze(c.data(), c.size(), settings, "piano", 0);
		for (int i = 0; i < 3; ++i)
			snapshot = engine.analyze(g.data(), g.size(), settings, "piano", 0);

		expect_label(runner, snapshot.keyboard_chord.label, "G", "spillover chord transition keyboard chord");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "Cmaj7",
				      "spillover chord transition false extension");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "C7",
				      "spillover chord transition false extension");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "Cadd9",
				      "spillover chord transition false extension");
	}
}

void check_high_full_mix_cluster_not_vocal_or_other(Runner &runner)
{
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.015f};
	{
		mao_test::Buffer buffer = {};
		for (int midi : {76, 79, 83})
			add_harmonic_note(buffer, midi, 0.22f, piano_profile);

		const auto snapshot = analyze_buffer(buffer, "full mix");
		for (int pitch_class : {4, 7, 11}) {
			expect_global_pitch_class(runner, snapshot, pitch_class, "high full-mix cluster global");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class, "high full-mix cluster vocal");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class, "high full-mix cluster other");
			runner.expect(grid_pitch_active(snapshot.keyboard_notes, pitch_class) ||
					      grid_pitch_active(snapshot.ambiguous_notes, pitch_class),
				      "high full-mix cluster: expected keyboard or ambiguous evidence");
		}
	}
	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 84, 0.24f, piano_profile);
		const auto snapshot = analyze_buffer(buffer, "full mix");
		expect_global_pitch_class(runner, snapshot, 0, "single high piano global");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 0, "single high piano vocal");
		expect_no_pitch_class(runner, snapshot.other_notes, 0, "single high piano other");
	}
}

void check_full_mix_single_instrument_precision(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.015f};
		for (int midi : {60, 64, 67})
			add_harmonic_note(buffer, midi, 0.24f, piano_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker piano-only", 3);
		expect_label(runner, snapshot.global_chord.label, "C", "full-mix piano-only global chord");
		for (int midi : {60, 64, 67}) {
			const int pitch_class = ((midi % 12) + 12) % 12;
			expect_global_pitch_class(runner, snapshot, pitch_class, "full-mix piano-only global");
			expect_pitch_class(runner, snapshot.keyboard_notes, pitch_class,
					   "full-mix piano-only keyboard ownership");
			expect_midi_not_duplicated_across_rows(runner, snapshot, midi,
							       "full-mix piano-only ownership");
			expect_no_pitch_class(runner, snapshot.guitar_notes, pitch_class,
					      "full-mix piano-only guitar spillover");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class,
					      "full-mix piano-only vocal spillover");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class,
					      "full-mix piano-only other spillover");
		}
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
		for (int midi : {55, 59, 62})
			add_harmonic_note(buffer, midi, 0.24f, guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker guitar-only", 3);
		expect_label(runner, snapshot.global_chord.label, "G", "full-mix guitar-only global chord");
		runner.expect(grid_active_cell_count(snapshot.guitar_notes) >= 2,
			      "full-mix guitar-only ownership: expected at least two guitar notes, got " +
				      std::to_string(grid_active_cell_count(snapshot.guitar_notes)) +
				      " label `" + snapshot.guitar.label + "`");
		for (int midi : {55, 59, 62}) {
			const int pitch_class = ((midi % 12) + 12) % 12;
			expect_global_pitch_class(runner, snapshot, pitch_class, "full-mix guitar-only global");
			expect_midi_not_duplicated_across_rows(runner, snapshot, midi,
							       "full-mix guitar-only ownership");
			expect_no_pitch_class(runner, snapshot.keyboard_notes, pitch_class,
					      "full-mix guitar-only keyboard spillover");
			expect_no_pitch_class(runner, snapshot.vocal_notes, pitch_class,
					      "full-mix guitar-only vocal spillover");
			expect_no_pitch_class(runner, snapshot.other_notes, pitch_class,
					      "full-mix guitar-only other spillover");
		}
	}
}

void check_full_mix_single_owned_note_has_no_instrument_chord(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
		add_harmonic_note(buffer, 55, 0.28f, guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "single guitar note", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix single guitar note global");
		expect_midi_not_duplicated_across_rows(runner, snapshot, 55,
						       "full-mix single guitar note ownership");
		expect_no_chord(runner, snapshot.guitar_chord, "full-mix single guitar note chord");
		expect_no_chord(runner, snapshot.keyboard_chord, "full-mix single guitar note keyboard chord");
		expect_no_chord(runner, snapshot.other_chord, "full-mix single guitar note other chord");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};
		add_harmonic_note(buffer, 74, 0.28f, other_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "single other note", 3);
		expect_global_pitch_class(runner, snapshot, 2, "full-mix single other note global");
		expect_midi_not_duplicated_across_rows(runner, snapshot, 74,
						       "full-mix single other note ownership");
		expect_no_chord(runner, snapshot.other_chord, "full-mix single other note chord");
		expect_no_chord(runner, snapshot.guitar_chord, "full-mix single other note guitar chord");
		expect_no_chord(runner, snapshot.keyboard_chord, "full-mix single other note keyboard chord");
	}
}

void check_simultaneous_onset_group_rejects_vocal_spillover(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> piano_profile = {1.0f, 0.14f, 0.05f, 0.02f};
	const std::vector<float> vocal_like_profile = {1.0f, 0.035f, 0.018f, 0.010f};
	for (int midi : {60, 64, 67})
		add_harmonic_note(buffer, midi, 0.22f, piano_profile);
	add_harmonic_note(buffer, 84, 0.24f, vocal_like_profile);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_label(runner, snapshot.global_chord.label, "C", "simultaneous-onset group global chord");
	expect_global_pitch_class(runner, snapshot, 0, "simultaneous-onset group global C");
	expect_no_pitch_class(runner, snapshot.vocal_notes, 0, "simultaneous-onset group vocal spillover");
	runner.expect(grid_pitch_active(snapshot.keyboard_notes, 0) ||
			      grid_pitch_active(snapshot.ambiguous_notes, 0),
		      "simultaneous-onset group: expected C to stay keyboard or ambiguous");
}

void check_full_mix_vocal_requires_temporal_confirmation(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> vocal_like_profile = {1.0f, 0.035f, 0.018f, 0.010f};
	add_harmonic_note(buffer, 84, 0.24f, vocal_like_profile);

	mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_global_pitch_class(runner, snapshot, 0, "full-mix vocal confirmation first-frame global");
	expect_no_pitch_class(runner, snapshot.vocal_notes, 0, "full-mix vocal confirmation first-frame vocal");
	runner.expect(grid_pitch_active(snapshot.ambiguous_notes, 0),
		      "full-mix vocal confirmation: expected first C6 candidate to stay ambiguous");

	snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_pitch_class(runner, snapshot.vocal_notes, 0, "full-mix vocal confirmation second-frame vocal");
	expect_midi_not_duplicated_across_rows(runner, snapshot, 84, "full-mix vocal confirmation ownership");
}

void check_full_mix_midrange_vocal_recall(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> vocal_profile = {1.0f, 0.070f, 0.032f, 0.016f};
	add_harmonic_note(buffer, 64, 0.24f, vocal_profile);

	mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_global_pitch_class(runner, snapshot, 4, "full-mix midrange vocal first-frame global");
	expect_no_pitch_class(runner, snapshot.vocal_notes, 4, "full-mix midrange vocal first-frame vocal");

	snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	runner.expect(grid_pitch_active(snapshot.vocal_notes, 4),
		      std::string("full-mix midrange vocal second-frame vocal: expected E active, got keyboard `") +
			      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
			      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`, ambiguous `" +
			      snapshot.global_chord.label + "`");
	expect_midi_not_duplicated_across_rows(runner, snapshot, 64, "full-mix midrange vocal ownership");
}

void check_full_mix_realistic_vocal_recall(Runner &runner)
{
	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;

		mao_test::Buffer buffer = {};
		const std::vector<float> low_vocal_profile = {1.0f, 0.22f, 0.12f, 0.055f, 0.025f};
		add_harmonic_note(buffer, 53, 0.24f, low_vocal_profile);

		mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		expect_global_pitch_class(runner, snapshot, 5, "full-mix lower vocal first-frame global");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 5, "full-mix lower vocal first-frame vocal");

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		runner.expect(grid_pitch_active(snapshot.vocal_notes, 5),
			      std::string("full-mix lower vocal second-frame vocal: expected F active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
				      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`, global `" +
				      snapshot.global_chord.label + "`, ambiguous " +
				      (grid_pitch_active(snapshot.ambiguous_notes, 5) ? "active" : "inactive"));
		expect_midi_not_duplicated_across_rows(runner, snapshot, 53, "full-mix lower vocal ownership");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;

		mao_test::Buffer buffer = {};
		const std::vector<float> rich_vocal_profile = {1.0f, 0.30f, 0.18f, 0.10f, 0.045f};
		add_harmonic_note(buffer, 64, 0.24f, rich_vocal_profile);

		mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		expect_global_pitch_class(runner, snapshot, 4, "full-mix rich vocal first-frame global");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 4, "full-mix rich vocal first-frame vocal");

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		runner.expect(grid_pitch_active(snapshot.vocal_notes, 4),
			      std::string("full-mix rich vocal second-frame vocal: expected E active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
				      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`, global `" +
				      snapshot.global_chord.label + "`, ambiguous " +
				      (grid_pitch_active(snapshot.ambiguous_notes, 4) ? "active" : "inactive"));
		expect_midi_not_duplicated_across_rows(runner, snapshot, 64, "full-mix rich vocal ownership");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;

		const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
		const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f, 0.03f};
		const std::vector<float> lead_vocal_profile = {1.0f, 0.24f, 0.14f, 0.08f, 0.035f};
		mao::AnalysisSnapshot snapshot = {};
		for (int frame = 0; frame < 3; ++frame) {
			const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
			mao_test::Buffer buffer = {};
			add_harmonic_note_at_offset(buffer, 36, 0.15f, bass_profile, sample_offset);
			for (int midi : {60, 64, 67})
				add_harmonic_note_at_offset(buffer, midi, 0.050f, key_profile, sample_offset);
			add_harmonic_note_at_offset(buffer, 69, 0.24f, lead_vocal_profile, sample_offset);
			snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		}

		runner.expect(grid_pitch_active(snapshot.vocal_notes, 9),
			      std::string("full-mix vocal-over-chord vocal: expected A active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
				      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`, global `" +
				      snapshot.global_chord.label + "`, ambiguous " +
				      (grid_pitch_active(snapshot.ambiguous_notes, 9) ? "active" : "inactive"));
		expect_global_pitch_class(runner, snapshot, 9, "full-mix vocal-over-chord global");
		expect_midi_not_duplicated_across_rows(runner, snapshot, 69, "full-mix vocal-over-chord ownership");
	}
}

void check_mixed_keyboard_guitar_note_bounds(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f, 0.03f};
	const std::vector<float> guitar_profile = {1.0f, 0.54f, 0.30f, 0.18f, 0.10f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 5; ++frame) {
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
		mao_test::Buffer buffer = {};
		add_harmonic_note_at_offset(buffer, 36, 0.18f, bass_profile, sample_offset);
		for (int midi : {69, 73, 76})
			add_harmonic_note_at_offset(buffer, midi, 0.12f, key_profile, sample_offset);
		for (int midi : {48, 52, 55, 60, 64})
			add_harmonic_note_at_offset(buffer, midi, 0.10f, guitar_profile, sample_offset);
		for (int midi : {76, 79})
			add_harmonic_note_at_offset(buffer, midi, 0.060f, other_profile, sample_offset);
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	}

	runner.expect(grid_has_any_active(snapshot.keyboard_notes),
		      "mixed keyboard/guitar bounds: expected keyboard notes active");
	runner.expect(grid_has_any_active(snapshot.guitar_notes),
		      "mixed keyboard/guitar bounds: expected guitar notes active");
	runner.expect(grid_active_cell_count(snapshot.keyboard_notes) <= 8,
		      "mixed keyboard/guitar bounds: expected keyboard grid <= 8 active cells, got " +
			      std::to_string(grid_active_cell_count(snapshot.keyboard_notes)) + " label `" +
			      snapshot.keyboard.label + "`");
	runner.expect(grid_active_cell_count(snapshot.guitar_notes) <= 6,
		      "mixed keyboard/guitar bounds: expected guitar grid <= 6 active cells, got " +
			      std::to_string(grid_active_cell_count(snapshot.guitar_notes)) + " label `" +
			      snapshot.guitar.label + "`");
}

void check_sparse_full_mix_other_requires_temporal_confirmation(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};
	add_harmonic_note(buffer, 74, 0.24f, other_profile);

	mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_global_pitch_class(runner, snapshot, 2, "sparse full-mix other confirmation first-frame global");
	expect_no_pitch_class(runner, snapshot.other_notes, 2, "sparse full-mix other confirmation first-frame other");
	runner.expect(grid_pitch_active(snapshot.ambiguous_notes, 2),
		      "sparse full-mix other confirmation: expected first D5 candidate to stay ambiguous");

	snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_pitch_class(runner, snapshot.other_notes, 2, "sparse full-mix other confirmation second-frame other");
	expect_midi_not_duplicated_across_rows(runner, snapshot, 74, "sparse full-mix other confirmation ownership");
}

void check_explicit_input_mode_and_bpm(Runner &runner)
{
	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.14f, 0.05f, 0.02f};
		for (int midi : {60, 64, 67})
			add_harmonic_note(buffer, midi, 0.24f, piano_profile);

		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "piano", 0);
		expect_label(runner, snapshot.global_chord.label, "C",
			     "explicit input mode: FullMix should override piano source-name isolation");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.analysis_interval_seconds = 0.05f;
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		mao::AnalysisSnapshot snapshot = {};
		for (int frame = 0; frame < 108; ++frame) {
			mao_test::Buffer buffer = {};
			if (frame % 12 == 0) {
				add_decayed_sine(buffer, 65.0f, 0.90f, 1400);
				add_decayed_sine(buffer, 1100.0f, 0.30f, 520);
			}
			snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "tempo test", 0);
		}

		runner.expect(snapshot.estimated_bpm >= 70.0f && snapshot.estimated_bpm <= 130.0f,
			      "BPM estimate: expected plausible tempo from synthetic pulse, got " +
				      std::to_string(snapshot.estimated_bpm));
		runner.expect(snapshot.bpm_confidence >= 0.20f,
			      "BPM estimate: expected confidence >= 20%, got " +
				      std::to_string(snapshot.bpm_confidence));
	}
}

void check_frontend_full_mix_equivalence(Runner &runner)
{
	mao::AnalysisEngine obs_engine;
	mao::AnalysisEngine standalone_engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	const auto obs_ready = obs_engine.analyze(nullptr, 0, settings, "OBS MIX", 0);
	const auto standalone_ready = standalone_engine.analyze(nullptr, 0, settings, "SPEAKER MONITOR", 0);
	expect_frontend_equivalent_snapshot(runner, obs_ready, standalone_ready, "frontend equivalence ready");

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const std::vector<float> other_profile = {1.0f, 0.58f, 0.34f, 0.20f};

	for (int frame = 0; frame < 12; ++frame) {
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
		mao_test::Buffer buffer = {};
		if (frame < 6) {
			add_harmonic_note_at_offset(buffer, 36, 0.18f, bass_profile, sample_offset);
			for (int midi : {60, 64, 67})
				add_harmonic_note_at_offset(buffer, midi, 0.10f, key_profile, sample_offset);
			for (int midi : {48, 52, 55})
				add_harmonic_note_at_offset(buffer, midi, 0.075f, guitar_profile, sample_offset);
		} else {
			add_harmonic_note_at_offset(buffer, 43, 0.18f, bass_profile, sample_offset);
			for (int midi : {55, 59, 62})
				add_harmonic_note_at_offset(buffer, midi, 0.11f, key_profile, sample_offset);
			for (int midi : {50, 55, 59})
				add_harmonic_note_at_offset(buffer, midi, 0.075f, guitar_profile, sample_offset);
		}
		add_harmonic_note_at_offset(buffer, frame < 6 ? 76 : 74, 0.055f, other_profile, sample_offset);
		if (frame == 2 || frame == 8) {
			add_decayed_sine(buffer, 65.0f, 0.24f, 1400);
			add_decayed_sine(buffer, 1100.0f, 0.22f, 520);
		}

		const auto obs_snapshot = obs_engine.analyze(buffer.data(), buffer.size(), settings, "OBS MIX", 0);
		const auto standalone_snapshot =
			standalone_engine.analyze(buffer.data(), buffer.size(), settings, "SPEAKER MONITOR", 0);
		expect_frontend_equivalent_snapshot(runner, obs_snapshot, standalone_snapshot,
						    "frontend equivalence frame " + std::to_string(frame));
	}
}

int midi_at_or_above(int min_midi, int pitch_class)
{
	return min_midi + ((pitch_class - min_midi % 12 + 12) % 12);
}

int bass_midi_for_pitch_class(int pitch_class)
{
	int midi = 24 + pitch_class;
	while (midi < 31)
		midi += 12;
	while (midi > 43)
		midi -= 12;
	return midi;
}

bool is_foundation_instrument(const char *instrument)
{
	return std::strcmp(instrument, "Db") == 0 || std::strcmp(instrument, "Tba") == 0;
}

int urmp_instrument_floor(const char *instrument)
{
	if (std::strcmp(instrument, "Vn") == 0 || std::strcmp(instrument, "Fl") == 0 ||
	    std::strcmp(instrument, "Ob") == 0 || std::strcmp(instrument, "Tpt") == 0)
		return 72;
	if (std::strcmp(instrument, "Va") == 0 || std::strcmp(instrument, "Cl") == 0 ||
	    std::strcmp(instrument, "Sax") == 0)
		return 67;
	if (std::strcmp(instrument, "Vc") == 0 || std::strcmp(instrument, "Hn") == 0 ||
	    std::strcmp(instrument, "Tbn") == 0 || std::strcmp(instrument, "Bn") == 0)
		return 60;
	return 60;
}

const char *urmp_source_hint(const char *instrument)
{
	if (is_foundation_instrument(instrument))
		return "bass track";
	if (std::strcmp(instrument, "Vn") == 0 || std::strcmp(instrument, "Va") == 0 ||
	    std::strcmp(instrument, "Vc") == 0 || std::strcmp(instrument, "Db") == 0)
		return "string track";
	if (std::strcmp(instrument, "Tpt") == 0 || std::strcmp(instrument, "Hn") == 0 ||
	    std::strcmp(instrument, "Tbn") == 0 || std::strcmp(instrument, "Tba") == 0)
		return "brass track";
	return "wind track";
}

void add_urmp_instrument_track(mao_test::Buffer &buffer, const char *instrument, int midi)
{
	const std::vector<float> string_profile = {1.0f, 0.52f, 0.31f, 0.18f, 0.10f};
	const std::vector<float> wind_profile = {1.0f, 0.46f, 0.25f, 0.13f, 0.07f};
	const std::vector<float> brass_profile = {1.0f, 0.62f, 0.38f, 0.22f, 0.13f};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};

	if (is_foundation_instrument(instrument)) {
		add_harmonic_note(buffer, midi, 0.22f, bass_profile);
		return;
	}
	if (std::strcmp(instrument, "Vn") == 0 || std::strcmp(instrument, "Va") == 0 ||
	    std::strcmp(instrument, "Vc") == 0) {
		add_harmonic_note(buffer, midi, 0.13f, string_profile);
		return;
	}
	if (std::strcmp(instrument, "Tpt") == 0 || std::strcmp(instrument, "Hn") == 0 ||
	    std::strcmp(instrument, "Tbn") == 0) {
		add_harmonic_note(buffer, midi, 0.12f, brass_profile);
		return;
	}

	add_harmonic_note(buffer, midi, 0.13f, wind_profile);
}

void append_pitch_class(std::vector<int> &pitch_classes, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	if (std::find(pitch_classes.begin(), pitch_classes.end(), pitch_class) == pitch_classes.end())
		pitch_classes.push_back(pitch_class);
}

void check_urmp_real_piece_metadata_regressions(Runner &runner)
{
	struct UrmpPieceCase {
		const char *id;
		const char *title;
		std::vector<const char *> instruments;
		int root_pitch_class;
		bool minor;
	};

	// Piece titles and instrumentations mirror the official URMP documentation.
	const std::vector<UrmpPieceCase> pieces = {
		{"01_Jupiter", "Jupiter", {"Vn", "Vc"}, 0, false},
		{"02_Sonata", "Sonata", {"Vn", "Vn"}, 7, false},
		{"03_Dance", "Dance of the Sugar Plum Fairy", {"Fl", "Cl"}, 4, true},
		{"04_Allegro", "Allegro for Musical Clock", {"Fl", "Fl"}, 2, false},
		{"05_Entertainer", "The Entertainer", {"Tpt", "Tpt"}, 0, false},
		{"06_Entertainer", "The Entertainer", {"Sax", "Sax"}, 5, false},
		{"07_GString", "Air on the G string", {"Tpt", "Tbn"}, 9, true},
		{"08_Spring", "Spring from the Four Seasons", {"Fl", "Vn"}, 4, false},
		{"09_Jesus", "Jesus Bleibet Meine Freude", {"Tpt", "Vn"}, 7, false},
		{"10_March", "March from Occasional Oratorio", {"Tpt", "Sax"}, 2, false},
		{"11_Maria", "Ave Maria", {"Ob", "Vc"}, 8, false},
		{"12_Spring", "Spring from the Four Seasons", {"Vn", "Vn", "Vc"}, 4, false},
		{"13_Hark", "Hark the herald angels sing", {"Vn", "Vn", "Va"}, 7, false},
		{"14_Waltz", "Waltz from Sleeping Beauty", {"Fl", "Fl", "Cl"}, 3, false},
		{"15_Surprise", "Theme from Surprise Symphony", {"Tpt", "Tpt", "Tbn"}, 0, false},
		{"16_Surprise", "Theme from Surprise Symphony", {"Tpt", "Tpt", "Sax"}, 0, false},
		{"17_Nocturne", "Nocturne", {"Vn", "Fl", "Cl"}, 1, true},
		{"18_Nocturne", "Nocturne", {"Vn", "Fl", "Tpt"}, 1, true},
		{"19_Pavane", "Pavane", {"Cl", "Vn", "Vc"}, 6, true},
		{"20_Pavane", "Pavane", {"Tpt", "Vn", "Vc"}, 6, true},
		{"21_Rejouissance", "La Rejouissance", {"Cl", "Tbn", "Tba"}, 2, false},
		{"22_Rejouissance", "La Rejouissance", {"Sax", "Tbn", "Tba"}, 2, false},
		{"23_Rejouissance", "La Rejouissance", {"Cl", "Sax", "Tba"}, 2, false},
		{"24_Pirates", "Pirates of the Aegean", {"Vn", "Vn", "Va", "Vc"}, 9, true},
		{"25_Pirates", "Pirates of the Aegean", {"Vn", "Vn", "Va", "Sax"}, 9, true},
		{"26_King", "In the Hall of the Mountain King", {"Vn", "Vn", "Va", "Vc"}, 11, true},
		{"27_King", "In the Hall of the Mountain King", {"Vn", "Vn", "Va", "Sax"}, 11, true},
		{"28_Fugue", "The Art of the Fugue", {"Fl", "Ob", "Cl", "Bn"}, 2, true},
		{"29_Fugue", "The Art of the Fugue", {"Fl", "Fl", "Ob", "Cl"}, 2, true},
		{"30_Fugue", "The Art of the Fugue", {"Fl", "Fl", "Ob", "Sax"}, 2, true},
		{"31_Slavonic", "Slavonic Dance", {"Tpt", "Tpt", "Hn", "Tbn"}, 4, false},
		{"32_Fugue", "The Art of the Fugue", {"Vn", "Vn", "Va", "Vc"}, 2, true},
		{"33_Elise", "Fur Elise", {"Tpt", "Tpt", "Hn", "Tbn"}, 9, true},
		{"34_Fugue", "The Art of the Fugue", {"Tpt", "Tpt", "Hn", "Tbn"}, 2, true},
		{"35_Rondeau", "Rondeau from Abdelazer", {"Vn", "Vn", "Va", "Db"}, 2, false},
		{"36_Rondeau", "Rondeau from Abdelazer", {"Vn", "Vn", "Va", "Vc"}, 2, false},
		{"37_Rondeau", "Rondeau from Abdelazer", {"Fl", "Vn", "Va", "Cl"}, 2, false},
		{"38_Jerusalem", "Jerusalem", {"Vn", "Vn", "Va", "Vc", "Db"}, 10, false},
		{"39_Jerusalem", "Jerusalem", {"Vn", "Vn", "Va", "Sax", "Db"}, 10, false},
		{"40_Miserere", "Miserere Mei Deus", {"Fl", "Fl", "Ob", "Cl", "Bn"}, 5, true},
		{"41_Miserere", "Miserere Mei Deus", {"Fl", "Fl", "Ob", "Sax", "Bn"}, 5, true},
		{"42_Arioso", "Arioso", {"Tpt", "Tpt", "Hn", "Tbn", "Tba"}, 7, false},
		{"43_Chorale", "Chorale", {"Tpt", "Tpt", "Hn", "Tbn", "Tba"}, 0, false},
		{"44_K515", "String Quintet K515", {"Vn", "Vn", "Va", "Va", "Db"}, 3, false},
	};

	for (const UrmpPieceCase &piece : pieces) {
		const std::vector<int> intervals = piece.minor ? std::vector<int>{0, 3, 7} :
								 std::vector<int>{0, 4, 7};
		const std::string chord = std::string(mao_test::note_name(piece.root_pitch_class)) +
					  (piece.minor ? "m" : "");
		const std::string context = std::string("URMP same-song multitrack ") + piece.id + " " +
					    piece.title + " " + chord;
		std::vector<int> expected_other_pitch_classes;
		int expected_bass_midi = -1;
		mao_test::Buffer mix = {};
		std::size_t harmonic_track_index = 0;

		for (const char *instrument : piece.instruments) {
			int midi = 0;
			if (is_foundation_instrument(instrument)) {
				midi = bass_midi_for_pitch_class(piece.root_pitch_class);
				expected_bass_midi = midi;
			} else {
				const int interval = intervals[harmonic_track_index % intervals.size()];
				midi = midi_at_or_above(urmp_instrument_floor(instrument),
							(piece.root_pitch_class + interval) % 12);
				append_pitch_class(expected_other_pitch_classes, midi);
				++harmonic_track_index;
			}

			mao_test::Buffer track_buffer = {};
			add_urmp_instrument_track(track_buffer, instrument, midi);
			for (std::size_t i = 0; i < mix.size(); ++i)
				mix[i] += track_buffer[i];

			const auto track_snapshot = analyze_buffer(track_buffer, urmp_source_hint(instrument));
			const std::string track_context = context + " track " + instrument;
			if (is_foundation_instrument(instrument)) {
				expect_label(runner, track_snapshot.bass.label, mao_test::note_label(midi),
					     track_context);
			} else {
				expect_note_token(runner, track_snapshot.other.label,
						  mao_test::note_label(midi).c_str(), track_context);
			}
		}

		const auto snapshot = analyze_buffer(mix, "URMP same-song full mix");

		if (expected_bass_midi >= 0)
			expect_label(runner, snapshot.bass.label, mao_test::note_label(expected_bass_midi),
				     context + " bass foundation");

		for (int pitch_class : expected_other_pitch_classes) {
			expect_global_pitch_class(runner, snapshot, pitch_class, context + " global notes");
		}

		if (expected_other_pitch_classes.size() >= 3)
			runner.expect(std::strcmp(snapshot.global_chord.label, "--") != 0,
				      context + ": expected a global chord label, got `--`");
	}
}

void check_slakh_style_multitrack_song_regressions(Runner &runner)
{
	struct SongCase {
		const char *name;
		int root_pitch_class;
		bool minor;
	};

	const std::vector<SongCase> songs = {
		{"song 01", 0, false}, {"song 02", 9, false}, {"song 03", 5, false},
		{"song 04", 7, false}, {"song 05", 2, true},  {"song 06", 4, true},
		{"song 07", 11, true}, {"song 08", 3, false}, {"song 09", 8, false},
		{"song 10", 10, false}, {"song 11", 1, true}, {"song 12", 6, true},
		{"song 13", 2, false}, {"song 14", 4, false}, {"song 15", 9, true},
		{"song 16", 7, true}, {"song 17", 5, true}, {"song 18", 11, false},
		{"song 19", 1, false}, {"song 20", 6, false}, {"song 21", 3, true},
		{"song 22", 8, true}, {"song 23", 10, true}, {"song 24", 0, true},
	};

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
	const std::vector<float> guitar_profile = {1.0f, 0.42f, 0.20f, 0.10f, 0.05f};
	const std::vector<float> distorted_guitar_profile = {1.0f, 0.54f, 0.30f, 0.18f, 0.10f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	for (std::size_t i = 0; i < songs.size(); ++i) {
		const SongCase &song = songs[i];
		const std::vector<int> intervals = song.minor ? std::vector<int>{0, 3, 7} :
								 std::vector<int>{0, 4, 7};
		std::vector<int> keyboard_midis;
		std::vector<int> guitar_midis;
		std::vector<int> other_midis;
		mao_test::Buffer buffer = {};

		const int bass_midi = bass_midi_for_pitch_class(song.root_pitch_class);
		add_harmonic_note(buffer, bass_midi, 0.20f, bass_profile);

		const int keyboard_root = 60 + song.root_pitch_class;
		const int guitar_root = midi_at_or_above(52, song.root_pitch_class);
		const int other_root = 72 + song.root_pitch_class;
		for (int interval : intervals) {
			keyboard_midis.push_back(keyboard_root + interval);
			guitar_midis.push_back(guitar_root + interval);
			other_midis.push_back(other_root + interval);
		}

		for (int midi : keyboard_midis)
			add_harmonic_note(buffer, midi, 0.13f, piano_profile);
		for (int midi : guitar_midis)
			add_harmonic_note(buffer, midi, 0.11f, i % 3 == 0 ? distorted_guitar_profile : guitar_profile);
		for (int midi : other_midis)
			add_harmonic_note(buffer, midi, 0.075f, other_profile);
		add_decayed_sine(buffer, 65.0f, 0.18f, 700);
		add_decayed_sine(buffer, 5200.0f, 0.035f, 420);

		const auto snapshot = analyze_buffer(buffer, "Slakh-style full mix");
		const std::string chord = std::string(mao_test::note_name(song.root_pitch_class)) +
					  (song.minor ? "m" : "");
		const std::string context = std::string("Slakh-style multitrack ") + song.name + " " + chord;

		expect_label(runner, snapshot.bass.label, mao_test::note_label(bass_midi), context + " bass");
		runner.expect(has_chord_label(snapshot.global_chord.label, chord),
			      context + ": expected global chord `" + chord + "`, got `" +
				      snapshot.global_chord.label + "`");

		for (int interval : intervals) {
			const int pitch_class = (song.root_pitch_class + interval) % 12;
			expect_global_pitch_class(runner, snapshot, pitch_class, context + " global");
		}
	}
}

void check_public_multitrack_dataset_style_regressions(Runner &runner)
{
	struct DatasetCase {
		const char *name;
		int root_pitch_class;
		bool minor;
		bool drums;
		bool bass;
		bool keyboard;
		bool guitar;
		bool vocal;
		bool other;
		bool distorted_guitar;
	};

	const std::vector<DatasetCase> datasets = {
		{"MUSDB18 four-stem rock", 0, false, true, true, true, true, true, true, false},
		{"MUSDB18-HQ four-stem pop", 9, false, true, true, true, true, true, true, false},
		{"DSD100 Mixing Secrets band", 5, false, true, true, true, true, true, true, false},
		{"Cambridge MT guitar session", 7, false, true, true, true, true, true, true, true},
		{"MedleyDB full band", 2, true, true, true, true, true, true, true, false},
		{"MedleyDB 2.0 fusion", 4, true, true, true, true, true, false, true, false},
		{"MoisesDB five-stem guitar piano", 11, true, true, true, true, true, true, true, false},
		{"MoisesDB six-stem pop", 3, false, true, true, true, true, true, true, false},
		{"URMP string quartet style", 8, false, false, false, true, false, false, true, false},
		{"URMP chamber piano strings", 10, false, false, true, true, false, false, true, false},
		{"RawStems eight-group clean", 1, true, true, true, true, true, true, true, false},
		{"RawStems restored distorted", 6, true, true, true, true, true, true, true, true},
		{"MulTTiPop MIDI pop", 2, false, true, true, true, true, true, true, false},
		{"ACMID seven-stem piano guitar strings", 4, false, true, true, true, true, false, true, false},
		{"Spheres orchestral brass strings", 9, true, false, true, true, false, false, true, false},
		{"MDX challenge four-stem", 7, true, true, true, true, true, true, true, false},
		{"Open Multitrack Testbed indie", 5, true, true, true, true, true, true, true, false},
		{"Native Instruments stems pack", 0, true, true, true, true, true, true, true, true},
		{"Heise remix stems", 11, false, true, true, true, true, true, true, true},
		{"Slakh MIDI rendered ensemble", 3, true, true, true, true, true, false, true, false},
		{"MUSDB18 sparse vocal other", 6, false, true, true, true, false, true, true, false},
		{"MedleyDB instrumental no vocal", 8, true, true, true, true, true, false, true, false},
		{"MoisesDB guitar focus", 10, true, true, true, true, true, true, true, true},
		{"RawStems keyboard focus", 1, false, true, true, true, false, true, true, false},
		{"MulTTiPop piano roll dense", 4, true, true, true, true, true, true, true, false},
		{"ACMID acoustic guitar", 0, false, true, true, true, true, false, true, false},
		{"ACMID electric guitar", 2, true, true, true, true, true, false, true, true},
		{"Spheres low strings bass support", 5, false, false, true, true, false, false, true, false},
		{"URMP violin cello piano", 7, false, false, true, true, false, false, true, false},
		{"DSD100 vocal band alternate", 9, true, true, true, true, true, true, true, false},
		{"Cambridge MT dense rock", 11, true, true, true, true, true, true, true, true},
		{"MedleyDB jazz fusion", 3, false, true, true, true, true, false, true, false},
		{"MoisesDB stem taxonomy broad", 6, true, true, true, true, true, true, true, false},
		{"RawStems hierarchical groups", 8, false, true, true, true, true, true, true, true},
		{"Open Multitrack Testbed live", 10, false, true, true, true, true, true, true, false},
		{"Slakh orchestral MIDI", 1, true, false, true, true, false, false, true, false},
	};

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
	const std::vector<float> guitar_profile = {1.0f, 0.42f, 0.20f, 0.10f, 0.05f};
	const std::vector<float> distorted_guitar_profile = {1.0f, 0.54f, 0.30f, 0.18f, 0.10f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};
	const std::vector<float> vocal_profile = {1.0f, 0.04f, 0.015f};

	for (std::size_t i = 0; i < datasets.size(); ++i) {
		const DatasetCase &dataset = datasets[i];
		const std::vector<int> intervals = dataset.minor ? std::vector<int>{0, 3, 7} :
								   std::vector<int>{0, 4, 7};
		const std::string chord = std::string(mao_test::note_name(dataset.root_pitch_class)) +
					  (dataset.minor ? "m" : "");
		const std::string context = std::string("public multitrack dataset fixture ") + dataset.name +
					    " " + chord;
		std::vector<int> keyboard_midis;
		std::vector<int> guitar_midis;
		std::vector<int> other_midis;
		mao_test::Buffer buffer = {};

		if (dataset.bass)
			add_harmonic_note(buffer, bass_midi_for_pitch_class(dataset.root_pitch_class), 0.19f,
					  bass_profile);

		const int keyboard_root = 60 + dataset.root_pitch_class;
		const int guitar_root = midi_at_or_above(52, dataset.root_pitch_class);
		const int other_root = 72 + dataset.root_pitch_class;
		for (int interval : intervals) {
			keyboard_midis.push_back(keyboard_root + interval);
			guitar_midis.push_back(guitar_root + interval);
			other_midis.push_back(other_root + interval);
		}

		if (dataset.keyboard) {
			for (int midi : keyboard_midis)
				add_harmonic_note(buffer, midi, 0.14f, piano_profile);
		}
		if (dataset.guitar) {
			const std::vector<float> &profile =
				dataset.distorted_guitar ? distorted_guitar_profile : guitar_profile;
			for (int midi : guitar_midis)
				add_harmonic_note(buffer, midi, 0.105f, profile);
		}
		if (dataset.other) {
			for (int midi : other_midis)
				add_harmonic_note(buffer, midi, 0.075f, other_profile);
		}
		if (dataset.vocal) {
			int vocal_midi = 72 + dataset.root_pitch_class;
			if (vocal_midi > 84)
				vocal_midi -= 12;
			add_harmonic_note(buffer, vocal_midi, 0.16f, vocal_profile);
		}
		if (dataset.drums) {
			add_decayed_sine(buffer, 65.0f, 0.15f, 700);
			add_decayed_sine(buffer, 220.0f, 0.06f, 520);
			add_decayed_sine(buffer, 5200.0f, 0.028f, 420);
		}

		const auto snapshot = analyze_buffer(buffer, "public dataset full mix");

		if (dataset.bass) {
			expect_label(runner, snapshot.bass.label,
				     mao_test::note_label(bass_midi_for_pitch_class(dataset.root_pitch_class)),
				     context + " bass");
		}
		if (dataset.keyboard || dataset.guitar || dataset.other) {
			runner.expect(has_chord_label(snapshot.global_chord.label, chord),
				      context + ": expected global chord `" + chord + "`, got `" +
					      snapshot.global_chord.label + "`");
		}

		for (int interval : intervals) {
			const int pitch_class = (dataset.root_pitch_class + interval) % 12;
			if (dataset.keyboard || dataset.guitar || dataset.other) {
				expect_global_pitch_class(runner, snapshot, pitch_class, context + " global");
			}
		}
		if (dataset.vocal) {
			expect_global_pitch_class(runner, snapshot, dataset.root_pitch_class, context + " vocal global");
		}
	}
}

void check_drum_hit_with_melodic_mix(Runner &runner)
{
	mao::AnalysisEngine engine;
	const mao::AnalysisSettings settings = mao_test::default_settings();
	mao_test::Buffer buffer = {};
	add_decayed_sine(buffer, 65.0f, 0.85f);
	add_decayed_sine(buffer, 1100.0f, 0.24f, 520);
	mao_test::Buffer background = {};
	for (int midi : {60, 64, 67}) {
		add_harmonic_note(background, midi, 0.20f, {1.0f, 0.16f, 0.08f});
		add_harmonic_note(buffer, midi, 0.20f, {1.0f, 0.16f, 0.08f});
	}
	for (int i = 0; i < 4; ++i)
		(void)engine.analyze(background.data(), background.size(), settings, "full mix", 0);

	const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "drum hit with melodic mix: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	for (int pitch_class : {0, 4, 7}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "drum hit with melodic mix");
	}
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

void check_complex_real_timbres_survive_tuning_wobble(Runner &runner)
{
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;

	auto analyze_twice = [&](const mao_test::Buffer &buffer, const char *source) {
		mao::AnalysisEngine engine;
		(void)engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
		return engine.analyze(buffer.data(), buffer.size(), settings, source, 0);
	};

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> bass_profile = {1.0f, 0.28f, 0.13f, 0.06f};
		add_detuned_harmonic_note_at_offset(buffer, 40, 0.20f, bass_profile, 13.0f, 0);
		const auto snapshot = analyze_twice(buffer, "bass guitar");
		expect_label(runner, snapshot.bass.label, "E2", "complex real timbre bass tuning wobble");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.18f, 0.07f, 0.03f};
		for (int midi : {60, 64, 67})
			add_detuned_harmonic_note_at_offset(buffer, midi, 0.18f, piano_profile, -13.0f, 0);
		const auto snapshot = analyze_twice(buffer, "piano");
		expect_note_token(runner, snapshot.keyboard.label, "C4", "complex real timbre piano tuning wobble");
		expect_note_token(runner, snapshot.keyboard.label, "E4", "complex real timbre piano tuning wobble");
		expect_note_token(runner, snapshot.keyboard.label, "G4", "complex real timbre piano tuning wobble");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "complex real timbre piano chord");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> distorted_guitar_profile = {1.0f, 0.58f, 0.34f, 0.20f, 0.12f};
		for (int midi : {55, 59, 62})
			add_detuned_harmonic_note_at_offset(buffer, midi, 0.15f, distorted_guitar_profile, 14.0f,
							   0);
		const auto snapshot = analyze_twice(buffer, "distorted guitar");
		expect_note_token(runner, snapshot.guitar.label, "G3", "complex real timbre distorted guitar");
		expect_note_token(runner, snapshot.guitar.label, "B3", "complex real timbre distorted guitar");
		expect_note_token(runner, snapshot.guitar.label, "D4", "complex real timbre distorted guitar");
		expect_label(runner, snapshot.guitar_chord.label, "G", "complex real timbre distorted guitar chord");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> synth_profile = {1.0f, 0.70f, 0.45f, 0.25f, 0.14f};
		for (int midi : {62, 66, 69})
			add_detuned_harmonic_note_at_offset(buffer, midi, 0.13f, synth_profile, -14.0f, 0);
		const auto snapshot = analyze_twice(buffer, "synth lead");
		expect_note_token(runner, snapshot.other.label, "D4", "complex real timbre synth");
		expect_note_token(runner, snapshot.other.label, "F#4", "complex real timbre synth");
		expect_note_token(runner, snapshot.other.label, "A4", "complex real timbre synth");
		expect_label(runner, snapshot.other_chord.label, "D", "complex real timbre synth chord");
	}
}

void check_low_acoustic_piano_fundamental_survives_partial_dominance(Runner &runner)
{
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> low_piano_profile = {0.55f, 0.72f, 1.0f, 0.46f, 0.26f, 0.14f};
	add_harmonic_note(buffer, 25, 0.24f, low_piano_profile);

	mao::AnalysisEngine engine;
	(void)engine.analyze(buffer.data(), buffer.size(), settings, "iowa piano", 0);
	const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "iowa piano", 0);
	expect_note_token(runner, snapshot.keyboard.label, "C#1",
			  "low acoustic piano fundamental partial-dominant timbre");
	runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 25) > 0.0f,
		      std::string("low acoustic piano fundamental: expected C#1 cell active, got `") +
			      snapshot.keyboard.label + "`");
	expect_no_drums(runner, snapshot, "low acoustic piano fundamental");
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

	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 48, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 55, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 52, 0.060f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_label(runner, snapshot.guitar_chord.label, "C", "weak guitar third hidden chord grid");
		expect_note_token(runner, snapshot.guitar.label, "C3", "weak guitar third hidden chord grid");
		expect_note_token(runner, snapshot.guitar.label, "G3", "weak guitar third hidden chord grid");
		runner.expect(!mao_test::has_note_token(snapshot.guitar.label, "E3"),
			      std::string("weak guitar third hidden chord grid: expected E3 hidden, got `") +
				      snapshot.guitar.label + "`");
	}

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

void check_keyboard_hand_span_chords(Runner &runner)
{
	{
		const auto buffer = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "keyboard hand-span compact C");
	}

	{
		const auto buffer = mao_test::make_midi_notes({48, 76, 91}, 0.34f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "C", "keyboard hand-span impossible C");
		expect_label(runner, snapshot.keyboard_chord.label, "--", "keyboard hand-span impossible spread");
	}

	{
		const auto buffer = mao_test::make_midi_notes({36, 72, 76, 79}, 0.32f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_label(runner, snapshot.keyboard_chord.label, "C", "keyboard hand-span compact upper C");
	}

	{
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 67, 0.28f);
		mao_test::add_midi_note(buffer, 71, 0.28f);
		mao_test::add_midi_note(buffer, 74, 0.28f);
		const auto snapshot = analyze_buffer(buffer, "keyboard");
		expect_label(runner, snapshot.keyboard_chord.label, "G", "keyboard hand-span mixed right hand");
		expect_no_chord_label(runner, snapshot.keyboard_chord.label, "C", "keyboard hand-span mixed right hand");
	}
}

void check_guitar_caged_voicings(Runner &runner)
{
	struct GuitarShape {
		const char *name;
		std::vector<int> midis;
		const char *chord;
	};

	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const std::vector<GuitarShape> shapes = {
		{"C open shape", {48, 52, 55, 60, 64}, "C"},
		{"A open shape", {45, 52, 57, 61, 64}, "A"},
		{"G open shape", {43, 47, 50, 55, 59, 67}, "G"},
		{"E open shape", {40, 47, 52, 56, 59, 64}, "E"},
		{"D open shape", {50, 57, 62, 66}, "D"},
		{"A minor shape", {45, 52, 57, 60, 64}, "Am"},
		{"E minor shape", {40, 47, 52, 55, 59, 64}, "Em"},
		{"D minor shape", {50, 57, 62, 65}, "Dm"},
		{"F E-shape barre", {41, 48, 53, 57, 60, 65}, "F"},
		{"Bm A-shape barre", {47, 54, 59, 62, 66}, "Bm"},
	};

	for (const GuitarShape &shape : shapes) {
		const auto buffer = make_harmonic_notes(shape.midis, 0.17f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		const std::string context = std::string("CAGED guitar ") + shape.name;
		expect_label(runner, snapshot.guitar_chord.label, shape.chord, context);
		for (int midi : shape.midis) {
			const std::string expected_note = mao_test::note_label(midi);
			expect_note_token(runner, snapshot.guitar.label, expected_note.c_str(), context);
		}
	}
}

void check_guitar_caged_mix_root_independence(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> keyboard_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};

	add_harmonic_note(buffer, 31, 0.42f, bass_profile);
	add_harmonic_note(buffer, 55, 0.22f, keyboard_profile);
	add_harmonic_note(buffer, 59, 0.22f, keyboard_profile);
	add_harmonic_note(buffer, 62, 0.22f, keyboard_profile);
	for (int midi : {48, 52, 55, 60, 64})
		add_harmonic_note(buffer, midi, 0.20f, guitar_profile);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_label(runner, snapshot.bass.label, "G1", "CAGED mix root independence bass");
	expect_label(runner, snapshot.global_chord.label, "C", "CAGED mix root independence global chord");
	expect_no_chord_label(runner, snapshot.global_chord.label, "G", "CAGED mix root independence global chord");
	for (int pitch_class : {0, 4, 7}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "CAGED mix root independence global notes");
	}
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
	expect_global_pitch_class(runner, snapshot, 0, "same-note timbre split global");
	expect_midi_ambiguous_only(runner, snapshot, 60, "same-note timbre split");
	expect_midi_not_duplicated_across_rows(runner, snapshot, 60, "same-note timbre split ownership");
}

void check_ambiguous_same_note_full_mix_chord_ownership(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
	const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	for (int midi : {60, 64, 67}) {
		add_harmonic_note(buffer, midi, 0.24f, piano_profile);
		add_harmonic_note(buffer, midi, 0.22f, guitar_profile);
		add_harmonic_note(buffer, midi, 0.20f, other_profile);
	}

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "ambiguous same-note full mix", 3);
	expect_label(runner, snapshot.global_chord.label, "C", "ambiguous same-note full mix global chord");
	expect_no_chord(runner, snapshot.keyboard_chord, "ambiguous same-note full mix keyboard chord");
	expect_no_chord(runner, snapshot.guitar_chord, "ambiguous same-note full mix guitar chord");
	expect_no_chord(runner, snapshot.other_chord, "ambiguous same-note full mix other chord");
	for (int midi : {60, 64, 67})
		expect_midi_ambiguous_only(runner, snapshot, midi, "ambiguous same-note full mix ownership");
}

void check_full_mix_global_chord_guides_root_with_inversion(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.25f;
	settings.root_window_seconds = 15.0f;

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
	const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	mao_test::Buffer buffer = {};
	add_harmonic_note(buffer, 40, 0.34f, bass_profile);
	for (int midi : {60, 64, 67}) {
		add_harmonic_note(buffer, midi, 0.20f, piano_profile);
		add_harmonic_note(buffer, midi, 0.18f, guitar_profile);
		add_harmonic_note(buffer, midi, 0.16f, other_profile);
	}

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 72; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix inversion", 0);

	expect_label(runner, snapshot.bass.label, "E2", "full-mix inversion bass");
	expect_label(runner, snapshot.global_chord.label, "C", "full-mix inversion global chord");
	expect_no_chord(runner, snapshot.keyboard_chord, "full-mix inversion keyboard chord");
	expect_no_chord(runner, snapshot.guitar_chord, "full-mix inversion guitar chord");
	expect_no_chord(runner, snapshot.other_chord, "full-mix inversion other chord");
	runner.expect(std::strcmp(snapshot.root.label, "C") == 0,
		      std::string("full-mix inversion: expected root C from global chord despite E bass, got `") +
			      snapshot.root.label + "` candidates `" + snapshot.root_candidates + "`");
}

void check_full_mix_keyboard_chord_ignores_bass_inversion(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> keyboard_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};

	mao_test::Buffer buffer = {};
	add_harmonic_note(buffer, 40, 0.34f, bass_profile);
	for (int midi : {60, 64, 67})
		add_harmonic_note(buffer, midi, 0.28f, keyboard_profile);

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 4; ++frame)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix keyboard inversion", 0);

	expect_label(runner, snapshot.bass.label, "E2", "full-mix keyboard inversion bass");
	expect_label(runner, snapshot.global_chord.label, "C", "full-mix keyboard inversion global chord");
	expect_label(runner, snapshot.keyboard_chord.label, "C", "full-mix keyboard inversion keyboard chord");
	expect_no_chord_label(runner, snapshot.keyboard_chord.label, "E",
			      "full-mix keyboard inversion keyboard chord");
	for (int pitch_class : {0, 4, 7})
		expect_pitch_class(runner, snapshot.keyboard_notes, pitch_class,
				   "full-mix keyboard inversion keyboard notes");
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

void check_bass_pure_tone_stays_out_of_harmonic_rows(Runner &runner)
{
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 40, 0.70f);
	const auto snapshot = analyze_buffer(buffer, "mix");
	expect_label(runner, snapshot.bass.label, "E2", "bass pure tone");
	runner.expect(!grid_pitch_active(snapshot.keyboard_notes, 4),
		      std::string("bass pure tone: expected keyboard E column inactive, got `") +
			      snapshot.keyboard.label + "`");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 4),
		      std::string("bass pure tone: expected guitar E column inactive, got `") + snapshot.guitar.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.vocal_notes, 4),
		      std::string("bass pure tone: expected vocal E column inactive, got `") + snapshot.vocal.label +
			      "`");
	runner.expect(!grid_pitch_active(snapshot.other_notes, 4),
		      std::string("bass pure tone: expected other E column inactive, got `") + snapshot.other.label +
			      "`");
}

void check_full_mix_bass_harmonic_note_not_duplicated(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.42f, 0.22f, 0.10f};
	add_harmonic_note(buffer, 40, 0.34f, bass_profile);

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker bass-only", 3);
	expect_label(runner, snapshot.bass.label, "E2", "full-mix bass harmonic ownership");
	expect_midi_not_duplicated_across_instruments(runner, snapshot, 40,
						      "full-mix bass harmonic ownership");
	expect_empty_note_grid(runner, snapshot.keyboard_notes, "full-mix bass harmonic keyboard spillover");
	expect_empty_note_grid(runner, snapshot.guitar_notes, "full-mix bass harmonic guitar spillover");
	expect_empty_note_grid(runner, snapshot.vocal_notes, "full-mix bass harmonic vocal spillover");
	expect_empty_note_grid(runner, snapshot.other_notes, "full-mix bass harmonic other spillover");
}

void check_multi_instrument_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};

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

	expect_label(runner, snapshot.global_chord.label, "C", "multi-instrument mix global chord");
	for (int pitch_class : {0, 4, 7, 6, 10, 2, 8}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "multi-instrument mix global");
	}
}

void check_low_level_full_instrument_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};

	add_harmonic_note(buffer, 35, 0.12f, bass_profile);
	add_harmonic_note(buffer, 60, 0.050f, key_profile);
	add_harmonic_note(buffer, 64, 0.050f, key_profile);
	add_harmonic_note(buffer, 67, 0.050f, key_profile);
	add_harmonic_note(buffer, 54, 0.038f, guitar_profile);
	add_harmonic_note(buffer, 58, 0.038f, guitar_profile);
	mao_test::add_midi_note(buffer, 74, 0.028f);
	mao_test::add_midi_note(buffer, 80, 0.026f);

	const auto snapshot = analyze_buffer(buffer, "Mic/Aux");
	expect_label(runner, snapshot.bass.label, "B1", "low-level full mix bass");
	for (int pitch_class : {0, 4, 7, 6, 10, 2, 8}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "low-level full mix global");
	}
}

void check_bass_survives_low_mid_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};

	add_harmonic_note(buffer, 35, 0.10f, bass_profile);
	add_harmonic_note(buffer, 54, 0.24f, guitar_profile);
	add_harmonic_note(buffer, 58, 0.24f, guitar_profile);

	const auto snapshot = analyze_buffer(buffer, "Mic/Aux");
	expect_label(runner, snapshot.bass.label, "B1", "bass survives low-mid mix");
	for (int pitch_class : {6, 10}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "bass survives low-mid mix global");
	}
}

void check_bass_pluck_does_not_trigger_kick(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	const std::vector<float> bass_profile = {1.0f, 0.42f, 0.22f, 0.10f};
	mao::AnalysisSnapshot snapshot = {};

	for (int frame = 0; frame < 8; ++frame) {
		mao_test::Buffer sustain = {};
		add_harmonic_note_at_offset(sustain, 36, 0.15f, bass_profile, static_cast<uint64_t>(frame) * 2400);
		snapshot = engine.analyze(sustain.data(), sustain.size(), settings, "Mic/Aux", 0);
	}

	mao_test::Buffer pluck = {};
	add_harmonic_note_at_offset(pluck, 36, 0.30f, bass_profile, 8 * 2400);
	add_decayed_sine(pluck, mao_test::midi_frequency(36), 0.11f, 1200);
	add_decayed_sine(pluck, mao_test::midi_frequency(48), 0.040f, 900);
	snapshot = engine.analyze(pluck.data(), pluck.size(), settings, "Mic/Aux", 0);
	expect_label(runner, snapshot.bass.label, "C2", "bass pluck no kick bass note");
	runner.expect(!snapshot.drums[mao::Kick].active,
		      "bass pluck no kick: expected kick inactive, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
}

void check_low_level_mic_aux_parts(Runner &runner)
{
	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = mao_test::default_settings();
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, 64, 0.035f);
		(void)engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		const auto snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		expect_note_token(runner, snapshot.keyboard.label, "E4", "low-level keyboard part");
		expect_no_drums(runner, snapshot, "low-level keyboard part");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
		add_harmonic_note(buffer, 54, 0.055f, guitar_profile);
		add_harmonic_note(buffer, 58, 0.055f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_note_token(runner, snapshot.guitar.label, "F#3", "low-level guitar part");
		expect_note_token(runner, snapshot.guitar.label, "A#3", "low-level guitar part");
		expect_no_drums(runner, snapshot, "low-level guitar part");
	}
}

void check_dense_multi_instrument_mix(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};

	add_harmonic_note(buffer, 37, 0.50f, bass_profile);
	add_harmonic_note(buffer, 62, 0.32f, key_profile);
	add_harmonic_note(buffer, 66, 0.32f, key_profile);
	add_harmonic_note(buffer, 69, 0.32f, key_profile);
	add_harmonic_note(buffer, 53, 0.32f, guitar_profile);
	add_harmonic_note(buffer, 58, 0.32f, guitar_profile);
	add_harmonic_note(buffer, 65, 0.32f, guitar_profile);
	mao_test::add_midi_note(buffer, 76, 0.24f);
	mao_test::add_midi_note(buffer, 82, 0.13f);

	const auto snapshot = analyze_buffer(buffer, "full mix");
	expect_label(runner, snapshot.bass.label, "C#2", "dense multi-instrument mix bass");
	expect_label(runner, snapshot.global_chord.label, "D", "dense multi-instrument mix global chord");
	for (int pitch_class : {2, 6, 9, 5, 10, 4}) {
		expect_global_pitch_class(runner, snapshot, pitch_class, "dense multi-instrument mix global");
	}
}

void check_live_mic_aux_stream_low_parts(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;

	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const std::vector<float> other_profile = {1.0f, 0.62f, 0.42f, 0.27f, 0.16f};

	int bass_hits = 0;
	int harmonic_hits = 0;
	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 18; ++frame) {
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
		mao_test::Buffer buffer = {};
		add_harmonic_note_at_offset(buffer, 35, 0.10f, bass_profile, sample_offset);
		for (int midi : {60, 64, 67})
			add_harmonic_note_at_offset(buffer, midi, 0.030f, key_profile, sample_offset);
		for (int midi : {54, 58, 62})
			add_harmonic_note_at_offset(buffer, midi, 0.028f, guitar_profile, sample_offset);
		add_harmonic_note_at_offset(buffer, 74, 0.13f, other_profile, sample_offset);
		add_harmonic_note_at_offset(buffer, 76, 0.10f, {1.0f, 0.04f, 0.015f}, sample_offset);

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		if (frame < 2)
			continue;
		if (std::strcmp(snapshot.bass.label, "B1") == 0)
			++bass_hits;
		if (snapshot_global_pitch_active(snapshot, 0) && snapshot_global_pitch_active(snapshot, 4) &&
		    snapshot_global_pitch_active(snapshot, 7) && snapshot_global_pitch_active(snapshot, 6) &&
		    snapshot_global_pitch_active(snapshot, 10) && snapshot_global_pitch_active(snapshot, 2))
			++harmonic_hits;
	}

	runner.expect(bass_hits >= 12,
		      "live Mic/Aux stream low parts: expected stable bass, got " + std::to_string(bass_hits) +
			      " frames, last `" + snapshot.bass.label + "`");
	runner.expect(harmonic_hits >= 12,
		      "live Mic/Aux stream low parts: expected stable global harmonic tones, got " +
			      std::to_string(harmonic_hits) + " frames, global `" + snapshot.global_chord.label + "`");
}

void check_soft_drum_transient_stream(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	mao_test::Buffer background = mao_test::make_midi_notes({60, 64, 67}, 0.030f);
	mao::AnalysisSnapshot snapshot = {};

	for (int i = 0; i < 6; ++i)
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer kick = background;
	add_decayed_sine(kick, 65.0f, 0.22f, 1500);
	add_decayed_sine(kick, 1100.0f, 0.20f, 520);
	snapshot = engine.analyze(kick.data(), kick.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "soft drum transient stream: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));

	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer snare = background;
	add_decayed_sine(snare, 190.0f, 0.11f, 1300);
	add_decayed_sine(snare, 1800.0f, 0.040f, 900);
	snapshot = engine.analyze(snare.data(), snare.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "soft drum transient stream: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " tom " +
			      std::to_string(snapshot.drums[mao::Tom].level));

	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer cymbal = background;
	add_decayed_sine(cymbal, 5200.0f, 0.035f, 1100);
	add_decayed_sine(cymbal, 7600.0f, 0.030f, 900);
	snapshot = engine.analyze(cymbal.data(), cymbal.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::HiHat].active || snapshot.drums[mao::Crash].active ||
			      snapshot.drums[mao::Ride].active,
		      "soft drum transient stream: expected cymbal active, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level));
}

void check_high_crash_probe_counts_as_high_energy(Runner &runner)
{
	mao_test::Buffer buffer = {};
	add_decayed_sine(buffer, 12500.0f, 0.18f, 1100);

	const auto snapshot = analyze_buffer(buffer, "Mic/Aux");
	runner.expect(snapshot.high_energy >= 0.85f,
		      "highest cymbal probe: expected high energy, got " +
			      std::to_string(snapshot.high_energy));
	runner.expect(snapshot.drums[mao::HiHat].active || snapshot.drums[mao::Crash].active ||
			      snapshot.drums[mao::Ride].active,
		      "highest cymbal probe: expected cymbal active, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level));
}

void check_upbeat_mix_drums_and_chords(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	const std::vector<float> bass_profile = {1.0f, 0.30f, 0.14f};
	const std::vector<float> key_profile = {1.0f, 0.16f, 0.08f};
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const std::vector<float> other_profile = {1.0f, 0.52f, 0.30f, 0.16f};

	auto make_background = [&](uint64_t sample_offset) {
		mao_test::Buffer buffer = {};
		add_harmonic_note_at_offset(buffer, 36, 0.20f, bass_profile, sample_offset);
		for (int midi : {60, 64, 67})
			add_harmonic_note_at_offset(buffer, midi, 0.105f, key_profile, sample_offset);
		for (int midi : {48, 52, 55, 60, 64})
			add_harmonic_note_at_offset(buffer, midi, 0.090f, guitar_profile, sample_offset);
		add_harmonic_note_at_offset(buffer, 76, 0.060f, other_profile, sample_offset);
		add_harmonic_note_at_offset(buffer, 79, 0.055f, other_profile, sample_offset);
		return buffer;
	};

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 10; ++frame) {
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
		mao_test::Buffer background = make_background(sample_offset);
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);
	}

	expect_label(runner, snapshot.global_chord.label, "C", "upbeat mix global chord before drums");

	mao_test::Buffer kick = make_background(10 * 2400);
	add_decayed_sine(kick, 65.0f, 0.14f, 1300);
	add_decayed_sine(kick, 90.0f, 0.11f, 900);
	add_decayed_sine(kick, 120.0f, 0.040f, 650);
	add_decayed_sine(kick, 1100.0f, 0.42f, 480);
	snapshot = engine.analyze(kick.data(), kick.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "upbeat mix drums: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level) + " rms " +
			      std::to_string(snapshot.rms) + " peak " + std::to_string(snapshot.peak) +
			      " low " + std::to_string(snapshot.low_energy));
	expect_label(runner, snapshot.global_chord.label, "C", "upbeat mix global chord with kick");

	for (int frame = 11; frame < 15; ++frame) {
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * 2400;
		mao_test::Buffer background = make_background(sample_offset);
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);
	}

	mao_test::Buffer snare = make_background(15 * 2400);
	add_decayed_sine(snare, 190.0f, 0.065f, 1300);
	add_decayed_sine(snare, 1800.0f, 0.030f, 900);
	snapshot = engine.analyze(snare.data(), snare.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "upbeat mix drums: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " tom " +
			      std::to_string(snapshot.drums[mao::Tom].level));
	expect_label(runner, snapshot.global_chord.label, "C", "upbeat mix global chord with snare");
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

mao_test::Buffer triad_buffer(int root_pitch_class, bool minor)
{
	const int root = midi_at_or_above(60, root_pitch_class);
	return mao_test::make_midi_notes({root, root + (minor ? 3 : 4), root + 7}, 0.34f);
}

mao::AnalysisSnapshot analyze_root_chord_loop(const std::vector<mao_test::Buffer> &progression, int cycles,
					     int repeats_per_chord)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	mao::AnalysisSnapshot snapshot = {};
	for (int cycle = 0; cycle < cycles; ++cycle) {
		for (const mao_test::Buffer &buffer : progression) {
			for (int repeat = 0; repeat < repeats_per_chord; ++repeat)
				snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		}
	}
	return snapshot;
}

void check_root_from_common_major_degrees(Runner &runner)
{
	const mao::AnalysisSnapshot one_four_five =
		analyze_root_chord_loop({triad_buffer(0, false), triad_buffer(5, false), triad_buffer(7, false)},
					10, 3);
	runner.expect(std::strcmp(one_four_five.root.label, "C") == 0,
		      std::string("root 1/4/5: expected C for C/F/G history, got `") +
			      one_four_five.root.label + "` candidates `" + one_four_five.root_candidates + "`");
	runner.expect(mao_test::contains(one_four_five.root_candidates, "C "),
		      std::string("root 1/4/5: expected C candidate, got `") +
			      one_four_five.root_candidates + "`");

	const mao::AnalysisSnapshot four_five_one =
		analyze_root_chord_loop({triad_buffer(0, false), triad_buffer(2, false), triad_buffer(7, false)},
					10, 3);
	runner.expect(std::strcmp(four_five_one.root.label, "G") == 0,
		      std::string("root 4/5/1: expected G for C/D/G history, got `") +
			      four_five_one.root.label + "` candidates `" + four_five_one.root_candidates + "`");
	runner.expect(mao_test::contains(four_five_one.root_candidates, "G "),
		      std::string("root 4/5/1: expected G candidate, got `") +
			      four_five_one.root_candidates + "`");
}

void check_root_from_chord_progression(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();

	const std::vector<mao_test::Buffer> progression = {
		triad_buffer(0, false),	triad_buffer(2, false), triad_buffer(9, true),
		triad_buffer(4, true),	triad_buffer(11, true), triad_buffer(6, true),
		triad_buffer(7, false),
	};

	mao::AnalysisSnapshot snapshot = {};
	for (int cycle = 0; cycle < 4; ++cycle) {
		for (const mao_test::Buffer &buffer : progression) {
			for (int repeat = 0; repeat < 3; ++repeat)
				snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "keyboard", 0);
		}
	}

	runner.expect(std::strcmp(snapshot.root.label, "G") == 0,
		      std::string("root progression: expected G for C D Am Em Bm F#m G history, got `") +
			      snapshot.root.label + "` candidates `" + snapshot.root_candidates + "`");
	runner.expect(mao_test::contains(snapshot.root_candidates, "G "),
		      std::string("root progression: expected G candidate, got `") + snapshot.root_candidates + "`");
}

void check_root_from_bass_degrees(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	const std::vector<mao_test::Buffer> bass_notes = {
		mao_test::make_midi_notes({bass_midi_for_pitch_class(7)}, 0.70f),
		mao_test::make_midi_notes({bass_midi_for_pitch_class(9)}, 0.70f),
		mao_test::make_midi_notes({bass_midi_for_pitch_class(2)}, 0.70f),
	};

	mao::AnalysisSnapshot snapshot = {};
	for (int cycle = 0; cycle < 10; ++cycle) {
		for (const mao_test::Buffer &buffer : bass_notes) {
			for (int repeat = 0; repeat < 2; ++repeat)
				snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "bass", 0);
		}
	}

	runner.expect(std::strcmp(snapshot.root.label, "D") == 0,
		      std::string("root bass degrees: expected D for D/G/A bass history, got `") +
			      snapshot.root.label + "` candidates `" + snapshot.root_candidates + "`");
	runner.expect(mao_test::contains(snapshot.root_candidates, "D "),
		      std::string("root bass degrees: expected D candidate, got `") + snapshot.root_candidates + "`");
}

void check_empty_input_resets_same_source_state(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 8; ++i)
		snapshot = engine.analyze(chord.data(), chord.size(), settings, "OBS MIX", 0);
	runner.expect(std::strcmp(snapshot.root.label, "C") == 0,
		      std::string("empty input reset: expected seeded root C, got `") + snapshot.root.label + "`");

	mao_test::Buffer kick = {};
	add_decayed_sine(kick, 65.0f, 0.85f, 1400);
	add_decayed_sine(kick, 1100.0f, 0.28f, 520);
	snapshot = engine.analyze(kick.data(), kick.size(), settings, "OBS MIX", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "empty input reset: expected seeded kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));

	(void)engine.analyze(nullptr, 0, settings, "OBS MIX", 0);
	mao_test::Buffer silence = {};
	snapshot = engine.analyze(silence.data(), silence.size(), settings, "OBS MIX", 0);
	expect_label(runner, snapshot.root.label, "--", "empty input reset root state");
	runner.expect(!snapshot.drums[mao::Kick].active,
		      "empty input reset: expected kick inactive after restart, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
}

void check_explicit_analysis_reset(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 8; ++i)
		snapshot = engine.analyze(chord.data(), chord.size(), settings, "SPEAKER MONITOR", 0);
	expect_label(runner, snapshot.global_chord.label, "C", "explicit reset seeded global chord");
	runner.expect(std::strcmp(snapshot.root.label, "C") == 0,
		      std::string("explicit reset: expected seeded root C, got `") + snapshot.root.label + "`");

	mao_test::Buffer kick = {};
	add_decayed_sine(kick, 65.0f, 0.85f, 1400);
	add_decayed_sine(kick, 1100.0f, 0.28f, 520);
	snapshot = engine.analyze(kick.data(), kick.size(), settings, "SPEAKER MONITOR", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "explicit reset: expected seeded kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));

	engine.reset();
	mao_test::Buffer silence = {};
	snapshot = engine.analyze(silence.data(), silence.size(), settings, "SPEAKER MONITOR", 0);
	expect_label(runner, snapshot.root.label, "--", "explicit reset root");
	expect_label(runner, snapshot.global_chord.label, "--", "explicit reset global chord");
	expect_empty_note_grid(runner, snapshot.keyboard_notes, "explicit reset keyboard notes");
	expect_empty_note_grid(runner, snapshot.guitar_notes, "explicit reset guitar notes");
	expect_empty_note_grid(runner, snapshot.ambiguous_notes, "explicit reset ambiguous notes");
	runner.expect(!snapshot.drums[mao::Kick].active,
		      "explicit reset: expected kick inactive, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
}

void check_source_and_sample_rate_changes_reset_state(Runner &runner)
{
	auto seed_full_mix = [](mao::AnalysisEngine &engine, const mao::AnalysisSettings &settings,
				const char *source) {
		const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
		mao::AnalysisSnapshot snapshot = {};
		for (int i = 0; i < 8; ++i)
			snapshot = engine.analyze(chord.data(), chord.size(), settings, source, 0);

		mao_test::Buffer kick = {};
		add_decayed_sine(kick, 65.0f, 0.85f, 1400);
		add_decayed_sine(kick, 1100.0f, 0.28f, 520);
		snapshot = engine.analyze(kick.data(), kick.size(), settings, source, 0);
		return snapshot;
	};
	auto expect_full_mix_reset = [&](const mao::AnalysisSnapshot &snapshot, const std::string &context) {
		expect_label(runner, snapshot.root.label, "--", context + " root");
		expect_label(runner, snapshot.global_chord.label, "--", context + " global chord");
		expect_empty_note_grid(runner, snapshot.bass_notes, context + " bass notes");
		expect_empty_note_grid(runner, snapshot.keyboard_notes, context + " keyboard notes");
		expect_empty_note_grid(runner, snapshot.guitar_notes, context + " guitar notes");
		expect_empty_note_grid(runner, snapshot.vocal_notes, context + " vocal notes");
		expect_empty_note_grid(runner, snapshot.other_notes, context + " other notes");
		expect_empty_note_grid(runner, snapshot.ambiguous_notes, context + " ambiguous notes");
		runner.expect(!snapshot.drums[mao::Kick].active,
			      context + ": expected kick inactive, level " +
				      std::to_string(snapshot.drums[mao::Kick].level));
	};

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;
		const mao::AnalysisSnapshot seeded = seed_full_mix(engine, settings, "OBS MIX");
		expect_label(runner, seeded.root.label, "C", "source-change reset seeded root");
		runner.expect(seeded.drums[mao::Kick].active,
			      "source-change reset: expected seeded kick active, level " +
				      std::to_string(seeded.drums[mao::Kick].level));

		const mao_test::Buffer silence = {};
		const mao::AnalysisSnapshot reset =
			engine.analyze(silence.data(), silence.size(), settings, "SPEAKER MONITOR", 0);
		expect_full_mix_reset(reset, "source-change reset");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;
		const mao::AnalysisSnapshot seeded = seed_full_mix(engine, settings, "OBS MIX");
		expect_label(runner, seeded.root.label, "C", "sample-rate reset seeded root");
		runner.expect(seeded.drums[mao::Kick].active,
			      "sample-rate reset: expected seeded kick active, level " +
				      std::to_string(seeded.drums[mao::Kick].level));

		settings.sample_rate = 44100;
		const mao_test::Buffer silence = {};
		const mao::AnalysisSnapshot reset =
			engine.analyze(silence.data(), silence.size(), settings, "OBS MIX", 0);
		expect_full_mix_reset(reset, "sample-rate reset");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::IsolatedKeyboard;
		settings.analysis_interval_seconds = 0.05f;
		const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
		mao::AnalysisSnapshot snapshot = {};
		for (int i = 0; i < 4; ++i)
			snapshot = engine.analyze(chord.data(), chord.size(), settings, "keyboard bus", 0);
		expect_chord_label_present(runner, snapshot.keyboard_chord.label, "C",
					   "sample-rate reset seeded keyboard chord");
		expect_pitch_class(runner, snapshot.keyboard_notes, 0, "sample-rate reset seeded keyboard notes");

		settings.sample_rate = 44100;
		const mao_test::Buffer silence = {};
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "keyboard bus", 0);
		expect_label(runner, snapshot.keyboard_chord.label, "--", "sample-rate reset keyboard chord");
		expect_empty_note_grid(runner, snapshot.keyboard_notes, "sample-rate reset keyboard notes");
	}
}

void check_input_mode_change_resets_state(Runner &runner)
{
	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::IsolatedKeyboard;
		settings.analysis_interval_seconds = 0.05f;
		const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
		mao::AnalysisSnapshot snapshot = {};
		for (int i = 0; i < 4; ++i)
			snapshot = engine.analyze(chord.data(), chord.size(), settings, "shared bus", 0);
		expect_chord_label_present(runner, snapshot.keyboard_chord.label, "C",
					   "input-mode reset seeded keyboard chord");
		expect_pitch_class(runner, snapshot.keyboard_notes, 0, "input-mode reset seeded keyboard notes");

		settings.input_mode = mao::AnalysisInputMode::FullMix;
		const mao_test::Buffer silence = {};
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "shared bus", 0);
		expect_label(runner, snapshot.keyboard_chord.label, "--", "input-mode reset keyboard chord");
		expect_label(runner, snapshot.global_chord.label, "--", "input-mode reset global chord");
		expect_empty_note_grid(runner, snapshot.keyboard_notes, "input-mode reset keyboard notes");
		expect_empty_note_grid(runner, snapshot.ambiguous_notes, "input-mode reset ambiguous notes");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;
		const mao_test::Buffer chord = mao_test::make_midi_notes({60, 64, 67}, 0.34f);
		mao::AnalysisSnapshot snapshot = {};
		for (int i = 0; i < 8; ++i)
			snapshot = engine.analyze(chord.data(), chord.size(), settings, "shared bus", 0);
		expect_label(runner, snapshot.global_chord.label, "C", "input-mode reset seeded global chord");

		settings.input_mode = mao::AnalysisInputMode::IsolatedGuitar;
		const mao_test::Buffer silence = {};
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "shared bus", 0);
		expect_label(runner, snapshot.global_chord.label, "--", "input-mode reset isolated global chord");
		expect_label(runner, snapshot.guitar_chord.label, "--", "input-mode reset isolated guitar chord");
		expect_empty_note_grid(runner, snapshot.guitar_notes, "input-mode reset isolated guitar notes");
		expect_empty_note_grid(runner, snapshot.ambiguous_notes, "input-mode reset isolated ambiguous notes");
	}
}

} // namespace

int main()
{
	Runner runner;
	check_bass_notes(runner);
	check_bass_octave_suppression(runner);
	check_full_mix_bass_conservative_switching(runner);
	check_vocal_notes(runner);
	check_harmonic_single_notes(runner);
	check_harmonic_chords(runner);
	check_extended_chords(runner);
	check_equivalent_chord_labels(runner);
	check_guitar_supported_extension_aliases(runner);
	check_quiet_note_rejection(runner);
	check_quiet_standalone_rejection(runner);
	check_note_level_fade(runner);
	check_sustained_note_envelope(runner);
	check_temporal_note_stability(runner);
	check_full_mix_tuning_hysteresis_uses_global_tracking(runner);
	check_temporal_chord_stability(runner);
	check_full_mix_global_chord_uses_analytical_tracking(runner);
	check_required_chord_transitions(runner);
	check_full_mix_global_chord_transitions(runner);
	check_chord_margin_and_simplification(runner);
	check_chord_evidence_separate_from_visual_fade(runner);
	check_low_level_mixed_notes(runner);
	check_melodic_sources_do_not_trigger_drums(runner);
	check_layered_midi_instrument_voices(runner);
	check_same_instrument_timbre_variants(runner);
	check_distorted_midi_guitar_timbre(runner);
	check_spillover_regressions(runner);
	check_high_full_mix_cluster_not_vocal_or_other(runner);
	check_full_mix_single_instrument_precision(runner);
	check_full_mix_single_owned_note_has_no_instrument_chord(runner);
	check_simultaneous_onset_group_rejects_vocal_spillover(runner);
	check_full_mix_vocal_requires_temporal_confirmation(runner);
	check_full_mix_midrange_vocal_recall(runner);
	check_full_mix_realistic_vocal_recall(runner);
	check_mixed_keyboard_guitar_note_bounds(runner);
	check_sparse_full_mix_other_requires_temporal_confirmation(runner);
	check_explicit_input_mode_and_bpm(runner);
	check_frontend_full_mix_equivalence(runner);
	check_urmp_real_piece_metadata_regressions(runner);
	check_slakh_style_multitrack_song_regressions(runner);
	check_public_multitrack_dataset_style_regressions(runner);
	check_drum_hit_with_melodic_mix(runner);
	check_detuned_note_tolerance(runner);
	check_complex_real_timbres_survive_tuning_wobble(runner);
	check_low_acoustic_piano_fundamental_survives_partial_dominance(runner);
	check_realistic_instrument_chords(runner);
	check_keyboard_hand_span_chords(runner);
	check_guitar_caged_voicings(runner);
	check_guitar_caged_mix_root_independence(runner);
	check_same_note_timbre_split(runner);
	check_ambiguous_same_note_full_mix_chord_ownership(runner);
	check_full_mix_global_chord_guides_root_with_inversion(runner);
	check_full_mix_keyboard_chord_ignores_bass_inversion(runner);
	check_other_source_hints(runner);
	check_note_sub_rows(runner);
	check_bass_pure_tone_stays_out_of_harmonic_rows(runner);
	check_full_mix_bass_harmonic_note_not_duplicated(runner);
	check_multi_instrument_mix(runner);
	check_low_level_full_instrument_mix(runner);
	check_bass_survives_low_mid_mix(runner);
	check_bass_pluck_does_not_trigger_kick(runner);
	check_low_level_mic_aux_parts(runner);
	check_dense_multi_instrument_mix(runner);
	check_live_mic_aux_stream_low_parts(runner);
	check_soft_drum_transient_stream(runner);
	check_high_crash_probe_counts_as_high_energy(runner);
	check_upbeat_mix_drums_and_chords(runner);
	check_root_candidates(runner);
	check_root_from_common_major_degrees(runner);
	check_root_from_chord_progression(runner);
	check_root_from_bass_degrees(runner);
	check_empty_input_resets_same_source_state(runner);
	check_explicit_analysis_reset(runner);
	check_source_and_sample_rate_changes_reset_state(runner);
	check_input_mode_change_resets_state(runner);

	if (runner.failures != 0) {
		std::fprintf(stderr, "analyzer_cases: %d/%d checks failed\n", runner.failures, runner.checks);
		return 1;
	}

	std::printf("analyzer_cases: %d checks passed\n", runner.checks);
	return 0;
}
