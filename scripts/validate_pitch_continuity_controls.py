#!/usr/bin/env python3
"""Continuous preservation on the frozen 1154-case instrument suite."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from pitch_continuity_control_evidence import audio_gates,support_text
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge
from validate_pitch_continuity_calibration import NATIVE,MODEL,CONTEXT,DICTIONARY

SOURCE=ROOT/'build/multiscale_low_keyboard_controls/02e823638e79b6e3'
POINTER=ROOT/'build/pitch_continuity_controls/current.json'


def read(path):
    return json.loads(path.read_text())


def parity():
    tools=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541'
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267'
    matrix=np.load(DICTIONARY)['dictionary'];context=read(CONTEXT);results={}
    original=read(ROOT/'build/pitch_attack_prefetch_screen/requests.json')
    for name in ('training-1','training-2','training-3','training-4'):
        raw=baseline/(name+'.f32');feature=tools/(name+'-features.tsv');rate=44100
        frames,requests=audio_gates(raw,feature,rate,matrix,context)
        if name=='training-4':
            directory=ROOT/'build/pitch_continuity_calibration/66b2f935153a348e'
            expected=read(directory/'support.json')['requests'];target=directory/'support.tsv';model=directory/'model.tsv'
        else:
            expected=original['schedules'][name]['strong_change'];target=ROOT/'build/pitch_attack_continuity_screen'/(name+'-native-support.tsv')
            model=ROOT/'build/pitch_attack_evidence/c2298a7181c716c3'/(name+'.tsv')
        assert requests==expected
        # Dense reference contains nonrequested snapshots; filter it without changing timings.
        temporary=ROOT/'build/pitch_control_gate_parity';temporary.mkdir(parents=True,exist_ok=True)
        filtered=temporary/(name+'.tsv')
        with model.open() as source,filtered.open('w') as out:
            reader=csv.DictReader(source,delimiter='\t');writer=csv.DictWriter(out,fieldnames=reader.fieldnames,delimiter='\t');writer.writeheader()
            for row in reader:
                if int(row['end_sample']) in set(requests):
                    writer.writerow(row)
        text,stats=support_text(frames,requests,filtered,rate)
        assert text==target.read_text()
        results[name]=dict(frames=len(frames),requests=stats['requests'],support_sha256=digest(target))
    atomic_json(ROOT/'build/pitch_control_gate_parity/report.json',dict(passed=True,recordings=results,
        helpers={p:digest(ROOT/p) for p in ('scripts/pitch_continuity_control_evidence.py','scripts/validate_pitch_continuity_controls.py')}))
    print('Exact request and all-pitch seed/sustain mask parity across 4800 known frames',flush=True)


def freeze():
    identity();held=ROOT/'build/pitch_continuity_heldout/e6e6ad529ce07f1c/report.json'
    assert read(held)['complete'] and read(held)['passed']
    selected_pointer=read(ROOT/'build/selected_pitch_evidence_native/current.json')
    selected_parity=ROOT/selected_pointer['report'];assert digest(selected_parity)==selected_pointer['sha256'] and read(selected_parity)['passed']
    gate_parity=ROOT/'build/pitch_control_gate_parity/report.json';assert read(gate_parity)['passed']
    source_plan=read(SOURCE/'plan.json');entries={};files=[SOURCE/'plan.json',held,selected_parity,gate_parity,NATIVE/'build.json',CONTEXT,DICTIONARY,Path(__file__)]
    for shard in range(4):
        path=SOURCE/('report-'+str(shard)+'.json');report=read(path);assert report['complete'] and report['passed']
        assert report['plan_sha256']==digest(SOURCE/'plan.json');files.append(path);entries.update(report['recordings'])
    cases=[]
    for sample in source_plan['cases']:
        name=sample['id'];entry=entries[name]
        raw=SOURCE/(name+'.f32') if sample['fresh'] else ROOT/sample['raw'];reference=SOURCE/(name+'.tsv')
        assert digest(raw)==entry['raw_sha256'] and digest(reference)==entry['sha256']
        cases.append(dict(sample,raw=str(raw.relative_to(ROOT)),raw_sha256=digest(raw),rate=entry['rate'],reference=str(reference.relative_to(ROOT)),reference_sha256=digest(reference),windows=entry['windows']))
    cases.sort(key=lambda s:(0 if s['family'] in ('guitar','vocals','voice') or 'vocalset' in s['id'] or 'guitarset' in s['id'] else 2 if s['family']=='piano' else 1,s['id']))
    assert len(cases)==1154 and sum(s['windows'] for s in cases)==94834
    tools=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541';selected=selected_parity.parent
    files += [tools/'features',selected/'replay',NATIVE/'pair',MODEL/'build.json',ROOT/read(MODEL/'build.json')['inputs']['model'],ROOT/read(MODEL/'build.json')['inputs']['library']]
    files += [ROOT/'scripts'/p for p in ('pitch_continuity_control_evidence.py','pitch_attack_queue.py','piano_context_features.py','joint_pitch_reference.py',
        'transfer_real_piano_dictionary.py','evaluate_guitar_duplicate_model.py','audit_keyboard_recovery.py','midi_sustain_reference.py','routing_duration_score.py')]
    plan=dict(inputs={str(p.relative_to(ROOT)):digest(p) for p in files},cases=cases,tools=str(tools.relative_to(ROOT)),selected=str(selected.relative_to(ROOT)),
        stop_on_first_failure=True,scope='Frozen 1154-case continuous suite. Original and derived rates are not independent recordings. Known nonpiano and unscored additions are both rejected; static isolated-piano additions certify pitch, not release timing. Captured measured-time availability, not live-worker latency qualification.')
    key=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()[:16];directory=POINTER.parent/key;directory.mkdir(parents=True,exist_ok=True)
    path=directory/'plan.json'
    if path.exists():
        assert read(path)==plan
    else:
        atomic_json(path,plan)
    atomic_json(POINTER,dict(plan=str(path.relative_to(ROOT)),sha256=digest(path)))
    print(path.relative_to(ROOT),'1154 cases, 94834 windows',flush=True)


def load():
    pointer=read(POINTER);path=ROOT/pointer['plan'];assert digest(path)==pointer['sha256'];plan=read(path)
    assert all(digest(ROOT/p)==h for p,h in plan['inputs'].items())
    return path.parent,plan


def run():
    directory,plan=load();matrix=np.load(DICTIONARY)['dictionary'];context=read(CONTEXT);model_inputs=read(MODEL/'build.json')['inputs']
    with (directory/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);checkpoint=directory/'report.json'
        state=read(checkpoint) if checkpoint.exists() else dict(plan_sha256=digest(directory/'plan.json'),recordings={},complete=False)
        assert state['plan_sha256']==digest(directory/'plan.json')
        for sample in plan['cases']:
            name=sample['id'];job=directory/name;job.mkdir(parents=True,exist_ok=True)
            if name not in state['recordings']:
                raw=ROOT/sample['raw'];rate=sample['rate'];assert digest(raw)==sample['raw_sha256']
                feature=job/'features.tsv';requested=job/'requests.txt';model=job/'model.tsv';support=job/'support.tsv'
                if rate in (16000,44100,48000):
                    subprocess.run([str(ROOT/plan['tools']/'features'),str(raw),str(rate),str(feature)],check=True)
                    frames,requests=audio_gates(raw,feature,rate,matrix,context)
                    requested.write_text(''.join(str(e)+'\n' for e in requests))
                    subprocess.run([str(ROOT/plan['selected']/'replay'),str(raw),str(rate),str(ROOT/model_inputs['library']),str(ROOT/model_inputs['model']),str(model),str(requested)],check=True,timeout=1800,stdout=subprocess.DEVNULL)
                    text,stats=support_text(frames,requests,model,rate);support.write_text(text)
                else:
                    # The frozen native trial explicitly resets/bypasses its cache
                    # outside these three rates. Exercise that actual path without
                    # resampling the reference PCM or inventing unsupported gates.
                    for path in (feature,requested,model,support):
                        path.write_text('')
                    stats=dict(requests=0,processed=0,estimated_worker_core_share=0.,
                        scope='Native unsupported-rate bypass; no feature/model evaluation')
                output=job/'pair.tsv';subprocess.run([str(NATIVE/'pair'),str(raw),str(rate),str(output),str(support)],check=True,timeout=3600)
                with output.open() as stream,(ROOT/sample['reference']).open() as reference:
                    rows=list(csv.DictReader(stream,delimiter='\t'));expected=list(csv.DictReader(reference,delimiter='\t'))
                assert len(rows)==len(expected)==sample['windows']
                columns=('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums')
                assert all(all(r[k]==e[k] for k in columns) for r,e in zip(rows,expected)),name+' primary mismatch'
                allowed={}
                if sample['family']=='piano' and 'midi' in sample:
                    assert digest(ROOT/sample['midi'])==sample['midi_sha256']
                    for note in read_intervals((ROOT/sample['midi']).read_bytes()):
                        if note['channel']!=9:
                            allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
                    allowed={m:merge(v) for m,v in allowed.items()}
                sets=[{int(m) for m in r['after_keys'].split(',') if m} for r in rows]
                metrics=dict(added=0,removed=0,nonpiano_or_unscored_additions=0,wrong_isolated_piano_pitches=0,unsupported_piano_added_seconds=0.,
                    isolated_additions=0,unrelated_changes=0,tempo_changes=0,survivor_changes=0)
                for index,row in enumerate(rows):
                    before={int(m) for m in row['keys'].split(',') if m};after=sets[index]
                    metrics['removed']+=len(before-after);metrics['added']+=len(after-before)
                    metrics['unrelated_changes']+=bool(row['unrelated_difference']);metrics['tempo_changes']+=row['bpm_changed']!='0';metrics['survivor_changes']+=row['survivor_changed']!='0'
                    for midi in after-before:
                        metrics['isolated_additions']+=midi not in (sets[index-1] if index else set()) and midi not in (sets[index+1] if index+1<len(rows) else set())
                        if sample['family']!='piano':
                            metrics['nonpiano_or_unscored_additions']+=1
                        elif 'expected_midi' in sample:
                            metrics['wrong_isolated_piano_pitches']+=midi!=sample['expected_midi']
                        else:
                            start=int(row['end_sample'])/rate;end=min(sample['windows']*.05,start+.05)
                            metrics['unsupported_piano_added_seconds']+=max(0.,end-start-coverage(allowed.get(midi,[]),start,end))
                passed=all(abs(v)<1e-8 for k,v in metrics.items() if k!='added')
                entry=dict(metrics=metrics,passed=passed,windows=len(rows),model=stats,
                    files={p.name:digest(p) for p in (feature,requested,model,support,output)})
                state['recordings'][name]=entry;atomic_json(checkpoint,state)
                if len(state['recordings'])%20==0 or not passed:
                    print(len(state['recordings']),name,json.dumps(entry),flush=True)
            else:
                assert all(digest(job/file)==h for file,h in state['recordings'][name]['files'].items())
            if not state['recordings'][name]['passed']:
                break
        failed=[n for n,r in state['recordings'].items() if not r['passed']]
        state.update(complete=True,evaluated_cases=len(state['recordings']),selected_cases=len(plan['cases']),failed_cases=failed,
            passed=not failed and len(state['recordings'])==len(plan['cases']),stopped_on_failure=bool(failed),
            decision='reject_controls' if failed else 'requires_live_worker_and_latency')
        atomic_json(checkpoint,state);print(json.dumps({k:v for k,v in state.items() if k!='recordings'},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('parity','freeze','run'));args=parser.parse_args()
    {'parity':parity,'freeze':freeze,'run':run}[args.mode]()


if __name__=='__main__':
    main()
