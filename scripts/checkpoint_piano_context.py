#!/usr/bin/env python3
"""Review and publish only the disabled acoustic-piano context research."""
import argparse
import ast
import json
import subprocess
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS=['make/routing_duration.mk','make/piano_context.mk','docs/routing_duration_goal.md',
       'scripts/piano_context_features.py','scripts/capture_piano_context.py','scripts/evaluate_piano_context.py',
       'scripts/audit_piano_context_recovery.py','scripts/checkpoint_piano_context.py',
       'scripts/inspect_routing_replays.py','tests/test_piano_context_features.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    data_path=ROOT/'build/piano_context_data/6bd7cc884c68ff15/report.json'
    data=read(data_path)
    assert data['complete'] and data['rows']==11123
    assert all(digest(ROOT/p)==h for p,h in data['inputs']['scripts'].items())
    model_path=ROOT/'build/piano_context_model/3b35eca632935a8c/report.json'
    model=read(model_path)
    assert model['inputs']['data']['sha256']==digest(data_path)
    assert all(digest(ROOT/p)==h for p,h in model['inputs']['scripts'].items())
    assert digest(ROOT/model['frozen'])==model['frozen_sha256']
    assert model['threshold']==.99
    assert model['metrics']['heldout']['negative_rows']==1932
    assert model['metrics']['heldout']['accepted_negative']==0
    audit=read(ROOT/'build/piano_context_recovery/report.json')
    assert all(digest(ROOT/p)==h for p,h in audit['inputs'].items())
    assert sum(r['proposed'] for r in audit['summary'].values())==76
    assert not any(r['accepted'] for r in audit['summary'].values())
    assert 'experimental_joint_body' not in git('show','HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    subprocess.run(['make','test-piano-context-features'],cwd=ROOT,check=True)
    print('Verified grouped context screen and zero retained recovery benefit; no production change',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',action='store_true')
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity()
    assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS)
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('diff','--cached','--check')
    diff=git('diff','--cached')
    (ROOT/'build/piano_context_staged.diff').write_text(diff)
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Screen independent piano context and reject guard without recovery benefit'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
