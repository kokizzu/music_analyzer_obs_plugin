#!/usr/bin/env python3
"""Training-only audit of independent native Piano context for restoration."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def confirmed(row):
    return any(set(row[k].split(',')) - set(row['after_' + k].split(',')) for k in ('guitar', 'voice'))


def main():
    pointer = json.loads((ROOT / 'build/joint_body_measurement/current-training.json').read_text())
    body_path = ROOT / pointer['report']
    body = json.loads(body_path.read_text())
    assert body['complete'] and body['passed'] and digest(body_path) == pointer['sha256']
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    reference_path = ROOT / 'build/routing_consensus_pair/e63350f9b5113f8b/report.json'
    reference = json.loads(reference_path.read_text())
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (body_path, baseline_path, reference_path, Path(__file__))}
    periods = [0, .25, 1., 3.]
    results = {}
    for name in body['recordings']:
        current, ref = body_path.parent / (name + '.tsv'), reference_path.parent / ('piano-' + name + '.tsv')
        assert digest(current) == body['recordings'][name]['sha256'] and digest(ref) == reference['recordings']['piano-' + name]['sha256']
        inputs[str(current.relative_to(ROOT))], inputs[str(ref.relative_to(ROOT))] = digest(current), digest(ref)
        sample = next(s for s in baseline['selection'] if s['id'] == name)
        midi_path = ROOT / sample['midi']
        assert digest(midi_path) == sample['midi_sha256']
        held = {}
        for n in read_intervals(midi_path.read_bytes()):
            if n['channel'] != 9:
                held.setdefault(n['midi'], []).append((n['start'], n['key_end']))
        held = {m: merge(v) for m, v in held.items()}
        rate = baseline['recordings'][name]['rate']
        last = None
        metrics = {str(period): dict(cells=0, held_seconds=0.) for period in periods}
        cases = []
        for row, r in zip(rows(current), rows(ref)):
            assert row['end_sample'] == r['end_sample']
            endpoint = int(row['end_sample'])
            if confirmed(r):
                last = endpoint
            age = None if last is None else (endpoint - last) / rate
            before, after = ({int(v) for v in row[k].split(',') if v} for k in ('keys', 'after_keys'))
            for midi in after - before:
                seconds = coverage(held.get(midi, []), endpoint / rate, min(60., endpoint / rate + .05))
                cases.append(dict(end_sample=endpoint, midi=midi, piano_context_age_seconds=age, held_seconds=seconds))
                for period in periods:
                    if age is not None and age <= period + 1e-9:
                        metrics[str(period)]['cells'] += 1
                        metrics[str(period)]['held_seconds'] += seconds
        results[name] = dict(cases=cases, metrics=metrics)
    directory = ROOT / 'build/joint_context_audit'
    directory.mkdir(parents=True, exist_ok=True)
    primary = ROOT / 'build/routing_consensus_rollout/682b938120772cd4/replay'
    rollout = json.loads((primary.parent / 'report.json').read_text())
    assert digest(primary) == rollout['binary_sha256']
    brass = {}
    for suffix, rate in [('original', 16000), ('48k', 48000)]:
        raw = ROOT / 'build/joint_body_controls/28eb805570ce51ef' / ('brass_acoustic_006-039-025-' + suffix + '.f32')
        target = directory / ('brass-' + suffix + '.tsv')
        subprocess.run([str(primary), str(raw), str(rate), str(target)], check=True, timeout=600)
        inputs[str(raw.relative_to(ROOT))] = digest(raw)
        inputs[str(target.relative_to(ROOT))] = digest(target)
        frames = rows(target)
        contexts = [int(r['end_sample']) / rate for r in frames if confirmed(r)]
        brass[suffix] = dict(confirmed_context_times=contexts,
                            context_at_bad_restore=any(0 <= 1.6 - time <= 3 for time in contexts))
    report = dict(inputs=inputs, periods=periods, training=results, brass_counterexample=brass,
                  primary_binary_sha256=digest(primary), scope='Training-only recovery context audit, plus the already observed brass counterexample. No new held-out inspection, threshold promotion or detector change. Context is an actual three-hop native Piano routing confirmation, not source metadata.')
    atomic_json(directory / 'report.json', report)
    print(json.dumps(dict(training=results, brass=brass), indent=2), flush=True)


if __name__ == '__main__':
    main()
