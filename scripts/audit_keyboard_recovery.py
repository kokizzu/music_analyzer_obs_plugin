#!/usr/bin/env python3
"""Training-only audit of strong native Keyboard candidates hidden in Guitar."""
import csv
import json
from collections import defaultdict
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import eligible
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import intersections, length, merge


def coverage(intervals, start, end):
    return length(intersections([(start, end)], intervals))


def main():
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    evidence_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    baseline, evidence = (json.loads(p.read_text()) for p in (baseline_path, evidence_path))
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (baseline_path, evidence_path, Path(__file__))}
    for name in ('routing_duration_score.py', 'midi_sustain_reference.py', 'evaluate_guitar_duplicate_model.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    metrics, candidates = {}, []
    for sample in baseline['selection']:
        if sample['cohort'] != 'training' or sample['id'] == 'training-4':
            continue
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        inputs[str(midi_path.relative_to(ROOT))] = digest(midi_path)
        held, allowed = defaultdict(list), defaultdict(list)
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel'] != 9:
                held[note['midi']].append((note['start'], note['key_end']))
                allowed[note['midi']].append((note['start'], note['end'] + .3))
        held = {midi: merge(values) for midi, values in held.items()}
        allowed = {midi: merge(values) for midi, values in allowed.items()}
        path = evidence_path.parent / (sample['id'] + '.tsv')
        assert digest(path) == evidence['recordings'][sample['id']]['sha256']
        inputs[str(path.relative_to(ROOT))] = digest(path)
        rate = baseline['recordings'][sample['id']]['rate']
        horizon = baseline['recordings'][sample['id']]['duration']['audio_seconds']
        previous_keys = set()
        metric = metrics[sample['id']] = dict(candidates=0, fully_held=0, fully_supported=0,
                                            held_seconds=0., unsupported_seconds=0., one_hop_candidates=0,
                                            owner_counts={})
        with path.open() as stream:
            for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                rows = list(frame)
                current = {int(v) for v in rows[0]['keys'].split(',') if v}
                start, end = int(endpoint) / rate, min(horizon, int(endpoint) / rate + .05)
                if end <= start:
                    continue
                for row in rows:
                    midi = int(row['midi'])
                    if midi < 0 or midi in current or not eligible(dict(row, keys=row['midi'])):
                        continue
                    key_overlap = coverage(held.get(midi, []), start, end)
                    support_overlap = coverage(allowed.get(midi, []), start, end)
                    metric['candidates'] += 1
                    metric['fully_held'] += key_overlap >= end - start - 1e-9
                    metric['fully_supported'] += support_overlap >= end - start - 1e-9
                    metric['held_seconds'] += key_overlap
                    metric['unsupported_seconds'] += end - start - support_overlap
                    metric['one_hop_candidates'] += midi in previous_keys
                    metric['owner_counts'][row['owner']] = metric['owner_counts'].get(row['owner'], 0) + 1
                    candidates.append(dict(recording=sample['id'], end_sample=int(endpoint), midi=midi,
                                           held_fraction=key_overlap / (end - start), support_fraction=support_overlap / (end - start),
                                           previous_keys=midi in previous_keys, candidate=row))
                previous_keys = current
    assert all(digest(ROOT / name) == checksum for name, checksum in inputs.items())
    atomic_json(ROOT / 'build/keyboard_recovery_audit.json', dict(inputs=inputs, metrics=metrics, candidates=candidates,
                scope='Training-1/2/3 only, no fit or native change. Current Guitar MIDI absent from Keyboard; exact native physical eligibility. MIDI coverage scored causally over next hop, no backdating.'))
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
