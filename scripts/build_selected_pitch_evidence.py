#!/usr/bin/env python3
"""Sparse inference with continuously updated, unchanged PCM history."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from routing_duration_baseline import ROOT,atomic_json,digest

BASE=ROOT/'build/pitch_attack_evidence_native/9b729e8c3393b8ba'


def read(path):
    return json.loads(path.read_text())


def build():
    original=read(BASE/'build.json')
    assert digest(BASE/'replay')==original['binary_sha256']
    assert digest(ROOT/'tests/pitch_attack_evidence.cpp')==original['inputs']['harness_sha256']
    inputs=dict(base_build_sha256=digest(BASE/'build.json'),assets={p:digest(ROOT/p) for p in (
        'scripts/build_selected_pitch_evidence.py','tests/pitch_evidence_requests.hpp','tests/pitch_evidence_requests.cpp')})
    directory=ROOT/'build/selected_pitch_evidence_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True);checkpoint=directory/'build.json'
    if not checkpoint.exists():
        for path in BASE.iterdir():
            if path.suffix in ('.hpp','.cpp'):
                shutil.copy2(path,directory/path.name)
        shutil.copy2(ROOT/'tests/pitch_evidence_requests.hpp',directory/'pitch_evidence_requests.hpp')
        text=(ROOT/'tests/pitch_attack_evidence.cpp').read_text()
        text='#include "pitch_evidence_requests.hpp"\n'+text
        text=text.replace('argc != 6','argc != 7',1)
        anchor='\tmao::BasicPitchOnnxRuntime runtime;'
        assert text.count(anchor)==1
        text=text.replace(anchor,'''
    const auto request_hop=std::size_t(std::lround(rate*.05));
    std::ifstream request_file(argv[6]);
    std::set<std::size_t> requested;
    if (!request_file || !read_pitch_requests(request_file,request_hop,requested)) return 10;
'''+anchor,1)
        text=text.replace('if (!runtime.load(argv[3], argv[4]))','if (!requested.empty() && *requested.rbegin()>=rate*2 && !runtime.load(argv[3], argv[4]))',1)
        anchor='\t\tif (!history.push(fresh.data(), fresh.size(), rate, waveform)) continue;'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n\t\tif (!requested.count(end)) continue;',1)
        text=text.replace('if (!input.eof() || !captures) return 9;','if (!input.eof() || !end) return 9;\n\tif (!requested.empty() && *requested.rbegin()>end) return 11;',1)
        (directory/'selected.cpp').write_text(text)
        sdk=ROOT/'build/onnxruntime-linux-x64-1.29.0/include'
        subprocess.run(['g++','-O2','-std=c++17','-I'+str(directory),str(ROOT/'tests/pitch_evidence_requests.cpp'),'-o',str(directory/'test-requests')],check=True)
        subprocess.run([str(directory/'test-requests')],check=True)
        sources=[directory/name for name in ('basic_pitch_onnx_runtime.cpp','basic_pitch_onnx_decoder.cpp','basic_pitch_pcm_history.cpp')]
        subprocess.run(['g++','-O2','-std=c++17','-I'+str(directory),'-I'+str(sdk),str(directory/'selected.cpp'),*map(str,sources),'-ldl','-pthread','-o',str(directory/'replay')],check=True)
        atomic_json(checkpoint,dict(inputs=inputs,binary_sha256=digest(directory/'replay'),request_test_passed=True))
    result=read(checkpoint)
    assert result['inputs']==inputs and result['request_test_passed'] and digest(directory/'replay')==result['binary_sha256']
    return directory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args()
    directory=build()
    if args.build:
        print(directory.relative_to(ROOT),flush=True);return
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267'
    original=read(BASE/'build.json')['inputs']
    requests=read(ROOT/'build/pitch_attack_prefetch_screen/requests.json')
    calibration=ROOT/'build/pitch_continuity_calibration/66b2f935153a348e'
    source_paths={name:ROOT/'build/pitch_attack_evidence/c2298a7181c716c3'/(name+'.tsv') for name in ('training-1','training-2','training-3')}
    source_paths['training-4']=calibration/'model.tsv'
    results={}
    for name,dense in source_paths.items():
        rate=read(baseline/'report.json')['recordings'][name]['rate']
        ends=requests['schedules'][name]['strong_change'] if name!='training-4' else read(calibration/'support.json')['requests']
        requested=directory/(name+'-requests.txt');requested.write_text(''.join(str(e)+'\n' for e in ends))
        target=directory/(name+'.tsv')
        subprocess.run([str(directory/'replay'),str(baseline/(name+'.f32')),str(rate),str(ROOT/original['library']),str(ROOT/original['model']),str(target),str(requested)],check=True,timeout=1800)
        with dense.open() as stream:
            expected={(int(r['end_sample']),int(r['midi'])):r for r in csv.DictReader(stream,delimiter='\t') if int(r['end_sample']) in set(ends)}
        with target.open() as stream:
            actual={(int(r['end_sample']),int(r['midi'])):r for r in csv.DictReader(stream,delimiter='\t')}
        assert actual.keys()==expected.keys()
        maximum=max(abs(float(r[k])-float(expected[key][k])) for key,r in actual.items() for k in ('legacy','edge4_note','edge4_onset'))
        assert maximum<1e-8
        results[name]=dict(captures=len(actual)//88,maximum_model_error=maximum,sha256=digest(target),dense_sha256=digest(dense),requests_sha256=digest(requested))
        print(name,json.dumps(results[name]),flush=True)
    # Empty requests must succeed without trying to load a model or runtime.
    empty=directory/'empty.txt';empty.write_text('')
    subprocess.run([str(directory/'replay'),str(baseline/'training-1.f32'),'44100','missing-runtime','missing-model',str(directory/'empty.tsv'),str(empty)],check=True)
    atomic_json(directory/'parity.json',dict(build_sha256=digest(directory/'build.json'),recordings=results,passed=True,
        scope='Same probability tensors at selected endpoints; execution times are measured afresh and are not asserted equal to dense capture. No asynchronous worker or latency qualification.'))
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'parity.json').relative_to(ROOT)),sha256=digest(directory/'parity.json')))


if __name__=='__main__':
    main()
