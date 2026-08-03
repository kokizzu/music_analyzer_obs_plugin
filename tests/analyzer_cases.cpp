#include "analyzer.hpp"
#include "analyzer_test_utils.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <sstream>
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

mao::AnalysisSnapshot analyze_buffer_with_mode_window(const mao_test::Buffer &buffer,
						      mao::AnalysisInputMode input_mode,
						      const char *source,
						      float window_seconds, int frames = 4)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = input_mode;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_samples = 0;
	settings.analysis_window_seconds = window_seconds;
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

int test_chord_label_component_count(const char *actual)
{
	if (!actual || !actual[0] || std::strcmp(actual, "--") == 0)
		return 0;

	int count = 1;
	for (const char *cursor = actual; *cursor; ++cursor) {
		if (*cursor == '=')
			++count;
	}
	return count;
}

bool chord_primary_label_is(const char *actual, const std::string &expected)
{
	if (!actual)
		return false;
	const char *end = std::strchr(actual, '=');
	const std::size_t len = end ? static_cast<std::size_t>(end - actual) : std::strlen(actual);
	return len == expected.size() && std::strncmp(actual, expected.c_str(), expected.size()) == 0;
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

void add_tempo_kick(mao_test::Buffer &buffer, float scale = 1.0f)
{
	add_decayed_sine(buffer, 65.0f, 0.78f * scale, 1500);
	add_decayed_sine(buffer, 90.0f, 0.22f * scale, 1100);
	add_decayed_sine(buffer, 1100.0f, 0.26f * scale, 520);
}

void add_tempo_snare(mao_test::Buffer &buffer, float scale = 1.0f)
{
	add_decayed_sine(buffer, 170.0f, 0.16f * scale, 1300);
	add_decayed_sine(buffer, 650.0f, 0.065f * scale, 760);
	add_decayed_sine(buffer, 1800.0f, 0.16f * scale, 620);
	add_decayed_sine(buffer, 3600.0f, 0.055f * scale, 460);
}

void add_tempo_hihat(mao_test::Buffer &buffer, float scale = 1.0f)
{
	add_decayed_sine(buffer, 5600.0f, 0.070f * scale, 900);
	add_decayed_sine(buffer, 7600.0f, 0.090f * scale, 820);
	add_decayed_sine(buffer, 9800.0f, 0.065f * scale, 620);
}

void add_tempo_fill(mao_test::Buffer &buffer)
{
	add_decayed_sine(buffer, 140.0f, 0.20f, 1200);
	add_decayed_sine(buffer, 220.0f, 0.16f, 1000);
	add_decayed_sine(buffer, 3600.0f, 0.16f, 580);
	add_decayed_sine(buffer, 7600.0f, 0.18f, 560);
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

void add_tempo_backing(mao_test::Buffer &buffer, uint64_t sample_offset)
{
	add_harmonic_note_at_offset(buffer, 48, 0.0050f, {1.0f, 0.16f}, sample_offset);
	add_harmonic_note_at_offset(buffer, 55, 0.0038f, {1.0f, 0.12f}, sample_offset);
}

void add_tempo_tonal_pulse(mao_test::Buffer &buffer, uint64_t sample_offset, float scale = 1.0f)
{
	add_harmonic_note_at_offset(buffer, 48, 0.050f * scale, {1.0f, 0.22f, 0.08f}, sample_offset);
	add_harmonic_note_at_offset(buffer, 55, 0.043f * scale, {1.0f, 0.18f, 0.06f}, sample_offset);
	add_harmonic_note_at_offset(buffer, 64, 0.026f * scale, {1.0f, 0.14f}, sample_offset);
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

int grid_primary_midi_for_pitch(const mao::NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			return row[pitch_class].midi;
	}
	return -1;
}

std::string note_grid_pitch_classes(const mao::NoteGrid &grid)
{
	std::string out;
	for (int pitch_class = 0; pitch_class < 12; ++pitch_class) {
		if (!grid_pitch_active(grid, pitch_class))
			continue;
		if (!out.empty())
			out += ",";
		out += mao_test::note_name(pitch_class);
	}
	return out.empty() ? "--" : out;
}

std::string note_grid_active_labels(const mao::NoteGrid &grid)
{
	std::string out;
	char level[24];
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (!cell.active)
				continue;
			if (!out.empty())
				out += ",";
			std::snprintf(level, sizeof(level), "%.3f", cell.level);
			out += cell.label;
			out += "/";
			out += std::to_string(cell.midi);
			out += "=";
			out += level;
		}
	}
	return out.empty() ? "--" : out;
}

float note_grid_pitch_level(const mao::NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	float level = 0.0f;
	if (grid.cells[pitch_class].active)
		level = std::max(level, grid.cells[pitch_class].level);
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max(level, row[pitch_class].level);
	}
	return level;
}

float note_grid_pitch_visual_level(const mao::NoteGrid &grid, int pitch_class)
{
	pitch_class = ((pitch_class % 12) + 12) % 12;
	auto visual_level = [](const mao::NoteCell &cell) {
		return cell.visual_level >= 0.0f ? cell.visual_level : cell.level;
	};

	float level = 0.0f;
	if (grid.cells[pitch_class].active)
		level = std::max(level, visual_level(grid.cells[pitch_class]));
	for (const auto &row : grid.rows) {
		if (row[pitch_class].active)
			level = std::max(level, visual_level(row[pitch_class]));
	}
	return level;
}

std::string pitch_level_list(const mao::NoteGrid &grid, const std::vector<int> &pitch_classes)
{
	std::string out;
	char value[32];
	for (int pitch_class : pitch_classes) {
		if (!out.empty())
			out += ",";
		std::snprintf(value, sizeof(value), "%s=%.3f", mao_test::note_name(pitch_class),
			      note_grid_pitch_level(grid, pitch_class));
		out += value;
	}
	return out;
}

