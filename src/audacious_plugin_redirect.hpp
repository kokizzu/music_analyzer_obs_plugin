#pragma once

// Parse the renderer declaration before redirecting only plugin.cpp's analyzer
// render calls. OBS source registration and texture drawing stay untouched.
#include "audacious_overlay.hpp"
#include "visualizer_renderer.hpp"

#define render_visualizer render_visualizer_with_audacious
