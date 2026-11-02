#include "analyzer.hpp"
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
    std::set<int> values;
    for (const auto &row:grid.rows) for (const auto &cell:row)
        if (cell.active && cell.midi>=0 && (cell.visual_level<0 ? cell.level : cell.visual_level)>0) values.insert(cell.midi);
    std::string result;
    for (int midi:values) result+=(result.empty() ? "" : ",")+std::to_string(midi);
    return result;
}

int main(int argc,char **argv)
{
    if (argc!=4) return 2;
    const unsigned rate=std::stoul(argv[2]);
    if (rate!=16000 && rate!=44100 && rate!=48000) return 2;
    std::ifstream input(argv[1],std::ios::binary);std::ofstream output(argv[3]);
    if (!input || !output) return 3;
    mao::AnalysisSettings settings;
    settings.sample_rate=rate;settings.analysis_window_seconds=.1f;settings.analysis_interval_seconds=.05f;
    settings.input_mode=mao::AnalysisInputMode::FullMix;
    if (!settings.native_piano_duplicate_consensus) return 4;
    auto engine=std::make_unique<mao::AnalysisEngine>();
    const auto hop=std::size_t(std::lround(rate*.05));
    std::vector<float> fresh(hop),window(mao::resolve_analysis_window_samples(settings),0);
    output<<"end_sample\tbass\tguitar\tkeys\tvoice\tother\tambiguous\tchord\tbpm\tconfidence\tdrums\n"<<std::setprecision(6);
    std::size_t end=0;
    while (input.read(reinterpret_cast<char *>(fresh.data()),hop*sizeof(float))) {
        for (float value:fresh) if (!std::isfinite(value)) return 5;
        end+=hop;
        std::move(window.begin()+hop,window.end(),window.begin());
        std::copy(fresh.begin(),fresh.end(),window.end()-hop);
        const auto s=engine->analyze(window.data(),window.size(),settings,"sustained benchmark",0);
        std::string drums;
        for (const auto &d:s.drums) if (d.active) drums+=(drums.empty() ? "" : ",")+std::string(d.label);
        output<<end<<'\t'<<notes(s.bass_notes)<<'\t'<<notes(s.guitar_notes)<<'\t'<<notes(s.keyboard_notes)<<'\t'
              <<notes(s.vocal_notes)<<'\t'<<notes(s.other_notes)<<'\t'<<notes(s.ambiguous_notes)<<'\t'
              <<s.global_chord.label<<'\t'<<s.estimated_bpm<<'\t'<<s.bpm_confidence<<'\t'<<drums<<'\n';
    }
    return input.eof() && end ? 0 : 6;
}
