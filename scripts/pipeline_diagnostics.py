#!/usr/bin/env python3
"""Measure an isolated primary standalone app with a paced real-piano input."""
import collections
import argparse
import io
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tarfile
import tempfile
import threading
import time
from analyzer_diagnostic import primary_tool
from detection_validation_store import Store
from publish_next_detection import git
from routing_duration_baseline import ROOT,digest
from source_recovery_patch import replace_once


def stats(values):
    if not values: return None
    ordered=sorted(values)
    return dict(count=len(values),p99=ordered[math.ceil(len(ordered)*.99)-1],max=ordered[-1])


def summarize(lines,sent):
    analyses={};presented={};durations=[];skipped=set()
    for line in lines:
        if not line.startswith('MAODIAG '): continue
        parts=line.split();kind=parts[1];values=dict(p.split('=',1) for p in parts[2:])
        if kind=='S':
            sample=int(values['sample'])
            if sample not in sent or sample in skipped: raise ValueError('Invalid idle skip clock')
            skipped.add(sample);continue
        sequence=int(values['sequence']);stamp=int(values['ns']);duration=float(values['ms'])
        if not math.isfinite(duration) or duration<0: raise ValueError('Invalid duration')
        if kind=='A':
            sample=int(values['sample'])
            if sample not in sent or stamp<sent[sample] or sequence in analyses: raise ValueError('Invalid source clock')
            analyses[sequence]=(sample,stamp,duration,float(values.get('rms',0)))
            durations.append(duration)
        elif kind=='P' and sequence not in presented:
            presented[sequence]=(stamp,duration)
    if not analyses: raise ValueError('No analysis timing events')
    ages=[];presentation=[]
    for sequence,(sample,stamp,_,_) in analyses.items():
        if sequence in presented:
            shown,duration=presented[sequence]
            if shown<stamp: raise ValueError('Presentation preceded analysis')
            ages.append((shown-sent[sample])/1e6);presentation.append(duration)
    analyzed_samples={r[0] for r in analyses.values()}
    if analyzed_samples&skipped: raise ValueError('Hop both analyzed and skipped')
    return dict(analysis_ms=stats(durations),present_call_ms=stats(presentation),source_to_present_ms=stats(ages),
        unpresented_analysis_frames=len(analyses)-len(ages),active_frames=sum(r[3]>=.0025 for r in analyses.values()),
        intentional_idle_hops=len(skipped),controlled_stream_hop_gaps=len(set(sent)-analyzed_samples-skipped),
        physical_capture_latency_ms=None,audio_dropped_windows=None)


def instrument(source):
    prefix='''#include <chrono>
#include <cstdio>
static long long mao_diag_ns() {return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
'''
    source=replace_once(source,'\t\tsnapshot_ = engine_.analyze(window_.data(), window_samples_, settings_, source_name_.c_str(), 0);',
        '''\t\tconst auto mao_begin=mao_diag_ns();
\t\tsnapshot_ = engine_.analyze(window_.data(), window_samples_, settings_, source_name_.c_str(), 0);
\t\tconst auto mao_end=mao_diag_ns();
\t\tstd::fprintf(stderr,"MAODIAG A sample=%llu sequence=%llu ns=%lld ms=%.6f rms=%.6f\\n",(unsigned long long)audio_frames_,(unsigned long long)(sequence_+1),mao_end,(mao_end-mao_begin)/1e6,(double)snapshot_.rms);''')
    primary_skip='\t\tif (silent_window && should_skip_silent_analysis())\n\t\t\treturn false;'
    if primary_skip in source:
        source=replace_once(source,primary_skip,
        '''\t\tif (silent_window && should_skip_silent_analysis()) {
\t\t\tstd::fprintf(stderr,"MAODIAG S sample=%llu\\n",(unsigned long long)audio_frames_);
\t\t\treturn false;
\t\t}''')
    else:
        source=replace_once(source,'\t\tif (skip) {\n\t\t\tengine_.invalidate_audio_history();',
            '''\t\tif (skip) {
\t\t\tstd::fprintf(stderr,"MAODIAG S sample=%llu\\n",(unsigned long long)audio_frames_);
\t\t\tengine_.invalidate_audio_history();''')
    source=replace_once(source,'\t\tif (should_present) {\n\t\t\tpresent(&session, visualizer);',
        '''\t\tif (should_present) {
\t\t\tconst auto mao_begin=mao_diag_ns();
\t\t\tpresent(&session, visualizer);
\t\t\tconst auto mao_end=mao_diag_ns();
\t\t\tstd::fprintf(stderr,"MAODIAG P sequence=%llu ns=%lld ms=%.6f\\n",(unsigned long long)analyzer.snapshot().sequence,mao_end,(mao_end-mao_begin)/1e6);''')
    return prefix+source


