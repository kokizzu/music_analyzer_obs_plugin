#!/usr/bin/env python3
"""Build exact-primary replay and feature tools; verify on known recordings."""
import csv
import hashlib
import io
import json
from itertools import groupby
from pathlib import Path
import subprocess
import tarfile
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from piano_context_features import features
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest


def read(path):
    return json.loads(path.read_text())


def build():
    identity()
    old=ROOT/'build/pitch_attack_envelope_native/9bf32267d49cc8fb/build.json'
    objects=read(old)['inputs']['objects']
    assert all(digest(ROOT/p)==h for p,h in objects.items())
    inputs=dict(source_tree=git('rev-parse','HEAD:src').strip(),objects=objects,
        assets={p:digest(ROOT/p) for p in ('tests/piano_context_pcm.cpp','tests/pitch_primary_replay.cpp','scripts/build_pitch_heldout_tools.py')})
    directory=ROOT/'build/pitch_heldout_tools'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if not checkpoint.exists():
        archive=subprocess.run(['git','archive','HEAD','src'],cwd=ROOT,capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            for entry in stream:
                if entry.name=='src' and entry.isdir():
                    continue
                assert entry.name.startswith('src/') and '..' not in Path(entry.name).parts
                if entry.isfile():
                    target=directory/entry.name;target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(stream.extractfile(entry).read())
        include=['-I'+str(directory/'src'),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),
                 '-I'+str(ROOT/'build/routing_duration_primary/02001c66f49dc729/third_party/beat_and_tempo_tracking')]
        subprocess.run(['g++','-O2','-std=c++17',*include,str(ROOT/'tests/piano_context_pcm.cpp'),'-o',str(directory/'features')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,'-c',str(directory/'src/analyzer.cpp'),'-o',str(directory/'analyzer.o')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,str(ROOT/'tests/pitch_primary_replay.cpp'),str(directory/'analyzer.o'),
                        *[str(ROOT/p) for p in objects],'-lm','-pthread','-ldl','-o',str(directory/'primary')],check=True)
        atomic_json(checkpoint,dict(inputs=inputs,binaries={name:digest(directory/name) for name in ('features','primary')}))
    built=read(checkpoint)
    assert built['inputs']==inputs and all(digest(directory/name)==h for name,h in built['binaries'].items())
    return directory


def main():
    directory=build()
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267'
    native=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7'
    reference=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b'
    context=read(ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json')
    baseline_report=read(baseline/'report.json');native_report=read(native/'report.json');ref_report=read(reference/'report.json')
    reports={}
    for name in ('training-1','training-2','training-3','training-4'):
        raw=baseline/(name+'.f32');rate=baseline_report['recordings'][name]['rate']
        assert digest(raw)==baseline_report['recordings'][name]['prefix_sha256']
        feature=directory/(name+'-features.tsv')
        subprocess.run([str(directory/'features'),str(raw),str(rate),str(feature)],check=True)
        old=native/(name+'.tsv');assert digest(old)==native_report['recordings'][name]['sha256']
        with feature.open() as stream,old.open() as known:
            values=list(csv.DictReader(stream,delimiter='\t'))
            expected=[next(rows) for _,rows in groupby(csv.DictReader(known,delimiter='\t'),key=lambda r:r['end_sample'])]
        assert len(values)==len(expected)==1200
        audio=np.fromfile(raw,dtype='<f4');count=round(rate*.1);padded=np.pad(audio,(count,0))
        maximum=0.;mismatch=0
        for row,original in zip(values,expected):
            assert row['end_sample']==original['end_sample'] and row['mfcc_valid']==original['mfcc_valid']
            a=[float(row['mfcc'+str(i)]) for i in range(24)];b=[float(original['mfcc'+str(i)]) for i in range(24)]
            maximum=max(maximum,max(abs(x-y) for x,y in zip(a,b)))
            if row['mfcc_valid']=='1':
                end=int(row['end_sample']);pcm=padded[end:end+count]
                p,q=(lower_probability(context['model'],features(pcm,rate,v)) for v in (a,b))
                mismatch+=(p>=context['negative_max']+.001)!=(q>=context['negative_max']+.001)
        assert maximum<1e-7 and mismatch==0
        reports[name]=dict(feature_sha256=digest(feature),maximum_cepstral_error=maximum,context_decision_mismatches=mismatch)
        if name in ('training-1','training-4'):
            output=directory/(name+'-primary.tsv')
            subprocess.run([str(directory/'primary'),str(raw),str(rate),str(output)],check=True,timeout=3600)
            old=reference/('piano-'+name+'.tsv');assert digest(old)==ref_report['recordings']['piano-'+name]['sha256']
            with output.open() as stream,old.open() as known:
                actual=list(csv.DictReader(stream,delimiter='\t'));expected=list(csv.DictReader(known,delimiter='\t'))
            assert len(actual)==len(expected)==1200
            assert all(all(r[k]==s['after_'+k if k in ('guitar','voice') else k] for k in r) for r,s in zip(actual,expected))
            reports[name]['primary_sha256']=digest(output)
        print(name,json.dumps(reports[name]),flush=True)
    atomic_json(directory/'parity.json',dict(build_sha256=digest(directory/'build.json'),recordings=reports,passed=True,
        scope='4800 feature endpoints, 2400 exact-primary output endpoints; no fresh held-out source decoded.'))
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'parity.json').relative_to(ROOT)),sha256=digest(directory/'parity.json')))
    print(directory.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
