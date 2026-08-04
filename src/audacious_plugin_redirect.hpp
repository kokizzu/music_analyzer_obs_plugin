#pragma once

// Parse the original declarations before redirecting the three call sites
// inside plugin.cpp. This avoids rewriting libobs's own declarations.
#include <obs.h>

#include "audacious_overlay.hpp"
#include "visualizer_renderer.hpp"

#define render_visualizer render_visualizer_with_audacious
#define obs_source_draw mao::audacious_obs_source_draw

// OBS exposes obs_register_source as a convenience macro on some versions.
// Preserve its behavior in audacious_registration.cpp, but replace the macro
// only for plugin.cpp after obs.h has already been parsed.
#ifdef obs_register_source
#undef obs_register_source
#endif
#define obs_register_source mao::audacious_obs_register_source
