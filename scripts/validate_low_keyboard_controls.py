#!/usr/bin/env python3
"""Protect labelled low notes and unrelated outputs with frozen native settings."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from validate_routing_consensus import prepare


def annotated_notes(report, name):
    result = []
    for manifest, checksum in report['inputs'].get('manifests', {}).items():
        path = ROOT / manifest
        assert digest(path) == checksum
        for line in path.read_text().splitlines():
            fields = line.split('\t')
            if fields[0] == 'NOTE' and fields[1] == name:
                result.append([float(fields[2]), float(fields[3]), int(fields[4])])
    return result


def guitarset_notes(audio):
    path = ROOT / audio.replace('_mic.wav', '.jams')
    assert path.exists()
    notes = []
    for annotation in json.loads(path.read_text())['annotations']:
        if annotation['namespace'] != 'note_midi':
            continue
        data = annotation['data']
        values = data.values() if isinstance(data, dict) else data
        for row in values:
            notes.append([float(row['time']), float(row['time']) + float(row['duration']), round(float(row['value']))])
    return notes


def selection():
    cases, provenance = [], {}
    base = ROOT / 'build/real_note_samples'
    manifest = base / 'manifest.tsv'
    provenance[str(manifest.relative_to(ROOT))] = digest(manifest)
    with manifest.open() as stream:
        low = [row for row in csv.DictReader(stream, delimiter='\t') if int(row['midi']) < 40]
    assert len(low) == 324
    for target in (None, 48000):
        for sample in low:
            audio = base / sample['path']
            cases.append(dict(id=sample['id'] + ('-48k' if target else '-original'), family=sample['family'], expected_midi=int(sample['midi']),
                fresh=True, audio=str(audio.relative_to(ROOT)), audio_sha256=digest(audio), target_rate=target, seconds=4))
    for kind, relative in [('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
                           ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
                           ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json')]:
        path = ROOT / relative
        source = json.loads(path.read_text())
        assert source['complete']
        provenance[relative] = digest(path)
        samples = {sample['id']: sample for sample in source['inputs']['selection']}
        reference = ROOT / 'build/routing_consensus_pair/31e4706686b5b160'
        reference_report = json.loads((reference / 'report.json').read_text())
        for name, entry in source['recordings'].items():
            sample = samples[name]
            key = kind + '-' + name
            raw = path.parent / (name + '.f32')
            reference_path = reference / (key + '.tsv')
            assert digest(reference_path) == reference_report['recordings'][key]['sha256']
            item = dict(id='existing-' + key, fresh=False, family=sample.get('family', 'guitar'), rate=entry['rate'],
                        raw=str(raw.relative_to(ROOT)), raw_sha256=digest(raw), reference=str(reference_path.relative_to(ROOT)),
                        reference_sha256=digest(reference_path), notes=annotated_notes(source, name))
            if kind == 'single':
                item['expected_midi'] = sample['midi']
            elif kind == 'music':
                item['notes'] = guitarset_notes(sample['audio'])
            cases.append(item)
    source_directory = ROOT / 'build/routing_consensus_extensions/3aa507e9ead66390'
    plan_path = source_directory / 'plan.json'
    plan = json.loads(plan_path.read_text())
    provenance[str(plan_path.relative_to(ROOT))] = digest(plan_path)
    entries = {}
    for shard in range(2):
        path = source_directory / ('report-' + str(shard) + '.json')
        report = json.loads(path.read_text())
        assert report['complete'] and report['passed']
        provenance[str(path.relative_to(ROOT))] = digest(path)
        entries.update(report['recordings'])
    legacy_path = ROOT / 'build/piano_voice_extensions/ebc264a1f5031e97/report.json'
    legacy = json.loads(legacy_path.read_text())
    original = {item['id']: item for item in legacy['inputs']['cases']}
    piano_base = ROOT / 'build/maestro_real_samples'
    with (piano_base / 'maestro-v3.0.0.csv').open() as stream:
        midi_by_audio = {str((piano_base / row['audio_filename']).relative_to(ROOT)): str((piano_base / row['midi_filename']).relative_to(ROOT)) for row in csv.DictReader(stream)}
    for sample in plan['cases']:
        name, entry = sample['id'], entries[sample['id']]
        raw = source_directory / (name + '.f32') if sample['fresh'] else ROOT / sample['raw']
        reference = source_directory / (name + '.tsv')
        assert digest(raw) == entry['raw_sha256'] and digest(reference) == entry['sha256']
        item = dict(id='extended-' + name, fresh=False, family='piano' if sample['kind'] == 'piano' else 'control',
                    rate=entry['rate'], raw=str(raw.relative_to(ROOT)), raw_sha256=digest(raw),
                    reference=str(reference.relative_to(ROOT)), reference_sha256=digest(reference))
        original_sample = sample if sample['fresh'] else original[name.removeprefix('regression-')]
        if sample['kind'] == 'piano':
            item['midi'] = midi_by_audio[original_sample['audio']]
            item['midi_sha256'] = digest(ROOT / item['midi'])
        elif sample['kind'] == 'poly-guitar':
            item['notes'] = guitarset_notes(original_sample['audio'])
        cases.append(item)
    assert len(cases) == 1154 and len({sample['id'] for sample in cases}) == len(cases)
    return cases, provenance


def inspect(path, sample, rate, expected=None):
    notes = sample.get('notes', [])
    if 'midi' in sample:
        assert digest(ROOT / sample['midi']) == sample['midi_sha256']
        notes = [[row['start'], row['end'], row['midi']] for row in read_intervals((ROOT / sample['midi']).read_bytes()) if row['channel'] != 9]
    result = dict(windows=0, removed=0, added=0, correct_any_losses=0, correct_keyboard_losses=0, unrelated_changes=0, tempo_changes=0)
    before_times, after_times = [], []
    with path.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            result['windows'] += 1
            assert int(row['end_sample']) == result['windows'] * int(rate * .05 + .5)
            if expected is not None:
                assert all(row[key] == expected[row['end_sample']]['after_' + key if key in ('guitar', 'voice') else key]
                           for key in ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
            before, after = ({int(v) for v in row[key].split(',') if v} for key in ('keys', 'after_keys'))
            lost = {int(v) for v in row['any_lost'].split(',') if v}
            removed = before - after
            result['removed'] += len(removed)
            result['added'] += len(after - before)
            time = int(row['end_sample']) / rate
            protected = {midi for start, end, midi in notes if start - .15 < time + .05 and end + .3 > time}
            if 'expected_midi' in sample:
                protected.add(sample['expected_midi'])
            result['correct_any_losses'] += len(lost & protected)
            if sample['family'] == 'piano':
                result['correct_keyboard_losses'] += len(removed & protected)
            result['unrelated_changes'] += bool(row['unrelated_difference'])
            result['tempo_changes'] += row['bpm_changed'] != '0'
            before_times.append(float(row['before_ms']))
            after_times.append(float(row['after_ms']))
    def timing(values):
        ordered = sorted(values)
        return dict(p99=ordered[int((len(ordered) - 1) * .99)], maximum=ordered[-1], deadline_misses=sum(value > 50 for value in values))
    result.update(sha256=digest(path), before_ms=timing(before_times), after_ms=timing(after_times))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=4)
    args = parser.parse_args()
    assert 0 <= args.shard < args.shards
    pointer = json.loads((ROOT / 'build/low_keyboard_trial/current.json').read_text())
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256']
    build = json.loads(build_path.read_text())
    assert all(digest(ROOT / p) == value for p, value in build['inputs']['assets'].items())
    cases, provenance = selection()
    inputs = dict(build_sha256=digest(build_path), cases=cases, provenance=provenance, shards=args.shards,
                  script_sha256=digest(Path(__file__)), preparation_helper_sha256=digest(ROOT / 'scripts/validate_routing_consensus.py'),
                  frozen_sha256=digest(ROOT / 'build/low_keyboard_measurement/frozen.json'))
    frozen = json.loads((ROOT / 'build/low_keyboard_measurement/frozen.json').read_text())
    assert frozen['build_sha256'] == inputs['build_sha256'] and frozen['guard_sha256'] == digest(ROOT / 'src/low_keyboard_fundamental_guard.inc')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_controls' / key
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory / 'plan.json').exists():
        atomic_json(directory / 'plan.json', inputs)
    else:
        assert json.loads((directory / 'plan.json').read_text()) == inputs
    print('Frozen low-note control plan', directory.relative_to(ROOT), 'cases', len(cases), flush=True)
    if args.plan:
        return
    with (directory / ('capture-' + str(args.shard) + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        checkpoint = directory / ('report-' + str(args.shard) + '.json')
        state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(plan_sha256=digest(directory / 'plan.json'), recordings={}, complete=False, passed=False)
        assert state['plan_sha256'] == digest(directory / 'plan.json')
        for index, sample in enumerate(cases[args.shard::args.shards], 1):
            path = directory / (sample['id'] + '.tsv')
            if sample['id'] in state['recordings']:
                assert digest(path) == state['recordings'][sample['id']]['sha256']
                continue
            raw, rate = prepare(sample, directory)
            pending = path.with_suffix('.pending.tsv')
            subprocess.run([str(build_path.parent / 'pair'), str(raw), str(rate), str(pending)], check=True, timeout=3600)
            pending.replace(path)
            expected = None
            if 'reference' in sample:
                assert digest(ROOT / sample['reference']) == sample['reference_sha256']
                with (ROOT / sample['reference']).open() as stream:
                    expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
            entry = inspect(path, sample, rate, expected)
            assert entry['windows'] == raw.stat().st_size // 4 // int(rate * .05 + .5)
            entry.update(raw_sha256=digest(raw), rate=rate)
            state['recordings'][sample['id']] = entry
            atomic_json(checkpoint, state)
            if index % 20 == 0 or entry['correct_any_losses'] or entry['correct_keyboard_losses'] or entry['unrelated_changes']:
                print(index, sample['id'], 'removed', entry['removed'], 'correct losses', entry['correct_any_losses'], entry['correct_keyboard_losses'], flush=True)
        assert digest(Path(__file__)) == inputs['script_sha256']
        state['complete'] = True
        state['passed'] = not any(row['correct_any_losses'] or row['correct_keyboard_losses'] or row['unrelated_changes'] or row['tempo_changes'] or row['added'] or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
        atomic_json(checkpoint, state)
        print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
        assert state['passed']


if __name__ == '__main__':
    main()
