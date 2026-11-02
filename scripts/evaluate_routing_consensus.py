#!/usr/bin/env python3
"""Screen three-hop corroboration of frozen current-window duplicate decisions."""
import csv
import json
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from evaluate_voice_duplicate import decisions, protected_voice
from routing_duration_baseline import ROOT, atomic_json, digest

REQUIRED_HOPS = 3  # 100ms window / 50ms hop: first and third windows do not overlap.


def confirmed(predicted, previous):
    hits = {midi: min(previous.get(midi, 0) + 1, REQUIRED_HOPS) for midi in predicted}
    return {midi for midi, count in hits.items() if count == REQUIRED_HOPS}, hits


def main():
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(model_path.read_text())
    inputs = {str(model_path.relative_to(ROOT)): digest(model_path)}
    for name in ('evaluate_routing_consensus.py', 'evaluate_voice_duplicate.py', 'evaluate_guitar_duplicate_model.py', 'evaluate_guitar_music_model.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    metrics = {}
    reports = [('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'),
               ('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
               ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
               ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json'),
               ('regression', 'build/routing_regression_evidence/report.json')]
    for kind, relative in reports:
        path = ROOT / relative
        report = json.loads(path.read_text())
        assert kind == 'regression' or report['complete']
        inputs[relative] = digest(path)
        samples = {sample['id']: sample for sample in report.get('inputs', {}).get('selection', [])}
        for name, entry in report['recordings'].items():
            sample = samples.get(name)
            cohort = kind + '-' + (sample['cohort'] if sample else entry.get('cohort', 'regression'))
            metric = metrics.setdefault(cohort, dict(guitar_removed=0, voice_removed=0, protected_guitar_changes=0, protected_voice_changes=0))
            capture = path.parent / (name + '.tsv')
            assert digest(capture) == entry['sha256']
            inputs[str(capture.relative_to(ROOT))] = digest(capture)
            guitar_hits, voice_hits = {}, {}
            with capture.open() as stream:
                for _, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    rows = list(frame)
                    context = frame_context(rows)
                    guitar_predicted = {int(row['midi']) for row in rows if eligible(row) and lower_probability(model['model'], features(row) + context) >= model['threshold']}
                    voice_predicted = decisions(rows, model)
                    guitar, guitar_hits = confirmed(guitar_predicted, guitar_hits)
                    voice, voice_hits = confirmed(voice_predicted, voice_hits)
                    metric['guitar_removed'] += len(guitar)
                    metric['voice_removed'] += len(voice)
                    if kind in ('poly', 'music') or kind == 'regression' and name.startswith(('03_', '04_')):
                        metric['protected_guitar_changes'] += len(guitar)
                    elif kind == 'single' and sample['family'] == 'guitar':
                        metric['protected_guitar_changes'] += sample['midi'] in guitar
                    if kind == 'single':
                        metric['protected_voice_changes'] += sum(protected_voice(sample, midi) for midi in voice)
                    elif kind == 'regression' and name.startswith('vocalset_'):
                        metric['protected_voice_changes'] += len(voice)
    passed = (metrics['piano-heldout']['guitar_removed'] > 0 and metrics['piano-heldout']['voice_removed'] > 0
              and not any(row['protected_guitar_changes'] or row['protected_voice_changes'] for row in metrics.values()))
    assert all(digest(ROOT / name) == checksum for name, checksum in inputs.items())
    result = dict(inputs=inputs, required_hops=REQUIRED_HOPS, metrics=metrics,
                  decision='candidate_for_native_replay' if passed else 'reject',
                  scope='Fixed forest/cutoff; three consecutive same-MIDI eligible duplicate predictions, reset on any missing prediction and between recordings. Known reserved/48k failures are regression data after observation, not fresh holdout. Native replay and fresh recording-disjoint controls required before promotion.')
    atomic_json(ROOT / 'build/routing_consensus_evaluation.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
