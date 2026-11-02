#!/usr/bin/env python3
"""Preservation replay for the frozen causal coherence native trial."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

from routing_duration_baseline import ROOT, atomic_json, digest
from validate_low_keyboard_controls import selection, inspect
from validate_routing_consensus import prepare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--shard', type=int, default=0)
    args = parser.parse_args()
    assert 0 <= args.shard < 4
    frozen_path = ROOT / 'build/low_keyboard_coherence_measurement/frozen.json'
    frozen = json.loads(frozen_path.read_text())
    build_path = ROOT / frozen['build']
    assert digest(build_path) == frozen['build_sha256']
    build = json.loads(build_path.read_text())
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    cases, provenance = selection()
    inputs = dict(build_sha256=digest(build_path), frozen_sha256=digest(frozen_path), cases=cases, provenance=provenance,
                  script_sha256=digest(Path(__file__)),
                  helpers={p: digest(ROOT / p) for p in ('scripts/validate_low_keyboard_controls.py', 'scripts/validate_routing_consensus.py')})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_coherence_controls' / key
    directory.mkdir(parents=True, exist_ok=True)
    plan = directory / 'plan.json'
    if plan.exists():
        assert json.loads(plan.read_text()) == inputs
    else:
        atomic_json(plan, inputs)
    print('Frozen coherence controls', directory.relative_to(ROOT), len(cases), flush=True)
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
                    expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
            entry = inspect(path, sample, rate, expected)
            with path.open() as stream:
                entry['survivor_changes'] = sum(row['survivor_changed'] != '0' for row in csv.DictReader(stream, delimiter='\t'))
            assert entry['windows'] == raw.stat().st_size // 4 // int(rate * .05 + .5)
            entry.update(raw_sha256=digest(raw), rate=rate)
            state['recordings'][sample['id']] = entry
            atomic_json(checkpoint, state)
            if index % 20 == 0 or entry['correct_any_losses'] or entry['correct_keyboard_losses']:
                print(index, sample['id'], 'removed', entry['removed'], 'correct losses', entry['correct_any_losses'], entry['correct_keyboard_losses'], flush=True)
        assert digest(Path(__file__)) == inputs['script_sha256']
        state['complete'] = True
        state['passed'] = not any(any(row[k] for k in ('correct_any_losses', 'correct_keyboard_losses', 'unrelated_changes', 'tempo_changes', 'added', 'survivor_changes')) or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
        atomic_json(checkpoint, state)
        print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
        assert state['passed']


if __name__ == '__main__':
    main()
