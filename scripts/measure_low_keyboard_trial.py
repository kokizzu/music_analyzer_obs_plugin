#!/usr/bin/env python3
"""Score direct low-fundamental support on training piano before any holdout."""
import argparse
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
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--calibration', action='store_true')
    group.add_argument('--heldout', action='store_true')
    args = parser.parse_args()
    phase = 'heldout' if args.heldout else 'calibration' if args.calibration else 'training'
    pointer = json.loads((ROOT / 'build/low_keyboard_trial/current.json').read_text())
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256']
    build = json.loads(build_path.read_text())
    assert build['regression_passed'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['assets'].items())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path), script_sha256=digest(Path(__file__)),
                  phase=phase, guard_sha256=digest(ROOT / 'src/low_keyboard_fundamental_guard.inc'),
                  helpers={p: digest(ROOT / p) for p in ('scripts/routing_duration_score.py', 'scripts/midi_sustain_reference.py', 'scripts/audit_keyboard_recovery.py')})
    if phase == 'calibration':
        previous = json.loads((ROOT / 'build/low_keyboard_measurement/current-training.json').read_text())
        training_path = ROOT / previous['report']
        assert digest(training_path) == previous['sha256']
        training = json.loads(training_path.read_text())
        assert training['complete'] and training['passed'] and training['inputs']['build_sha256'] == inputs['build_sha256']
        assert training['inputs']['script_sha256'] == inputs['script_sha256']
        inputs['training_report_sha256'] = digest(training_path)
    if phase == 'heldout':
        frozen = json.loads((ROOT / 'build/low_keyboard_measurement/frozen.json').read_text())
        assert frozen['build_sha256'] == inputs['build_sha256'] and frozen['guard_sha256'] == inputs['guard_sha256']
        assert frozen['measurement_script_sha256'] == inputs['script_sha256']
        inputs['frozen_sha256'] = digest(ROOT / 'build/low_keyboard_measurement/frozen.json')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_measurement' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, baseline, build_path, directory)


def capture(inputs, baseline_path, baseline, build_path, directory):
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    for sample in baseline['selection']:
        selected = (sample['cohort'] == 'heldout' if inputs['phase'] == 'heldout' else
                    sample['id'] == 'training-4' if inputs['phase'] == 'calibration' else
                    sample['cohort'] == 'training' and sample['id'] != 'training-4')
        if not selected:
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
        reference = ROOT / 'build/routing_consensus_pair/e63350f9b5113f8b' / ('piano-' + name + '.tsv')
        current_reference = json.loads((reference.parent / 'report.json').read_text())
        assert digest(reference) == current_reference['recordings']['piano-' + name]['sha256']
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
            assert all(row[column] == before['after_' + column if column in ('guitar', 'voice') else column] for column in ('end_sample', 'bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
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
    benefit = any(row['deltas']['unsupported_removed_seconds'] > 0 or row['deltas']['held_added_seconds'] > 0 for row in state['recordings'].values())
    state['passed'] = (inputs['phase'] == 'calibration' or benefit) and not any(
        row['deltas']['supported_removed_seconds'] > 1e-8 or row['deltas']['unsupported_added_seconds'] > 1e-8 or
        row['deltas']['unrelated_changed_frames'] or row['deltas']['tempo_changed_frames'] or
        row['after']['matched_attacks'] < row['before']['matched_attacks'] for row in state['recordings'].values())
    atomic_json(checkpoint, state)
    atomic_json(directory.parent / ('current-' + inputs['phase'] + '.json'),
                dict(report=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed'], 'Training-only causal duration gate failed; do not examine holdout or promote'


if __name__ == '__main__':
    main()
