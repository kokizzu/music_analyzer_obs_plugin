#!/usr/bin/env python3
"""Recheck all four known long-window piano failures before fresh evaluation."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge
from validate_low_keyboard_controls import inspect


def read(path):
    return json.loads(path.read_text())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--record',type=int,choices=(13,15),required=True)
    args=parser.parse_args()
    pointer=read(ROOT/'build/phase_low_keyboard_native/current.json')
    build_path=ROOT/pointer['build']
    build=read(build_path)
    assert digest(build_path)==pointer['sha256'] and digest(build_path.parent/'pair')==build['binary_sha256']
    assert all(digest(ROOT/p)==h for p,h in build['inputs']['assets'].items())
    phases={}
    for phase in ('training','calibration'):
        ptr=read(ROOT/'build/phase_low_keyboard_measurement'/('current-'+phase+'.json'))
        path=ROOT/ptr['report']
        report=read(path)
        assert digest(path)==ptr['sha256'] and report['complete'] and report['passed']
        assert report['inputs']['build_sha256']==digest(build_path)
        phases[phase]=ptr
    prior_plan_path=ROOT/'build/multiscale_low_keyboard_controls/02e823638e79b6e3/plan.json'
    prior_plan=read(prior_plan_path)
    selected=[s for s in prior_plan['cases'] if s['id'] in {
        'extended-fresh-piano-'+str(n)+'-'+rate for n in (13,15) for rate in ('original','48k')}]
    assert len(selected)==4
    inputs=dict(build_sha256=digest(build_path),phases=phases,selection=selected,prior_plan_sha256=digest(prior_plan_path),
        script_sha256=digest(Path(__file__)),helpers={p:digest(ROOT/p) for p in ('scripts/validate_low_keyboard_controls.py',
            'scripts/audit_keyboard_recovery.py','scripts/midi_sustain_reference.py','scripts/routing_duration_score.py')},
        scope='Known regressions only, not fresh held-out data. Fixed phase/long-window rule; no parameter tuning.')
    directory=ROOT/'build/phase_low_keyboard_regressions'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',inputs)
    with (directory/('capture-'+str(args.record)+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        checkpoint=directory/('report-'+str(args.record)+'.json')
        state=read(checkpoint) if checkpoint.exists() else dict(plan_sha256=digest(directory/'plan.json'),recordings={},complete=False)
        assert state['plan_sha256']==digest(directory/'plan.json')
        for sample in selected:
            if '-'+str(args.record)+'-' not in sample['id']:
                continue
            raw=ROOT/sample['raw']
            assert not sample['fresh'] and digest(raw)==sample['raw_sha256']
            path=directory/(sample['id']+'.tsv')
            if sample['id'] not in state['recordings']:
                subprocess.run([str(build_path.parent/'pair'),str(raw),str(sample['rate']),str(path)],check=True,timeout=3600)
            else:
                assert digest(path)==state['recordings'][sample['id']]['sha256']
            reference=ROOT/sample['reference']
            assert digest(reference)==sample['reference_sha256']
            with reference.open() as stream:
                expected={r['end_sample']:r for r in csv.DictReader(stream,delimiter='\t')}
            entry=inspect(path,sample,sample['rate'],expected)
            midi=ROOT/sample['midi']
            assert digest(midi)==sample['midi_sha256']
            notes=[n for n in read_intervals(midi.read_bytes()) if n['channel']!=9]
            held={}
            for n in notes:
                held.setdefault(n['midi'],[]).append((n['start'],n['key_end']))
            held={m:merge(v) for m,v in held.items()}
            losses=[]
            with path.open() as stream:
                rows=list(csv.DictReader(stream,delimiter='\t'))
            entry['survivor_changes']=sum(r['survivor_changed']!='0' for r in rows)
            for row in rows:
                start=int(row['end_sample'])/sample['rate']
                before,after=({int(v) for v in row[k].split(',') if v} for k in ('keys','after_keys'))
                for m in before-after:
                    if any(n['midi']==m and n['start']-.15<start+.05 and n['end']+.3>start for n in notes):
                        losses.append(dict(end_sample=int(row['end_sample']),midi=m,held_seconds=coverage(held.get(m,[]),start,min(60.,start+.05))))
            entry['protected_loss_details']=losses
            state['recordings'][sample['id']]=entry
            atomic_json(checkpoint,state)
            print(sample['id'],json.dumps({k:v for k,v in entry.items() if k not in ('before_ms','after_ms')}),flush=True)
        assert digest(Path(__file__))==inputs['script_sha256']
        state['complete']=True
        state['passed']=not any(any(r[k] for k in ('correct_any_losses','correct_keyboard_losses','added','unrelated_changes','tempo_changes','survivor_changes')) or r['after_ms']['deadline_misses'] for r in state['recordings'].values())
        atomic_json(checkpoint,state)
        atomic_json(directory.parent/('current-'+str(args.record)+'.json'),dict(report=str(checkpoint.relative_to(ROOT)),sha256=digest(checkpoint)))
        print(checkpoint.relative_to(ROOT),'passed',state['passed'],flush=True)
        assert state['passed'],'Known piano regression remains; do not consume fresh held-out recordings'


if __name__=='__main__':
    main()
