#!/usr/bin/env python3
"""Recording-disjoint calibration and frozen holdout for native coherence."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path

from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, atomic_json, digest

BASE = ROOT / 'build/low_keyboard_coherence_measurement'


def read(path):
    return json.loads(path.read_text())


def phase_report(phase):
    pointer = read(BASE / ('current-' + phase + '.json'))
    path = ROOT / pointer['report']
    assert digest(path) == pointer['sha256']
    report = read(path)
    assert report['complete'] and report['passed'] and report['inputs']['phase'] == phase
    for name, row in report['recordings'].items():
        assert digest(path.parent / (name + '.tsv')) == row['sha256']
        assert not any(row['deltas'][k] for k in ('held_removed_seconds', 'supported_removed_seconds', 'added_cells',
                                                  'unrelated_changed_frames', 'tempo_changed_frames', 'surviving_cell_changed_frames'))
        assert row['maximum_after_ms'] < 50
    return path, report


def training_proof():
    path, report = phase_report('training')
    offline = read(ROOT / 'build/low_keyboard_coherence/dc5f99cb5044a9d7/report.json')
    assert set(report['recordings']) == {'training-1', 'training-2', 'training-3'}
    for name, row in report['recordings'].items():
        expected = offline['recordings'][name]['metrics']["(0.4, 0.01, 'latched', 'fundamental-or-third')"]
        assert row['deltas']['removed_cells'] == expected['removed']
        assert all(abs(row['deltas'][k] - expected[k]) < 1e-7 for k in ('held_removed_seconds', 'supported_removed_seconds', 'unsupported_removed_seconds'))
    return path, report


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--calibration', action='store_true')
    group.add_argument('--freeze', action='store_true')
    group.add_argument('--heldout', action='store_true')
    args = parser.parse_args()
    training_path, training = training_proof()
    pointer = read(ROOT / 'build/low_keyboard_coherence_trial/current.json')
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256'] == training['inputs']['build_sha256']
    build = read(build_path)
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    frozen_path = BASE / 'frozen.json'
    if args.freeze:
        calibration_path, calibration = phase_report('calibration')
        assert calibration['inputs']['build_sha256'] == digest(build_path)
        assert calibration['inputs']['training_report_sha256'] == digest(training_path)
        result = dict(build=str(build_path.relative_to(ROOT)), build_sha256=digest(build_path),
                      guard_sha256=digest(ROOT / 'src/low_keyboard_coherence.hpp'),
                      driver_sha256=digest(Path(__file__)), scorer_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'),
                      training=dict(path=str(training_path.relative_to(ROOT)), sha256=digest(training_path)),
                      calibration=dict(path=str(calibration_path.relative_to(ROOT)), sha256=digest(calibration_path)),
                      seconds=.4, normalized_floor=.01, support='fundamental-or-third', mode='latched', previous_frames=3)
        if frozen_path.exists():
            assert read(frozen_path) == result, 'Do not overwrite frozen held-out parameters'
        else:
            atomic_json(frozen_path, result)
        print('Frozen coherence parameters after native training parity and disjoint calibration', flush=True)
        return
    phase = 'heldout' if args.heldout else 'calibration'
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path),
                  script_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'), driver_sha256=digest(Path(__file__)),
                  guard_sha256=digest(ROOT / 'src/low_keyboard_coherence.hpp'), phase=phase,
                  training_report_sha256=digest(training_path))
    if args.heldout:
        frozen = read(frozen_path)
        assert frozen['build_sha256'] == inputs['build_sha256'] and frozen['guard_sha256'] == inputs['guard_sha256']
        assert frozen['driver_sha256'] == inputs['driver_sha256'] and frozen['scorer_sha256'] == inputs['script_sha256']
        inputs['frozen_sha256'] = digest(frozen_path)
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = BASE / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, read(baseline_path), build_path, directory)


if __name__ == '__main__':
    main()
