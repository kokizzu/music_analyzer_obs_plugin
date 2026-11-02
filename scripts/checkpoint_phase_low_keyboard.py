#!/usr/bin/env python3
"""Verify pitch-leakage attribution and preserve the rejected phase trial."""
import argparse
import ast
import csv
import json
import subprocess
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest
from validate_low_keyboard_controls import inspect

PATHS=['make/keyboard_release.mk','make/phase_low_keyboard.mk','docs/routing_duration_goal.md','scripts/audit_multiscale_exposure.py',
       'tests/test_multiscale_exposure.py','scripts/phase_low_keyboard_reference.py','tests/test_phase_low_keyboard.py',
       'scripts/screen_phase_low_keyboard.py','src/phase_low_keyboard.hpp','tests/phase_low_keyboard.cpp',
       'scripts/build_phase_low_keyboard.py','scripts/measure_phase_low_keyboard.py','scripts/validate_phase_regressions.py',
       'scripts/checkpoint_phase_low_keyboard.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    exposure=read(ROOT/'build/multiscale_exposure_audit/report.json')
    assert all(digest(ROOT/p)==h for p,h in exposure['inputs'].items())
    fresh=[r for r in exposure['recordings'].values() if r['phase']=='fresh']
    assert len(fresh)==4 and sum(r['metrics']['actual_removed'] for r in fresh)==0
    assert sum(r['metrics']['eligible_unsupported_seconds'] for r in fresh)>600
    screen_path=ROOT/'build/phase_low_keyboard_screen/report.json'
    screen=read(screen_path)
    assert all(digest(ROOT/p)==h for p,h in screen['inputs'].items())
    assert screen['aggregate']['cells']==977 and screen['aggregate']['supported_removed_seconds']==0
    assert screen['parameters']==dict(amplitude_floor=.01,phase_cents=25,short_seconds=.1,long_seconds=.4,previous_visible=3)
    build_path=ROOT/'build/phase_low_keyboard_native/457dd81a7f48eb95/build.json'
    build=read(build_path)
    assert build['regression_passed'] and digest(build_path.parent/'pair')==build['binary_sha256']
    assert build['inputs']['script_sha256']==digest(ROOT/'scripts/build_phase_low_keyboard.py')
    assert all(digest(ROOT/p)==h for p,h in build['inputs']['assets'].items())
    for phase,directory in (('training','bf1df8ac312b1818'),('calibration','6a35d1d6c9e272e4')):
        path=ROOT/'build/phase_low_keyboard_measurement'/directory/'report.json'
        report=read(path)
        assert report['complete'] and report['passed'] and report['inputs']['build_sha256']==digest(build_path)
        assert report['inputs']['driver_sha256']==digest(ROOT/'scripts/measure_phase_low_keyboard.py')
        assert report['inputs']['guard_sha256']==digest(ROOT/'src/phase_low_keyboard.hpp')
        for name,row in report['recordings'].items():
            assert digest(path.parent/(name+'.tsv'))==row['sha256']
            assert not any(row['deltas'][k] for k in ('supported_removed_seconds','added_cells','unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames'))
            assert row['before']['matched_attacks']==row['after']['matched_attacks']
        if phase=='training':
            parity=read(path.parent/'parity.json')
            assert parity['passed'] and parity['report_sha256']==digest(path) and parity['offline_sha256']==digest(screen_path)
    directory=ROOT/'build/phase_low_keyboard_regressions/23c359bf2f1a72f0'
    plan=read(directory/'plan.json')
    assert plan['script_sha256']==digest(ROOT/'scripts/validate_phase_regressions.py')
    assert plan['build_sha256']==digest(build_path)
    assert all(digest(ROOT/p)==h for p,h in plan['helpers'].items())
    samples={s['id']:s for s in plan['selection']}
    contexts=[]
    for number in (13,15):
        report=read(directory/('report-'+str(number)+'.json'))
        assert report['complete'] and not report['passed'] and len(report['recordings'])==2
        assert report['plan_sha256']==digest(directory/'plan.json')
        for name,row in report['recordings'].items():
            sample=samples[name]
            path=directory/(name+'.tsv')
            assert digest(path)==row['sha256']
            actual=inspect(path,sample,sample['rate'])
            assert all(actual[k]==row[k] for k in actual)
            assert row['correct_keyboard_losses']==row['correct_any_losses']==1
            assert not any(row[k] for k in ('added','unrelated_changes','tempo_changes','survivor_changes'))
            assert len(row['protected_loss_details'])==1
            midi=ROOT/sample['midi']
            assert digest(midi)==sample['midi_sha256']
            notes=[n for n in read_intervals(midi.read_bytes()) if n['channel']!=9]
            for loss in row['protected_loss_details']:
                start=loss['end_sample']/sample['rate']
                related=[n for n in notes if n['midi']==loss['midi'] and n['start']-.15<start+.05 and n['end']+.3>start]
                key=coverage([(n['start'],n['key_end']) for n in related],start,start+.05)
                pedal=coverage([(n['start'],n['end']) for n in related],start,start+.05)
                allowed=coverage([(n['start'],n['end']+.3) for n in related],start,start+.05)
                assert key==loss['held_seconds']==0
                contexts.append(dict(sample=name,time=start,midi=loss['midi'],held_seconds=key,sounding_seconds=pedal,
                                     release_tolerance_seconds=max(0.,allowed-pedal),protected_notes=related))
    assert 'experimental_phase_low_keyboard' not in git('show','HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for target in ('test-multiscale-exposure','test-phase-low-keyboard','test-native-phase-low-keyboard'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    atomic_json(ROOT/'build/phase_low_keyboard_regression_context.json',dict(cases=contexts,decision='reject_under_unchanged_protection_gate'))
    print(json.dumps(contexts,indent=2),flush=True)
    print('Verified exposure explanation, native train/calibration parity and four protected-note regression failures; no new held-out access or promotion',flush=True)


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
    git('diff','--cached','--check')
    (ROOT/'build/phase_low_keyboard_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Diagnose short-window pitch leakage and reject phase trial on protected-note regressions'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
