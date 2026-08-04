#pragma once

// Parse the original declarations before redirecting the two call sites inside
// plugin.cpp. This avoids rewriting libobs's own obs_source_draw declaration.
#include <obs.h>

#include "audacious_overlay.hpp"
#include "visualizer_renderer.hpp"

#define render_visualizer render_visualizer_with_audacious
#define obs_source_draw mao::audacious_obs_source_draw
