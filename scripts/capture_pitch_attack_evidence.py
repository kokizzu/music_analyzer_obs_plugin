#!/usr/bin/env python3
"""Dense diagnostic model snapshots from immutable primary helper sources."""
import argparse
import csv
import fcntl
import hashlib
import json
from itertools import groupby
from pathlib import Path
import subprocess
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest


def build():
    identity()
    names=['basic_pitch_onnx_runtime.hpp','basic_pitch_onnx_runtime.cpp','basic_pitch_pcm_history.hpp',
           'basic_pitch_pcm_history.cpp','basic_pitch_onnx_decoder.hpp','basic_pitch_onnx_decoder.cpp']
    sources={name:git('show','HEAD:src/'+name) for name in names}
    sdk=ROOT/'build/onnxruntime-linux-x64-1.29.0'
    library=sdk/'lib/libonnxruntime.so.1.29.0'
    model=ROOT/'build/basic_pitch/nmp.onnx'
    inputs=dict(sources={n:hashlib.sha256(v.encode()).hexdigest() for n,v in sources.items()},
                harness_sha256=digest(ROOT/'tests/pitch_attack_evidence.cpp'),script_sha256=digest(Path(__file__)),
                sdk_headers={p.name:digest(p) for p in sorted((sdk/'include').glob('*.h'))},
                library=str(library.relative_to(ROOT)),library_sha256=digest(library),
                model=str(model.relative_to(ROOT)),model_sha256=digest(model),
                compiler=subprocess.run(['g++','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0],
                experiment='Only the exported history snapshot stride changes from 500 to 50 ms; tensor edge 168, original PCM and original decoder also recorded')
    directory=ROOT/'build/pitch_attack_evidence_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text())
        assert state['inputs']==inputs and digest(directory/'replay')==state['binary_sha256']
    else:
        for name,text in sources.items():
            if name=='basic_pitch_pcm_history.hpp':
                anchor='kSnapshotStride = kTargetSampleRate / 2;'
                assert text.count(anchor)==1
                text=text.replace(anchor,'kSnapshotStride = kTargetSampleRate / 20;',1)
            (directory/name).write_text(text)
        (directory/'replay.cpp').write_bytes((ROOT/'tests/pitch_attack_evidence.cpp').read_bytes())
        subprocess.run(['g++','-O2','-std=c++17','-I'+str(directory),'-I'+str(sdk/'include'),str(directory/'replay.cpp'),
                        *[str(directory/n) for n in names if n.endswith('.cpp')],'-ldl','-pthread','-o',str(directory/'replay')],check=True)
        state=dict(inputs=inputs,binary_sha256=digest(directory/'replay'))
        atomic_json(checkpoint,state)
    atomic_json(directory.parent/'current.json',dict(build=str(checkpoint.relative_to(ROOT)),sha256=digest(checkpoint)))
    return checkpoint,state


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--build',action='store_true')
    args=parser.parse_args()
    build_path,built=build()
    if args.build:
        print(build_path.relative_to(ROOT),flush=True)
        return
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=json.loads(baseline_path.read_text())
    inputs=dict(build_sha256=digest(build_path),baseline_sha256=digest(baseline_path),script_sha256=digest(Path(__file__)),
                selection=['training-1','training-2','training-3'],note_threshold=.3,onset_threshold=.5,maximum_model_age_seconds=.15,
                availability='Simulate one worker choosing the latest pending 50 ms request; completion uses measured inference wall time, never backdated',
                scope='Training-only dense model evidence, no analyzer changes or production/hardware-paced latency claim')
    directory=ROOT/'build/pitch_attack_evidence'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',inputs)
    with (directory/'capture.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        checkpoint=directory/'report.json'
        state=json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs,recordings={},complete=False)
        assert state['inputs']==inputs
        for name in inputs['selection']:
            raw=baseline_path.parent/(name+'.f32')
            assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
            rate=baseline['recordings'][name]['rate']
            target=directory/(name+'.tsv')
            if name in state['recordings']:
                assert digest(target)==state['recordings'][name]['sha256']
                continue
            pending=target.with_suffix('.pending.tsv')
            subprocess.run([str(build_path.parent/'replay'),str(raw),str(rate),str(ROOT/built['inputs']['library']),
                            str(ROOT/built['inputs']['model']),str(pending)],check=True,timeout=1800)
            pending.replace(target)
            captures=0
            wall=[];cpu=[]
            with target.open() as stream:
                for end,group in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                    rows=list(group)
                    assert [int(r['midi']) for r in rows]==list(range(21,109))
                    assert end==round(rate*.05)*(captures+40)
                    assert all(r['wall_ms']==rows[0]['wall_ms'] and r['cpu_ms']==rows[0]['cpu_ms'] for r in rows)
                    assert all(0<=float(r[k])<=1 for r in rows for k in ('legacy','edge4_note','edge4_onset'))
                    wall.append(float(rows[0]['wall_ms']));cpu.append(float(rows[0]['cpu_ms']))
                    captures+=1
            assert captures==1161
            state['recordings'][name]=dict(sha256=digest(target),raw_sha256=digest(raw),rate=rate,captures=captures,
                mean_wall_ms=sum(wall)/len(wall),max_wall_ms=max(wall),mean_cpu_ms=sum(cpu)/len(cpu),max_cpu_ms=max(cpu))
            atomic_json(checkpoint,state)
            print(name,json.dumps(state['recordings'][name]),flush=True)
        assert digest(Path(__file__))==inputs['script_sha256'] and digest(build_path)==inputs['build_sha256']
        state['complete']=True
        atomic_json(checkpoint,state)
        atomic_json(directory.parent/'current.json',dict(report=str(checkpoint.relative_to(ROOT)),sha256=digest(checkpoint)))
        print(checkpoint.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
