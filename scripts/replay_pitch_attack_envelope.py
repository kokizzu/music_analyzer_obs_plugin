#!/usr/bin/env python3
"""Replay native envelopes with causal captured evidence, not a live worker."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import hashlib
import io
import json
import math
from itertools import groupby
from pathlib import Path
import shutil
import subprocess
import tarfile
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from joint_pitch_reference import fit
from piano_context_features import features
from pitch_attack_queue import simulate_latest,available_result
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from transfer_real_piano_dictionary import observations


def read(path):
    return json.loads(path.read_text())


def build():
    identity()
    assets=['tests/joint_grace_pair.cpp','tests/note_grid_comparison.hpp','tests/pitch_attack_replay_support.hpp']
    objects=ROOT/'build/routing_duration_primary/02001c66f49dc729'
    object_paths=[objects/(name+'.o') for name in ('BTT','DFT','Filter','STFT','Statistics','fastsin',
                  'basic_pitch_onnx_worker','basic_pitch_onnx_runtime','basic_pitch_onnx_decoder','basic_pitch_pcm_history')]
    inputs=dict(source_tree=git('rev-parse','HEAD:src').strip(),script_sha256=digest(Path(__file__)),
        assets={p:digest(ROOT/p) for p in assets},objects={str(p.relative_to(ROOT)):digest(p) for p in object_paths},
        hypothesis='Audio-supported immediate confirmation; existing native envelope and downstream processing unchanged')
    directory=ROOT/'build/pitch_attack_envelope_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if not checkpoint.exists():
        archive=subprocess.run(['git','archive','HEAD','src'],cwd=ROOT,capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            for member in stream:
                if member.name=='src' and member.isdir():
                    continue
                assert member.name.startswith('src/') and '..' not in Path(member.name).parts
                if member.isfile():
                    target=directory/member.name
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(stream.extractfile(member).read())
        header=directory/'src/analyzer.hpp'
        text=header.read_text()
        anchor='\tbool native_piano_duplicate_consensus = true;'
        assert text.count(anchor)==1
        header.write_text(text.replace(anchor,anchor+'\n\tbool experimental_pitch_attack_replay = false;',1))
        cpp=directory/'src/analyzer.cpp'
        text=cpp.read_text()
        text='#include "pitch_attack_replay_support.hpp"\n'+text
        anchor='\t\tsmooth_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_tracking_, -1,'
        assert text.count(anchor)==1
        text=text.replace(anchor,'''
        std::array<float,kNoteProbeCount> replay_attack_floors;
        replay_attack_floors.fill(mixed_source ? kMixedNoteEnvelopeImmediateConfirmFloor : kNoteEnvelopeImmediateConfirmFloor);
        const bool replay_attack_eligible = settings.experimental_pitch_attack_replay &&
            input_mode == AnalysisInputMode::FullMix && !settings.basic_pitch_vocal_fusion_enabled &&
            count == usable && usable == static_cast<std::size_t>(std::lround(sample_rate_*.1)) &&
            std::abs(settings.analysis_interval_seconds-.05f)<1e-6f && dropped_windows==0 &&
            (sample_rate_==16000 || sample_rate_==44100 || sample_rate_==48000);
        if (replay_attack_eligible)
            for (std::size_t i=0;i<88;++i)
                if (mao_attack_replay::supported[i]) replay_attack_floors[i]=kNoteEnvelopeNewNoteFloor;
'''+anchor,1)
        begin=text.index(anchor)
        end=text.index(';',begin)
        body=text[begin:end]
        suffix='mixed_source ? &mixed_keyboard_display_candidates : nullptr)'
        assert body.count(suffix)==1
        text=text[:begin]+body.replace(suffix,suffix[:-1]+', &replay_attack_floors)',1)+text[end:]
        cpp.write_text(text)
        shutil.copy2(ROOT/assets[2],directory/'src/pitch_attack_replay_support.hpp')
        for name in ('note_grid_comparison.hpp',):
            shutil.copy2(ROOT/'tests'/name,directory/name)
        shutil.copy2(ROOT/'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp',directory/'non_tempo_snapshot.hpp')
        harness=(ROOT/assets[0]).read_text().replace('experimental_joint_grace','experimental_pitch_attack_replay')
        harness='#include "pitch_attack_replay_support.hpp"\n#include <map>\n#include <sstream>\n'+harness
        harness=harness.replace('argc != 4','argc != 5',1)
        anchor='\tmao::AnalysisSettings settings;'
        assert harness.count(anchor)==1
        harness=harness.replace(anchor,'''
    std::map<std::size_t,std::array<bool,88>> support;
    std::ifstream evidence(argv[4]);
    if (!evidence) return 4;
    std::string line;
    std::size_t previous=0;
    while (std::getline(evidence,line)) {
        std::istringstream row(line);
        std::size_t endpoint; int midi;
        if (!(row>>endpoint>>midi) || endpoint<previous || midi<21 || midi>108) return 5;
        support[endpoint][midi-21]=true; previous=endpoint;
    }
'''+anchor,1)
        anchor='\t\tend += hop;'
        assert harness.count(anchor)==1
        harness=harness.replace(anchor,anchor+'\n\t\tmao_attack_replay::supported=support[end];',1)
        (directory/'pair.cpp').write_text(harness)
        include=['-I'+str(directory/'src'),'-I'+str(directory),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),
                 '-I'+str(objects/'third_party/beat_and_tempo_tracking')]
        subprocess.run(['g++','-O2','-std=c++17',*include,'-c',str(cpp),'-o',str(directory/'analyzer.o')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,str(directory/'pair.cpp'),str(directory/'analyzer.o'),
                        *map(str,object_paths),'-lm','-pthread','-ldl','-o',str(directory/'pair')],check=True)
        atomic_json(checkpoint,dict(inputs=inputs,binary_sha256=digest(directory/'pair'),
            cpp_sha256=digest(cpp),hpp_sha256=digest(header)))
    result=read(checkpoint)
    assert result['inputs']==inputs and digest(directory/'pair')==result['binary_sha256']
    return checkpoint


def prepare(directory):
    evidence_path=ROOT/read(ROOT/'build/pitch_attack_evidence/current.json')['report']
    evidence=read(evidence_path)
    requests_path=ROOT/'build/pitch_attack_prefetch_screen/requests.json'
    requests=read(requests_path)
    assert all(digest(ROOT/p)==h for p,h in requests['inputs'].items())
    matrix_path=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/dictionary.npz'
    context_path=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
    matrix=np.load(matrix_path)['dictionary']
    context=read(context_path)
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    native_path=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    native=read(native_path)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (evidence_path,requests_path,matrix_path,context_path,baseline_path,native_path)}
    prepared={}
    for name,recording in evidence['recordings'].items():
        rate=recording['rate']
        hop,count=round(rate*.05),round(rate*.1)
        raw=baseline_path.parent/(name+'.f32')
        native_input=native_path.parent/(name+'.tsv')
        captured=evidence_path.parent/(name+'.tsv')
        assert digest(raw)==recording['raw_sha256']==baseline['recordings'][name]['prefix_sha256']
        assert digest(native_input)==native['recordings'][name]['sha256']
        assert digest(captured)==recording['sha256']
        inputs.update({str(p.relative_to(ROOT)):digest(p) for p in (raw,native_input,captured)})
        audio=np.fromfile(raw,dtype='<f4')
        padded=np.pad(audio,(count,0))
        observed=observations(audio.astype(float),rate)
        activation=fit(matrix,observed)
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(matrix.T@observed,1e-12)
        events=[]
        requested=set(requests['schedules'][name]['strong_change'])
        with captured.open() as stream:
            for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                group=list(rows)
                if end in requested:
                    events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(group[0]['wall_ms']),
                        notes={int(r['midi']):float(r['edge4_note']) for r in group}))
        queue=simulate_latest(events,rate)
        support=[]
        with native_input.open() as stream:
            for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
                row=next(rows)
                assert end==(index+1)*hop
                latest=available_result(queue,end,round(rate*.15))
                if latest is None or row['mfcc_valid']!='1':
                    continue
                vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                if lower_probability(context['model'],vector)<context['negative_max']+.001:
                    continue
                for midi in range(21,109):
                    if relative[midi-21,index]>=.8 and explained[midi-21,index]>=.3 and events[latest['event_index']]['notes'][midi]>=.3:
                        support.append((end,midi))
        target=directory/(name+'-support.tsv')
        target.write_text(''.join(str(e)+'\t'+str(m)+'\n' for e,m in support))
        prepared[name]=dict(path=str(target.relative_to(ROOT)),sha256=digest(target),cells=len(support),rate=rate,raw=str(raw.relative_to(ROOT)))
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'evidence.json',dict(inputs=inputs,recordings=prepared,
        scope='All 88 pitches at every endpoint, audio-only gates; no first-hit cases or MIDI annotations used. Captured completion-time simulation, not a live worker.'))
    return prepared


def main():
    checkpoint=build()
    directory=checkpoint.parent
    prepared=prepare(directory)
    # Freeze full-frame audio support before any annotation scoring.
    plan=dict(build=str(checkpoint.relative_to(ROOT)),build_sha256=digest(checkpoint),
              evidence_sha256=digest(directory/'evidence.json'),recordings=prepared,
              scope='Native envelope feasibility replay. Fixed development strong_change/edge4 policy, assumed 5 ms preparation; no hardware latency or promotion claim.')
    atomic_json(directory/'plan.json',plan)
    for name,row in prepared.items():
        subprocess.run([str(directory/'pair'),str(ROOT/row['raw']),str(row['rate']),str(directory/(name+'.tsv')),str(ROOT/row['path'])],check=True,timeout=3600)
        print(name,'native paired replay complete',flush=True)
    atomic_json(directory/'replay.json',dict(plan_sha256=digest(directory/'plan.json'),complete=True,
        outputs={name:digest(directory/(name+'.tsv')) for name in prepared}))
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'replay.json').relative_to(ROOT)),sha256=digest(directory/'replay.json')))
    print(directory.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
