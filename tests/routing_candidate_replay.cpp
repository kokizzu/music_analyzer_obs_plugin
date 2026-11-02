#include "analyzer.hpp"
#include "native_timbre_features.hpp"
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
	std::set<int> pitches;
	for (const auto &row : grid.rows) for (const auto &cell : row)
		if (cell.active && cell.midi >= 0 && (cell.visual_level < 0 ? cell.level : cell.visual_level) > 0) pitches.insert(cell.midi);
	std::string result;
	for (int midi : pitches) result += (result.empty() ? "" : ",") + std::to_string(midi);
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
	auto engine = std::make_unique<mao::AnalysisEngine>();
	mao::timbre::CepstralExtractor extractor;
	const std::size_t hop = static_cast<std::size_t>(rate * .05 + .5);
	std::vector<float> fresh(hop), window(mao::resolve_analysis_window_samples(settings), 0);
	output << "end_sample\tbass\tguitar\tkeys\tvoice\tother\tambiguous\tchord\tbpm\tconfidence\tdrums"
		<< "\tmidi\towner\townership\tonset\tdecay\tpitch_stability\tsimultaneous_onset\tbass_score\tkeyboard_score\tguitar_score\tvocal_score\tother_score"
		<< "\tlevel\tpitch\tperiodicity\tharmonicity\tfit\tcentroid\tslope\tnoise\tlower_octave\tproduct\tsubharmonic\tadjacent_lower\tadjacent_upper\tthird_octave\tprofile\tpolyphony_rejected";
	for (int i = 0; i < 5; ++i) output << "\tpartial" << i;
	output << "\tmfcc_valid";
	for (int i = 0; i < 24; ++i) output << "\tmfcc" << i;
	output << '\n';
	std::size_t end = 0;
	while (input.read(reinterpret_cast<char *>(fresh.data()), hop * sizeof(float))) {
		for (float sample : fresh) if (!std::isfinite(sample)) return 3;
		end += hop;
		std::move(window.begin() + hop, window.end(), window.begin());
		std::copy(fresh.begin(), fresh.end(), window.end() - hop);
		const auto snapshot = engine->analyze(window.data(), window.size(), settings, "sustained benchmark", 0);
		mao::timbre::Cepstra cepstra{};
		const bool valid = extractor.extract(window.data(), window.size(), rate, cepstra);
		const auto count = std::min<std::size_t>(snapshot.full_mix_debug_candidate_count, snapshot.full_mix_debug_candidates.size());
		for (std::size_t i = 0; i < std::max<std::size_t>(1, count); ++i) {
			const mao::FullMixDebugCandidate candidate = count ? snapshot.full_mix_debug_candidates[i] : mao::FullMixDebugCandidate{};
			output << std::setprecision(6) << end << '\t' << notes(snapshot.bass_notes) << '\t' << notes(snapshot.guitar_notes)
				<< '\t' << notes(snapshot.keyboard_notes) << '\t' << notes(snapshot.vocal_notes) << '\t' << notes(snapshot.other_notes)
				<< '\t' << notes(snapshot.ambiguous_notes) << '\t' << snapshot.global_chord.label << '\t' << snapshot.estimated_bpm << '\t' << snapshot.bpm_confidence << '\t';
			std::string drums;
			for (const auto &drum : snapshot.drums) if (drum.active) drums += (drums.empty() ? "" : ",") + std::string(drum.label);
			output << drums << std::setprecision(17) << '\t' << candidate.midi << '\t' << static_cast<int>(candidate.owner)
				<< '\t' << candidate.ownership_confidence << '\t' << candidate.onset_strength << '\t' << candidate.decay_rate
				<< '\t' << candidate.pitch_stability << '\t' << candidate.simultaneous_onset << '\t' << candidate.bass_score
				<< '\t' << candidate.keyboard_score << '\t' << candidate.guitar_score << '\t' << candidate.vocal_score << '\t' << candidate.other_score
				<< '\t' << candidate.spectral_level << '\t' << candidate.pitch_confidence << '\t' << candidate.periodicity << '\t' << candidate.harmonicity
				<< '\t' << candidate.harmonic_fit_error << '\t' << candidate.spectral_centroid << '\t' << candidate.spectral_slope << '\t' << candidate.local_noise_level
				<< '\t' << candidate.lower_octave_ratio << '\t' << candidate.harmonic_product_score << '\t' << candidate.lower_subharmonic_product_ratio
				<< '\t' << candidate.adjacent_lower_ratio << '\t' << candidate.adjacent_upper_ratio << '\t' << candidate.third_octave_ratio
				<< '\t' << candidate.vocal_tone_profile_supported << '\t' << candidate.vocal_rejected_for_polyphony;
			for (double value : candidate.harmonic_ratios) output << '\t' << value;
			output << '\t' << valid;
			for (double value : cepstra) output << '\t' << value;
			output << '\n';
		}
	}
	return input.eof() && end ? 0 : 3;
}
