#!/usr/bin/env python3
"""Check stable-body native behavior against its pre-existing training rule."""
import argparse
import csv
import fcntl
import hashlib
import json
from itertools import groupby
from pathlib import Path

from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calibration', action='store_true')
    args = parser.parse_args()
    pointer = json.loads((ROOT / 'build/joint_body_native/current.json').read_text())
    build_path = ROOT / pointer['build']
    build = json.loads(build_path.read_text())
    assert digest(build_path) == pointer['sha256'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    offline_path = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2/report.json'
    offline = json.loads(offline_path.read_text())
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path),
                  script_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'), driver_sha256=digest(Path(__file__)),
                  offline_sha256=digest(offline_path), phase='calibration' if args.calibration else 'training')
    directory = ROOT / 'build/joint_body_measurement' / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        capture(inputs, baseline_path, json.loads(baseline_path.read_text()), build_path, directory)
        report = json.loads((directory / 'report.json').read_text())
        native_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
        native = json.loads(native_path.read_text())
        for name, result in report['recordings'].items():
            expected = offline['calibration'] if args.calibration else offline['training'][name]
            candidates_path = native_path.parent / (name + '.tsv')
            assert digest(candidates_path) == native['recordings'][name]['sha256']
            stable = set()
            with candidates_path.open() as stream:
                for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r: int(r['end_sample'])):
                    best = {}
                    for row in group:
                        midi = int(row['midi'])
                        if midi not in best or float(row['keyboard_score']) + .01 * float(row['ownership']) > float(best[midi]['keyboard_score']) + .01 * float(best[midi]['ownership']):
                            best[midi] = row
                    for midi, row in best.items():
                        if row['profile'] == '0' and float(row['pitch_stability']) >= .75 and float(row['onset']) <= .1 and float(row['decay']) <= .15:
                            stable.add((endpoint, midi))
            proposals = {(c['end_sample'], c['midi']) for c in expected['cases']} & stable
            wanted, actual = set(), set()
            with (directory / (name + '.tsv')).open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    endpoint = int(row['end_sample'])
                    free = [int(v) for v in row['free_slots'].split(',')]
                    for end, midi in sorted(proposals):
                        if end == endpoint and free[midi % 12]:
                            wanted.add((end, midi)); free[midi % 12] -= 1
                    before, after = ({int(v) for v in row[k].split(',') if v} for k in ('keys', 'after_keys'))
                    actual.update((endpoint, m) for m in after - before)
            assert wanted == actual, (name, sorted(wanted - actual), sorted(actual - wanted))
            assert not result['deltas']['removed_cells'] and not result['deltas']['surviving_cell_changed_frames']
            assert not result['deltas']['unsupported_added_seconds'] and result['maximum_after_ms'] < 50
            print(name, 'exact stable-body native parity', sorted(actual), flush=True)


if __name__ == '__main__':
    main()
