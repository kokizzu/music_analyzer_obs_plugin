#!/usr/bin/env python3
"""Capture all-pitch causal joint fits for continuous training-note analysis."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import hashlib
import json
from pathlib import Path

import numpy as np

from joint_pitch_reference import spectrum, fit
from routing_duration_baseline import ROOT, atomic_json, digest


def causal_windows(audio, rate):
    hop, count = round(rate * .05), round(rate * .1)
    assert audio.ndim == 1 and len(audio) % hop == 0 and np.isfinite(audio).all()
    padded = np.pad(audio, (count, 0))
    positions = np.arange(1600) * rate / 16000
    return np.stack([np.interp(positions, np.arange(count), padded[end:end+count]) for end in range(hop, len(audio)+1, hop)])


def main():
    dictionary_path = ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    dictionary = json.loads(dictionary_path.read_text())
    matrix = np.array(dictionary['columns']).T
    assert matrix.shape == (2049, 88)
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    inputs = dict(dictionary_sha256=digest(dictionary_path), baseline_sha256=digest(baseline_path),
                  script_sha256=digest(Path(__file__)), helper_sha256=digest(ROOT / 'scripts/joint_pitch_reference.py'),
                  numpy_version=np.__version__, iterations=80, selection=['training-1', 'training-2', 'training-3'],
                  resampling='Independent causal 100ms windows, linear interpolation to 1600 samples; no lookahead or waveform gain')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/joint_note_coverage' / key
    directory.mkdir(parents=True, exist_ok=True)
    report = dict(inputs=inputs, recordings={}, complete=False,
                  scope='Training only, all 88 pitches at all native endpoints. Fixed isolated-reference dictionary; no runtime change or held-out use.')
    for name in inputs['selection']:
        raw = baseline_path.parent / (name + '.f32')
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        audio = np.fromfile(raw, dtype='<f4').astype(float)
        observed = spectrum(causal_windows(audio, baseline['recordings'][name]['rate'])).T
        observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
        activations = fit(matrix, observed, inputs['iterations'])
        projection = matrix.T @ observed
        residual = np.linalg.norm(observed - matrix @ activations, axis=0)
        target = directory / (name + '.npz')
        np.savez(target, activation=activations, projection=projection, residual=residual)
        report['recordings'][name] = dict(raw_sha256=digest(raw), sha256=digest(target), frames=activations.shape[1])
        atomic_json(directory / 'report.json', report)
        print(name, activations.shape[1], 'frames x', activations.shape[0], 'joint pitch activations', flush=True)
    report['complete'] = True
    atomic_json(directory / 'report.json', report)
    atomic_json(directory.parent / 'current.json', dict(report=str((directory / 'report.json').relative_to(ROOT)), sha256=digest(directory / 'report.json')))
    print((directory / 'report.json').relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
