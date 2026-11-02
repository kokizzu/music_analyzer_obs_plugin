#!/usr/bin/env python3
"""Verify and publish the continuous coverage and disjoint grace calibration."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import argparse
import ast
import hashlib
import json
import subprocess

import numpy as np

from calibrate_joint_grace import evaluate
from capture_joint_note_coverage import causal_windows
from joint_pitch_reference import spectrum, fit
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'scripts/capture_joint_note_coverage.py', 'scripts/screen_joint_note_coverage.py',
         'scripts/joint_grace_rules.py', 'scripts/calibrate_joint_grace.py',
         'scripts/checkpoint_joint_grace.py', 'tests/test_joint_note_coverage.py', 'tests/test_joint_grace_rules.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    capture_path = ROOT / 'build/joint_note_coverage/017a9ad67bd36e7d/report.json'
    capture = read(capture_path)
    assert capture['complete']
    assert capture['inputs']['script_sha256'] == digest(ROOT / 'scripts/capture_joint_note_coverage.py')
    assert capture['inputs']['helper_sha256'] == digest(ROOT / 'scripts/joint_pitch_reference.py')
    assert sum(r['frames'] * 88 for r in capture['recordings'].values()) == 316800
    for name, row in capture['recordings'].items():
        assert digest(capture_path.parent / (name + '.npz')) == row['sha256']
    screen = read(ROOT / 'build/joint_note_coverage_screen.json')
    assert len(screen['aggregate']) == 125
    assert all(digest(ROOT / p) == h for p, h in screen['inputs'].items())
    grace = read(ROOT / 'build/keyboard_grace_audit.json')
    assert all(digest(ROOT / p) == h for p, h in grace['inputs'].items())
    directory = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2'
    report = read(directory / 'report.json')
    assert report['complete'] and report['passed'] and read(directory / 'frozen-training.json') == report['inputs']
    assert all(digest(ROOT / p) == h for p, h in report['inputs']['scripts'].items())
    assert all(digest(ROOT / p) == h for p, h in report['artifacts'].items())
    assert report['inputs']['capture_sha256'] == digest(capture_path)
    assert report['inputs']['screen_sha256'] == digest(ROOT / 'build/joint_note_coverage_screen.json')
    assert report['inputs']['rule']['mode'] == 'grace-display'
    assert report['inputs']['rule']['relative_floor'] == .8 and report['inputs']['rule']['explained_floor'] == .3
    for key, parent in [('stage_build', 'keyboard_stage_trace'), ('tracking_build', 'primary_duration_trace')]:
        built = report[key]
        signature = hashlib.sha256(json.dumps(built['inputs'], sort_keys=True).encode()).hexdigest()[:16]
        assert digest(ROOT / 'build' / parent / signature / 'replay') == built['binary_sha256']
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = read(baseline_path)
    for name, expected in report['training'].items():
        arrays = np.load(capture_path.parent / (name + '.npz'))
        actual = evaluate(name, ROOT / 'build/keyboard_stage_trace/034803c68151329e' / (name + '.frames.tsv'),
                          ROOT / 'build/keyboard_stage_trace/034803c68151329e' / (name + '.trace.tsv'),
                          ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f' / (name + '.trace.tsv'),
                          arrays['activation'], arrays['projection'], baseline)
        assert actual == expected
    raw = baseline_path.parent / 'training-4.f32'
    assert digest(raw) == baseline['recordings']['training-4']['prefix_sha256']
    dictionary_path = ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    assert digest(dictionary_path) == report['inputs']['dictionary_sha256']
    dictionary = np.array(read(dictionary_path)['columns']).T
    observed = spectrum(causal_windows(np.fromfile(raw, dtype='<f4').astype(float), baseline['recordings']['training-4']['rate'])).T
    observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
    activation = fit(dictionary, observed)
    actual = evaluate('training-4', directory / 'frames.tsv', directory / 'stages.tsv', directory / 'tracking.tsv',
                      activation, dictionary.T @ observed, baseline)
    assert actual == report['calibration'] and actual['metrics']['unsupported_seconds'] == 0
    assert .084 < actual['metrics']['held_seconds'] < .085
    assert actual['after']['matched_attacks'] == actual['before']['matched_attacks']
    assert actual['after']['early_release_seconds'] < actual['before']['early_release_seconds']
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    assert 'joint_grace' not in git('show', 'HEAD:src/analyzer.hpp')
    print('Verified 316800 causal pitch estimates, 125 training screens, exact training-rule parity and disjoint release calibration; no runtime integration', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    verify()
    if not (args.stage or args.publish):
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    for target in ('test-joint-note-coverage', 'test-joint-grace-rules', 'test-joint-pitch', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    (ROOT / 'build/joint_grace_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Validate causal joint-pitch coverage and freeze release-grace calibration'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
