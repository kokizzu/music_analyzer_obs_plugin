#!/usr/bin/env python3
"""Capture a training-only joint spectral cue from isolated piano references."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import csv
import hashlib
import json
from pathlib import Path
import wave

import numpy as np

from joint_pitch_reference import spectrum, fit
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    manifest = ROOT / 'build/real_note_samples/manifest.tsv'
    with manifest.open() as stream:
        samples = [r for r in csv.DictReader(stream, delimiter='\t') if r['id'].startswith('keyboard_acoustic_004-')]
    assert len(samples) == 106
    inputs = dict(manifest_sha256=digest(manifest), script_sha256=digest(Path(__file__)), helper_sha256=digest(ROOT / 'scripts/joint_pitch_reference.py'),
                  reference_group='keyboard_acoustic_004', samples={}, numpy_version=np.__version__, iterations=80,
                  rate=16000, window_samples=1600, fft_size=4096, midis=list(range(21, 109)),
                  reference_endpoints=[1600, 3200, 4800], smoothing=[.25, .5, .25], missing_note_rule='Frequency-axis interpolation from nearest isolated reference pitch')
    templates = {}
    for sample in samples:
        path = manifest.parent / sample['path']
        inputs['samples'][str(path.relative_to(ROOT))] = digest(path)
        with wave.open(str(path), 'rb') as stream:
            assert stream.getnchannels() == 1 and stream.getsampwidth() == 2 and stream.getframerate() == 16000
            audio = np.frombuffer(stream.readframes(4800), dtype='<i2').astype(float) / 32768
        frames = np.stack([audio[end-1600:end] for end in inputs['reference_endpoints']])
        spectra = spectrum(frames)
        spectra /= np.maximum(np.linalg.norm(spectra, axis=1, keepdims=True), 1e-12)
        templates.setdefault(int(sample['midi']), []).append(spectra.mean(axis=0))
    templates = {m: np.mean(v, axis=0) for m, v in templates.items()}
    frequencies = np.fft.rfftfreq(4096, 1 / 16000)
    columns, provenance = [], []
    for midi in inputs['midis']:
        source = min(templates, key=lambda m: (abs(m-midi), m))
        values = np.interp(frequencies / 2 ** ((midi-source)/12), frequencies, templates[source], left=0, right=0)
        columns.append(values / max(np.linalg.norm(values), 1e-12))
        provenance.append(dict(midi=midi, reference_midi=source, interpolated=midi != source))
    dictionary = np.stack(columns, axis=1)
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    audit_path = ROOT / 'build/keyboard_confirmation_audit.json'
    baseline, audit = (json.loads(p.read_text()) for p in (baseline_path, audit_path))
    inputs.update(baseline_sha256=digest(baseline_path), audit_sha256=digest(audit_path))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/joint_pitch' / key
    directory.mkdir(parents=True, exist_ok=True)
    atomic_json(directory / 'dictionary.json', dict(inputs=inputs, provenance=provenance, columns=dictionary.T.tolist()))
    report = dict(inputs=inputs, dictionary_sha256=digest(directory / 'dictionary.json'), recordings={}, complete=False,
                  scope='Training-1/2/3 only. Each original causal 100 ms window is independently resampled and fitted. Batching is per-column independent, with no lookahead or recording-fitted templates. Reference piano identity is disjoint from performance recordings. No native behavior change or held-out use.')
    for name in ('training-1', 'training-2', 'training-3'):
        raw = baseline_path.parent / (name + '.f32')
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        audio = np.fromfile(raw, dtype='<f4').astype(float)
        rate = baseline['recordings'][name]['rate']
        hop, count = round(rate * .05), round(rate * .1)
        padded = np.pad(audio, (count, 0))
        positions = np.arange(1600) * rate / 16000
        frames = np.stack([np.interp(positions, np.arange(count), padded[end:end+count]) for end in range(hop, len(audio)+1, hop)])
        observed = spectrum(frames).T
        observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
        activation = fit(dictionary, observed, inputs['iterations'])
        projection = dictionary.T @ observed
        features = []
        for case in audit['recordings'][name]['cases']:
            frame = case['end_sample'] // hop - 1
            midi = case['midi']
            if not 21 <= midi <= 108:
                continue
            index = midi - 21
            value = activation[index, frame]
            features.append(dict(end_sample=case['end_sample'], midi=midi,
                relative_activation=float(value / max(activation[:, frame].max(), 1e-12)),
                activation_fraction=float(value / max(activation[:, frame].sum(), 1e-12)),
                explained_projection=float(value / max(projection[index, frame], 1e-12)),
                residual=float(np.linalg.norm(observed[:, frame] - dictionary @ activation[:, frame])),
                held_seconds=case['held_seconds'], unsupported_seconds=case['unsupported_seconds']))
        report['recordings'][name] = dict(raw_sha256=digest(raw), frames=len(frames), cases=features)
        atomic_json(directory / 'report.json', report)
        print(name, len(features), 'first-hit cues from', len(frames), 'independent causal fits', flush=True)
    report['complete'] = True
    atomic_json(directory / 'report.json', report)
    atomic_json(directory.parent / 'current.json', dict(report=str((directory / 'report.json').relative_to(ROOT)), sha256=digest(directory / 'report.json')))
    print((directory / 'report.json').relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
