#!/usr/bin/env python3
"""Publish exact release attribution without promoting a destructive rule."""
import argparse
import ast
import json
import subprocess
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS=['make/routing_duration.mk','make/keyboard_release.mk','scripts/audit_keyboard_release_tails.py',
       'scripts/checkpoint_keyboard_release.py','tests/test_keyboard_release_tails.py','docs/routing_duration_goal.md']


def verify():
    identity()
    report=json.loads((ROOT/'build/keyboard_release_tail_audit/report.json').read_text())
    assert all(digest(ROOT/p)==h for p,h in report['inputs'].items())
    assert set(report['recordings'])=={'training-1','training-2','training-3'}
    total=0
    held=0.
    for recording in report['recordings'].values():
        groups=recording['groups']
        for key,value in groups['raw-absent-final'].items():
            assert abs(value-groups['smoothing-tail'][key]-groups['postprocess-addition'][key])<1e-7
        assert not any(k.startswith('smoothing-tail-misses-over-13') for k in groups)
        proposals=recording['proposals']
        assert len(proposals)==groups['two-misses-no-joint-support']['cells']
        assert all(p['misses']>=2 and p['relative']<.01 and p['explained']<.01 for p in proposals)
        total+=len(proposals)
        held+=sum(p['held_seconds'] for p in proposals)
    assert total==5064 and abs(held-14.108891775261228)<1e-7
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    subprocess.run(['make','test-keyboard-release-tails'],cwd=ROOT,check=True)
    print('Verified training-only release attribution and rejection: 14.109 key-held seconds would be removed',flush=True)


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
    (ROOT/'build/keyboard_release_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Separate smoothing tails from late note insertions and reject unsafe release shortening'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