std::string pitch_level_list(const std::array<float, 12> &levels, const std::vector<int> &pitch_classes)
{
	std::string out;
	char value[32];
	for (int pitch_class : pitch_classes) {
		pitch_class = ((pitch_class % 12) + 12) % 12;
		if (!out.empty())
			out += ",";
		std::snprintf(value, sizeof(value), "%s=%.6f", mao_test::note_name(pitch_class),
			      levels[static_cast<std::size_t>(pitch_class)]);
		out += value;
	}
	return out;
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
	static constexpr float kConfidentOwnerLevel = 0.24f;
	auto grid_has_midi = [midi](const mao::NoteGrid &grid) {
		for (const auto &row : grid.rows) {
			for (const mao::NoteCell &cell : row) {
				if (cell.active && cell.midi == midi && cell.level >= kConfidentOwnerLevel)
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
	static constexpr float kConfidentOwnerLevel = 0.24f;
	auto grid_has_midi = [midi](const mao::NoteGrid &grid) {
		for (const auto &row : grid.rows) {
			for (const mao::NoteCell &cell : row) {
				if (cell.active && cell.midi == midi && cell.level >= kConfidentOwnerLevel)
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

std::string full_mix_debug_summary_for_midi(const mao::AnalysisSnapshot &snapshot, int midi);

void expect_midi_not_duplicated_across_rows(Runner &runner, const mao::AnalysisSnapshot &snapshot, int midi,
					    const std::string &context)
{
	const int count = full_mix_owned_midi_count(snapshot, midi);
	runner.expect(count <= 1, context + ": expected " + mao_test::note_label(midi) +
				   " in at most one confident row, got " + std::to_string(count) +
				   " labels keys=`" + snapshot.keyboard.label + "` guitar=`" +
				   snapshot.guitar.label + "` vocal=`" + snapshot.vocal.label +
				   "` other=`" + snapshot.other.label + "` debug `" +
				   full_mix_debug_summary_for_midi(snapshot, midi) + "`");
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
	runner.expect(!grid_has_any_active(grid),
		      context + ": expected no active notes, got `" + note_grid_active_labels(grid) + "`");
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

float grid_visual_level_for_midi(const mao::NoteGrid &grid, int midi)
{
	auto visual_level = [](const mao::NoteCell &cell) {
		return cell.visual_level >= 0.0f ? cell.visual_level : cell.level;
	};

	float level = 0.0f;
	for (const auto &row : grid.rows) {
		for (const mao::NoteCell &cell : row) {
			if (cell.active && cell.midi == midi)
				level = std::max(level, visual_level(cell));
		}
	}
	return level;
}

const char *instrument_kind_name(mao::InstrumentKind kind)
{
	switch (kind) {
	case mao::InstrumentKind::Bass:
		return "bass";
	case mao::InstrumentKind::Guitar:
		return "guitar";
	case mao::InstrumentKind::Keyboard:
		return "keys";
	case mao::InstrumentKind::Vocal:
		return "vocal";
	case mao::InstrumentKind::Other:
		return "other";
	case mao::InstrumentKind::Ambiguous:
	default:
		return "amb";
	}
}

const mao::FullMixDebugCandidate *debug_candidate_for_midi(const mao::AnalysisSnapshot &snapshot, int midi)
{
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (debug.midi == midi)
			return &debug;
	}
	return nullptr;
}

std::string full_mix_debug_summary_for_midi(const mao::AnalysisSnapshot &snapshot, int midi)
{
	std::ostringstream out;
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (debug.midi != midi)
			continue;
		if (out.tellp() > 0)
			out << "; ";
		out << instrument_kind_name(debug.owner) << " conf=" << debug.ownership_confidence
		    << " kgo=" << debug.keyboard_score << "," << debug.guitar_score << ","
		    << debug.vocal_score << "," << debug.other_score
		    << " spec=" << debug.spectral_level << " pitch=" << debug.pitch_confidence
		    << " per=" << debug.periodicity << " fit=" << debug.harmonic_fit_error
		    << " cent=" << debug.spectral_centroid << " slope=" << debug.spectral_slope
		    << " noise=" << debug.local_noise_level << " adj=" << debug.adjacent_lower_ratio
		    << "," << debug.adjacent_upper_ratio << " third=" << debug.third_octave_ratio
		    << " partials="
		    << debug.harmonic_ratios[1] << "," << debug.harmonic_ratios[2] << ","
		    << debug.harmonic_ratios[3] << "," << debug.harmonic_ratios[4];
	}
	return out.str();
}

void expect_midi_in_keyboard_guitar_other(Runner &runner, const mao::AnalysisSnapshot &snapshot, int midi,
					  const std::string &context)
{
	const float keyboard = grid_level_for_midi(snapshot.keyboard_notes, midi);
	const float guitar = grid_level_for_midi(snapshot.guitar_notes, midi);
	const float other = grid_level_for_midi(snapshot.other_notes, midi);
	const float ambiguous = grid_level_for_midi(snapshot.ambiguous_notes, midi);
	const std::string detail = " levels keys=" + std::to_string(keyboard) +
				   " guitar=" + std::to_string(guitar) + " other=" +
				   std::to_string(other) + " amb=" + std::to_string(ambiguous) +
				   " debug `" + full_mix_debug_summary_for_midi(snapshot, midi) + "`";
	runner.expect(keyboard > 0.0f,
		      context + ": expected " + mao_test::note_label(midi) + " in keys," + detail);
	runner.expect(guitar > 0.0f,
		      context + ": expected " + mao_test::note_label(midi) + " in guitar," + detail);
	runner.expect(other > 0.0f,
		      context + ": expected " + mao_test::note_label(midi) + " in other," + detail);
}

std::string full_mix_debug_summary(const mao::AnalysisSnapshot &snapshot)
{
	std::ostringstream out;
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (out.tellp() > 0)
			out << "; ";
		out << mao_test::note_label(debug.midi) << ":" << instrument_kind_name(debug.owner)
		    << " conf=" << debug.ownership_confidence << " kgo=" << debug.keyboard_score << ","
		    << debug.guitar_score << "," << debug.vocal_score << "," << debug.other_score
		    << " spec=" << debug.spectral_level;
	}
	return out.str();
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

void check_isolated_bass_periodic_fundamental_rescue(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> picked_bass_profile = {0.34f, 0.58f, 1.0f, 0.64f, 0.26f};
	add_harmonic_note(buffer, 38, 0.24f, picked_bass_profile);
	const auto snapshot = analyze_buffer_with_mode_window(buffer, mao::AnalysisInputMode::IsolatedBass,
							      "bass", 0.10f);
	expect_label(runner, snapshot.bass.label, "D2", "isolated picked bass periodic fundamental");
}

void check_isolated_bass_upper_note_not_third_partial_alias(Runner &runner)
{
	mao_test::Buffer buffer = {};
	mao_test::add_midi_note(buffer, 29, 0.06f);
	mao_test::add_midi_note(buffer, 48, 0.36f);
	mao_test::add_midi_note(buffer, 60, 0.18f);
	const auto snapshot = analyze_buffer_with_mode_window(buffer, mao::AnalysisInputMode::IsolatedBass,
							      "idmt-bass-lines", 0.10f);
	expect_label(runner, snapshot.bass.label, "C3", "isolated bass upper note third-partial alias");
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
	runner.expect(std::strcmp(snapshot.bass.label, "E2") == 0,
		      std::string("full-mix bass switching confirmed: expected E2, got `") +
			      snapshot.bass.label + "` guitar `" + snapshot.guitar.label +
			      "` debug E2 `" + full_mix_debug_summary_for_midi(snapshot, 40) + "`");
}

void check_full_mix_electronic_bass_visual_floor(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> octave_dominant_bass_profile = {0.76f, 1.0f, 0.98f, 0.76f, 0.16f, 0.13f};
	add_harmonic_note(buffer, 35, 0.22f, octave_dominant_bass_profile);

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);

	const float bass_level = grid_visual_level_for_midi(snapshot.bass_notes, 35);
	const float keyboard_level = grid_visual_level_for_midi(snapshot.keyboard_notes, 35);
	expect_label(runner, snapshot.bass.label, "B1", "full-mix electronic bass visual floor note");
	runner.expect(bass_level >= 0.90f,
		      "full-mix electronic bass visual floor: expected bright B1 bass, got " +
			      std::to_string(bass_level) + " bass notes `" +
			      note_grid_active_labels(snapshot.bass_notes) + "` keyboard `" +
			      note_grid_active_labels(snapshot.keyboard_notes) + "` debug B2 `" +
			      full_mix_debug_summary_for_midi(snapshot, 47) + "`");
	runner.expect(bass_level >= keyboard_level,
		      "full-mix electronic bass visual floor: expected bass at least as bright as keyboard mirror, got bass " +
			      std::to_string(bass_level) + " keyboard " + std::to_string(keyboard_level));
}

void check_full_mix_low_electronic_bass_visual_floor(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> low_octave_bass_profile = {0.32f, 1.0f, 0.42f, 0.060f, 0.012f, 0.004f};
	add_harmonic_note(buffer, 31, 0.24f, low_octave_bass_profile);

	mao::AnalysisSnapshot snapshot = {};
	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);

	const float bass_level = grid_visual_level_for_midi(snapshot.bass_notes, 31);
	const float keyboard_level = grid_visual_level_for_midi(snapshot.keyboard_notes, 31);
	expect_label(runner, snapshot.bass.label, "G1", "full-mix low electronic bass visual floor note");
	runner.expect(bass_level >= 0.90f,
		      "full-mix low electronic bass visual floor: expected bright G1 bass, got " +
			      std::to_string(bass_level) + " bass notes `" +
			      note_grid_active_labels(snapshot.bass_notes) + "` keyboard `" +
			      note_grid_active_labels(snapshot.keyboard_notes) + "` debug G2 `" +
			      full_mix_debug_summary_for_midi(snapshot, 43) + "`");
	runner.expect(bass_level >= keyboard_level,
		      "full-mix low electronic bass visual floor: expected bass at least as bright as keyboard mirror, got bass " +
			      std::to_string(bass_level) + " keyboard " + std::to_string(keyboard_level));
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
				if (std::strcmp(instrument.name, "guitar") == 0) {
					runner.expect(has_chord_label(instrument.chord(snapshot).label, expected_chord),
						      context + ": expected chord label `" + expected_chord +
							      "`, got `" + instrument.chord(snapshot).label + "`");
				} else {
					expect_label(runner, instrument.chord(snapshot).label, expected_chord, context);
				}
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

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
		add_harmonic_note(buffer, 48, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 51, 0.12f, guitar_profile);
		add_harmonic_note(buffer, 55, 0.19f, guitar_profile);
		add_harmonic_note(buffer, 47, 0.13f, guitar_profile);

		const auto snapshot = analyze_buffer(buffer, "guitar");
		const std::string context = "equivalent noisy guitar Cm triad";
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "Cm"),
			      context + ": expected Cm alias, got `" + snapshot.guitar_chord.label + "`");
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
	runner.expect(chord_primary_label_is(snapshot.guitar_chord.label, "C"),
		      std::string("guitar weak extension primary: expected C primary, got `") +
			      snapshot.guitar_chord.label + "`");

	mao_test::Buffer low_core_buffer = {};
	for (int midi : {48, 55})
		add_harmonic_note(low_core_buffer, midi, 0.20f, guitar_profile);
	for (int midi : {52, 59})
		add_harmonic_note(low_core_buffer, midi, 0.11f, guitar_profile);

	const auto low_core_snapshot = analyze_buffer(low_core_buffer, "guitar");
	runner.expect(has_chord_label(low_core_snapshot.guitar_chord.label, "Cmaj7"),
		      std::string("guitar low-core extension aliases: expected Cmaj7 alias, got `") +
			      low_core_snapshot.guitar_chord.label + "`");

	mao_test::Buffer low_root_minor_seventh = {};
	add_harmonic_note(low_root_minor_seventh, 49, 0.075f, guitar_profile);
	for (int midi : {52, 56, 59})
		add_harmonic_note(low_root_minor_seventh, midi, 0.16f, guitar_profile);

	const auto low_root_minor_seventh_snapshot = analyze_buffer(low_root_minor_seventh, "guitar");
	runner.expect(has_chord_label(low_root_minor_seventh_snapshot.guitar_chord.label, "C#m7"),
		      std::string("guitar low-root extension aliases: expected C#m7 alias, got `") +
			      low_root_minor_seventh_snapshot.guitar_chord.label + "`");

	mao_test::Buffer diminished_with_seventh = {};
	for (int midi : {57, 60, 63})
		add_harmonic_note(diminished_with_seventh, midi, 0.22f, guitar_profile);
	add_harmonic_note(diminished_with_seventh, 67, 0.10f, guitar_profile);

	const auto diminished_with_seventh_snapshot = analyze_buffer(diminished_with_seventh, "guitar");
	runner.expect(has_chord_label(diminished_with_seventh_snapshot.guitar_chord.label, "Adim"),
		      std::string("guitar diminished triad alias recovery: expected Adim, got `") +
			      diminished_with_seventh_snapshot.guitar_chord.label + "` raw `" +
			      diminished_with_seventh_snapshot.guitar_raw_chord.label + "` smooth `" +
			      diminished_with_seventh_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(diminished_with_seventh_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(
				      diminished_with_seventh_snapshot.guitar_chord_analysis_notes) +
			      "`");

	mao_test::Buffer ambiguous_root_extension = {};
	for (int midi : {45, 48, 52, 55, 59})
		add_harmonic_note(ambiguous_root_extension, midi, 0.18f, guitar_profile);

	const auto ambiguous_root_snapshot = analyze_buffer(ambiguous_root_extension, "guitar");
	runner.expect(has_chord_label(ambiguous_root_snapshot.guitar_chord.label, "Cmaj7"),
		      std::string("guitar related-root extension aliases: expected Cmaj7 alias, got `") +
			      ambiguous_root_snapshot.guitar_chord.label + "`");

	mao_test::Buffer moderate_third_major_seventh = {};
	add_harmonic_note(moderate_third_major_seventh, 50, 0.20f, guitar_profile);
	add_harmonic_note(moderate_third_major_seventh, 57, 0.30f, guitar_profile);
	add_harmonic_note(moderate_third_major_seventh, 61, 0.16f, guitar_profile);
	add_harmonic_note(moderate_third_major_seventh, 66, 0.075f, guitar_profile);

	const auto moderate_third_major_seventh_snapshot =
		analyze_buffer(moderate_third_major_seventh, "guitar");
	runner.expect(has_chord_label(moderate_third_major_seventh_snapshot.guitar_chord.label, "Dmaj7"),
		      std::string("guitar moderate-third major seventh alias: expected Dmaj7, got `") +
			      moderate_third_major_seventh_snapshot.guitar_chord.label + "`");

	mao_test::Buffer display_supported_major_seventh = {};
	for (int midi : {43, 50, 54, 55, 59})
		add_harmonic_note(display_supported_major_seventh, midi, 0.18f, guitar_profile);

	const auto display_supported_major_seventh_snapshot =
		analyze_buffer(display_supported_major_seventh, "guitar");
	runner.expect(has_chord_label(display_supported_major_seventh_snapshot.guitar_chord.label, "Gmaj7"),
		      std::string("guitar display-supported extension aliases: expected Gmaj7, got `") +
			      display_supported_major_seventh_snapshot.guitar_chord.label + "`");

	mao_test::Buffer probe_supported_major_seventh = {};
	add_harmonic_note(probe_supported_major_seventh, 48, 0.18f, guitar_profile);
	add_harmonic_note(probe_supported_major_seventh, 52, 0.19f, guitar_profile);
	add_harmonic_note(probe_supported_major_seventh, 55, 0.26f, guitar_profile);
	add_harmonic_note(probe_supported_major_seventh, 56, 0.095f, guitar_profile);
	add_harmonic_note(probe_supported_major_seventh, 59, 0.045f, guitar_profile);

	const auto probe_supported_major_seventh_snapshot =
		analyze_buffer(probe_supported_major_seventh, "guitar");
	runner.expect(
		has_chord_label(probe_supported_major_seventh_snapshot.guitar_chord.label, "Cmaj7"),
		std::string("guitar probe-supported extension aliases: expected Cmaj7, got `") +
			probe_supported_major_seventh_snapshot.guitar_chord.label + "` raw `" +
			probe_supported_major_seventh_snapshot.guitar_raw_chord.label + "` smooth `" +
			probe_supported_major_seventh_snapshot.guitar_smoothed_chord.label + "` analysis `" +
			note_grid_pitch_classes(
				probe_supported_major_seventh_snapshot.guitar_chord_analysis_notes) +
			"`");

	mao_test::Buffer extension_with_minor_spill = {};
	add_harmonic_note(extension_with_minor_spill, 45, 0.21f, guitar_profile);
	add_harmonic_note(extension_with_minor_spill, 49, 0.12f, guitar_profile);
	add_harmonic_note(extension_with_minor_spill, 52, 0.22f, guitar_profile);
	add_harmonic_note(extension_with_minor_spill, 56, 0.080f, guitar_profile);
	add_harmonic_note(extension_with_minor_spill, 48, 0.13f, guitar_profile);

	const auto extension_with_minor_spill_snapshot = analyze_buffer(extension_with_minor_spill, "guitar");
	runner.expect(has_chord_label(extension_with_minor_spill_snapshot.guitar_chord.label, "A"),
		      std::string("guitar extension base triad alias: expected A, got `") +
			      extension_with_minor_spill_snapshot.guitar_chord.label + "`");

	mao_test::Buffer lower_flat_seventh = {};
	add_harmonic_note(lower_flat_seventh, 50, 0.13f, guitar_profile);
	add_harmonic_note(lower_flat_seventh, 56, 0.24f, guitar_profile);
	add_harmonic_note(lower_flat_seventh, 59, 0.23f, guitar_profile);
	add_harmonic_note(lower_flat_seventh, 64, 0.14f, guitar_profile);

	const auto lower_flat_seventh_snapshot = analyze_buffer(lower_flat_seventh, "guitar");
	runner.expect(has_chord_label(lower_flat_seventh_snapshot.guitar_chord.label, "E7"),
		      std::string("guitar lower flat-seventh aliases: expected E7, got `") +
			      lower_flat_seventh_snapshot.guitar_chord.label + "`");

	mao_test::Buffer dominant_seventh_omitted_fifth = {};
	for (int midi : {52, 56, 62})
		add_harmonic_note(dominant_seventh_omitted_fifth, midi, 0.18f, guitar_profile);

	const auto dominant_seventh_omitted_fifth_snapshot =
		analyze_buffer(dominant_seventh_omitted_fifth, "guitar");
	runner.expect(has_chord_label(dominant_seventh_omitted_fifth_snapshot.guitar_chord.label, "E7"),
		      std::string("guitar omitted-fifth dominant seventh: expected E7, got `") +
			      dominant_seventh_omitted_fifth_snapshot.guitar_chord.label + "`");

	mao_test::Buffer minor_seventh_omitted_fifth = {};
	add_harmonic_note(minor_seventh_omitted_fifth, 45, 0.26f, guitar_profile);
	add_harmonic_note(minor_seventh_omitted_fifth, 48, 0.15f, guitar_profile);
	add_harmonic_note(minor_seventh_omitted_fifth, 55, 0.15f, guitar_profile);

	const auto minor_seventh_omitted_fifth_snapshot =
		analyze_buffer(minor_seventh_omitted_fifth, "guitar");
	runner.expect(has_chord_label(minor_seventh_omitted_fifth_snapshot.guitar_chord.label, "Am7"),
		      std::string("guitar omitted-fifth minor seventh: expected Am7, got `") +
			      minor_seventh_omitted_fifth_snapshot.guitar_chord.label + "` raw `" +
			      minor_seventh_omitted_fifth_snapshot.guitar_raw_chord.label + "` smooth `" +
			      minor_seventh_omitted_fifth_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(minor_seventh_omitted_fifth_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(
				      minor_seventh_omitted_fifth_snapshot.guitar_chord_analysis_notes) +
			      "`");

	mao_test::Buffer major_seventh_omitted_fifth = {};
	for (int midi : {48, 52, 59})
		add_harmonic_note(major_seventh_omitted_fifth, midi, 0.18f, guitar_profile);

	const auto major_seventh_omitted_fifth_snapshot =
		analyze_buffer(major_seventh_omitted_fifth, "guitar");
	runner.expect(has_chord_label(major_seventh_omitted_fifth_snapshot.guitar_chord.label, "Cmaj7"),
		      std::string("guitar omitted-fifth major seventh: expected Cmaj7, got `") +
			      major_seventh_omitted_fifth_snapshot.guitar_chord.label + "`");

	mao_test::Buffer suspended_with_weak_third = {};
	add_harmonic_note(suspended_with_weak_third, 45, 0.22f, guitar_profile);
	add_harmonic_note(suspended_with_weak_third, 50, 0.19f, guitar_profile);
	add_harmonic_note(suspended_with_weak_third, 52, 0.22f, guitar_profile);
	add_harmonic_note(suspended_with_weak_third, 49, 0.060f, guitar_profile);

	const auto suspended_with_weak_third_snapshot = analyze_buffer(suspended_with_weak_third, "guitar");
	runner.expect(has_chord_label(suspended_with_weak_third_snapshot.guitar_chord.label, "Asus4"),
		      std::string("guitar suspended alias with weak third: expected Asus4, got `") +
			      suspended_with_weak_third_snapshot.guitar_chord.label + "`");

	mao_test::Buffer noisy_power = {};
	add_harmonic_note(noisy_power, 48, 0.24f, guitar_profile);
	add_harmonic_note(noisy_power, 55, 0.22f, guitar_profile);
	add_harmonic_note(noisy_power, 50, 0.09f, guitar_profile);

	const auto noisy_power_snapshot = analyze_buffer(noisy_power, "guitar");
	runner.expect(has_chord_label(noisy_power_snapshot.guitar_chord.label, "Cpow"),
		      std::string("guitar noisy power aliases: expected Cpow alias, got `") +
			      noisy_power_snapshot.guitar_chord.label + "` raw `" +
			      noisy_power_snapshot.guitar_raw_chord.label + "` smooth `" +
			      noisy_power_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(noisy_power_snapshot.guitar_notes) + "` analysis `" +
			      note_grid_pitch_classes(noisy_power_snapshot.guitar_chord_analysis_notes) + "` levels `" +
			      pitch_level_list(noisy_power_snapshot.guitar_notes, {0, 3, 4, 7}) +
			      "` analysis-levels `" +
			      pitch_level_list(noisy_power_snapshot.guitar_chord_analysis_notes, {0, 3, 4, 7}) +
			      "` probe `" +
			      pitch_level_list(noisy_power_snapshot.guitar_chord_debug_probe_levels, {0, 3, 4, 7}) +
			      "` melodic `" +
			      pitch_level_list(noisy_power_snapshot.guitar_chord_debug_melodic_probe_levels,
					       {0, 3, 4, 7}) +
			      "`");

	mao_test::Buffer crowded_augmented_noise = {};
	for (int midi : {51, 52, 53, 55, 56, 57, 58, 59})
		add_harmonic_note(crowded_augmented_noise, midi, 0.16f, guitar_profile);

	const auto crowded_augmented_noise_snapshot = analyze_buffer(crowded_augmented_noise, "guitar");
	expect_no_chord_label(runner, crowded_augmented_noise_snapshot.guitar_chord.label, "D#aug",
			      "guitar crowded symmetric altered noise D#aug");
	expect_no_chord_label(runner, crowded_augmented_noise_snapshot.guitar_chord.label, "Gaug",
			      "guitar crowded symmetric altered noise Gaug");
	expect_no_chord_label(runner, crowded_augmented_noise_snapshot.guitar_chord.label, "Baug",
			      "guitar crowded symmetric altered noise Baug");
	runner.expect(test_chord_label_component_count(crowded_augmented_noise_snapshot.guitar_chord.label) <
			      7,
		      std::string("guitar crowded altered noise: expected compact label, got `") +
			      crowded_augmented_noise_snapshot.guitar_chord.label + "`");

	mao_test::Buffer thirdless_named_dyad = {};
	add_harmonic_note(thirdless_named_dyad, 48, 0.20f, guitar_profile);
	add_harmonic_note(thirdless_named_dyad, 55, 0.18f, guitar_profile);

	const auto thirdless_named_dyad_snapshot = analyze_buffer(thirdless_named_dyad, "guitar");
	runner.expect(has_chord_label(thirdless_named_dyad_snapshot.guitar_chord.label, "Cpow"),
		      std::string("guitar thirdless named dyad: expected Cpow, got `") +
			      thirdless_named_dyad_snapshot.guitar_chord.label + "` raw `" +
			      thirdless_named_dyad_snapshot.guitar_raw_chord.label + "` smooth `" +
			      thirdless_named_dyad_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(thirdless_named_dyad_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(thirdless_named_dyad_snapshot.guitar_chord_analysis_notes) +
			      "` levels `" +
			      pitch_level_list(thirdless_named_dyad_snapshot.guitar_notes, {0, 1, 3, 4, 7, 11}) +
			      "` analysis-levels `" +
			      pitch_level_list(thirdless_named_dyad_snapshot.guitar_chord_analysis_notes,
					       {0, 1, 3, 4, 7, 11}) +
			      "` probe `" +
			      pitch_level_list(thirdless_named_dyad_snapshot.guitar_chord_debug_probe_levels,
					       {0, 1, 3, 4, 7, 11}) +
			      "` melodic `" +
			      pitch_level_list(thirdless_named_dyad_snapshot.guitar_chord_debug_melodic_probe_levels,
					       {0, 1, 3, 4, 7, 11}) +
			      "`");

	mao_test::Buffer harmonic_single_note = {};
	const std::vector<float> strong_harmonic_guitar_profile = {1.0f, 0.82f, 0.55f, 0.36f, 0.04f};
	add_harmonic_note(harmonic_single_note, 52, 0.24f, strong_harmonic_guitar_profile);

	const auto harmonic_single_note_snapshot = analyze_buffer(harmonic_single_note, "guitar");
	expect_note_token(runner, harmonic_single_note_snapshot.guitar.label, "E3",
			  "guitar single-note harmonic chord rejection");
	expect_no_chord(runner, harmonic_single_note_snapshot.guitar_chord,
			std::string("guitar single-note harmonic chord rejection raw `") +
				harmonic_single_note_snapshot.guitar_raw_chord.label + "` smooth `" +
				harmonic_single_note_snapshot.guitar_smoothed_chord.label + "` notes `" +
				note_grid_pitch_classes(harmonic_single_note_snapshot.guitar_notes) +
				"` analysis `" +
				note_grid_pitch_classes(harmonic_single_note_snapshot.guitar_chord_analysis_notes) +
				"`");

	mao_test::Buffer weak_third_harmonic_single_note = {};
	const std::vector<float> weak_third_single_note_profile = {1.0f, 0.87f, 0.24f, 0.06f, 0.13f};
	add_harmonic_note(weak_third_harmonic_single_note, 54, 0.24f, weak_third_single_note_profile);

	const auto weak_third_harmonic_single_note_snapshot =
		analyze_buffer(weak_third_harmonic_single_note, "guitar");
	expect_note_token(runner, weak_third_harmonic_single_note_snapshot.guitar.label, "F#3",
			  "guitar weak-third single-note harmonic chord rejection");
	expect_no_chord(runner, weak_third_harmonic_single_note_snapshot.guitar_chord,
			std::string("guitar weak-third single-note harmonic chord rejection raw `") +
				weak_third_harmonic_single_note_snapshot.guitar_raw_chord.label +
				"` smooth `" +
				weak_third_harmonic_single_note_snapshot.guitar_smoothed_chord.label +
				"` notes `" +
				note_grid_pitch_classes(weak_third_harmonic_single_note_snapshot.guitar_notes) +
				"` analysis `" +
				note_grid_pitch_classes(
					weak_third_harmonic_single_note_snapshot
						.guitar_chord_analysis_notes) +
				"`");

	mao_test::Buffer distorted_root_residue_single_note = {};
	const std::vector<float> distorted_root_profile = {1.0f, 0.62f, 0.36f, 0.22f, 0.12f};
	add_harmonic_note(distorted_root_residue_single_note, 45, 0.54f, distorted_root_profile);
	add_harmonic_note(distorted_root_residue_single_note, 44, 0.22f, {1.0f, 0.24f});
	add_harmonic_note(distorted_root_residue_single_note, 46, 0.22f, {1.0f, 0.24f});

	const auto distorted_root_residue_snapshot =
		analyze_buffer(distorted_root_residue_single_note, "guitar");
	expect_note_token(runner, distorted_root_residue_snapshot.guitar.label, "A2",
			  "guitar distorted single-note root-residue rejection");
	expect_no_chord(runner, distorted_root_residue_snapshot.guitar_chord,
			std::string("guitar distorted single-note root-residue rejection raw `") +
				distorted_root_residue_snapshot.guitar_raw_chord.label + "` smooth `" +
				distorted_root_residue_snapshot.guitar_smoothed_chord.label + "` notes `" +
				note_grid_pitch_classes(distorted_root_residue_snapshot.guitar_notes) +
				"` analysis `" +
				note_grid_pitch_classes(
					distorted_root_residue_snapshot.guitar_chord_analysis_notes) +
				"`");

	mao_test::Buffer moderate_root_residue_single_note = {};
	add_harmonic_note(moderate_root_residue_single_note, 56, 0.46f, {1.0f, 0.05f, 0.74f, 0.05f});

	const auto moderate_root_residue_snapshot =
		analyze_buffer(moderate_root_residue_single_note, "guitar");
	expect_note_token(runner, moderate_root_residue_snapshot.guitar.label, "G#3",
			  "guitar moderate single-note root-residue rejection");
	expect_no_chord(runner, moderate_root_residue_snapshot.guitar_chord,
			std::string("guitar moderate single-note root-residue rejection raw `") +
				moderate_root_residue_snapshot.guitar_raw_chord.label + "` smooth `" +
				moderate_root_residue_snapshot.guitar_smoothed_chord.label + "` notes `" +
				note_grid_pitch_classes(moderate_root_residue_snapshot.guitar_notes) +
				"` analysis `" +
				note_grid_pitch_classes(
					moderate_root_residue_snapshot.guitar_chord_analysis_notes) +
				"`");

	mao_test::Buffer flanked_thirdless_named_dyad = {};
	add_harmonic_note(flanked_thirdless_named_dyad, 48, 0.22f, guitar_profile);
	add_harmonic_note(flanked_thirdless_named_dyad, 55, 0.20f, guitar_profile);
	add_harmonic_note(flanked_thirdless_named_dyad, 47, 0.050f, guitar_profile);
	add_harmonic_note(flanked_thirdless_named_dyad, 49, 0.050f, guitar_profile);

	const auto flanked_thirdless_named_dyad_snapshot =
		analyze_buffer(flanked_thirdless_named_dyad, "guitar");
	runner.expect(has_chord_label(flanked_thirdless_named_dyad_snapshot.guitar_chord.label, "Cpow"),
		      std::string("guitar root-flanked thirdless dyad: expected Cpow, got `") +
			      flanked_thirdless_named_dyad_snapshot.guitar_chord.label + "` raw `" +
			      flanked_thirdless_named_dyad_snapshot.guitar_raw_chord.label + "` smooth `" +
			      flanked_thirdless_named_dyad_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(flanked_thirdless_named_dyad_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(
				      flanked_thirdless_named_dyad_snapshot.guitar_chord_analysis_notes) +
			      "` levels `" +
			      pitch_level_list(flanked_thirdless_named_dyad_snapshot.guitar_notes,
					       {0, 1, 3, 4, 7, 11}) +
			      "`");
	expect_no_chord_label(runner, flanked_thirdless_named_dyad_snapshot.guitar_chord.label, "C",
			      std::string("guitar root-flanked thirdless dyad major alias probe `") +
				      pitch_level_list(
					      flanked_thirdless_named_dyad_snapshot.guitar_chord_debug_probe_levels,
					      {0, 1, 3, 4, 7, 11}) +
				      "` melodic `" +
				      pitch_level_list(
					      flanked_thirdless_named_dyad_snapshot
						      .guitar_chord_debug_melodic_probe_levels,
					      {0, 1, 3, 4, 7, 11}) +
				      "`");
	expect_no_chord_label(runner, flanked_thirdless_named_dyad_snapshot.guitar_chord.label, "Cm",
			      std::string("guitar root-flanked thirdless dyad minor alias probe `") +
				      pitch_level_list(
					      flanked_thirdless_named_dyad_snapshot.guitar_chord_debug_probe_levels,
					      {0, 1, 3, 4, 7, 11}) +
				      "` melodic `" +
				      pitch_level_list(
					      flanked_thirdless_named_dyad_snapshot
						      .guitar_chord_debug_melodic_probe_levels,
					      {0, 1, 3, 4, 7, 11}) +
				      "`");

	mao_test::Buffer full_triad = {};
	for (int midi : {48, 52, 55})
		add_harmonic_note(full_triad, midi, 0.24f, guitar_profile);

	const auto full_triad_snapshot = analyze_buffer(full_triad, "guitar");
	expect_no_chord_label(runner, full_triad_snapshot.guitar_chord.label, "Cpow",
			      "guitar power aliases full triad");

	mao_test::Buffer weak_third_triad = {};
	add_harmonic_note(weak_third_triad, 48, 0.24f, guitar_profile);
	add_harmonic_note(weak_third_triad, 52, 0.045f, guitar_profile);
	add_harmonic_note(weak_third_triad, 55, 0.22f, guitar_profile);

	const auto weak_third_snapshot = analyze_buffer(weak_third_triad, "guitar");
	runner.expect(has_chord_label(weak_third_snapshot.guitar_chord.label, "C"),
		      std::string("guitar weak-third triad aliases: expected C, got `") +
			      weak_third_snapshot.guitar_chord.label + "` raw `" +
			      weak_third_snapshot.guitar_raw_chord.label + "` smooth `" +
			      weak_third_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(weak_third_snapshot.guitar_notes) + "` analysis `" +
			      note_grid_pitch_classes(weak_third_snapshot.guitar_chord_analysis_notes) + "` levels `" +
			      pitch_level_list(weak_third_snapshot.guitar_notes, {0, 3, 4, 7}) +
			      "` analysis-levels `" +
			      pitch_level_list(weak_third_snapshot.guitar_chord_analysis_notes, {0, 3, 4, 7}) +
			      "` probe `" +
			      pitch_level_list(weak_third_snapshot.guitar_chord_debug_probe_levels, {0, 3, 4, 7}) +
			      "` melodic `" +
			      pitch_level_list(weak_third_snapshot.guitar_chord_debug_melodic_probe_levels,
					       {0, 3, 4, 7}) +
			      "`");
	expect_no_chord_label(runner, weak_third_snapshot.guitar_chord.label, "Cpow",
			      std::string("guitar weak-third triad power alias raw `") +
				      weak_third_snapshot.guitar_raw_chord.label + "` smooth `" +
				      weak_third_snapshot.guitar_smoothed_chord.label + "` notes `" +
				      note_grid_pitch_classes(weak_third_snapshot.guitar_notes) + "` analysis `" +
				      note_grid_pitch_classes(weak_third_snapshot.guitar_chord_analysis_notes) +
				      "` levels `" + pitch_level_list(weak_third_snapshot.guitar_notes, {0, 3, 4, 7}) +
				      "` analysis-levels `" +
				      pitch_level_list(weak_third_snapshot.guitar_chord_analysis_notes, {0, 3, 4, 7}) +
				      "` probe `" +
				      pitch_level_list(weak_third_snapshot.guitar_chord_debug_probe_levels, {0, 3, 4, 7}) +
				      "` melodic `" +
				      pitch_level_list(weak_third_snapshot.guitar_chord_debug_melodic_probe_levels,
						       {0, 3, 4, 7}) +
				      "`");

	mao_test::Buffer probe_weak_third_triad = {};
	add_harmonic_note(probe_weak_third_triad, 48, 0.24f, guitar_profile);
	add_harmonic_note(probe_weak_third_triad, 52, 0.034f, guitar_profile);
	add_harmonic_note(probe_weak_third_triad, 55, 0.22f, guitar_profile);

	const auto probe_weak_third_snapshot = analyze_buffer(probe_weak_third_triad, "guitar");
	runner.expect(has_chord_label(probe_weak_third_snapshot.guitar_chord.label, "C"),
		      std::string("guitar probe-weak third triad aliases: expected C, got `") +
			      probe_weak_third_snapshot.guitar_chord.label + "`");

	mao_test::Buffer consistent_probe_power_third = {};
	add_harmonic_note(consistent_probe_power_third, 47, 0.24f, guitar_profile);
	add_harmonic_note(consistent_probe_power_third, 54, 0.22f, guitar_profile);
	add_harmonic_note(consistent_probe_power_third, 51, 0.024f, guitar_profile);

	const auto consistent_probe_power_snapshot = analyze_buffer(consistent_probe_power_third, "guitar");
	runner.expect(has_chord_label(consistent_probe_power_snapshot.guitar_chord.label, "B"),
		      std::string("guitar consistent weak third over power chord: expected B alias, got `") +
			      consistent_probe_power_snapshot.guitar_chord.label + "` raw `" +
			      consistent_probe_power_snapshot.guitar_raw_chord.label + "` smooth `" +
			      consistent_probe_power_snapshot.guitar_smoothed_chord.label + "` probe `" +
			      pitch_level_list(consistent_probe_power_snapshot.guitar_chord_debug_probe_levels,
					       {11, 2, 3, 6}) +
			      "` melodic `" +
			      pitch_level_list(consistent_probe_power_snapshot.guitar_chord_debug_melodic_probe_levels,
					       {11, 2, 3, 6}) +
			      "`");
	expect_no_chord_label(runner, consistent_probe_power_snapshot.guitar_chord.label, "Bm",
			      "guitar consistent weak third over power chord minor alias");

	mao_test::Buffer weak_root_triad = {};
	add_harmonic_note(weak_root_triad, 48, 0.034f, guitar_profile);
	add_harmonic_note(weak_root_triad, 52, 0.22f, guitar_profile);
	add_harmonic_note(weak_root_triad, 55, 0.22f, guitar_profile);

	const auto weak_root_snapshot = analyze_buffer(weak_root_triad, "guitar");
	runner.expect(grid_pitch_active(weak_root_snapshot.guitar_chord_analysis_notes, 0),
		      "guitar weak-root analysis support: expected C in chord-analysis grid");
	runner.expect(has_chord_label(weak_root_snapshot.guitar_chord.label, "C"),
		      std::string("guitar weak-root analysis support: expected C, got `") +
			      weak_root_snapshot.guitar_chord.label + "`");

	mao_test::Buffer hidden_root_triad = {};
	add_harmonic_note(hidden_root_triad, 48, 0.025f, guitar_profile);
	add_harmonic_note(hidden_root_triad, 52, 0.22f, guitar_profile);
	add_harmonic_note(hidden_root_triad, 55, 0.22f, guitar_profile);

	const auto hidden_root_snapshot = analyze_buffer(hidden_root_triad, "guitar");
	runner.expect(grid_pitch_active(hidden_root_snapshot.guitar_chord_analysis_notes, 0),
		      "guitar hidden-root analysis support: expected C in chord-analysis grid");
	runner.expect(!grid_pitch_active(hidden_root_snapshot.guitar_notes, 0),
		      "guitar hidden-root analysis support: expected C hidden from visible grid");
	runner.expect(has_chord_label(hidden_root_snapshot.guitar_chord.label, "C"),
		      std::string("guitar hidden-root analysis support: expected C, got `") +
			      hidden_root_snapshot.guitar_chord.label + "`");

	mao_test::Buffer visible_root_analysis_triad = {};
	add_harmonic_note(visible_root_analysis_triad, 50, 0.24f, guitar_profile);
	add_harmonic_note(visible_root_analysis_triad, 54, 0.038f, guitar_profile);
	add_harmonic_note(visible_root_analysis_triad, 57, 0.086f, guitar_profile);

	const auto visible_root_analysis_snapshot = analyze_buffer(visible_root_analysis_triad, "guitar");
	runner.expect(grid_pitch_active(visible_root_analysis_snapshot.guitar_notes, 2),
		      "guitar visible-root analysis triad: expected D visible in guitar grid");
	runner.expect(grid_pitch_active(visible_root_analysis_snapshot.guitar_chord_analysis_notes, 6) &&
			      grid_pitch_active(visible_root_analysis_snapshot.guitar_chord_analysis_notes, 9),
		      "guitar visible-root analysis triad: expected F# and A in chord-analysis grid");
	runner.expect(has_chord_label(visible_root_analysis_snapshot.guitar_chord.label, "D"),
		      std::string("guitar visible-root analysis triad: expected D, got `") +
			      visible_root_analysis_snapshot.guitar_chord.label + "` notes `" +
			      note_grid_pitch_classes(visible_root_analysis_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(
				      visible_root_analysis_snapshot.guitar_chord_analysis_notes) +
			      "`");

	mao_test::Buffer smoothed_hidden_root_triad = {};
	add_harmonic_note(smoothed_hidden_root_triad, 48, 0.040f, guitar_profile);
	add_harmonic_note(smoothed_hidden_root_triad, 52, 0.44f, guitar_profile);
	add_harmonic_note(smoothed_hidden_root_triad, 55, 1.00f, guitar_profile);
	add_harmonic_note(smoothed_hidden_root_triad, 54, 0.41f, guitar_profile);
	add_harmonic_note(smoothed_hidden_root_triad, 56, 0.25f, guitar_profile);

	const auto smoothed_hidden_root_snapshot = analyze_buffer(smoothed_hidden_root_triad, "guitar");
	runner.expect(has_chord_label(smoothed_hidden_root_snapshot.guitar_smoothed_chord.label, "C"),
		      std::string("guitar smoothed hidden-root candidate: expected smoothed C alias, got `") +
			      smoothed_hidden_root_snapshot.guitar_smoothed_chord.label + "`");
	runner.expect(has_chord_label(smoothed_hidden_root_snapshot.guitar_chord.label, "C"),
		      std::string("guitar smoothed hidden-root candidate: expected displayed C alias, got `") +
			      smoothed_hidden_root_snapshot.guitar_chord.label + "` raw `" +
			      smoothed_hidden_root_snapshot.guitar_raw_chord.label + "` smooth `" +
			      smoothed_hidden_root_snapshot.guitar_smoothed_chord.label + "` analysis `" +
			      note_grid_pitch_classes(smoothed_hidden_root_snapshot.guitar_chord_analysis_notes) +
			      "`");

	mao_test::Buffer contaminated_minor_triad = {};
	add_harmonic_note(contaminated_minor_triad, 49, 0.22f, guitar_profile);
	add_harmonic_note(contaminated_minor_triad, 52, 0.15f, guitar_profile);
	add_harmonic_note(contaminated_minor_triad, 56, 0.17f, guitar_profile);
	add_harmonic_note(contaminated_minor_triad, 45, 0.19f, guitar_profile);
	add_harmonic_note(contaminated_minor_triad, 48, 0.08f, guitar_profile);
	add_harmonic_note(contaminated_minor_triad, 55, 0.08f, guitar_profile);

	const auto contaminated_minor_snapshot = analyze_buffer(contaminated_minor_triad, "guitar");
	runner.expect(has_chord_label(contaminated_minor_snapshot.guitar_chord.label, "C#m"),
		      std::string("guitar analysis-supported triad over shifted extension: expected C#m, got `") +
			      contaminated_minor_snapshot.guitar_chord.label + "`");

	mao_test::Buffer root_third_with_false_root = {};
	add_harmonic_note(root_third_with_false_root, 57, 0.105f, guitar_profile);
	add_harmonic_note(root_third_with_false_root, 60, 0.24f, guitar_profile);
	add_harmonic_note(root_third_with_false_root, 64, 0.030f, guitar_profile);
	add_harmonic_note(root_third_with_false_root, 65, 0.048f, guitar_profile);

	const auto root_third_with_false_root_snapshot =
		analyze_buffer(root_third_with_false_root, "guitar");
	runner.expect(has_chord_label(root_third_with_false_root_snapshot.guitar_chord.label, "Am"),
		      std::string("guitar root-third dyad over false displayed root: expected Am alias, got `") +
			      root_third_with_false_root_snapshot.guitar_chord.label + "` raw `" +
			      root_third_with_false_root_snapshot.guitar_raw_chord.label + "` smooth `" +
			      root_third_with_false_root_snapshot.guitar_smoothed_chord.label + "` notes `" +
			      note_grid_pitch_classes(root_third_with_false_root_snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_pitch_classes(
				      root_third_with_false_root_snapshot.guitar_chord_analysis_notes) +
			      "`");

	mao_test::Buffer major_dyad = {};
	add_harmonic_note(major_dyad, 49, 0.22f, guitar_profile);
	add_harmonic_note(major_dyad, 53, 0.20f, guitar_profile);

	const auto major_dyad_snapshot = analyze_buffer(major_dyad, "guitar");
	runner.expect(has_chord_label(major_dyad_snapshot.guitar_chord.label, "C#"),
		      std::string("guitar root-third major dyad: expected C#, got `") +
			      major_dyad_snapshot.guitar_chord.label + "`");
	expect_no_chord_label(runner, major_dyad_snapshot.guitar_chord.label, "C#pow",
			      "guitar root-third major dyad power alias");

	mao_test::Buffer minor_dyad = {};
	add_harmonic_note(minor_dyad, 51, 0.22f, guitar_profile);
	add_harmonic_note(minor_dyad, 54, 0.20f, guitar_profile);

	const auto minor_dyad_snapshot = analyze_buffer(minor_dyad, "guitar");
	runner.expect(has_chord_label(minor_dyad_snapshot.guitar_chord.label, "D#m"),
		      std::string("guitar root-third minor dyad: expected D#m, got `") +
			      minor_dyad_snapshot.guitar_chord.label + "`");
	expect_no_chord_label(runner, minor_dyad_snapshot.guitar_chord.label, "D#pow",
			      "guitar root-third minor dyad power alias");

	const auto inverted_minor_dyad_snapshot = analyze_buffer(mao_test::make_midi_notes({72, 81}, 0.34f),
								 "guitar");
	runner.expect(has_chord_label(inverted_minor_dyad_snapshot.guitar_chord.label, "Am"),
		      std::string("guitar inverted root-third minor dyad: expected Am, got `") +
			      inverted_minor_dyad_snapshot.guitar_chord.label + "`");

	const auto pure_major_dyad_snapshot = analyze_buffer(mao_test::make_midi_notes({52, 56}, 0.34f), "guitar");
	runner.expect(has_chord_label(pure_major_dyad_snapshot.guitar_chord.label, "E"),
		      std::string("guitar pure root-third major dyad: expected E, got `") +
			      pure_major_dyad_snapshot.guitar_chord.label + "`");
	runner.expect(has_chord_label(pure_major_dyad_snapshot.guitar_chord.label, "C#m"),
		      std::string("guitar pure root-third major dyad: expected rootless C#m alias, got `") +
			      pure_major_dyad_snapshot.guitar_chord.label + "`");

	const auto pure_minor_dyad_snapshot = analyze_buffer(mao_test::make_midi_notes({51, 54}, 0.34f), "guitar");
	runner.expect(has_chord_label(pure_minor_dyad_snapshot.guitar_chord.label, "D#m"),
		      std::string("guitar pure root-third minor dyad: expected D#m, got `") +
			      pure_minor_dyad_snapshot.guitar_chord.label + "`");

	mao_test::Buffer weak_root_minor_dyad = {};
	add_harmonic_note(weak_root_minor_dyad, 57, 0.055f, guitar_profile);
	add_harmonic_note(weak_root_minor_dyad, 60, 0.22f, guitar_profile);

	const auto weak_root_minor_dyad_snapshot = analyze_buffer(weak_root_minor_dyad, "guitar");
	runner.expect(has_chord_label(weak_root_minor_dyad_snapshot.guitar_chord.label, "Am"),
		      std::string("guitar weak-root minor dyad without fifth: expected Am, got `") +
			      weak_root_minor_dyad_snapshot.guitar_chord.label + "`");

	mao_test::Buffer strong_ambiguous_thirds = {};
	add_harmonic_note(strong_ambiguous_thirds, 52, 0.16f, guitar_profile);
	add_harmonic_note(strong_ambiguous_thirds, 55, 0.24f, guitar_profile);
	add_harmonic_note(strong_ambiguous_thirds, 56, 0.23f, guitar_profile);
	add_harmonic_note(strong_ambiguous_thirds, 59, 0.14f, guitar_profile);

	const auto strong_ambiguous_thirds_snapshot = analyze_buffer(strong_ambiguous_thirds, "guitar");
	runner.expect(has_chord_label(strong_ambiguous_thirds_snapshot.guitar_chord.label, "E"),
		      std::string("guitar strong ambiguous thirds: expected E alias, got `") +
			      strong_ambiguous_thirds_snapshot.guitar_chord.label + "`");
	runner.expect(has_chord_label(strong_ambiguous_thirds_snapshot.guitar_chord.label, "Em"),
		      std::string("guitar strong ambiguous thirds: expected Em alias, got `") +
			      strong_ambiguous_thirds_snapshot.guitar_chord.label + "`");

	mao_test::Buffer ambiguous_weak_thirds = {};
	add_harmonic_note(ambiguous_weak_thirds, 48, 0.24f, guitar_profile);
	add_harmonic_note(ambiguous_weak_thirds, 51, 0.034f, guitar_profile);
	add_harmonic_note(ambiguous_weak_thirds, 52, 0.034f, guitar_profile);
	add_harmonic_note(ambiguous_weak_thirds, 55, 0.22f, guitar_profile);

	const auto ambiguous_weak_thirds_snapshot = analyze_buffer(ambiguous_weak_thirds, "guitar");
	expect_no_chord_label(runner, ambiguous_weak_thirds_snapshot.guitar_chord.label, "C",
			      std::string("guitar ambiguous weak thirds major alias raw `") +
				      ambiguous_weak_thirds_snapshot.guitar_raw_chord.label + "` smooth `" +
				      ambiguous_weak_thirds_snapshot.guitar_smoothed_chord.label + "` notes `" +
				      ambiguous_weak_thirds_snapshot.guitar.label + "` analysis `" +
				      note_grid_pitch_classes(ambiguous_weak_thirds_snapshot.guitar_chord_analysis_notes) +
				      "` probe `" +
				      pitch_level_list(ambiguous_weak_thirds_snapshot.guitar_chord_debug_probe_levels,
						       {0, 3, 4, 7}) +
				      "` melodic `" +
				      pitch_level_list(
					      ambiguous_weak_thirds_snapshot.guitar_chord_debug_melodic_probe_levels,
					      {0, 3, 4, 7}) +
				      "`");
	expect_no_chord_label(runner, ambiguous_weak_thirds_snapshot.guitar_chord.label, "Cm",
			      std::string("guitar ambiguous weak thirds minor alias raw `") +
				      ambiguous_weak_thirds_snapshot.guitar_raw_chord.label + "` smooth `" +
				      ambiguous_weak_thirds_snapshot.guitar_smoothed_chord.label + "` notes `" +
				      ambiguous_weak_thirds_snapshot.guitar.label + "` analysis `" +
				      note_grid_pitch_classes(ambiguous_weak_thirds_snapshot.guitar_chord_analysis_notes) +
				      "` probe `" +
				      pitch_level_list(ambiguous_weak_thirds_snapshot.guitar_chord_debug_probe_levels,
						       {0, 3, 4, 7}) +
				      "` melodic `" +
				      pitch_level_list(
					      ambiguous_weak_thirds_snapshot.guitar_chord_debug_melodic_probe_levels,
					      {0, 3, 4, 7}) +
				      "`");

	mao_test::Buffer weak_dim_shape = {};
	add_harmonic_note(weak_dim_shape, 53, 0.24f, guitar_profile);
	add_harmonic_note(weak_dim_shape, 56, 0.24f, guitar_profile);
	add_harmonic_note(weak_dim_shape, 59, 0.050f, guitar_profile);

	const auto weak_dim_snapshot = analyze_buffer(weak_dim_shape, "guitar");
	runner.expect(has_chord_label(weak_dim_snapshot.guitar_chord.label, "Fdim"),
		      std::string("guitar weak-tone diminished CAGED fallback: expected Fdim, got `") +
			      weak_dim_snapshot.guitar_chord.label + "`");

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> bright_guitar_profile = {1.0f, 0.58f, 0.34f, 0.20f, 0.12f};
		add_harmonic_note(buffer, 47, 0.22f, bright_guitar_profile);
		add_harmonic_note(buffer, 51, 0.18f, bright_guitar_profile);
		add_harmonic_note(buffer, 54, 0.13f, bright_guitar_profile);
		for (int midi : {48, 53, 55, 58})
			add_harmonic_note(buffer, midi, 0.040f, bright_guitar_profile);

		const auto snapshot = analyze_buffer(buffer, "distorted guitar");
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "B"),
			      std::string("guitar noisy full-tone major triad recovery: expected B, got `") +
				      snapshot.guitar_chord.label + "` raw `" +
				      snapshot.guitar_raw_chord.label + "` smooth `" +
				      snapshot.guitar_smoothed_chord.label + "` notes `" +
				      note_grid_pitch_classes(snapshot.guitar_notes) + "` analysis `" +
				      note_grid_pitch_classes(snapshot.guitar_chord_analysis_notes) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> bright_guitar_profile = {1.0f, 0.58f, 0.34f, 0.20f, 0.12f};
		add_harmonic_note(buffer, 49, 0.22f, bright_guitar_profile);
		add_harmonic_note(buffer, 54, 0.20f, bright_guitar_profile);
		add_harmonic_note(buffer, 57, 0.20f, bright_guitar_profile);
		add_harmonic_note(buffer, 50, 0.17f, bright_guitar_profile);

		const auto snapshot = analyze_buffer(buffer, "distorted guitar");
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "D"),
			      std::string("guitar analysis-complete relative major alias: expected D, got `") +
				      snapshot.guitar_chord.label + "` raw `" +
				      snapshot.guitar_raw_chord.label + "` smooth `" +
				      snapshot.guitar_smoothed_chord.label + "` notes `" +
				      note_grid_pitch_classes(snapshot.guitar_notes) + "` analysis `" +
				      note_grid_pitch_classes(snapshot.guitar_chord_analysis_notes) + "`");
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
						"G", {"Dm7", "Dm9", "Ddim", "Daug", "G9",
						      "Gmaj7", "Gdim", "Gaug"});
	expect_full_mix_global_chord_transition(runner, "required transition Csus4 to C", csus4,
						"Csus4", c, "C",
						{"C7", "Cmaj7", "Cadd9", "C9", "Cdim", "Caug"});
	expect_full_mix_global_chord_transition(runner, "required transition C to Cmaj7", c, "C",
						cmaj7, "C", {"C7", "C9", "Cadd9", "Cdim", "Caug"});
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
	{
		mao_test::Buffer present_major_seventh = {};
		mao_test::add_midi_note(present_major_seventh, 60, 0.34f);
		mao_test::add_midi_note(present_major_seventh, 64, 0.34f);
		mao_test::add_midi_note(present_major_seventh, 67, 0.34f);
		mao_test::add_midi_note(present_major_seventh, 71, 0.24f);
		const auto snapshot = analyze_buffer(present_major_seventh, "keyboard");
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "Cmaj7"),
			      std::string("chord simplification: present major seventh should not collapse, got `") +
				      snapshot.keyboard_chord.label + "`");
	}
	{
		mao_test::Buffer present_dominant_seventh = {};
		mao_test::add_midi_note(present_dominant_seventh, 60, 0.34f);
		mao_test::add_midi_note(present_dominant_seventh, 64, 0.34f);
		mao_test::add_midi_note(present_dominant_seventh, 67, 0.34f);
		mao_test::add_midi_note(present_dominant_seventh, 70, 0.24f);
		const auto snapshot = analyze_buffer(present_dominant_seventh, "keyboard");
		runner.expect(has_chord_label(snapshot.keyboard_chord.label, "C7"),
			      std::string("chord simplification: present dominant seventh should not collapse, got `") +
				      snapshot.keyboard_chord.label + "`");
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

void check_isolated_guitar_octave_harmonic_display(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> octave_dominant_guitar_profile = {0.12f, 1.0f, 0.010f, 0.82f, 0.10f};
	add_harmonic_note(buffer, 40, 0.24f, octave_dominant_guitar_profile);

	const auto snapshot = analyze_buffer(buffer, "guitar");
	expect_note_token(runner, snapshot.guitar.label, "E2", "isolated guitar octave harmonic display");
	runner.expect(grid_level_for_midi(snapshot.guitar_notes, 40) > 0.0f,
		      std::string("isolated guitar octave harmonic display: expected E2 row, got `") +
			      snapshot.guitar.label + "` notes `" + note_grid_active_labels(snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_active_labels(snapshot.guitar_chord_analysis_notes) + "` smoothed `" +
			      note_grid_active_labels(snapshot.guitar_chord_smoothed_notes) + "`");
	const int pitch_class = 40 % 12;
	runner.expect(snapshot.guitar_notes.cells[pitch_class].active &&
			      snapshot.guitar_notes.cells[pitch_class].midi == 40,
		      std::string("isolated guitar octave harmonic display: expected E2 primary cell, got `") +
			      snapshot.guitar.label + "` notes `" + note_grid_active_labels(snapshot.guitar_notes) +
			      "` analysis `" +
			      note_grid_active_labels(snapshot.guitar_chord_analysis_notes) + "` smoothed `" +
			      note_grid_active_labels(snapshot.guitar_chord_smoothed_notes) + "`");
}

void check_isolated_keyboard_low_octave_display(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> octave_competitive_keyboard_profile = {1.0f, 0.99f, 0.16f, 0.12f};
	add_harmonic_note(buffer, 52, 0.24f, octave_competitive_keyboard_profile);

	const auto snapshot = analyze_buffer(buffer, "keyboard");
	expect_note_token(runner, snapshot.keyboard.label, "E3", "isolated keyboard low octave display");
	const int pitch_class = 52 % 12;
	runner.expect(snapshot.keyboard_notes.rows[0][pitch_class].active &&
			      snapshot.keyboard_notes.rows[0][pitch_class].midi == 52,
		      std::string("isolated keyboard low octave display: expected E3 first row, got `") +
			      snapshot.keyboard.label + "` notes `" +
			      note_grid_active_labels(snapshot.keyboard_notes) + "`");
	runner.expect(snapshot.keyboard_notes.cells[pitch_class].active &&
			      snapshot.keyboard_notes.cells[pitch_class].midi == 52,
		      std::string("isolated keyboard low octave display: expected E3 primary cell, got `") +
			      snapshot.keyboard.label + "` notes `" +
			      note_grid_active_labels(snapshot.keyboard_notes) + "`");
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
	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 93, 0.24f, piano_profile);
		const auto snapshot = analyze_buffer(buffer, "full mix");
		expect_global_pitch_class(runner, snapshot, 9, "single A6 piano global");
		expect_pitch_class(runner, snapshot.keyboard_notes, 9, "single A6 piano keyboard");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 9, "single A6 piano vocal");
		expect_no_pitch_class(runner, snapshot.other_notes, 9, "single A6 piano other");
	}
	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_pure_profile = {1.0f};
		add_harmonic_note(buffer, 81, 0.24f, high_pure_profile);
		const auto snapshot = analyze_buffer(buffer, "full mix");
		expect_global_pitch_class(runner, snapshot, 9, "single high pure guitar global");
		expect_pitch_class(runner, snapshot.guitar_notes, 9, "single high pure guitar mirror");
		const float detected_level = note_grid_pitch_level(snapshot.guitar_notes, 9);
		const float visual_level = note_grid_pitch_visual_level(snapshot.guitar_notes, 9);
		runner.expect(visual_level >= 0.25f && visual_level < detected_level,
			      "single high pure guitar mirror: expected readable render-only attenuation, detected " +
				      std::to_string(detected_level) + " visual " + std::to_string(visual_level));
	}
	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;
		mao_test::Buffer buffer = {};
		const std::vector<float> high_pure_profile = {1.0f};
		add_harmonic_note(buffer, 81, 0.24f, high_pure_profile);
		mao::AnalysisSnapshot snapshot = {};
		for (int frame = 0; frame < 3; ++frame)
			snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "full mix", 0);

		const float live_detected = grid_level_for_midi(snapshot.guitar_notes, 81);
		const float live_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 81);
		runner.expect(live_visual > 0.0f && live_visual < live_detected * 0.45f,
			      "single high pure guitar release: expected live mirror attenuation, detected " +
				      std::to_string(live_detected) + " visual " + std::to_string(live_visual));

		mao_test::Buffer silence = {};
		snapshot = engine.analyze(silence.data(), silence.size(), settings, "full mix", 0);
		const float release_detected = grid_level_for_midi(snapshot.guitar_notes, 81);
		const float release_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 81);
		runner.expect(release_detected > 0.0f,
			      "single high pure guitar release: expected decaying envelope to remain visible");
		runner.expect(release_visual > 0.0f && release_visual < release_detected * 0.45f,
			      "single high pure guitar release: expected mirror attenuation during release, detected " +
				      std::to_string(release_detected) + " visual " +
				      std::to_string(release_visual));
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
			runner.expect(!grid_pitch_active(snapshot.vocal_notes, pitch_class),
				      std::string("full-mix piano-only vocal spillover: expected pitch class ") +
					      mao_test::note_name(pitch_class) + " inactive, got vocal `" +
					      snapshot.vocal.label + "`, debug `" +
					      full_mix_debug_summary_for_midi(snapshot, midi) + "`");
			runner.expect(!grid_pitch_active(snapshot.other_notes, pitch_class),
				      std::string("full-mix piano-only other spillover: expected pitch class ") +
					      mao_test::note_name(pitch_class) + " inactive, got other `" +
					      snapshot.other.label + "`, debug `" +
					      full_mix_debug_summary_for_midi(snapshot, midi) + "`");
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
			runner.expect(!grid_pitch_active(snapshot.other_notes, pitch_class),
				      std::string("full-mix guitar-only other spillover: expected pitch class ") +
					      mao_test::note_name(pitch_class) + " inactive, got other `" +
					      snapshot.other.label + "`, debug `" +
					      full_mix_debug_summary_for_midi(snapshot, midi) + "`");
		}
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> piano_profile = {1.0f, 0.12f, 0.04f, 0.015f};
		add_harmonic_note(buffer, 48, 0.26f, piano_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker low piano", 3);
		expect_global_pitch_class(runner, snapshot, 0, "full-mix low piano global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 48) > 0.0f,
			      std::string("full-mix low piano: expected keyboard C3 ownership, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_electronic_keyboard_profile = {1.0f, 0.82f, 0.38f, 0.24f, 0.18f};
		add_harmonic_note(buffer, 43, 0.27f, low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 43) > 0.0f,
			      std::string("full-mix low electronic keyboard: expected keyboard G2 ownership, "
					  "got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label + "`");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 43) <= 0.0f,
			      std::string("full-mix low electronic keyboard: expected no exact guitar "
					  "G2 duplicate, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 43) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_low_electronic_keyboard_profile =
			{1.0f, 0.59f, 0.24f, 0.27f, 0.05f};
		add_harmonic_note(buffer, 42, 0.27f, measured_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 6,
					  "full-mix measured low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 42) > 0.0f,
			      std::string("full-mix measured low electronic keyboard: expected keyboard "
					  "F#2 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 42) + "`");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 42) <= 0.0f,
			      std::string("full-mix measured low electronic keyboard: expected no exact "
					  "guitar F#2 duplicate, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 42) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> moderate_low_keyboard_profile = {1.0f, 0.62f, 0.30f, 0.20f, 0.16f};
		add_harmonic_note(buffer, 43, 0.27f, moderate_low_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker moderate low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix moderate low keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 43) > 0.0f,
			      std::string("full-mix moderate low keyboard: expected keyboard G2 ownership, "
					  "got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sub_low_electronic_keyboard_profile =
			{1.0f, 0.50f, 0.11f, 0.10f, 0.025f};
		add_harmonic_note(buffer, 31, 0.27f, sub_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sub-low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix sub-low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 31) > 0.0f,
			      std::string("full-mix sub-low electronic keyboard: expected keyboard G1 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 31) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_dominant_e1_keyboard_profile =
			{1.0f, 2.0f, 0.15f, 0.32f, 0.04f};
		add_harmonic_note(buffer, 28, 0.20f, octave_dominant_e1_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-dominant E1 keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix octave-dominant E1 keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 28) > 0.0f,
			      std::string("full-mix octave-dominant E1 keyboard: expected keyboard E1 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 28) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> rich_sub_low_electronic_keyboard_profile =
			{1.0f, 0.62f, 0.24f, 0.060f, 0.12f};
		add_harmonic_note(buffer, 31, 0.27f, rich_sub_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker rich sub-low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix rich sub-low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 31) > 0.0f,
			      std::string("full-mix rich sub-low electronic keyboard: expected keyboard G1 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 31) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> fundamental_stack_sub_low_keyboard_profile =
			{1.0f, 0.26f, 0.42f, 0.34f, 0.015f, 0.10f};
		add_harmonic_note(buffer, 31, 0.27f, fundamental_stack_sub_low_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker fundamental-stack sub-low keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix fundamental-stack sub-low keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 31) > 0.0f,
			      std::string("full-mix fundamental-stack sub-low keyboard: expected keyboard "
					  "G1 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 31) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_dominant_sub_low_keyboard_profile =
			{1.0f, 0.92f, 0.20f, 0.08f, 0.04f};
		add_harmonic_note(buffer, 34, 0.27f, octave_dominant_sub_low_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-dominant sub-low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 10,
					  "full-mix octave-dominant sub-low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 34) > 0.0f,
			      std::string("full-mix octave-dominant sub-low electronic keyboard: expected "
					  "keyboard A#1 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 34) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_selected_sub_low_keyboard_profile =
			{0.42f, 1.0f, 0.52f, 0.72f, 0.34f};
		add_harmonic_note(buffer, 38, 0.27f, octave_selected_sub_low_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-selected sub-low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 2,
					  "full-mix octave-selected sub-low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 38) > 0.0f,
			      std::string("full-mix octave-selected sub-low electronic keyboard: expected "
					  "keyboard D2 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 38) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> noisy_low_electronic_keyboard_profile =
			{1.0f, 0.54f, 0.13f, 0.17f, 0.052f};
		add_harmonic_note(buffer, 40, 0.27f, noisy_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker noisy low electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4, "full-mix noisy low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 40) > 0.0f,
			      std::string("full-mix noisy low electronic keyboard: expected keyboard E2 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 40) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> noisy_low_thin_electronic_keyboard_profile =
			{1.0f, 0.35f, 0.10f, 0.016f, 0.026f};
		add_harmonic_note(buffer, 46, 0.27f, noisy_low_thin_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker noisy low thin electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 10,
					  "full-mix noisy low thin electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 46) > 0.0f,
			      std::string("full-mix noisy low thin electronic keyboard: expected keyboard A#2 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 46) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> noisy_low_sparse_electronic_keyboard_profile =
			{1.0f, 0.20f, 0.14f, 0.018f, 0.050f};
		add_harmonic_note(buffer, 40, 0.27f, noisy_low_sparse_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker noisy low sparse electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix noisy low sparse electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 40) > 0.0f,
			      std::string("full-mix noisy low sparse electronic keyboard: expected keyboard E2 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 40) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> noisy_low_mid_electronic_keyboard_profile =
			{1.0f, 0.35f, 0.08f, 0.075f, 0.008f};
		add_harmonic_note(buffer, 48, 0.27f, noisy_low_mid_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker noisy low-mid electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix noisy low-mid electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 48) > 0.0f,
			      std::string("full-mix noisy low-mid electronic keyboard: expected keyboard C3 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 48) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> clean_octave_electronic_keyboard_profile =
			{1.0f, 0.60f, 0.068f, 0.031f, 0.006f};
		add_harmonic_note(buffer, 72, 0.24f, clean_octave_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker clean octave electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix clean octave electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 72) > 0.0f,
			      std::string("full-mix clean octave electronic keyboard: expected keyboard C5 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, other `" + snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 72) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> other_alias_profile = {1.0f, 7.39f, 0.37f, 4.16f, 0.17f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
		add_harmonic_note(buffer, 48, 0.10f, other_alias_profile);
		add_harmonic_note(buffer, 60, 0.24f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured electronic keyboard suboctave", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix measured electronic keyboard suboctave global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 60) > 0.0f,
			      std::string("full-mix measured electronic keyboard suboctave: expected "
					  "keyboard C4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, other `" + snapshot.other.label +
				      "`, debug C3 `" + full_mix_debug_summary_for_midi(snapshot, 48) +
				      "`, debug C4 `" + full_mix_debug_summary_for_midi(snapshot, 60) + "`");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 48) <= 0.0f,
			      std::string("full-mix measured electronic keyboard suboctave: expected no "
					  "other C3 alias, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 48) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> lower_partial_other_alias_profile =
			{1.0f, 5.43f, 0.32f, 2.66f, 0.26f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
		add_harmonic_note(buffer, 52, 0.10f, lower_partial_other_alias_profile);
		add_harmonic_note(buffer, 64, 0.24f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured electronic keyboard low partial suboctave", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix measured electronic keyboard low-partial suboctave global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 64) > 0.0f,
			      std::string("full-mix measured electronic keyboard low-partial suboctave: "
					  "expected keyboard E4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, other `" + snapshot.other.label +
				      "`, debug E3 `" + full_mix_debug_summary_for_midi(snapshot, 52) +
				      "`, debug E4 `" + full_mix_debug_summary_for_midi(snapshot, 64) + "`");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 52) <= 0.0f,
			      std::string("full-mix measured electronic keyboard low-partial suboctave: "
					  "expected no other E3 alias, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 52) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> edge_other_alias_profile =
			{1.0f, 5.35f, 0.33f, 2.45f, 0.24f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.02f, 0.01f};
		add_harmonic_note(buffer, 55, 0.10f, edge_other_alias_profile);
		add_harmonic_note(buffer, 67, 0.24f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured electronic keyboard edge suboctave", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix measured electronic keyboard edge suboctave global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 67) > 0.0f,
			      std::string("full-mix measured electronic keyboard edge suboctave: expected "
					  "keyboard G4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, other `" + snapshot.other.label +
				      "`, debug G3 `" + full_mix_debug_summary_for_midi(snapshot, 55) +
				      "`, debug G4 `" + full_mix_debug_summary_for_midi(snapshot, 67) + "`");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 55) <= 0.0f,
			      std::string("full-mix measured electronic keyboard edge suboctave: expected "
					  "no other G3 alias, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 55) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> other_harmonic_profile =
			{1.0f, 2.42f, 1.12f, 0.61f, 0.87f};
		add_harmonic_note(buffer, 47, 0.24f, other_harmonic_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured brass keyboard shadow", 3);
		expect_global_pitch_class(runner, snapshot, 11,
					  "full-mix measured brass keyboard shadow global");
		runner.expect(grid_pitch_active(snapshot.other_notes, 11),
			      std::string("full-mix measured brass keyboard shadow: expected other B "
					  "display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 47) + "`");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 47) <= 0.0f,
			      std::string("full-mix measured brass keyboard shadow: expected no keyboard "
					  "B2 shadow, got keyboard `") +
				      snapshot.keyboard.label + "`, other `" + snapshot.other.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 47) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> organ_subharmonic_alias_profile =
			{1.0f, 0.35f, 0.08f, 0.075f, 0.008f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.015f, 0.006f};
		add_harmonic_note(buffer, 53, 0.20f, organ_subharmonic_alias_profile);
		add_harmonic_note(buffer, 65, 0.24f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker organ upper keyboard with low alias", 3);
		expect_global_pitch_class(runner, snapshot, 5, "full-mix organ upper keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 65) > 0.0f,
			      std::string("full-mix organ upper keyboard: expected keyboard F4 display, "
					  "got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, debug lower `" + full_mix_debug_summary_for_midi(snapshot, 53) +
				      "`, debug upper `" + full_mix_debug_summary_for_midi(snapshot, 65) +
				      "`");
		runner.expect(grid_level_for_midi(snapshot.bass_notes, 53) <= 0.0f,
			      std::string("full-mix organ upper keyboard: expected no bass F3 alias, "
					  "got bass `") +
				      snapshot.bass.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug lower `" + full_mix_debug_summary_for_midi(snapshot, 53) +
				      "`, debug upper `" + full_mix_debug_summary_for_midi(snapshot, 65) +
				      "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_low_organ_alias_profile =
			{1.0f, 5.66f, 0.24f, 5.50f, 0.29f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.015f, 0.006f};
		add_harmonic_note(buffer, 55, 0.10f, measured_low_organ_alias_profile);
		add_harmonic_note(buffer, 67, 0.24f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured organ bass alias with upper keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix measured organ bass alias global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 67) > 0.0f,
			      std::string("full-mix measured organ bass alias: expected keyboard G4 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, debug lower `" + full_mix_debug_summary_for_midi(snapshot, 55) +
				      "`, debug upper `" + full_mix_debug_summary_for_midi(snapshot, 67) +
				      "`");
		runner.expect(grid_level_for_midi(snapshot.bass_notes, 55) <= 0.0f,
			      std::string("full-mix measured organ bass alias: expected no bass G3 "
					  "alias, got bass `") +
				      snapshot.bass.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug lower `" + full_mix_debug_summary_for_midi(snapshot, 55) +
				      "`, debug upper `" + full_mix_debug_summary_for_midi(snapshot, 67) +
				      "`");
	}

	{
		mao_test::Buffer low_alias = {};
		mao_test::Buffer alias_with_upper_keyboard = {};
		const std::vector<float> priming_alias_profile =
			{1.0f, 0.62f, 0.15f, 0.12f, 0.008f};
		const std::vector<float> shadowed_alias_profile =
			{1.0f, 0.35f, 0.08f, 0.075f, 0.008f};
		const std::vector<float> upper_keyboard_profile = {1.0f, 0.12f, 0.04f, 0.015f, 0.006f};
		add_harmonic_note(low_alias, 53, 0.24f, priming_alias_profile);
		add_harmonic_note(alias_with_upper_keyboard, 53, 0.20f, shadowed_alias_profile);
		add_harmonic_note(alias_with_upper_keyboard, 65, 0.24f, upper_keyboard_profile);

		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		mao::AnalysisSnapshot snapshot = {};
		for (int frame = 0; frame < 3; ++frame)
			snapshot = engine.analyze(low_alias.data(), low_alias.size(), settings,
						  "speaker organ low alias before keyboard", 0);
		const bool primed_low_alias = grid_level_for_midi(snapshot.bass_notes, 53) > 0.0f;
		const std::string primed_bass_label = snapshot.bass.label;

		snapshot = engine.analyze(alias_with_upper_keyboard.data(), alias_with_upper_keyboard.size(),
					  settings, "speaker organ low alias with upper keyboard", 0);
		runner.expect(primed_low_alias,
			      std::string("full-mix organ keyboard alias release: expected initial low alias "
					  "to prime bass tracking, got bass `") +
				      primed_bass_label + "`");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 65) > 0.0f,
			      std::string("full-mix organ keyboard alias release: expected keyboard F4 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, lower debug `" + full_mix_debug_summary_for_midi(snapshot, 53) +
				      "`, upper debug `" + full_mix_debug_summary_for_midi(snapshot, 65) +
				      "`");
		runner.expect(grid_level_for_midi(snapshot.bass_notes, 53) <= 0.0f,
			      std::string("full-mix organ keyboard alias release: expected shadowed tracked "
					  "bass F3 alias to clear immediately, got bass `") +
				      snapshot.bass.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, lower debug `" + full_mix_debug_summary_for_midi(snapshot, 53) +
				      "`, upper debug `" + full_mix_debug_summary_for_midi(snapshot, 65) +
				      "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> electronic_keyboard_octave_shadow_profile =
			{1.0f, 0.72f, 0.14f, 0.040f, 0.020f};
		add_harmonic_note(buffer, 51, 0.27f, electronic_keyboard_octave_shadow_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker electronic keyboard octave shadow", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix electronic keyboard octave shadow global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 63) <= 0.0f,
			      std::string("full-mix electronic keyboard octave shadow: expected no guitar "
					  "D#4 octave alias, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, other `" + snapshot.other.label + "`, lower debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 51) + "`, upper debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 63) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> electronic_keyboard_third_octave_shadow_profile =
			{1.0f, 0.16f, 0.06f, 0.035f, 0.018f, 0.010f, 0.006f, 1.10f};
		add_harmonic_note(buffer, 40, 0.24f, electronic_keyboard_third_octave_shadow_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker electronic keyboard third-octave shadow", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix electronic keyboard third-octave shadow global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 76) <= 0.0f,
			      std::string("full-mix electronic keyboard third-octave shadow: expected no "
					  "guitar E5 octave-ladder alias, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, other `" + snapshot.other.label + "`, lower debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 40) + "`, upper debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 76) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> electronic_keyboard_octave_stack_profile =
			{1.0f, 0.62f, 0.15f, 0.72f, 0.040f, 0.018f, 0.010f, 1.05f};
		add_harmonic_note(buffer, 37, 0.20f, electronic_keyboard_octave_stack_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker electronic keyboard octave stack", 3);
		expect_global_pitch_class(runner, snapshot, 1,
					  "full-mix electronic keyboard octave stack global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 61) <= 0.0f,
			      std::string("full-mix electronic keyboard octave stack: expected no guitar "
					  "C#4 octave-stack shadow, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, other `" + snapshot.other.label + "`, middle debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 61) + "`, upper debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 73) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_low_electronic_keyboard_profile =
			{1.0f, 0.93f, 0.15f, 0.49f, 0.53f};
		add_harmonic_note(buffer, 51, 0.20f, measured_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured low electronic keyboard octave mirror", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix measured low electronic keyboard octave mirror global");
		runner.expect(grid_pitch_active(snapshot.keyboard_notes, 3) ||
				      grid_pitch_active(snapshot.ambiguous_notes, 3),
			      std::string("full-mix measured low electronic keyboard octave mirror: "
					  "expected keyboard/ambiguous D#, got keyboard `") +
				      snapshot.keyboard.label + "`, ambiguous `" +
				      note_grid_active_labels(snapshot.ambiguous_notes) + "`, guitar `" +
				      snapshot.guitar.label + "`");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 51);
		const float guitar_octave_visual = std::max(grid_visual_level_for_midi(snapshot.guitar_notes, 63),
							    grid_visual_level_for_midi(snapshot.guitar_notes, 75));
		runner.expect(keyboard_visual >= 0.55f && guitar_octave_visual <= keyboard_visual,
			      std::string("full-mix measured low electronic keyboard octave mirror: "
					  "expected guitar D#4/D#5 mirrors not brighter than keyboard, got "
					  "keyboard visual ") +
				      std::to_string(keyboard_visual) + ", guitar octave visual " +
				      std::to_string(guitar_octave_visual) + ", guitar `" +
				      snapshot.guitar.label + "`, lower debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 51) + "`, guitar D#4 debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 63) + "`, guitar D#5 debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 75) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_acoustic_guitar_profile =
			{1.0f, 0.21f, 0.54f, 0.34f, 0.020f};
		const std::vector<float> upper_keyboard_profile =
			{1.0f, 0.030f, 0.010f, 0.004f, 0.002f};
		add_harmonic_note(buffer, 51, 0.10f, low_acoustic_guitar_profile);
		add_harmonic_note(buffer, 63, 0.12f, upper_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low acoustic guitar with upper keyboard support", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix low acoustic guitar upper keyboard global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 51) > 0.0f,
			      std::string("full-mix low acoustic guitar upper keyboard: expected guitar "
					  "D#3 display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, other `" + snapshot.other.label + "`, lower debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 51) + "`, upper debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 63) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_alias_electronic_keyboard_profile =
			{1.0f, 1.48f, 0.060f, 0.006f, 0.004f};
		add_harmonic_note(buffer, 85, 0.24f, high_alias_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker high alias electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 1,
					  "full-mix high alias electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 85) > 0.0f,
			      std::string("full-mix high alias electronic keyboard: expected keyboard C#6 "
					  "display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, other `" + snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 85) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> clean_sustained_keyboard_profile = {1.0f, 0.11f, 0.07f, 0.026f, 0.001f};
		add_harmonic_note(buffer, 64, 0.24f, clean_sustained_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker clean sustained electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4, "full-mix clean sustained keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 64) > 0.0f,
			      std::string("full-mix clean sustained keyboard: expected keyboard E4 display, "
				      "got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> vocal_owned_partial_keyboard_profile =
			{1.0f, 0.148f, 0.019f, 0.086f, 0.002f};
		add_harmonic_note(buffer, 66, 0.24f, vocal_owned_partial_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker vocal-owned partial electronic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 6,
					  "full-mix vocal-owned partial electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 66) > 0.0f,
			      std::string("full-mix vocal-owned partial electronic keyboard: expected "
					  "keyboard F#4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 66) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> vocal_owned_pure_high_note_profile =
			{1.0f, 0.002f, 0.001f, 0.0f, 0.0f};
		add_harmonic_note(buffer, 84, 0.24f, vocal_owned_pure_high_note_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker pure high note", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix vocal-owned pure high note global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 84) > 0.0f,
			      std::string("full-mix vocal-owned pure high note: expected keyboard "
					  "C6 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 84) + "`");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 84) > 0.0f,
			      std::string("full-mix vocal-owned pure high note: expected guitar "
					  "C6 display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 84) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> upper_acoustic_guitar_body_profile =
			{1.0f, 0.101f, 0.116f, 0.021f, 0.001f};
		add_harmonic_note(buffer, 69, 0.24f, upper_acoustic_guitar_body_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker upper plucked body", 3);
		expect_global_pitch_class(runner, snapshot, 9,
					  "full-mix vocal-owned upper acoustic guitar body global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 69) > 0.0f,
			      std::string("full-mix vocal-owned upper acoustic guitar body: expected "
					  "guitar A4 display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 69) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sparse_electronic_guitar_body_profile =
			{1.0f, 0.122f, 0.012f, 0.012f, 0.0f};
		add_harmonic_note(buffer, 67, 0.24f, sparse_electronic_guitar_body_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sparse plucked body", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix vocal-owned sparse electronic guitar body global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 67) > 0.0f,
			      std::string("full-mix vocal-owned sparse electronic guitar body: expected "
					  "guitar G4 display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 67) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_mid_acoustic_guitar_profile =
			{1.0f, 0.148f, 0.027f, 0.126f, 0.001f};
		add_harmonic_note(buffer, 62, 0.24f, measured_mid_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured plucked body", 3);
		expect_global_pitch_class(runner, snapshot, 2,
					  "full-mix measured mid acoustic guitar body global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 62) > 0.0f,
			      std::string("full-mix measured mid acoustic guitar body: expected guitar "
					  "D4 display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 62) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> upper_acoustic_body_profile =
			{1.0f, 0.10f, 0.09f, 0.027f, 0.009f};
		add_harmonic_note(buffer, 69, 0.24f, upper_acoustic_body_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker upper acoustic body", 3);
		expect_global_pitch_class(runner, snapshot, 9,
					  "full-mix vocal-owned upper acoustic body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 69) > 0.0f,
			      std::string("full-mix vocal-owned upper acoustic body: expected keyboard "
					  "A4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 69) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sparse_electronic_body_profile =
			{1.0f, 0.120f, 0.012f, 0.010f, 0.0f};
		add_harmonic_note(buffer, 69, 0.24f, sparse_electronic_body_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sparse electronic body", 3);
		expect_global_pitch_class(runner, snapshot, 9,
					  "full-mix vocal-owned sparse electronic body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 69) > 0.0f,
			      std::string("full-mix vocal-owned sparse electronic body: expected keyboard "
					  "A4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 69) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_electronic_body_profile =
			{1.0f, 0.033f, 0.0f, 0.001f, 0.0f};
		add_harmonic_note(buffer, 84, 0.24f, high_electronic_body_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker bright high electronic body", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix vocal-owned bright high electronic body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 84) > 0.0f,
			      std::string("full-mix vocal-owned bright high electronic body: expected "
					  "keyboard C6 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 84) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> vocal_owned_noisy_acoustic_keyboard_profile =
			{1.0f, 0.113f, 0.132f, 0.029f, 0.029f};
		add_harmonic_note(buffer, 58, 0.24f, vocal_owned_noisy_acoustic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker vocal-owned noisy acoustic keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 10,
					  "full-mix vocal-owned noisy acoustic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 58) > 0.0f,
			      std::string("full-mix vocal-owned noisy acoustic keyboard: expected keyboard "
					  "A#3 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 58) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> vocal_owned_mid_acoustic_piano_profile =
			{1.0f, 0.084f, 0.040f, 0.029f, 0.006f};
		add_harmonic_note(buffer, 62, 0.24f, vocal_owned_mid_acoustic_piano_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker mid struck body", 3);
		expect_global_pitch_class(runner, snapshot, 2,
					  "full-mix vocal-owned mid acoustic piano body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 62) > 0.0f,
			      std::string("full-mix vocal-owned mid acoustic piano body: expected keyboard "
					  "D4 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 62) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> resonant_acoustic_piano_profile =
			{1.0f, 0.079f, 0.126f, 0.045f, 0.038f};
		add_harmonic_note(buffer, 58, 0.24f, resonant_acoustic_piano_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker resonant struck body", 3);
		expect_global_pitch_class(runner, snapshot, 10,
					  "full-mix measured resonant acoustic piano body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 58) > 0.0f,
			      std::string("full-mix measured resonant acoustic piano body: expected "
					  "keyboard A#3 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 58) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_mallet_piano_profile =
			{1.0f, 0.004f, 0.064f, 0.009f, 0.0f};
		add_harmonic_note(buffer, 84, 0.24f, high_mallet_piano_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker high mallet body", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix measured high mallet piano body global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 84) > 0.0f,
			      std::string("full-mix measured high mallet piano body: expected "
					  "keyboard C6 display, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 84) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> noisy_low_electronic_keyboard_profile =
			{1.0f, 0.111f, 0.055f, 0.021f, 0.001f};
		add_harmonic_note(buffer, 53, 0.24f, noisy_low_electronic_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker noisy low electronic body", 3);
		expect_global_pitch_class(runner, snapshot, 5,
					  "full-mix vocal-owned noisy low electronic keyboard global");
		runner.expect(grid_level_for_midi(snapshot.keyboard_notes, 53) > 0.0f,
			      std::string("full-mix vocal-owned noisy low electronic keyboard: expected "
					  "keyboard F3 display, got keyboard `") +
				      snapshot.keyboard.label + "`, bass `" + snapshot.bass.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_mid_acoustic_other_profile =
			{1.0f, 0.271f, 0.076f, 0.063f, 0.011f};
		add_harmonic_note(buffer, 64, 0.24f, measured_mid_acoustic_other_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker resonant acoustic body", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix measured mid acoustic other body global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 64) > 0.0f,
			      std::string("full-mix measured mid acoustic other body: expected other "
					  "E4 display, got other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, keyboard `" +
				      snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 64) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_c4_acoustic_string_profile =
			{1.0f, 0.245f, 0.112f, 0.021f, 0.003f};
		add_harmonic_note(buffer, 60, 0.24f, measured_c4_acoustic_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured acoustic string body", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix measured C4 acoustic string body global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 60) > 0.0f,
			      std::string("full-mix measured C4 acoustic string body: expected other "
					  "C4 display, got other `") +
				      snapshot.other.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
				      snapshot.vocal.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 60) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_low_acoustic_string_profile =
			{1.0f, 0.077f, 0.052f, 0.004f, 0.037f};
		add_harmonic_note(buffer, 58, 0.24f, measured_low_acoustic_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low acoustic string body", 3);
		expect_global_pitch_class(runner, snapshot, 10,
					  "full-mix measured low acoustic string body global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 58) > 0.0f,
			      std::string("full-mix measured low acoustic string body: expected other "
					  "A#3 display, got other `") +
				      snapshot.other.label + "`, bass `" + snapshot.bass.label +
				      "`, vocal `" + snapshot.vocal.label + "`, keyboard `" +
				      snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 58) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_electric_piano_tine_profile =
			{1.0f, 0.44f, 0.10f, 0.010f, 0.025f};
		add_harmonic_note(buffer, 53, 0.24f, measured_electric_piano_tine_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured electric piano tine", 3);
		expect_global_pitch_class(runner, snapshot, 5, "full-mix measured electric piano tine global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 53);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 53);
		runner.expect(keyboard_visual >= 0.35f,
			      std::string("full-mix measured electric piano tine: expected visible keyboard "
					  "F3, got keyboard `") +
				      snapshot.keyboard.label + "` visual " + std::to_string(keyboard_visual) +
				      ", guitar `" + snapshot.guitar.label + "` visual " +
				      std::to_string(guitar_visual) + ", debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
		runner.expect(guitar_visual <= keyboard_visual,
			      std::string("full-mix measured electric piano tine: expected guitar F3 not "
					  "brighter than keyboard, got guitar visual ") +
			      std::to_string(guitar_visual) + ", keyboard visual " +
			      std::to_string(keyboard_visual) + ", debug `" +
			      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_bright_tine_keyboard_profile =
			{1.0f, 0.44f, 0.29f, 0.030f, 0.049f};
		add_harmonic_note(buffer, 53, 0.24f, measured_bright_tine_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured bright tine keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 5,
					  "full-mix measured bright tine keyboard global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 53);
		runner.expect(keyboard_visual >= 0.80f,
			      std::string("full-mix measured bright tine keyboard: expected readable "
					  "keyboard F3 visual >= 0.80, got ") +
				      std::to_string(keyboard_visual) + ", keyboard `" +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, bass `" + snapshot.bass.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_dimmed_tine_keyboard_profile =
			{1.0f, 0.43f, 0.095f, 0.12f, 0.055f};
		add_harmonic_note(buffer, 52, 0.24f, measured_dimmed_tine_keyboard_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured dimmed tine keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix measured dimmed tine keyboard global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 52);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 52);
		runner.expect(keyboard_visual >= 0.88f && keyboard_visual >= guitar_visual * 0.88f,
			      std::string("full-mix measured dimmed tine keyboard: expected readable "
					  "keyboard E3 visual, got keyboard visual ") +
				      std::to_string(keyboard_visual) + ", guitar visual " +
				      std::to_string(guitar_visual) + ", keyboard `" +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 52) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_early_tine_attack_profile =
			{1.0f, 0.327f, 0.165f, 0.010f, 0.013f};
		add_harmonic_note(buffer, 53, 0.24f, measured_early_tine_attack_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured early tine attack keyboard", 4);
		expect_global_pitch_class(runner, snapshot, 5,
					  "full-mix measured early tine attack keyboard global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 53);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 53);
		runner.expect(keyboard_visual >= 0.50f && keyboard_visual >= guitar_visual,
			      std::string("full-mix measured early tine attack keyboard: expected keyboard "
					  "F3 to own the attack before guitar, got keyboard visual ") +
				      std::to_string(keyboard_visual) + ", guitar visual " +
				      std::to_string(guitar_visual) + ", keyboard `" +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_bright_tine_attack_profile =
			{1.0f, 0.588f, 0.385f, 0.020f, 0.016f};
		add_harmonic_note(buffer, 64, 0.24f, measured_bright_tine_attack_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured bright tine attack keyboard", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix measured bright tine attack keyboard global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 64);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 64);
		runner.expect(keyboard_visual >= 0.50f && keyboard_visual >= guitar_visual,
			      std::string("full-mix measured bright tine attack keyboard: expected keyboard "
					  "E4 to own the attack before guitar, got keyboard visual ") +
				      std::to_string(keyboard_visual) + ", guitar visual " +
				      std::to_string(guitar_visual) + ", keyboard `" +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 64) + "`");
	}

	{
		const std::vector<std::vector<float>> measured_tine_attack_profiles = {
			{1.0f, 0.327f, 0.165f, 0.010f, 0.013f},
			{1.0f, 0.323f, 0.162f, 0.011f, 0.013f},
			{1.0f, 0.332f, 0.149f, 0.011f, 0.015f},
			{1.0f, 0.373f, 0.131f, 0.011f, 0.020f},
			{1.0f, 0.440f, 0.104f, 0.010f, 0.025f},
		};
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		mao::AnalysisSnapshot snapshot = {};
		for (const std::vector<float> &profile : measured_tine_attack_profiles) {
			mao_test::Buffer buffer = {};
			add_harmonic_note(buffer, 53, 0.24f, profile);
			snapshot = engine.analyze(buffer.data(), buffer.size(), settings,
						  "speaker measured tine attack keyboard", 0);
		}

		expect_global_pitch_class(runner, snapshot, 5,
					  "full-mix measured tine attack keyboard global");
		const float keyboard_visual = grid_visual_level_for_midi(snapshot.keyboard_notes, 53);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 53);
		runner.expect(keyboard_visual >= 0.88f && keyboard_visual >= guitar_visual * 0.88f,
			      std::string("full-mix measured tine attack keyboard: expected readable "
					  "keyboard F3 after attack, got keyboard visual ") +
				      std::to_string(keyboard_visual) + ", guitar visual " +
				      std::to_string(guitar_visual) + ", keyboard `" +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_wind_profile = {1.0f, 0.37f, 0.16f, 0.027f, 0.015f};
		add_harmonic_note(buffer, 68, 0.24f, high_wind_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker high brass other", 3);
		expect_global_pitch_class(runner, snapshot, 8, "full-mix high brass other global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 68) > 0.0f,
			      std::string("full-mix high brass other: expected other G#4 display, "
					  "got other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> bright_high_brass_profile = {1.0f, 0.18f, 0.54f, 0.58f, 0.012f};
		add_harmonic_note(buffer, 79, 0.22f, bright_high_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker bright high brass other", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix bright high brass global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 79) > 0.0f,
			      std::string("full-mix bright high brass: expected other G5 display, got "
					  "other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, guitar `" + snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> guitar_profile = {1.0f, 0.36f, 0.17f, 0.07f, 0.03f};
		add_harmonic_note(buffer, 52, 0.26f, guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker mid guitar", 3);
		expect_global_pitch_class(runner, snapshot, 4, "full-mix mid guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 52) > 0.0f,
			      std::string("full-mix mid guitar: expected guitar E3 ownership, got guitar `") +
				      snapshot.guitar.label + "`, bass `" + snapshot.bass.label + "`");
		runner.expect(grid_level_for_midi(snapshot.bass_notes, 52) <= 0.0f,
			      std::string("full-mix mid guitar: expected no same-pitch bass E3 shadow, got bass `") +
				      snapshot.bass.label + "` bass_level=" +
				      std::to_string(grid_level_for_midi(snapshot.bass_notes, 52)) +
				      " guitar_level=" +
				      std::to_string(grid_level_for_midi(snapshot.guitar_notes, 52)) +
				      " debug E3 `" +
				      full_mix_debug_summary_for_midi(snapshot, 52) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_stack_guitar_profile = {1.0f, 1.00f, 0.02f, 0.45f, 0.18f};
		add_harmonic_note(buffer, 60, 0.24f, octave_stack_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-stack acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 0, "full-mix octave-stack guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 60) > 0.0f,
			      std::string("full-mix octave-stack guitar: expected guitar C4 ownership, "
					  "got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, other `" + snapshot.other.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_acoustic_guitar_profile = {1.0f, 0.78f, 0.30f, 0.09f, 0.04f};
		add_harmonic_note(buffer, 42, 0.27f, low_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 6, "full-mix low acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 42) > 0.0f,
			      std::string("full-mix low acoustic guitar: expected guitar F#2 ownership, got "
					  "guitar `") +
				      snapshot.guitar.label + "`, bass `" + snapshot.bass.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_noisy_acoustic_guitar_profile =
			{1.0f, 0.43f, 0.022f, 0.29f, 0.078f};
		add_harmonic_note(buffer, 43, 0.27f, low_noisy_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low noisy acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 7, "full-mix low noisy acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 43) > 0.0f,
			      std::string("full-mix low noisy acoustic guitar: expected guitar G2 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, bass `" + snapshot.bass.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 43) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_acoustic_octave_profile = {1.0f, 0.78f, 0.22f, 0.025f, 0.025f};
		add_harmonic_note(buffer, 49, 0.27f, low_acoustic_octave_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low acoustic guitar octave", 3);
		expect_global_pitch_class(runner, snapshot, 1, "full-mix low acoustic guitar octave global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 49) > 0.0f,
			      std::string("full-mix low acoustic guitar octave: expected guitar C#3 ownership, "
					  "got guitar `") +
				      snapshot.guitar.label + "`, bass `" + snapshot.bass.label + "`, other `" +
				      snapshot.other.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> keyboard_owned_acoustic_guitar_profile =
			{1.0f, 0.30f, 0.025f, 0.24f, 0.014f};
		add_harmonic_note(buffer, 56, 0.27f, keyboard_owned_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker keyboard-owned acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 8,
					  "full-mix keyboard-owned acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 56) > 0.0f,
			      std::string("full-mix keyboard-owned acoustic guitar: expected guitar G#3 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 56) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sparse_acoustic_guitar_profile = {1.0f, 0.32f, 0.030f, 0.020f, 0.010f};
		add_harmonic_note(buffer, 54, 0.27f, sparse_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sparse acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 6, "full-mix sparse acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 54) > 0.0f,
			      std::string("full-mix sparse acoustic guitar: expected guitar F#3 ownership, "
					  "got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 6,
				      "full-mix sparse acoustic guitar vocal spillover");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_dominant_acoustic_guitar_profile =
			{1.0f, 1.45f, 0.14f, 0.047f, 0.090f};
		add_harmonic_note(buffer, 52, 0.20f, octave_dominant_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-dominant acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 4,
					  "full-mix octave-dominant acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 52) > 0.0f,
			      std::string("full-mix octave-dominant acoustic guitar: expected guitar E3 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, vocal `" + snapshot.vocal.label +
				      "`, other `" + snapshot.other.label + "`");
		runner.expect(grid_primary_midi_for_pitch(snapshot.guitar_notes, 4) == 52,
			      std::string("full-mix octave-dominant acoustic guitar: expected E3 primary "
					  "row, got guitar `") +
				      snapshot.guitar.label + "` notes `" +
				      note_grid_active_labels(snapshot.guitar_notes) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_plucked_acoustic_guitar_profile =
			{1.0f, 0.11f, 0.19f, 0.14f, 0.010f};
		add_harmonic_note(buffer, 68, 0.24f, high_plucked_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker high plucked acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 8,
					  "full-mix high plucked acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 68) > 0.0f,
			      std::string("full-mix high plucked acoustic guitar: expected guitar G#4 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, vocal `" + snapshot.vocal.label +
				      "`, other `" + snapshot.other.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> clean_high_acoustic_guitar_profile =
			{1.0f, 0.08f, 0.012f, 0.022f, 0.002f};
		add_harmonic_note(buffer, 68, 0.24f, clean_high_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker clean high acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 8, "full-mix clean high acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 68) > 0.0f,
			      std::string("full-mix clean high acoustic guitar: expected guitar G#4 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, vocal `" + snapshot.vocal.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 68) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> mid_vocal_like_acoustic_guitar_profile =
			{1.0f, 0.15f, 0.041f, 0.13f, 0.049f};
		add_harmonic_note(buffer, 54, 0.24f, mid_vocal_like_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker mid vocal-like acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 6,
					  "full-mix mid vocal-like acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 54) > 0.0f,
			      std::string("full-mix mid vocal-like acoustic guitar: expected guitar F#3 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 54) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> high_partial_acoustic_guitar_profile =
			{1.0f, 0.096f, 0.039f, 0.129f, 0.016f};
		add_harmonic_note(buffer, 61, 0.24f, high_partial_acoustic_guitar_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker high-partial acoustic guitar", 3);
		expect_global_pitch_class(runner, snapshot, 1,
					  "full-mix high-partial acoustic guitar global");
		runner.expect(grid_level_for_midi(snapshot.guitar_notes, 61) > 0.0f,
			      std::string("full-mix high-partial acoustic guitar: expected guitar C#4 "
					  "display, got guitar `") +
				      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 61) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_bowed_string_profile = {1.0f, 0.055f, 0.15f, 0.13f, 0.10f};
		add_harmonic_note(buffer, 42, 0.24f, low_bowed_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low bowed string other", 3);
		expect_global_pitch_class(runner, snapshot, 6, "full-mix low bowed string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 42) > 0.0f,
			      std::string("full-mix low bowed string: expected other F#2 display, got "
					  "other `") +
				      snapshot.other.label + "`, bass `" + snapshot.bass.label +
				      "`, guitar `" + snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sub_low_bowed_string_profile =
			{1.0f, 0.15f, 0.25f, 0.07f, 0.012f};
		add_harmonic_note(buffer, 36, 0.24f, sub_low_bowed_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sub-low bowed string other", 3);
		expect_global_pitch_class(runner, snapshot, 0, "full-mix sub-low bowed string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 36) > 0.0f,
			      std::string("full-mix sub-low bowed string: expected other C2 display, got "
					  "other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, guitar `" +
				      snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> sparse_sub_low_bowed_string_profile =
			{1.0f, 0.075f, 0.16f, 0.018f, 0.010f};
		add_harmonic_note(buffer, 39, 0.24f, sparse_sub_low_bowed_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker sparse sub-low bowed string other", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix sparse sub-low bowed string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 39) > 0.0f,
			      std::string("full-mix sparse sub-low bowed string: expected other D#2 "
					  "display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, guitar `" +
				      snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> very_sparse_sub_low_bowed_string_profile =
			{1.0f, 0.045f, 0.060f, 0.012f, 0.008f};
		add_harmonic_note(buffer, 38, 0.24f, very_sparse_sub_low_bowed_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker very sparse sub-low bowed string other", 3);
		expect_global_pitch_class(runner, snapshot, 2,
					  "full-mix very sparse sub-low bowed string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 38) > 0.0f,
			      std::string("full-mix very sparse sub-low bowed string: expected other D2 "
					  "display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, guitar `" +
				      snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_alias_sparse_sub_low_bowed_string_profile =
			{1.0f, 0.16f, 0.020f, 0.018f, 0.006f};
		add_harmonic_note(buffer, 39, 0.24f, octave_alias_sparse_sub_low_bowed_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-alias sparse sub-low bowed string other", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix octave-alias sparse sub-low bowed string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 39) > 0.0f,
			      std::string("full-mix octave-alias sparse sub-low bowed string: expected "
					  "other D#2 display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, guitar `" +
				      snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_shadowed_low_brass_profile =
			{0.58f, 1.0f, 0.40f, 0.34f, 0.26f, 0.22f, 0.0f, 0.28f};
		add_harmonic_note(buffer, 39, 0.24f, octave_shadowed_low_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-shadowed low brass other", 3);
		expect_global_pitch_class(runner, snapshot, 3,
					  "full-mix octave-shadowed low brass global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 39) > 0.0f,
			      std::string("full-mix octave-shadowed low brass: expected other D#2 "
					  "display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, bass `" + snapshot.bass.label + "`, guitar `" +
				      snapshot.guitar.label + "`, debug lower `" +
				      full_mix_debug_summary_for_midi(snapshot, 39) +
				      "`, debug octave `" +
				      full_mix_debug_summary_for_midi(snapshot, 51) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> measured_low_brass_fundamental_profile =
			{1.0f, 0.32f, 0.40f, 0.42f, 0.38f};
		add_harmonic_note(buffer, 45, 0.24f, measured_low_brass_fundamental_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker measured low brass fundamental other", 3);
		expect_global_pitch_class(runner, snapshot, 9,
					  "full-mix measured low brass fundamental global");
		const float other_visual = grid_visual_level_for_midi(snapshot.other_notes, 45);
		const float guitar_visual = grid_visual_level_for_midi(snapshot.guitar_notes, 45);
		runner.expect(other_visual >= 0.58f && other_visual >= guitar_visual * 0.80f,
			      std::string("full-mix measured low brass fundamental: expected readable "
					  "other A2 visual, got other visual ") +
				      std::to_string(other_visual) + ", guitar visual " +
				      std::to_string(guitar_visual) + ", other `" + snapshot.other.label +
				      "`, guitar `" + snapshot.guitar.label + "`, bass `" +
				      snapshot.bass.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 45) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_weak_upper_string_profile =
			{1.0f, 0.18f, 0.018f, 0.005f, 0.006f};
		add_harmonic_note(buffer, 53, 0.24f, low_weak_upper_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low weak-upper string other", 3);
		expect_global_pitch_class(runner, snapshot, 5, "full-mix low weak-upper string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 53) > 0.0f,
			      std::string("full-mix low weak-upper string: expected other F3 display, got "
					  "other `") +
				      snapshot.other.label + "`, bass `" + snapshot.bass.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> hollow_reed_profile = {1.0f, 0.30f, 0.025f, 0.012f, 0.002f};
		add_harmonic_note(buffer, 72, 0.24f, hollow_reed_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker hollow reed other", 3);
		expect_global_pitch_class(runner, snapshot, 0, "full-mix hollow reed global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 72) > 0.0f,
			      std::string("full-mix hollow reed: expected other C5 display, got other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 72) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_noisy_string_profile =
			{1.0f, 0.24f, 0.28f, 0.08f, 0.012f};
		add_harmonic_note(buffer, 48, 0.24f, low_noisy_string_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker low noisy string other", 3);
		expect_global_pitch_class(runner, snapshot, 0, "full-mix low noisy string global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 48) > 0.0f,
			      std::string("full-mix low noisy string: expected other C3 display, got other `") +
				      snapshot.other.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, guitar `" + snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 48) + "`");
		const float other_visual = grid_visual_level_for_midi(snapshot.other_notes, 48);
		runner.expect(other_visual >= 0.24f,
			      std::string("full-mix low noisy string: expected readable other C3 visual "
					  "level >= 0.24, got ") +
				      std::to_string(other_visual) + ", other `" + snapshot.other.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, guitar `" +
				      snapshot.guitar.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 48) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_dominant_reed_profile =
			{1.0f, 1.45f, 0.48f, 0.020f, 0.006f};
		add_harmonic_note(buffer, 69, 0.24f, octave_dominant_reed_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "speaker octave-dominant reed other", 3);
		expect_global_pitch_class(runner, snapshot, 9, "full-mix octave-dominant reed global");
		runner.expect(grid_level_for_midi(snapshot.other_notes, 69) > 0.0f,
			      std::string("full-mix octave-dominant reed: expected other A4 display, got "
					  "other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label +
				      "`, keyboard `" + snapshot.keyboard.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 69) + "`");
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

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> low_brass_profile = {1.0f, 0.60f, 0.40f, 0.24f, 0.14f};
		add_harmonic_note(buffer, 52, 0.28f, low_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "single low other note", 3);
		expect_global_pitch_class(runner, snapshot, 4, "full-mix single low other note global");
		runner.expect(grid_pitch_active(snapshot.other_notes, 4),
			      std::string("full-mix single low other note: expected other E ownership, got other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label + "`, bass `" +
				      snapshot.bass.label + "`");
		expect_no_chord(runner, snapshot.other_chord, "full-mix single low other note chord");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> lower_mid_brass_profile = {1.0f, 0.62f, 0.42f, 0.24f, 0.14f};
		add_harmonic_note(buffer, 59, 0.28f, lower_mid_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "single lower-mid other note", 3);
		expect_global_pitch_class(runner, snapshot, 11, "full-mix single lower-mid other note global");
		runner.expect(grid_pitch_active(snapshot.other_notes, 11),
			      std::string("full-mix single lower-mid other note: expected other B ownership, "
					  "got other `") +
				      snapshot.other.label + "`, guitar `" + snapshot.guitar.label + "`, bass `" +
				      snapshot.bass.label + "`");
		expect_no_chord(runner, snapshot.other_chord, "full-mix single lower-mid other note chord");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> shadowed_low_brass_profile =
			{1.0f, 0.62f, 0.42f, 0.24f, 0.14f, 0.0f, 0.0f, 1.0f};
		add_harmonic_note(buffer, 43, 0.22f, shadowed_low_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "single third-octave-shadowed other note", 3);
		expect_global_pitch_class(runner, snapshot, 7,
					  "full-mix third-octave-shadowed other global");
		runner.expect(grid_pitch_active(snapshot.other_notes, 7) ||
				      grid_pitch_active(snapshot.ambiguous_notes, 7),
			      std::string("full-mix third-octave-shadowed other: expected other/ambiguous G, "
					  "got other `") +
				      snapshot.other.label + "`, ambiguous `" +
				      note_grid_active_labels(snapshot.ambiguous_notes) + "`, guitar `" +
				      snapshot.guitar.label + "`");
		runner.expect(!grid_pitch_active(snapshot.guitar_notes, 7),
			      std::string("full-mix third-octave-shadowed other guitar mirror: "
					  "expected no guitar G, got `") +
				      note_grid_active_labels(snapshot.guitar_notes) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> octave_ladder_brass_profile =
			{1.0f, 3.20f, 2.75f, 1.25f, 0.62f, 0.0f, 0.0f, 1.0f};
		add_harmonic_note(buffer, 42, 0.070f, octave_ladder_brass_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "single octave-ladder other note", 3);
		expect_global_pitch_class(runner, snapshot, 6, "full-mix octave-ladder other global");
		runner.expect(grid_pitch_active(snapshot.other_notes, 6) ||
				      grid_pitch_active(snapshot.ambiguous_notes, 6),
			      std::string("full-mix octave-ladder other: expected other/ambiguous F#, "
					  "got other `") +
				      snapshot.other.label + "`, ambiguous `" +
				      note_grid_active_labels(snapshot.ambiguous_notes) + "`, guitar `" +
				      snapshot.guitar.label + "`");
		runner.expect(!grid_pitch_active(snapshot.guitar_notes, 6),
			      std::string("full-mix octave-ladder other guitar shadow: expected no guitar F#, "
					  "got `") +
				      note_grid_active_labels(snapshot.guitar_notes) + "`, debug lower `" +
				      full_mix_debug_summary_for_midi(snapshot, 42) + "`, debug octave `" +
				      full_mix_debug_summary_for_midi(snapshot, 54) + "`, debug second `" +
				      full_mix_debug_summary_for_midi(snapshot, 66) + "`");
	}

	{
		mao_test::Buffer buffer = {};
		const std::vector<float> electronic_keyboard_ladder_profile =
			{1.0f, 0.96f, 0.18f, 1.18f, 0.12f, 0.0f, 0.0f, 1.10f};
		add_harmonic_note(buffer, 36, 0.18f, electronic_keyboard_ladder_profile);

		const auto snapshot =
			analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
						 "single electronic keyboard octave ladder", 3);
		expect_global_pitch_class(runner, snapshot, 0,
					  "full-mix electronic keyboard ladder global");
		runner.expect(grid_pitch_active(snapshot.keyboard_notes, 0) ||
				      grid_pitch_active(snapshot.ambiguous_notes, 0),
			      std::string("full-mix electronic keyboard ladder: expected keyboard/ambiguous C, "
					  "got keyboard `") +
				      snapshot.keyboard.label + "`, ambiguous `" +
				      note_grid_active_labels(snapshot.ambiguous_notes) + "`, guitar `" +
				      snapshot.guitar.label + "`");
		runner.expect(!grid_pitch_active(snapshot.guitar_notes, 0),
			      std::string("full-mix electronic keyboard ladder guitar shadow: "
					  "expected no guitar C, got `") +
				      note_grid_active_labels(snapshot.guitar_notes) + "`, debug C2 `" +
				      full_mix_debug_summary_for_midi(snapshot, 36) + "`, debug C3 `" +
				      full_mix_debug_summary_for_midi(snapshot, 48) + "`, debug C4 `" +
				      full_mix_debug_summary_for_midi(snapshot, 60) + "`, debug C5 `" +
				      full_mix_debug_summary_for_midi(snapshot, 72) + "`");
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

void check_blended_ambiguous_debug_scores(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> blended_guitar_profile = {1.0f, 0.34f, 0.16f, 0.10f, 0.05f};
	for (int midi : {60, 64, 67})
		add_harmonic_note(buffer, midi, 0.24f, blended_guitar_profile);

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
					 "blended ambiguous debug scores", 1);
	const int midi = 60;
	const mao::FullMixDebugCandidate *candidate = nullptr;
	const std::size_t count =
		std::min<std::size_t>(snapshot.full_mix_debug_candidate_count,
				      snapshot.full_mix_debug_candidates.size());
	for (std::size_t i = 0; i < count; ++i) {
		const mao::FullMixDebugCandidate &debug = snapshot.full_mix_debug_candidates[i];
		if (debug.midi == midi) {
			candidate = &debug;
			break;
		}
	}

	const std::string context =
		std::string("blended ambiguous debug scores ") + mao_test::note_label(midi);
	runner.expect(candidate != nullptr, context + ": missing debug candidate");
	if (!candidate)
		return;
	const float named_score =
		std::max({candidate->keyboard_score, candidate->guitar_score, candidate->other_score});
	runner.expect(candidate->owner == mao::InstrumentKind::Ambiguous,
		      context + ": expected ambiguous owner, got `" +
			      instrument_kind_name(candidate->owner) + "` debug `" +
			      full_mix_debug_summary_for_midi(snapshot, midi) + "`");
	runner.expect(candidate->ownership_confidence > 0.0f && named_score > 0.0f,
		      context + ": expected retained row-score evidence in ambiguous debug, got `" +
			      full_mix_debug_summary_for_midi(snapshot, midi) + "`");
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

void check_full_mix_stable_vocal_visual_floor(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer buffer = {};
	const std::vector<float> measured_open_vocal_profile =
		{1.0f, 0.042f, 0.018f, 0.024f, 0.038f, 0.0f, 0.0f, 0.034f};
	add_harmonic_note(buffer, 66, 0.24f, measured_open_vocal_profile);

	mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	expect_global_pitch_class(runner, snapshot, 6, "full-mix stable vocal visual first-frame global");
	expect_no_pitch_class(runner, snapshot.vocal_notes, 6, "full-mix stable vocal visual first-frame vocal");

	snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
	const float visual_level = grid_visual_level_for_midi(snapshot.vocal_notes, 66);
	runner.expect(visual_level >= 0.88f,
		      std::string("full-mix stable vocal visual: expected bright confirmed vocal F#4, got ") +
			      std::to_string(visual_level) + ", vocal `" + snapshot.vocal.label +
			      "`, keyboard `" + snapshot.keyboard.label + "`, guitar `" +
			      snapshot.guitar.label + "`, other `" + snapshot.other.label +
			      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 66) + "`");
	expect_midi_not_duplicated_across_rows(runner, snapshot, 66, "full-mix stable vocal visual ownership");
}

void check_full_mix_realistic_vocal_recall(Runner &runner)
{
	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;

		mao_test::Buffer buffer = {};
		const std::vector<float> low_fundamental_vocal_profile =
			{1.0f, 1.20f, 0.72f, 0.36f, 0.18f};
		add_harmonic_note(buffer, 41, 0.24f, low_fundamental_vocal_profile);

		mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		expect_global_pitch_class(runner, snapshot, 5, "full-mix low fundamental vocal first-frame global");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 5,
				      "full-mix low fundamental vocal first-frame vocal");

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		runner.expect(grid_pitch_active(snapshot.vocal_notes, 5),
			      std::string("full-mix low fundamental vocal second-frame vocal: expected F active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug F2 `" +
				      full_mix_debug_summary_for_midi(snapshot, 41) + "`");
		runner.expect(grid_level_for_midi(snapshot.vocal_notes, 53) > 0.0f,
			      "full-mix low fundamental vocal: expected display-safe F3 alias in vocal grid");
		runner.expect(grid_level_for_midi(snapshot.vocal_notes, 41) <= 0.0f,
			      "full-mix low fundamental vocal: expected F2 below vocal grid display floor");
	}

	{
		mao::AnalysisEngine engine;
		mao::AnalysisSettings settings = mao_test::default_settings();
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		settings.analysis_interval_seconds = 0.05f;

		mao_test::Buffer buffer = {};
		const std::vector<float> low_vocal_profile = {1.0f, 0.24f, 0.12f, 0.055f, 0.025f};
		add_harmonic_note(buffer, 50, 0.24f, low_vocal_profile);

		mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		expect_global_pitch_class(runner, snapshot, 2, "full-mix D3 vocal first-frame global");
		const mao::FullMixDebugCandidate *first_debug = debug_candidate_for_midi(snapshot, 50);
		runner.expect(first_debug && first_debug->owner == mao::InstrumentKind::Vocal,
			      std::string("full-mix D3 vocal first-frame owner: expected vocal debug, got `") +
				      full_mix_debug_summary(snapshot) + "`");
		runner.expect(!grid_pitch_active(snapshot.vocal_notes, 2),
			      std::string("full-mix D3 vocal first-frame vocal: expected pending D, got vocal `") +
				      snapshot.vocal.label + "`, keyboard `" + snapshot.keyboard.label +
				      "`, debug `" + full_mix_debug_summary(snapshot) + "`");

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		runner.expect(grid_pitch_active(snapshot.vocal_notes, 2),
			      std::string("full-mix D3 vocal second-frame vocal: expected D active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label + "`, vocal `" +
				      snapshot.vocal.label + "`, other `" + snapshot.other.label + "`, global `" +
				      snapshot.global_chord.label + "`, ambiguous " +
				      (grid_pitch_active(snapshot.ambiguous_notes, 2) ? "active" : "inactive") +
				      "`, rms " + std::to_string(snapshot.rms) + ", keyboard grid `" +
				      note_grid_active_labels(snapshot.keyboard_notes) + "`, vocal grid `" +
				      note_grid_active_labels(snapshot.vocal_notes) + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 50) + "`, all debug `" +
				      full_mix_debug_summary(snapshot) + "`");
		expect_midi_not_duplicated_across_rows(runner, snapshot, 50, "full-mix D3 vocal ownership");
	}

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

		mao_test::Buffer buffer = {};
		const std::vector<float> adjacent_voice_profile = {1.0f, 0.50f, 0.18f, 0.06f, 0.025f};
		add_harmonic_note(buffer, 62, 0.24f, adjacent_voice_profile);
		add_harmonic_note(buffer, 61, 0.014f, {1.0f});
		add_harmonic_note(buffer, 63, 0.012f, {1.0f});

		mao::AnalysisSnapshot snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		expect_global_pitch_class(runner, snapshot, 2, "full-mix adjacent vocal first-frame global");
		expect_no_pitch_class(runner, snapshot.vocal_notes, 2,
				      "full-mix adjacent vocal first-frame vocal");

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "Mic/Aux", 0);
		const mao::FullMixDebugCandidate *debug = debug_candidate_for_midi(snapshot, 62);
		runner.expect(debug != nullptr,
			      "full-mix adjacent vocal: expected debug candidate for D4");
		if (debug) {
			runner.expect(debug->owner == mao::InstrumentKind::Guitar ||
				      debug->owner == mao::InstrumentKind::Other,
				      std::string("full-mix adjacent vocal: expected guitar/other owner before display mirror, got `") +
					      instrument_kind_name(debug->owner) + "` debug `" +
					      full_mix_debug_summary_for_midi(snapshot, 62) + "`");
		}
		runner.expect(grid_pitch_active(snapshot.vocal_notes, 2),
			      std::string("full-mix adjacent vocal second-frame vocal: expected D active, got keyboard `") +
				      snapshot.keyboard.label + "`, guitar `" + snapshot.guitar.label +
				      "`, vocal `" + snapshot.vocal.label + "`, other `" +
				      snapshot.other.label + "`, debug `" +
				      full_mix_debug_summary_for_midi(snapshot, 62) + "`");
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
		      std::string("mixed keyboard/guitar bounds: expected guitar notes active, got guitar `") +
			      note_grid_active_labels(snapshot.guitar_notes) + "`, debug C3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 48) + "`, debug E3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 52) + "`, debug G3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 55) + "`, debug C4 `" +
			      full_mix_debug_summary_for_midi(snapshot, 60) + "`, debug E4 `" +
			      full_mix_debug_summary_for_midi(snapshot, 64) + "`, debug C2 `" +
			      full_mix_debug_summary_for_midi(snapshot, 36) + "`");
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

mao::AnalysisSettings tempo_test_settings()
{
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;
	settings.analysis_window_seconds = 0.10f;
	settings.analysis_window_samples = 0;
	return settings;
}

mao::AnalysisSnapshot run_tempo_pattern(mao::AnalysisEngine &engine, const mao::AnalysisSettings &settings,
					float bpm, int frames, bool eighth_hats, bool one_frame_fill)
{
	const float beat_seconds = 60.0f / bpm;
	const float half_beat_seconds = beat_seconds * 0.5f;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (eighth_hats && next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, 0.70f);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += half_beat_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer);
			else
				add_tempo_kick(buffer);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}
		if (one_frame_fill && frame == frames / 2 + static_cast<int>(std::lround(half_beat_seconds /
										      interval_seconds * 0.5f)))
			add_tempo_fill(buffer);

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_sparse_body_hihat_tempo_pattern(mao::AnalysisEngine &engine,
						  const mao::AnalysisSettings &settings,
						  float bpm, int frames, float hihat_division,
						  float hihat_scale)
{
	const float beat_seconds = 60.0f / bpm;
	const float hihat_seconds = beat_seconds / hihat_division;
	const float body_seconds = beat_seconds * 2.0f;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_body_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int body_hit = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, hihat_scale);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += hihat_seconds;
		}
		if (next_body_seconds <= frame_center_seconds) {
			if (body_hit % 2 == 0)
				add_tempo_kick(buffer);
			else
				add_tempo_snare(buffer);
			++body_hit;
			while (next_body_seconds <= frame_center_seconds)
				next_body_seconds += body_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_dense_subdivision_tempo_pattern(mao::AnalysisEngine &engine,
							   const mao::AnalysisSettings &settings,
							   float bpm, int frames, float hihat_division,
							   float hihat_scale, float body_scale)
{
	const float beat_seconds = 60.0f / bpm;
	const float hihat_seconds = beat_seconds / hihat_division;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, hihat_scale);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += hihat_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer, body_scale);
			else
				add_tempo_kick(buffer, body_scale);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "dense subdivision tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_syncopated_tempo_pattern(mao::AnalysisEngine &engine,
						    const mao::AnalysisSettings &settings,
						    float bpm, int frames)
{
	const float beat_seconds = 60.0f / bpm;
	const float eighth_seconds = beat_seconds * 0.5f;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, beat % 2 == 0 ? 0.62f : 0.82f);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += eighth_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 8 == 0 || beat % 8 == 3)
				add_tempo_kick(buffer, beat % 8 == 3 ? 0.82f : 1.0f);
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer, 0.92f);
			if (beat % 16 == 10)
				add_tempo_fill(buffer);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "syncopated tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_dense_sixteenth_hat_tempo_pattern(mao::AnalysisEngine &engine,
							     const mao::AnalysisSettings &settings,
							     float bpm, int frames)
{
	const float beat_seconds = 60.0f / bpm;
	const float sixteenth_seconds = beat_seconds * 0.25f;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, (beat % 2 == 0) ? 1.22f : 1.08f);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += sixteenth_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer, 0.46f);
			else
				add_tempo_kick(buffer, 0.44f);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings,
					  "dense sixteenth hat tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_triplet_hat_tempo_pattern(mao::AnalysisEngine &engine,
						     const mao::AnalysisSettings &settings,
						     float bpm, int frames)
{
	const float beat_seconds = 60.0f / bpm;
	const float triplet_seconds = beat_seconds * (2.0f / 3.0f);
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, 1.28f);
			while (next_hat_seconds <= frame_center_seconds)
				next_hat_seconds += triplet_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer, 0.42f);
			else
				add_tempo_kick(buffer, beat % 8 == 4 ? 0.36f : 0.50f);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings,
					  "triplet subdivision tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_offbeat_hat_tempo_pattern(mao::AnalysisEngine &engine,
						    const mao::AnalysisSettings &settings,
						    float bpm, int frames)
{
	const float beat_seconds = 60.0f / bpm;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_offbeat_seconds = beat_seconds * 0.5f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_offbeat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, 1.24f);
			while (next_offbeat_seconds <= frame_center_seconds)
				next_offbeat_seconds += beat_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			if (beat % 4 == 1 || beat % 4 == 3)
				add_tempo_snare(buffer, 0.58f);
			else
				add_tempo_kick(buffer, beat % 8 == 4 ? 0.44f : 0.64f);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "offbeat hat tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_body_dropout_tempo_pattern(mao::AnalysisEngine &engine,
						     const mao::AnalysisSettings &settings,
						     float bpm, int frames)
{
	const float beat_seconds = 60.0f / bpm;
	const float eighth_seconds = beat_seconds * 0.5f;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_beat_seconds = 0.0f;
	float next_hihat_seconds = 0.0f;
	int beat = 0;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		add_tempo_backing(buffer, static_cast<uint64_t>(frame) * hop_samples);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_hihat_seconds <= frame_center_seconds) {
			add_tempo_hihat(buffer, beat % 2 == 0 ? 0.76f : 0.96f);
			while (next_hihat_seconds <= frame_center_seconds)
				next_hihat_seconds += eighth_seconds;
		}
		if (next_beat_seconds <= frame_center_seconds) {
			const bool dropout = beat % 16 == 6 || beat % 16 == 14;
			if (!dropout) {
				if (beat % 4 == 1 || beat % 4 == 3)
					add_tempo_snare(buffer, beat % 8 == 3 ? 0.76f : 0.68f);
				else
					add_tempo_kick(buffer, beat % 8 == 4 ? 0.54f : 0.82f);
			}
			if (beat % 16 == 11)
				add_tempo_fill(buffer);
			++beat;
			while (next_beat_seconds <= frame_center_seconds)
				next_beat_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "body dropout tempo test", 0);
	}

	return snapshot;
}

mao::AnalysisSnapshot run_tonal_pulse_tempo_pattern(mao::AnalysisEngine &engine,
						     const mao::AnalysisSettings &settings,
						     float bpm, int frames, float pulse_scale = 1.0f)
{
	const float beat_seconds = 60.0f / bpm;
	const float interval_seconds = settings.analysis_interval_seconds;
	const uint64_t hop_samples = static_cast<uint64_t>(
		std::lround(settings.analysis_interval_seconds * static_cast<float>(settings.sample_rate)));
	mao::AnalysisSnapshot snapshot = {};
	float next_pulse_seconds = 0.0f;

	for (int frame = 0; frame < frames; ++frame) {
		mao_test::Buffer buffer = {};
		const uint64_t sample_offset = static_cast<uint64_t>(frame) * hop_samples;
		add_tempo_backing(buffer, sample_offset);
		const float frame_seconds = static_cast<float>(frame) * interval_seconds;
		const float frame_center_seconds = frame_seconds + interval_seconds * 0.5f;

		if (next_pulse_seconds <= frame_center_seconds) {
			add_tempo_tonal_pulse(buffer, sample_offset, pulse_scale);
			while (next_pulse_seconds <= frame_center_seconds)
				next_pulse_seconds += beat_seconds;
		}

		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "tonal tempo test", 0);
	}

	return snapshot;
}

void expect_bpm_near(Runner &runner, const mao::AnalysisSnapshot &snapshot, float expected, float tolerance,
		     const std::string &context, float min_confidence = 0.22f)
{
	std::ostringstream candidates;
	candidates << " candidates";
	for (std::size_t i = 0; i < snapshot.tempo_debug_candidate_count; ++i) {
		const mao::TempoDebugCandidate &candidate = snapshot.tempo_debug_candidates[i];
		candidates << " " << candidate.bpm << "(s=" << candidate.score
			   << ",a=" << candidate.adjacent_score << ",b=" << candidate.body_score
			   << ",ba=" << candidate.adjacent_body_score << ",sub=" << candidate.subdivision_score
			   << ",suba=" << candidate.adjacent_subdivision_score
			   << ",ph=" << candidate.phase_score
			   << ",phb=" << candidate.phase_body_coverage
			   << ",pha=" << candidate.phase_all_coverage << ")";
	}
	runner.expect(std::fabs(snapshot.estimated_bpm - expected) <= tolerance,
		      context + ": expected BPM " + std::to_string(snapshot.estimated_bpm) + " near " +
			      std::to_string(expected) + candidates.str());
	runner.expect(snapshot.bpm_confidence >= min_confidence,
		      context + ": expected confidence >= " + std::to_string(min_confidence * 100.0f) +
			      "%, got " +
			      std::to_string(snapshot.bpm_confidence));
}

void expect_tempo_candidate_near(Runner &runner, const mao::AnalysisSnapshot &snapshot, float expected,
				 float tolerance, const std::string &context)
{
	bool found = false;
	std::ostringstream candidates;
	candidates << " candidates";
	for (std::size_t i = 0; i < snapshot.tempo_debug_candidate_count; ++i) {
		const mao::TempoDebugCandidate &candidate = snapshot.tempo_debug_candidates[i];
		candidates << " " << candidate.bpm << "(s=" << candidate.score
			   << ",a=" << candidate.adjacent_score << ",b=" << candidate.body_score
			   << ",ba=" << candidate.adjacent_body_score << ",sub=" << candidate.subdivision_score
			   << ",suba=" << candidate.adjacent_subdivision_score
			   << ",ph=" << candidate.phase_score
			   << ",phb=" << candidate.phase_body_coverage
			   << ",pha=" << candidate.phase_all_coverage << ")";
		if (std::fabs(static_cast<float>(snapshot.tempo_debug_candidates[i].bpm) - expected) <= tolerance) {
			found = true;
			break;
		}
	}
	runner.expect(found, context + ": expected top tempo candidates to include BPM near " +
				    std::to_string(expected) + candidates.str());
}

void expect_best_tempo_phase_support(Runner &runner, const mao::AnalysisSnapshot &snapshot,
				     const std::string &context)
{
	runner.expect(snapshot.tempo_debug_candidate_count > 0,
		      context + ": expected at least one tempo debug candidate");
	if (snapshot.tempo_debug_candidate_count == 0)
		return;
	const mao::TempoDebugCandidate &candidate = snapshot.tempo_debug_candidates[0];
	runner.expect(candidate.phase_score > 0.0f,
		      context + ": expected best tempo candidate to have phase score");
	runner.expect(candidate.phase_all_coverage >= 0.25f,
		      context + ": expected best tempo candidate phase all coverage >= 25%, got " +
			      std::to_string(candidate.phase_all_coverage));
	runner.expect(candidate.phase_body_coverage >= 0.15f,
		      context + ": expected best tempo candidate phase body coverage >= 15%, got " +
			      std::to_string(candidate.phase_body_coverage));
	runner.expect(candidate.phase_offset_seconds >= 0.0f,
		      context + ": expected non-negative phase offset");
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
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 100.0f, 180, false, false);
		expect_bpm_near(runner, snapshot, 100.0f, 5.0f, "BPM estimate 100");
		expect_best_tempo_phase_support(runner, snapshot, "BPM phase support 100");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 120.0f, 220, true, true);
		expect_bpm_near(runner, snapshot, 120.0f, 5.0f, "BPM estimate with eighth hats and fill");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 90.0f, 240, true, false);
		expect_bpm_near(runner, snapshot, 90.0f, 7.0f,
				"BPM estimate should not double slower eighth-hat groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_sparse_body_hihat_tempo_pattern(engine, settings, 96.0f, 300, 2.0f, 0.70f);
		expect_bpm_near(runner, snapshot, 96.0f, 7.0f,
				"BPM estimate should not double sparse eighth-hat groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_dense_subdivision_tempo_pattern(engine, settings, 104.0f, 340, 2.0f, 1.25f, 0.42f);
		expect_bpm_near(runner, snapshot, 104.0f, 7.0f,
				"BPM estimate should prefer weak body pulse over loud eighth hats");
		expect_tempo_candidate_near(runner, snapshot, 104.0f, 4.0f,
					    "BPM diagnostics dense subdivision groove");
		expect_best_tempo_phase_support(runner, snapshot, "BPM phase support dense subdivision groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_syncopated_tempo_pattern(engine, settings, 128.0f, 320);
		expect_bpm_near(runner, snapshot, 128.0f, 7.0f,
				"BPM estimate should survive syncopated kick and fill");
		expect_tempo_candidate_near(runner, snapshot, 128.0f, 4.0f,
					    "BPM diagnostics syncopated groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_dense_sixteenth_hat_tempo_pattern(engine, settings, 92.0f, 360);
		expect_bpm_near(runner, snapshot, 92.0f, 7.0f,
				"BPM estimate should not follow loud sixteenth hats");
		expect_tempo_candidate_near(runner, snapshot, 92.0f, 4.0f,
					    "BPM diagnostics dense sixteenth hats");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_triplet_hat_tempo_pattern(engine, settings, 120.0f, 360);
		expect_bpm_near(runner, snapshot, 120.0f, 7.0f,
				"BPM estimate should reject loud triplet-hat subdivision");
		expect_tempo_candidate_near(runner, snapshot, 120.0f, 4.0f,
					    "BPM diagnostics triplet hats");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_dense_subdivision_tempo_pattern(engine, settings, 100.0f, 360, 4.0f, 1.62f, 0.16f);
		expect_bpm_near(runner, snapshot, 100.0f, 7.0f,
				"BPM estimate should reject loud sixteenth-hat subdivision with weak body");
		expect_tempo_candidate_near(runner, snapshot, 100.0f, 4.0f,
					    "BPM diagnostics weak-body sixteenth hats");
		expect_best_tempo_phase_support(runner, snapshot, "BPM phase support weak-body sixteenth hats");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_offbeat_hat_tempo_pattern(engine, settings, 116.0f, 420);
		expect_bpm_near(runner, snapshot, 116.0f, 7.0f,
				"BPM estimate should prefer beat body over offbeat hats", 0.18f);
		expect_tempo_candidate_near(runner, snapshot, 116.0f, 4.0f,
					    "BPM diagnostics offbeat hats");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_body_dropout_tempo_pattern(engine, settings, 132.0f, 360);
		expect_bpm_near(runner, snapshot, 132.0f, 8.0f,
				"BPM estimate should survive body dropouts and one fill");
		expect_tempo_candidate_near(runner, snapshot, 132.0f, 5.0f,
					    "BPM diagnostics body dropouts");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tonal_pulse_tempo_pattern(engine, settings, 112.0f, 260);
		expect_bpm_near(runner, snapshot, 112.0f, 7.0f,
				"BPM estimate from broad tonal pulses");
		expect_tempo_candidate_near(runner, snapshot, 112.0f, 4.0f,
					    "BPM diagnostics broad tonal pulses");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot =
			run_tonal_pulse_tempo_pattern(engine, settings, 118.0f, 450, 0.28f);
		expect_bpm_near(runner, snapshot, 118.0f, 8.0f,
				"BPM estimate from weak broad tonal pulses");
		expect_tempo_candidate_near(runner, snapshot, 118.0f, 5.0f,
					    "BPM diagnostics weak broad tonal pulses");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 64.0f, 280, true, false);
		expect_bpm_near(runner, snapshot, 64.0f, 5.0f, "BPM estimate low-tempo groove");
		expect_tempo_candidate_near(runner, snapshot, 64.0f, 3.0f,
					    "BPM diagnostics low-tempo groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		const mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 205.0f, 240, false, false);
		expect_bpm_near(runner, snapshot, 205.0f, 8.0f, "BPM estimate fast-tempo groove");
		expect_tempo_candidate_near(runner, snapshot, 205.0f, 4.0f,
					    "BPM diagnostics fast-tempo groove");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 100.0f, 150, false, false);
		expect_bpm_near(runner, snapshot, 100.0f, 6.0f, "BPM estimate before tempo change");
		snapshot = run_tempo_pattern(engine, settings, 140.0f, 180, false, false);
		expect_bpm_near(runner, snapshot, 140.0f, 7.0f, "BPM estimate after tempo change");
	}

	{
		mao::AnalysisEngine engine;
		const mao::AnalysisSettings settings = tempo_test_settings();
		mao::AnalysisSnapshot snapshot = run_tempo_pattern(engine, settings, 120.0f, 180, false, false);
		expect_bpm_near(runner, snapshot, 120.0f, 5.0f, "BPM estimate before silence");
		mao_test::Buffer silence = {};
		for (int frame = 0; frame < 90; ++frame)
			snapshot = engine.analyze(silence.data(), silence.size(), settings, "tempo test", 0);
		runner.expect(snapshot.estimated_bpm == 0.0f && snapshot.bpm_confidence == 0.0f,
			      "BPM estimate: expected silence to clear tempo, got BPM " +
				      std::to_string(snapshot.estimated_bpm) + " confidence " +
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
		const std::string bass_context =
			context + " bass levels bass=" +
			std::to_string(grid_level_for_midi(snapshot.bass_notes, bass_midi)) +
			" other=" + std::to_string(grid_level_for_midi(snapshot.other_notes, bass_midi)) +
			" debug `" + full_mix_debug_summary_for_midi(snapshot, bass_midi) + "`";

		expect_label(runner, snapshot.bass.label, mao_test::note_label(bass_midi), bass_context);
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
			const int bass_midi = bass_midi_for_pitch_class(dataset.root_pitch_class);
			const std::string bass_context =
				context + " bass levels bass=" +
				std::to_string(grid_level_for_midi(snapshot.bass_notes, bass_midi)) +
				" other=" +
				std::to_string(grid_level_for_midi(snapshot.other_notes, bass_midi)) +
				" debug `" + full_mix_debug_summary_for_midi(snapshot, bass_midi) + "`";
			expect_label(runner, snapshot.bass.label, mao_test::note_label(bass_midi), bass_context);
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

	mao_test::Buffer c2_with_subharmonic = {};
	const std::vector<float> c2_profile = {1.0f, 0.34f, 0.13f, 0.22f, 0.20f, 0.043f};
	add_harmonic_note(c2_with_subharmonic, 36, 0.24f, c2_profile);
	mao_test::add_sine(c2_with_subharmonic, mao_test::midi_frequency(24), 0.0008f);
	const auto c2_snapshot =
		analyze_buffer_with_mode(c2_with_subharmonic, mao::AnalysisInputMode::FullMix,
					 "speaker piano", 4);
	runner.expect(grid_primary_midi_for_pitch(c2_snapshot.keyboard_notes, 0) == 36,
		      std::string("low acoustic piano C2 subharmonic guard: expected C2 primary, got `") +
			      note_grid_active_labels(c2_snapshot.keyboard_notes) + "`");
}

void check_realistic_instrument_chords(Runner &runner)
{
	const std::vector<float> guitar_profile = {1.0f, 0.34f, 0.16f, 0.08f};
	const auto guitar_buffer = make_harmonic_notes({48, 52, 55, 60, 64}, 0.17f, guitar_profile);
	const auto guitar_snapshot = analyze_buffer(guitar_buffer, "guitar");
	expect_chord_label_present(runner, guitar_snapshot.guitar_chord.label, "C",
				   "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "C3", "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "E3", "realistic guitar C chord");
	expect_note_token(runner, guitar_snapshot.guitar.label, "G3", "realistic guitar C chord");

	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 48, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 55, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 52, 0.060f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		expect_chord_label_present(runner, snapshot.guitar_chord.label, "C",
					   "weak guitar third hidden chord grid");
		expect_note_token(runner, snapshot.guitar.label, "C3", "weak guitar third hidden chord grid");
		expect_note_token(runner, snapshot.guitar.label, "G3", "weak guitar third hidden chord grid");
		runner.expect(!mao_test::has_note_token(snapshot.guitar.label, "E3"),
			      std::string("weak guitar third hidden chord grid: expected E3 hidden, got `") +
				      snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 48, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 55, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 52, 0.060f, guitar_profile);
		add_harmonic_note(buffer, 59, 0.065f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		const std::string context = "weak guitar third extension hidden chord grid";
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "C"),
			      context + ": expected C alias, got `" + snapshot.guitar_chord.label + "`");
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "Cmaj7"),
			      context + ": expected Cmaj7 alias, got `" + snapshot.guitar_chord.label + "`");
		runner.expect(!mao_test::has_note_token(snapshot.guitar.label, "E3"),
			      context + ": expected E3 hidden, got `" + snapshot.guitar.label + "`");
	}

	{
		mao_test::Buffer buffer = {};
		add_harmonic_note(buffer, 45, 0.22f, guitar_profile);
		add_harmonic_note(buffer, 52, 0.24f, guitar_profile);
		add_harmonic_note(buffer, 56, 0.10f, guitar_profile);
		add_harmonic_note(buffer, 48, 0.045f, guitar_profile);
		const auto snapshot = analyze_buffer(buffer, "guitar");
		const std::string context = "weak raw minor third same-root guitar quality";
		runner.expect(has_chord_label(snapshot.guitar_chord.label, "Am"),
			      context + ": expected Am alias, got `" + snapshot.guitar_chord.label + "`");
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
		runner.expect(has_chord_label(snapshot.guitar_chord.label, shape.chord),
			      context + ": expected chord label `" + shape.chord + "`, got `" +
				      snapshot.guitar_chord.label + "`");
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
	expect_chord_label_present(runner, snapshot.global_chord.label, "C",
				   "CAGED mix root independence global chord");
	runner.expect(has_chord_label(snapshot.guitar_chord.label, "C"),
		      std::string("CAGED mix root independence guitar chord: expected C alias, got `") +
			      snapshot.guitar_chord.label + "` notes `" +
			      note_grid_pitch_classes(snapshot.guitar_notes) + "` analysis `" +
			      note_grid_pitch_classes(snapshot.guitar_chord_analysis_notes) + "` smooth `" +
			      note_grid_pitch_classes(snapshot.guitar_chord_smoothed_notes) + "` debug C3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 48) + "` debug E3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 52) + "` debug G3 `" +
			      full_mix_debug_summary_for_midi(snapshot, 55) + "` debug C4 `" +
			      full_mix_debug_summary_for_midi(snapshot, 60) + "` debug E4 `" +
			      full_mix_debug_summary_for_midi(snapshot, 64) + "`");
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

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "same-note timbre split", 3);
	expect_global_pitch_class(runner, snapshot, 0, "same-note timbre split global");
	expect_midi_in_keyboard_guitar_other(runner, snapshot, 60, "same-note timbre split");
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
	expect_label(runner, snapshot.keyboard_chord.label, "C", "ambiguous same-note full mix keyboard chord");
	expect_label(runner, snapshot.guitar_chord.label, "C", "ambiguous same-note full mix guitar chord");
	expect_label(runner, snapshot.other_chord.label, "C", "ambiguous same-note full mix other chord");
	for (int midi : {60, 64, 67})
		expect_midi_in_keyboard_guitar_other(runner, snapshot, midi,
						     "ambiguous same-note full mix ownership");
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

	runner.expect(std::strcmp(snapshot.bass.label, "E2") == 0,
		      std::string("full-mix inversion bass: expected E2, got `") +
			      snapshot.bass.label + "` guitar `" + snapshot.guitar.label +
			      "` debug E2 `" + full_mix_debug_summary_for_midi(snapshot, 40) + "`");
	expect_label(runner, snapshot.global_chord.label, "C", "full-mix inversion global chord");
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

	mao_test::Buffer low_buffer = {};
	const std::vector<float> low_electronic_bass_profile = {1.0f, 0.80f, 0.18f, 0.05f, 0.03f};
	add_harmonic_note(low_buffer, 29, 0.30f, low_electronic_bass_profile);

	const auto low_snapshot =
		analyze_buffer_with_mode(low_buffer, mao::AnalysisInputMode::FullMix,
					 "speaker low electronic bass-only", 3);
	expect_label(runner, low_snapshot.bass.label, "F1", "full-mix low electronic bass harmonic ownership");
	expect_empty_note_grid(runner, low_snapshot.keyboard_notes,
			       "full-mix low electronic bass keyboard harmonic spillover");
	expect_empty_note_grid(runner, low_snapshot.guitar_notes,
			       "full-mix low electronic bass guitar harmonic spillover");
	expect_empty_note_grid(runner, low_snapshot.vocal_notes,
			       "full-mix low electronic bass vocal harmonic spillover");
	expect_empty_note_grid(runner, low_snapshot.other_notes,
			       "full-mix low electronic bass other harmonic spillover");
}

void check_full_mix_high_bass_range(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> high_bass_profile = {1.0f, 0.56f, 0.34f, 0.16f};
	add_harmonic_note(buffer, 53, 0.26f, high_bass_profile);

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix, "speaker monitor", 3);
	expect_label(runner, snapshot.bass.label, "F3", "full-mix high bass ownership");
	runner.expect(grid_level_for_midi(snapshot.bass_notes, 53) > 0.0f,
		      "full-mix high bass ownership: expected F3 in bass note grid");

	mao_test::Buffer upper_electronic_buffer = {};
	const std::vector<float> upper_electronic_bass_profile = {1.0f, 0.62f, 0.21f, 0.042f, 0.006f};
	add_harmonic_note(upper_electronic_buffer, 54, 0.26f, upper_electronic_bass_profile);

	const auto upper_electronic_snapshot =
		analyze_buffer_with_mode(upper_electronic_buffer, mao::AnalysisInputMode::FullMix,
					 "speaker measured upper electronic bass", 3);
	expect_label(runner, upper_electronic_snapshot.bass.label, "F#3",
		     "full-mix upper electronic bass ownership");
	runner.expect(grid_level_for_midi(upper_electronic_snapshot.bass_notes, 54) > 0.0f,
		      std::string("full-mix upper electronic bass: expected F#3 in bass note grid, "
				  "got bass `") +
			      upper_electronic_snapshot.bass.label + "`, keyboard `" +
			      upper_electronic_snapshot.keyboard.label + "`, guitar `" +
			      upper_electronic_snapshot.guitar.label + "`, debug `" +
			      full_mix_debug_summary_for_midi(upper_electronic_snapshot, 54) + "`");

	mao_test::Buffer clean_buffer = {};
	const std::vector<float> clean_synth_bass_profile = {1.0f, 0.10f, 0.045f, 0.015f};
	add_harmonic_note(clean_buffer, 56, 0.26f, clean_synth_bass_profile);

	const auto clean_snapshot =
		analyze_buffer_with_mode(clean_buffer, mao::AnalysisInputMode::FullMix,
					 "speaker clean upper synth bass", 3);
	expect_label(runner, clean_snapshot.bass.label, "G#3",
		     "full-mix clean upper synth bass ownership");
	runner.expect(grid_level_for_midi(clean_snapshot.bass_notes, 56) > 0.0f,
		      std::string("full-mix clean upper synth bass: expected G#3 in bass note grid, "
				  "got bass `") +
			      clean_snapshot.bass.label + "`, keyboard `" + clean_snapshot.keyboard.label +
			      "`, vocal `" + clean_snapshot.vocal.label + "`, debug `" +
			      full_mix_debug_summary_for_midi(clean_snapshot, 56) + "`");

	mao_test::Buffer high_clean_buffer = {};
	const std::vector<float> high_clean_synth_bass_profile = {1.0f, 0.030f, 0.003f, 0.001f};
	add_harmonic_note(high_clean_buffer, 61, 0.26f, high_clean_synth_bass_profile);

	const auto high_clean_snapshot =
		analyze_buffer_with_mode(high_clean_buffer, mao::AnalysisInputMode::FullMix,
					 "speaker high clean synth bass", 3);
	expect_label(runner, high_clean_snapshot.bass.label, "C#4",
		     "full-mix high clean synth bass ownership");
	runner.expect(grid_level_for_midi(high_clean_snapshot.bass_notes, 61) > 0.0f,
		      std::string("full-mix high clean synth bass: expected C#4 in bass note grid, "
				  "got bass `") +
			      high_clean_snapshot.bass.label + "`, keyboard `" +
			      high_clean_snapshot.keyboard.label + "`, vocal `" +
			      high_clean_snapshot.vocal.label + "`, debug `" +
			      full_mix_debug_summary_for_midi(high_clean_snapshot, 61) + "`");
}

void check_full_mix_organ_suboctave_does_not_take_over_bass(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;

	mao_test::Buffer upper = {};
	const std::vector<float> organ_upper_profile = {1.0f, 0.10f, 0.004f};
	add_harmonic_note(upper, 65, 0.26f, organ_upper_profile);

	mao_test::Buffer suboctave_takeover = {};
	const std::vector<float> organ_suboctave_profile = {1.0f, 0.84f, 0.54f, 0.32f, 0.16f};
	add_harmonic_note(suboctave_takeover, 53, 0.24f, organ_suboctave_profile);

	mao::AnalysisSnapshot snapshot = {};
	for (int frame = 0; frame < 3; ++frame)
		snapshot = engine.analyze(upper.data(), upper.size(), settings, "speaker monitor", 0);
	snapshot = engine.analyze(suboctave_takeover.data(), suboctave_takeover.size(), settings,
				  "speaker monitor", 0);

	runner.expect(!grid_pitch_has_octave(snapshot.bass_notes, 5, "3"),
		      std::string("full-mix organ suboctave takeover: expected no bass F3, got bass `") +
			      snapshot.bass.label + "`, keyboard `" + snapshot.keyboard.label + "`, guitar `" +
			      snapshot.guitar.label + "`, other `" + snapshot.other.label + "`, debug `" +
			      full_mix_debug_summary_for_midi(snapshot, 53) + "`");
}

void check_full_mix_organ_partial_does_not_take_over_guitar(Runner &runner)
{
	mao_test::Buffer buffer = {};
	const std::vector<float> organ_partial_profile = {1.0f, 3.90f, 0.040f, 0.016f, 0.002f};
	add_harmonic_note(buffer, 80, 0.060f, organ_partial_profile);

	const auto snapshot =
		analyze_buffer_with_mode(buffer, mao::AnalysisInputMode::FullMix,
					 "speaker organ keyboard", 3);
	expect_global_pitch_class(runner, snapshot, 8, "full-mix organ partial global");
	runner.expect(!grid_pitch_active(snapshot.guitar_notes, 8),
		      std::string("full-mix organ partial guitar shadow: expected no G# guitar row, "
				  "got guitar `") +
			      snapshot.guitar.label + "`, keyboard `" + snapshot.keyboard.label +
			      "`, debug `" + full_mix_debug_summary_for_midi(snapshot, 80) + "`");
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

	expect_chord_label_present(runner, snapshot.global_chord.label, "C",
				   "multi-instrument mix global chord");
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

	mao::AnalysisEngine drum_engine;
	mao::AnalysisSnapshot drum_snapshot = {};
	for (int frame = 0; frame < 8; ++frame) {
		mao_test::Buffer sustain = {};
		add_harmonic_note_at_offset(sustain, 36, 0.12f, bass_profile, static_cast<uint64_t>(frame) * 2400);
		drum_snapshot = drum_engine.analyze(sustain.data(), sustain.size(), settings, "E-GMD drums", 0);
	}

	mao_test::Buffer low_kick = {};
	add_decayed_sine(low_kick, 65.0f, 0.28f, 1500);
	add_decayed_sine(low_kick, 130.0f, 0.12f, 900);
	drum_snapshot = drum_engine.analyze(low_kick.data(), low_kick.size(), settings, "E-GMD drums", 0);
	runner.expect(drum_snapshot.drums[mao::Kick].active,
		      "explicit drum source low kick: expected kick active, level " +
			      std::to_string(drum_snapshot.drums[mao::Kick].level) + " tom " +
			      std::to_string(drum_snapshot.drums[mao::Tom].level));
}

void check_real_drum_track_tom_bleed_suppression(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	mao::AnalysisSnapshot snapshot = {};

	for (int frame = 0; frame < 2; ++frame) {
		mao_test::Buffer warmup = {};
		add_decayed_sine(warmup, 500.0f, 0.006f, 1000);
		snapshot = engine.analyze(warmup.data(), warmup.size(), settings, "E-GMD drums", 0);
	}
	for (int frame = 0; frame < 3; ++frame) {
		mao_test::Buffer buffer = {};
		add_decayed_sine(buffer, 160.0f, 0.090f, 1500);
		add_decayed_sine(buffer, 220.0f, 0.110f, 1300);
		add_decayed_sine(buffer, 750.0f, 0.050f, 900);
		add_decayed_sine(buffer, 1100.0f, 0.036f, 800);
		add_decayed_sine(buffer, 90.0f, 0.008f, 1400);
		add_decayed_sine(buffer, 120.0f, 0.065f, 1400);
		add_decayed_sine(buffer, 320.0f, 0.060f, 1200);
		add_decayed_sine(buffer, 3600.0f, 0.360f, 520);
		add_decayed_sine(buffer, 5600.0f, 0.460f, 480);
		add_decayed_sine(buffer, 7600.0f, 0.380f, 460);
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "E-GMD drums", 0);
	}

	runner.expect(snapshot.drums[mao::Snare].active,
		      "real drum track tom bleed: expected snare active, level " +
			      std::to_string(snapshot.drums[mao::Snare].level));
	const bool cymbal_active = snapshot.drums[mao::HiHat].active ||
				   snapshot.drums[mao::Crash].active ||
				   snapshot.drums[mao::Ride].active;
	runner.expect(cymbal_active,
		      "real drum track tom bleed: expected active cymbal context, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level) + " high " +
			      std::to_string(snapshot.high_energy));
	runner.expect(!snapshot.drums[mao::Tom].active,
		      "real drum track tom bleed: expected tom inactive, level " +
			      std::to_string(snapshot.drums[mao::Tom].level) + " body " +
			      std::to_string(snapshot.drum_debug_tom_body) + " snare " +
			      std::to_string(snapshot.drum_debug_snare_body) + " upper " +
			      std::to_string(snapshot.drum_debug_upper_tom_body) + " shape " +
			      std::to_string(snapshot.drum_debug_body_shape));
}

void check_real_drum_track_embedded_hihat_survives_bleed_cap(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	mao::AnalysisSnapshot snapshot = {};

	for (int frame = 0; frame < 4; ++frame) {
		mao_test::Buffer warmup = {};
		add_decayed_sine(warmup, 120.0f, 0.012f, 1400);
		snapshot = engine.analyze(warmup.data(), warmup.size(), settings, "E-GMD drums", 0);
	}

	for (int frame = 0; frame < 2; ++frame) {
		mao_test::Buffer buffer = {};
		add_decayed_sine(buffer, 90.0f, 0.15f, 1500);
		add_decayed_sine(buffer, 150.0f, 0.12f, 1400);
		add_decayed_sine(buffer, 220.0f, 0.085f, 1200);
		add_decayed_sine(buffer, 3600.0f, 0.110f, 520);
		add_decayed_sine(buffer, 5600.0f, 0.125f, 480);
		add_decayed_sine(buffer, 7600.0f, 0.105f, 460);
		snapshot = engine.analyze(buffer.data(), buffer.size(), settings, "E-GMD drums", 0);
	}

	runner.expect(snapshot.drums[mao::HiHat].active,
		      "real drum track embedded hihat: expected hihat active, level " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " supported " +
			      std::to_string(snapshot.drum_debug_shape_supported[mao::HiHat]) +
			      " threshold " +
			      std::to_string(snapshot.drum_debug_trigger_thresholds[mao::HiHat]) +
			      " trigger " +
			      std::to_string(snapshot.drum_debug_trigger_scores[mao::HiHat]) + " high " +
			      std::to_string(snapshot.high_energy));
	runner.expect(snapshot.drums[mao::HiHat].level >= 0.34f,
		      "real drum track embedded hihat: expected hihat above weak-bleed cap, level " +
			      std::to_string(snapshot.drums[mao::HiHat].level));
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
	expect_chord_label_present(runner, snapshot.global_chord.label, "D",
				   "dense multi-instrument mix global chord");
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
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Tom].level + 0.02f,
		      "soft drum transient stream: expected snare to outrank tom, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " tom " +
			      std::to_string(snapshot.drums[mao::Tom].level));

	for (int i = 0; i < 4; ++i)
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao::AnalysisEngine low_body_snare_engine;
	for (int i = 0; i < 6; ++i)
		snapshot = low_body_snare_engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer low_body_snare = background;
	add_decayed_sine(low_body_snare, 78.0f, 0.035f, 1200);
	add_decayed_sine(low_body_snare, 190.0f, 0.180f, 1300);
	add_decayed_sine(low_body_snare, 1800.0f, 0.080f, 800);
	snapshot = low_body_snare_engine.analyze(low_body_snare.data(), low_body_snare.size(), settings,
						 "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "low-body snare transient: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Kick].level,
		      "low-body snare transient: expected snare not kick primary, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Rim].level,
		      "low-body snare transient: expected snare not rim primary, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " rim " +
			      std::to_string(snapshot.drums[mao::Rim].level));

	mao::AnalysisEngine kick_backed_snare_engine;
	for (int i = 0; i < 6; ++i)
		snapshot = kick_backed_snare_engine.analyze(background.data(), background.size(), settings,
							    "Mic/Aux", 0);

	mao_test::Buffer kick_backed_snare = background;
	add_decayed_sine(kick_backed_snare, 65.0f, 0.55f, 1500);
	add_decayed_sine(kick_backed_snare, 90.0f, 0.17f, 1100);
	add_decayed_sine(kick_backed_snare, 120.0f, 0.10f, 820);
	add_decayed_sine(kick_backed_snare, 190.0f, 0.12f, 1300);
	add_decayed_sine(kick_backed_snare, 220.0f, 0.080f, 1100);
	add_decayed_sine(kick_backed_snare, 1100.0f, 0.12f, 520);
	add_decayed_sine(kick_backed_snare, 2200.0f, 0.035f, 430);
	snapshot = kick_backed_snare_engine.analyze(kick_backed_snare.data(),
						   kick_backed_snare.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Kick].active,
		      "kick-backed snare transient: expected kick active, kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(snapshot.drums[mao::Snare].active,
		      "kick-backed snare transient: expected embedded snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level) + " tom " +
			      std::to_string(snapshot.drums[mao::Tom].level));

	mao::AnalysisEngine bright_snare_engine;
	for (int i = 0; i < 6; ++i)
		snapshot = bright_snare_engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer bright_snare = background;
	add_decayed_sine(bright_snare, 160.0f, 0.070f, 1300);
	add_decayed_sine(bright_snare, 220.0f, 0.085f, 1100);
	add_decayed_sine(bright_snare, 650.0f, 0.045f, 720);
	add_decayed_sine(bright_snare, 1100.0f, 0.090f, 520);
	add_decayed_sine(bright_snare, 2200.0f, 0.040f, 430);
	snapshot = bright_snare_engine.analyze(bright_snare.data(), bright_snare.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "bright snare transient: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " rim " +
			      std::to_string(snapshot.drums[mao::Rim].level));
	runner.expect(snapshot.drums[mao::Rim].active,
		      "bright snare transient: expected rim evidence active for regression, rim " +
			      std::to_string(snapshot.drums[mao::Rim].level));
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Rim].level,
		      "bright snare transient: expected snare not rim primary, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " rim " +
			      std::to_string(snapshot.drums[mao::Rim].level));

	mao::AnalysisEngine crash_backed_snare_engine;
	for (int i = 0; i < 6; ++i)
		snapshot = crash_backed_snare_engine.analyze(background.data(), background.size(), settings,
							     "drum sample", 0);

	mao_test::Buffer crash_backed_snare = background;
	add_decayed_sine(crash_backed_snare, 160.0f, 0.070f, 1300);
	add_decayed_sine(crash_backed_snare, 220.0f, 0.085f, 1100);
	add_decayed_sine(crash_backed_snare, 650.0f, 0.045f, 720);
	add_decayed_sine(crash_backed_snare, 1100.0f, 0.090f, 520);
	add_decayed_sine(crash_backed_snare, 2200.0f, 0.040f, 430);
	add_decayed_sine(crash_backed_snare, 5200.0f, 0.050f, 820);
	add_decayed_sine(crash_backed_snare, 7600.0f, 0.045f, 680);
	snapshot = crash_backed_snare_engine.analyze(crash_backed_snare.data(),
						    crash_backed_snare.size(), settings, "drum sample", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "crash-backed snare sample: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " rim " +
			      std::to_string(snapshot.drums[mao::Rim].level));
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Rim].level,
		      "crash-backed snare sample: expected snare not rim primary, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " rim " +
			      std::to_string(snapshot.drums[mao::Rim].level) + " high " +
			      std::to_string(snapshot.high_energy) + " body_shape " +
			      std::to_string(snapshot.drum_debug_body_shape) + " transient " +
			      std::to_string(snapshot.drum_debug_transient_ratio) + " onset " +
			      std::to_string(snapshot.drum_debug_onset) + " upper_tom " +
			      std::to_string(snapshot.drum_debug_upper_tom_body) + " snare_body " +
			      std::to_string(snapshot.drum_debug_snare_body) + " tom_body " +
			      std::to_string(snapshot.drum_debug_tom_body));

	mao::AnalysisEngine low_kickish_snare_engine;
	for (int i = 0; i < 6; ++i)
		snapshot = low_kickish_snare_engine.analyze(background.data(), background.size(), settings,
							    "drum sample", 0);

	mao_test::Buffer low_kickish_snare = background;
	add_decayed_sine(low_kickish_snare, 65.0f, 0.52f, 1500);
	add_decayed_sine(low_kickish_snare, 90.0f, 0.18f, 1100);
	add_decayed_sine(low_kickish_snare, 120.0f, 0.10f, 820);
	add_decayed_sine(low_kickish_snare, 160.0f, 0.085f, 1300);
	add_decayed_sine(low_kickish_snare, 220.0f, 0.095f, 1100);
	add_decayed_sine(low_kickish_snare, 1100.0f, 0.090f, 520);
	add_decayed_sine(low_kickish_snare, 2200.0f, 0.045f, 430);
	add_decayed_sine(low_kickish_snare, 5600.0f, 0.030f, 460);
	add_decayed_sine(low_kickish_snare, 7600.0f, 0.028f, 420);
	snapshot = low_kickish_snare_engine.analyze(low_kickish_snare.data(),
						    low_kickish_snare.size(), settings, "drum sample", 0);
	runner.expect(snapshot.drums[mao::Snare].active,
		      "low-kick one-shot snare sample: expected snare active, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(snapshot.drums[mao::Snare].level >= snapshot.drums[mao::Kick].level,
		      "low-kick one-shot snare sample: expected snare not kick primary, snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));

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

void check_embedded_rim_side_stick_transient(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.analysis_interval_seconds = 0.05f;
	mao_test::Buffer background = mao_test::make_midi_notes({60, 64, 67}, 0.018f);
	mao::AnalysisSnapshot snapshot = {};

	for (int i = 0; i < 6; ++i)
		snapshot = engine.analyze(background.data(), background.size(), settings, "Mic/Aux", 0);

	mao_test::Buffer rim = background;
	add_decayed_sine(rim, 160.0f, 0.045f, 1400);
	add_decayed_sine(rim, 220.0f, 0.040f, 1150);
	add_decayed_sine(rim, 650.0f, 0.034f, 520);
	add_decayed_sine(rim, 1100.0f, 0.064f, 430);
	add_decayed_sine(rim, 2200.0f, 0.024f, 360);
	snapshot = engine.analyze(rim.data(), rim.size(), settings, "Mic/Aux", 0);
	runner.expect(snapshot.drums[mao::Rim].active,
		      "embedded rim side-stick transient: expected rim active, rim " +
			      std::to_string(snapshot.drums[mao::Rim].level) + " snare " +
			      std::to_string(snapshot.drums[mao::Snare].level) + " tom " +
			      std::to_string(snapshot.drums[mao::Tom].level));
	runner.expect(!snapshot.drums[mao::Kick].active,
		      "embedded rim side-stick transient: expected no kick false positive, kick " +
			      std::to_string(snapshot.drums[mao::Kick].level));
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
	runner.expect(snapshot.drums[mao::Crash].level >= snapshot.drums[mao::HiHat].level &&
			      snapshot.drums[mao::Crash].level >= snapshot.drums[mao::Ride].level,
		      "highest cymbal probe: expected crash to be strongest, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level));
	runner.expect(snapshot.drums[mao::Crash].level -
				      std::min(snapshot.drums[mao::HiHat].level,
					       snapshot.drums[mao::Ride].level) >=
			      0.03f,
		      "highest cymbal probe: expected separated cymbal levels, hihat " +
			      std::to_string(snapshot.drums[mao::HiHat].level) + " crash " +
			      std::to_string(snapshot.drums[mao::Crash].level) + " ride " +
			      std::to_string(snapshot.drums[mao::Ride].level));
}

void check_strong_drum_levels_keep_headroom(Runner &runner)
{
	mao_test::Buffer buffer = {};
	add_decayed_sine(buffer, 65.0f, 0.85f, 1400);
	add_decayed_sine(buffer, 1100.0f, 0.28f, 520);
	const auto snapshot = analyze_buffer(buffer, "Mic/Aux");

	runner.expect(snapshot.drums[mao::Kick].active,
		      "strong drum level headroom: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	for (const mao::DrumState &drum : snapshot.drums) {
		if (!drum.active)
			continue;
		runner.expect(drum.level < 0.98f,
			      std::string("strong drum level headroom: expected active ") + drum.label +
				      " below full-scale saturation, got " + std::to_string(drum.level));
	}
}

void check_low_dominant_kick_suppresses_body_bleed(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer kick = {};
	add_decayed_sine(kick, 65.0f, 0.70f, 1500);
	add_decayed_sine(kick, 90.0f, 0.24f, 1100);
	add_decayed_sine(kick, 120.0f, 0.10f, 820);
	add_decayed_sine(kick, 1100.0f, 0.20f, 520);
	const auto snapshot = engine.analyze(kick.data(), kick.size(), settings, "Mic/Aux", 0);

	runner.expect(snapshot.drums[mao::Kick].active,
		      "low-dominant kick bleed: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(!snapshot.drums[mao::Tom].active,
		      "low-dominant kick bleed: expected tom inactive, level " +
			      std::to_string(snapshot.drums[mao::Tom].level));
	runner.expect(!snapshot.drums[mao::Snare].active,
		      "low-dominant kick bleed: expected snare inactive, level " +
			      std::to_string(snapshot.drums[mao::Snare].level));
	runner.expect(!snapshot.drums[mao::Rim].active,
		      "low-dominant kick bleed: expected rim inactive, level " +
			      std::to_string(snapshot.drums[mao::Rim].level));
}

void check_saturated_one_shot_kick_suppresses_tom_bleed(Runner &runner)
{
	mao::AnalysisEngine engine;
	mao::AnalysisSettings settings = mao_test::default_settings();
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_interval_seconds = 0.05f;

	mao_test::Buffer kick = {};
	add_decayed_sine(kick, 55.0f, 0.52f, 1600);
	add_decayed_sine(kick, 72.0f, 0.88f, 1500);
	add_decayed_sine(kick, 95.0f, 0.34f, 1200);
	add_decayed_sine(kick, 125.0f, 0.22f, 900);
	add_decayed_sine(kick, 180.0f, 0.13f, 820);
	add_decayed_sine(kick, 1100.0f, 0.34f, 520);
	const auto snapshot = engine.analyze(kick.data(), kick.size(), settings, "drum sample", 0);

	runner.expect(snapshot.drums[mao::Kick].active,
		      "saturated one-shot kick bleed: expected kick active, level " +
			      std::to_string(snapshot.drums[mao::Kick].level));
	runner.expect(!snapshot.drums[mao::Tom].active,
		      "saturated one-shot kick bleed: expected tom inactive, level " +
			      std::to_string(snapshot.drums[mao::Tom].level) + " kick " +
			      std::to_string(snapshot.drums[mao::Kick].level) + " body_shape " +
			      std::to_string(snapshot.drum_debug_body_shape) + " kick_body " +
			      std::to_string(snapshot.drum_debug_kick_body) + " tom_body " +
			      std::to_string(snapshot.drum_debug_tom_body));
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
	check_isolated_bass_periodic_fundamental_rescue(runner);
	check_isolated_bass_upper_note_not_third_partial_alias(runner);
	check_full_mix_bass_conservative_switching(runner);
	check_full_mix_electronic_bass_visual_floor(runner);
	check_full_mix_low_electronic_bass_visual_floor(runner);
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
	check_real_drum_track_tom_bleed_suppression(runner);
	check_real_drum_track_embedded_hihat_survives_bleed_cap(runner);
	check_same_instrument_timbre_variants(runner);
	check_distorted_midi_guitar_timbre(runner);
	check_isolated_guitar_octave_harmonic_display(runner);
	check_isolated_keyboard_low_octave_display(runner);
	check_spillover_regressions(runner);
	check_high_full_mix_cluster_not_vocal_or_other(runner);
	check_full_mix_single_instrument_precision(runner);
	check_full_mix_single_owned_note_has_no_instrument_chord(runner);
	check_simultaneous_onset_group_rejects_vocal_spillover(runner);
	check_blended_ambiguous_debug_scores(runner);
	check_full_mix_vocal_requires_temporal_confirmation(runner);
	check_full_mix_midrange_vocal_recall(runner);
	check_full_mix_stable_vocal_visual_floor(runner);
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
	check_full_mix_high_bass_range(runner);
	check_full_mix_organ_suboctave_does_not_take_over_bass(runner);
	check_full_mix_organ_partial_does_not_take_over_guitar(runner);
	check_multi_instrument_mix(runner);
	check_low_level_full_instrument_mix(runner);
	check_bass_survives_low_mid_mix(runner);
	check_bass_pluck_does_not_trigger_kick(runner);
	check_low_level_mic_aux_parts(runner);
	check_dense_multi_instrument_mix(runner);
	check_live_mic_aux_stream_low_parts(runner);
	check_soft_drum_transient_stream(runner);
	check_embedded_rim_side_stick_transient(runner);
	check_high_crash_probe_counts_as_high_energy(runner);
	check_strong_drum_levels_keep_headroom(runner);
	check_low_dominant_kick_suppresses_body_bleed(runner);
	check_saturated_one_shot_kick_suppresses_tom_bleed(runner);
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
