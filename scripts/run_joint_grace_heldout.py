#!/usr/bin/env python3
"""Freeze validated native release behavior before recording-disjoint replay."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path

from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, atomic_json, digest


def read(path):
    return json.loads(path.read_text())


def verify_phase(phase, offline):
    pointer = read(ROOT / 'build/joint_grace_measurement' / ('current-' + phase + '.json'))
    path = ROOT / pointer['report']
    report = read(path)
    assert digest(path) == pointer['sha256'] and report['complete'] and report['passed']
    assert report['inputs']['driver_sha256'] == digest(ROOT / 'scripts/measure_joint_grace.py')
    for name, result in report['recordings'].items():
        raw = path.parent / (name + '.tsv')
        assert digest(raw) == result['sha256']
        expected = offline['calibration'] if phase == 'calibration' else offline['training'][name]
        proposed = {(c['end_sample'], c['midi']) for c in expected['cases']}
        actual, representable = set(), set()
        with raw.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                before, after = ({int(v) for v in row[k].split(',') if v} for k in ('keys', 'after_keys'))
                endpoint = int(row['end_sample'])
                actual.update((endpoint, m) for m in after - before)
                free = [int(v) for v in row['free_slots'].split(',')]
                for end, midi in sorted(proposed):
                    if end == endpoint and free[midi % 12]:
                        representable.add((end, midi))
                        free[midi % 12] -= 1
        assert actual == representable
        assert not any(result['deltas'][k] for k in ('removed_cells', 'surviving_cell_changed_frames', 'unrelated_changed_frames', 'tempo_changed_frames', 'unsupported_added_seconds'))
        assert result['maximum_after_ms'] < 50
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path)), report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--record', choices=['heldout-' + str(i) for i in range(1, 5)])
    args = parser.parse_args()
    assert args.freeze != bool(args.record)
    pointer = read(ROOT / 'build/joint_grace_native/current.json')
    build_path = ROOT / pointer['build']
    build = read(build_path)
    assert digest(build_path) == pointer['sha256']
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    parent = ROOT / 'build/joint_grace_heldout'
    parent.mkdir(parents=True, exist_ok=True)
    if args.freeze:
        offline_path = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2/report.json'
        offline = read(offline_path)
        training, t = verify_phase('training', offline)
        calibration, c = verify_phase('calibration', offline)
        assert t['inputs']['build_sha256'] == c['inputs']['build_sha256'] == digest(build_path)
        baseline = read(ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json')
        training_samples = [s for s in baseline['selection'] if s['cohort'] == 'training']
        held = [s for s in baseline['selection'] if s['cohort'] == 'heldout']
        assert len(held) == len(training_samples) == 4
        for key in ('audio_sha256', 'midi_sha256'):
            assert not {s[key] for s in held} & {s[key] for s in training_samples}
        config = dict(build=str(build_path.relative_to(ROOT)), build_sha256=digest(build_path), training=training,
                      calibration=calibration, script_sha256=digest(Path(__file__)),
                      scorer_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'),
                      selection=held, relative_floor=.8, explained_floor=.3,
                      capacity='Restore into hidden/inactive rows only; never replace a visible cell')
        key = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
        path = parent / ('frozen-' + key + '.json')
        if path.exists():
            assert read(path) == config
        else:
            atomic_json(path, config)
        atomic_json(parent / 'current-frozen.json', dict(path=str(path.relative_to(ROOT)), sha256=digest(path)))
        print('Frozen native release rule before held-out replay:', path.relative_to(ROOT), flush=True)
        return
    pointer = read(parent / 'current-frozen.json')
    frozen_path = ROOT / pointer['path']
    frozen = read(frozen_path)
    assert digest(frozen_path) == pointer['sha256'] and frozen['build_sha256'] == digest(build_path)
    assert frozen['script_sha256'] == digest(Path(__file__))
    assert frozen['scorer_sha256'] == digest(ROOT / 'scripts/measure_low_keyboard_trial.py')
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = read(baseline_path)
    sample = next(s for s in frozen['selection'] if s['id'] == args.record)
    assert sample == next(s for s in baseline['selection'] if s['id'] == args.record)
    baseline['selection'] = [sample]
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path), script_sha256=frozen['scorer_sha256'],
                  driver_sha256=digest(Path(__file__)), frozen_sha256=digest(frozen_path), phase='heldout', record=args.record)
    directory = parent / args.record / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, baseline, build_path, directory)
        report = read(directory / 'report.json')
        result = report['recordings'][args.record]
        assert not result['deltas']['removed_cells'] and not result['deltas']['surviving_cell_changed_frames']
        assert result['maximum_after_ms'] < 50


if __name__ == '__main__':
    main()
