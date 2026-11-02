#!/usr/bin/env python3
"""Freeze and replay four recording-disjoint performances for multiwindow low-note suppression."""
import argparse
import array
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from publish_next_detection import git
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge, score


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--record', type=int, choices=range(21, 25))
    args = parser.parse_args()
    assert args.freeze != bool(args.record)
    pointer = read(ROOT / 'build/multiscale_low_keyboard_native/current.json')
    build_path = ROOT / pointer['build']
    build = read(build_path)
    assert digest(build_path) == pointer['sha256'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    parent = ROOT / 'build/multiscale_low_keyboard_fresh'
    parent.mkdir(parents=True, exist_ok=True)
    if args.freeze:
        phases = {}
        for phase in ('training', 'calibration'):
            ref = read(ROOT / 'build/multiscale_low_keyboard_measurement' / ('current-' + phase + '.json'))
            path = ROOT / ref['report']
            report = read(path)
            assert digest(path) == ref['sha256'] and report['complete'] and report['passed']
            assert report['inputs']['build_sha256'] == digest(build_path)
            assert report['inputs']['driver_sha256'] == digest(ROOT / 'scripts/measure_multiscale_low_keyboard.py')
            for name, entry in report['recordings'].items():
                assert digest(path.parent / (name + '.tsv')) == entry['sha256']
                assert not entry['deltas']['unsupported_added_seconds'] and not entry['deltas']['surviving_cell_changed_frames']
                assert entry['after']['matched_attacks'] >= entry['before']['matched_attacks']
            phases[phase] = ref
        base = ROOT / 'build/maestro_real_samples'
        manifest = base / 'maestro-v3.0.0.csv'
        with manifest.open() as stream:
            rows = list(csv.DictReader(stream))
        previous_audio = {digest(base / r['audio_filename']) for r in rows[:20]}
        previous_midi = {digest(base / r['midi_filename']) for r in rows[:20]}
        baseline = read(ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json')
        previous_audio.update(s['audio_sha256'] for s in baseline['selection'])
        previous_midi.update(s['midi_sha256'] for s in baseline['selection'])
        selection = []
        for number, row in enumerate(rows[20:24], 21):
            audio, midi = base / row['audio_filename'], base / row['midi_filename']
            a, m = digest(audio), digest(midi)
            assert a not in previous_audio and m not in previous_midi, 'Fresh performance overlaps prior evaluation'
            selection.append(dict(id='fresh-' + str(number), number=number, audio=str(audio.relative_to(ROOT)), midi=str(midi.relative_to(ROOT)), audio_sha256=a, midi_sha256=m))
        assert len({s['audio_sha256'] for s in selection}) == len({s['midi_sha256'] for s in selection}) == 4
        primary = ROOT / 'build/routing_consensus_rollout/682b938120772cd4'
        rollout = read(primary / 'report.json')
        assert digest(primary / 'replay') == rollout['binary_sha256']
        for name in ('analyzer.cpp', 'analyzer.hpp'):
            assert git('show', 'HEAD:src/' + name) == (primary / 'src' / name).read_text()
        frozen = dict(build=str(build_path.relative_to(ROOT)), build_sha256=digest(build_path), phases=phases,
                      script_sha256=digest(Path(__file__)), selection=selection, manifest_sha256=digest(manifest),
                      primary_binary_sha256=digest(primary / 'replay'), source_cpp_sha256=digest(primary / 'src/analyzer.cpp'),
                      scorer_sha256=digest(ROOT / 'scripts/routing_duration_score.py'),
                      midi_reader_sha256=digest(ROOT / 'scripts/midi_sustain_reference.py'),
                      parameters='100/400 ms union, .01 fundamental-or-third, original-display latch, three prior hops', seconds=60,
                      protocol='Disjoint from known first-20 evaluation recording IDs 21-24, original rate and causal endpoints. Report key-held, actual pedal-only and tolerance-only removals separately. Require no supported removals or attack/protected/unrelated regressions; benefit assessed across all four recordings.')
        key = hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()[:16]
        path = parent / ('frozen-' + key + '.json')
        if path.exists():
            assert read(path) == frozen
        else:
            atomic_json(path, frozen)
        atomic_json(parent / 'current-frozen.json', dict(path=str(path.relative_to(ROOT)), sha256=digest(path)))
        print('Frozen multiwindow candidate and four fresh recordings:', path.relative_to(ROOT), flush=True)
        return
    pointer = read(parent / 'current-frozen.json')
    frozen_path = ROOT / pointer['path']
    frozen = read(frozen_path)
    assert digest(frozen_path) == pointer['sha256'] and frozen['build_sha256'] == digest(build_path)
    assert frozen['script_sha256'] == digest(Path(__file__))
    assert frozen['scorer_sha256'] == digest(ROOT / 'scripts/routing_duration_score.py')
    assert frozen['midi_reader_sha256'] == digest(ROOT / 'scripts/midi_sustain_reference.py')
    sample = next(s for s in frozen['selection'] if s['number'] == args.record)
    directory = parent / frozen_path.stem / sample['id']
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        audio = ROOT / sample['audio']
        assert digest(audio) == sample['audio_sha256']
        raw = directory / 'prefix.f32'
        with wave.open(str(audio), 'rb') as stream:
            assert stream.getsampwidth() == 2 and stream.getcomptype() == 'NONE'
            rate, channels = stream.getframerate(), stream.getnchannels()
            pcm = array.array('h', stream.readframes(rate * frozen['seconds']))
        if sys.byteorder != 'little':
            pcm.byteswap()
        mono = array.array('f', (sum(pcm[i:i+channels]) / (32768 * channels) for i in range(0, len(pcm), channels)))
        hop = round(rate * .05)
        del mono[len(mono)//hop*hop:]
        assert len(mono) >= rate * 20
        with raw.open('wb') as stream:
            mono.tofile(stream)
        primary = ROOT / 'build/routing_consensus_rollout/682b938120772cd4/replay'
        assert digest(primary) == frozen['primary_binary_sha256']
        for binary, target in ((primary, directory / 'primary.tsv'), (build_path.parent / 'pair', directory / 'pair.tsv')):
            subprocess.run([str(binary), str(raw), str(rate), str(target)], check=True, timeout=3600)
        with (directory / 'primary.tsv').open() as stream:
            reference = list(csv.DictReader(stream, delimiter='\t'))
        with (directory / 'pair.tsv').open() as stream:
            frames = list(csv.DictReader(stream, delimiter='\t'))
        assert len(frames) == len(reference) == len(mono) // hop
        midi = ROOT / sample['midi']
        assert digest(midi) == sample['midi_sha256']
        notes = read_intervals(midi.read_bytes())
        held, sounding, allowed = {}, {}, {}
        for note in notes:
            if note['channel'] != 9:
                held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
                sounding.setdefault(note['midi'], []).append((note['start'], note['end']))
                allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held, sounding, allowed = ({m: merge(v) for m, v in d.items()} for d in (held, sounding, allowed))
        deltas = dict(held_removed=0., pedal_only_removed=0., grace_only_removed=0., unsupported_removed=0., added=0, removed=0, held_added=0., pedal_only_added=0., grace_only_added=0., unsupported_added=0., unrelated=0, tempo=0, survivor=0)
        after_frames = []
        horizon = len(mono) / rate
        for row, expected in zip(frames, reference):
            assert all(row[k] == expected['after_' + k if k in ('guitar', 'voice') else k] for k in ('end_sample', 'keys', 'guitar', 'voice', 'bass', 'other', 'ambiguous', 'chord', 'drums', 'bpm', 'confidence'))
            before, after = ({int(v) for v in row[k].split(',') if v} for k in ('keys', 'after_keys'))
            deltas['removed'] += len(before - after)
            deltas['unrelated'] += bool(row['unrelated_difference'])
            deltas['tempo'] += row['bpm_changed'] != '0'
            deltas['survivor'] += row['survivor_changed'] != '0'
            start, end = int(row['end_sample']) / rate, min(horizon, int(row['end_sample']) / rate + .05)
            for m in before - after:
                h, s, a = (coverage(d.get(m, []), start, end) for d in (held, sounding, allowed))
                deltas['held_removed'] += h
                deltas['pedal_only_removed'] += max(0., s-h)
                deltas['grace_only_removed'] += max(0., a-s)
                deltas['unsupported_removed'] += max(0., end-start-a)
            for m in after - before:
                h, s, a = (coverage(d.get(m, []), start, end) for d in (held, sounding, allowed))
                deltas['added'] += 1
                deltas['held_added'] += h
                deltas['pedal_only_added'] += max(0., s - h)
                deltas['grace_only_added'] += max(0., a - s)
                deltas['unsupported_added'] += max(0., end - start - a)
            after_frames.append(dict(row, keys=row['after_keys']))
        before, after = (score(rows, notes, rate)['keys'] for rows in (frames, after_frames))
        maximum = max(float(r['after_ms']) for r in frames)
        passed = not any(deltas[k] for k in ('added', 'unrelated', 'tempo', 'survivor')) and deltas['held_removed']+deltas['pedal_only_removed']+deltas['grace_only_removed'] < 1e-8 and deltas['unsupported_added'] < 1e-8 and after['matched_attacks'] >= before['matched_attacks'] and maximum < 50
        report = dict(frozen_sha256=digest(frozen_path), sample=sample, rate=rate, windows=len(frames), deltas=deltas,
                      before=before, after=after, maximum_after_ms=maximum, passed=passed, complete=True,
                      artifacts={str(p.relative_to(ROOT)): digest(p) for p in (raw, directory / 'primary.tsv', directory / 'pair.tsv')})
        atomic_json(directory / 'report.json', report)
        print(sample['id'], json.dumps(deltas), 'attacks', before['matched_attacks'], after['matched_attacks'], 'passed', passed, flush=True)
        assert passed


if __name__ == '__main__':
    main()
