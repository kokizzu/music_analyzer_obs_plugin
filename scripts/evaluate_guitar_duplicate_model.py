#!/usr/bin/env python3
"""Freeze a native Guitar-duplicate candidate using training/calibration only."""
import csv
import hashlib
import json
import math
from pathlib import Path

from evaluate_next_detection import fit_forest
from routing_duration_baseline import ROOT, atomic_json, digest

NATIVE = ['ownership', 'onset', 'decay', 'pitch_stability', 'simultaneous_onset',
          'bass_score', 'keyboard_score', 'guitar_score', 'vocal_score', 'other_score',
          'level', 'pitch', 'periodicity', 'harmonicity', 'fit', 'centroid', 'slope', 'noise',
          'lower_octave', 'product', 'subharmonic', 'adjacent_lower', 'adjacent_upper', 'third_octave']
FEATURES = NATIVE + ['partial' + str(i) for i in range(5)] + ['mfcc' + str(i) for i in range(24)]


def eligible(row):
    values = [float(row[name]) for name in ('keyboard_score', 'guitar_score', 'vocal_score')]
    return (row['midi'] in row['guitar'].split(',') and row['midi'] in row['keys'].split(',') and
            row['mfcc_valid'] == '1' and row['profile'] == '0' and all(math.isfinite(value) for value in values) and
            .9 <= values[0] <= 1 and 0 <= values[1] <= .05 and 0 <= values[2] <= .05)


def features(row):
    raw = [float(row[name]) for name in FEATURES]
    assert all(math.isfinite(value) for value in raw)
    return [math.copysign(math.log1p(abs(value)), value) if i < 29 else value for i, value in enumerate(raw)]


def tree_lower_probability(tree, values):
    if isinstance(tree, list):
        return tree[0]
    value = values[tree['feature']]
    epsilon = (1 + abs(value)) * 1e-10
    if value + epsilon <= tree['threshold']:
        return tree_lower_probability(tree['left'], values)
    if value - epsilon > tree['threshold']:
        return tree_lower_probability(tree['right'], values)
    return min(tree_lower_probability(tree['left'], values), tree_lower_probability(tree['right'], values))


def lower_probability(model, values):
    return sum(tree_lower_probability(tree, values) for tree in model['trees']) / len(model['trees'])


def main():
    import numpy as np
    piano_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    controls_path = ROOT / 'build/routing_controls/84b9eb144888ea8d/report.json'
    poly_path = ROOT / 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'
    piano, controls = (json.loads(path.read_text()) for path in (piano_path, controls_path))
    assert piano['complete'] and controls['complete']
    assert piano['inputs']['build'] == controls['inputs']['build']
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (piano_path, controls_path, Path(__file__), ROOT / 'scripts/evaluate_next_detection.py')}
    poly = json.loads(poly_path.read_text())
    assert poly['complete'] and poly['inputs']['exporter_sha256'] == controls['inputs']['exporter_sha256']
    inputs[str(poly_path.relative_to(ROOT))] = digest(poly_path)
    data = []
    for name, recording in piano['recordings'].items():
        path = piano_path.parent / (name + '.tsv')
        assert digest(path) == recording['sha256']
        inputs[str(path.relative_to(ROOT))] = recording['sha256']
        with path.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                if eligible(row):
                    group = name
                    cohort = 'calibration' if name == 'training-4' else recording['cohort']
                    data.append(dict(raw=row, group=group, cohort='piano-' + cohort, label=0))
    selected = {row['id']: row for row in controls['inputs']['selection']}
    for name, recording in controls['recordings'].items():
        sample = selected[name]
        path = controls_path.parent / (name + '.tsv')
        assert digest(path) == recording['sha256']
        inputs[str(path.relative_to(ROOT))] = recording['sha256']
        with path.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                if not eligible(row):
                    continue
                cohort = 'calibration' if sample['group'] == 'guitar_acoustic_021' else sample['cohort']
                correct = sample['family'] == 'guitar' and int(row['midi']) == sample['midi']
                data.append(dict(raw=row, group=sample['group'], cohort=sample['family'] + '-' + cohort,
                                 label=1 if correct else None))
    selected_poly = {row['id']: row for row in poly['inputs']['selection']}
    for name, recording in poly['recordings'].items():
        sample = selected_poly[name]
        path = poly_path.parent / (name + '.tsv')
        assert digest(path) == recording['sha256']
        inputs[str(path.relative_to(ROOT))] = recording['sha256']
        with path.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                if eligible(row):
                    data.append(dict(raw=row, group=sample['group'], cohort='guitar-poly-' + sample['cohort'], label=1))
    training = [row for row in data if row['cohort'].endswith('-training') and row['label'] is not None]
    x = np.array([features(row['raw']) for row in training])
    y = np.array([row['label'] for row in training])
    assert (y == 0).sum() > 100 and (y == 1).sum() > 100
    predict, model = fit_forest(x, y, 2)
    # Hold back an entire Guitar identity for cutoff calibration, not adjacent
    # windows from a fitting clip. Held-out recordings never determine cutoff.
    calibration = [row for row in data if row['cohort'].endswith('-calibration') and row['label'] == 1]
    assert len(calibration) >= 10
    negative = [row for row in training if row['label'] == 1] + calibration
    wrong_probability = predict(np.array([features(row['raw']) for row in negative]))[:, 0]
    threshold = max(.9, min(1., float(wrong_probability.max()) + .01))
    metrics = {}
    for row in data:
        probability = lower_probability(model, features(row['raw']))
        metric = metrics.setdefault(row['cohort'], dict(eligible=0, removed=0, wrong_piano_removed=0, correct_guitar_losses=0, protected_guitar_row_changes=0, unscored_control_changes=0))
        remove = probability >= threshold
        metric['eligible'] += 1
        metric['removed'] += int(remove)
        metric['wrong_piano_removed'] += int(remove and row['label'] == 0)
        metric['correct_guitar_losses'] += int(remove and row['label'] == 1 and not row['cohort'].startswith('guitar-poly-'))
        metric['protected_guitar_row_changes'] += int(remove and row['label'] == 1 and row['cohort'].startswith('guitar-poly-'))
        metric['unscored_control_changes'] += int(remove and row['label'] is None)
    passed = metrics.get('piano-heldout', {}).get('wrong_piano_removed', 0) > 0 and not any(row['correct_guitar_losses'] or row['protected_guitar_row_changes'] for row in metrics.values())
    report = dict(inputs=inputs, model=model, features=FEATURES, transformed_native_features=29,
                  threshold=threshold, training_rows=len(training), negative_calibration_rows=len(calibration),
                  boundary_uncertainty=1e-10,
                  numpy_version=np.__version__, metrics=metrics,
                  decision='candidate_for_native_replay' if passed else 'reject',
                  scope='Guitar display duplicates only; same pitch must remain visible in Keyboard; no Voice changes; model/cutoff fit before held-out evaluation; no promotion without actual native paired replay and broader controls')
    assert all(digest(ROOT / p) == value for p, value in inputs.items())
    destination = ROOT / 'build/routing_guitar_duplicate_model.json'
    atomic_json(destination, report)
    print(json.dumps({key: value for key, value in report.items() if key not in ('model', 'features', 'inputs')}, indent=2))


if __name__ == '__main__':
    main()
