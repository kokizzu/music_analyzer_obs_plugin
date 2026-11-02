#!/usr/bin/env python3
"""Require native/offline agreement before disjoint calibration access."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
from measure_low_keyboard_trial import capture
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--calibration',action='store_true')
    args=parser.parse_args()
    phase='calibration' if args.calibration else 'training'
    pointer=json.loads((ROOT/'build/phase_low_keyboard_native/current.json').read_text())
    build_path=ROOT/pointer['build']
    assert digest(build_path)==pointer['sha256']
    build=json.loads(build_path.read_text())
    assert build['regression_passed'] and digest(build_path.parent/'pair')==build['binary_sha256']
    assert all(digest(ROOT/p)==h for p,h in build['inputs']['assets'].items())
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    inputs=dict(build_sha256=digest(build_path),baseline_sha256=digest(baseline_path),phase=phase,
                script_sha256=digest(ROOT/'scripts/measure_low_keyboard_trial.py'),driver_sha256=digest(Path(__file__)),
                guard_sha256=digest(ROOT/'src/phase_low_keyboard.hpp'),helpers={p:digest(ROOT/p) for p in
                    ('scripts/routing_duration_score.py','scripts/midi_sustain_reference.py','scripts/audit_keyboard_recovery.py')})
    if args.calibration:
        ptr=json.loads((ROOT/'build/phase_low_keyboard_measurement/current-training.json').read_text())
        path=ROOT/ptr['report']
        previous=json.loads(path.read_text())
        assert digest(path)==ptr['sha256'] and previous['complete'] and previous['passed']
        assert previous['inputs']['build_sha256']==inputs['build_sha256']
        parity_path=path.parent/'parity.json'
        parity=json.loads(parity_path.read_text())
        assert parity['passed'] and parity['report_sha256']==digest(path)
        inputs['training_sha256']=digest(path)
        inputs['parity_sha256']=digest(parity_path)
    directory=ROOT/'build/phase_low_keyboard_measurement'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    with (directory/'capture.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        capture(inputs,baseline_path,json.loads(baseline_path.read_text()),build_path,directory)
        if not args.calibration:
            offline_path=ROOT/'build/phase_low_keyboard_screen/report.json'
            offline=json.loads(offline_path.read_text())
            assert offline['decision']=='requires_native_calibration'
            assert all(digest(ROOT/p)==h for p,h in offline['inputs'].items())
            report=json.loads((directory/'report.json').read_text())
            for name,recording in report['recordings'].items():
                removed=set()
                with (directory/(name+'.tsv')).open() as stream:
                    for row in csv.DictReader(stream,delimiter='\t'):
                        before,after=({int(v) for v in row[k].split(',') if v} for k in ('keys','after_keys'))
                        removed.update((int(row['end_sample']),m) for m in before-after)
                expected={(r['end_sample'],r['midi']) for r in offline['recordings'][name]['removed']}
                assert removed==expected,(name,sorted(removed^expected))
                assert recording['deltas']['surviving_cell_changed_frames']==0
            atomic_json(directory/'parity.json',dict(passed=True,report_sha256=digest(directory/'report.json'),offline_sha256=digest(offline_path)))
            print('Native removal sets exactly match the fixed multiwindow training screen',flush=True)


if __name__=='__main__':
    main()
