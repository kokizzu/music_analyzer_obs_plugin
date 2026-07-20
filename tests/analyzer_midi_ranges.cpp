#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

constexpr float kDefaultWindowSeconds = static_cast<float>(mao::kDefaultAnalysisWindowMs) / 1000.0f;

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

bool contains(const char *text, const char *needle)
{
	return text && needle && std::strstr(text, needle) != nullptr;
}

bool has_note_token(const char *text, const std::string &note)
{
	if (!text)
		return false;

	const char *cursor = text;
	while (*cursor) {
		while (*cursor == ' ')
			++cursor;
		const char *end = cursor;
		while (*end && *end != ' ')
			++end;
		if (static_cast<std::size_t>(end - cursor) == note.size() &&
		    std::strncmp(cursor, note.c_str(), note.size()) == 0)
			return true;
		cursor = end;
	}
	return false;
}

void expect_note_token(Runner &runner, const char *actual, int midi, const std::string &context)
{
	const std::string expected = mao_test::note_label(midi);
	runner.expect(has_note_token(actual, expected),
		      context + ": expected note `" + expected + "`, got `" + (actual ? actual : "") + "`");
}

void expect_label(Runner &runner, const char *actual, const std::string &expected, const std::string &context)
{
	runner.expect(actual && expected == actual,
		      context + ": expected `" + expected + "`, got `" + (actual ? actual : "") + "`");
}

bool grid_has_pitch_class(const mao::NoteGrid &grid, int midi)
{
	const int pitch_class = ((midi % 12) + 12) % 12;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return true;
	}
	return grid.cells[pitch_class].active;
}

void expect_grid_pitch(Runner &runner, const mao::NoteGrid &grid, int midi, const std::string &context)
{
	runner.expect(grid_has_pitch_class(grid, midi),
		      context + ": expected pitch class " + mao_test::note_name(midi) + " active");
}

bool snapshot_has_pitch_class(const mao::AnalysisSnapshot &snapshot, int midi)
{
	return grid_has_pitch_class(snapshot.ambiguous_notes, midi) ||
	       grid_has_pitch_class(snapshot.keyboard_notes, midi) ||
	       grid_has_pitch_class(snapshot.guitar_notes, midi) ||
	       grid_has_pitch_class(snapshot.vocal_notes, midi) ||
	       grid_has_pitch_class(snapshot.other_notes, midi);
}

const char *drum_name(std::size_t index)
{
	static constexpr const char *kNames[mao::kDrumCount] = {"kick", "snare", "hihat", "crash",
								"tom", "ride", "rim"};
	return index < mao::kDrumCount ? kNames[index] : "unknown";
}

std::string drum_debug_details(const mao::AnalysisSnapshot &snapshot)
{
	std::string text;
	for (std::size_t i = 0; i < mao::kDrumCount; ++i) {
		char part[160] = {};
		std::snprintf(part, sizeof(part),
			      "%s%s level=%.2f band=%.2f seg=%.2f shapeScore=%.2f trig=%.2f/%.2f shape=%d",
			      text.empty() ? "" : " | ", drum_name(i), snapshot.drums[i].level,
			      snapshot.drum_debug_bands[i], snapshot.drum_debug_segment_bands[i],
			      snapshot.drum_debug_shape_scores[i], snapshot.drum_debug_trigger_scores[i],
			      snapshot.drum_debug_trigger_thresholds[i],
			      snapshot.drum_debug_shape_supported[i] ? 1 : 0);
		text += part;
	}
	char tail[240] = {};
	std::snprintf(tail, sizeof(tail),
		      " | transient=%.2f onset=%.2f energy=%.2f/%.2f/%.2f body=%.2f/%.2f/%.2f crack=%.2f upperTom=%.2f bodyShape=%d",
		      snapshot.drum_debug_transient_ratio, snapshot.drum_debug_onset, snapshot.low_energy,
		      snapshot.mid_energy, snapshot.high_energy, snapshot.drum_debug_kick_body,
		      snapshot.drum_debug_snare_body, snapshot.drum_debug_tom_body,
		      snapshot.drum_debug_snare_crack, snapshot.drum_debug_upper_tom_body,
		      snapshot.drum_debug_body_shape);
	text += tail;
	return text;
}

