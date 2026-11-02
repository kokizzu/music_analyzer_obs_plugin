#!/usr/bin/env python3
"""Score the alias visibility fix causally on training piano before any holdout."""
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge, score


def main():
    pointer = json.loads((ROOT / 'build/keyboard_alias_trial/current.json').read_text())
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256']
    build = json.loads(build_path.read_text())
    assert build['regression_passed'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['assets'].items())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path), script_sha256=digest(Path(__file__)),
                  helpers={p: digest(ROOT / p) for p in ('scripts/routing_duration_score.py', 'scripts/midi_sustain_reference.py', 'scripts/audit_keyboard_recovery.py')})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/keyboard_alias_measurement' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, baseline, build_path, directory)


def capture(inputs, baseline_path, baseline, build_path, directory):
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    for sample in baseline['selection']:
        if sample['cohort'] != 'training' or sample['id'] == 'training-4':
            continue
        name = sample['id']
        entry = baseline['recordings'][name]
        rate, raw = entry['rate'], baseline_path.parent / (name + '.f32')
        assert digest(raw) == entry['prefix_sha256']
        destination = directory / (name + '.tsv')
        if name in state['recordings']:
            assert digest(destination) == state['recordings'][name]['sha256']
        else:
            pending = destination.with_suffix('.pending.tsv')
            subprocess.run([str(build_path.parent / 'pair'), str(raw), str(rate), str(pending)], check=True, timeout=3600)
            pending.replace(destination)
        reference = baseline_path.parent / (name + '.tsv')
        assert digest(reference) == entry['frames_sha256']
        with reference.open() as stream:
            expected = list(csv.DictReader(stream, delimiter='\t'))
        with destination.open() as stream:
            frames = list(csv.DictReader(stream, delimiter='\t'))
        assert len(frames) == len(expected)
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        notes = read_intervals(midi_path.read_bytes())
        held, allowed = {}, {}
        for note in notes:
            if note['channel'] != 9:
                held.setdefault(note['midi'], []).append((note['start'], note['key_end']))
                allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
        held = {midi: merge(intervals) for midi, intervals in held.items()}
        allowed = {midi: merge(intervals) for midi, intervals in allowed.items()}
        deltas = dict(held_removed_seconds=0., supported_removed_seconds=0., unsupported_removed_seconds=0.,
                      held_added_seconds=0., unsupported_added_seconds=0., unrelated_changed_frames=0,
                      tempo_changed_frames=0, surviving_cell_changed_frames=0, removed_cells=0, added_cells=0)
        after_frames = []
        horizon = entry['duration']['audio_seconds']
        for row, before in zip(frames, expected):
            assert all(row[column] == before[column] for column in ('end_sample', 'bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
            deltas['unrelated_changed_frames'] += bool(row['unrelated_difference'])
            deltas['tempo_changed_frames'] += row['bpm_changed'] != '0'
            deltas['surviving_cell_changed_frames'] += row['survivor_changed'] != '0'
            original, changed = ({int(v) for v in row[column].split(',') if v} for column in ('keys', 'after_keys'))
            start, end = int(row['end_sample']) / rate, min(horizon, int(row['end_sample']) / rate + .05)
            for midi in original - changed:
                deltas['removed_cells'] += 1
                deltas['held_removed_seconds'] += coverage(held.get(midi, []), start, end)
                supported = coverage(allowed.get(midi, []), start, end)
                deltas['supported_removed_seconds'] += supported
                deltas['unsupported_removed_seconds'] += end - start - supported
            for midi in changed - original:
                deltas['added_cells'] += 1
                deltas['held_added_seconds'] += coverage(held.get(midi, []), start, end)
                deltas['unsupported_added_seconds'] += end - start - coverage(allowed.get(midi, []), start, end)
            after_frames.append(dict(row, keys=row['after_keys']))
        before_score, after_score = score(frames, notes, rate), score(after_frames, notes, rate)
        result = dict(sha256=digest(destination), deltas=deltas, before=before_score['keys'], after=after_score['keys'],
                      maximum_after_ms=max(float(row['after_ms']) for row in frames))
        state['recordings'][name] = result
        atomic_json(checkpoint, state)
        print(name, json.dumps(deltas), flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = any(row['deltas']['unsupported_removed_seconds'] > 0 or row['deltas']['held_added_seconds'] > 0 for row in state['recordings'].values()) and not any(
        row['deltas']['supported_removed_seconds'] > 1e-8 or row['deltas']['unsupported_added_seconds'] > 1e-8 or
        row['deltas']['unrelated_changed_frames'] or row['deltas']['tempo_changed_frames'] or
        row['after']['matched_attacks'] < row['before']['matched_attacks'] for row in state['recordings'].values())
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed'], 'Training-only causal duration gate failed; do not examine holdout or promote'


if __name__ == '__main__':
    main()
