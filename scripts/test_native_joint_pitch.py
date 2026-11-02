#!/usr/bin/env python3
"""Build the independent native fitter and verify frozen training parity."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from capture_joint_note_coverage import causal_windows
from joint_pitch_reference import spectrum, fit
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    dictionary_path = ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    dictionary = np.array(json.loads(dictionary_path.read_text())['columns'])
    inputs = dict(dictionary_sha256=digest(dictionary_path), script_sha256=digest(Path(__file__)),
                  assets={p: digest(ROOT / p) for p in ('src/joint_piano_fit.hpp', 'tests/joint_piano_fit_replay.cpp',
                          'scripts/capture_joint_note_coverage.py', 'scripts/joint_pitch_reference.py')},
                  compiler=subprocess.run(['g++', '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0],
                  absolute_tolerance=1e-7)
    directory = ROOT / 'build/native_joint_pitch' / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    model = directory / 'dictionary.f64'
    dictionary.astype('<f8').tofile(model)
    binary = directory / 'replay'
    subprocess.run(['g++', '-O2', '-std=c++17', '-Wall', '-Wextra', '-I' + str(ROOT / 'src'),
                    str(ROOT / 'tests/joint_piano_fit_replay.cpp'), '-o', str(binary)], check=True)
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    capture_path = ROOT / 'build/joint_note_coverage/017a9ad67bd36e7d/report.json'
    captured = json.loads(capture_path.read_text())
    report = dict(inputs=inputs, binary_sha256=digest(binary), recordings={}, complete=False, passed=False)
    for name in ('training-1', 'training-2', 'training-3'):
        raw = baseline_path.parent / (name + '.f32')
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        result = directory / (name + '.f64')
        process = subprocess.run([str(binary), str(model), str(raw), str(baseline['recordings'][name]['rate']), str(result)], check=True, text=True, capture_output=True)
        actual = np.fromfile(result, dtype='<f8').reshape(-1, 4, 88).transpose(1, 2, 0)
        source = capture_path.parent / (name + '.npz')
        assert digest(source) == captured['recordings'][name]['sha256']
        arrays = np.load(source)
        activation, projection = arrays['activation'], arrays['projection']
        expected = np.stack((activation, projection, activation / np.maximum(activation.max(axis=0), 1e-12), activation / np.maximum(projection, 1e-12)))
        error = float(np.max(np.abs(actual - expected)))
        decisions = (actual[2] >= .8) & (actual[3] >= .3)
        reference = (expected[2] >= .8) & (expected[3] >= .3)
        mismatches = int(np.count_nonzero(decisions != reference))
        report['recordings'][name] = dict(sha256=digest(result), raw_sha256=digest(raw), frames=actual.shape[-1],
                                        maximum_absolute_error=error, threshold_mismatches=mismatches, timing=process.stdout.strip())
        atomic_json(directory / 'report.json', report)
        print(name, error, 'max absolute error;', mismatches, 'threshold mismatches;', process.stdout.strip(), flush=True)
    for rate in (16000, 44100, 48000):
        name = 'synthetic-' + str(rate)
        time = np.arange(rate) / rate
        audio = (.2 * np.sin(2*np.pi*65.406391325*time) + .1*np.sin(2*np.pi*440*time) +
                 .01*np.random.default_rng(714).normal(size=rate)).astype('<f4')
        audio[:round(rate*.2)] = 0
        raw = directory / (name + '.f32')
        audio.tofile(raw)
        result = directory / (name + '.f64')
        process = subprocess.run([str(binary), str(model), str(raw), str(rate), str(result)], check=True, text=True, capture_output=True)
        actual = np.fromfile(result, dtype='<f8').reshape(-1, 4, 88).transpose(1, 2, 0)
        observed = spectrum(causal_windows(audio.astype(float), rate)).T
        observed /= np.maximum(np.linalg.norm(observed, axis=0, keepdims=True), 1e-12)
        activation = fit(dictionary.T, observed)
        projection = dictionary @ observed
        expected = np.stack((activation, projection, activation / np.maximum(activation.max(axis=0), 1e-12), activation / np.maximum(projection, 1e-12)))
        error = float(np.max(np.abs(actual - expected)))
        mismatches = int(np.count_nonzero(((actual[2] >= .8) & (actual[3] >= .3)) != ((expected[2] >= .8) & (expected[3] >= .3))))
        report['recordings'][name] = dict(sha256=digest(result), raw_sha256=digest(raw), frames=actual.shape[-1],
                                        maximum_absolute_error=error, threshold_mismatches=mismatches, timing=process.stdout.strip())
        print(name, error, 'max absolute error;', mismatches, 'threshold mismatches', flush=True)
    report.update(complete=True, passed=all(r['maximum_absolute_error'] < inputs['absolute_tolerance'] and r['threshold_mismatches'] == 0 for r in report['recordings'].values()))
    atomic_json(directory / 'report.json', report)
    atomic_json(directory.parent / 'current.json', dict(report=str((directory / 'report.json').relative_to(ROOT)), sha256=digest(directory / 'report.json')))
    assert report['passed']


if __name__ == '__main__':
    main()
