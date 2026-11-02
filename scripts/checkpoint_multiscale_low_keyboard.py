#!/usr/bin/env python3
"""Publish the disabled multiwindow trial with explicit fresh-benefit limits."""
import argparse
import ast
import json
import subprocess
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS=['make/keyboard_release.mk','docs/routing_duration_goal.md','src/multiscale_low_keyboard.hpp',
       'scripts/screen_multiscale_low_keyboard.py','tests/test_multiscale_low_keyboard.py','tests/multiscale_low_keyboard.cpp',
       'scripts/build_multiscale_low_keyboard.py','scripts/measure_multiscale_low_keyboard.py','scripts/run_multiscale_fresh.py',
       'scripts/validate_multiscale_controls.py','scripts/benchmark_multiscale_low_keyboard.py','scripts/checkpoint_multiscale_low_keyboard.py',
       'scripts/qualify_multiscale_low_keyboard.py','scripts/inspect_routing_replays.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    build_path=ROOT/'build/multiscale_low_keyboard_native/ec738e83351c85da/build.json'
    build=read(build_path)
    assert build['regression_passed'] and digest(build_path.parent/'pair')==build['binary_sha256']
    assert digest(ROOT/'scripts/build_multiscale_low_keyboard.py')==build['inputs']['script_sha256']
    assert all(digest(ROOT/p)==h for p,h in build['inputs']['assets'].items())
    assert digest(build_path.parent/'src/analyzer.cpp')==build['cpp_sha256']
    assert digest(build_path.parent/'src/analyzer.hpp')==build['hpp_sha256']
    screen_path=ROOT/'build/multiscale_low_keyboard/eccdf0fef5d9a750/report.json'
    screen=read(screen_path)
    assert digest(ROOT/'scripts/screen_multiscale_low_keyboard.py')==screen['inputs']['script_sha256']
    assert screen['aggregate']['cells']==129 and screen['aggregate']['supported_removed_seconds']==0
    frozen_path=ROOT/'build/multiscale_low_keyboard_fresh/frozen-8a1371232dc7af1a.json'
    frozen=read(frozen_path)
    assert digest(build_path)==frozen['build_sha256']
    assert frozen['script_sha256']==digest(ROOT/'scripts/run_multiscale_fresh.py')
    for phase,ptr in frozen['phases'].items():
        path=ROOT/ptr['report']
        report=read(path)
        assert digest(path)==ptr['sha256'] and report['complete'] and report['passed']
        assert report['inputs']['driver_sha256']==digest(ROOT/'scripts/measure_multiscale_low_keyboard.py')
        for name,row in report['recordings'].items():
            assert digest(path.parent/(name+'.tsv'))==row['sha256']
            assert not any(row['deltas'][k] for k in ('supported_removed_seconds','added_cells','surviving_cell_changed_frames','unrelated_changed_frames','tempo_changed_frames'))
            assert row['before']['matched_attacks']==row['after']['matched_attacks']
        if phase=='training':
            parity=read(path.parent/'parity.json')
            assert parity['passed'] and parity['report_sha256']==digest(path) and parity['offline_sha256']==digest(screen_path)
    for sample in frozen['selection']:
        path=frozen_path.parent/frozen_path.stem/sample['id']/'report.json'
        report=read(path)
        assert report['complete'] and report['passed'] and report['frozen_sha256']==digest(frozen_path)
        assert all(digest(ROOT/p)==h for p,h in report['artifacts'].items())
        assert not any(report['deltas'].values())
        assert report['before']['matched_attacks']==report['after']['matched_attacks']
    plan=read(ROOT/'build/multiscale_low_keyboard_controls/02e823638e79b6e3/plan.json')
    assert len(plan['cases'])==1154 and plan['build_sha256']==digest(build_path)
    assert plan['script_sha256']==digest(ROOT/'scripts/validate_multiscale_controls.py')
    assert 'experimental_multiscale_low_keyboard' not in git('show','HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for target in ('test-multiscale-low-keyboard','test-native-multiscale-low-keyboard'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    qualification=ROOT/'build/multiscale_low_keyboard_qualification/report.json'
    if qualification.exists():
        report=read(qualification)
        assert all(digest(ROOT/p)==h for p,h in report['inputs'].items())
        assert not report['promote'] and report['fresh_unsupported_removed_seconds']==0
        assert report['preservation_passed'] and report['latency_run'] and report['latency_passed']
        assert report['preservation']['cases']==1154 and report['preservation']['windows']==94834
        assert report['preservation']['removed']==3261 and report['isolated_keyboard_wrong_pitches_removed']==1887
        assert all(not r['removed'] and not r['correct_losses'] for r in report['piano_performances'].values())
    print('Verified disabled native multiwindow trial: train/calibration gain, four fresh recordings unchanged; consult separate preservation/latency qualification',flush=True)


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
    (ROOT/'build/multiscale_low_keyboard_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    message=('Qualify multiwindow instrument preservation and CPU latency'
             if (ROOT/'build/multiscale_low_keyboard_qualification/report.json').exists() else
             'Validate disabled multiwindow low-note trial and record neutral fresh results')
    print(git('commit','-m',message),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
