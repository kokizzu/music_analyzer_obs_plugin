#!/usr/bin/env python3
"""Publish sparse inference and control protocol without unrelated work."""
import argparse
import ast
import csv
import json
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge
from validate_pitch_continuity_controls import load

PATHS=['make/pitch_heldout.mk','make/pitch_continuity_controls.mk',
       'tests/pitch_evidence_requests.hpp','tests/pitch_evidence_requests.cpp',
       'scripts/build_selected_pitch_evidence.py','scripts/pitch_continuity_control_evidence.py',
       'scripts/validate_pitch_continuity_controls.py','scripts/checkpoint_pitch_controls.py',
       'scripts/inspect_routing_replays.py','docs/routing_duration_goal.md','tests/test_pitch_control_tail.py']


def verify():
    identity();directory,plan=load()
    assert len(plan['cases'])==1154 and sum(s['windows'] for s in plan['cases'])==94834
    assert plan['stop_on_first_failure']
    gate=json.loads((ROOT/'build/pitch_control_gate_parity/report.json').read_text())
    assert gate['passed'] and len(gate['recordings'])==4
    assert all(digest(ROOT/p)==h for p,h in gate['helpers'].items())
    pointer=json.loads((ROOT/'build/selected_pitch_evidence_native/current.json').read_text())
    parity=ROOT/pointer['report'];assert digest(parity)==pointer['sha256']
    assert json.loads(parity.read_text())['passed']
    snapshot=json.loads((directory/'report.json').read_text())
    assert snapshot['plan_sha256']==digest(directory/'plan.json')
    completed=snapshot['recordings'];assert completed
    assert list(completed)==[s['id'] for s in plan['cases'][:len(completed)]]
    cases={s['id']:s for s in plan['cases']}
    for name,entry in completed.items():
        sample=cases[name]
        assert all(digest(directory/name/p)==h for p,h in entry['files'].items())
        assert digest(ROOT/sample['raw'])==sample['raw_sha256']
        assert digest(ROOT/sample['reference'])==sample['reference_sha256']
        with (directory/name/'pair.tsv').open() as stream,(ROOT/sample['reference']).open() as reference:
            rows=list(csv.DictReader(stream,delimiter='\t'));original=list(csv.DictReader(reference,delimiter='\t'))
        assert len(rows)==len(original)==sample['windows']==entry['windows']
        columns=('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums')
        assert all(all(r[k]==o[k] for k in columns) for r,o in zip(rows,original))
        visible=lambda row,key:{int(m) for m in row[key].split(',') if m}
        after=[visible(r,'after_keys') for r in rows]
        allowed={}
        if sample['family']=='piano' and 'midi' in sample:
            assert digest(ROOT/sample['midi'])==sample['midi_sha256']
            for note in read_intervals((ROOT/sample['midi']).read_bytes()):
                if note['channel']!=9:
                    allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
            allowed={m:merge(v) for m,v in allowed.items()}
        actual={k:0 for k in entry['metrics']}
        for index,row in enumerate(rows):
            before=visible(row,'keys');added=after[index]-before
            actual['added']+=len(added);actual['removed']+=len(before-after[index])
            actual['unrelated_changes']+=bool(row['unrelated_difference'])
            actual['tempo_changes']+=row['bpm_changed']!='0'
            actual['survivor_changes']+=row['survivor_changed']!='0'
            for midi in added:
                actual['isolated_additions']+=midi not in (after[index-1] if index else set()) and midi not in (after[index+1] if index+1<len(rows) else set())
                if sample['family']!='piano':
                    actual['nonpiano_or_unscored_additions']+=1
                elif 'expected_midi' in sample:
                    actual['wrong_isolated_piano_pitches']+=midi!=sample['expected_midi']
                else:
                    start=int(row['end_sample'])/sample['rate'];end=min(sample['windows']*.05,start+.05)
                    actual['unsupported_piano_added_seconds']+=max(0.,end-start-coverage(allowed.get(midi,[]),start,end))
        assert all(abs(actual[k]-v)<1e-8 for k,v in entry['metrics'].items())
        assert entry['passed']==all(abs(v)<1e-8 for k,v in entry['metrics'].items() if k!='added')
    failures=[n for n,r in completed.items() if not r['passed']]
    if snapshot['complete']:
        assert snapshot['evaluated_cases']==len(completed) and snapshot['selected_cases']==len(plan['cases'])
        assert snapshot['failed_cases']==failures and snapshot['stopped_on_failure']==bool(failures)
        assert snapshot['passed']==(not failures and len(completed)==len(plan['cases']))
        if failures:
            assert failures==[list(completed)[-1]] and snapshot['decision']=='reject_controls'
        else:
            assert len(completed)==len(plan['cases']) and snapshot['decision']=='requires_live_worker_and_latency'
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    atomic_json(directory/'verified_snapshot.json',dict(snapshot=snapshot,
        scope='Completed cases only; a running prefix is provisional. No production or live latency claim.'))
    print(json.dumps(dict(completed=len(completed),selected=len(plan['cases']),complete=snapshot['complete'],
        failed=[n for n,r in completed.items() if not r['passed']])),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--publish',action='store_true')
    args=parser.parse_args();verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity();assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS);git('diff','--cached','--check')
    (ROOT/'build/pitch_controls_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Add sparse pitch inference parity and frozen continuous controls'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