def run_paced(binary,raw,rate,basic_pitch=False):
    lines=[];retained=[0];truncated=[False];hop=round(rate*.05);sent={};write_ms=[];lateness=[]
    command=[str(binary),'--raw-f32le','-','--sample-rate',str(rate),'--no-hardware','--fps','30']
    if basic_pitch:
        command += ['--basic-pitch','--basic-pitch-runtime',str(ROOT/'build/onnxruntime-linux-x64-1.29.0/lib/libonnxruntime.so.1.29.0'),
            '--basic-pitch-model',str(ROOT/'build/basic_pitch/nmp.onnx')]
    process=subprocess.Popen(command,
        stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
    def drain():
        for line in iter(process.stderr.readline,b''):
            if line.startswith(b'MAODIAG '):
                retained[0]+=len(line)
                if retained[0]<=1024*1024: lines.append(line.decode())
                else: truncated[0]=True
    reader=threading.Thread(target=drain,daemon=True);reader.start()
    selector=selectors.DefaultSelector();os.set_blocking(process.stdin.fileno(),False)
    selector.register(process.stdin,selectors.EVENT_WRITE);start=time.monotonic_ns()
    try:
        with raw.open('rb') as stream:
            for index in range(1,201):
                chunk=stream.read(hop*4)
                if len(chunk)!=hop*4: raise ValueError('Need ten seconds of fixture audio')
                deadline=start+round(index*hop/rate*1e9)
                delay=(deadline-time.monotonic_ns())/1e9
                if delay>0: time.sleep(delay)
                sent[index*hop]=deadline;begin=time.monotonic_ns();lateness.append((begin-deadline)/1e6)
                offset=0
                while offset<len(chunk):
                    if not selector.select(timeout=2): raise TimeoutError('Standalone stopped consuming input')
                    try: offset+=os.write(process.stdin.fileno(),chunk[offset:])
                    except BlockingIOError: continue
                write_ms.append((time.monotonic_ns()-begin)/1e6)
        process.stdin.close();code=process.wait(timeout=20)
        reader.join(timeout=2)
        if code or reader.is_alive() or truncated[0]: raise RuntimeError('Incomplete or truncated pipeline measurement')
    finally:
        selector.close()
        if process.poll() is None:
            print('Stopping owned diagnostic process group',process.pid,flush=True)
            os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=5)
        reader.join(timeout=2)
    result=summarize(lines,sent);result.update(producer_write_ms=stats(write_ms),producer_lateness_ms=stats(lateness))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',action='store_true');args=parser.parse_args()
    _,metadata=primary_tool();directory=ROOT/'build/detection_tools';directory.mkdir(exist_ok=True)
    raw=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/training-1.f32'
    expected=json.loads((raw.parent/'report.json').read_text())['recordings']['training-1'];assert digest(raw)==expected['prefix_sha256']
    print('Building isolated '+('workspace' if args.workspace else 'primary')+' standalone with timing probes',flush=True)
    with tempfile.TemporaryDirectory(prefix='pipeline-',dir=directory) as temporary:
        work=Path(temporary);archive=subprocess.run(['git','archive','HEAD','src'],cwd=ROOT,capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            for entry in stream:
                assert entry.name=='src' or (entry.name.startswith('src/') and '..' not in Path(entry.name).parts)
                if entry.isfile():
                    path=work/entry.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(stream.extractfile(entry).read())
        standalone=work/'src/standalone.cpp'
        if args.workspace:
            # Quoted includes search beside the translation unit first. Keep
            # workspace source outside the frozen source directory so it uses
            # the matching workspace headers and object-file ABI.
            standalone=work/'workspace.cpp'
            standalone.write_text((ROOT/'src/standalone.cpp').read_text())
        standalone.write_text(instrument(standalone.read_text()))
        includes=['-I'+str(work/'src'),'-I'+str(ROOT/'build/deps/usr/include/SDL2'),'-I'+str(ROOT/'build/deps/usr/include/x86_64-linux-gnu'),
            '-I'+str(ROOT/'third_party/beat_and_tempo_tracking'),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include')]
        objects=[str(ROOT/p) for p,h in metadata['inputs']['objects'].items() if Path(p).name in ('BTT.o','DFT.o','Filter.o','STFT.o','Statistics.o','fastsin.o')]
        assert len(objects)==6 and all(digest(ROOT/p)==h for p,h in metadata['inputs']['objects'].items())
        binary=work/'app';sources=['standalone.cpp','analyzer.cpp','visualizer_renderer.cpp','basic_pitch_onnx_worker.cpp','basic_pitch_onnx_runtime.cpp','basic_pitch_onnx_decoder.cpp','basic_pitch_pcm_history.cpp']
        workspace_inputs={}
        if args.workspace:
            # The existing Make target builds these before this explicit mode.
            # Link matching workspace headers/objects without publishing them.
            objects=[ROOT/'build'/name for name in ('analyzer_test_basic_pitch.o','visualizer_renderer.o','btt_BTT.o','btt_DFT.o','btt_Filter.o',
                'btt_STFT.o','btt_Statistics.o','btt_fastsin.o','basic_pitch_onnx_runtime_real.o','basic_pitch_onnx_decoder.o','basic_pitch_onnx_worker.o','basic_pitch_pcm_history.o')]
            includes[0]='-I'+str(ROOT/'src')
            workspace_inputs={str(p.relative_to(ROOT)):digest(p) for p in objects}
            workspace_inputs.update({'src/'+name:digest(ROOT/'src'/name) for name in ('standalone.cpp','analyzer.cpp','analyzer.hpp','visualizer_renderer.cpp','visualizer_renderer.hpp','basic_pitch_onnx_worker.cpp','basic_pitch_onnx_worker.hpp')})
            compile_sources=[str(standalone)]
        else:
            compile_sources=[str(work/'src'/s) for s in sources]
        subprocess.run(['g++','-O2','-std=c++17','-DMAO_STANDALONE_WITH_SDL=1','-DMAO_ENABLE_BASIC_PITCH',*includes,
            *compile_sources,*map(str,objects),'/lib/x86_64-linux-gnu/libSDL2-2.0.so.0','-ldl','-pthread','-o',str(binary)],check=True)
        print('Measuring ten seconds of paced real-piano input through the app and renderer',flush=True)
        result=run_paced(binary,raw,44100,basic_pitch=args.workspace);result['diagnostic_binary_sha256']=digest(binary)
    result.update(source_tree=metadata['inputs']['source_tree'],inputs={'scripts/pipeline_diagnostics.py':digest(Path(__file__)),str(raw.relative_to(ROOT)):digest(raw)},
        scope='Instrumented committed-primary standalone, real SDL window and renderer, ten-second prerecorded piano stream paced at 50ms. Source-to-present includes controlled transport, analysis and UI presentation calls; excludes physical device/driver and display scanout. UI-coalesced frames are not audio drops. Native path; model worker tested separately.')
    if args.workspace:
        result['inputs'].update(workspace_inputs)
        result['scope']='Instrumented dirty-workspace standalone with Basic Pitch requested, real SDL window, renderer and ten-second prerecorded piano stream paced at 50ms. Source-to-present includes controlled transport, analysis and UI presentation calls; excludes physical device/driver, display scanout and model evidence age. UI-coalesced frames are not audio drops. This does not qualify the committed-primary standalone build.'
    result['passed_pipeline_budget']=bool(result['source_to_present_ms']) and result['active_frames']>=100 and result['controlled_stream_hop_gaps']==0 and result['analysis_ms']['p99']<50 and result['source_to_present_ms']['p99']<100 and result['source_to_present_ms']['max']<250
    with Store() as store: store.evidence('workspace-pipeline' if args.workspace else 'standalone-pipeline','benchmark',result)
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__': main()
