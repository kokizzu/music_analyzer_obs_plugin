#!/usr/bin/env python3
"""Training-only causal low-frequency evidence; no native/default changes."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    os.nice(10)  # Yield CPU to the independent native validation replays.
    path = ROOT / 'build/keyboard_stage_trace/034803c68151329e/report.json'
    source = json.loads(path.read_text())
    assert source['complete']
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    inputs = dict(trace_sha256=digest(path), baseline_sha256=digest(baseline_path), script_sha256=digest(Path(__file__)),
                  windows=[.1, .2, .4], floors=[1e-5, 3e-5, 1e-4, 3e-4, .001, .003, .01],
                  modes=['current', 'latched'], supports=['fundamental', 'fundamental-or-third'],
                  warmup='At least three prior unmodified displayed frames and a full causal measurement window',
                  numpy_version=np.__version__)
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_coherence' / key
    directory.mkdir(parents=True, exist_ok=True)
    report = dict(inputs=inputs, recordings={}, complete=False,
                  scope='Training-1/2/3 only. Exact original PCM; weighted-mean subtraction, Hann-windowed frequency projections and RMS normalization are diagnostic features, not waveform modification. No lookahead, held-out use, threshold promotion or detector changes.')
    configurations = [(window, floor, mode, support) for window in inputs['windows'] for floor in inputs['floors']
                      for mode in inputs['modes'] for support in inputs['supports']]
    for name, entry in source['recordings'].items():
        raw = baseline_path.parent / (name + '.f32')
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        rate = baseline['recordings'][name]['rate']
        audio = np.fromfile(raw, dtype='<f4').astype(np.float64)
        frames_path = path.parent / (name + '.frames.tsv')
        assert digest(frames_path) == entry['frames_sha256']
        with frames_path.open() as stream:
            frames = list(csv.DictReader(stream, delimiter='\t'))
        candidates = {}
        for candidate in entry['low_cases']:
            candidates.setdefault(candidate['end_sample'], []).append(candidate)
        geometries = {}
        frequencies = np.array([440 * 2 ** ((midi - 69) / 12) for midi in range(21, 40)])
        for seconds in inputs['windows']:
            count = round(seconds * rate)
            window = np.hanning(count)
            times = np.arange(count) / rate
            weights = np.exp(-2j * np.pi * np.concatenate((frequencies, frequencies * 3))[:, None] * times) * window
            geometries[seconds] = count, window, float(window.sum()), weights
        stable = {}
        latched = {configuration: set() for configuration in configurations}
        metrics = {str(configuration): dict(removed=0, held_removed_seconds=0., supported_removed_seconds=0., unsupported_removed_seconds=0.)
                   for configuration in configurations}
        saved = []
        for index, frame in enumerate(frames, 1):
            endpoint = int(frame['end_sample'])
            current = {int(v) for v in frame['keys'].split(',') if v and 21 <= int(v) < 40}
            evidence = {}
            for seconds, (count, window, weight_sum, weights) in geometries.items():
                if endpoint < count:
                    continue
                values = audio[endpoint - count:endpoint]
                centered = values - float(window @ values) / weight_sum
                rms = math.sqrt(max(0., float(window @ (centered * centered)) / weight_sum))
                projection = np.abs(weights @ centered) * 2 / weight_sum / max(math.sqrt(2) * rms, 1e-12)
                evidence[seconds] = projection[:19], projection[19:]
            for configuration in configurations:
                seconds, floor, mode, support = configuration
                latched[configuration].intersection_update(current)
                if seconds not in evidence:
                    continue
                fundamental, third = evidence[seconds]
                supported = {midi for midi in current if fundamental[midi - 21] >= floor or
                             support == 'fundamental-or-third' and third[midi - 21] >= floor}
                latched[configuration].update(supported)
                accepted = latched[configuration] if mode == 'latched' else supported
                metric = metrics[str(configuration)]
                for candidate in candidates.get(endpoint, []):
                    midi = candidate['midi']
                    if stable.get(midi, 0) < 3 or midi in accepted:
                        continue
                    metric['removed'] += 1
                    for key in ('held_seconds', 'supported_seconds', 'unsupported_seconds'):
                        metric[key.replace('_seconds', '_removed_seconds')] += candidate[key]
            for candidate in candidates.get(endpoint, []):
                saved.append(dict(end_sample=endpoint, midi=candidate['midi'], stable_before=stable.get(candidate['midi'], 0),
                                  evidence={str(seconds): [float(value[candidate['midi'] - 21]) for value in pair] for seconds, pair in evidence.items()},
                                  held_seconds=candidate['held_seconds'], supported_seconds=candidate['supported_seconds'], unsupported_seconds=candidate['unsupported_seconds']))
            stable = {midi: min(stable.get(midi, 0) + 1, 3) for midi in current}
            if index % 400 == 0:
                print(name, index, '/', len(frames), 'causal windows', flush=True)
        report['recordings'][name] = dict(metrics=metrics, evidence=saved, raw_sha256=digest(raw))
        atomic_json(directory / 'report.json', report)
    aggregate = {}
    for entry in report['recordings'].values():
        for configuration, metric in entry['metrics'].items():
            target = aggregate.setdefault(configuration, {key: 0 for key in metric})
            for key, value in metric.items():
                target[key] += value
    report.update(complete=True, aggregate=aggregate)
    assert digest(Path(__file__)) == inputs['script_sha256']
    atomic_json(directory / 'report.json', report)
    safe = [(configuration, metric) for configuration, metric in aggregate.items() if metric['supported_removed_seconds'] < 1e-8]
    print(json.dumps(sorted(safe, key=lambda item: item[1]['unsupported_removed_seconds'], reverse=True)[:8], indent=2), flush=True)
    print((directory / 'report.json').relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