void add_harmonic_note(mao_test::Buffer &buffer, int midi, float amp, const std::vector<float> &profile)
{
	const float base = mao_test::midi_frequency(midi);
	for (std::size_t harmonic = 0; harmonic < profile.size(); ++harmonic)
		mao_test::add_sine(buffer, base * static_cast<float>(harmonic + 1), amp * profile[harmonic]);
}

void add_decayed_sine(mao_test::Buffer &buffer, float freq, float amp, std::size_t samples)
{
	samples = std::min(samples, buffer.size());
	for (std::size_t i = 0; i < samples; ++i) {
		const float decay = 1.0f - static_cast<float>(i) / static_cast<float>(samples);
		buffer[i] += amp * decay *
			     std::sin(2.0f * mao_test::kPi * freq * static_cast<float>(i) /
				      mao_test::kSampleRate);
	}
}

mao::AnalysisSnapshot analyze_repeated(const mao_test::Buffer &buffer, const char *source_name,
				       mao::AnalysisInputMode mode = mao::AnalysisInputMode::Auto,
				       int frames = 3)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = kDefaultWindowSeconds;
	settings.input_mode = mode;

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < frames; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, source_name, 0);
	return snapshot;
}

void add_drum_for_midi(mao_test::Buffer &buffer, int midi)
{
	switch (midi) {
	case 35:
	case 36:
		add_decayed_sine(buffer, 65.0f, 0.82f, 1400);
		add_decayed_sine(buffer, 90.0f, 0.24f, 900);
		add_decayed_sine(buffer, 1100.0f, 0.30f, 520);
		break;
	case 37:
		add_decayed_sine(buffer, 650.0f, 0.18f, 420);
		add_decayed_sine(buffer, 1100.0f, 0.42f, 360);
		add_decayed_sine(buffer, 2200.0f, 0.20f, 320);
		break;
	case 38:
	case 40:
		add_decayed_sine(buffer, 190.0f, 0.30f, 1300);
		add_decayed_sine(buffer, 1100.0f, 0.16f, 620);
		add_decayed_sine(buffer, 1800.0f, 0.18f, 760);
		break;
	case 41:
	case 43:
		add_decayed_sine(buffer, 110.0f, 0.46f, 1500);
		add_decayed_sine(buffer, 160.0f, 0.28f, 1300);
		break;
	case 45:
	case 47:
		add_decayed_sine(buffer, 150.0f, 0.42f, 1300);
		add_decayed_sine(buffer, 220.0f, 0.24f, 1050);
		break;
	case 48:
	case 50:
		add_decayed_sine(buffer, 220.0f, 0.38f, 1100);
		add_decayed_sine(buffer, 300.0f, 0.20f, 900);
		break;
	case 42:
	case 44:
	case 46:
		add_decayed_sine(buffer, 5600.0f, 0.13f, 700);
		add_decayed_sine(buffer, 7600.0f, 0.16f, 820);
		add_decayed_sine(buffer, 9800.0f, 0.11f, 640);
		break;
	case 49:
	case 57:
		add_decayed_sine(buffer, 5600.0f, 0.10f, 1100);
		add_decayed_sine(buffer, 7600.0f, 0.17f, 1350);
		add_decayed_sine(buffer, 9800.0f, 0.16f, 1450);
		add_decayed_sine(buffer, 12500.0f, 0.10f, 1200);
		break;
	case 51:
	case 53:
	case 59:
		add_decayed_sine(buffer, 3600.0f, 0.14f, 1000);
		add_decayed_sine(buffer, 5600.0f, 0.16f, 1250);
		add_decayed_sine(buffer, 7600.0f, 0.10f, 1100);
		break;
	default:
		break;
	}
}

