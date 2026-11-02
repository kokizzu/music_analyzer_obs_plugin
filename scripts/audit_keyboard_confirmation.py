#!/usr/bin/env python3
"""Training-only audit of real raw Keyboard notes delayed by confirmation."""
import csv
import json
from itertools import groupby
from pathlib import Path

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge, score


def main():
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    trace_path = ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f/report.json'
    native_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    baseline, trace, native = (json.loads(p.read_text()) for p in (baseline_path, trace_path, native_path))
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (baseline_path, trace_path, native_path, Path(__file__))}
    recordings = {}
    for name in ('training-1', 'training-2', 'training-3'):
        sample = next(s for s in baseline['selection'] if s['id'] == name)
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        inputs[str(midi_path.relative_to(ROOT))] = digest(midi_path)
        notes = read_intervals(midi_path.read_bytes())
        held, allowed = {}, {}
        for note in notes:
            if note['channel'] == 9:
                continue
            held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
            allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held, allowed = ({m: merge(v) for m, v in d.items()} for d in (held, allowed))
        paths = [trace_path.parent / (name + '.trace.tsv'), native_path.parent / (name + '.tsv')]
        hashes = [trace['recordings'][name]['trace_sha256'], native['recordings'][name]['sha256']]
        for path, checksum in zip(paths, hashes):
            assert digest(path) == checksum
            inputs[str(path.relative_to(ROOT))] = checksum
        with paths[0].open() as stream:
            tracking = {(r['end_sample'], int(r['midi'])): r for r in csv.DictReader(stream, delimiter='\t')}
        frames, cases, metrics = [], [], {}
        variants = {rule: [] for rule in ('all-first-hit', 'strong-native')}
        rate = baseline['recordings'][name]['rate']
        with paths[1].open() as stream:
            for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r: r['end_sample']):
                rows = list(group)
                frame = rows[0]
                frames.append(frame)
                visible = {int(v) for v in frame['keys'].split(',') if v}
                added = {rule: set() for rule in variants}
                seen = set()
                for row in rows:
                    midi = int(row['midi'])
                    if midi < 0 or midi in seen or midi in visible:
                        continue
                    state = tracking[endpoint, midi]
                    if float(state['raw']) <= 0 or float(state['smoothed']) > 0 or state['confirmed'] != '0' or int(state['hits']) != 1 or int(state['misses']) != 0:
                        continue
                    seen.add(midi)
                    start, end = int(endpoint) / rate, min(60., int(endpoint) / rate + .05)
                    if end <= start:
                        continue
                    recovered = coverage(held.get(midi, []), start, end)
                    unsupported = max(0., end - start - coverage(allowed.get(midi, []), start, end))
                    strong = row['owner'] == '2' and row['profile'] == '0' and float(row['keyboard_score']) >= .9 and float(row['guitar_score']) <= .3 and float(row['vocal_score']) <= .1
                    case = dict(end_sample=int(endpoint), midi=midi, held_seconds=recovered, unsupported_seconds=unsupported,
                                strong_native=strong, candidate=row, tracking=state)
                    cases.append(case)
                    for rule, eligible in [('all-first-hit', True), ('strong-native', strong)]:
                        metric = metrics.setdefault(rule, dict(added=0, held_recovery_seconds=0., unsupported_added_seconds=0.))
                        if eligible:
                            metric['added'] += 1
                            metric['held_recovery_seconds'] += recovered
                            metric['unsupported_added_seconds'] += unsupported
                            added[rule].add(midi)
                for rule in variants:
                    variants[rule].append(dict(frame, keys=','.join(str(v) for v in sorted(visible | added[rule]))))
        original = score(frames, notes, rate)['keys']
        for rule, values in variants.items():
            result = score(values, notes, rate)['keys']
            metrics[rule].update(matched_attacks_before=original['matched_attacks'], matched_attacks_after=result['matched_attacks'],
                                 early_release_before=original['early_release_seconds'], early_release_after=result['early_release_seconds'])
        recordings[name] = dict(metrics=metrics, cases=cases)
    for helper in ('routing_duration_score.py', 'midi_sustain_reference.py', 'audit_keyboard_recovery.py'):
        inputs['scripts/' + helper] = digest(ROOT / 'scripts' / helper)
    assert all(digest(ROOT / p) == h for p, h in inputs.items())
    result = dict(inputs=inputs, recordings=recordings, scope='Training only; first raw hit, absent from final Keyboard, unconfirmed and unsmoothed. Hypothetical additions only; no native change, held-out use or promotion. Unsupported additions disqualify simple bypass rules.')
    atomic_json(ROOT / 'build/keyboard_confirmation_audit.json', result)
    print(json.dumps({name: r['metrics'] for name, r in recordings.items()}, indent=2), flush=True)


if __name__ == '__main__':
    main()
