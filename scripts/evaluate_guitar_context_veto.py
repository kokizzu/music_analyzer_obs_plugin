#!/usr/bin/env python3
"""Check a conservative native-owner veto around the frozen duplicate model."""
import csv
import argparse
import hashlib
import json
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyboard-context', action='store_true')
    args = parser.parse_args()
    source = ROOT / 'build/routing_guitar_duplicate_model.json'
    model = json.loads(source.read_text())
    inputs = {str(source.relative_to(ROOT)): digest(source), str(Path(__file__).relative_to(ROOT)): digest(Path(__file__)),
              'scripts/evaluate_guitar_duplicate_model.py': digest(ROOT / 'scripts/evaluate_guitar_duplicate_model.py')}
    metrics = {}
    for report_path in (ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json',
                        ROOT / 'build/routing_controls/84b9eb144888ea8d/report.json',
                        ROOT / 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'):
        report = json.loads(report_path.read_text())
        assert report['complete']
        inputs[str(report_path.relative_to(ROOT))] = digest(report_path)
        selected = {row['id']: row for row in report['inputs'].get('selection', [])}
        annotations = {}
        for manifest, checksum in report['inputs'].get('manifests', {}).items():
            assert digest(ROOT / manifest) == checksum
            for line in (ROOT / manifest).read_text().splitlines():
                values = line.split('\t')
                if values[0] == 'NOTE':
                    annotations.setdefault(values[1], []).append((float(values[2]), float(values[3]), int(values[4])))
        for name, recording in report['recordings'].items():
            path = report_path.parent / (name + '.tsv')
            assert digest(path) == recording['sha256']
            inputs[str(path.relative_to(ROOT))] = digest(path)
            sample = selected.get(name)
            cohort = 'piano-' + recording['cohort'] if sample is None else ('guitar-poly-' if sample.get('protect_entire_guitar_row') else sample['family'] + '-') + sample['cohort']
            result = metrics.setdefault(cohort, dict(eligible=0, native_guitar_vetoes=0, wrong_piano_removed=0, correct_guitar_losses=0, protected_guitar_row_changes=0, annotated_guitar_losses=0, unverified_guitar_changes=0, unscored_control_changes=0))
            with path.open() as stream:
                for _, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    candidates = list(group)
                    veto = any((row['owner'] not in ('0', '2') if args.keyboard_context else row['owner'] == '1')
                               for row in candidates if int(row['midi']) >= 0)
                    for row in candidates:
                        if not eligible(row):
                            continue
                        result['eligible'] += 1
                        result['native_guitar_vetoes'] += int(veto)
                        remove = not veto and lower_probability(model['model'], features(row)) >= model['threshold']
                        if sample is None:
                            result['wrong_piano_removed'] += int(remove)
                        elif sample.get('protect_entire_guitar_row'):
                            result['protected_guitar_row_changes'] += int(remove)
                            time = int(row['end_sample']) / recording['rate']
                            assert name in annotations
                            supported = any(midi == int(row['midi']) and start - .15 <= time and end + .3 >= max(0., time - .1) for start, end, midi in annotations[name])
                            result['annotated_guitar_losses'] += int(remove and supported)
                            result['unverified_guitar_changes'] += int(remove and not supported)
                        elif sample['family'] == 'guitar' and int(row['midi']) == sample['midi']:
                            result['correct_guitar_losses'] += int(remove)
                        else:
                            result['unscored_control_changes'] += int(remove)
    passed = metrics['piano-heldout']['wrong_piano_removed'] > 0 and not any(row['correct_guitar_losses'] or row['protected_guitar_row_changes'] for row in metrics.values())
    report = dict(inputs=inputs, metrics=metrics, model_sha256=digest(source),
                  rule=('Require every native candidate to be Keyboard- or Bass-owned' if args.keyboard_context else
                        'Veto every suppression in a window containing any native Guitar-owned candidate, without corpus- or pitch-specific exceptions'),
                  decision='candidate_for_native_replay' if passed else 'reject')
    assert all(digest(ROOT / path) == checksum for path, checksum in inputs.items())
    destination = ROOT / 'build' / ('routing_guitar_keyboard_context.json' if args.keyboard_context else 'routing_guitar_context_veto.json')
    atomic_json(destination, report)
    print(json.dumps({key: value for key, value in report.items() if key != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
