#!/usr/bin/env python3
"""Attribute final Keyboard timing errors to native post-smoothing mutations."""
import csv
import fcntl
import hashlib
import io
import json
from itertools import groupby
from pathlib import Path
import re
import subprocess
import tarfile

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def attribute(events, final):
    active, initial, origins, removed = set(), set(), {}, {}
    for sequence, row in enumerate(events):
        assert int(row['sequence']) == sequence
        midi = int(row['midi'])
        if midi < 0:
            assert sequence == 0 and row['stage'] == 'frame'
            continue
        before, after = float(row['before']) > 0, float(row['after']) > 0
        assert before == (midi in active) and before != after, 'Broken trace transition chain'
        stage = ('between:' if row['between'] == '1' else '') + row['stage']
        if row['stage'] == 'initial':
            initial.add(midi)
            stage = 'smoothed'
        if after:
            active.add(midi)
            origins[midi] = stage
        else:
            active.remove(midi)
            origins.pop(midi)
            removed[midi] = stage
    assert active == final, 'Trace does not reconstruct actual final display'
    return initial, origins, removed


def build():
    identity()
    assets = ['tests/keyboard_stage_trace.hpp', 'tests/keyboard_stage_trace.cpp']
    base = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    objects = [base / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(), assets={p: digest(ROOT / p) for p in assets},
                  objects={str(p.relative_to(ROOT)): digest(p) for p in objects}, script_sha256=digest(Path(__file__)),
                  compiler=subprocess.run(['g++', '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
                  sdk_headers={p.name: digest(p) for p in sorted(sdk[0].parent.glob('*.h'))})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/keyboard_stage_trace' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    with (directory / 'build.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if checkpoint.exists():
            state = json.loads(checkpoint.read_text())
            assert state['inputs'] == inputs and digest(directory / 'replay') == state['binary_sha256']
            return directory, state
        archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(directory, filter='data')
        cpp = (directory / 'src/analyzer.cpp').read_text()
        begin = cpp.index('void append_full_mix_low_keyboard_candidates(')
        end = cpp.index('\n}', begin) + 2
        block = cpp[begin:end]
        anchor = '\t\tconst bool harmonic_supported_peak = harmonic_supported_level >= strongest_note_level * 0.18f;'
        assert block.count(anchor) == 1
        block = block.replace(anchor, anchor + '\n\t\tmao_stage_trace::state.low[static_cast<std::size_t>(midi - kFirstMidi)] =\n'
                              '\t\t\t{raw_note_level, adjacent_note_level, strongest_note_level, harmonic_supported_level, partial_count, true};', 1)
        cpp = cpp[:begin] + block + cpp[end:]
        pattern = re.compile(r'(?m)^(?:void|bool)\s+(\w+)\(([^;{}]*?)\)\s*\n\{')
        inserts, functions = [], []
        for match in pattern.finditer(cpp):
            parameters = []
            for parameter in re.finditer(r'\bNoteGrid\s*&\s*(\w+)', match[2]):
                if not match[2][:parameter.start()].rstrip().endswith('const'):
                    parameters.append(parameter[1])
            if not parameters:
                continue
            functions.append(match[1])
            inserts.append((match.end(), ''.join('\n\tmao_stage_trace::Scope mao_stage_scope_' + str(i) + '(' + name + ', __func__);'
                                                for i, name in enumerate(parameters))))
        assert all(name in functions for name in ('smooth_note_grid_envelope', 'write_note_grid_cell', 'clear_note_grid_midi', 'attenuate_note_grid_display_by_candidates'))
        for index, text in reversed(inserts):
            cpp = cpp[:index] + text + cpp[index:]
        cpp = cpp.replace('#include "analyzer.hpp"', '#include "analyzer.hpp"\n#include "keyboard_stage_trace.hpp"', 1)
        anchor = 'mixed_source ? &mixed_keyboard_display_candidates : nullptr);\n\t\tif (!mixed_source)'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, 'mixed_source ? &mixed_keyboard_display_candidates : nullptr);\n'
                          '\t\tmao_stage_trace::state.start(snapshot.keyboard_notes);\n\t\tif (!mixed_source)', 1)
        (directory / 'src/analyzer.cpp').write_text(cpp)
        (directory / 'src/keyboard_stage_trace.hpp').write_bytes((ROOT / assets[0]).read_bytes())
        (directory / 'replay.cpp').write_bytes((ROOT / assets[1]).read_bytes())
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent), '-I' + str(base / 'third_party/beat_and_tempo_tracking'),
                        '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), str(directory / 'replay.cpp'),
                        str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'replay')], check=True)
        state = dict(inputs=inputs, functions=functions, binary_sha256=digest(directory / 'replay'), cpp_sha256=digest(directory / 'src/analyzer.cpp'))
        atomic_json(checkpoint, state)
        print('Instrumented', len(functions), 'native grid mutators', flush=True)
        return directory, state


