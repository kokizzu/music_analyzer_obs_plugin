#include "analyzer.hpp"
#include "non_tempo_snapshot.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <memory>
#include <set>
#include <string>
#include <vector>

static std::set<int> notes(const mao::NoteGrid &grid)
{
	std::set<int> result;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && (cell.visual_level < 0 ? cell.level : cell.visual_level) > 0) result.insert(cell.midi);
	return result;
}
static std::string text(const std::set<int> &values)
{
	std::string result;
	for (int value : values) result += (result.empty() ? "" : ",") + std::to_string(value);
	return result;
}
static std::set<int> any_notes(const mao::AnalysisSnapshot &snapshot)
{
	std::set<int> result;
	for (const auto *grid : {&snapshot.bass_notes, &snapshot.guitar_notes, &snapshot.keyboard_notes,
		&snapshot.vocal_notes, &snapshot.other_notes, &snapshot.ambiguous_notes}) {
		const auto pitches = notes(*grid);
		result.insert(pitches.begin(), pitches.end());
	}
	return result;
}

int main(int argc, char **argv)
{
	if (argc != 4) return 2;
	const unsigned rate = std::stoul(argv[2]);
	if (rate < 8000 || rate > 192000) return 2;
	std::ifstream input(argv[1], std::ios::binary);
	std::ofstream output(argv[3]);
	if (!input || !output) return 2;
	mao::AnalysisSettings settings;
	settings.sample_rate = rate;
	settings.analysis_window_seconds = .1f;
	settings.analysis_interval_seconds = .05f;
	settings.input_mode = mao::AnalysisInputMode::FullMix;
	if (!settings.native_piano_duplicate_consensus) return 4;
	auto baseline_settings = settings;
	baseline_settings.native_piano_duplicate_consensus = false;
	auto baseline = std::make_unique<mao::AnalysisEngine>();
	auto trial = std::make_unique<mao::AnalysisEngine>();
	const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
	std::vector<float> fresh(hop), window(mao::resolve_analysis_window_samples(settings), 0);
	output << "end_sample\tbass\tguitar\tkeys\tvoice\tother\tambiguous\tchord\tbpm\tconfidence\tdrums\tafter_guitar\tafter_voice\tany_lost\tunrelated_difference\tbpm_changed\tsurvivor_changed\tbefore_ms\tafter_ms\n";
	std::size_t end = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		for (float sample : fresh) if (!std::isfinite(sample)) return 3;
		end += hop;
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		const auto begin = std::chrono::steady_clock::now();
		const auto before = baseline->analyze(window.data(), window.size(), baseline_settings, "sustained benchmark", 0);
		const auto middle = std::chrono::steady_clock::now();
		const auto after = trial->analyze(window.data(), window.size(), settings, "sustained benchmark", 0);
		const auto finish = std::chrono::steady_clock::now();
		auto comparable = after;
		comparable.guitar_notes = before.guitar_notes;
		comparable.guitar = before.guitar;
		comparable.vocal_notes = before.vocal_notes;
		comparable.vocal = before.vocal;
		const char *difference = mao_test::non_tempo_difference(before, comparable);
		const auto all_before = any_notes(before), all_after = any_notes(after);
		std::set<int> lost;
		std::set_difference(all_before.begin(), all_before.end(), all_after.begin(), all_after.end(), std::inserter(lost, lost.end()));
		bool survivor_changed = false;
		for (const auto &grids : {std::pair{&before.guitar_notes, &after.guitar_notes}, std::pair{&before.vocal_notes, &after.vocal_notes}})
			for (std::size_t row = 0; row < grids.first->rows.size(); ++row)
				for (std::size_t pc = 0; pc < 12; ++pc) {
					const auto &a = grids.first->rows[row][pc], &b = grids.second->rows[row][pc];
					if (a.active && b.active && !mao_test::same_cell(a, b)) survivor_changed = true;
				}
		std::string drums;
		for (const auto &drum : before.drums) if (drum.active) drums += (drums.empty() ? "" : ",") + std::string(drum.label);
		const bool bpm_changed = before.estimated_bpm != after.estimated_bpm || before.bpm_confidence != after.bpm_confidence ||
			before.immediate_source_bpm != after.immediate_source_bpm || before.phase_estimated_bpm != after.phase_estimated_bpm ||
			before.phase_bpm_confidence != after.phase_bpm_confidence || before.permissive_tracker_bpm != after.permissive_tracker_bpm ||
			before.permissive_tracker_confidence != after.permissive_tracker_confidence || before.high_tempo_tracker_bpm != after.high_tempo_tracker_bpm ||
			before.high_tempo_tracker_confidence != after.high_tempo_tracker_confidence;
		output << std::setprecision(6) << end << '\t' << text(notes(before.bass_notes)) << '\t' << text(notes(before.guitar_notes)) << '\t'
			<< text(notes(before.keyboard_notes)) << '\t' << text(notes(before.vocal_notes)) << '\t' << text(notes(before.other_notes)) << '\t'
			<< text(notes(before.ambiguous_notes)) << '\t' << before.global_chord.label << '\t' << before.estimated_bpm << '\t' << before.bpm_confidence << '\t' << drums << '\t'
			<< text(notes(after.guitar_notes)) << '\t' << text(notes(after.vocal_notes)) << '\t' << text(lost) << '\t' << (difference ? difference : "") << '\t' << bpm_changed << '\t' << survivor_changed << '\t'
			<< std::chrono::duration<double, std::milli>(middle - begin).count() << '\t'
			<< std::chrono::duration<double, std::milli>(finish - middle).count() << '\n';
	}
	return input.eof() && end ? 0 : 3;
}
