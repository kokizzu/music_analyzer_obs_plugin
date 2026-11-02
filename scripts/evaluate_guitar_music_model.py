#!/usr/bin/env python3
"""Train a context-aware duplicate verifier with actual chordal performances."""
import csv
import json
from itertools import groupby
from pathlib import Path

from evaluate_next_detection import fit_forest
from evaluate_guitar_duplicate_model import FEATURES as BASE_FEATURES, eligible, features, lower_probability
from routing_duration_baseline import ROOT, atomic_json, digest

CONTEXT = ['context_owner_' + str(i) for i in range(6)] + ['context_profile', 'context_population', 'context_pitch_span']


def frame_context(candidates):
    real = [row for row in candidates if int(row['midi']) >= 0]
    count = len(real)
    if not count:
        return [0.] * 9
    owners = [sum(int(row['owner']) == owner for row in real) / count for owner in range(6)]
    pitches = [int(row['midi']) for row in real]
    return owners + [sum(row['profile'] == '1' for row in real) / count, min(count / 64, 1.), (max(pitches) - min(pitches)) / 127]


def main():
    import numpy as np
    configurations = [('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'),
                      ('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
                      ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
                      ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json')]
    data, inputs = [], {str(Path(__file__).relative_to(ROOT)): digest(Path(__file__))}
    for name in ('scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_next_detection.py'):
        inputs[name] = digest(ROOT / name)
    for kind, relative in configurations:
        source = ROOT / relative
        capture = json.loads(source.read_text())
        assert capture['complete']
        inputs[relative] = digest(source)
        samples = {row['id']: row for row in capture['inputs'].get('selection', [])}
        for name, recording in capture['recordings'].items():
            sample = samples.get(name)
            path = source.parent / (name + '.tsv')
            assert digest(path) == recording['sha256']
            inputs[str(path.relative_to(ROOT))] = digest(path)
            if kind == 'piano':
                cohort = 'calibration' if name == 'training-4' else recording['cohort']
                label = 0
                group = name
            else:
                cohort, group = sample['cohort'], sample['group']
                if group == 'guitar_acoustic_021':
                    cohort = 'calibration'
                label = 1 if kind in ('poly', 'music') else None
            with path.open() as stream:
                for _, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    candidates = list(frame)
                    context = frame_context(candidates)
                    for row in candidates:
                        if not eligible(row):
                            continue
                        correct = kind == 'single' and sample['family'] == 'guitar' and int(row['midi']) == sample['midi']
                        target = 1 if correct else label
                        data.append(dict(values=features(row) + context, cohort=kind + '-' + cohort, group=group,
                                         label=target, conservatively_protected=kind in ('poly', 'music')))
    training = [row for row in data if row['cohort'].endswith('-training') and row['label'] is not None]
    x = np.array([row['values'] for row in training])
    y = np.array([row['label'] for row in training])
    assert (y == 0).sum() > 100 and (y == 1).sum() > 100
    predict, model = fit_forest(x, y, 2)
    calibration = [row for row in data if row['cohort'].endswith('-calibration') and row['label'] == 1]
    assert any(row['group'] == 'GuitarSet-02' for row in calibration), 'Need musical negative calibration'
    negative = [row for row in training if row['label'] == 1] + calibration
    threshold = max(.9, min(1., float(predict(np.array([row['values'] for row in negative]))[:, 0].max()) + .01))
    metrics = {}
    for row in data:
        remove = lower_probability(model, row['values']) >= threshold
        metric = metrics.setdefault(row['cohort'], dict(eligible=0, wrong_piano_removed=0, correct_guitar_losses=0,
                                                       protected_guitar_row_changes=0, unscored_control_changes=0))
        metric['eligible'] += 1
        metric['wrong_piano_removed'] += int(remove and row['label'] == 0)
        metric['correct_guitar_losses'] += int(remove and row['label'] == 1 and not row['conservatively_protected'])
        metric['protected_guitar_row_changes'] += int(remove and row['conservatively_protected'])
        metric['unscored_control_changes'] += int(remove and row['label'] is None)
    passed = metrics['piano-heldout']['wrong_piano_removed'] > 0 and not any(
        row['correct_guitar_losses'] or row['protected_guitar_row_changes'] for row in metrics.values())
    report = dict(inputs=inputs, features=BASE_FEATURES + CONTEXT, transformed_native_features=29,
                  model=model, threshold=threshold, boundary_uncertainty=1e-10, metrics=metrics,
                  training_rows=len(training), negative_calibration_rows=len(calibration), numpy_version=np.__version__,
                  decision='candidate_for_native_replay' if passed else 'reject',
                  scope='Model/cutoff fit only on designated training/calibration groups; performer 05 heldout; all polyphonic Guitar-row changes conservatively rejected; no runtime promotion from this offline screen')
    assert all(digest(ROOT / p) == checksum for p, checksum in inputs.items())
    destination = ROOT / 'build/routing_guitar_music_model.json'
    atomic_json(destination, report)
    print(json.dumps({key: value for key, value in report.items() if key not in ('inputs', 'model', 'features')}, indent=2))


if __name__ == '__main__':
    main()
