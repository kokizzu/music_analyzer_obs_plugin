#!/usr/bin/env python3
"""Build and regression-test a Keyboard-only alias visibility candidate."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest

FUNCTIONS = ['prefer_debug_supported_keyboard_octave_primary', 'prefer_exact_debug_keyboard_lower_octave_primary',
             'prefer_probe_visible_low_keyboard_primary', 'prefer_raw_supported_mid_keyboard_lower_octave_primary',
             'prefer_measured_low_keyboard_octave_alias_primary', 'promote_source_hinted_keyboard_bass_primary',
             'promote_source_hinted_keyboard_weak_low_octave_primary']


def append_argument(source, name, argument):
    assert source.count(name + '(') == 1
    begin = source.index(name + '(') + len(name)
    depth = 0
    for index in range(begin, len(source)):
        depth += source[index] == '('
        depth -= source[index] == ')'
        if depth == 0:
            return source[:index] + ', ' + argument + source[index:]
    raise AssertionError('Unclosed call')


def candidate_sources(cpp, header):
    anchor = '\tbool experimental_piano_guitar_filter = false;'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n\tbool experimental_keyboard_alias_visibility_guard = false;', 1)
    for name in FUNCTIONS:
        begin = cpp.index('void ' + name + '(')
        end = cpp.index('\n}', begin) + 2
        block = cpp[begin:end]
        assert block.count('int preferred_root)') == 1
        block = block.replace('int preferred_root)', 'int preferred_root, bool visibility_guard = true)', 1)
        block = append_argument(block, 'promote_note_grid_primary_midi', 'visibility_guard')
        block = block.replace('promote_note_grid_primary_midi(', 'promote_keyboard_note_grid_primary_midi(', 1)
        cpp = cpp[:begin] + block + cpp[end:]
    anchor = 'void prefer_debug_supported_vocal_lower_octave_primary('
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, (ROOT / 'src/keyboard_alias_visibility_guard.inc').read_text() + '\n' + anchor, 1)
    begin = cpp.index('AnalysisSnapshot AnalysisEngine::analyze(')
    body = cpp[begin:]
    for name in FUNCTIONS:
        body = append_argument(body, name, 'settings.experimental_keyboard_alias_visibility_guard')
    return cpp[:begin] + body, header


def main():
    identity()
    assets = ['src/keyboard_alias_visibility_guard.inc', 'tests/keyboard_alias_visibility.cpp', 'tests/keyboard_alias_visibility_pair.cpp']
    base = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    objects = [base / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(), assets={p: digest(ROOT / p) for p in assets},
                  objects={str(p.relative_to(ROOT)): digest(p) for p in objects}, script_sha256=digest(Path(__file__)),
                  comparison_sha256=digest(ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp'))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/keyboard_alias_trial' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'pair') == state['binary_sha256']
    else:
        archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(directory, filter='data')
        cpp, header = candidate_sources(git('show', 'HEAD:src/analyzer.cpp'), git('show', 'HEAD:src/analyzer.hpp'))
        (directory / 'src/analyzer.cpp').write_text(cpp)
        (directory / 'src/analyzer.hpp').write_text(header)
        include = ['-I' + str(directory / 'src'), '-I' + str(sdk[0].parent), '-I' + str(base / 'third_party/beat_and_tempo_tracking')]
        subprocess.run(['g++', '-O2', '-std=c++17', *include, str(ROOT / 'tests/keyboard_alias_visibility.cpp'),
                        *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'regression')], check=True)
        subprocess.run([str(directory / 'regression')], check=True)
        (directory / 'pair.cpp').write_bytes((ROOT / 'tests/keyboard_alias_visibility_pair.cpp').read_bytes())
        (directory / 'non_tempo_snapshot.hpp').write_bytes((ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp').read_bytes())
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-I' + str(directory), str(directory / 'pair.cpp'),
                        str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'pair')], check=True)
        state = dict(inputs=inputs, cpp_sha256=digest(directory / 'src/analyzer.cpp'), hpp_sha256=digest(directory / 'src/analyzer.hpp'),
                     binary_sha256=digest(directory / 'pair'), regression_sha256=digest(directory / 'regression'), regression_passed=True)
        atomic_json(checkpoint, state)
    atomic_json(directory.parent / 'current.json', dict(build=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
