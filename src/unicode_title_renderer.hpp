#pragma once

#include <string>

namespace mao {

struct VisualizerRenderer;

// Draws UTF-8 text directly into the visualizer's existing RGBA pixel buffer.
// Returns false without modifying the buffer when the runtime Pango/Cairo stack
// is unavailable, allowing the caller to fall back to the bitmap renderer.
bool render_unicode_header_title(VisualizerRenderer *visualizer, const std::string &text, int x, int y,
				 int max_width, int target_height);

} // namespace mao
