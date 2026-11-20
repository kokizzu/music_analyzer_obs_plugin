#include "basic_pitch_onnx_worker.hpp"
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <vector>

namespace {
std::mutex gate_mutex;
std::condition_variable gate;
unsigned entered=0,released=0;
std::vector<float> inputs;
bool await_entered(unsigned count) {
    std::unique_lock<std::mutex> lock(gate_mutex);
    return gate.wait_for(lock,std::chrono::seconds(3),[&]{return entered>=count;});
}
void release(unsigned count) { {std::lock_guard<std::mutex> lock(gate_mutex);released=count;}gate.notify_all(); }
}
namespace mao {
BasicPitchOnnxRuntime::~BasicPitchOnnxRuntime() {}
bool BasicPitchOnnxRuntime::load(const char *,const char *) { return true; }
bool BasicPitchOnnxRuntime::infer(const float *waveform,std::size_t,BasicPitchOnnxOutput &output) {
    std::unique_lock<std::mutex> lock(gate_mutex);
    const unsigned call=++entered;inputs.push_back(waveform[0]);gate.notify_all();
    if(!gate.wait_for(lock,std::chrono::seconds(3),[&]{return released>=call;})) return false;
    output.note.assign(BasicPitchOnnxOutput::kFrames*88,0);
    output.onset.assign(output.note.size(),0);
    return true;
}
}
int main() {
    mao::BasicPitchOnnxWorker worker("fake","fake");
    std::vector<float> waveform(mao::BasicPitchOnnxRuntime::kInputSamples,.1f);
    uint64_t old=0,pending=0,fresh=0,sequence=0;mao::BasicPitchCausalNotes notes;
    bool passed=worker.start() && worker.submit(waveform.data(),waveform.size(),&old) && await_entered(1);
    waveform[0]=.2f;passed=passed && worker.submit(waveform.data(),waveform.size(),&pending);
    worker.reset_context();
    passed=passed && !worker.copy_latest(notes) && !worker.wait_for_result(old,1);
    waveform[0]=.3f;passed=passed && worker.submit(waveform.data(),waveform.size(),&fresh) && fresh>pending;
    release(1);
    passed=passed && await_entered(2);
    // Fresh inference has started, so old inference has passed its publication
    // point. It must still be invisible while the fresh result is blocked.
    passed=passed && !worker.copy_latest(notes) && inputs.size()==2 && inputs[1]==.3f;
    release(100);
    passed=passed && worker.wait_for_result(fresh,3000) && worker.copy_latest(notes,&sequence) && sequence==fresh;
    worker.stop();passed=passed && worker.start() && !worker.copy_latest(notes);
    worker.stop();
    std::cout<<"deterministic in-flight/pending/restart isolation "<<(passed?"PASS":"FAIL")<<'\n';
    return passed?0:10;
}
