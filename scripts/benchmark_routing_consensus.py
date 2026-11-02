#!/usr/bin/env python3
"""Separate scheduler wall-time outliers from measured native thread CPU cost."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from measure_routing_consensus import load_build
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    build_path, build = load_build()
    source = ROOT / 'tests/routing_consensus_latency.cpp'
    objects = [ROOT / path for path in build['inputs']['objects']]
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['objects'].items())
    inputs = dict(build_sha256=digest(build_path), source_sha256=digest(source), script_sha256=digest(Path(__file__)),
                  analyzer_object_sha256=digest(build_path.parent / 'analyzer.o'),
                  repetitions=5, gates=dict(after_wall_p99_ms=50., after_cpu_max_ms=50., mean_added_cpu_ms=1., p99_added_cpu_ms=2.))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_consensus_latency' / key
    directory.mkdir(parents=True, exist_ok=True)
    binary = directory / 'replay'
    if not binary.exists():
        (directory / 'replay.cpp').write_bytes(source.read_bytes())
        (directory / 'non_tempo_snapshot.hpp').write_bytes((build_path.parent / 'non_tempo_snapshot.hpp').read_bytes())
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(build_path.parent / 'src'), '-I' + str(build_path.parent),
                        str(directory / 'replay.cpp'), str(build_path.parent / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    raw = ROOT / 'build/routing_guitarset_controls/9801a45ca6c823e8/00_Rock2-85-F_comp_mic.f32'
    source_report = json.loads((raw.parent / 'report.json').read_text())
    rate = source_report['recordings'][raw.stem]['rate']
    inputs.update(binary_sha256=digest(binary), raw_sha256=digest(raw), rate=rate)
    state = dict(inputs=inputs, repetitions=[], complete=False, passed=False)
    cpu_deltas, wall_after, cpu_after = [], [], []
    outliers = []
    for index in range(inputs['repetitions']):
        path = directory / ('pass-' + str(index) + '.tsv')
        subprocess.run([str(binary), str(raw), str(rate), str(path)], check=True, timeout=1800)
        with path.open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        assert len(rows) == 200
        for row in rows:
            assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
            assert row['guitar'] == row['after_guitar'] and row['voice'] == row['after_voice']
            cpu_deltas.append(float(row['after_cpu_ms']) - float(row['before_cpu_ms']))
            wall_after.append(float(row['after_ms']))
            cpu_after.append(float(row['after_cpu_ms']))
            if float(row['after_ms']) > 50:
                outliers.append(dict(repetition=index, end_sample=int(row['end_sample']),
                                     wall_ms=float(row['after_ms']), cpu_ms=float(row['after_cpu_ms'])))
        state['repetitions'].append(dict(sha256=digest(path), windows=len(rows)))
        atomic_json(directory / 'report.json', state)
        print('Latency pass', index + 1, '/', inputs['repetitions'], flush=True)
    metrics = dict(windows=len(wall_after), after_wall_p99_ms=sorted(wall_after)[int((len(wall_after) - 1) * .99)],
                   after_wall_max_ms=max(wall_after), after_cpu_max_ms=max(cpu_after),
                   mean_added_cpu_ms=sum(cpu_deltas) / len(cpu_deltas),
                   p99_added_cpu_ms=sorted(cpu_deltas)[int((len(cpu_deltas) - 1) * .99)], wall_deadline_outliers=outliers)
    state.update(complete=True, metrics=metrics, passed=all(metrics[key] < threshold for key, threshold in inputs['gates'].items()))
    assert digest(source) == inputs['source_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    atomic_json(directory / 'report.json', state)
    print(json.dumps(metrics, indent=2), flush=True)
    print((directory / 'report.json').relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed']


if __name__ == '__main__':
    main()
