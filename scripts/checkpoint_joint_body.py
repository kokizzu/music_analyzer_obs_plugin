#!/usr/bin/env python3
"""Verify fresh stable-body evaluation and its complete preservation rejection."""
import argparse
import ast
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest
from validate_low_keyboard_controls import inspect

PATHS = ['make/routing_duration.mk', 'make/joint_body.mk', 'docs/routing_duration_goal.md',
         'src/joint_grace_body.hpp', 'tests/joint_grace_body.cpp', 'tests/joint_body_pair.cpp',
         'scripts/build_joint_body_trial.py', 'scripts/measure_joint_body.py', 'scripts/run_joint_body_fresh.py',
         'scripts/validate_joint_body_controls.py', 'scripts/audit_joint_body_context.py', 'scripts/checkpoint_joint_body.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    build_path = ROOT / 'build/joint_body_native/24cc08e20352e385/build.json'
    build = read(build_path)
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert digest(build_path.parent / 'src/analyzer.cpp') == build['cpp_sha256']
    assert digest(build_path.parent / 'src/analyzer.hpp') == build['hpp_sha256']
    assert build['inputs']['script_sha256'] == digest(ROOT / 'scripts/build_joint_body_trial.py')
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    frozen_path = ROOT / 'build/joint_body_fresh/frozen-3877a43a9e4e961d.json'
    frozen = read(frozen_path)
    assert frozen['build_sha256'] == digest(build_path)
    assert frozen['script_sha256'] == digest(ROOT / 'scripts/run_joint_body_fresh.py')
    assert frozen['scorer_sha256'] == digest(ROOT / 'scripts/routing_duration_score.py')
    assert frozen['midi_reader_sha256'] == digest(ROOT / 'scripts/midi_sustain_reference.py')
    for phase, pointer in frozen['phases'].items():
        path = ROOT / pointer['report']
        report = read(path)
        assert digest(path) == pointer['sha256'] and report['complete'] and report['passed']
        assert report['inputs']['driver_sha256'] == digest(ROOT / 'scripts/measure_joint_body.py')
        for name, row in report['recordings'].items():
            assert digest(path.parent / (name + '.tsv')) == row['sha256']
    fresh_gain = 0.
    for sample in frozen['selection']:
        directory = frozen_path.parent / frozen_path.stem / sample['id']
        report = read(directory / 'report.json')
        assert report['complete'] and report['passed'] and report['frozen_sha256'] == digest(frozen_path)
        assert all(digest(ROOT / p) == h for p, h in report['artifacts'].items())
        assert report['before']['matched_attacks'] == report['after']['matched_attacks']
        assert not any(report['deltas'][k] for k in ('removed', 'unrelated', 'tempo', 'survivor', 'unsupported_added'))
        fresh_gain += report['deltas']['held_added']
    assert abs(fresh_gain - .05) < 1e-7
    directory = ROOT / 'build/joint_body_controls/28eb805570ce51ef'
    plan = read(directory / 'plan.json')
    assert len(plan['cases']) == 1154 and plan['build_sha256'] == digest(build_path)
    assert plan['script_sha256'] == digest(ROOT / 'scripts/validate_joint_body_controls.py')
    assert all(digest(ROOT / p) == h for p, h in plan['helpers'].items())
    counts = dict(cases=0, windows=0, added=0, rejected_additions=0, affected_cases=0)
    for shard in range(4):
        report = read(directory / ('report-' + str(shard) + '.json'))
        assert report['complete'] and not report['passed'] and report['plan_sha256'] == digest(directory / 'plan.json')
        cases = plan['cases'][shard::4]
        assert set(report['recordings']) == {s['id'] for s in cases}
        for sample in cases:
            row = report['recordings'][sample['id']]
            path = directory / (sample['id'] + '.tsv')
            assert digest(path) == row['sha256']
            actual = inspect(path, sample, row['rate'])
            assert all(actual[k] == row[k] for k in actual)
            counts['cases'] += 1; counts['windows'] += row['windows']; counts['added'] += row['added']
            counts['rejected_additions'] += row['nonpiano_or_unscored_additions']
            counts['affected_cases'] += bool(row['nonpiano_or_unscored_additions'])
            assert not any(row[k] for k in ('removed', 'unrelated_changes', 'tempo_changes', 'survivor_changes', 'wrong_isolated_piano_pitches'))
            assert row['unsupported_piano_added_seconds'] == 0 and row['after_ms']['deadline_misses'] == 0
    assert counts == dict(cases=1154, windows=94834, added=69, rejected_additions=43, affected_cases=27)
    audit = read(ROOT / 'build/joint_context_audit/report.json')
    assert all(digest(ROOT / p) == h for p, h in audit['inputs'].items())
    assert all(not r['confirmed_context_times'] for r in audit['brass_counterexample'].values())
    assert 'experimental_joint_body' not in git('show', 'HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified stable-body train/calibration parity, 4 fresh recordings and 1154-case instrument rejection; no production promotion', flush=True)


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
    for target in ('test-joint-grace-body', 'test-joint-grace-history', 'test-joint-grace-restore', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    (ROOT / 'build/joint_body_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Evaluate attack-aware release trial on fresh piano and reject foreign-instrument additions'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
