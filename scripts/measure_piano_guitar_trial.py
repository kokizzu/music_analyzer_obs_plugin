#!/usr/bin/env python3
"""Verify actual native before/after engines, including offline/native parity."""
import argparse
import csv
import hashlib
import json
from itertools import groupby
from pathlib import Path
import subprocess

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from routing_duration_baseline import ROOT, atomic_json, digest


def midis(value):
    return {int(number) for number in value.split(',') if number}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(model_path.read_text())
    builds = []
    for path in (ROOT / 'build/piano_guitar_trial').glob('*/build.json'):
        build = json.loads(path.read_text())
        if all(digest(ROOT / p) == value for p, value in build['inputs']['assets'].items()):
            builds.append((path, build))
    assert len(builds) == 1, 'Need one matching completed native build'
    build_path, build = builds[0]
    binary = build_path.parent / 'pair'
    assert digest(binary) == build['binary_sha256']
    reports = ['build/routing_controls/84b9eb144888ea8d/report.json', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json',
               'build/routing_guitarset_controls/9801a45ca6c823e8/report.json'] if args.controls else ['build/routing_candidate_evidence/42e25eb544a48fc7/report.json']
    inputs = dict(model_sha256=digest(model_path), build_sha256=digest(build_path), script_sha256=digest(Path(__file__)),
                  helpers={p: digest(ROOT / p) for p in ('scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_guitar_music_model.py')},
                  controls=args.controls, reports={p: digest(ROOT / p) for p in reports})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/piano_guitar_pair' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    atomic_json(checkpoint, state)
    compare = ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums')
    for report_name in reports:
        path = ROOT / report_name
        report = json.loads(path.read_text())
        assert report['complete']
        samples = {sample['id']: sample for sample in report['inputs'].get('selection', [])}
        for name, recording in report['recordings'].items():
            sample = samples.get(name)
            if args.controls:
                raw = path.parent / (name + '.f32')
                rate = recording['rate']
                cohort = ('poly-' if sample.get('protect_entire_guitar_row') else sample['family'] + '-') + sample['cohort']
            else:
                baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
                baseline = json.loads(baseline_path.read_text())
                raw = baseline_path.parent / (name + '.f32')
                rate = baseline['recordings'][name]['rate']
                cohort = 'piano-' + recording['cohort']
            evidence_path = path.parent / (name + '.tsv')
            assert digest(evidence_path) == recording['sha256']
            expected, expected_removed = {}, {}
            with evidence_path.open() as stream:
                for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    candidates = list(frame)
                    expected[endpoint] = candidates[0]
                    context = frame_context(candidates)
                    expected_removed[endpoint] = {int(row['midi']) for row in candidates if eligible(row) and lower_probability(model['model'], features(row) + context) >= model['threshold']}
            sample_key = path.parent.parent.name + '-' + name
            destination = directory / (sample_key + '.tsv')
            if sample_key in state['recordings']:
                assert digest(destination) == state['recordings'][sample_key]['sha256']
            else:
                subprocess.run([str(binary), str(raw), str(rate), str(destination)], check=True, timeout=3600)
            with destination.open() as stream:
                frames = list(csv.DictReader(stream, delimiter='\t'))
            assert len(frames) == len(expected)
            removed_count = losses = protected_changes = 0
            after_times, before_times = [], []
            for row in frames:
                endpoint = row['end_sample']
                assert endpoint in expected and all(row[column] == expected[endpoint][column] for column in compare), 'Disabled candidate changed primary baseline'
                assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
                before, after = midis(row['guitar']), midis(row['after_guitar'])
                assert after <= before, 'Guitar suppression added a pitch'
                removed = before - after
                assert removed == expected_removed[endpoint], 'Native feature/inference differs from captured offline decision'
                removed_count += len(removed)
                if sample is not None:
                    if sample.get('protect_entire_guitar_row'):
                        protected_changes += len(removed)
                    elif sample['family'] == 'guitar':
                        losses += sample['midi'] in removed
                before_times.append(float(row['before_ms']))
                after_times.append(float(row['after_ms']))
            def timing(values):
                ordered = sorted(values)
                return dict(p50=ordered[(len(ordered) - 1) // 2], p99=ordered[int((len(ordered) - 1) * .99)], maximum=ordered[-1],
                            deadline_misses=sum(value > int(rate * .05 + .5) / rate * 1000 for value in values))
            result = dict(cohort=cohort, windows=len(frames), removed=removed_count, correct_guitar_losses=losses,
                          protected_guitar_row_changes=protected_changes, sha256=digest(destination),
                          before_ms=timing(before_times), after_ms=timing(after_times))
            state['recordings'][sample_key] = result
            atomic_json(checkpoint, state)
            print(name, json.dumps(result), flush=True)
    assert digest(binary) == build['binary_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = not any(row['correct_guitar_losses'] or row['protected_guitar_row_changes'] for row in state['recordings'].values())
    if not args.controls:
        state['passed'] &= any(row['cohort'] == 'piano-heldout' and row['removed'] for row in state['recordings'].values())
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), flush=True)
    assert state['passed'], 'Actual native paired acceptance gate failed'


if __name__ == '__main__':
    main()
