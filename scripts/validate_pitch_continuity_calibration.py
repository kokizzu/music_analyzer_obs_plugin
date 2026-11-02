#!/usr/bin/env python3
"""Frozen recording-disjoint calibration of native display continuity."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse
import csv
import fcntl
import hashlib
import json
import math
from itertools import groupby
from pathlib import Path
import subprocess
import numpy as np
from audit_keyboard_recovery import coverage
from evaluate_guitar_duplicate_model import lower_probability
from joint_pitch_reference import fit
from midi_sustain_reference import read_intervals
from piano_context_features import features
from pitch_attack_queue import simulate_latest,available_result
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge,score
from transfer_real_piano_dictionary import observations

BASELINE=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
NATIVE=ROOT/'build/pitch_attack_continuity_native/e0e07f89f02d4b24'
MODEL=ROOT/'build/pitch_attack_evidence_native/9b729e8c3393b8ba'
CONTEXT=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
DICTIONARY=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/dictionary.npz'
FEATURES=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
POINTER=ROOT/'build/pitch_continuity_calibration/current.json'


def read(path):
    return json.loads(path.read_text())


def signatures(inputs):
    assert all(digest(ROOT/p)==h for p,h in inputs.items())


def freeze():
    identity()
    baseline=read(BASELINE)
    sample=next(s for s in baseline['selection'] if s['id']=='training-4')
    fitting=read(DICTIONARY.parent/'plan.json')['selection']
    other=[s for s in baseline['selection'] if s['id'] in ('training-1','training-2','training-3')]+fitting
    assert all(sample['audio_sha256']!=s['audio_sha256'] and sample['midi_sha256']!=s['midi_sha256'] for s in other)
    assert digest(ROOT/sample['audio'])==sample['audio_sha256'] and digest(ROOT/sample['midi'])==sample['midi_sha256']
    development=read(NATIVE/'score.json')
    assert development['passed'] and development['decision']=='requires_live_worker_validation'
    for directory in (NATIVE,MODEL):
        built=read(directory/'build.json')
        binary=directory/('pair' if directory==NATIVE else 'replay')
        assert digest(binary)==built['binary_sha256']
    assert all(digest(ROOT/p)==h for p,h in read(NATIVE/'build.json')['inputs']['assets'].items())
    for name,checksum in read(MODEL/'build.json')['inputs']['sources'].items():
        assert hashlib.sha256(git('show','HEAD:src/'+name).encode()).hexdigest()==checksum
    files=[BASELINE,NATIVE/'build.json',NATIVE/'score.json',MODEL/'build.json',CONTEXT,DICTIONARY,DICTIONARY.parent/'plan.json',FEATURES,Path(__file__)]
    files += [ROOT/'scripts'/p for p in ('piano_context_features.py','joint_pitch_reference.py','transfer_real_piano_dictionary.py',
        'pitch_attack_queue.py','evaluate_guitar_duplicate_model.py','midi_sustain_reference.py','routing_duration_score.py','audit_keyboard_recovery.py')]
    raw=BASELINE.parent/'training-4.f32'
    feature=FEATURES.parent/'training-4.tsv'
    assert digest(raw)==baseline['recordings']['training-4']['prefix_sha256']
    assert digest(feature)==read(FEATURES)['recordings']['training-4']['sha256']
    files += [raw,feature,ROOT/sample['audio'],ROOT/sample['midi']]
    model_inputs=read(MODEL/'build.json')['inputs']
    files += [ROOT/model_inputs['model'],ROOT/model_inputs['library']]
    assert digest(ROOT/model_inputs['model'])==model_inputs['model_sha256']
    assert digest(ROOT/model_inputs['library'])==model_inputs['library_sha256']
    plan=dict(inputs={str(p.relative_to(ROOT)):digest(p) for p in files},sample=sample,rate=baseline['recordings']['training-4']['rate'],
        raw=str(raw.relative_to(ROOT)),feature=str(feature.relative_to(ROOT)),native_build=str((NATIVE/'build.json').relative_to(ROOT)),
        model_build=str((MODEL/'build.json').relative_to(ROOT)),context_threshold=read(CONTEXT)['negative_max']+.001,
        relative_floor=.8,explained_floor=.3,note_floor=.3,maximum_request_age_seconds=.15,preparation_ms=5.,display_hops=3,
        scope='Known separate calibration recording, disjoint from development and dictionary fitting; previously used by other studies, not a fresh held-out performance. No tuning after this freeze. Captured causal model evidence, not live-worker latency qualification.')
    key=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()[:16]
    directory=POINTER.parent/key
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/'plan.json'
    if path.exists():
        assert read(path)==plan
    else:
        atomic_json(path,plan)
    atomic_json(POINTER,dict(plan=str(path.relative_to(ROOT)),sha256=digest(path)))
    print(path.relative_to(ROOT),flush=True)


def load():
    pointer=read(POINTER)
    path=ROOT/pointer['plan']
    assert digest(path)==pointer['sha256']
    plan=read(path)
    signatures(plan['inputs'])
    return path.parent,plan


def capture(directory,plan):
    target=directory/'model.tsv'
    checkpoint=directory/'capture.json'
    if checkpoint.exists():
        assert digest(target)==read(checkpoint)['sha256']
        return
    inputs=read(MODEL/'build.json')['inputs']
    pending=directory/'model.pending.tsv'
    subprocess.run([str(MODEL/'replay'),str(ROOT/plan['raw']),str(plan['rate']),str(ROOT/inputs['library']),str(ROOT/inputs['model']),str(pending)],check=True,timeout=1800)
    count=0;wall=[];cpu=[]
    with pending.open() as stream:
        for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
            group=list(rows)
            assert end==round(plan['rate']*.05)*(count+40)
            assert [int(r['midi']) for r in group]==list(range(21,109))
            assert all(math.isfinite(float(r[k])) and 0<=float(r[k])<=1 for r in group for k in ('legacy','edge4_note','edge4_onset'))
            wall.append(float(group[0]['wall_ms']));cpu.append(float(group[0]['cpu_ms']));count+=1
    assert count==1161 and all(math.isfinite(v) and v>=0 for v in wall+cpu)
    pending.replace(target)
    atomic_json(checkpoint,dict(sha256=digest(target),captures=count,mean_wall_ms=sum(wall)/count,max_wall_ms=max(wall),mean_cpu_ms=sum(cpu)/count))
    print('Captured',count,'calibration model snapshots',flush=True)


def prepare(directory,plan):
    assert digest(directory/'model.tsv')==read(directory/'capture.json')['sha256']
    rate=plan['rate'];hop=round(rate*.05);count=round(rate*.1)
    audio=np.fromfile(ROOT/plan['raw'],dtype='<f4');padded=np.pad(audio,(count,0))
    matrix=np.load(DICTIONARY)['dictionary']
    x=observations(audio.astype(float),rate)
    activation=fit(matrix,x)
    relative=activation/np.maximum(activation.max(axis=0),1e-12)
    explained=activation/np.maximum(matrix.T@x,1e-12)
    context=read(CONTEXT)
    frames=[];requests=[];previous=set()
    with (ROOT/plan['feature']).open() as stream:
        for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
            row=next(rows);assert end==(index+1)*hop
            strong={i+21 for i in range(88) if relative[i,index]>=.8 and explained[i,index]>=.3}
            new=strong-previous;previous=strong
            probability=0.
            if row['mfcc_valid']=='1':
                vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                probability=lower_probability(context['model'],vector)
            if probability>=plan['context_threshold'] and new:
                requests.append(end)
            frames.append((end,strong if probability>=plan['context_threshold'] else set(),{i+21 for i in range(88) if explained[i,index]>=.3}))
    assert len(frames)==1200
    events=[];selected=set(requests)
    with (directory/'model.tsv').open() as stream:
        for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
            group=list(rows)
            if end in selected:
                events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(group[0]['wall_ms']),cpu_ms=float(group[0]['cpu_ms']),notes={int(r['midi']):float(r['edge4_note']) for r in group}))
    queue=simulate_latest(events,rate)
    lines=[]
    for end,strong,continuing in frames:
        latest=available_result(queue,end,round(rate*.15))
        if latest is None:
            continue
        notes=events[latest['event_index']]['notes']
        for midi in range(21,109):
            seed=midi in strong and notes[midi]>=.3
            sustain=midi in continuing and notes[midi]>=.3
            if seed or sustain:
                lines.append(f'{end}\t{midi}\t{int(seed)}\t{int(sustain)}\n')
    target=directory/'support.tsv';target.write_text(''.join(lines))
    atomic_json(directory/'support.json',dict(plan_sha256=digest(directory/'plan.json'),capture_sha256=digest(directory/'capture.json'),
        sha256=digest(target),requests=requests,processed=len(queue),estimated_worker_core_share=sum(events[r['event_index']]['cpu_ms'] for r in queue)/60000,
        scope='Frozen all-pitch audio/model support before reading MIDI note intervals; preparation delay is assumed.'))
    print('Prepared calibration support;',len(events),'model requests processed',flush=True)


def replay(directory,plan):
    assert digest(directory/'support.tsv')==read(directory/'support.json')['sha256']
    target=directory/'pair.tsv';checkpoint=directory/'replay.json'
    if checkpoint.exists():
        assert digest(target)==read(checkpoint)['sha256']
        return
    pending=directory/'pair.pending.tsv'
    subprocess.run([str(NATIVE/'pair'),str(ROOT/plan['raw']),str(plan['rate']),str(pending),str(directory/'support.tsv')],check=True,timeout=3600)
    pending.replace(target)
    atomic_json(checkpoint,dict(sha256=digest(target),support_sha256=digest(directory/'support.json'),plan_sha256=digest(directory/'plan.json')))
    print('Native calibration paired replay complete',flush=True)


def evaluate(directory,plan):
    checkpoint=read(directory/'replay.json')
    assert digest(directory/'pair.tsv')==checkpoint['sha256'] and digest(directory/'support.json')==checkpoint['support_sha256']
    assert digest(directory/'plan.json')==checkpoint['plan_sha256']
    reference=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b'
    reference_path=reference/'piano-training-4.tsv'
    assert digest(reference_path)==read(reference/'report.json')['recordings']['piano-training-4']['sha256']
    with (directory/'pair.tsv').open() as stream,reference_path.open() as expected:
        rows=list(csv.DictReader(stream,delimiter='\t'));before=list(csv.DictReader(expected,delimiter='\t'))
    assert len(rows)==len(before)==1200
    for row,original in zip(rows,before):
        assert all(row[k]==original['after_'+k if k in ('guitar','voice') else k] for k in ('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums'))
    notes=read_intervals((ROOT/plan['sample']['midi']).read_bytes())
    held={};allowed={}
    for note in notes:
        if note['channel']!=9:
            held.setdefault(note['midi'],[]).append((note['start'],note['key_end']))
            allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
    held={m:merge(v) for m,v in held.items()};allowed={m:merge(v) for m,v in allowed.items()}
    visible=[{int(m) for m in row['after_keys'].split(',') if m} for row in rows]
    delta=dict(added_cells=0,removed_cells=0,held_added_seconds=0.,supported_removed_seconds=0.,unsupported_added_seconds=0.,isolated_additions=0,
        unrelated_changed_frames=0,tempo_changed_frames=0,surviving_cell_changed_frames=0)
    additions=[];removals=[]
    for i,row in enumerate(rows):
        original={int(m) for m in row['keys'].split(',') if m};changed=visible[i]
        start=int(row['end_sample'])/plan['rate'];end=min(60.,start+.05)
        delta['unrelated_changed_frames']+=bool(row['unrelated_difference'])
        delta['tempo_changed_frames']+=row['bpm_changed']!='0';delta['surviving_cell_changed_frames']+=row['survivor_changed']!='0'
        for midi in original-changed:
            delta['removed_cells']+=1;delta['supported_removed_seconds']+=coverage(allowed.get(midi,[]),start,end)
            removals.append(dict(end_sample=int(row['end_sample']),midi=midi))
        for midi in changed-original:
            key=coverage(held.get(midi,[]),start,end);wrong=end-start-coverage(allowed.get(midi,[]),start,end)
            isolated=midi not in (visible[i-1] if i else set()) and midi not in (visible[i+1] if i+1<len(rows) else set())
            delta['added_cells']+=1;delta['held_added_seconds']+=key;delta['unsupported_added_seconds']+=wrong;delta['isolated_additions']+=isolated
            additions.append(dict(end_sample=int(row['end_sample']),midi=midi,held_seconds=key,unsupported_seconds=wrong,isolated=isolated))
    original=score(rows,notes,plan['rate'])['keys'];after=score([dict(row,keys=row['after_keys']) for row in rows],notes,plan['rate'])['keys']
    passed=not any(delta[k] for k in ('removed_cells','unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames','isolated_additions')) and delta['unsupported_added_seconds']<1e-8 and after['matched_attacks']>=original['matched_attacks']
    result=dict(plan_sha256=digest(directory/'plan.json'),replay_sha256=digest(directory/'replay.json'),before=original,after=after,deltas=delta,
        additions=additions,removals=removals,passed=passed,decision='requires_fresh_heldout_and_live_worker' if passed else 'reject_calibration',
        scope=plan['scope'])
    atomic_json(directory/'score.json',result)
    print(json.dumps(dict(deltas=delta,attack_gain=after['matched_attacks']-original['matched_attacks'],passed=passed)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('freeze','capture','prepare','replay','score'))
    args=parser.parse_args()
    if args.mode=='freeze':
        freeze();return
    directory,plan=load()
    with (directory/'calibration.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        {'capture':capture,'prepare':prepare,'replay':replay,'score':evaluate}[args.mode](directory,plan)
    signatures(plan['inputs'])


if __name__=='__main__':
    main()
