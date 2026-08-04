#pragma once

namespace mao {

struct AnalysisSnapshot;
struct VisualizerRenderer;

void render_visualizer_with_audacious(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot,
                                      float snapshot_age);

} // namespace mao