mao::DrumIndex drum_category_for_midi(int midi)
{
	switch (midi) {
	case 35:
	case 36:
		return mao::Kick;
	case 37:
		return mao::Rim;
	case 38:
	case 40:
		return mao::Snare;
	case 41:
	case 43:
	case 45:
	case 47:
	case 48:
	case 50:
		return mao::Tom;
	case 42:
	case 44:
	case 46:
		return mao::HiHat;
	case 49:
	case 57:
		return mao::Crash;
	case 51:
	case 53:
	case 59:
		return mao::Ride;
	default:
		return mao::Kick;
	}
}

void check_gm_drum_midi_notes(Runner &runner)
{
	const std::vector<int> drum_midis = {35, 36, 37, 38, 40, 41, 43, 45, 47, 48, 50,
					     42, 44, 46, 49, 57, 51, 53, 59};
	for (int midi : drum_midis) {
		mao_test::Buffer warmup = {};
		mao_test::add_midi_note(warmup, 60, 0.006f);
		mao_test::Buffer buffer = warmup;
		add_drum_for_midi(buffer, midi);
		const mao::AnalysisSnapshot snapshot = analyze_repeated(buffer, "GM drum kit", mao::AnalysisInputMode::FullMix, 3);
		const mao::DrumIndex expected = drum_category_for_midi(midi);
		runner.expect(snapshot.drums[expected].active,
			      "GM drum MIDI " + std::to_string(midi) + ": expected " +
				      snapshot.drums[expected].label + " active");
	}
}

struct InstrumentCase {
	const char *name = "";
	const char *source = "";
	const char *family = "";
	const std::vector<float> profile;
	const std::vector<int> midis;
	float amp = 0.34f;
	const mao::InstrumentState &(*state)(const mao::AnalysisSnapshot &) = nullptr;
	const mao::NoteGrid &(*grid)(const mao::AnalysisSnapshot &) = nullptr;
};

const mao::InstrumentState &bass_state(const mao::AnalysisSnapshot &snapshot) { return snapshot.bass; }
const mao::InstrumentState &keyboard_state(const mao::AnalysisSnapshot &snapshot) { return snapshot.keyboard; }
const mao::InstrumentState &guitar_state(const mao::AnalysisSnapshot &snapshot) { return snapshot.guitar; }
const mao::InstrumentState &vocal_state(const mao::AnalysisSnapshot &snapshot) { return snapshot.vocal; }
const mao::InstrumentState &other_state(const mao::AnalysisSnapshot &snapshot) { return snapshot.other; }

const mao::NoteGrid &keyboard_grid(const mao::AnalysisSnapshot &snapshot) { return snapshot.keyboard_notes; }
const mao::NoteGrid &guitar_grid(const mao::AnalysisSnapshot &snapshot) { return snapshot.guitar_notes; }
const mao::NoteGrid &vocal_grid(const mao::AnalysisSnapshot &snapshot) { return snapshot.vocal_notes; }
const mao::NoteGrid &other_grid(const mao::AnalysisSnapshot &snapshot) { return snapshot.other_notes; }

void check_instrument_midi_ranges(Runner &runner)
{
	const std::vector<InstrumentCase> cases = {
		{"bass", "bass", "bass", {1.0f, 0.30f, 0.14f}, {28, 35, 40, 47, 52, 59}, 0.60f,
		 bass_state, nullptr},
		{"piano", "piano", "keyboard", {1.0f, 0.14f, 0.06f, 0.025f}, {21, 36, 48, 60, 72, 84, 96},
		 0.42f, keyboard_state, keyboard_grid},
		{"electric piano", "keys", "keyboard", {1.0f, 0.08f, 0.04f}, {36, 48, 60, 72, 84, 96},
		 0.40f, keyboard_state, keyboard_grid},
		{"clean guitar", "guitar", "guitar", {1.0f, 0.34f, 0.16f, 0.08f}, {40, 45, 52, 59, 64, 71, 76, 83},
		 0.38f, guitar_state, guitar_grid},
		{"distorted guitar", "guitar", "guitar", {1.0f, 0.55f, 0.34f, 0.20f, 0.12f},
		 {40, 47, 52, 59, 64, 71, 76}, 0.34f, guitar_state, guitar_grid},
		{"synth", "synth", "other", {1.0f, 0.62f, 0.42f, 0.27f, 0.16f}, {36, 48, 60, 72, 84},
		 0.34f, other_state, other_grid},
		{"strings", "strings", "other", {1.0f, 0.50f, 0.30f, 0.18f}, {43, 55, 67, 79, 91},
		 0.34f, other_state, other_grid},
		{"vocal", "vocal", "vocal", {1.0f, 0.10f, 0.04f}, {48, 53, 60, 67, 72, 79, 84},
		 0.42f, vocal_state, vocal_grid},
	};

	for (const InstrumentCase &test_case : cases) {
		for (int midi : test_case.midis) {
			mao_test::Buffer buffer = {};
			add_harmonic_note(buffer, midi, test_case.amp, test_case.profile);
			const mao::AnalysisSnapshot snapshot = analyze_repeated(buffer, test_case.source);
			const std::string context = std::string("MIDI ") + test_case.name + " " +
						    mao_test::note_label(midi);
			if (std::strcmp(test_case.family, "bass") == 0) {
				expect_label(runner, test_case.state(snapshot).label, mao_test::note_label(midi), context);
			} else {
				expect_note_token(runner, test_case.state(snapshot).label, midi, context);
				expect_grid_pitch(runner, test_case.grid(snapshot), midi, context);
			}
		}
	}
}

