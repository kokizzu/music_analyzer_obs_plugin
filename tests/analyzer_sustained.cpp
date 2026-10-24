#include "analyzer.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <string>
#include <thread>
#include <vector>
#include <sys/resource.h>

template <typename Settings>
static auto configure_correction(Settings &settings, bool enabled, int)
	-> decltype(settings.experimental_pcm_tempo_correction = enabled, bool())
{
	settings.experimental_pcm_tempo_correction = enabled;
	return true;
}
template <typename Settings>
static bool configure_correction(Settings &, bool, long) { return false; }

template <typename Settings>
static auto configure_diagnostic_rows(Settings &settings, int)
	-> decltype(settings.enable_vocal_detection = true, settings.enable_other_detection = true, void())
{
	settings.enable_vocal_detection = settings.enable_other_detection = true;
}
template <typename Settings>
static void configure_diagnostic_rows(Settings &, long) {}

static std::string notes(const mao::NoteGrid &grid)
{
	std::set<int> result;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && (cell.visual_level < 0 ? cell.level : cell.visual_level) > 0)
			result.insert(cell.midi);
	std::string text;
	for (int midi : result) text += (text.empty() ? "" : ",") + std::to_string(midi);
	return text;
}

int main(int argc, char **argv)
{
	if (argc == 2 && std::string(argv[1]) == "--capabilities") {
		mao::AnalysisSettings settings;
		std::cout << (configure_correction(settings, false, 0) ? "pcm-correction\n" : "native-only\n");
		return 0;
	}
	if (argc != 6) return 2;
	const unsigned rate = std::stoul(argv[2]);
	if (rate < 8000 || rate > 192000) return 2;
	const bool paced = std::string(argv[4]) == "paced";
	const bool correction = std::string(argv[5]) == "corrected";
	std::ifstream input(argv[1], std::ios::binary);
	std::ofstream output(argv[3]);
	if (!input || !output) return 2;
	mao::AnalysisSettings settings;
	settings.sample_rate = rate;
	settings.analysis_window_seconds = .1f;
	settings.analysis_interval_seconds = .05f;
	configure_diagnostic_rows(settings, 0);
	const bool supports_correction = configure_correction(settings, correction, 0);
	if (correction && !supports_correction) return 2;
	auto engine = std::make_unique<mao::AnalysisEngine>();
	const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
	std::vector<float> fresh(hop), window(mao::resolve_analysis_window_samples(settings), 0);
	if (window.size() < hop) return 2;
	output << "end_sample\thop_index\tsequence\twall_ms\tcpu_ms\trss_kb\tbpm\tconfidence\tchord\tbass\tguitar\tkeys\tvoice\tother\tdrums\trms\n";
	const auto origin = std::chrono::steady_clock::now();
	std::size_t end = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		for (float sample : fresh) if (!std::isfinite(sample)) return 3;
		end += hop;
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		if (paced) std::this_thread::sleep_until(origin + std::chrono::duration_cast<std::chrono::steady_clock::duration>(std::chrono::duration<double>((end - hop) / double(rate))));
		struct rusage before{}, after{};
		getrusage(RUSAGE_SELF, &before);
		const auto started = std::chrono::steady_clock::now();
		const auto snapshot = engine->analyze(window.data(), window.size(), settings, "sustained benchmark", 0);
		const double wall = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - started).count();
		getrusage(RUSAGE_SELF, &after);
		const double cpu = (after.ru_utime.tv_sec - before.ru_utime.tv_sec + after.ru_stime.tv_sec - before.ru_stime.tv_sec) * 1000. +
			(after.ru_utime.tv_usec - before.ru_utime.tv_usec + after.ru_stime.tv_usec - before.ru_stime.tv_usec) / 1000.;
		std::string drums;
		for (const auto &drum : snapshot.drums) if (drum.active) drums += (drums.empty() ? "" : ",") + std::string(drum.label);
		output << end << '\t' << end / hop << '\t' << snapshot.sequence << '\t' << wall << '\t' << cpu << '\t' << after.ru_maxrss << '\t'
			<< snapshot.estimated_bpm << '\t' << snapshot.bpm_confidence << '\t' << snapshot.global_chord.label << '\t'
			<< notes(snapshot.bass_notes) << '\t' << notes(snapshot.guitar_notes) << '\t' << notes(snapshot.keyboard_notes) << '\t'
			<< notes(snapshot.vocal_notes) << '\t' << notes(snapshot.other_notes) << '\t' << drums << '\t' << snapshot.rms << '\n';
	}
	if (!input.eof()) return 3;
	return end > 0 ? 0 : 3;
}
