#!/usr/bin/env python3
"""Compile only the experimental Voice hook on a plain primary-source export.

No branch/worktree, index mutation or replacement of the dirty analyzer occurs.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import argparse

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze-hook', action='store_true')
    args = parser.parse_args()
    asset = ROOT / 'src/experimental_keyboard_voice_hook.inc'
    if args.freeze_hook:
        local = (ROOT / 'src/analyzer.cpp').read_text()
        start = '\tif (mixed_source && vocal_enabled && settings.experimental_keyboard_voice_suppression) {'
        assert local.count(start) == 1
        hook = local[local.index(start):].split('\n#if defined(MAO_ENABLE_BASIC_PITCH)', 1)[0]
        temporary = asset.with_suffix('.tmp')
        temporary.write_text('// Research-only hook: primary replay has no held-out gain; not included by production.\n' + hook)
        temporary.replace(asset)
        print('Frozen research hook', digest(asset))
        return
    head = git('rev-parse', 'HEAD').decode().strip()
    hook = asset.read_text()
    original = git('show', 'HEAD:src/analyzer.cpp').decode()
    header = git('show', 'HEAD:src/analyzer.hpp').decode()
    assert 'experimental_keyboard_voice_suppression' not in original + header
    anchor = '\n\t// Keep the expensive high-tempo hypothesis outside the phase path.'
    assert original.count(anchor) == 1
    candidate = original.replace('#include "analyzer.hpp"', '#include "analyzer.hpp"\n#include "native_mfcc_voice.hpp"', 1)
    candidate = candidate.replace(anchor, '\n' + hook + anchor, 1)
    setting = '\tint tempo_debug_probe_bpm = 0;'
    assert header.count(setting) == 1
    candidate_header = header.replace(setting, setting + '\n\t// Experimental native spectral verification; disabled pending broader evidence.\n\tbool experimental_keyboard_voice_suppression = false;', 1)
    signatures = dict(head=head, hook_sha256=hashlib.sha256(hook.encode()).hexdigest(),
                      script_sha256=digest(Path(__file__)))
    runtime_headers = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(runtime_headers) == 1, 'Need one existing local ONNX Runtime SDK; no download is performed'
    signatures['runtime_header_sha256'] = digest(runtime_headers[0])
    key = hashlib.sha256(json.dumps(signatures, sort_keys=True).encode()).hexdigest()[:12]
    directory = ROOT / 'build/primary_voice_trial' / key
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory / 'src/analyzer.cpp').exists():
        archive = git('archive', 'HEAD', 'src', 'tests', 'third_party')
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(directory, filter='data')
    (directory / 'src/analyzer.cpp').write_text(candidate)
    (directory / 'src/analyzer.hpp').write_text(candidate_header)
    for name in ('native_keyboard_voice_pair.cpp', 'non_tempo_snapshot.hpp'):
        text = (ROOT / 'tests' / name).read_text()
        if name == 'native_keyboard_voice_pair.cpp':
            # Older primary has neither diagnostic-row settings nor PCM
            # correction. Its original mode remains unchanged in both engines.
            text = text.replace('\t\tsettings.enable_vocal_detection = settings.enable_other_detection = true;\n', '')
            text = text.replace('\t\tsettings.experimental_pcm_tempo_correction = false;\n', '')
        else:
            # Compare every grid/state available on this interface. These
            # diagnostics exist only in the older dirty chord experiment.
            if 'keyboard_chord_analysis_notes' not in header:
                text = ''.join(line for line in text.splitlines(True) if '"keyboard_chord_analysis_notes"' not in line)
            if 'keyboard_chord_raw_label' not in header:
                begin = text.index('\tif (std::strcmp(a.keyboard_chord_raw_label')
                end = text.index('\tfor (std::size_t i = 0; i < a.drums.size()', begin)
                text = text[:begin] + text[end:]
        (directory / 'tests' / name).write_text(text)
    build = directory / 'build'
    build.mkdir(exist_ok=True)
    vendor = directory / 'third_party/beat_and_tempo_tracking'
    objects = []
    for source in sorted((vendor / 'src').glob('*.c')):
        output = build / (source.stem + '.o')
        subprocess.run(['cc', '-O2', '-I' + str(vendor), '-c', str(source), '-o', str(output)], check=True)
        objects.append(str(output))
    for name in ('basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history'):
        output = build / (name + '.o')
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(runtime_headers[0].parent),
                        '-c', str(directory / 'src' / (name + '.cpp')), '-o', str(output)], check=True)
        objects.append(str(output))
    analyzer = build / 'analyzer.o'
    subprocess.run(['g++', '-O2', '-std=c++17', '-DMAO_DISABLE_BASIC_PITCH', '-I' + str(directory / 'src'),
                    '-I' + str(vendor), '-c', str(directory / 'src/analyzer.cpp'), '-o', str(analyzer)], check=True)
    binary = build / 'native_keyboard_voice_pair'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), '-I' + str(directory / 'tests'),
                    str(directory / 'tests/native_keyboard_voice_pair.cpp'), str(analyzer), *objects,
                    '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    signatures.update(candidate_cpp_sha256=digest(directory / 'src/analyzer.cpp'),
                      candidate_hpp_sha256=digest(directory / 'src/analyzer.hpp'), binary_sha256=digest(binary))
    (directory / 'checkpoint.json').write_text(json.dumps(signatures, indent=2) + '\n')
    print(directory.relative_to(ROOT))


if __name__ == '__main__':
    main()
