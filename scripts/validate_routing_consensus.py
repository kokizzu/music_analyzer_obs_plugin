#!/usr/bin/env python3
"""Replay known regressions, mixtures and frozen fresh recording-disjoint controls."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess

from measure_routing_consensus import inspect_frames, load_build
from routing_duration_baseline import ROOT, atomic_json, digest


def source_filename(row):
    match = re.search(r'(?:^|,)filename=([^,]+)', row.get('qualities', ''))
    return match.group(1) if match else row['id']


def selection():
    legacy_path = ROOT / 'build/piano_voice_extensions/ebc264a1f5031e97/report.json'
    legacy = json.loads(legacy_path.read_text())
    assert legacy['complete']
    cases = []
    for sample in legacy['inputs']['cases']:
        entry = legacy['recordings'][sample['id']]
        kind = sample['kind']
        cases.append(dict(id='regression-' + sample['id'], kind=kind, fresh=False, rate=entry['rate'],
                          raw=str((legacy_path.parent / (sample['id'] + '.f32')).relative_to(ROOT)), raw_sha256=entry['raw_sha256'],
                          reference=str((legacy_path.parent / (sample['id'] + '.tsv')).relative_to(ROOT)), reference_sha256=entry['sha256'],
                          protect_guitar=kind == 'poly-guitar' or kind.startswith('real-voice-mixture'),
                          protect_voice=sample['protect_voice'] and kind != 'poly-guitar'))
    known_audio = set()
    provenance = {str(legacy_path.relative_to(ROOT)): digest(legacy_path)}
    old_path = ROOT / 'build/next_piano_timbre/cdf899eac5ec/checkpoint.json'
    old = json.loads(old_path.read_text())
    provenance[str(old_path.relative_to(ROOT))] = digest(old_path)
    known_ids = {sample['id'] for sample in old['selection']}
    for relative in ('build/routing_controls/84b9eb144888ea8d/report.json',
                     'build/routing_guitarset_controls/9801a45ca6c823e8/report.json',
                     'build/routing_duration_baseline/f3c7f7a446eed267/report.json'):
        path = ROOT / relative
        report = json.loads(path.read_text())
        provenance[relative] = digest(path)
        for sample in report.get('inputs', {}).get('selection', report.get('selection', [])):
            known_ids.add(sample['id'])
            known_audio.add(sample['audio_sha256'])
    known_audio.update(sample['audio_sha256'] for sample in legacy['inputs']['cases'])
    base = ROOT / 'build/maestro_real_samples'
    manifest = base / 'maestro-v3.0.0.csv'
    provenance[str(manifest.relative_to(ROOT))] = digest(manifest)
    with manifest.open() as stream:
        pianos = list(csv.DictReader(stream))[12:16]
    assert len(pianos) == 4
    for index, row in enumerate(pianos, 13):
        audio, midi = base / row['audio_filename'], base / row['midi_filename']
        assert digest(audio) not in known_audio
        for rate in (None, 48000):
            cases.append(dict(id='fresh-piano-' + str(index) + ('-48k' if rate else '-original'), kind='piano', fresh=True,
                              audio=str(audio.relative_to(ROOT)), audio_sha256=digest(audio), target_rate=rate, seconds=60,
                              midi=str(midi.relative_to(ROOT)), midi_sha256=digest(midi), protect_guitar=False, protect_voice=False))
    paths = sorted((ROOT / 'build/guitarset').glob('05_*_comp_mic.wav'), key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())
    paths = [path for path in paths if digest(path) not in known_audio][:4]
    assert len(paths) == 4
    for audio in paths:
        for rate in (None, 48000):
            cases.append(dict(id='fresh-' + audio.stem + ('-48k' if rate else '-original'), kind='poly-guitar', fresh=True,
                              audio=str(audio.relative_to(ROOT)), audio_sha256=digest(audio), target_rate=rate, seconds=10,
                              protect_guitar=True, protect_voice=False))
    manifests = [ROOT / 'build/vocalset_samples/manifest.tsv', ROOT / 'build/vocalset_samples_expanded/manifest.tsv']
    known_recordings = set()
    available = []
    for manifest in manifests:
        provenance[str(manifest.relative_to(ROOT))] = digest(manifest)
        with manifest.open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        known_recordings.update(source_filename(row) for row in rows if row['id'] in known_ids)
        if 'expanded' in str(manifest):
            available = [(row, manifest.parent / row['path']) for row in rows]
    used_recordings = set(known_recordings)
    singers = ['f' + str(i) for i in range(1, 10)] + ['m' + str(i) for i in range(1, 12)]
    for singer in singers:
        selected = []
        for row, audio in sorted(available, key=lambda pair: hashlib.sha256(pair[0]['id'].encode()).hexdigest()):
            if not row['id'].startswith('vocalset_' + singer + '_') or source_filename(row) in used_recordings:
                continue
            if digest(audio) in known_audio:
                continue
            selected.append((row, audio))
            used_recordings.add(source_filename(row))
            if len(selected) == 2:
                break
        assert len(selected) == 2, 'Need two unused source recordings per singer: ' + singer
        for row, audio in selected:
            for rate in (None, 48000):
                cases.append(dict(id='fresh-' + row['id'] + ('-48k' if rate else '-original'), kind='isolated-voice', fresh=True,
                                  audio=str(audio.relative_to(ROOT)), audio_sha256=digest(audio), target_rate=rate, seconds=4,
                                  source_recording=source_filename(row), protect_guitar=False, protect_voice=True))
    assert len(cases) == 260 and len({sample['id'] for sample in cases}) == len(cases)
    return cases, provenance


def prepare(sample, directory):
    if not sample['fresh']:
        raw = ROOT / sample['raw']
        assert digest(raw) == sample['raw_sha256']
        return raw, sample['rate']
    assert digest(ROOT / sample['audio']) == sample['audio_sha256']
    info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
        'stream=sample_rate,channels,duration', '-of', 'json', str(ROOT / sample['audio'])], text=True, capture_output=True, check=True).stdout)['streams'][0]
    rate, channels = sample['target_rate'] or int(info['sample_rate']), int(info['channels'])
    assert channels in (1, 2)
    raw = directory / (sample['id'] + '.f32')
    command = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1', '-filter_threads', '1',
               '-i', str(ROOT / sample['audio']), '-t', str(sample['seconds'])]
    if channels == 2:
        command += ['-af', 'pan=mono|c0=0.5*c0+0.5*c1']
    subprocess.run(command + ['-ac', '1', '-ar', str(rate), '-f', 'f32le', str(raw)], check=True)
    assert abs(raw.stat().st_size // 4 - round(min(float(info['duration']), sample['seconds']) * rate)) <= 2
    return raw, rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=2)
    args = parser.parse_args()
    assert 0 <= args.shard < args.shards
    build_path, build = load_build()
    cases, provenance = selection()
    inputs = dict(build_sha256=digest(build_path), cases=cases, provenance=provenance,
                  shards=args.shards,
                  script_sha256=digest(Path(__file__)), helper_sha256=digest(ROOT / 'scripts/measure_routing_consensus.py'),
                  ffmpeg_version=subprocess.run(['ffmpeg', '-version'], text=True, capture_output=True, check=True).stdout.splitlines()[0])
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_consensus_extensions' / key
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / 'plan.json').exists():
        assert json.loads((directory / 'plan.json').read_text()) == inputs
    else:
        atomic_json(directory / 'plan.json', inputs)
    print('Frozen plan', directory.relative_to(ROOT), 'cases', len(cases), 'fresh', sum(sample['fresh'] for sample in cases), flush=True)
    if args.plan:
        return
    with (directory / ('capture-' + str(args.shard) + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        checkpoint = directory / ('report-' + str(args.shard) + '.json')
        state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs_sha256=digest(directory / 'plan.json'),
            shard=args.shard, shards=args.shards, recordings={}, complete=False, passed=False)
        assert state['inputs_sha256'] == digest(directory / 'plan.json') and state['shards'] == args.shards
        for sample in cases[args.shard::args.shards]:
            destination = directory / (sample['id'] + '.tsv')
            if sample['id'] in state['recordings']:
                assert digest(destination) == state['recordings'][sample['id']]['sha256']
                continue
            raw, rate = prepare(sample, directory)
            pending = destination.with_suffix('.pending.tsv')
            subprocess.run([str(build_path.parent / 'pair'), str(raw), str(rate), str(pending)], check=True, timeout=3600)
            pending.replace(destination)
            expected = None
            if 'reference' in sample:
                reference = ROOT / sample['reference']
                assert digest(reference) == sample['reference_sha256']
                with reference.open() as stream:
                    expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
            result = inspect_frames(destination, rate, poly=sample['protect_guitar'], expected=expected)
            if sample['protect_voice']:
                result['protected_voice_changes'] = result['voice_removed']
            assert result['windows'] == raw.stat().st_size // 4 // int(rate * .05 + .5)
            result.update(kind=sample['kind'], fresh=sample['fresh'], rate=rate, raw_sha256=digest(raw))
            state['recordings'][sample['id']] = result
            atomic_json(checkpoint, state)
            print(sample['id'], 'removed G/V', result['guitar_removed'], result['voice_removed'],
                  'protected changes', result['protected_guitar_changes'], result['protected_voice_changes'], flush=True)
        assert digest(Path(__file__)) == inputs['script_sha256']
        state['complete'] = True
        state['passed'] = not any(row['protected_guitar_changes'] or row['protected_voice_changes'] or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
        atomic_json(checkpoint, state)
        print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
        assert state['passed']


if __name__ == '__main__':
    main()
