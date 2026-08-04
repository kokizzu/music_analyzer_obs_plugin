#pragma once

// Parse the original declarations before redirecting the three call sites
// inside plugin.cpp. This avoids rewriting libobs's own declarations.
#include <obs.h>

#include "audacious_overlay.hpp"
#include "visualizer_renderer.hpp"

#define render_visualizer render_visualizer_with_audacious
#define obs_source_draw mao::audacious_obs_source_draw
#define obs_register_source mao::audacious_obs_register_source
