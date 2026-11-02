#!/usr/bin/env python3
"""Paired wall/thread CPU measurements under the unchanged native latency gates."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    frozen = json.loads((ROOT / 'build/low_keyboard_coherence_measurement/frozen.json').read_text())
    build_path = ROOT / frozen['build']
    assert digest(build_path) == frozen['build_sha256']
    build = json.loads(build_path.read_text())
    source = ROOT / 'tests/low_keyboard_coherence_latency.cpp'
    inputs = dict(build_sha256=digest(build_path), source_sha256=digest(source), script_sha256=digest(Path(__file__)),
                  analyzer_object_sha256=digest(build_path.parent / 'analyzer.o'), repetitions=5,
                  comparison_sha256=digest(ROOT / 'tests/note_grid_comparison.hpp'),
                  gates=dict(after_wall_p99_ms=50., after_cpu_max_ms=50., mean_added_cpu_ms=1., p99_added_cpu_ms=2.))
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    original = baseline_path.parent / 'training-1.f32'
    assert digest(original) == baseline['recordings']['training-1']['prefix_sha256']
    rate = baseline['recordings']['training-1']['rate']
    inputs.update(raw_sha256=digest(original), rate=rate, seconds=10)
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_coherence_latency' / key
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'replay.cpp').write_bytes(source.read_bytes())
    for name in ('non_tempo_snapshot.hpp', 'note_grid_comparison.hpp'):
        (directory / name).write_bytes((build_path.parent / name).read_bytes())
    raw = directory / 'prefix.f32'
    raw.write_bytes(original.read_bytes()[:rate * 10 * 4])
    objects = [ROOT / path for path in build['inputs']['objects']]
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['objects'].items())
    binary = directory / 'replay'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(build_path.parent / 'src'), '-I' + str(directory),
                    str(directory / 'replay.cpp'), str(build_path.parent / 'analyzer.o'), *map(str, objects),
                    '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    inputs['binary_sha256'] = digest(binary)
    state = dict(inputs=inputs, repetitions=[], complete=False, passed=False)
    deltas, wall, cpu = [], [], []
    decisions = None
    for index in range(5):
        path = directory / ('pass-' + str(index) + '.tsv')
        subprocess.run([str(binary), str(raw), str(rate), str(path)], check=True, timeout=1800)
        with path.open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        assert len(rows) == 200
        current = [tuple(row[k] for k in ('end_sample', 'keys', 'after_keys')) for row in rows]
        if decisions is None:
            decisions = current
        else:
            assert current == decisions
        for row in rows:
            assert row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
            assert set(row['after_keys'].split(',')) - {''} <= set(row['keys'].split(','))
            deltas.append(float(row['after_cpu_ms']) - float(row['before_cpu_ms']))
            wall.append(float(row['after_ms']))
            cpu.append(float(row['after_cpu_ms']))
        state['repetitions'].append(dict(sha256=digest(path), windows=len(rows)))
        atomic_json(directory / 'report.json', state)
        print('Coherence latency pass', index + 1, '/ 5', flush=True)
    metrics = dict(windows=len(wall), after_wall_p99_ms=sorted(wall)[int((len(wall) - 1) * .99)], after_wall_max_ms=max(wall),
                   after_cpu_max_ms=max(cpu), mean_added_cpu_ms=sum(deltas) / len(deltas),
                   p99_added_cpu_ms=sorted(deltas)[int((len(deltas) - 1) * .99)], wall_deadline_misses=sum(v > 50 for v in wall))
    state.update(complete=True, metrics=metrics, passed=all(metrics[k] < threshold for k, threshold in inputs['gates'].items()))
    assert digest(source) == inputs['source_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    atomic_json(directory / 'report.json', state)
    print(json.dumps(metrics, indent=2), flush=True)
    print((directory / 'report.json').relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed']


if __name__ == '__main__':
    main()
