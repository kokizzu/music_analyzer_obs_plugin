#!/usr/bin/env python3
"""Publish the tested, rejected coherence experiment without changing production."""
import argparse
import ast
import csv
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest
from validate_low_keyboard_controls import inspect
from validate_low_keyboard_coherence import training_proof, phase_report

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md', 'src/low_keyboard_coherence.hpp',
         'tests/low_keyboard_coherence.cpp', 'tests/low_keyboard_coherence_history.cpp',
         'tests/low_keyboard_coherence_pair.cpp', 'tests/low_keyboard_coherence_latency.cpp',
         'scripts/build_keyboard_alias_trial.py', 'scripts/low_keyboard_coherence_trial.py',
         'scripts/measure_low_keyboard_coherence.py', 'scripts/validate_low_keyboard_coherence.py',
         'scripts/validate_low_keyboard_coherence_controls.py', 'scripts/benchmark_low_keyboard_coherence.py',
         'scripts/checkpoint_keyboard_coherence.py', 'scripts/audit_keyboard_confirmation.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    training_path, training = training_proof()
    calibration_path, calibration = phase_report('calibration')
    base = ROOT / 'build/low_keyboard_coherence_measurement'
    frozen = read(base / 'frozen.json')
    build_path = ROOT / frozen['build']
    build = read(build_path)
    assert digest(build_path) == frozen['build_sha256']
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    for path, checksum in build['inputs']['assets'].items():
        if path == 'tests/low_keyboard_coherence_pair.cpp':
            archived = build_path.parent / 'pair.cpp'
            assert digest(archived) == checksum
            # Only an extra empty line at EOF was removed after measurement.
            assert (ROOT / path).read_text() == archived.read_text().rstrip('\n') + '\n'
        else:
            assert digest(ROOT / path) == checksum
    assert frozen['training']['sha256'] == digest(training_path)
    assert frozen['calibration']['sha256'] == digest(calibration_path)
    assert frozen['driver_sha256'] == digest(ROOT / 'scripts/validate_low_keyboard_coherence.py')
    assert frozen['guard_sha256'] == digest(ROOT / 'src/low_keyboard_coherence.hpp')
    held_path = base / '54c758308a514c37/report.json'
    held = read(held_path)
    assert held['complete'] and not held['passed']
    assert held['inputs']['frozen_sha256'] == digest(base / 'frozen.json')
    assert held['inputs']['driver_sha256'] == frozen['driver_sha256']
    assert .0145 < held['recordings']['heldout-4']['deltas']['held_removed_seconds'] < .0147
    for name, row in held['recordings'].items():
        assert digest(held_path.parent / (name + '.tsv')) == row['sha256']
    directory = ROOT / 'build/low_keyboard_coherence_controls/4126b0a9fd9c84d1'
    plan = read(directory / 'plan.json')
    assert plan['build_sha256'] == digest(build_path) and plan['frozen_sha256'] == digest(base / 'frozen.json')
    assert plan['script_sha256'] == digest(ROOT / 'scripts/validate_low_keyboard_coherence_controls.py')
    assert all(digest(ROOT / p) == h for p, h in plan['helpers'].items())
    assert len(plan['cases']) == 1154
    windows = 0
    preservation_passed = True
    for shard in range(4):
        report = read(directory / ('report-' + str(shard) + '.json'))
        assert report['complete'] and report['plan_sha256'] == digest(directory / 'plan.json')
        cases = plan['cases'][shard::4]
        assert set(report['recordings']) == {s['id'] for s in cases}
        passed = True
        for sample in cases:
            row = report['recordings'][sample['id']]
            path = directory / (sample['id'] + '.tsv')
            expected = None
            if 'reference' in sample:
                assert digest(ROOT / sample['reference']) == sample['reference_sha256']
                with (ROOT / sample['reference']).open() as stream:
                    expected = {r['end_sample']: r for r in csv.DictReader(stream, delimiter='\t')}
            actual = inspect(path, sample, row['rate'], expected)
            assert all(row[k] == actual[k] for k in actual)
            with path.open() as stream:
                assert sum(r['survivor_changed'] != '0' for r in csv.DictReader(stream, delimiter='\t')) == row['survivor_changes']
            passed &= not any(row[k] for k in ('correct_any_losses', 'correct_keyboard_losses', 'survivor_changes', 'unrelated_changes', 'tempo_changes', 'added')) and not row['after_ms']['deadline_misses']
            windows += row['windows']
        assert passed == report['passed']
        preservation_passed &= passed
    latency_path = ROOT / 'build/low_keyboard_coherence_latency/b1071b59a4aec0fe/report.json'
    latency = read(latency_path)
    assert latency['complete'] and not latency['passed']
    assert latency['inputs']['build_sha256'] == digest(build_path)
    assert latency['inputs']['source_sha256'] == digest(latency_path.parent / 'replay.cpp')
    assert (ROOT / 'tests/low_keyboard_coherence_latency.cpp').read_text() == (latency_path.parent / 'replay.cpp').read_text().rstrip('\n') + '\n'
    assert latency['inputs']['script_sha256'] == digest(ROOT / 'scripts/benchmark_low_keyboard_coherence.py')
    assert latency['metrics']['p99_added_cpu_ms'] > latency['inputs']['gates']['p99_added_cpu_ms'] == 2
    for index, entry in enumerate(latency['repetitions']):
        assert digest(latency_path.parent / ('pass-' + str(index) + '.tsv')) == entry['sha256']
    assert 'experimental_low_keyboard_coherence' not in git('show', 'HEAD:src/analyzer.hpp')
    audit = read(ROOT / 'build/keyboard_confirmation_audit.json')
    assert set(audit['recordings']) == {'training-1', 'training-2', 'training-3'}
    assert all(digest(ROOT / p) == h for p, h in audit['inputs'].items())
    assert all(r['metrics']['all-first-hit']['unsupported_added_seconds'] > 0 for r in audit['recordings'].values())
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified rejected native experiment: held-note loss and p99 CPU failure; controls', windows, 'windows, passed', preservation_passed, flush=True)


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
    for target in ('test-low-keyboard-coherence', 'test-low-keyboard-coherence-history', 'test-note-grid-comparison', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    (ROOT / 'build/keyboard_coherence_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Implement and reject causal low-note coherence trial after held-out evaluation'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
