#!/usr/bin/env python3
"""Protect Voice on real mixtures, cross-rate controls and reserved performances."""
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

from routing_duration_baseline import ROOT, atomic_json, digest
from validate_piano_guitar_extensions import selection as reserved_selection


def selection():
    cases = reserved_selection('reserved')
    for case in cases:
        case['protect_voice'] = case['kind'] != 'piano'
    controls_path = ROOT / 'build/routing_controls/84b9eb144888ea8d/report.json'
    controls = json.loads(controls_path.read_text())
    for sample in controls['inputs']['selection']:
        if sample['family'] != 'vocals':
            continue
        cases.append(dict(id=sample['id'] + '-48k', audio=sample['audio'], audio_sha256=sample['audio_sha256'],
                          seconds=4, target_rate=48000, protect_voice=True, kind='isolated-voice-derived'))
    old_path = ROOT / 'build/next_piano_timbre/cdf899eac5ec/checkpoint.json'
    old = json.loads(old_path.read_text())
    for sample in old['selection']:
        if not sample.get('incomplete_pitch_labels'):
            continue
        cases.append(dict(id=sample['id'], audio=sample['original_audio'], audio_sha256=sample['audio_sha256'],
                          seconds=4, target_rate=None, protect_voice=True, kind='real-voice-mixture',
                          labelled_midi=sample['midi'], valid_end_seconds=sample['valid_end_seconds']))
    original = ROOT / 'build/medleydb_vocal_mix_samples/source/LizNelson_Rainfall_MIX.wav'
    for target in (None, 48000):
        cases.append(dict(id='medleydb-rainfall-first60-' + ('48k' if target else 'original'), audio=str(original.relative_to(ROOT)),
                          audio_sha256=digest(original), seconds=60, target_rate=target,
                          protect_voice=True, kind='real-voice-mixture-long'))
    assert len(cases) == 164 and len({case['id'] for case in cases}) == len(cases)
    return cases, {str(p.relative_to(ROOT)): digest(p) for p in (controls_path, old_path)}


def main():
    builds = [(p, json.loads(p.read_text())) for p in (ROOT / 'build/piano_voice_trial').glob('*/build.json')]
    builds = [(p, b) for p, b in builds if all(digest(ROOT / a) == h for a, h in b['inputs']['assets'].items())]
    assert len(builds) == 1
    build_path, build = builds[0]
    binary = build_path.parent / 'pair'
    assert digest(binary) == build['binary_sha256']
    cases, provenance = selection()
    inputs = dict(build_sha256=digest(build_path), cases=cases, provenance=provenance,
                  script_sha256=digest(Path(__file__)), selection_helper_sha256=digest(ROOT / 'scripts/validate_piano_guitar_extensions.py'),
                  ffmpeg_version=subprocess.run(['ffmpeg', '-version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
                  conversion='Decode original PCM; stereo arithmetic mean; no gain/looping; explicit derived 48k resampling')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/piano_voice_extensions' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'replay.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        atomic_json(directory / 'plan.json', inputs)
        replay(inputs, cases, binary, directory)


def replay(inputs, cases, binary, directory):
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    for index, sample in enumerate(cases, 1):
        assert digest(ROOT / sample['audio']) == sample['audio_sha256']
        destination = directory / (sample['id'] + '.tsv')
        if sample['id'] in state['recordings']:
            assert digest(destination) == state['recordings'][sample['id']]['sha256']
            continue
        metadata = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=sample_rate,channels,duration', '-of', 'json', str(ROOT / sample['audio'])],
            text=True, capture_output=True, check=True).stdout)['streams'][0]
        original_rate, channels = int(metadata['sample_rate']), int(metadata['channels'])
        assert channels in (1, 2)
        rate = sample['target_rate'] or original_rate
        raw = directory / (sample['id'] + '.f32')
        command = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1', '-filter_threads', '1',
                   '-i', str(ROOT / sample['audio']), '-t', str(sample['seconds'])]
        if channels == 2:
            command += ['-af', 'pan=mono|c0=0.5*c0+0.5*c1']
        subprocess.run(command + ['-ac', '1', '-ar', str(rate), '-f', 'f32le', str(raw)], check=True)
        duration = min(sample['seconds'], float(metadata['duration']))
        assert abs(raw.stat().st_size // 4 - round(duration * rate)) <= 2
        pending = destination.with_suffix('.pending.tsv')
        subprocess.run([str(binary), str(raw), str(rate), str(pending)], check=True, timeout=3600)
        pending.replace(destination)
        count = removed_count = losses = labelled_losses = 0
        before_times, after_times = [], []
        hop = int(rate * .05 + .5)
        with destination.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                count += 1
                assert int(row['end_sample']) == count * hop
                assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
                before, after = ({int(v) for v in row[column].split(',') if v} for column in ('voice', 'after_voice'))
                assert after <= before
                removed = before - after
                removed_count += len(removed)
                losses += len(removed) if sample['protect_voice'] else 0
                time = int(row['end_sample']) / rate
                valid = any(abs(time - endpoint) < .001 for endpoint in sample.get('valid_end_seconds', []))
                labelled_losses += bool(valid and sample.get('labelled_midi') in removed)
                before_times.append(float(row['before_ms']))
                after_times.append(float(row['after_ms']))
        assert count == raw.stat().st_size // 4 // hop
        def timing(values):
            ordered = sorted(values)
            return dict(p50=ordered[(len(ordered) - 1) // 2], p99=ordered[int((len(ordered) - 1) * .99)],
                        maximum=ordered[-1], deadline_misses=sum(value > hop / rate * 1000 for value in values))
        state['recordings'][sample['id']] = dict(kind=sample['kind'], rate=rate, windows=count, removed=removed_count,
            protected_voice_losses=losses, labelled_mixture_losses=labelled_losses, before_ms=timing(before_times),
            after_ms=timing(after_times), sha256=digest(destination), raw_sha256=digest(raw))
        atomic_json(checkpoint, state)
        if index % 10 == 0 or removed_count or sample['kind'] == 'piano':
            print(index, '/', len(cases), sample['id'], 'removed', removed_count, 'protected losses', losses, flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = not any(row['protected_voice_losses'] or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
    state['passed'] &= any(row['kind'] == 'piano' and row['removed'] for row in state['recordings'].values())
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed']


if __name__ == '__main__':
    main()
