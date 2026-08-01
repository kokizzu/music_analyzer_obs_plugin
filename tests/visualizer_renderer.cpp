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
