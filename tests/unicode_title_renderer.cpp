#include "unicode_title_renderer.hpp"
#include "visualizer_renderer.hpp"

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>

int main()
{
	mao::VisualizerRenderer visualizer;
	visualizer.width = 960;
	visualizer.height = 64;
	visualizer.pixels.assign(static_cast<std::size_t>(visualizer.width) * visualizer.height * 4, 0);
	for (std::size_t i = 0; i < visualizer.pixels.size(); i += 4) {
		visualizer.pixels[i + 0] = 12;
		visualizer.pixels[i + 1] = 16;
		visualizer.pixels[i + 2] = 22;
		visualizer.pixels[i + 3] = 255;
	}

	constexpr int kTitleX = 316;
	constexpr int kTitleWidth = 584; // Ends at x=900, 8 px before the silent marker at x=908.
	const bool rendered = mao::render_unicode_header_title(
		&visualizer,
		"愛昧ショコラーテ -PandaBoYremix- [0qomiyjPNDc] EXTRA EXTRA EXTRA EXTRA",
		kTitleX, 12, kTitleWidth, 26, 1.25f);
	assert(rendered);

	std::size_t changed_pixels = 0;
	int maximum_changed_x = -1;
	for (uint32_t y = 0; y < visualizer.height; ++y) {
		for (uint32_t x = 0; x < visualizer.width; ++x) {
			const std::size_t offset =
				(static_cast<std::size_t>(y) * visualizer.width + static_cast<std::size_t>(x)) * 4;
			if (visualizer.pixels[offset + 0] != 12 || visualizer.pixels[offset + 1] != 16 ||
			    visualizer.pixels[offset + 2] != 22) {
				++changed_pixels;
				maximum_changed_x = std::max(maximum_changed_x, static_cast<int>(x));
			}
		}
	}
	assert(changed_pixels > 100);
	assert(maximum_changed_x < kTitleX + kTitleWidth);

	std::cout << "unicode title renderer tests passed\n";
	return 0;
}
