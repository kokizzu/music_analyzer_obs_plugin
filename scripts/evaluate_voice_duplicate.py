#!/usr/bin/env python3
"""Evaluate frozen duplicate evidence on Voice, without fitting to test data."""
import csv
import json
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from routing_duration_baseline import ROOT, atomic_json, digest


def protected_voice(sample, midi):
    if sample['family'] != 'vocals':
        return False
    return sample['group'].startswith('VocalSet-') or midi == sample['midi']


def decisions(rows, model):
    context = frame_context(rows)
    removed = set()
    for row in rows:
        if row['midi'] not in row['voice'].split(','):
            continue
        probe = dict(row, guitar=row['midi'])
        if eligible(probe) and lower_probability(model['model'], features(row) + context) >= model['threshold']:
            removed.add(int(row['midi']))
    return removed


def main():
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(model_path.read_text())
    inputs = {str(model_path.relative_to(ROOT)): digest(model_path)}
    for name in ('evaluate_voice_duplicate.py', 'evaluate_guitar_duplicate_model.py', 'evaluate_guitar_music_model.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    metrics = {}
    recordings = {}
    for kind, relative in [('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'),
                           ('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
                           ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
                           ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json')]:
        path = ROOT / relative
        report = json.loads(path.read_text())
        assert report['complete']
        inputs[relative] = digest(path)
        selected = {sample['id']: sample for sample in report['inputs'].get('selection', [])}
        for name, entry in report['recordings'].items():
            sample = selected.get(name)
            cohort = kind + '-' + (sample['cohort'] if sample else entry['cohort'])
            metric = metrics.setdefault(cohort, dict(windows=0, removed=0, protected_voice_losses=0))
            capture = path.parent / (name + '.tsv')
            assert digest(capture) == entry['sha256']
            inputs[str(capture.relative_to(ROOT))] = digest(capture)
            changed = []
            with capture.open() as stream:
                for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    removed = decisions(list(frame), model)
                    metric['windows'] += 1
                    metric['removed'] += len(removed)
                    metric['protected_voice_losses'] += sum(protected_voice(sample, midi) for midi in removed) if sample and kind == 'single' else 0
                    changed.extend((int(endpoint), midi) for midi in sorted(removed))
            recordings[kind + '/' + name] = changed
    passed = metrics['piano-heldout']['removed'] > 0 and not any(value['protected_voice_losses'] for value in metrics.values())
    result = dict(inputs=inputs, metrics=metrics, recordings=recordings,
                  decision='candidate_for_native_replay' if passed else 'reject',
                  scope='Frozen Guitar classifier applied to Voice duplicates with unchanged physical eligibility; no refit or cutoff tuning. Same MIDI must remain in visible Keyboard. Every VocalSet Voice pitch and labelled NSynth Voice pitch is protected. Real mixed Voice sources and native replay required before runtime promotion.')
    assert all(digest(ROOT / name) == checksum for name, checksum in inputs.items())
    atomic_json(ROOT / 'build/voice_duplicate_evaluation.json', result)
    print(json.dumps(dict(metrics=metrics, decision=result['decision']), indent=2))


if __name__ == '__main__':
    main()
