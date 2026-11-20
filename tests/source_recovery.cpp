#include "analyzer.hpp"
#include "basic_pitch_onnx_worker.hpp"
#include <array>
#include <chrono>
#include <cmath>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>

namespace mao {
struct SourceRecoveryProbe {
    static bool ready(const AnalysisEngine &engine) { return engine.basic_pitch_notes_ready_; }
    static BasicPitchOnnxWorker *worker(AnalysisEngine &engine) { return engine.basic_pitch_worker_.get(); }
};
}

int main(int argc,char **argv)
{
    if(argc!=3) return 2;
    unsigned failed=0,passed=0;
    for(unsigned scenario=0;scenario<7;++scenario) {
        auto engine=std::make_unique<mao::AnalysisEngine>();
        mao::AnalysisSettings settings;
        settings.sample_rate=48000;settings.analysis_window_seconds=.1f;settings.analysis_interval_seconds=.05f;
        settings.input_mode=mao::AnalysisInputMode::FullMix;
        settings.basic_pitch_vocal_fusion_enabled=true;settings.basic_pitch_runtime_library=argv[1];settings.basic_pitch_model=argv[2];
        std::vector<float> silence(4800,0);
        engine->analyze(silence.data(),silence.size(),settings,"source A",0);
        auto *worker=mao::SourceRecoveryProbe::worker(*engine);
        if(!worker) return 3;
        std::array<float,mao::BasicPitchOnnxRuntime::kInputSamples> waveform{};
        for(std::size_t i=0;i<waveform.size();++i) waveform[i]=.1f*std::sin(2*3.141592653589793*440*i/22050);
        uint64_t sequence=0;
        if(!worker->submit(waveform.data(),waveform.size(),&sequence) || !worker->wait_for_result(sequence,5000)) return 4;
        engine->analyze(silence.data(),silence.size(),settings,"source A",0);
        if(!mao::SourceRecoveryProbe::ready(*engine)) return 5;
        const char *source="source A";uint64_t dropped=0;
        if(scenario==0) engine->reset();
        if(scenario==1) source="source B";
        if(scenario==2) {settings.sample_rate=44100;silence.resize(4410);}
        if(scenario==3) {settings.analysis_window_seconds=.2f;silence.resize(9600);}
        if(scenario==4) {engine->analyze(nullptr,0,settings,source,0);}
        if(scenario==5) settings.input_mode=mao::AnalysisInputMode::IsolatedKeyboard;
        if(scenario==6) dropped=1;
        engine->analyze(silence.data(),silence.size(),settings,source,dropped);
        const bool stale=mao::SourceRecoveryProbe::ready(*engine);
        // Keep consuming fresh silence below model warmup; old results must not reappear.
        for(int hop=0;hop<3;++hop) engine->analyze(silence.data(),silence.size(),settings,source,dropped);
        const bool resurrected=mao::SourceRecoveryProbe::ready(*engine);
        if(stale||resurrected) {++failed;std::cout<<"FAIL stale context scenario "<<scenario<<'\n';}
        else ++passed;
    }
    std::cout<<"source recovery passed="<<passed<<" failed="<<failed<<'\n';
    return failed?10:0;
}
