#!/usr/bin/env python3
"""Capture native candidate evidence without changing the measured primary engine."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from routing_duration_baseline import ROOT, atomic_json, digest, primary_build


def main():
    directory, build = primary_build()
    captures = []
    for path in (ROOT / 'build/routing_duration_baseline').glob('*/report.json'):
        report = json.loads(path.read_text())
        if report['complete'] and report['build']['binary_sha256'] == build['binary_sha256']:
            captures.append((path, report))
    assert len(captures) == 1, 'Need one complete matching primary baseline'
    baseline_path, baseline = captures[0]
    source = ROOT / 'tests/routing_candidate_replay.cpp'
    inputs = dict(build=build, baseline_sha256=digest(baseline_path), source_sha256=digest(source),
                  script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_candidate_evidence' / key
    output.mkdir(parents=True, exist_ok=True)
    binary = output / 'replay'
    state_path = output / 'report.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else dict(inputs=inputs, recordings={}, complete=False)
    assert state['inputs'] == inputs
    if not binary.exists():
        objects = [str(directory / (name + '.o')) for name in (
            'BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin', 'basic_pitch_onnx_worker',
            'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history', 'analyzer')]
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), str(source),
                        *objects, '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    if 'binary_sha256' in state:
        assert state['binary_sha256'] == digest(binary)
    state['binary_sha256'] = digest(binary)
    atomic_json(state_path, state)
    compare = ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums')
    for sample in baseline['selection']:
        name = sample['id']
        raw = baseline_path.parent / (name + '.f32')
        reference = baseline_path.parent / (name + '.tsv')
        recording = baseline['recordings'][name]
        assert digest(raw) == recording['prefix_sha256'] and digest(reference) == recording['frames_sha256']
        destination = output / (name + '.tsv')
        if name not in state['recordings']:
            subprocess.run([str(binary), str(raw), str(recording['rate']), str(destination)], check=True, timeout=1800)
        else:
            assert digest(destination) == state['recordings'][name]['sha256']
        with reference.open() as stream:
            expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
        seen, count = set(), 0
        with destination.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                assert row['end_sample'] in expected
                assert all(row[key] == expected[row['end_sample']][key] for key in compare), 'Evidence exporter changed primary outputs'
                seen.add(row['end_sample'])
                count += 1
        assert seen == set(expected), 'Missing evidence window'
        state['recordings'][name] = dict(sha256=digest(destination), candidate_rows=count, windows=len(seen), cohort=sample['cohort'])
        atomic_json(state_path, state)
        print(name, len(seen), 'windows;', count, 'candidate rows; exact primary-output parity', flush=True)
    assert digest(source) == inputs['source_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    atomic_json(state_path, state)
    print(state_path.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
