#!/usr/bin/env python3
"""Stage default-on primary sources and prove default output before publication."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from measure_routing_consensus import load_build
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    identity()
    build_path, build = load_build()
    for suffix in ('cpp', 'hpp'):
        assert hashlib.sha256(git('show', 'HEAD:src/analyzer.' + suffix).encode()).hexdigest() == build['inputs']['primary_' + suffix + '_sha256']
    header = (build_path.parent / 'src/analyzer.hpp').read_text()
    assert header.count('\tbool native_piano_duplicate_consensus = false;') == 1
    header = header.replace('\tbool native_piano_duplicate_consensus = false;', '\tbool native_piano_duplicate_consensus = true;', 1)
    source = ROOT / 'tests/routing_consensus_default.cpp'
    reference = ROOT / 'build/routing_consensus_pair/e63350f9b5113f8b/piano-heldout-1.tsv'
    assert reference.exists()
    inputs = dict(build_sha256=digest(build_path), default_hpp_sha256=hashlib.sha256(header.encode()).hexdigest(),
                  source_sha256=digest(source), script_sha256=digest(Path(__file__)), reference_sha256=digest(reference))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_consensus_rollout' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'report.json'
    if checkpoint.exists():
        report = json.loads(checkpoint.read_text())
        assert report['inputs'] == inputs and report['passed']
        assert digest(directory / 'default.tsv') == report['frames_sha256']
        print(directory.relative_to(ROOT))
        return
    shutil.copytree(build_path.parent / 'src', directory / 'src', dirs_exist_ok=True)
    (directory / 'src/analyzer.hpp').write_text(header)
    (directory / 'replay.cpp').write_bytes(source.read_bytes())
    (directory / 'non_tempo_snapshot.hpp').write_bytes((build_path.parent / 'non_tempo_snapshot.hpp').read_bytes())
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    base = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    include = ['-I' + str(directory / 'src'), '-I' + str(sdk[0].parent), '-I' + str(base / 'third_party/beat_and_tempo_tracking')]
    subprocess.run(['g++', '-O2', '-std=c++17', *include, '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
    objects = [ROOT / path for path in build['inputs']['objects']]
    subprocess.run(['g++', '-O2', '-std=c++17', *include, '-I' + str(directory), str(directory / 'replay.cpp'),
                    str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'replay')], check=True)
    raw = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/heldout-1.f32'
    subprocess.run([str(directory / 'replay'), str(raw), '44100', str(directory / 'default.tsv')], check=True, timeout=3600)
    with (directory / 'default.tsv').open() as stream, reference.open() as expected:
        actual, before = list(csv.DictReader(stream, delimiter='\t')), list(csv.DictReader(expected, delimiter='\t'))
    assert len(actual) == len(before) == 1200
    assert all(all(row[key] == old[key] for key in row if key not in ('before_ms', 'after_ms')) for row, old in zip(actual, before))
    assert digest(directory / 'src/analyzer.cpp') == build['cpp_sha256']
    assert digest(directory / 'src/analyzer.hpp') == inputs['default_hpp_sha256']
    report = dict(inputs=inputs, passed=True, windows=len(actual), binary_sha256=digest(directory / 'replay'),
                  frames_sha256=digest(directory / 'default.tsv'), cpp_sha256=build['cpp_sha256'], hpp_sha256=inputs['default_hpp_sha256'],
                  scope='Prospective primary source, actual default=true constructor path, exact equality to the validated explicit-on engine at all endpoints; no working source or Git index mutation')
    atomic_json(checkpoint, report)
    atomic_json(directory.parent / 'current.json', dict(report=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT), 'actual default-on replay passed', flush=True)


if __name__ == '__main__':
    main()
