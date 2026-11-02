#!/usr/bin/env python3
"""Build unmodified primary analysis sources and score fixed aligned recordings."""
import argparse
import array
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import wave

from midi_sustain_reference import read_intervals
from measure_sustained_analyzer import summarize
from publish_next_detection import git, identity
from routing_duration_score import score

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def primary_build():
    identity()
    head = git('rev-parse', 'HEAD').strip()
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1, 'Need one existing local runtime SDK; no download is performed'
    harness = git('show', 'HEAD:tests/analyzer_sustained.cpp')
    changes = [('configure_diagnostic_rows(settings, 0);', 'settings.input_mode = mao::AnalysisInputMode::FullMix;'),
               ('other\\tdrums', 'other\\tambiguous\\tdrums'),
               ("<< notes(snapshot.vocal_notes) << '\\t' << notes(snapshot.other_notes) << '\\t' << drums", "<< notes(snapshot.vocal_notes) << '\\t' << notes(snapshot.other_notes) << '\\t' << notes(snapshot.ambiguous_notes) << '\\t' << drums")]
    for before, after in changes:
        assert harness.count(before) == 1, 'Review changed primary harness interface: ' + before
        harness = harness.replace(before, after, 1)
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(),
                  vendor_tree=git('rev-parse', 'HEAD:third_party').strip(),
                  harness_sha256=hashlib.sha256(harness.encode()).hexdigest(),
                  sdk_headers={p.name: digest(p) for p in sorted(sdk[0].parent.glob('*.h'))},
                  compiler=subprocess.run(['g++', '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
                  flags='-O2 -std=c++17; default native settings; FullMix; 100ms/50ms')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_duration_primary' / key
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'replay') == state['binary_sha256']
        return directory, state
    directory.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(['git', 'archive', head, 'src', 'third_party'], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(directory, filter='data')
    (directory / 'replay.cpp').write_text(harness)
    vendor = directory / 'third_party/beat_and_tempo_tracking'
    objects = []
    for source in sorted((vendor / 'src').glob('*.c')):
        output = directory / (source.stem + '.o')
        subprocess.run(['cc', '-O2', '-I' + str(vendor), '-c', str(source), '-o', str(output)], check=True)
        objects.append(str(output))
    for name in ('basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history', 'analyzer'):
        output = directory / (name + '.o')
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent), '-I' + str(vendor),
                        '-c', str(directory / 'src' / (name + '.cpp')), '-o', str(output)], check=True)
        objects.append(str(output))
    binary = directory / 'replay'
    subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), str(directory / 'replay.cpp'),
                    *objects, '-lm', '-pthread', '-ldl', '-o', str(binary)], check=True)
    state = dict(inputs=inputs, source_commit=head, binary_sha256=digest(binary))
    atomic_json(checkpoint, state)
    print('Built primary replay', directory.relative_to(ROOT), flush=True)
    return directory, state


def selection():
    selected = []
    # Freeze deterministic recording selection before examining analyzer output.
    # Folder names are not proof of independent dataset provenance.
    for cohort, folder, begin in (('training', 'maps_piano_samples', 0), ('heldout', 'maestro_real_samples', 4)):
        base = ROOT / 'build' / folder
        manifest = base / 'maestro-v3.0.0.csv'
        with manifest.open() as stream:
            rows = list(csv.DictReader(stream))[begin:begin + 4]
        assert len(rows) == 4, 'Need four complete aligned recordings per cohort'
        for index, row in enumerate(rows, 1):
            wav, midi = base / row['audio_filename'], base / row['midi_filename']
            selected.append(dict(id=cohort + '-' + str(index), cohort=cohort,
                                 audio=str(wav.relative_to(ROOT)), midi=str(midi.relative_to(ROOT)),
                                 audio_sha256=digest(wav), midi_sha256=digest(midi), manifest_sha256=digest(manifest)))
    assert len({row['audio_sha256'] for row in selected}) == len(selected), 'Duplicate recording'
    train_midi = {row['midi_sha256'] for row in selected if row['cohort'] == 'training'}
    assert not train_midi & {row['midi_sha256'] for row in selected if row['cohort'] == 'heldout'}, 'Performance leakage across cohorts'
    return selected


