#include "analyzer.hpp"
#include "keyboard_stage_trace.hpp"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <memory>
#include <set>
#include <string>
#include <vector>

static std::string notes(const mao::NoteGrid &grid)
{
	std::set<int> midis;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && (cell.visual_level < 0 ? cell.level : cell.visual_level) > 0) midis.insert(cell.midi);
	std::string result;
	for (int midi : midis) result += (result.empty() ? "" : ",") + std::to_string(midi);
	return result;
}
int main(int argc, char **argv)
{
	if (argc != 5) return 2;
	const unsigned rate = std::stoul(argv[2]);
	std::ifstream input(argv[1], std::ios::binary);
	std::ofstream frames(argv[3]), trace(argv[4]);
	if (!input || !frames || !trace) return 2;
	mao::AnalysisSettings settings;
	settings.sample_rate = rate;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	settings.analysis_window_seconds = .1f;
	settings.analysis_interval_seconds = .05f;
	auto engine = std::make_unique<mao::AnalysisEngine>();
	const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
	std::vector<float> fresh(hop), window(mao::resolve_analysis_window_samples(settings), 0);
	frames << "end_sample\tbass\tguitar\tkeys\tvoice\tother\tambiguous\tchord\tbpm\tconfidence\tdrums\n";
	trace << "end_sample\tsequence\tstage\tbetween\tmidi\tbefore\tafter\tdirect\tadjacent\tstrongest\tharmonic\tpartials\tconsidered\n";
	std::size_t end = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		for (float sample : fresh) if (!std::isfinite(sample)) return 3;
		end += hop;
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		mao_stage_trace::state.started = false;
		const auto snapshot = engine->analyze(window.data(), window.size(), settings, "sustained benchmark", 0);
		auto &state = mao_stage_trace::state;
		if (!state.started || state.depth != 0) return 4;
		state.finish(snapshot.keyboard_notes);
		std::string drums;
		for (const auto &drum : snapshot.drums) if (drum.active) drums += (drums.empty() ? "" : ",") + std::string(drum.label);
		frames << std::setprecision(6) << end << '\t' << notes(snapshot.bass_notes) << '\t' << notes(snapshot.guitar_notes) << '\t'
			<< notes(snapshot.keyboard_notes) << '\t' << notes(snapshot.vocal_notes) << '\t' << notes(snapshot.other_notes) << '\t'
			<< notes(snapshot.ambiguous_notes) << '\t' << snapshot.global_chord.label << '\t' << snapshot.estimated_bpm << '\t'
			<< snapshot.bpm_confidence << '\t' << drums << '\n';
		trace << end << "\t0\tframe\t0\t-1\t0\t0\t0\t0\t0\t0\t0\t0\n";
		const auto metadata = [&](std::size_t index) {
			const auto &low = state.low[index];
			trace << '\t' << low.direct << '\t' << low.adjacent << '\t' << low.strongest << '\t' << low.harmonic
				<< '\t' << low.partials << '\t' << low.considered << '\n';
		};
		unsigned sequence = 0;
		for (std::size_t i = 0; i < state.initial.size(); ++i)
			if (state.initial[i] > 0) {
				trace << std::setprecision(9) << end << '\t' << ++sequence << "\tinitial\t0\t"
					<< i + mao::kFirstAnalyzedMidi << "\t0\t" << state.initial[i];
				metadata(i);
			}
		for (const auto &event : state.events) {
			trace << std::setprecision(9) << end << '\t' << ++sequence << '\t' << event.stage << '\t' << event.between << '\t'
				<< event.midi << '\t' << event.before << '\t' << event.after;
			metadata(static_cast<std::size_t>(event.midi - mao::kFirstAnalyzedMidi));
		}
	}
	return input.eof() && end ? 0 : 3;
}
