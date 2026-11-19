#!/usr/bin/env python3
"""Observe the actual committed-primary ONNX worker on a paced 50ms schedule."""
import json
from pathlib import Path
import subprocess
import tempfile
from analyzer_diagnostic import primary_tool,TOOLS
from detection_validation_store import Store
from publish_next_detection import git
from routing_duration_baseline import ROOT,digest


def main():
    _,metadata=primary_tool()
    names=('basic_pitch_onnx_worker.cpp','basic_pitch_onnx_worker.hpp','basic_pitch_onnx_runtime.cpp','basic_pitch_onnx_runtime.hpp',
        'basic_pitch_onnx_decoder.cpp','basic_pitch_onnx_decoder.hpp','basic_pitch_pcm_history.cpp','basic_pitch_pcm_history.hpp')
    for name in names:
        assert (TOOLS/'src'/name).read_text()==git('show','HEAD:src/'+name)
    source=ROOT/'tests/detection_worker_latency.cpp';directory=ROOT/'build/detection_tools';directory.mkdir(exist_ok=True)
    runtime=ROOT/'build/onnxruntime-linux-x64-1.29.0/lib/libonnxruntime.so.1.29.0';model=ROOT/'build/basic_pitch/nmp.onnx'
    raw=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/training-1.f32'
    reference=json.loads((raw.parent/'report.json').read_text())['recordings']['training-1']
    assert digest(raw)==reference['prefix_sha256'] and reference['rate']==44100
    # Temporary executable avoids retaining a second versioned binary cache.
    with tempfile.TemporaryDirectory(prefix='worker-benchmark-',dir=directory) as temporary:
        binary=Path(temporary)/'worker'
        subprocess.run(['g++','-O2','-std=c++17','-DMAO_ENABLE_BASIC_PITCH','-I'+str(TOOLS/'src'),
            '-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),str(source),
            *[str(TOOLS/'src'/name) for name in names if name.endswith('.cpp')],'-pthread','-ldl','-o',str(binary)],check=True)
        completed=subprocess.run([str(binary),str(runtime),str(model),str(raw)],capture_output=True,text=True,check=True,timeout=30)
    result=json.loads(completed.stdout)
    result.update(source_tree=metadata['inputs']['source_tree'],inputs={str(p.relative_to(ROOT)):digest(p) for p in (source,Path(__file__),runtime,model,raw)},
        gates=dict(completion_p99_ms=45,completion_max_ms=50,submit_p99_ms=1,unobserved_or_replaced=0),
        scope='100 actual asynchronous worker submissions stress-paced at 50ms after warmup; primary waveform refresh remains 500ms. Completion observed by 1ms polling. Unobserved/replaced results are not necessarily audio drops. Submission timing excludes history preparation. No live callback, device queue, UI or thermal-stability qualification.')
    result['passed_worker_budget']=result['completion_p99_ms']<45 and result['completion_max_ms']<50 and result['submit_p99_ms']<1 and result['unobserved_or_replaced']==0
    with Store() as store:
        store.evidence('worker-latency','benchmark',result)
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
