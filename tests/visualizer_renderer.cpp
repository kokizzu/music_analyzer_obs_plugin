#include "../src/visualizer_renderer.cpp"

#include <cmath>
#include <cstdio>

namespace mao {
namespace {

bool near(float actual, float expected)
{
	return std::fabs(actual - expected) <= 0.001f;
}

void set_note_cell(NoteCell &cell, int midi, float level, float visual_level)
{
	cell = {};
	std::snprintf(cell.label, sizeof(cell.label), "4");
	cell.midi = midi;
	cell.level = level;
	cell.visual_level = visual_level;
	cell.active = true;
}

void expect_true(bool condition, const char *message, int *checks, int *failures)
{
	++*checks;
	if (!condition) {
		std::fprintf(stderr, "visualizer_renderer_tests: %s\n", message);
		++*failures;
	}
}

int run_visualizer_renderer_tests()
{
	int checks = 0;
	int failures = 0;

	char band[8] = {};
	format_band_percentage(band, sizeof(band), 0.0f);
	expect_true(std::strcmp(band, " 0%") == 0, "zero band percentage should use fixed width", &checks,
		    &failures);
	format_band_percentage(band, sizeof(band), 0.09f);
	expect_true(std::strcmp(band, " 9%") == 0, "single-digit band percentage should space-pad", &checks,
		    &failures);
	format_band_percentage(band, sizeof(band), 0.10f);
	expect_true(std::strcmp(band, "10%") == 0, "double-digit band percentage should not zero-pad",
		    &checks, &failures);
	format_band_percentage(band, sizeof(band), 1.0f);
	expect_true(std::strcmp(band, "MAX") == 0, "full band percentage should render as MAX", &checks,
		    &failures);

	AnalysisSnapshot tempo_snapshot;
	tempo_snapshot.tempo_debug_candidate_count = 3;
	tempo_snapshot.tempo_debug_candidates[0].bpm = 126;
	tempo_snapshot.tempo_debug_candidates[0].score = 8.0f;
	tempo_snapshot.tempo_debug_candidates[1].bpm = 63;
	tempo_snapshot.tempo_debug_candidates[1].score = 6.0f;
	tempo_snapshot.tempo_debug_candidates[2].bpm = 189;
	tempo_snapshot.tempo_debug_candidates[2].score = 4.0f;
	char bpm_candidates[64] = {};
	format_bpm_candidate_list(bpm_candidates, sizeof(bpm_candidates), tempo_snapshot);
	expect_true(std::strcmp(bpm_candidates, "CAND 126:100 63:75 189:50") == 0,
		    "BPM candidate formatter should show relative scores", &checks, &failures);
	tempo_snapshot.estimated_bpm = 126.0f;
	tempo_snapshot.bpm_confidence = kBpmDisplayConfidenceThreshold - 0.01f;
	expect_true(!has_displayable_bpm(tempo_snapshot),
		    "BPM display should hide estimates below the confidence threshold", &checks, &failures);
	tempo_snapshot.bpm_confidence = kBpmDisplayConfidenceThreshold;
	expect_true(has_displayable_bpm(tempo_snapshot),
		    "BPM display should show estimates at the confidence threshold", &checks, &failures);

	expect_true(near(display_highlight_level(0.0f), 0.0f), "zero level should not highlight", &checks,
		    &failures);
	expect_true(near(display_highlight_level(0.01f), 0.04f),
		    "weak note levels should fade linearly below the full-highlight threshold", &checks, &failures);
	expect_true(near(display_highlight_level(0.125f), 0.5f),
		    "half-threshold note levels should render as half highlight", &checks, &failures);
	expect_true(near(display_highlight_level(0.25f), 1.0f),
		    "25 percent note level should render as full highlight", &checks, &failures);
	expect_true(near(display_highlight_level(1.0f), 1.0f),
		    "levels above the full-highlight threshold should clamp to full highlight", &checks, &failures);

	NoteGrid grid;
	set_note_cell(grid.rows[0][0], 40, 0.90f, 0.90f);
	set_note_cell(grid.rows[0][1], 52, 0.80f, 0.80f);
	char current_note[8] = {};
	expect_true(current_note_label(grid, current_note, sizeof(current_note)) &&
			    std::strcmp(current_note, "E") == 0,
		    "bass and vocal chord fields should use the strongest current note label", &checks, &failures);
	expect_true(near(guitar_note_grid_midi_level(grid, 52), 0.80f * kGuitarUpperPitchClassShadowScale),
		    "guitar upper same-pitch marker should be softened but still visible", &checks, &failures);
	expect_true(display_highlight_level(guitar_note_grid_midi_level(grid, 52)) >= 1.0f,
		    "strong guitar upper same-pitch marker should still render at full brightness", &checks,
		    &failures);

	NoteGrid malformed_grid;
	NoteCell &malformed_cell = malformed_grid.rows[0][0];
	std::memset(malformed_cell.label, 'X', sizeof(malformed_cell.label));
	malformed_cell.midi = 60;
	malformed_cell.level = 1.0f;
	malformed_cell.visual_level = 1.0f;
	malformed_cell.active = true;
	set_note_cell(malformed_grid.rows[0][1], 62, 0.70f, 0.70f);
	current_note[0] = '\0';
	expect_true(current_note_label(malformed_grid, current_note, sizeof(current_note)) &&
			    std::strcmp(current_note, "D") == 0,
		    "unterminated note-cell labels must not be selected or read past their fixed buffer", &checks,
		    &failures);

	NoteGrid piano_grid;
	set_note_cell(piano_grid.rows[0][0], 60, 0.90f, 0.90f);
	set_note_cell(piano_grid.rows[0][1], 72, 0.80f, 0.80f);
	expect_true(near(piano_key_level(piano_grid, 72), 0.80f * kPianoUpperPitchClassShadowScale),
		    "piano upper same-pitch marker should be softened but still visible", &checks, &failures);
	expect_true(display_highlight_level(piano_key_level(piano_grid, 72)) >= 1.0f,
		    "strong piano upper same-pitch marker should still render at full brightness", &checks,
		    &failures);

	VisualizerRenderer renderer;
	renderer.layout_mode = VisualizerLayoutMode::Complete;
	resize_visualizer(&renderer, 960, 540);
	AnalysisSnapshot snapshot;
	snapshot.audio_seen = true;
	snapshot.rms = 0.10f;
	snapshot.sequence = 1;
	set_note_cell(snapshot.keyboard_notes.rows[0][0], 60, 0.95f, 0.10f);
	render_visualizer(&renderer, snapshot, 0.0f);
	expect_true(renderer.stable_labels[StableKeyboard].label[0] == '\0',
		    "visually suppressed note should not populate sustain", &checks, &failures);

	snapshot.sequence = 2;
	set_note_cell(snapshot.keyboard_notes.rows[0][4], 64, 0.62f, 0.62f);
	render_visualizer(&renderer, snapshot, 0.0f);
	expect_true(std::strcmp(renderer.stable_labels[StableKeyboard].label, "E") == 0,
		    "sustain should prefer rendered confidence over raw level", &checks, &failures);

	if (failures != 0)
		return 1;

	std::printf("visualizer_renderer_tests: %d checks passed\n", checks);
	return 0;
}

} // namespace
} // namespace mao

int main()
{
	return mao::run_visualizer_renderer_tests();
}
