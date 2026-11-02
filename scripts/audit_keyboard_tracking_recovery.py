#!/usr/bin/env python3
"""Check whether existing confirmed tracking safely repairs postprocessing gaps."""
import csv
import json
from pathlib import Path

from evaluate_guitar_duplicate_model import features, lower_probability
from evaluate_guitar_music_model import frame_context
from itertools import groupby
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    audit_path = ROOT / 'build/keyboard_recovery_audit.json'
    trace_directory = ROOT / 'build/primary_duration_trace/954041e8c8c9eb7f'
    trace_path = trace_directory / 'report.json'
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    audit, trace, model = (json.loads(path.read_text()) for path in (audit_path, trace_path, model_path))
    assert trace['complete']
    inputs = {str(path.relative_to(ROOT)): digest(path) for path in (audit_path, trace_path, model_path, Path(__file__))}
    for name in ('evaluate_guitar_duplicate_model.py', 'evaluate_guitar_music_model.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    totals = {}
    for name, recording in trace['recordings'].items():
        path = trace_directory / (name + '.trace.tsv')
        assert digest(path) == recording['trace_sha256']
        inputs[str(path.relative_to(ROOT))] = digest(path)
        with path.open() as stream:
            tracking = {(int(row['end_sample']), int(row['midi'])): row for row in csv.DictReader(stream, delimiter='\t')}
        evidence = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7' / (name + '.tsv')
        assert str(evidence.relative_to(ROOT)) in audit['inputs']
        assert digest(evidence) == audit['inputs'][str(evidence.relative_to(ROOT))]
        contexts = {}
        with evidence.open() as stream:
            for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                contexts[int(endpoint)] = frame_context(list(frame))
        for candidate in audit['candidates']:
            if candidate['recording'] != name:
                continue
            row = tracking[candidate['end_sample'], candidate['midi']]
            accepted = lower_probability(model['model'], features(candidate['candidate']) + contexts[candidate['end_sample']]) >= model['threshold']
            for rule, enabled in [('smoothed', float(row['smoothed']) > 0),
                                  ('smoothed-model', float(row['smoothed']) > 0 and accepted),
                                  ('stable-smoothed-model', float(row['smoothed']) > 0 and accepted and int(row['hits']) >= 3)]:
                metric = totals.setdefault(rule, dict(added=0, held_recovery_seconds=0., unsupported_added_seconds=0.))
                if enabled:
                    metric['added'] += 1
                    metric['held_recovery_seconds'] += candidate['held_fraction'] * .05
                    metric['unsupported_added_seconds'] += (1 - candidate['support_fraction']) * .05
    assert all(digest(ROOT / name) == checksum for name, checksum in inputs.items())
    atomic_json(ROOT / 'build/keyboard_tracking_recovery_audit.json', dict(inputs=inputs, totals=totals,
                decision='training_diagnostic_only', scope='Same-pitch Guitar support plus native strong Keyboard evidence; training recordings only. Existing smoothed Keyboard cells lost by final postprocessing; no native changes.'))
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    main()