void check_combined_midi_arrangement(Runner &runner)
{
	auto make_bed = [] {
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 36, 0.17f, {1.0f, 0.30f, 0.14f});
		for (int midi : {60, 64, 67})
			add_harmonic_note(buffer, midi, 0.11f, {1.0f, 0.14f, 0.06f});
		for (int midi : {52, 55, 59})
			add_harmonic_note(buffer, midi, midi == 59 ? 0.13f : 0.095f,
					  {1.0f, 0.34f, 0.16f, 0.08f});
		for (int midi : {72, 76})
			add_harmonic_note(buffer, midi, 0.060f, {1.0f, 0.62f, 0.42f, 0.27f});
		add_harmonic_note(buffer, 69, 0.11f, {1.0f, 0.10f, 0.04f});
		return buffer;
	};

	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = kDefaultWindowSeconds;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 4; ++i) {
		const mao_test::Buffer bed = make_bed();
		snapshot = engine.analyze(bed.data(), bed.size(), settings, "Mic/Aux", 0);
	}

	mao_test::Buffer hit = make_bed();
	add_drum_for_midi(hit, 36);
	add_drum_for_midi(hit, 38);
	add_drum_for_midi(hit, 42);
	snapshot = engine.analyze(hit.data(), hit.size(), settings, "Mic/Aux", 0);

	expect_label(runner, snapshot.bass.label, "C2", "combined MIDI arrangement bass");
	for (int midi : {60, 64, 67, 52, 55, 59, 69, 72, 76})
		runner.expect(snapshot_has_pitch_class(snapshot, midi),
			      "combined MIDI arrangement: expected pitch class " +
				      std::string(mao_test::note_name(midi)) + " active");
	const std::string drum_debug = drum_debug_details(snapshot);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "combined MIDI arrangement: expected kick active; " + drum_debug);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "combined MIDI arrangement: expected snare active; " + drum_debug);
	runner.expect(snapshot.drums[mao::HiHat].active || snapshot.drums[mao::Crash].active ||
			      snapshot.drums[mao::Ride].active,
		      "combined MIDI arrangement: expected cymbal lane active, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level) + "; " + drum_debug);
	runner.expect(contains(snapshot.global_chord.label, "C") || contains(snapshot.global_chord.label, "Em"),
		      std::string("combined MIDI arrangement: expected C/Em-family chord, got `") +
			      snapshot.global_chord.label + "`");
}

} // namespace

int main()
{
	Runner runner;
	check_gm_drum_midi_notes(runner);
	check_instrument_midi_ranges(runner);
	check_combined_midi_arrangement(runner);

	if (runner.failures) {
		std::fprintf(stderr, "analyzer_midi_ranges: %d/%d checks failed\n", runner.failures, runner.checks);
		return 1;
	}
	std::printf("analyzer_midi_ranges: %d checks passed\n", runner.checks);
	return 0;
}
