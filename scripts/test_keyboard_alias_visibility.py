#!/usr/bin/env python3
"""Compile the focused visibility regression against a primary source export."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    identity()
    source = ROOT / 'tests/keyboard_alias_visibility.cpp'
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(), test_sha256=digest(source), script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/keyboard_alias_visibility' / key
    directory.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(directory, filter='data')
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    baseline = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    objects = [baseline / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    binary = directory / 'test'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), '-I' + str(sdk[0].parent),
                    '-I' + str(baseline / 'third_party/beat_and_tempo_tracking'), str(source), *map(str, objects),
                    '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    result = subprocess.run([str(binary)], text=True, capture_output=True)
    print(result.stdout + result.stderr, end='')
    atomic_json(directory / 'report.json', dict(inputs=inputs, binary_sha256=digest(binary), returncode=result.returncode,
                output=result.stdout + result.stderr, scope='Focused regression on unmodified primary; failure is expected before the visibility fix'))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
