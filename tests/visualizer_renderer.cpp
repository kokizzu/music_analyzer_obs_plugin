#include "../src/visualizer_renderer.cpp"

#include <cmath>
#include <cstdio>

namespace mao {
namespace {

bool near(float actual, float expected)
{
	return std::fabs(actual - expected) <= 0.001f;
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
