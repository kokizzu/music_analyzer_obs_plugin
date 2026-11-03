#!/usr/bin/env python3
"""Verify completed held-out cases; a running cohort is explicitly provisional."""
import argparse
import ast
import csv
import json
import subprocess
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from midi_sustain_reference import read_intervals
from score_pitch_continuity_pair import evaluate
from validate_pitch_continuity_heldout import load

PATHS=['make/pitch_continuity_validation.mk','make/pitch_heldout.mk','docs/routing_duration_goal.md','scripts/inspect_routing_replays.py',
       'scripts/build_pitch_heldout_tools.py','tests/piano_context_pcm.cpp','tests/pitch_primary_replay.cpp',
       'scripts/score_pitch_continuity_pair.py','tests/test_score_pitch_continuity_pair.py',
       'scripts/validate_pitch_continuity_heldout.py','scripts/checkpoint_pitch_heldout.py',
       'make/keyboard_routing_audit.mk','scripts/audit_keyboard_routing_gaps.py','tests/test_keyboard_routing_gaps.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    directory,plan=load()
    assert len(plan['selection'])==12 and plan['stop_on_first_failure'] and plan['minimum_beneficial_recordings']==2
    tools=ROOT/plan['tools'];parity=read(tools/'parity.json')
    assert parity['passed'] and len(parity['recordings'])==4
    assert all(r['maximum_cepstral_error']==0 and r['context_decision_mismatches']==0 for r in parity['recordings'].values())
    snapshot=read(directory/'report.json')
    assert snapshot['plan_sha256']==digest(directory/'plan.json')
    completed=snapshot['recordings'];assert completed
    assert list(completed)==[s['id'] for s in plan['selection'][:len(completed)]]
    assessments={}
    for sample in plan['selection'][:len(completed)]:
        name=sample['id'];job=directory/name;recorded=completed[name]
        assert all(digest(job/file)==h for file,h in recorded['files'].items())
        with (job/'pair.tsv').open() as stream,(job/'primary.tsv').open() as reference:
            rows=list(csv.DictReader(stream,delimiter='\t'));primary=list(csv.DictReader(reference,delimiter='\t'))
        assert len(rows)==len(primary)==1200
        actual=evaluate(rows,primary,read_intervals((ROOT/sample['midi']).read_bytes()),sample['rate'])
        saved=read(job/'score.json')
        assert all(actual[k]==saved[k] for k in actual)
        assert actual['passed']==recorded['passed'] and actual['benefit']==recorded['benefit']
        assessments[name]=dict(passed=actual['passed'],benefit=actual['benefit'],deltas=actual['deltas'],
            attack_gain=actual['after']['matched_attacks']-actual['before']['matched_attacks'])
    failures=[name for name,row in completed.items() if not row['passed']]
    if snapshot['complete']:
        assert failures==snapshot['failed_recordings']
        if failures:
            assert failures==[list(completed)[-1]] and snapshot['decision']=='reject_preservation'
        else:
            assert len(completed)==12
            assert snapshot['passed']==(sum(r['benefit'] for r in completed.values())>=2)
    subprocess.run(['make','test-score-pitch-continuity-pair'],cwd=ROOT,check=True)
    subprocess.run(['make','test-keyboard-routing-gaps'],cwd=ROOT,check=True)
    subprocess.run(['make','audit-keyboard-routing-gaps'],cwd=ROOT,check=True)
    audit=read(ROOT/'build/keyboard_routing_gap_audit.json')
    assert all(digest(ROOT/p)==h for p,h in audit['inputs'].items())
    assert set(audit['recordings'])=={'training-1','training-2','training-3'}
    raw_missing=sum(r['stages']['raw_keyboard_absent']['missing_held_seconds'] for r in audit['recordings'].values())
    confirmation_missing=sum(r['stages']['confirmation']['missing_held_seconds'] for r in audit['recordings'].values())
    assert abs(raw_missing-291.7610650202849)<1e-7 and abs(confirmation_missing-12.331463770256388)<1e-7
    assert sum(r['attacks']['missed'] for r in audit['recordings'].values())==867
    assert sum(r['attacks']['prior_visibility_context']['prior_note_sounding'] for r in audit['recordings'].values())==224
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    atomic_json(directory/'verified_snapshot.json',dict(snapshot=snapshot,assessments=assessments,
        scope='Only completed cases in this snapshot are verified; running or unevaluated recordings are not claimed passed. No production promotion.'))
    print(json.dumps(dict(verified_recordings=len(completed),cohort_complete=snapshot['complete'],assessments=assessments)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--publish',action='store_true')
    args=parser.parse_args();verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity()
    assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS);git('diff','--cached','--check')
    (ROOT/'build/pitch_heldout_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Record completed piano continuity holdout and audit broader routing gaps'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
