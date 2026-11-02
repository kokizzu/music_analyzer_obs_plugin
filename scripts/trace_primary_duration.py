#!/usr/bin/env python3
"""Trace raw/smoothed/final Keyboard stages in an isolated primary export."""
import csv
import fcntl
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def build():
    identity()
    baseline = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    cpp = git('show', 'HEAD:src/analyzer.cpp')
    objects = [baseline / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(),
                  assets={p: digest(ROOT / p) for p in ('tests/primary_duration_trace.cpp', 'tests/primary_duration_trace.hpp')},
                  objects={str(p.relative_to(ROOT)): digest(p) for p in objects},
                  sdk_headers={p.name: digest(p) for p in sorted(sdk[0].parent.glob('*.h'))},
                  compiler=subprocess.run(['g++', '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
                  script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/primary_duration_trace' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'replay') == state['binary_sha256']
        return directory, state
    archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(directory, filter='data')
    anchor = '#include "analyzer.hpp"'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + '\n#include "primary_duration_trace.hpp"', 1)
    anchor = '\tNoteGrid keyboard_chord_grid = snapshot.keyboard_notes;'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + '\n\tmao_duration_trace::state.raw_keys = snapshot.keyboard_notes;\n\tmao_duration_trace::state.captured_raw = true;', 1)
    anchor = 'mixed_source ? &mixed_keyboard_display_candidates : nullptr);\n\t\tif (!mixed_source)'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, 'mixed_source ? &mixed_keyboard_display_candidates : nullptr);\n'
                      '\t\tmao_duration_trace::state.smoothed_keys = snapshot.keyboard_notes;\n'
                      '\t\tmao_duration_trace::state.tracking = keyboard_note_tracking_;\n'
                      '\t\tmao_duration_trace::state.captured_smoothing = true;\n\t\tif (!mixed_source)', 1)
    (directory / 'src/analyzer.cpp').write_text(cpp)
    (directory / 'src/primary_duration_trace.hpp').write_bytes((ROOT / 'tests/primary_duration_trace.hpp').read_bytes())
    (directory / 'replay.cpp').write_bytes((ROOT / 'tests/primary_duration_trace.cpp').read_bytes())
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent),
                    '-I' + str(baseline / 'third_party/beat_and_tempo_tracking'), '-c', str(directory / 'src/analyzer.cpp'),
                    '-o', str(directory / 'analyzer.o')], check=True)
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), str(directory / 'replay.cpp'),
                    str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'replay')], check=True)
    state = dict(inputs=inputs, binary_sha256=digest(directory / 'replay'), instrumented_cpp_sha256=digest(directory / 'src/analyzer.cpp'))
    atomic_json(checkpoint, state)
    return directory, state


def main():
    directory, built = build()
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(directory, built)


def capture(directory, built):
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(build=built, baseline_sha256=digest(baseline_path), recordings={}, complete=False)
    assert state['build'] == built and state['baseline_sha256'] == digest(baseline_path)
    for sample in baseline['selection']:
        if sample['cohort'] != 'training' or sample['id'] == 'training-4':
            continue
        name = sample['id']
        frames_path, trace_path = directory / (name + '.frames.tsv'), directory / (name + '.trace.tsv')
        if name not in state['recordings']:
            subprocess.run([str(directory / 'replay'), str(baseline_path.parent / (name + '.f32')),
                            str(baseline['recordings'][name]['rate']), str(frames_path), str(trace_path)], check=True, timeout=3600)
        else:
            assert digest(frames_path) == state['recordings'][name]['frames_sha256']
            assert digest(trace_path) == state['recordings'][name]['trace_sha256']
        with frames_path.open() as stream, (baseline_path.parent / (name + '.tsv')).open() as original:
            actual, expected = list(csv.DictReader(stream, delimiter='\t')), list(csv.DictReader(original, delimiter='\t'))
        assert len(actual) == len(expected)
        for row, before in zip(actual, expected):
            assert all(row[column] == before[column] for column in row), 'Instrumentation altered primary output'
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        held, allowed = {}, {}
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel'] != 9:
                held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
                allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held = {midi: merge(values) for midi, values in held.items()}
        allowed = {midi: merge(values) for midi, values in allowed.items()}
        rate = baseline['recordings'][name]['rate']
        horizon = baseline['recordings'][name]['duration']['audio_seconds']
        metrics = dict(raw_absent_missing_held_seconds=0., confirmation_missing_held_seconds=0.,
                       smoothing_selection_missing_held_seconds=0., postprocess_missing_held_seconds=0.,
                       raw_unsupported_seconds=0., smoothed_unsupported_seconds=0., final_unsupported_seconds=0.,
                       postprocess_added_unsupported_seconds=0.)
        count = 0
        with trace_path.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                count += 1
                midi, start = int(row['midi']), int(row['end_sample']) / rate
                end = min(horizon, start + .05)
                overlap = coverage(held.get(midi, []), start, end)
                unsupported = end - start - coverage(allowed.get(midi, []), start, end)
                raw, smoothed, final = (float(row[key]) > 0 for key in ('raw', 'smoothed', 'final'))
                if not final:
                    category = ('postprocess' if smoothed else 'raw_absent' if not raw else
                                'confirmation' if row['confirmed'] == '0' else 'smoothing_selection')
                    metrics[category + '_missing_held_seconds'] += overlap
                for key, active in (('raw', raw), ('smoothed', smoothed), ('final', final)):
                    metrics[key + '_unsupported_seconds'] += unsupported if active else 0
                metrics['postprocess_added_unsupported_seconds'] += unsupported if final and not smoothed else 0
        state['recordings'][name] = dict(metrics=metrics, rows=count, frames_sha256=digest(frames_path), trace_sha256=digest(trace_path))
        atomic_json(checkpoint, state)
        print(name, json.dumps(metrics), flush=True)
    assert digest(directory / 'replay') == built['binary_sha256']
    state['complete'] = True
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
