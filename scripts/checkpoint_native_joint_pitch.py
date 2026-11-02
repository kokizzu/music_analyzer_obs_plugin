#!/usr/bin/env python3
"""Verify native spectral numerical parity and publish the unused fitter."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import argparse
import ast
import json
import subprocess

import numpy as np
from capture_joint_note_coverage import causal_windows
from joint_pitch_reference import spectrum, fit
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md', 'src/joint_piano_fit.hpp',
         'tests/joint_piano_fit_replay.cpp', 'tests/joint_piano_fit_safety.cpp',
         'scripts/test_native_joint_pitch.py', 'scripts/checkpoint_native_joint_pitch.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    pointer = read(ROOT / 'build/native_joint_pitch/current.json')
    path = ROOT / pointer['report']
    report = read(path)
    assert digest(path) == pointer['sha256'] and report['complete'] and report['passed']
    assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/test_native_joint_pitch.py')
    assert all(digest(ROOT / p) == h for p, h in report['inputs']['assets'].items())
    assert digest(path.parent / 'replay') == report['binary_sha256']
    model = ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    assert digest(model) == report['inputs']['dictionary_sha256']
    dictionary = np.array(read(model)['columns'])
    capture_path = ROOT / 'build/joint_note_coverage/017a9ad67bd36e7d/report.json'
    captured = read(capture_path)
    total = 0
    assert len(report['recordings']) == 6
    for name, row in report['recordings'].items():
        output = path.parent / (name + '.f64')
        assert digest(output) == row['sha256']
        actual = np.fromfile(output, dtype='<f8').reshape(-1, 4, 88).transpose(1, 2, 0)
        if name.startswith('training-'):
            source = capture_path.parent / (name + '.npz')
            assert digest(source) == captured['recordings'][name]['sha256']
            arrays = np.load(source)
            activation, projection = arrays['activation'], arrays['projection']
        else:
            rate = int(name.split('-')[-1])
            raw = path.parent / (name + '.f32')
            assert digest(raw) == row['raw_sha256']
            observed = spectrum(causal_windows(np.fromfile(raw, dtype='<f4').astype(float), rate)).T
            observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
            activation = fit(dictionary.T, observed)
            projection = dictionary @ observed
        expected = np.stack((activation, projection, activation / np.maximum(activation.max(axis=0), 1e-12), activation / np.maximum(projection, 1e-12)))
        error = float(np.max(np.abs(actual - expected)))
        assert error == row['maximum_absolute_error'] and error < 1e-7
        assert not np.count_nonzero(((actual[2] >= .8) & (actual[3] >= .3)) != ((expected[2] >= .8) & (expected[3] >= .3)))
        assert actual.shape[-1] == row['frames']
        total += row['frames']
    assert total == 3660
    assert 'joint_piano_fit' not in git('show', 'HEAD:src/analyzer.hpp')
    assert 'joint_piano_fit' not in git('show', 'HEAD:src/analyzer.cpp')
    for p in PATHS:
        if p.endswith('.py'):
            ast.parse((ROOT / p).read_text())
    print('Verified all native/reference fields at 3660 endpoints, three rates, zero frozen-threshold mismatches; helper unused by production', flush=True)


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
    subprocess.run(['make', 'test-joint-piano-fit-safety'], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    result = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    (ROOT / 'build/native_joint_pitch_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Implement native joint piano spectral fitter with independent numerical parity'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
