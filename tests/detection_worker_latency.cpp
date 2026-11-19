#include "basic_pitch_onnx_worker.hpp"
#include "basic_pitch_pcm_history.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <thread>
#include <vector>

int main(int argc,char **argv)
{
    if(argc!=4) return 2;
    using Clock=std::chrono::steady_clock;
    std::ifstream raw(argv[3],std::ios::binary);
    constexpr unsigned rate=44100,hop=2205,count=100;
    std::vector<float> fresh(hop);
    std::array<float,mao::BasicPitchOnnxRuntime::kInputSamples> waveform{};
    mao::BasicPitchPcmHistory history;
    bool ready=false;
    for(unsigned i=0;i<50 && !ready;++i) {
        if(!raw.read(reinterpret_cast<char*>(fresh.data()),hop*sizeof(float))) return 3;
        ready=history.push(fresh.data(),fresh.size(),rate,waveform);
    }
    if(!ready) return 4;
    mao::BasicPitchOnnxWorker worker(argv[1],argv[2]);
    if(!worker.start()) { std::cerr<<worker.last_error();return 5; }
    uint64_t warmup=0;
    if(!worker.submit(waveform.data(),waveform.size(),&warmup) || !worker.wait_for_result(warmup,5000)) return 6;
    std::map<uint64_t,Clock::time_point> submitted;
    std::vector<double> latency,submit_ms;
    uint64_t last=warmup;
    auto poll=[&]() {
        mao::BasicPitchCausalNotes notes;uint64_t sequence=0;
        if(worker.copy_latest(notes,&sequence) && sequence>last) {
            auto found=submitted.find(sequence);
            if(found!=submitted.end()) latency.push_back(std::chrono::duration<double,std::milli>(Clock::now()-found->second).count());
            last=sequence;
        }
    };
    const auto start=Clock::now();
    for(unsigned i=0;i<count;++i) {
        const auto deadline=start+std::chrono::milliseconds(50*i);
        while(Clock::now()<deadline) { poll();std::this_thread::sleep_for(std::chrono::milliseconds(1)); }
        if(!raw.read(reinterpret_cast<char*>(fresh.data()),hop*sizeof(float))) return 7;
        // Primary history refreshes at 500ms. Keep its latest valid waveform
        // between refreshes while stress-submitting the worker at 50ms.
        history.push(fresh.data(),fresh.size(),rate,waveform);
        const auto begin=Clock::now();uint64_t sequence=0;
        if(!worker.submit(waveform.data(),waveform.size(),&sequence)) return 8;
        const auto end=Clock::now();submitted.emplace(sequence,begin);
        submit_ms.push_back(std::chrono::duration<double,std::milli>(end-begin).count());poll();
    }
    const auto finish=start+std::chrono::milliseconds(count*50+200);
    while(Clock::now()<finish) { poll();std::this_thread::sleep_for(std::chrono::milliseconds(1)); }
    worker.stop();
    if(latency.empty()) return 9;
    std::sort(latency.begin(),latency.end());std::sort(submit_ms.begin(),submit_ms.end());
    auto p99=[](const auto &v) {return v[std::min(v.size()-1,static_cast<std::size_t>(std::ceil(v.size()*.99))-1)];};
    std::cout<<"{\"submitted\":"<<submitted.size()<<",\"observed_results\":"<<latency.size()
        <<",\"unobserved_or_replaced\":"<<submitted.size()-latency.size()
        <<",\"completion_p99_ms\":"<<p99(latency)<<",\"completion_max_ms\":"<<latency.back()
        <<",\"submit_p99_ms\":"<<p99(submit_ms)<<",\"submit_max_ms\":"<<submit_ms.back()<<"}\n";
}
