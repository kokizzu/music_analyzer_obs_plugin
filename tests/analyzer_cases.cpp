#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

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

void check_bass_notes(Runner &runner)
{
	for (int midi = 28; midi <= 52; ++midi) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, midi, 0.70f);
		const auto snapshot = analyze_buffer(buffer, "bass");
		expect_label(runner, snapshot.bass.label, mao_test::note_label(midi),
			     "bass note " + mao_test::note_label(midi));
	}
}

void check_vocal_notes(Runner &runner)
{
	for (int midi = 48; midi <= 72; ++midi) {
		mao_test::Buffer buffer = {};
		mao_test::add_midi_note(buffer, midi, 0.48f);
		const auto snapshot = analyze_buffer(buffer, "vocal");
		expect_label(runner, snapshot.vocal.label, mao_test::note_label(midi),
			     "vocal note " + mao_test::note_label(midi));
	}
}

struct HarmonicInstrument {
	const char *name = "";
	int base_midi = 60;
	int max_midi = 88;
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
		{"guitar", 60, 76, guitar_notes, guitar_chord},
		{"keyboard", 60, 88, keyboard_notes, keyboard_chord},
		{"other", 72, 96, other_notes, other_chord},
	};
	return kInstruments;
}

int root_for_template(const HarmonicInstrument &instrument, int pitch_class, int max_interval)
{
	int root = instrument.base_midi + pitch_class;
	while (root + max_interval > instrument.max_midi)
		root -= 12;
	return root;
}

void check_harmonic_single_notes(Runner &runner)
{
	for (const HarmonicInstrument &instrument : harmonic_instruments()) {
		for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
			const int midi = instrument.base_midi + pitch_class;
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
		{"sus2", {0, 2, 7}},
		{"sus4", {0, 5, 7}},
		{"7", {0, 4, 7, 10}},
		{"maj7", {0, 4, 7, 11}},
		{"m7", {0, 3, 7, 10}},
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
				expect_label(runner, instrument.chord(snapshot).label, expected_chord, context);
			}
		}
	}
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
	check_root_candidates(runner);

	if (runner.failures != 0) {
		std::fprintf(stderr, "analyzer_cases: %d/%d checks failed\n", runner.failures, runner.checks);
		return 1;
	}

	std::printf("analyzer_cases: %d checks passed\n", runner.checks);
	return 0;
}
