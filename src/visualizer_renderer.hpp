#pragma once

#include "analyzer.hpp"
#include "fret_control.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao {

// The Complete view keeps its content compact: its narrower summary column
// and aligned ROOT/BPM row fit inside this 840x480 canvas without empty tails.
constexpr uint32_t kDefaultVisualizerWidth = 840;
constexpr uint32_t kDefaultVisualizerHeight = 480;
constexpr uint32_t kBassGuitarVisualizerWidth = 960;
constexpr uint32_t kBassGuitarVisualizerHeight = 420;

enum class VisualizerLayoutMode {
	Complete,
	BassGuitar,
};

struct DrumBar {
	float age = 0.0f;
	float level = 0.0f;
	bool is_peak = false;
	uint64_t sequence = 0;
};

struct StableDisplayState {
	struct Vote {
		char label[64] = {};
		float score = 0.0f;
		uint64_t sequence = 0;
	};

	char label[64] = {};
	uint64_t last_sequence = 0;
	std::size_t vote_pos = 0;
	std::size_t vote_count = 0;
	std::array<Vote, 32> votes = {};
};

struct VisualizerRenderer {
	uint32_t width = kDefaultVisualizerWidth;
	uint32_t height = kDefaultVisualizerHeight;
	uint8_t background_opacity = 112;
	VisualizerLayoutMode layout_mode = VisualizerLayoutMode::Complete;
	// OTHERS is intentionally dormant: it is neither detected nor rendered in
	// the live visualizers.  Keep this local fallback false as well as the
	// global rendering gate, so a new renderer cannot reserve space for it.
	bool show_other_row = false;
	uint64_t drum_history_sequence = 0;
	std::array<std::vector<DrumBar>, kDrumCount> drum_history = {};
	// A white accent is applied only when a lower bar confirms that the
	// preceding highest bar was a local crest.  Equal-height bars leave the
	// current crest unchanged, so a plateau produces one accent at most.
	std::array<float, kDrumCount> drum_peak_candidate_levels = {};
	std::array<uint64_t, kDrumCount> drum_peak_candidate_sequences = {};
	std::array<float, kDrumCount> drum_peak_trough_levels = {};
	std::array<bool, kDrumCount> drum_peak_tracking_trough = {};
	std::array<StableDisplayState, 5> stable_labels = {};
	ExternalControlDisplay external_control = {};
	std::vector<uint8_t> pixels;
};

void resize_visualizer(VisualizerRenderer *visualizer, uint32_t width, uint32_t height);
bool snapshot_resets_visualizer_age(const AnalysisSnapshot &snapshot);
void format_visualizer_status_line(char *output, std::size_t output_size, const AnalysisSnapshot &snapshot,
				   float snapshot_age);
void render_visualizer(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age);
bool advance_visualizer_drum_history(VisualizerRenderer *visualizer, float seconds);
bool append_visualizer_drum_hits(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot);

} // namespace mao
