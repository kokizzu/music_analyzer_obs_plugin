#!/usr/bin/env python3
"""Verify and publish the isolated low-note duration research checkpoint."""
import argparse
import ast
import csv
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest
from validate_low_keyboard_controls import inspect

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'tests/keyboard_stage_trace.hpp', 'tests/keyboard_stage_trace.cpp',
         'tests/keyboard_stage_trace_test.cpp', 'tests/test_keyboard_stage_trace.py',
         'scripts/trace_keyboard_stages.py', 'src/low_keyboard_fundamental_guard.inc',
         'tests/low_keyboard_fundamental.cpp', 'tests/low_keyboard_pair.cpp',
         'tests/note_grid_comparison.hpp', 'tests/note_grid_comparison.cpp',
         'scripts/measure_low_keyboard_trial.py', 'scripts/freeze_low_keyboard_parameters.py',
         'scripts/validate_low_keyboard_controls.py', 'scripts/audit_keyboard_grace.py',
         'scripts/evaluate_low_keyboard_coherence.py', 'scripts/build_keyboard_alias_trial.py',
         'scripts/test_keyboard_alias_visibility.py', 'tests/keyboard_alias_visibility_pair.cpp',
         'scripts/inspect_routing_replays.py', 'scripts/checkpoint_low_keyboard_evidence.py']


def read(path):
    return json.loads((ROOT / path).read_text())


def verify():
    identity()
    build_path = 'build/low_keyboard_trial/74626cea8617a3c7/build.json'
    build = read(build_path)
    assert build['regression_passed']
    assert digest((ROOT / build_path).parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    frozen_path = 'build/low_keyboard_measurement/frozen.json'
    assert read(frozen_path)['build_sha256'] == digest(ROOT / build_path)
    for key in ('fee0dc0e64085c38', '7f84fa46b6edbbf9', '7c9cd886327aae31'):
        directory = 'build/low_keyboard_measurement/' + key
        report = read(directory + '/report.json')
        assert report['complete'] and report['passed']
        assert report['inputs']['build_sha256'] == digest(ROOT / build_path)
        assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/measure_low_keyboard_trial.py')
        for name, row in report['recordings'].items():
            assert digest(ROOT / directory / (name + '.tsv')) == row['sha256']
            assert not any(row['deltas'][field] for field in (
                'held_removed_seconds', 'supported_removed_seconds', 'added_cells',
                'unrelated_changed_frames', 'tempo_changed_frames', 'surviving_cell_changed_frames'))
    directory = ROOT / 'build/low_keyboard_controls/268291bdcd67a2de'
    plan = json.loads((directory / 'plan.json').read_text())
    assert len(plan['cases']) == 1154
    assert plan['build_sha256'] == digest(ROOT / build_path)
    assert plan['frozen_sha256'] == digest(ROOT / frozen_path)
    assert plan['script_sha256'] == digest(ROOT / 'scripts/validate_low_keyboard_controls.py')
    assert plan['preparation_helper_sha256'] == digest(ROOT / 'scripts/validate_routing_consensus.py')
    total = 0
    for shard in range(4):
        report = json.loads((directory / ('report-' + str(shard) + '.json')).read_text())
        assert report['complete'] and report['passed']
        assert report['plan_sha256'] == digest(directory / 'plan.json')
        cases = plan['cases'][shard::4]
        assert set(report['recordings']) == {s['id'] for s in cases}
        for sample in cases:
            entry = report['recordings'][sample['id']]
            expected = None
            if 'reference' in sample:
                assert digest(ROOT / sample['reference']) == sample['reference_sha256']
                with (ROOT / sample['reference']).open() as stream:
                    expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
            actual = inspect(directory / (sample['id'] + '.tsv'), sample, entry['rate'], expected)
            assert all(actual[k] == entry[k] for k in actual)
            assert not any(entry[k] for k in ('correct_any_losses', 'correct_keyboard_losses', 'unrelated_changes', 'tempo_changes', 'added'))
            assert not entry['after_ms']['deadline_misses']
            total += entry['windows']
    coherence = read('build/low_keyboard_coherence/dc5f99cb5044a9d7/report.json')
    assert coherence['complete'] and coherence['inputs']['script_sha256'] == digest(ROOT / 'scripts/evaluate_low_keyboard_coherence.py')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified 1154 native preservation cases,', total, 'endpoints; frozen training/calibration/held-out reports; offline coherence evidence', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    verify()
    if not (args.publish or args.stage):
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    for target in ('test-note-grid-comparison', 'test-keyboard-stage-trace', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    git('diff', '--cached', '--check')
    print(git('diff', '--cached', '--stat'), flush=True)
    (ROOT / 'build/low_keyboard_staged.diff').write_text(git('diff', '--cached'))
    if args.stage:
        return
    # Explicit source allowlist excludes the dirty production analyzer and all fixtures.
    assert 'experimental_low_keyboard_direct_support' not in git('show', ':src/analyzer.hpp')
    print(git('commit', '-m', 'Trace low-note duration errors and validate isolated direct-support guard'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
