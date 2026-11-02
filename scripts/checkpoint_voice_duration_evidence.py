#!/usr/bin/env python3
"""Publish verified Voice experiments and causal duration evidence on primary."""
import argparse
import ast
import csv
import hashlib
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'src/experimental_piano_voice_hook.inc', 'tests/piano_voice_pair.cpp',
         'tests/primary_duration_trace.cpp', 'tests/primary_duration_trace.hpp',
         'scripts/build_piano_voice_trial.py', 'scripts/measure_piano_voice_trial.py',
         'scripts/validate_piano_voice_extensions.py', 'scripts/evaluate_voice_duplicate.py',
         'scripts/audit_voice_duration_candidates.py', 'scripts/audit_keyboard_recovery.py',
         'scripts/evaluate_keyboard_recovery.py', 'scripts/trace_primary_duration.py',
         'scripts/audit_keyboard_tracking_recovery.py', 'scripts/capture_routing_regression_evidence.py',
         'scripts/evaluate_routing_consensus.py', 'tests/test_voice_duration_candidates.py',
         'tests/test_keyboard_recovery.py', 'tests/test_routing_consensus.py',
         'scripts/checkpoint_voice_duration_evidence.py']


def verify():
    identity()
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    for relative in ('build/voice_duplicate_evaluation.json', 'build/keyboard_recovery_audit.json',
                     'build/keyboard_recovery_evaluation.json', 'build/keyboard_tracking_recovery_audit.json',
                     'build/routing_consensus_evaluation.json', 'build/voice_duration_candidate_audit.json'):
        report = json.loads((ROOT / relative).read_text())
        assert all(digest(ROOT / path) == checksum for path, checksum in report['inputs'].items()), relative
    build_path = ROOT / 'build/piano_voice_trial/6c412eed26b1221e/build.json'
    build = json.loads(build_path.read_text())
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert build['inputs']['script_sha256'] == digest(ROOT / 'scripts/build_piano_voice_trial.py')
    assert all(digest(ROOT / path) == checksum for path, checksum in build['inputs']['assets'].items())
    for suffix in ('cpp', 'hpp'):
        assert hashlib.sha256(git('show', 'HEAD:src/analyzer.' + suffix).encode()).hexdigest() == build['inputs']['primary_' + suffix + '_sha256']
        assert digest(build_path.parent / ('src/analyzer.' + suffix)) == build[suffix + '_sha256']
    report_paths = ['build/piano_voice_pair/79e637eb626694e5/report.json',
                    'build/piano_voice_pair/8ede7313ac105261/report.json',
                    'build/piano_voice_extensions/ebc264a1f5031e97/report.json']
    for relative in report_paths:
        report_path = ROOT / relative
        report = json.loads(report_path.read_text())
        assert report['complete'] and report['inputs']['build_sha256'] == digest(build_path)
        extended = 'extensions' in relative
        expected_loss = 1 if extended else 0
        assert report['passed'] == (not extended)
        script = 'scripts/validate_piano_voice_extensions.py' if extended else 'scripts/measure_piano_voice_trial.py'
        assert report['inputs']['script_sha256'] == digest(ROOT / script)
        losses = windows = 0
        for name, entry in report['recordings'].items():
            path = report_path.parent / (name + '.tsv')
            assert digest(path) == entry['sha256']
            count = removed = 0
            with path.open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    count += 1
                    assert row['any_lost'] == row['unrelated_difference'] == ''
                    assert row['bpm_changed'] == row['survivor_changed'] == '0'
                    before, after = ({int(v) for v in row[column].split(',') if v} for column in ('voice', 'after_voice'))
                    assert after <= before
                    removed += len(before - after)
            assert count == entry['windows'] and removed == entry['removed']
            assert not entry['after_ms']['deadline_misses']
            losses += entry['protected_voice_losses']
            windows += count
        assert losses == expected_loss
        print(relative, 'windows', windows, 'protected Voice changes', losses)
    directory = ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f'
    trace = json.loads((directory / 'report.json').read_text())
    assert trace['complete'] and trace['build']['inputs']['source_tree'] == git('rev-parse', 'HEAD:src').strip()
    assert trace['build']['inputs']['script_sha256'] == digest(ROOT / 'scripts/trace_primary_duration.py')
    assert digest(directory / 'replay') == trace['build']['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in trace['build']['inputs']['assets'].items())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    assert trace['baseline_sha256'] == digest(baseline_path)
    for name, entry in trace['recordings'].items():
        assert digest(directory / (name + '.trace.tsv')) == entry['trace_sha256']
        assert digest(directory / (name + '.frames.tsv')) == entry['frames_sha256']
        reference_path = baseline_path.parent / (name + '.tsv')
        assert digest(reference_path) == baseline['recordings'][name]['frames_sha256']
        with (directory / (name + '.frames.tsv')).open() as stream, reference_path.open() as reference:
            actual, expected = list(csv.DictReader(stream, delimiter='\t')), list(csv.DictReader(reference, delimiter='\t'))
        assert len(actual) == len(expected) == 1200
        assert all(all(row[k] == before[k] for k in row) for row, before in zip(actual, expected))
        missing = sum(value for key, value in entry['metrics'].items() if key.endswith('_missing_held_seconds'))
        assert abs(missing - baseline['recordings'][name]['duration']['keys']['missing_note_seconds']) < 1e-7
    print('Primary duration trace: exact output parity at 3600 training endpoints')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    verify()
    if not args.publish:
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip and not git('diff', '--cached', '--name-only').strip()
    for target in ('test-voice-duration-candidates', 'test-keyboard-recovery', 'test-routing-consensus',
                   'test-routing-duration-score', 'test-piano-guitar-verifier'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    git('diff', '--cached', '--check')
    print(git('diff', '--cached', '--stat'))
    print(git('diff', '--cached', '--', 'docs/routing_duration_goal.md', 'src/experimental_piano_voice_hook.inc'))
    print(git('commit', '-m', 'Validate Voice routing candidates and trace primary note-duration errors'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
