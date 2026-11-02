#!/usr/bin/env python3
"""Fit a duration-specific verifier on recording-disjoint MIDI supervision."""
import csv
import json
import math
from collections import defaultdict
from itertools import groupby
from pathlib import Path

from audit_keyboard_recovery import coverage
from evaluate_guitar_duplicate_model import features, lower_probability
from evaluate_guitar_music_model import frame_context
from evaluate_next_detection import fit_forest
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def eligible(row):
    if int(row['midi']) < 0 or row['midi'] in row['keys'].split(',') or row['midi'] not in row['guitar'].split(','):
        return False
    scores = [float(row[key]) for key in ('keyboard_score', 'guitar_score', 'vocal_score')]
    return (row['mfcc_valid'] == '1' and row['profile'] == '0' and all(math.isfinite(v) for v in scores)
            and .5 <= scores[0] <= 1 and 0 <= scores[1] <= .3 and 0 <= scores[2] <= .1)


def main():
    import numpy as np
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    samples = {sample['id']: sample for sample in baseline['selection']}
    inputs = {str(baseline_path.relative_to(ROOT)): digest(baseline_path)}
    for name in ('evaluate_keyboard_recovery.py', 'audit_keyboard_recovery.py', 'evaluate_guitar_duplicate_model.py',
                 'evaluate_guitar_music_model.py', 'evaluate_next_detection.py', 'midi_sustain_reference.py', 'routing_duration_score.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    data = []
    configurations = [('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'),
                      ('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
                      ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
                      ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json')]
    for kind, relative in configurations:
        report_path = ROOT / relative
        report = json.loads(report_path.read_text())
        assert report['complete']
        inputs[relative] = digest(report_path)
        selected = {sample['id']: sample for sample in report['inputs'].get('selection', [])}
        for name, recording in report['recordings'].items():
            sample = selected.get(name)
            cohort = sample['cohort'] if sample else recording['cohort']
            if name == 'training-4' or sample and sample.get('group') == 'guitar_acoustic_021':
                cohort = 'calibration'
            if cohort == 'protected':
                cohort = 'calibration'  # Negative-only set; never a claimed holdout.
            held, allowed = defaultdict(list), defaultdict(list)
            if kind == 'piano':
                midi = ROOT / samples[name]['midi']
                assert digest(midi) == samples[name]['midi_sha256']
                inputs[str(midi.relative_to(ROOT))] = digest(midi)
                for note in read_intervals(midi.read_bytes()):
                    if note['channel'] != 9:
                        held[note['midi']].append((note['start'], note['key_end']))
                        allowed[note['midi']].append((note['start'], note['end'] + .3))
                held = {midi: merge(values) for midi, values in held.items()}
                allowed = {midi: merge(values) for midi, values in allowed.items()}
                rate = baseline['recordings'][name]['rate']
                horizon = baseline['recordings'][name]['duration']['audio_seconds']
            else:
                rate, horizon = recording['rate'], recording['windows'] * .05
            path = report_path.parent / (name + '.tsv')
            assert digest(path) == recording['sha256']
            inputs[str(path.relative_to(ROOT))] = digest(path)
            with path.open() as stream:
                for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    candidates = list(frame)
                    context = frame_context(candidates)
                    start, end = int(endpoint) / rate, min(horizon, int(endpoint) / rate + .05)
                    if end <= start:
                        continue
                    for row in candidates:
                        if not eligible(row):
                            continue
                        midi = int(row['midi'])
                        recovered = coverage(held.get(midi, []), start, end)
                        unsupported = end - start - coverage(allowed.get(midi, []), start, end)
                        data.append(dict(values=features(row) + context, cohort=kind + '-' + cohort,
                                         group=name, end_sample=int(endpoint), midi=midi,
                                         label=int(recovered < end - start - 1e-9),
                                         held_seconds=recovered, unsupported_seconds=unsupported))
    training = [row for row in data if row['cohort'].endswith('-training')]
    x, y = np.array([row['values'] for row in training]), np.array([row['label'] for row in training])
    assert (y == 0).sum() >= 8 and (y == 1).sum() >= 24
    predict, model = fit_forest(x, y, 2)
    negatives = [row for row in data if row['label'] == 1 and row['cohort'].endswith(('-training', '-calibration'))]
    threshold = max(.95, min(1., float(predict(np.array([row['values'] for row in negatives]))[:, 0].max()) + .01))
    metrics = {}
    for row in data:
        accepted = lower_probability(model, row['values']) >= threshold
        metric = metrics.setdefault(row['cohort'], dict(candidates=0, fully_held=0, added=0, held_recovery_seconds=0.,
                                                       unsupported_added_seconds=0., wrong_control_keys_added=0))
        metric['candidates'] += 1
        metric['fully_held'] += row['label'] == 0
        metric['added'] += accepted
        metric['held_recovery_seconds'] += row['held_seconds'] if accepted else 0
        metric['unsupported_added_seconds'] += row['unsupported_seconds'] if accepted else 0
        metric['wrong_control_keys_added'] += accepted and not row['cohort'].startswith('piano-')
    passed = metrics.get('piano-heldout', {}).get('held_recovery_seconds', 0) > 0 and not any(
        metric['wrong_control_keys_added'] or metric['unsupported_added_seconds'] > 1e-8 for metric in metrics.values())
    assert all(digest(ROOT / name) == checksum for name, checksum in inputs.items())
    result = dict(inputs=inputs, metrics=metrics, threshold=threshold, model=model, training_rows=len(training),
                  training_positive_rows=int((y == 0).sum()), negative_calibration_rows=sum(row['cohort'].endswith('-calibration') for row in negatives),
                  decision='candidate_for_native_replay' if passed else 'reject',
                  scope='Dedicated duration verifier; fit training groups only, cutoff training/calibration negatives only. Candidate must already be visible in Guitar and absent from Keyboard. Labels use the full causal next hop, MIDI key end and CC64 support plus 300ms grace. No native change or promotion.')
    atomic_json(ROOT / 'build/keyboard_recovery_evaluation.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs', 'model')}, indent=2))


if __name__ == '__main__':
    main()
