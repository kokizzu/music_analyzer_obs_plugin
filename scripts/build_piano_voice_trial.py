#!/usr/bin/env python3
"""Compile a Voice-only candidate against verified primary, preserving dirty work."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest

ASSETS = ['src/experimental_piano_voice_hook.inc', 'tests/piano_voice_pair.cpp',
          'src/piano_guitar_features.hpp', 'src/piano_guitar_verifier.hpp',
          'src/piano_guitar_model_data.hpp', 'src/native_timbre_features.hpp']


def main():
    identity()
    base = ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38'
    baseline = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    previous = json.loads((base / 'build.json').read_text())
    cpp, header = (git('show', 'HEAD:src/analyzer.' + suffix) for suffix in ('cpp', 'hpp'))
    assert hashlib.sha256(cpp.encode()).hexdigest() == previous['cpp_sha256']
    assert hashlib.sha256(header.encode()).hexdigest() == previous['hpp_sha256']
    objects = [baseline / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    inputs = dict(primary_cpp_sha256=previous['cpp_sha256'], primary_hpp_sha256=previous['hpp_sha256'],
                  source_commit=git('rev-parse', 'HEAD').strip(), objects={str(p.relative_to(ROOT)): digest(p) for p in objects},
                  assets={p: digest(ROOT / p) for p in ASSETS}, script_sha256=digest(Path(__file__)),
                  comparison_sha256=digest(base / 'non_tempo_snapshot.hpp'))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/piano_voice_trial' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'pair') == state['binary_sha256']
        print(directory.relative_to(ROOT))
        return
    archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(directory, filter='data')
    anchor = '\n\t// Keep the expensive high-tempo hypothesis outside the phase path.'
    assert cpp.count(anchor) == 1 and 'experimental_piano_voice_filter' not in header
    cpp = cpp.replace(anchor, '\n' + (ROOT / ASSETS[0]).read_text() + anchor, 1)
    anchor = '\tbool experimental_piano_guitar_filter = false;'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n\tbool experimental_piano_voice_filter = false;', 1)
    (directory / 'src/analyzer.cpp').write_text(cpp)
    (directory / 'src/analyzer.hpp').write_text(header)
    for path in ASSETS:
        if path.startswith('src/'):
            (directory / path).write_bytes((ROOT / path).read_bytes())
    (directory / 'pair.cpp').write_bytes((ROOT / 'tests/piano_voice_pair.cpp').read_bytes())
    (directory / 'non_tempo_snapshot.hpp').write_bytes((base / 'non_tempo_snapshot.hpp').read_bytes())
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent),
                    '-I' + str(baseline / 'third_party/beat_and_tempo_tracking'), '-c', str(directory / 'src/analyzer.cpp'),
                    '-o', str(directory / 'analyzer.o')], check=True)
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), '-I' + str(directory),
                    str(directory / 'pair.cpp'), str(directory / 'analyzer.o'), *map(str, objects),
                    '-lm', '-pthread', '-ldl', '-o', str(directory / 'pair')], check=True)
    assert all(digest(ROOT / p) == value for p, value in inputs['assets'].items())
    atomic_json(checkpoint, dict(inputs=inputs, cpp_sha256=digest(directory / 'src/analyzer.cpp'),
                                hpp_sha256=digest(directory / 'src/analyzer.hpp'), binary_sha256=digest(directory / 'pair')))
    print(directory.relative_to(ROOT))


if __name__ == '__main__':
    main()
