#!/usr/bin/env python3
"""Training-only continuous recovery/removal screens using a fixed joint fit."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import csv
import json
from itertools import groupby
from pathlib import Path

import numpy as np

from audit_keyboard_recovery import coverage
from evaluate_keyboard_recovery import eligible
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def metric():
    return dict(cells=0, held_seconds=0., supported_seconds=0., unsupported_seconds=0.)


def main():
    pointer = json.loads((ROOT / 'build/joint_note_coverage/current.json').read_text())
    path = ROOT / pointer['report']
    assert digest(path) == pointer['sha256']
    captured = json.loads(path.read_text())
    assert captured['complete']
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    trace_path = ROOT / 'build/keyboard_stage_trace/034803c68151329e/report.json'
    grace_path = ROOT / 'build/keyboard_grace_audit.json'
    native_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    baseline, trace, grace, native = (json.loads(p.read_text()) for p in (baseline_path, trace_path, grace_path, native_path))
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (path, baseline_path, trace_path, grace_path, native_path, Path(__file__))}
    for helper in ('audit_keyboard_recovery.py', 'evaluate_keyboard_recovery.py', 'midi_sustain_reference.py', 'routing_duration_score.py'):
        inputs['scripts/' + helper] = digest(ROOT / 'scripts' / helper)
    floors = [.01, .1, .3, .5, .8]
    configurations = [(mode, r, e) for mode in ('low-current', 'low-latched', 'grace-display', 'grace-body', 'guitar-supported') for r in floors for e in floors]
    recordings = {}
    for name in captured['recordings']:
        target = path.parent / (name + '.npz')
        assert digest(target) == captured['recordings'][name]['sha256']
        inputs[str(target.relative_to(ROOT))] = digest(target)
        arrays = np.load(target)
        activation, projection = arrays['activation'], arrays['projection']
        relative = activation / np.maximum(activation.max(axis=0), 1e-12)
        explained = activation / np.maximum(projection, 1e-12)
        sample = next(s for s in baseline['selection'] if s['id'] == name)
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        inputs[str(midi_path.relative_to(ROOT))] = digest(midi_path)
        held, allowed = {}, {}
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel'] == 9:
                continue
            held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
            allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held, allowed = ({m: merge(v) for m, v in d.items()} for d in (held, allowed))
        rate = baseline['recordings'][name]['rate']
        hop = round(rate * .05)
        frames_path = trace_path.parent / (name + '.frames.tsv')
        assert digest(frames_path) == trace['recordings'][name]['frames_sha256']
        inputs[str(frames_path.relative_to(ROOT))] = digest(frames_path)
        with frames_path.open() as stream:
            frames = list(csv.DictReader(stream, delimiter='\t'))
        native_frames = native_path.parent / (name + '.tsv')
        assert digest(native_frames) == native['recordings'][name]['sha256']
        inputs[str(native_frames.relative_to(ROOT))] = digest(native_frames)
        recovery = {}
        with native_frames.open() as stream:
            for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r: r['end_sample']):
                recovery[int(endpoint)] = {int(row['midi']) for row in group if eligible(row)}
        low = {}
        for case in trace['recordings'][name]['low_cases']:
            low.setdefault(case['end_sample'], []).append(case['midi'])
        grace_cases = {rule: {} for rule in ('grace-display', 'grace-body')}
        for rule, source in [('grace-display', 'stable-display'), ('grace-body', 'stable-body')]:
            for case in grace['additions'][source]:
                if case['recording'] == name:
                    grace_cases[rule].setdefault(case['end_sample'], []).append(case['midi'])
        metrics = {str(c): metric() for c in configurations}
        original_runs = {}
        latches = {(r, e): set() for r in floors for e in floors}
        positive_runs = {(r, e): {} for r in floors for e in floors}
        for index, frame in enumerate(frames):
            endpoint = int(frame['end_sample'])
            assert endpoint == (index + 1) * hop
            original = {int(v) for v in frame['keys'].split(',') if v}
            start, end = endpoint / rate, min(60., endpoint / rate + .05)
            if end <= start:
                continue
            for r in floors:
                for e in floors:
                    coherent = {m + 21 for m in range(88) if relative[m, index] >= r or explained[m, index] >= e}
                    strong = {m + 21 for m in range(88) if relative[m, index] >= r and explained[m, index] >= e}
                    latch = latches[r, e]
                    latch.intersection_update(original)
                    latch.update(coherent & original)
                    previous = positive_runs[r, e]
                    positive_runs[r, e] = {m: min(previous.get(m, 0) + 1, 3) for m in strong}
                    selected = {
                        'low-current': [m for m in low.get(endpoint, []) if original_runs.get(m, 0) >= 3 and m not in coherent],
                        'low-latched': [m for m in low.get(endpoint, []) if original_runs.get(m, 0) >= 3 and m not in latch],
                        'grace-display': [m for m in grace_cases['grace-display'].get(endpoint, []) if m in strong],
                        'grace-body': [m for m in grace_cases['grace-body'].get(endpoint, []) if m in strong],
                        'guitar-supported': [m for m in recovery.get(endpoint, []) if m not in original and positive_runs[r, e].get(m, 0) >= 3]}
                    for mode, midis in selected.items():
                        result = metrics[str((mode, r, e))]
                        for midi in midis:
                            supported = coverage(allowed.get(midi, []), start, end)
                            result['cells'] += 1
                            result['held_seconds'] += coverage(held.get(midi, []), start, end)
                            result['supported_seconds'] += supported
                            result['unsupported_seconds'] += max(0., end - start - supported)
            original_runs = {m: min(original_runs.get(m, 0) + 1, 3) for m in original}
        recordings[name] = metrics
        print(name, 'continuous screens complete', flush=True)
    aggregate = {str(c): metric() for c in configurations}
    for metrics in recordings.values():
        for config, values in metrics.items():
            for key, value in values.items():
                aggregate[config][key] += value
    viable = []
    for mode, r, e in configurations:
        row = aggregate[str((mode, r, e))]
        passed = row['unsupported_seconds'] > 0 and row['supported_seconds'] < 1e-8 if mode.startswith('low-') else row['held_seconds'] > 0 and row['unsupported_seconds'] < 1e-8
        if passed:
            viable.append(dict(mode=mode, relative_floor=r, explained_floor=e, metrics=row))
    assert all(digest(ROOT / p) == h for p, h in inputs.items())
    report = dict(inputs=inputs, floors=floors, recordings=recordings, aggregate=aggregate, viable=viable,
                  scope='Exploratory training-only parameter grid; no calibration/held-out inspection or native change. Removal uses original-display history; additions use current and past spectral fits only. Positive metrics are hypotheses requiring independent native validation, not promotion evidence.')
    atomic_json(ROOT / 'build/joint_note_coverage_screen.json', report)
    print(json.dumps(viable, indent=2), flush=True)


if __name__ == '__main__':
    main()
