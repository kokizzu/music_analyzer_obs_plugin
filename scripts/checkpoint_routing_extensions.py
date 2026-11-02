#!/usr/bin/env python3
"""Verify and optionally publish broader negative evidence, without promotion."""
import argparse
import ast
import csv
import hashlib
import json
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['scripts/validate_piano_guitar_extensions.py', 'scripts/audit_voice_duration_candidates.py',
         'scripts/repair_routing_replay_checkpoints.py',
         'scripts/run_routing_extensions.py',
         'scripts/inspect_routing_replays.py', 'scripts/checkpoint_routing_extensions.py',
         'tests/test_voice_duration_candidates.py', 'make/routing_duration.mk', 'docs/routing_duration_goal.md']
REPORTS = ['a08d4ff7c59b86cc', '6c86dfbf33340870', '52c43eb944858288', '93a449f0b4f656bd']


def verify():
    identity()
    build_path = ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/build.json'
    build = json.loads(build_path.read_text())
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / path) == checksum for path, checksum in build['inputs']['assets'].items())
    for suffix in ('cpp', 'hpp'):
        assert hashlib.sha256(git('show', 'HEAD:src/analyzer.' + suffix).encode()).hexdigest() == build[suffix + '_sha256']
    total_losses = 0
    for key in REPORTS:
        directory = ROOT / 'build/piano_guitar_extensions' / key
        report = json.loads((directory / 'report.json').read_text())
        assert report['complete']
        assert report['inputs'] == json.loads((directory / 'plan.json').read_text())
        assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/validate_piano_guitar_extensions.py')
        assert report['inputs']['build_sha256'] == digest(build_path)
        assert len(report['recordings']) == len(report['inputs']['cases'])
        windows = losses = 0
        for sample in report['inputs']['cases']:
            entry = report['recordings'][sample['id']]
            path = directory / (sample['id'] + '.tsv')
            assert digest(path) == entry['sha256']
            assert digest(ROOT / sample['audio']) == sample['audio_sha256']
            hop = int(entry['rate'] * .05 + .5)
            count = removed = bad_count = 0
            with path.open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    count += 1
                    assert int(row['end_sample']) == count * hop
                    assert row['any_lost'] == row['unrelated_difference'] == ''
                    assert row['bpm_changed'] == row['survivor_changed'] == '0'
                    before, after = ({int(v) for v in row[name].split(',') if v} for name in ('guitar', 'after_guitar'))
                    assert after <= before
                    difference = before - after
                    removed += len(difference)
                    bad_count += len(difference if sample['kind'] == 'poly-guitar' else difference & {sample['midi']} if sample['kind'] == 'single-guitar' else set())
            assert (count, removed, bad_count) == (entry['windows'], entry['removed'], entry['correct_or_protected_losses'])
            windows += count
            losses += bad_count
        total_losses += losses
        assert report['passed'] == (losses == 0)
        print(report['inputs']['mode'], key, 'windows', windows, 'protected losses', losses)
    assert total_losses > 0, 'Expected documented reserved-performance rejection'
    audit_path = ROOT / 'build/voice_duration_candidate_audit.json'
    audit = json.loads(audit_path.read_text())
    assert all(digest(ROOT / path) == checksum for path, checksum in audit['inputs'].items())
    assert audit['decision'] == 'diagnostic_only_no_runtime_change'
    assert audit['totals']['piano']['unsupported_added_seconds'] > 0
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    verify()
    if not args.publish:
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert not git('diff', '--cached', '--name-only').strip(), 'Preserve staged work'
    for target in ('test-voice-duration-candidates', 'test-routing-duration-score', 'test-guitar-music-context', 'test-piano-guitar-verifier'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    git('diff', '--cached', '--check')
    print(git('diff', '--cached', '--stat'))
    print(git('diff', '--cached', '--', 'docs/routing_duration_goal.md', 'make/routing_duration.mk'))
    print(git('commit', '-m', 'Record broader routing regressions and duration candidate audit'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
