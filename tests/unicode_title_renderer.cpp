#include "unicode_title_renderer.hpp"
#include "visualizer_renderer.hpp"

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

	const bool rendered = mao::render_unicode_header_title(
		&visualizer, "愛昧ショコラーテ -PandaBoYremix- [0qomiyjPNDc]", 316, 12, 616, 26);
	assert(rendered);

	std::size_t changed_pixels = 0;
	for (std::size_t i = 0; i < visualizer.pixels.size(); i += 4) {
		if (visualizer.pixels[i + 0] != 12 || visualizer.pixels[i + 1] != 16 ||
		    visualizer.pixels[i + 2] != 22)
			++changed_pixels;
	}
	assert(changed_pixels > 100);

	std::cout << "unicode title renderer tests passed\n";
	return 0;
}
