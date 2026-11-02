#!/usr/bin/env python3
"""Preservation suite for frozen stable-body restoration, including added rows."""
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
from routing_duration_score import merge
from validate_low_keyboard_controls import selection, inspect
from validate_routing_consensus import prepare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--shard', type=int, default=0, choices=range(4))
    args = parser.parse_args()
    frozen_pointer = json.loads((ROOT / 'build/joint_body_fresh/current-frozen.json').read_text())
    frozen_path = ROOT / frozen_pointer['path']
    frozen = json.loads(frozen_path.read_text())
    assert digest(frozen_path) == frozen_pointer['sha256']
    build_path = ROOT / frozen['build']
    build = json.loads(build_path.read_text())
    assert digest(build_path) == frozen['build_sha256'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    cases, provenance = selection()
    inputs = dict(frozen_sha256=digest(frozen_path), build_sha256=digest(build_path), cases=cases, provenance=provenance,
                  script_sha256=digest(Path(__file__)), helpers={p: digest(ROOT / p) for p in
                  ('scripts/validate_low_keyboard_controls.py', 'scripts/validate_routing_consensus.py',
                   'scripts/midi_sustain_reference.py', 'scripts/routing_duration_score.py', 'scripts/audit_keyboard_recovery.py')})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/joint_body_controls' / key
    directory.mkdir(parents=True, exist_ok=True)
    plan = directory / 'plan.json'
    if plan.exists():
        assert json.loads(plan.read_text()) == inputs
    else:
        atomic_json(plan, inputs)
    print('Frozen stable-body controls', directory.relative_to(ROOT), len(cases), flush=True)
    if args.plan:
        return
    with (directory / ('capture-' + str(args.shard) + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        checkpoint = directory / ('report-' + str(args.shard) + '.json')
        state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(plan_sha256=digest(plan), recordings={}, complete=False, passed=False)
        assert state['plan_sha256'] == digest(plan)
        for index, sample in enumerate(cases[args.shard::4], 1):
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
                    expected = {r['end_sample']: r for r in csv.DictReader(stream, delimiter='\t')}
            entry = inspect(path, sample, rate, expected)
            allowed = {}
            if sample['family'] == 'piano' and 'midi' in sample:
                assert digest(ROOT / sample['midi']) == sample['midi_sha256']
                for note in read_intervals((ROOT / sample['midi']).read_bytes()):
                    if note['channel'] != 9:
                        allowed.setdefault(note['midi'], []).append((note['start'], note['end'] + .3))
                allowed = {m: merge(v) for m, v in allowed.items()}
            entry.update(nonpiano_or_unscored_additions=0, unsupported_piano_added_seconds=0., wrong_isolated_piano_pitches=0, survivor_changes=0)
            with path.open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    entry['survivor_changes'] += row['survivor_changed'] != '0'
                    before, after = ({int(v) for v in row[k].split(',') if v} for k in ('keys', 'after_keys'))
                    for midi in after - before:
                        if sample['family'] != 'piano':
                            entry['nonpiano_or_unscored_additions'] += 1
                        elif 'expected_midi' in sample:
                            entry['wrong_isolated_piano_pitches'] += midi != sample['expected_midi']
                        else:
                            start, end = int(row['end_sample']) / rate, min(entry['windows'] * .05, int(row['end_sample']) / rate + .05)
                            entry['unsupported_piano_added_seconds'] += max(0., end - start - coverage(allowed.get(midi, []), start, end))
            entry.update(raw_sha256=digest(raw), rate=rate)
            state['recordings'][sample['id']] = entry
            atomic_json(checkpoint, state)
            if index % 20 == 0 or entry['nonpiano_or_unscored_additions'] or entry['unsupported_piano_added_seconds'] > 1e-8:
                print(index, sample['id'], 'added', entry['added'], 'nonpiano/unscored', entry['nonpiano_or_unscored_additions'],
                      'unsupported piano seconds', entry['unsupported_piano_added_seconds'], flush=True)
        assert digest(Path(__file__)) == inputs['script_sha256']
        state['complete'] = True
        state['passed'] = not any(any(r[k] for k in ('removed', 'unrelated_changes', 'tempo_changes', 'survivor_changes',
            'nonpiano_or_unscored_additions', 'wrong_isolated_piano_pitches')) or r['unsupported_piano_added_seconds'] > 1e-8 or
            r['after_ms']['deadline_misses'] for r in state['recordings'].values())
        atomic_json(checkpoint, state)
        print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
        assert state['passed']


if __name__ == '__main__':
    main()
