#!/usr/bin/env python3
"""Freeze twelve new performances and stop at the first preservation failure."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import wave
import numpy as np
from midi_sustain_reference import read_intervals
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from score_pitch_continuity_pair import evaluate
from validate_pitch_continuity_calibration import capture,prepare,replay,NATIVE,MODEL,CONTEXT,DICTIONARY

POINTER=ROOT/'build/pitch_continuity_heldout/current.json'


def read(path):
    return json.loads(path.read_text())


def signatures(inputs):
    assert all(digest(ROOT/p)==h for p,h in inputs.items())


def freeze():
    identity()
    calibration=ROOT/'build/pitch_continuity_calibration/66b2f935153a348e'
    assert read(calibration/'score.json')['passed']
    assert digest(calibration/'plan.json')==read(calibration/'score.json')['plan_sha256']
    signatures(read(calibration/'plan.json')['inputs'])
    tools_pointer=read(ROOT/'build/pitch_heldout_tools/current.json')
    parity_path=ROOT/tools_pointer['report'];assert digest(parity_path)==tools_pointer['sha256']
    parity=read(parity_path);assert parity['passed']
    tools=parity_path.parent;built=read(tools/'build.json')
    assert digest(tools/'build.json')==parity['build_sha256']
    assert built['inputs']['source_tree']==git('rev-parse','HEAD:src').strip()
    assert all(digest(tools/name)==h for name,h in built['binaries'].items())
    base=ROOT/'build/maestro_real_samples';manifest=base/'maestro-v3.0.0.csv'
    with manifest.open() as stream:
        rows=list(csv.DictReader(stream))
    previous_audio={digest(base/r['audio_filename']) for r in rows[:44]}
    previous_midi={digest(base/r['midi_filename']) for r in rows[:44]}
    baseline=read(ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json')
    previous_audio.update(s['audio_sha256'] for s in baseline['selection']);previous_midi.update(s['midi_sha256'] for s in baseline['selection'])
    selection=[];skipped=[];selected_audio=set();selected_midi=set()
    for number,row in enumerate(rows[44:],45):
        audio=base/row['audio_filename'];midi=base/row['midi_filename']
        a,m=digest(audio),digest(midi)
        if a in previous_audio|selected_audio or m in previous_midi|selected_midi:
            skipped.append(dict(row=number,reason='complete audio or MIDI hash already used'));continue
        with wave.open(str(audio),'rb') as stream:
            rate,channels,width,frames,kind=stream.getframerate(),stream.getnchannels(),stream.getsampwidth(),stream.getnframes(),stream.getcomptype()
        if rate not in (16000,44100,48000) or channels not in (1,2) or width!=2 or frames<rate*60 or kind!='NONE':
            skipped.append(dict(row=number,reason='unsupported native PCM format or shorter than 60 seconds'));continue
        selection.append(dict(id='fresh-'+str(number),audio=str(audio.relative_to(ROOT)),midi=str(midi.relative_to(ROOT)),audio_sha256=a,midi_sha256=m,
            rate=rate,channels=channels,metadata=row))
        selected_audio.add(a);selected_midi.add(m)
        if len(selection)==12:
            break
    assert len(selection)==12
    files=[manifest,calibration/'score.json',calibration/'plan.json',NATIVE/'build.json',MODEL/'build.json',CONTEXT,DICTIONARY,tools/'build.json',parity_path,Path(__file__)]
    files += [ROOT/'scripts'/p for p in ('validate_pitch_continuity_calibration.py','score_pitch_continuity_pair.py','midi_sustain_reference.py',
        'routing_duration_score.py','audit_keyboard_recovery.py','piano_context_features.py','joint_pitch_reference.py','transfer_real_piano_dictionary.py',
        'pitch_attack_queue.py','evaluate_guitar_duplicate_model.py')]
    files += [NATIVE/'pair',MODEL/'replay',tools/'features',tools/'primary']
    files += [ROOT/p for p in read(NATIVE/'build.json')['inputs']['assets']]
    model_inputs=read(MODEL/'build.json')['inputs'];files += [ROOT/model_inputs['library'],ROOT/model_inputs['model']]
    inputs={str(p.relative_to(ROOT)):digest(p) for p in files}
    for sample in selection:
        inputs[sample['audio']]=sample['audio_sha256'];inputs[sample['midi']]=sample['midi_sha256']
    plan=dict(inputs=inputs,selection=selection,skipped=skipped,tools=str(tools.relative_to(ROOT)),seconds=60,
        context_threshold=read(CONTEXT)['negative_max']+.001,relative_floor=.8,explained_floor=.3,note_floor=.3,maximum_request_age_seconds=.15,display_hops=3,preparation_ms=5.,
        stop_on_first_failure=True,minimum_beneficial_recordings=2,
        scope='First twelve eligible complete performances after manifest row 44, disjoint by full audio/MIDI hashes from known earlier cohorts and fitting. Cohort frozen before PCM decoding or MIDI interval scoring. No parameter tuning or production promotion; captured evidence is not live-worker latency qualification.')
    key=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()[:16]
    directory=POINTER.parent/key;directory.mkdir(parents=True,exist_ok=True)
    target=directory/'plan.json'
    if target.exists():
        assert read(target)==plan
    else:
        atomic_json(target,plan)
    atomic_json(POINTER,dict(plan=str(target.relative_to(ROOT)),sha256=digest(target)))
    print(target.relative_to(ROOT),[s['id'] for s in selection],flush=True)


def load():
    pointer=read(POINTER);path=ROOT/pointer['plan'];assert digest(path)==pointer['sha256']
    plan=read(path);signatures(plan['inputs'])
    return path.parent,plan


def run_case(directory,plan,sample):
    name=sample['id'];job=directory/name;job.mkdir(parents=True,exist_ok=True)
    raw=job/'audio.f32';rate=sample['rate']
    if not raw.exists():
        with wave.open(str(ROOT/sample['audio']),'rb') as stream:
            pcm=np.frombuffer(stream.readframes(rate*60),dtype='<i2').reshape(-1,sample['channels'])
        mono=(pcm.astype(float).mean(axis=1)/32768).astype('<f4')
        assert len(mono)==rate*60
        mono.tofile(raw)
    tools=ROOT/plan['tools'];feature=job/'features.tsv';primary=job/'primary.tsv'
    if not feature.exists():
        subprocess.run([str(tools/'features'),str(raw),str(rate),str(feature)],check=True)
    if not primary.exists():
        subprocess.run([str(tools/'primary'),str(raw),str(rate),str(primary)],check=True,timeout=3600)
    job_plan=dict(parent_plan_sha256=digest(directory/'plan.json'),sample=sample,rate=rate,raw=str(raw.relative_to(ROOT)),feature=str(feature.relative_to(ROOT)),
        raw_sha256=digest(raw),feature_sha256=digest(feature),primary_sha256=digest(primary),context_threshold=plan['context_threshold'],scope=plan['scope'])
    target=job/'plan.json'
    if target.exists():
        assert read(target)==job_plan
    else:
        atomic_json(target,job_plan)
    capture(job,job_plan);prepare(job,job_plan);replay(job,job_plan)
    with (job/'pair.tsv').open() as stream,primary.open() as reference:
        rows=list(csv.DictReader(stream,delimiter='\t'));expected=list(csv.DictReader(reference,delimiter='\t'))
    assert len(rows)==len(expected)==1200
    result=evaluate(rows,expected,read_intervals((ROOT/sample['midi']).read_bytes()),rate)
    result.update(plan_sha256=digest(target),replay_sha256=digest(job/'replay.json'))
    atomic_json(job/'score.json',result)
    print(name,json.dumps(dict(passed=result['passed'],benefit=result['benefit'],deltas=result['deltas'],attack_gain=result['after']['matched_attacks']-result['before']['matched_attacks'])),flush=True)
    return dict(score_sha256=digest(job/'score.json'),passed=result['passed'],benefit=result['benefit'],
        files={p.name:digest(p) for p in (raw,feature,primary,job/'plan.json',job/'model.tsv',job/'capture.json',job/'support.tsv',job/'support.json',job/'pair.tsv',job/'replay.json',job/'score.json')})


def run():
    directory,plan=load()
    with (directory/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        checkpoint=directory/'report.json'
        state=read(checkpoint) if checkpoint.exists() else dict(plan_sha256=digest(directory/'plan.json'),recordings={},complete=False)
        assert state['plan_sha256']==digest(directory/'plan.json')
        for sample in plan['selection']:
            name=sample['id']
            if name in state['recordings']:
                signatures({str((directory/name/file).relative_to(ROOT)):h for file,h in state['recordings'][name]['files'].items()})
            else:
                state['recordings'][name]=run_case(directory,plan,sample)
                atomic_json(checkpoint,state)
            if not state['recordings'][name]['passed']:
                break
        failed=[name for name,row in state['recordings'].items() if not row['passed']]
        benefited=sum(row['benefit'] for row in state['recordings'].values())
        state.update(complete=True,evaluated_recordings=len(state['recordings']),selected_recordings=len(plan['selection']),
            stopped_on_failure=bool(failed),failed_recordings=failed,beneficial_recordings=benefited,
            not_evaluated=[s['id'] for s in plan['selection'] if s['id'] not in state['recordings']],
            passed=not failed and benefited>=plan['minimum_beneficial_recordings'] and len(state['recordings'])==len(plan['selection']),
            decision='reject_preservation' if failed else 'requires_controls_live_worker_and_latency' if benefited>=plan['minimum_beneficial_recordings'] else 'reject_insufficient_heldout_benefit')
        signatures(plan['inputs']);atomic_json(checkpoint,state)
        print(json.dumps({k:v for k,v in state.items() if k!='recordings'},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('freeze','run'))
    args=parser.parse_args()
    {'freeze':freeze,'run':run}[args.mode]()


if __name__=='__main__':
    main()
