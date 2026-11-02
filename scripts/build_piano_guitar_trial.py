#!/usr/bin/env python3
"""Compile the native candidate on primary sources without editing dirty files."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from publish_next_detection import git
from routing_duration_baseline import ROOT, atomic_json, digest, primary_build

ASSETS = ['src/piano_guitar_features.hpp', 'src/piano_guitar_verifier.hpp', 'src/piano_guitar_model_data.hpp',
          'src/experimental_piano_guitar_hook.inc', 'models/piano_guitar_verifier.json', 'tests/piano_guitar_pair.cpp']


def main():
    baseline, build = primary_build()
    inputs = dict(build=build, assets={p: digest(ROOT / p) for p in ASSETS}, script_sha256=digest(Path(__file__)),
                  comparison_source_sha256=digest(ROOT / 'tests/non_tempo_snapshot.hpp'))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/piano_guitar_trial' / key
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
    cpp, header = (directory / 'src' / name for name in ('analyzer.cpp', 'analyzer.hpp'))
    original, settings = cpp.read_text(), header.read_text()
    integrated = 'experimental_piano_guitar_filter' in settings
    if integrated:
        assert (ROOT / 'src/experimental_piano_guitar_hook.inc').read_text() in original
        assert '#include "piano_guitar_features.hpp"' in original
    else:
        assert 'experimental_piano_guitar_filter' not in original
        original = original.replace('#include "analyzer.hpp"', '#include "analyzer.hpp"\n#include "piano_guitar_features.hpp"', 1)
    anchor = '\n\t// Keep the expensive high-tempo hypothesis outside the phase path.'
    assert original.count(anchor) == 1
    if not integrated:
        original = original.replace(anchor, '\n' + (ROOT / 'src/experimental_piano_guitar_hook.inc').read_text() + anchor, 1)
    setting = '\tint tempo_debug_probe_bpm = 0;'
    assert settings.count(setting) == 1
    if not integrated:
        settings = settings.replace(setting, setting + '\n\tbool experimental_piano_guitar_filter = false;', 1)
    cpp.write_text(original)
    header.write_text(settings)
    for p in ASSETS:
        if p.startswith('src/'):
            (directory / p).write_bytes((ROOT / p).read_bytes())
    comparison = (ROOT / 'tests/non_tempo_snapshot.hpp').read_text()
    if 'keyboard_chord_analysis_notes' not in settings:
        comparison = ''.join(line for line in comparison.splitlines(True) if '"keyboard_chord_analysis_notes"' not in line)
    if 'keyboard_chord_raw_label' not in settings:
        begin = comparison.index('\tif (std::strcmp(a.keyboard_chord_raw_label')
        end = comparison.index('\tfor (std::size_t i = 0; i < a.drums.size()', begin)
        comparison = comparison[:begin] + comparison[end:]
    (directory / 'non_tempo_snapshot.hpp').write_text(comparison)
    (directory / 'pair.cpp').write_bytes((ROOT / 'tests/piano_guitar_pair.cpp').read_bytes())
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    analyzer = directory / 'analyzer.o'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent),
                    '-I' + str(baseline / 'third_party/beat_and_tempo_tracking'), '-c', str(cpp), '-o', str(analyzer)], check=True)
    objects = [str(baseline / (name + '.o')) for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    binary = directory / 'pair'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), '-I' + str(directory),
                    str(directory / 'pair.cpp'), str(analyzer), *objects, '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    assert all(digest(ROOT / p) == value for p, value in inputs['assets'].items())
    state = dict(inputs=inputs, cpp_sha256=digest(cpp), hpp_sha256=digest(header), binary_sha256=digest(binary),
                 scope='Candidate hook only on primary source; optional flag false by default; dirty analyzer untouched')
    atomic_json(checkpoint, state)
    print(directory.relative_to(ROOT))


if __name__ == '__main__':
    main()
