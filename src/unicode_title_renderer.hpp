#pragma once

#include <string>

namespace mao {

struct VisualizerRenderer;

// Draws UTF-8 text directly into the visualizer's existing RGBA pixel buffer.
// Long text scrolls by pixels inside max_width. Returns false without modifying
// the buffer when the runtime Pango/Cairo stack is unavailable.
bool render_unicode_header_title(VisualizerRenderer *visualizer, const std::string &text, int x, int y,
				 int max_width, int target_height, float scroll_seconds = 0.0f);

} // namespace mao
