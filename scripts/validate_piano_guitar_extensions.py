#!/usr/bin/env python3
"""Validate frozen primary-native routing on extended and cross-rate recordings."""
import argparse
import array
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest


def selection(mode):
    cases = []
    if mode in ('original', 'rate48'):
        base = ROOT / 'build/real_note_samples'
        with (base / 'manifest.tsv').open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                if row['family'] != 'guitar':
                    continue
                path = base / row['path']
                cases.append(dict(id=row['id'], kind='single-guitar', midi=int(row['midi']), seconds=4,
                                  audio=str(path.relative_to(ROOT)), audio_sha256=digest(path), target_rate=48000 if mode == 'rate48' else None))
        assert len(cases) == 346
    else:
        for performer in ('03', '04'):
            paths = sorted((ROOT / 'build/guitarset').glob(performer + '_*_comp_mic.wav'), key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())[:4]
            assert len(paths) == 4
            for path in paths:
                for target in (None, 48000):
                    cases.append(dict(id=path.stem + ('-48k' if target else '-original'), kind='poly-guitar', seconds=10,
                                      audio=str(path.relative_to(ROOT)), audio_sha256=digest(path), target_rate=target))
        base = ROOT / 'build/maestro_real_samples'
        with (base / 'maestro-v3.0.0.csv').open() as stream:
            records = list(csv.DictReader(stream))[8:12]
        assert len(records) == 4
        for index, row in enumerate(records, 9):
            path = base / row['audio_filename']
            for target in (None, 48000):
                cases.append(dict(id='piano-reserve-' + str(index) + ('-48k' if target else '-original'), kind='piano', seconds=60,
                                  audio=str(path.relative_to(ROOT)), audio_sha256=digest(path), target_rate=target))
    return cases


def prepare(sample, output):
    path = ROOT / sample['audio']
    raw = output / (sample['id'] + '.original.f32')
    with wave.open(str(path), 'rb') as audio:
        assert audio.getsampwidth() == 2 and audio.getcomptype() == 'NONE'
        rate, channels = audio.getframerate(), audio.getnchannels()
        values = array.array('h', audio.readframes(min(audio.getnframes(), rate * sample['seconds'])))
    if sys.byteorder != 'little':
        values.byteswap()
    mono = array.array('f', (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
    assert len(mono) >= rate * sample['seconds'] - 1, 'Never loop short material'
    if sys.byteorder != 'little':
        mono.byteswap()
    raw.write_bytes(mono.tobytes())
    target = sample['target_rate']
    if target and target != rate:
        converted = output / (sample['id'] + '.derived.f32')
        subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1', '-filter_threads', '1',
                        '-f', 'f32le', '-ar', str(rate), '-ac', '1', '-i', str(raw), '-ar', str(target), '-f', 'f32le', str(converted)], check=True)
        assert abs(converted.stat().st_size // 4 - round(len(mono) * target / rate)) <= 1
        raw, rate = converted, target
    return raw, rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('original', 'rate48', 'reserved'), required=True)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    args = parser.parse_args()
    assert 0 <= args.shard < args.shards
    identity()
    build_path = ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/build.json'
    build = json.loads(build_path.read_text())
    binary = build_path.parent / 'pair'
    assert digest(binary) == build['binary_sha256']
    assert all(digest(ROOT / p) == value for p, value in build['inputs']['assets'].items())
    # This validates exactly the published implementation, not the dirty local
    # analyzer or a silently changed experimental source tree.
    assert hashlib.sha256(git('show', 'HEAD:src/analyzer.cpp').encode()).hexdigest() == build['cpp_sha256']
    assert hashlib.sha256(git('show', 'HEAD:src/analyzer.hpp').encode()).hexdigest() == build['hpp_sha256']
    cases = selection(args.mode)[args.shard::args.shards]
    inputs = dict(build_sha256=digest(build_path), script_sha256=digest(Path(__file__)), cases=cases,
                  mode=args.mode, shard=args.shard, shards=args.shards,
                  conversion='Original PCM downmix; derived 48kHz cases use FFmpeg resampling only, no gain/looping',
                  ffmpeg_version=subprocess.run(['ffmpeg', '-version'], text=True, capture_output=True, check=True).stdout.splitlines()[0])
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/piano_guitar_extensions' / key
    output.mkdir(parents=True, exist_ok=True)
    # Persist the complete selection before observing a single result.
    atomic_json(output / 'plan.json', inputs)
    checkpoint = output / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    atomic_json(checkpoint, state)
    for index, sample in enumerate(cases, 1):
        destination = output / (sample['id'] + '.tsv')
        if sample['id'] in state['recordings']:
            assert digest(destination) == state['recordings'][sample['id']]['sha256']
            continue
        raw, rate = prepare(sample, output)
        subprocess.run([str(binary), str(raw), str(rate), str(destination)], check=True, timeout=1800)
        hop = int(rate * .05 + .5)
        windows = removed_count = losses = 0
        before_times, after_times, examples = [], [], []
        with destination.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                windows += 1
                assert int(row['end_sample']) == windows * hop
                assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
                before, after = ({int(value) for value in row[key].split(',') if value} for key in ('guitar', 'after_guitar'))
                assert after <= before
                removed = before - after
                removed_count += len(removed)
                bad = removed if sample['kind'] == 'poly-guitar' else removed & {sample['midi']} if sample['kind'] == 'single-guitar' else set()
                losses += len(bad)
                if bad and len(examples) < 5:
                    examples.append(dict(end_sample=int(row['end_sample']), pitches=sorted(bad)))
                before_times.append(float(row['before_ms']))
                after_times.append(float(row['after_ms']))
        assert windows == raw.stat().st_size // 4 // hop
        def timing(values):
            ordered = sorted(values)
            return dict(p50=ordered[(len(ordered) - 1) // 2], p99=ordered[int((len(ordered) - 1) * .99)], maximum=ordered[-1],
                        deadline_misses=sum(value > hop / rate * 1000 for value in values))
        entry = dict(kind=sample['kind'], rate=rate, windows=windows, removed=removed_count, correct_or_protected_losses=losses,
                     loss_examples=examples, before_ms=timing(before_times), after_ms=timing(after_times), sha256=digest(destination), prefix_sha256=digest(raw))
        state['recordings'][sample['id']] = entry
        assert digest(ROOT / sample['audio']) == sample['audio_sha256']
        atomic_json(checkpoint, state)
        if index % 20 == 0 or losses or sample['kind'] == 'piano':
            print(index, '/', len(cases), sample['id'], 'removed', removed_count, 'losses', losses, flush=True)
    assert digest(binary) == build['binary_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = not any(row['correct_or_protected_losses'] for row in state['recordings'].values())
    if args.mode == 'reserved':
        state['passed'] &= all(any(row['kind'] == 'piano' and row['removed'] and (row['rate'] == 48000) == derived for row in state['recordings'].values()) for derived in (False, True))
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed'], 'Extended native acceptance gate failed'


if __name__ == '__main__':
    main()
