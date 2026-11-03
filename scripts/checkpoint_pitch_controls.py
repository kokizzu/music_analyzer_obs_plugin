#!/usr/bin/env python3
"""Publish sparse inference and control protocol without unrelated work."""
import argparse
import ast
import json
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from validate_pitch_continuity_controls import load

PATHS=['make/pitch_heldout.mk','make/pitch_continuity_controls.mk',
       'tests/pitch_evidence_requests.hpp','tests/pitch_evidence_requests.cpp',
       'scripts/build_selected_pitch_evidence.py','scripts/pitch_continuity_control_evidence.py',
       'scripts/validate_pitch_continuity_controls.py','scripts/checkpoint_pitch_controls.py',
       'scripts/inspect_routing_replays.py','docs/routing_duration_goal.md']


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
    for name,entry in completed.items():
        assert all(digest(directory/name/p)==h for p,h in entry['files'].items())
        assert entry['passed']==all(abs(v)<1e-8 for k,v in entry['metrics'].items() if k!='added')
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
