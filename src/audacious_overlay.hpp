#pragma once

#include <cstdint>

struct obs_source;
typedef struct obs_source obs_source_t;
struct gs_texture;
typedef struct gs_texture gs_texture_t;

namespace mao {

struct AnalysisSnapshot;
struct VisualizerRenderer;
struct AudaciousUnicodeOverlay;

void render_visualizer_with_audacious(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot,
				      float snapshot_age);

AudaciousUnicodeOverlay *create_audacious_unicode_overlay(obs_source_t *parent);
void destroy_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay);
void tick_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay);
void render_audacious_unicode_overlay(AudaciousUnicodeOverlay *overlay, uint32_t width, uint32_t height);

void audacious_obs_source_draw(gs_texture_t *texture, int x, int y, uint32_t width, uint32_t height, bool flip);

} // namespace mao
