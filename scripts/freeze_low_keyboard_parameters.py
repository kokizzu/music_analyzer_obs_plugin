#!/usr/bin/env python3
"""Freeze the native low-note floor after training/calibration, before holdout."""
import json

from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    directory = ROOT / 'build/low_keyboard_measurement'
    reports = {}
    inputs = []
    for phase in ('training', 'calibration'):
        pointer = json.loads((directory / ('current-' + phase + '.json')).read_text())
        path = ROOT / pointer['report']
        assert digest(path) == pointer['sha256']
        report = json.loads(path.read_text())
        assert report['complete'] and report['passed'] and report['inputs']['phase'] == phase
        assert report['inputs']['guard_sha256'] == digest(ROOT / 'src/low_keyboard_fundamental_guard.inc')
        assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/measure_low_keyboard_trial.py')
        inputs.append(report['inputs'])
        reports[phase] = dict(path=pointer['report'], sha256=digest(path))
    assert inputs[0]['build_sha256'] == inputs[1]['build_sha256']
    result = dict(reports=reports, build_sha256=inputs[0]['build_sha256'], guard_sha256=inputs[0]['guard_sha256'],
                  measurement_script_sha256=inputs[0]['script_sha256'], relative_direct_floor=.001, absolute_direct_floor=1e-6,
                  scope='Fixed from training-only direct-evidence inspection; separate calibration passed without held/pedal-support losses; no held-out inspection before this artifact')
    path = directory / 'frozen.json'
    if path.exists():
        assert json.loads(path.read_text()) == result, 'Do not overwrite a frozen held-out configuration'
    else:
        atomic_json(path, result)
    print(path.relative_to(ROOT), 'fixed relative floor', result['relative_direct_floor'])


if __name__ == '__main__':
    main()
