#define main native_pair_reference_main
#include "analyzer_real_note_samples.cpp"
#undef main
#include "non_tempo_snapshot.hpp"
#include <chrono>
#include <set>

static std::set<int> visible_notes(const mao::NoteGrid &grid)
{
	std::set<int> result;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && note_cell_visual_level(cell) > 0) result.insert(cell.midi);
	return result;
}

static std::set<int> any_notes(const mao::AnalysisSnapshot &snapshot)
{
	std::set<int> result;
	for (const auto *grid : {&snapshot.bass_notes, &snapshot.guitar_notes, &snapshot.keyboard_notes,
		&snapshot.vocal_notes, &snapshot.other_notes, &snapshot.ambiguous_notes}) {
		const auto notes = visible_notes(*grid);
		result.insert(notes.begin(), notes.end());
	}
	return result;
}

static std::string serialized(const std::set<int> &notes)
{
	std::string result;
	for (int midi : notes) result += (result.empty() ? "" : ",") + std::to_string(midi);
	return result;
}

int main(int argc, char **argv)
{
	if (argc != 3) return 2;
	std::vector<SampleRow> samples;
	if (!read_manifest(join_path(argv[1], "manifest.tsv"), samples)) return 1;
	std::ofstream output(argv[2]);
	if (!output) return 1;
	output << "sample_id\tfamily\texpected_midi\tend_sample\trate\tvoice_before\tvoice_after\tall_lost\tother_difference\tbpm_changed\texisting_voice_changed\tbefore_ms\tafter_ms\n";
	for (const auto &sample : samples) {
		std::vector<float> pcm;
		uint32_t rate = 0;
		std::string error;
		if (!read_wav_mono(join_path(argv[1], sample.path), pcm, rate, error) || rate < 8000 || rate > 192000) {
			std::fprintf(stderr, "Unable to read sample %s: %s\n", sample.id.c_str(), error.c_str());
			return 1;
		}
		mao::AnalysisSettings settings;
		settings.sample_rate = rate;
		settings.analysis_interval_seconds = .05f;
		settings.analysis_window_seconds = .1f;
		settings.analysis_window_samples = 0;
		settings.enable_vocal_detection = settings.enable_other_detection = true;
		settings.experimental_pcm_tempo_correction = false;
		settings.input_mode = mao::AnalysisInputMode::FullMix;
		auto baseline = std::make_unique<mao::AnalysisEngine>();
		auto trial = std::make_unique<mao::AnalysisEngine>();
		std::vector<float> window(mao::resolve_analysis_window_samples(settings), 0);
		const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
		for (std::size_t end = hop; end <= pcm.size(); end += hop) {
			std::move(window.begin() + hop, window.end(), window.begin());
			std::copy(pcm.begin() + end - hop, pcm.begin() + end, window.end() - hop);
			settings.experimental_keyboard_voice_suppression = false;
			const auto started = std::chrono::steady_clock::now();
			const auto before = baseline->analyze(window.data(), window.size(), settings, "native timbre pair", 0);
			const auto middle = std::chrono::steady_clock::now();
			settings.experimental_keyboard_voice_suppression = true;
			const auto after = trial->analyze(window.data(), window.size(), settings, "native timbre pair", 0);
			const auto finished = std::chrono::steady_clock::now();
			auto comparable = after;
			comparable.vocal_notes = before.vocal_notes;
			comparable.vocal = before.vocal;
			const char *difference = mao_test::non_tempo_difference(before, comparable);
			std::set<int> lost;
			const auto all_before = any_notes(before), all_after = any_notes(after);
			std::set_difference(all_before.begin(), all_before.end(), all_after.begin(), all_after.end(), std::inserter(lost, lost.end()));
			bool existing_changed = false;
			for (std::size_t row = 0; row < before.vocal_notes.rows.size(); ++row)
				for (std::size_t pc = 0; pc < 12; ++pc) {
					const auto &a = before.vocal_notes.rows[row][pc], &b = after.vocal_notes.rows[row][pc];
					if (a.active && b.active && !mao_test::same_cell(a, b)) existing_changed = true;
				}
			output << sample.id << '\t' << sample.family << '\t' << sample.midi << '\t' << end << '\t' << rate << '\t'
				<< serialized(visible_notes(before.vocal_notes)) << '\t' << serialized(visible_notes(after.vocal_notes)) << '\t'
				<< serialized(lost) << '\t' << (difference ? difference : "") << '\t'
				<< (before.estimated_bpm != after.estimated_bpm || before.bpm_confidence != after.bpm_confidence ||
					before.immediate_source_bpm != after.immediate_source_bpm) << '\t' << existing_changed << '\t'
				<< std::chrono::duration<double, std::milli>(middle - started).count() << '\t'
				<< std::chrono::duration<double, std::milli>(finished - middle).count() << '\n';
		}
	}
}