def main():
    directory, build_state = build()
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(directory, build_state)


def capture(directory, build_state):
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    references = ROOT / 'build/routing_consensus_pair/e63350f9b5113f8b'
    reference_report = json.loads((references / 'report.json').read_text())
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(build=build_state, baseline_sha256=digest(baseline_path),
              reference_sha256=digest(references / 'report.json'), recordings={}, complete=False)
    assert state['build'] == build_state and state['baseline_sha256'] == digest(baseline_path)
    for sample in baseline['selection']:
        if sample['cohort'] != 'training' or sample['id'] == 'training-4':
            continue
        name = sample['id']
        raw, frames_path, trace_path = (baseline_path.parent / (name + '.f32'), directory / (name + '.frames.tsv'), directory / (name + '.trace.tsv'))
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        rate = baseline['recordings'][name]['rate']
        if name not in state['recordings']:
            subprocess.run([str(directory / 'replay'), str(raw), str(rate), str(frames_path), str(trace_path)], check=True, timeout=3600)
        else:
            assert digest(frames_path) == state['recordings'][name]['frames_sha256'] and digest(trace_path) == state['recordings'][name]['trace_sha256']
        reference = references / ('piano-' + name + '.tsv')
        assert digest(reference) == reference_report['recordings']['piano-' + name]['sha256']
        with frames_path.open() as stream, reference.open() as original:
            frames, expected = list(csv.DictReader(stream, delimiter='\t')), list(csv.DictReader(original, delimiter='\t'))
        assert len(frames) == len(expected) == 1200
        for row, before in zip(frames, expected):
            assert all(row[key] == before['after_' + key if key in ('guitar', 'voice') else key] for key in row), 'Observer changed primary output'
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        held, allowed = {}, {}
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel'] != 9:
                held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
                allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held, allowed = ({midi: merge(values) for midi, values in mapping.items()} for mapping in (held, allowed))
        metrics, endpoint_rows, low_cases = {}, {row['end_sample']: row for row in frames}, []
        seen = set()
        with trace_path.open() as stream:
            for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                assert endpoint in endpoint_rows and endpoint not in seen
                seen.add(endpoint)
                final = {int(v) for v in endpoint_rows[endpoint]['keys'].split(',') if v}
                events = list(group)
                initial, origins, removed = attribute(events, final)
                evidence = {int(event['midi']): event for event in events if int(event['midi']) >= 0}
                start, end = int(endpoint) / rate, min(60., int(endpoint) / rate + .05)
                def metric(stage):
                    return metrics.setdefault(stage, dict(final_cells=0, final_unsupported_seconds=0., postprocess_added_held_seconds=0.,
                                                          smoothed_held_removed_seconds=0., smoothed_supported_removed_seconds=0.))
                for midi in final:
                    entry = metric(origins[midi])
                    entry['final_cells'] += 1
                    entry['final_unsupported_seconds'] += max(0., end - start - coverage(allowed.get(midi, []), start, end))
                    entry['postprocess_added_held_seconds'] += coverage(held.get(midi, []), start, end) if midi not in initial else 0.
                    if origins[midi] == 'write_note_grid_cell' and end > start:
                        detail = evidence[midi]
                        assert detail['considered'] == '1' and float(detail['strongest']) > 0
                        low_cases.append(dict(end_sample=int(endpoint), midi=midi,
                            direct=float(detail['direct']), adjacent=float(detail['adjacent']), strongest=float(detail['strongest']),
                            harmonic=float(detail['harmonic']), partials=int(detail['partials']),
                            held_seconds=coverage(held.get(midi, []), start, end), supported_seconds=coverage(allowed.get(midi, []), start, end),
                            unsupported_seconds=max(0., end - start - coverage(allowed.get(midi, []), start, end))))
                for midi in initial - final:
                    entry = metric(removed[midi])
                    entry['smoothed_held_removed_seconds'] += coverage(held.get(midi, []), start, end)
                    entry['smoothed_supported_removed_seconds'] += coverage(allowed.get(midi, []), start, end)
        assert seen == set(endpoint_rows)
        assert abs(sum(value['final_unsupported_seconds'] for value in metrics.values()) - baseline['recordings'][name]['duration']['keys']['annotation_unsupported_note_seconds']) < 1e-7
        state['recordings'][name] = dict(metrics=metrics, low_cases=low_cases, frames_sha256=digest(frames_path), trace_sha256=digest(trace_path), windows=len(frames))
        atomic_json(checkpoint, state)
        print(name, json.dumps(sorted(metrics.items(), key=lambda item: item[1]['final_unsupported_seconds'], reverse=True)[:8]), flush=True)
    assert digest(directory / 'replay') == build_state['binary_sha256']
    state['complete'] = True
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
