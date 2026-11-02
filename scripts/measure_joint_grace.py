#!/usr/bin/env python3
"""Measure actual native restoration and compare frozen causal decisions."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path

from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calibration', action='store_true')
    args = parser.parse_args()
    pointer = json.loads((ROOT / 'build/joint_grace_native/current.json').read_text())
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256']
    build = json.loads(build_path.read_text())
    assert digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    frozen_path = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2/report.json'
    assert digest(frozen_path) == build['inputs']['calibration_sha256']
    frozen = json.loads(frozen_path.read_text())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path),
                  script_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'), driver_sha256=digest(Path(__file__)),
                  frozen_sha256=digest(frozen_path), phase='calibration' if args.calibration else 'training')
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/joint_grace_measurement' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, json.loads(baseline_path.read_text()), build_path, directory)
        report = json.loads((directory / 'report.json').read_text())
        for name, row in report['recordings'].items():
            expected = frozen['calibration'] if args.calibration else frozen['training'][name]
            expected_cells = {(c['end_sample'], c['midi']) for c in expected['cases']}
            actual_cells = set()
            skipped = set()
            with (directory / (name + '.tsv')).open() as stream:
                for frame in csv.DictReader(stream, delimiter='\t'):
                    before, after = ({int(v) for v in frame[k].split(',') if v} for k in ('keys', 'after_keys'))
                    actual_cells.update((int(frame['end_sample']), m) for m in after - before)
                    free = [int(v) for v in frame['free_slots'].split(',')]
                    for endpoint, midi in sorted(expected_cells):
                        if endpoint != int(frame['end_sample']):
                            continue
                        if not free[midi % 12]:
                            skipped.add((endpoint, midi))
                        else:
                            free[midi % 12] -= 1
            expected_cells -= skipped
            assert actual_cells == expected_cells, (name, sorted(actual_cells - expected_cells), sorted(expected_cells - actual_cells))
            assert not row['deltas']['removed_cells'] and not row['deltas']['surviving_cell_changed_frames']
            expected_held = sum(c['held_seconds'] for c in expected['cases'] if (c['end_sample'], c['midi']) not in skipped)
            assert abs(row['deltas']['held_added_seconds'] - expected_held) < 1e-7
            assert not row['deltas']['unsupported_added_seconds'] and row['maximum_after_ms'] < 50
            assert row['after']['matched_attacks'] == expected['before']['matched_attacks']
            print(name, 'visible row-capacity skips', sorted(skipped), flush=True)
        print('Frozen native cell decisions and held recovery verified with visible row capacity; no surviving-cell changes', flush=True)


if __name__ == '__main__':
    main()
