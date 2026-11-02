#!/usr/bin/env python3
"""Training-only screen of one-hop grace for stable Keyboard notes erased as Other."""
import csv
import json
from itertools import groupby
from pathlib import Path

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge
from trace_keyboard_stages import attribute


def main():
    trace_directory = ROOT / 'build/keyboard_stage_trace/1303f17aa27cf9c8'
    track_directory = ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f'
    candidates_directory = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7'
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    trace, tracking, candidates, baseline = (json.loads(path.read_text()) for path in
        (trace_directory / 'report.json', track_directory / 'report.json', candidates_directory / 'report.json', baseline_path))
    assert trace['complete'] and tracking['complete'] and candidates['complete']
    inputs = {str(path.relative_to(ROOT)): digest(path) for path in
        (trace_directory / 'report.json', track_directory / 'report.json', candidates_directory / 'report.json', baseline_path, Path(__file__))}
    for name in ('trace_keyboard_stages.py', 'routing_duration_score.py', 'midi_sustain_reference.py', 'audit_keyboard_recovery.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    metrics = {}
    additions = {}
    for name in trace['recordings']:
        sample = next(sample for sample in baseline['selection'] if sample['id'] == name)
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        inputs[str(midi_path.relative_to(ROOT))] = digest(midi_path)
        held, allowed = {}, {}
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel'] != 9:
                held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
                allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held, allowed = ({midi: merge(values) for midi, values in mapping.items()} for mapping in (held, allowed))
        paths = [trace_directory / (name + '.trace.tsv'), trace_directory / (name + '.frames.tsv'),
                 track_directory / (name + '.trace.tsv'), candidates_directory / (name + '.tsv')]
        checksums = [trace['recordings'][name]['trace_sha256'], trace['recordings'][name]['frames_sha256'],
                     tracking['recordings'][name]['trace_sha256'], candidates['recordings'][name]['sha256']]
        for path, checksum in zip(paths, checksums):
            assert digest(path) == checksum
            inputs[str(path.relative_to(ROOT))] = checksum
        with paths[1].open() as stream:
            frames = {row['end_sample']: {int(v) for v in row['keys'].split(',') if v} for row in csv.DictReader(stream, delimiter='\t')}
        with paths[2].open() as stream:
            states = {(row['end_sample'], int(row['midi'])): row for row in csv.DictReader(stream, delimiter='\t')}
        owners, native = {}, {}
        with paths[3].open() as stream:
            for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                rows = list(frame)
                owners[endpoint] = {int(row['midi']) for row in rows if row['owner'] == '2' and float(row['keyboard_score']) >= .9 and row['profile'] == '0'}
                native[endpoint] = {}
                for row in rows:
                    midi = int(row['midi'])
                    old = native[endpoint].get(midi)
                    if old is None or float(row['keyboard_score']) + .01 * float(row['ownership']) > float(old['keyboard_score']) + .01 * float(old['ownership']):
                        native[endpoint][midi] = row
        stable, owned = {}, {}
        rate = baseline['recordings'][name]['rate']
        with paths[0].open() as stream:
            for endpoint, events in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                final = frames[endpoint]
                initial, _, removed = attribute(list(events), final)
                start, end = int(endpoint) / rate, min(60., int(endpoint) / rate + .05)
                for midi in initial - final:
                    if removed[midi] != 'suppress_other_dominant_same_pitch_keyboard_shadows':
                        continue
                    state = states[endpoint, midi]
                    if state['confirmed'] != '1' or int(state['hits']) < 3:
                        continue
                    debug = native[endpoint].get(midi)
                    stable_body = debug is not None and debug['profile'] == '0' and float(debug['pitch_stability']) >= .75 and float(debug['onset']) <= .1 and float(debug['decay']) <= .15
                    for rule, eligible in [('stable-display', stable.get(midi, 0) >= 3), ('stable-owned-display', owned.get(midi, 0) >= 3),
                                           ('stable-body', stable.get(midi, 0) >= 3 and stable_body)]:
                        metric = metrics.setdefault(rule, dict(added=0, held_recovery_seconds=0., unsupported_added_seconds=0.))
                        if not eligible:
                            continue
                        metric['added'] += 1
                        metric['held_recovery_seconds'] += coverage(held.get(midi, []), start, end)
                        metric['unsupported_added_seconds'] += max(0., end - start - coverage(allowed.get(midi, []), start, end))
                        additions.setdefault(rule, []).append(dict(recording=name, end_sample=int(endpoint), midi=midi))
                # Unmodified final state only; restored notes must never keep
                # themselves eligible across subsequent cleanup frames.
                stable = {midi: min(stable.get(midi, 0) + 1, 3) for midi in final}
                owned = {midi: min(owned.get(midi, 0) + 1, 3) for midi in final & owners[endpoint]}
    assert all(digest(ROOT / path) == checksum for path, checksum in inputs.items())
    result = dict(inputs=inputs, metrics=metrics, additions=additions, decision='training_diagnostic_only',
                  scope='Three prior unmodified visible/owned frames, current three raw Keyboard hits, one-hop restoration only after Other cleanup; no held-out use or native behavior change. Exact current primary traces, historical unchanged Keyboard tracking/native descriptors.')
    atomic_json(ROOT / 'build/keyboard_grace_audit.json', result)
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
