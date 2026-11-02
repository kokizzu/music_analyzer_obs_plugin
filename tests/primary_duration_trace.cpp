#include "analyzer.hpp"
#include "primary_duration_trace.hpp"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <memory>
#include <set>
#include <string>
#include <vector>

static float visual(const mao::NoteGrid &grid, int midi)
{
	float value = 0;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi == midi)
			value = std::max(value, cell.visual_level < 0 ? cell.level : cell.visual_level);
	return value;
}
static std::string notes(const mao::NoteGrid &grid)
{
	std::set<int> values;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && (cell.visual_level < 0 ? cell.level : cell.visual_level) > 0)
			values.insert(cell.midi);
	std::string result;
	for (int midi : values) result += (result.empty() ? "" : ",") + std::to_string(midi);
	return result;
}

int main(int argc, char **argv)
{
	if (argc != 5) return 2;
	const unsigned rate = std::stoul(argv[2]);
	std::ifstream input(argv[1], std::ios::binary);
	std::ofstream frames(argv[3]), trace(argv[4]);
	if (!input || !frames || !trace || rate < 8000 || rate > 192000) return 2;
	mao::AnalysisSettings settings;
	settings.sample_rate = rate;
	settings.analysis_window_seconds = .1f;
	settings.analysis_interval_seconds = .05f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	auto engine = std::make_unique<mao::AnalysisEngine>();
	const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
	std::vector<float> fresh(hop), window(mao::resolve_analysis_window_samples(settings), 0);
	frames << "end_sample\tbass\tguitar\tkeys\tvoice\tother\tambiguous\tchord\tbpm\tconfidence\tdrums\n";
	trace << "end_sample\tmidi\traw\tsmoothed\tfinal\tenvelope\tdisplay_scale\thits\tmisses\tconfirmed\n";
	std::size_t end = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		for (float sample : fresh) if (!std::isfinite(sample)) return 3;
		end += hop;
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		mao_duration_trace::state = {};
		const auto snapshot = engine->analyze(window.data(), window.size(), settings, "sustained benchmark", 0);
		const auto &state = mao_duration_trace::state;
		if (!state.captured_raw || !state.captured_smoothing) return 4;
		std::string drums;
		for (const auto &drum : snapshot.drums) if (drum.active)
			drums += (drums.empty() ? "" : ",") + std::string(drum.label);
		frames << std::setprecision(6) << end << '\t' << notes(snapshot.bass_notes) << '\t' << notes(snapshot.guitar_notes) << '\t'
			<< notes(snapshot.keyboard_notes) << '\t' << notes(snapshot.vocal_notes) << '\t' << notes(snapshot.other_notes) << '\t'
			<< notes(snapshot.ambiguous_notes) << '\t' << snapshot.global_chord.label << '\t' << snapshot.estimated_bpm << '\t'
			<< snapshot.bpm_confidence << '\t' << drums << '\n';
		for (int midi = mao::kFirstAnalyzedMidi; midi <= mao::kLastAnalyzedMidi; ++midi) {
			const auto &tracking = state.tracking[static_cast<std::size_t>(midi - mao::kFirstAnalyzedMidi)];
			trace << std::setprecision(9) << end << '\t' << midi << '\t' << visual(state.raw_keys, midi) << '\t'
				<< visual(state.smoothed_keys, midi) << '\t' << visual(snapshot.keyboard_notes, midi) << '\t'
				<< tracking.envelope << '\t' << tracking.display_scale << '\t' << tracking.consecutive_hits << '\t'
				<< tracking.consecutive_misses << '\t' << tracking.confirmed << '\n';
		}
	}
	return input.eof() && end ? 0 : 3;
}
