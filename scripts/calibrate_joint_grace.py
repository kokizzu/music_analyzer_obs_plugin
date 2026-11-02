#!/usr/bin/env python3
"""Freeze the training-selected release rule before disjoint calibration."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import csv
import hashlib
import json
from itertools import groupby
from pathlib import Path
import subprocess

import numpy as np

from audit_keyboard_recovery import coverage
from capture_joint_note_coverage import causal_windows
from joint_grace_rules import eligible
from joint_pitch_reference import spectrum, fit
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge, score
from trace_keyboard_stages import attribute, build as build_stages
from trace_primary_duration import build as build_tracking


def read(path):
    return json.loads(path.read_text())


def evaluate(name, frames_path, stages_path, tracking_path, activation, projection, baseline):
    with frames_path.open() as stream:
        frames = list(csv.DictReader(stream, delimiter='\t'))
    with tracking_path.open() as stream:
        tracking = {(int(r['end_sample']), int(r['midi'])): r for r in csv.DictReader(stream, delimiter='\t')}
    sample = next(s for s in baseline['selection'] if s['id'] == name)
    midi_path = ROOT / sample['midi']
    assert digest(midi_path) == sample['midi_sha256']
    notes = read_intervals(midi_path.read_bytes())
    held, allowed = {}, {}
    for note in notes:
        if note['channel'] != 9:
            held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
            allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
    held, allowed = ({m: merge(v) for m, v in d.items()} for d in (held, allowed))
    rate = baseline['recordings'][name]['rate']
    relative = activation / np.maximum(activation.max(axis=0), 1e-12)
    explained = activation / np.maximum(projection, 1e-12)
    previous, proposed, cases = {}, [], []
    metrics = dict(cells=0, held_seconds=0., supported_seconds=0., unsupported_seconds=0.)
    with stages_path.open() as stream:
        groups = groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r: int(r['end_sample']))
        for index, (endpoint, events) in enumerate(groups):
            frame = frames[index]
            assert endpoint == int(frame['end_sample'])
            final = {int(v) for v in frame['keys'].split(',') if v}
            initial, _, removed = attribute(list(events), final)
            additions = set()
            start, end = endpoint / rate, min(60., endpoint / rate + .05)
            if end > start:
                for midi in initial - final:
                    if not 21 <= midi <= 108:
                        continue
                    state = tracking[endpoint, midi]
                    if not eligible(True, False, removed[midi], state['confirmed'] == '1', int(state['hits']), previous.get(midi, 0),
                                    float(relative[midi - 21, index]), float(explained[midi - 21, index])):
                        continue
                    additions.add(midi)
                    recovered = coverage(held.get(midi, []), start, end)
                    supported = coverage(allowed.get(midi, []), start, end)
                    metrics['cells'] += 1
                    metrics['held_seconds'] += recovered
                    metrics['supported_seconds'] += supported
                    metrics['unsupported_seconds'] += max(0., end - start - supported)
                    cases.append(dict(end_sample=endpoint, midi=midi, held_seconds=recovered,
                                      unsupported_seconds=max(0., end - start - supported)))
            proposed.append(dict(frame, keys=','.join(str(v) for v in sorted(final | additions))))
            previous = {m: min(previous.get(m, 0) + 1, 3) for m in final}
    assert len(proposed) == len(frames) == activation.shape[1]
    before, after = (score(rows, notes, rate)['keys'] for rows in (frames, proposed))
    return dict(metrics=metrics, cases=cases, before=before, after=after)


def main():
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = read(baseline_path)
    screen_path = ROOT / 'build/joint_note_coverage_screen.json'
    screen = read(screen_path)
    candidate = next(c for c in screen['viable'] if c['mode'] == 'grace-display' and c['relative_floor'] == .8 and c['explained_floor'] == .3)
    assert candidate['metrics']['unsupported_seconds'] == 0 and candidate['metrics']['held_seconds'] > 0
    capture_path = ROOT / 'build/joint_note_coverage/017a9ad67bd36e7d/report.json'
    captured = read(capture_path)
    inputs = dict(screen_sha256=digest(screen_path), capture_sha256=digest(capture_path),
                  dictionary_sha256=digest(ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'),
                  baseline_sha256=digest(baseline_path), rule=candidate,
                  scripts={p: digest(ROOT / p) for p in ('scripts/calibrate_joint_grace.py', 'scripts/joint_grace_rules.py',
                           'scripts/joint_pitch_reference.py', 'scripts/capture_joint_note_coverage.py',
                           'scripts/trace_keyboard_stages.py', 'scripts/trace_primary_duration.py', 'scripts/routing_duration_score.py')})
    # Verify the exact causal rule on training traces before freezing it.
    training = {}
    for name in captured['recordings']:
        arrays_path = capture_path.parent / (name + '.npz')
        assert digest(arrays_path) == captured['recordings'][name]['sha256']
        arrays = np.load(arrays_path)
        training[name] = evaluate(name, ROOT / 'build/keyboard_stage_trace/034803c68151329e' / (name + '.frames.tsv'),
                                  ROOT / 'build/keyboard_stage_trace/034803c68151329e' / (name + '.trace.tsv'),
                                  ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f' / (name + '.trace.tsv'),
                                  arrays['activation'], arrays['projection'], baseline)
    for field, expected in candidate['metrics'].items():
        assert abs(sum(r['metrics'][field] for r in training.values()) - expected) < 1e-7
    directory = ROOT / 'build/joint_grace_calibration' / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    freeze = directory / 'frozen-training.json'
    if freeze.exists():
        assert read(freeze) == inputs
    else:
        atomic_json(freeze, inputs)
    print('Frozen training-selected grace rule before calibration:', directory.relative_to(ROOT), flush=True)
    stages_dir, stage_build = build_stages()
    tracking_dir, tracking_build = build_tracking()
    name = 'training-4'
    raw = baseline_path.parent / (name + '.f32')
    assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
    rate = baseline['recordings'][name]['rate']
    frames, stages, track_frames, tracking = [directory / p for p in ('frames.tsv', 'stages.tsv', 'tracking-frames.tsv', 'tracking.tsv')]
    subprocess.run([str(stages_dir / 'replay'), str(raw), str(rate), str(frames), str(stages)], check=True, timeout=3600)
    subprocess.run([str(tracking_dir / 'replay'), str(raw), str(rate), str(track_frames), str(tracking)], check=True, timeout=3600)
    assert frames.read_bytes() == track_frames.read_bytes()
    reference = ROOT / 'build/routing_consensus_pair/e63350f9b5113f8b/piano-training-4.tsv'
    with frames.open() as stream, reference.open() as other:
        actual, expected = list(csv.DictReader(stream, delimiter='\t')), list(csv.DictReader(other, delimiter='\t'))
    assert len(actual) == len(expected) == 1200
    for a, b in zip(actual, expected):
        assert all(a[k] == b['after_' + k if k in ('guitar', 'voice') else k] for k in a)
    dictionary = np.array(read(ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json')['columns']).T
    observed = spectrum(causal_windows(np.fromfile(raw, dtype='<f4').astype(float), rate)).T
    observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
    activation = fit(dictionary, observed)
    result = evaluate(name, frames, stages, tracking, activation, dictionary.T @ observed, baseline)
    passed = result['metrics']['unsupported_seconds'] < 1e-8 and result['after']['matched_attacks'] >= result['before']['matched_attacks']
    report = dict(inputs=inputs, training=training, calibration=result, passed=passed, complete=True,
                  stage_build=stage_build, tracking_build=tracking_build,
                  artifacts={str(p.relative_to(ROOT)): digest(p) for p in (frames, stages, track_frames, tracking)},
                  scope='Native instrumentation reconstructs current primary exactly; restoration remains an offline hypothesis, not a native implementation. Training rule frozen before recording-four calibration; no held-out use.')
    assert all(digest(ROOT / p) == h for p, h in inputs['scripts'].items())
    atomic_json(directory / 'report.json', report)
    atomic_json(directory.parent / 'current.json', dict(report=str((directory / 'report.json').relative_to(ROOT)), sha256=digest(directory / 'report.json')))
    print(json.dumps(result['metrics']), 'calibration passed', passed, flush=True)
    assert passed


if __name__ == '__main__':
    main()