def measure(directory, build):
    selected = selection()
    inputs = {name: digest(ROOT / name) for name in ('scripts/routing_duration_baseline.py', 'scripts/routing_duration_score.py',
              'scripts/midi_sustain_reference.py', 'scripts/measure_sustained_analyzer.py')}
    key = hashlib.sha256(json.dumps([build, selected, inputs, 60], sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_duration_baseline' / key
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / 'report.json'
    report = json.loads(report_path.read_text()) if report_path.exists() else dict(
        build=build, build_directory=str(directory.relative_to(ROOT)), selection=selected, inputs=inputs,
        recordings={}, complete=False, scope='Recording-disjoint aligned piano prefixes, original PCM rate; collection provenance not independently established; no learned worker or hardware capture')
    assert report['build'] == build and report['selection'] == selected and report['inputs'] == inputs
    atomic_json(report_path, report)
    prefix_hashes = set()
    for sample in selected:
        wav = ROOT / sample['audio']
        raw, frames_path = output / (sample['id'] + '.f32'), output / (sample['id'] + '.tsv')
        with wave.open(str(wav), 'rb') as audio:
            assert audio.getsampwidth() == 2 and audio.getcomptype() == 'NONE', 'Original PCM16 WAV required'
            rate, channels = audio.getframerate(), audio.getnchannels()
            values = array.array('h', audio.readframes(min(audio.getnframes(), rate * 60)))
        if sys.byteorder != 'little':
            values.byteswap()
        mono = array.array('f', (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
        assert len(mono) / rate >= 20, 'Never loop or substitute short clips'
        if sys.byteorder != 'little':
            mono.byteswap()
        raw.write_bytes(mono.tobytes())
        prefix_digest = digest(raw)
        assert prefix_digest not in prefix_hashes, 'Duplicate PCM prefix'
        prefix_hashes.add(prefix_digest)
        if sample['id'] in report['recordings']:
            assert digest(frames_path) == report['recordings'][sample['id']]['frames_sha256']
        else:
            subprocess.run([str(directory / 'replay'), str(raw), str(rate), str(frames_path), 'throughput', 'native'], check=True, timeout=1800)
        with frames_path.open() as stream:
            frames = list(csv.DictReader(stream, delimiter='\t'))
        assert len(frames) == len(mono) // int(rate * .05 + .5)
        intervals = read_intervals((ROOT / sample['midi']).read_bytes())
        metrics = score(frames, intervals, rate)
        assert metrics['keys']['held_note_seconds'] > 0, 'No aligned held-key labels in prefix'
        report['recordings'][sample['id']] = dict(frames_sha256=digest(frames_path), prefix_sha256=prefix_digest,
                                               rate=rate, duration=metrics, timing=summarize(frames, rate))
        assert digest(wav) == sample['audio_sha256'] and digest(ROOT / sample['midi']) == sample['midi_sha256']
        atomic_json(report_path, report)
        print(sample['id'], json.dumps(dict(missing=metrics['keys']['missing_note_seconds'],
              attacks_missed=metrics['keys']['missed_attacks'], foreign=metrics['foreign_rows'])), flush=True)
    assert all(digest(ROOT / path) == checksum for path, checksum in inputs.items())
    assert digest(directory / 'replay') == build['binary_sha256']
    report['complete'] = True
    atomic_json(report_path, report)
    print(report_path.relative_to(ROOT), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--measure', action='store_true')
    args = parser.parse_args()
    directory, build = primary_build()
    if args.measure:
        measure(directory, build)


if __name__ == '__main__':
    main()
