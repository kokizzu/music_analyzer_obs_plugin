#!/usr/bin/env python3
"""Replay primary Voice candidate and verify offline parity and protected notes."""
import argparse
import csv
import fcntl
import hashlib
import json
from itertools import groupby
from pathlib import Path
import subprocess

from evaluate_voice_duplicate import decisions, protected_voice
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    builds = [(p, json.loads(p.read_text())) for p in (ROOT / 'build/piano_voice_trial').glob('*/build.json')]
    builds = [(p, b) for p, b in builds if all(digest(ROOT / a) == h for a, h in b['inputs']['assets'].items())]
    assert len(builds) == 1
    build_path, build = builds[0]
    binary = build_path.parent / 'pair'
    assert digest(binary) == build['binary_sha256']
    sources = ['build/routing_controls/84b9eb144888ea8d/report.json', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json',
               'build/routing_guitarset_controls/9801a45ca6c823e8/report.json'] if args.controls else ['build/routing_candidate_evidence/42e25eb544a48fc7/report.json']
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(model_path.read_text())
    inputs = dict(build_sha256=digest(build_path), model_sha256=digest(model_path), controls=args.controls,
                  script_sha256=digest(Path(__file__)), sources={p: digest(ROOT / p) for p in sources},
                  helpers={p: digest(ROOT / p) for p in ('scripts/evaluate_voice_duplicate.py',
                           'scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_guitar_music_model.py')})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/piano_voice_pair' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'replay.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        replay(args, inputs, sources, model, binary, directory)


def replay(args, inputs, sources, model, binary, directory):
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    for source in sources:
        path = ROOT / source
        report = json.loads(path.read_text())
        assert report['complete']
        selected = {sample['id']: sample for sample in report['inputs'].get('selection', [])}
        for name, entry in report['recordings'].items():
            sample = selected.get(name)
            capture = path.parent / (name + '.tsv')
            assert digest(capture) == entry['sha256']
            expected, removals = {}, {}
            with capture.open() as stream:
                for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    rows = list(frame)
                    expected[endpoint], removals[endpoint] = rows[0], decisions(rows, model)
            if args.controls:
                raw, rate = path.parent / (name + '.f32'), entry['rate']
            else:
                base = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267'
                baseline = json.loads((base / 'report.json').read_text())
                raw, rate = base / (name + '.f32'), baseline['recordings'][name]['rate']
            sample_key = path.parent.parent.name + '-' + name
            destination = directory / (sample_key + '.tsv')
            if sample_key in state['recordings']:
                assert digest(destination) == state['recordings'][sample_key]['sha256']
            else:
                temporary = destination.with_suffix('.pending.tsv')
                subprocess.run([str(binary), str(raw), str(rate), str(temporary)], check=True, timeout=3600)
                temporary.replace(destination)
            removed_count = losses = count = 0
            before_times, after_times = [], []
            hop = int(rate * .05 + .5)
            with destination.open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    count += 1
                    endpoint = row['end_sample']
                    assert int(endpoint) == count * hop
                    assert all(row[column] == expected[endpoint][column] for column in ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
                    assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
                    before, after = ({int(v) for v in row[column].split(',') if v} for column in ('voice', 'after_voice'))
                    assert after <= before and before - after == removals[endpoint]
                    removed_count += len(before - after)
                    losses += sum(protected_voice(sample, midi) for midi in before - after) if sample and 'family' in sample else 0
                    before_times.append(float(row['before_ms']))
                    after_times.append(float(row['after_ms']))
            assert count == len(expected)
            def timing(values):
                ordered = sorted(values)
                return dict(p50=ordered[(len(ordered) - 1) // 2], p99=ordered[int((len(ordered) - 1) * .99)],
                            maximum=ordered[-1], deadline_misses=sum(value > hop / rate * 1000 for value in values))
            state['recordings'][sample_key] = dict(windows=count, removed=removed_count, protected_voice_losses=losses,
                before_ms=timing(before_times), after_ms=timing(after_times), sha256=digest(destination), raw_sha256=digest(raw))
            atomic_json(checkpoint, state)
            print(name, 'removed', removed_count, 'protected losses', losses, flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = not any(row['protected_voice_losses'] or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
    if not args.controls:
        state['passed'] &= any('heldout' in name and row['removed'] for name, row in state['recordings'].items())
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed']


if __name__ == '__main__':
    main()
