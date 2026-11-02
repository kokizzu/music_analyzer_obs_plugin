#!/usr/bin/env python3
"""Verify the rejected native release trial and publish its reproducible code."""
import argparse
import ast
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest
from run_joint_grace_heldout import verify_phase

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'src/joint_grace_history.hpp', 'src/joint_grace_restore.hpp', 'src/experimental_joint_grace_hook.inc',
         'tests/joint_grace_history.cpp', 'tests/joint_grace_restore.cpp', 'tests/joint_grace_pair.cpp',
         'scripts/build_joint_grace_trial.py', 'scripts/measure_joint_grace.py',
         'scripts/run_joint_grace_heldout.py', 'scripts/checkpoint_native_joint_grace.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    build_path = ROOT / 'build/joint_grace_native/900451015dcecef6/build.json'
    build = read(build_path)
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert build['inputs']['script_sha256'] == digest(ROOT / 'scripts/build_joint_grace_trial.py')
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    assert digest(build_path.parent / 'src/analyzer.cpp') == build['cpp_sha256']
    assert digest(build_path.parent / 'src/analyzer.hpp') == build['hpp_sha256']
    assert build['observer_instrumentation']
    offline_path = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2/report.json'
    assert digest(offline_path) == build['inputs']['calibration_sha256']
    assert digest(ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json') == build['inputs']['dictionary_sha256']
    offline = read(offline_path)
    training, t = verify_phase('training', offline)
    calibration, c = verify_phase('calibration', offline)
    frozen_path = ROOT / 'build/joint_grace_heldout/frozen-eb001a122070725c.json'
    frozen = read(frozen_path)
    assert frozen['training'] == training and frozen['calibration'] == calibration
    assert frozen['build_sha256'] == digest(build_path)
    assert frozen['script_sha256'] == digest(ROOT / 'scripts/run_joint_grace_heldout.py')
    assert frozen['scorer_sha256'] == digest(ROOT / 'scripts/measure_low_keyboard_trial.py')
    paths = {'heldout-1': '9d3b0b4dfd7b5f02', 'heldout-2': '2eee0d007cb21b6a',
             'heldout-3': 'd6c9655dbcda4a03', 'heldout-4': '0e7eddd15058c021'}
    held_recovery, attack_loss = 0., 0
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = read(baseline_path)
    for name, key in paths.items():
        path = frozen_path.parent / name / key / 'report.json'
        report = read(path)
        assert report['complete'] and report['inputs']['frozen_sha256'] == digest(frozen_path)
        assert report['inputs']['build_sha256'] == digest(build_path)
        assert report['inputs']['driver_sha256'] == frozen['script_sha256']
        assert report['inputs']['script_sha256'] == frozen['scorer_sha256']
        assert report['inputs']['baseline_sha256'] == digest(baseline_path)
        assert digest(baseline_path.parent / (name + '.f32')) == baseline['recordings'][name]['prefix_sha256']
        row = report['recordings'][name]
        assert digest(path.parent / (name + '.tsv')) == row['sha256']
        assert not any(row['deltas'][k] for k in ('removed_cells', 'supported_removed_seconds', 'unsupported_added_seconds',
                       'unrelated_changed_frames', 'tempo_changed_frames', 'surviving_cell_changed_frames'))
        held_recovery += row['deltas']['held_added_seconds']
        attack_loss += row['before']['matched_attacks'] - row['after']['matched_attacks']
        assert row['maximum_after_ms'] < 50
    assert .105 < held_recovery < .106 and attack_loss == 1
    assert 'experimental_joint_grace' not in git('show', 'HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified native training/calibration capacity parity and held-out rejection: 105ms recovery, one lost display attack; primary analyzer unchanged', flush=True)


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
    for target in ('test-joint-grace-history', 'test-joint-grace-restore', 'test-keyboard-stage-trace', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    (ROOT / 'build/native_joint_grace_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Validate native release restoration and retain held-out attack regression'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
