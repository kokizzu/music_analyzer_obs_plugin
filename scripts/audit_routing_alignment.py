#!/usr/bin/env python3
"""Check baseline audio/MIDI onset alignment without adjusting labels."""
import hashlib
import json
from pathlib import Path

from midi_sustain_reference import read_intervals
from routing_alignment import envelopes, lag_evidence
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    import numpy as np
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    assert baseline['complete']
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (baseline_path, Path(__file__), ROOT / 'scripts/routing_alignment.py', ROOT / 'scripts/midi_sustain_reference.py')}
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_alignment' / key
    output.mkdir(parents=True, exist_ok=True)
    report = dict(inputs=inputs, recordings={}, label_adjustments_applied=False,
                  scope='Spectral novelty/MIDI onset-envelope correlation within +/-400ms, whole prefix and thirds; not independent proof of note-level alignment')
    for sample in baseline['selection']:
        recording = baseline['recordings'][sample['id']]
        raw = baseline_path.parent / (sample['id'] + '.f32')
        midi = ROOT / sample['midi']
        assert digest(raw) == recording['prefix_sha256'] and digest(midi) == sample['midi_sha256']
        audio, reference, step = envelopes(np.fromfile(raw, dtype='<f4'), recording['rate'], read_intervals(midi.read_bytes()))
        result = dict(whole=lag_evidence(audio, reference, step), segments=[])
        for part in range(3):
            begin, end = part * len(audio) // 3, (part + 1) * len(audio) // 3
            result['segments'].append(lag_evidence(audio[begin:end], reference[begin:end], step))
        report['recordings'][sample['id']] = result
        print(sample['id'], json.dumps(result), flush=True)
    assert all(digest(ROOT / p) == checksum for p, checksum in inputs.items())
    atomic_json(output / 'report.json', report)
    print((output / 'report.json').relative_to(ROOT))


if __name__ == '__main__':
    main()
