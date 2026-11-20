#!/usr/bin/env python3
"""Compile source recovery regressions against a verified primary export."""
import argparse
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from analyzer_diagnostic import primary_tool,TOOLS
from detection_validation_store import Store
from publish_next_detection import git
from routing_duration_baseline import ROOT,digest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--candidate',action='store_true');args=parser.parse_args()
    _,metadata=primary_tool()
    directory=ROOT/'build/detection_tools';directory.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-recovery-',dir=directory) as temporary:
        work=Path(temporary)
        archive=subprocess.run(['git','archive','HEAD','src'],cwd=ROOT,capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            for entry in stream:
                assert entry.name=='src' or (entry.name.startswith('src/') and '..' not in Path(entry.name).parts)
                if entry.isfile():
                    target=work/entry.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(stream.extractfile(entry).read())
        sources_text={}
        if args.candidate:
            from source_recovery_patch import candidate_sources
            sources_text=candidate_sources()
            for name,text in sources_text.items():
                (work/'src'/name).write_text(text)
        header=work/'src/analyzer.hpp';text=header.read_text();assert text.count('class AnalysisEngine {')==1
        header.write_text(text.replace('class AnalysisEngine {','class AnalysisEngine {\n friend struct SourceRecoveryProbe;',1))
        includes=['-I'+str(work/'src'),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),
            '-I'+str(ROOT/'third_party/beat_and_tempo_tracking')]
        objects=[str(ROOT/p) for p,h in metadata['inputs']['objects'].items() if Path(p).name in ('BTT.o','DFT.o','Filter.o','STFT.o','Statistics.o','fastsin.o')]
        assert len(objects)==6
        engine=TOOLS/'analyzer.o'
        if args.candidate or metadata['inputs']['source_tree']!=json.loads((TOOLS/'build.json').read_text())['inputs']['source_tree']:
            engine=work/'analyzer.o'
            subprocess.run(['g++','-O2','-std=c++17',*includes,'-c',str(work/'src/analyzer.cpp'),'-o',str(engine)],check=True)
        binary=work/'test'
        sources=[work/'src'/name for name in ('basic_pitch_onnx_runtime.cpp','basic_pitch_onnx_decoder.cpp','basic_pitch_onnx_worker.cpp','basic_pitch_pcm_history.cpp')]
        subprocess.run(['g++','-O2','-std=c++17','-DMAO_ENABLE_BASIC_PITCH',*includes,str(ROOT/'tests/source_recovery.cpp'),
            str(engine),*objects,*map(str,sources),'-ldl','-pthread','-o',str(binary)],check=True)
        completed=subprocess.run([str(binary),str(ROOT/'build/onnxruntime-linux-x64-1.29.0/lib/libonnxruntime.so.1.29.0'),
            str(ROOT/'build/basic_pitch/nmp.onnx')],check=False,timeout=60)
        if args.candidate and completed.returncode==0:
            epoch=work/'epoch'
            subprocess.run(['g++','-O2','-std=c++17',*includes,str(ROOT/'tests/worker_context_epoch.cpp'),
                str(work/'src/basic_pitch_onnx_worker.cpp'),str(work/'src/basic_pitch_onnx_decoder.cpp'),'-pthread','-o',str(epoch)],check=True)
            subprocess.run([str(epoch)],check=True,timeout=15)
            # Compare actual paired inputs against frozen current-primary output.
            replay=work/'primary'
            subprocess.run(['g++','-O2','-std=c++17',*includes,str(ROOT/'tests/pitch_primary_replay.cpp'),
                str(engine),*objects,*map(str,sources),'-DMAO_ENABLE_BASIC_PITCH','-ldl','-pthread','-o',str(replay)],check=True)
            reference=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541';parity={}
            for name in ('training-1','training-4'):
                raw=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267'/(name+'.f32');out=work/(name+'.tsv')
                subprocess.run([str(replay),str(raw),'44100',str(out)],check=True,timeout=120)
                assert out.read_bytes()==(reference/(name+'-primary.tsv')).read_bytes(),name+' ordinary output changed'
                parity[name]=dict(frames=1200,output_sha256=digest(out))
            latency=work/'latency'
            subprocess.run(['g++','-O2','-std=c++17','-DMAO_ENABLE_BASIC_PITCH',*includes,str(ROOT/'tests/detection_worker_latency.cpp'),
                *map(str,sources),'-ldl','-pthread','-o',str(latency)],check=True)
            run=subprocess.run([str(latency),str(ROOT/'build/onnxruntime-linux-x64-1.29.0/lib/libonnxruntime.so.1.29.0'),
                str(ROOT/'build/basic_pitch/nmp.onnx'),str(ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/training-1.f32')],capture_output=True,text=True,check=True,timeout=30)
            timing=json.loads(run.stdout)
            assert timing['observed_results']==100 and timing['unobserved_or_replaced']==0 and timing['completion_p99_ms']<45 and timing['completion_max_ms']<50 and timing['submit_p99_ms']<1,timing
            # Keep one verified replay executable, replacing it atomically only
            # after the lifecycle, ordinary-output and latency gates all pass.
            pending=directory/'primary.pending';shutil.copy2(replay,pending);os.replace(pending,directory/'primary')
            result=dict(base_source_tree=metadata['inputs']['source_tree'],cases_passed=7,epoch_passed=True,ordinary=parity,timing=timing,
                binary='build/detection_tools/primary',binary_sha256=digest(directory/'primary'),
                inputs={str(ROOT.joinpath('tests',p).relative_to(ROOT)):digest(ROOT/'tests'/p) for p in
                    ('source_recovery.cpp','worker_context_epoch.cpp','pitch_primary_replay.cpp','detection_worker_latency.cpp')})
            result['inputs'].update({'scripts/'+p:digest(ROOT/'scripts'/p) for p in ('validate_source_recovery.py','source_recovery_patch.py')})
            with Store() as store:
                with store.connection:
                    result['source_payloads']={name:store.put(text.encode()) for name,text in sources_text.items()}
                store.evidence('source-recovery','validation',result)
            print(json.dumps(result,indent=2),flush=True)
        raise SystemExit(completed.returncode)


if __name__=='__main__':
    main()
