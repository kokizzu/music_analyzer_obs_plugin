#!/usr/bin/env python3
"""Replay native coherence on training before calibration or held-out use."""
import hashlib
import json
from pathlib import Path

from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, digest


def main():
    pointer = json.loads((ROOT / 'build/low_keyboard_coherence_trial/current.json').read_text())
    build_path = ROOT / pointer['build']
    assert digest(build_path) == pointer['sha256']
    build = json.loads(build_path.read_text())
    assert build['regression_passed'] and digest(build_path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == h for p, h in build['inputs']['assets'].items())
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    inputs = dict(build_sha256=digest(build_path), baseline_sha256=digest(baseline_path), script_sha256=digest(Path(__file__)),
                  scorer_sha256=digest(ROOT / 'scripts/measure_low_keyboard_trial.py'), phase='training',
                  guard_sha256=digest(ROOT / 'src/low_keyboard_coherence.hpp'))
    # Shared scorer checks its own producer hash, so bind it explicitly here.
    inputs['script_sha256'] = inputs['scorer_sha256']
    inputs['driver_sha256'] = digest(Path(__file__))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/low_keyboard_coherence_measurement' / key
    directory.mkdir(parents=True, exist_ok=True)
    capture(inputs, baseline_path, json.loads(baseline_path.read_text()), build_path, directory)
    report = json.loads((directory / 'report.json').read_text())
    offline = json.loads((ROOT / 'build/low_keyboard_coherence/dc5f99cb5044a9d7/report.json').read_text())
    for name, entry in report['recordings'].items():
        expected = offline['recordings'][name]['metrics']["(0.4, 0.01, 'latched', 'fundamental-or-third')"]
        for key in ('held_removed_seconds', 'supported_removed_seconds', 'unsupported_removed_seconds'):
            assert abs(entry['deltas'][key] - expected[key]) < 1e-7, (name, key, entry['deltas'][key], expected[key])
        assert entry['deltas']['removed_cells'] == expected['removed']
    print('Native training decisions reproduce frozen offline coherence metrics exactly', flush=True)


if __name__ == '__main__':
    main()
