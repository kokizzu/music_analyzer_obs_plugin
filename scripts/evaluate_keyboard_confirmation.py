#!/usr/bin/env python3
"""Recording-disjoint training screen for a first-hit Keyboard verifier."""
import argparse
import csv
import json
import math
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import features, lower_probability
from evaluate_next_detection import fit_forest
from routing_duration_baseline import ROOT, atomic_json, digest
from midi_sustain_reference import read_intervals
from routing_duration_score import score


def isolated_additions(frames, accepted, hop):
    visible = {int(f['end_sample']): {int(v) for v in f['keys'].split(',') if v} for f in frames}
    return sum(c['midi'] not in visible.get(c['end_sample'] - hop, set()) and
               c['midi'] not in visible.get(c['end_sample'] + hop, set()) for c in accepted)


def score_acceptances(name, accepted):
    path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(path.read_text())
    sample = next(s for s in baseline['selection'] if s['id'] == name)
    midi = ROOT / sample['midi']
    assert digest(midi) == sample['midi_sha256']
    notes = read_intervals(midi.read_bytes())
    native = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7'
    reference = json.loads((native / 'report.json').read_text())
    path = native / (name + '.tsv')
    assert digest(path) == reference['recordings'][name]['sha256']
    additions = {}
    for case in accepted:
        additions.setdefault(case['end_sample'], set()).add(case['midi'])
    original, proposed = [], []
    with path.open() as stream:
        for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r: r['end_sample']):
            frame = next(group)
            original.append(frame)
            pitches = {int(v) for v in frame['keys'].split(',') if v} | additions.get(int(endpoint), set())
            proposed.append(dict(frame, keys=','.join(str(v) for v in sorted(pitches))))
    before, after = (score(frames, notes, baseline['recordings'][name]['rate'])['keys'] for frames in (original, proposed))
    timing = {key: dict(before=before[key], after=after[key]) for key in ('matched_attacks', 'onset_gap_seconds', 'internal_dropout_seconds', 'early_release_seconds')}
    hop = round(baseline['recordings'][name]['rate'] * .05)
    timing['isolated_additions'] = isolated_additions(proposed, accepted, hop)
    return timing


def values(case, joint=None):
    row = case['candidate']
    result = features(row) + [case['midi'] / 127., float(case['tracking']['raw']), float(case['tracking']['envelope'])]
    if joint is not None:
        cue = joint[case['recording'], case['end_sample'], case['midi']]
        result += [cue[k] for k in ('relative_activation', 'activation_fraction', 'explained_projection', 'residual')]
    assert all(math.isfinite(v) for v in result)
    return result


def positive(case, pedal_support=False):
    # A complete next causal hop must be held. Pedal-only support is not an
    # attack-training positive, and partial boundary hops remain negatives.
    return case['unsupported_seconds'] < 1e-8 and (pedal_support or case['held_seconds'] >= .05 - 1e-8)


def main():
    import numpy as np
    parser = argparse.ArgumentParser()
    parser.add_argument('--joint', action='store_true')
    parser.add_argument('--empirical-cutoff', action='store_true')
    parser.add_argument('--pedal-support', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'build/keyboard_confirmation_audit.json'
    audit = json.loads(path.read_text())
    assert set(audit['recordings']) == {'training-1', 'training-2', 'training-3'}
    assert all(digest(ROOT / p) == h for p, h in audit['inputs'].items())
    inputs = dict(audit_sha256=digest(path), script_sha256=digest(Path(__file__)),
                  helpers={p: digest(ROOT / p) for p in ('scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_next_detection.py')},
                  minimum_threshold=0. if args.empirical_cutoff else .95, negative_margin=.01,
                  split='Leave one complete training recording out; cutoff from fitting-recording negatives only')
    inputs['label'] = 'Complete next hop supported by key/CC64 plus existing grace' if args.pedal_support else 'Complete next hop held'
    joint = None
    if args.joint:
        pointer = json.loads((ROOT / 'build/joint_pitch/current.json').read_text())
        joint_path = ROOT / pointer['report']
        assert digest(joint_path) == pointer['sha256']
        captured = json.loads(joint_path.read_text())
        assert captured['complete'] and captured['inputs']['audit_sha256'] == digest(path)
        inputs['joint_sha256'] = digest(joint_path)
        inputs['joint_report'] = pointer['report']
        joint = {(name, c['end_sample'], c['midi']): c for name, r in captured['recordings'].items() for c in r['cases']}
    for name, recording in audit['recordings'].items():
        for case in recording['cases']:
            case['recording'] = name
    folds = {}
    for held_group in audit['recordings']:
        train = [case for name, recording in audit['recordings'].items() if name != held_group for case in recording['cases']]
        validation = audit['recordings'][held_group]['cases']
        x = np.array([values(case, joint) for case in train])
        y = np.array([0 if positive(case, args.pedal_support) else 1 for case in train])
        assert (y == 0).sum() >= 8 and (y == 1).sum() >= 24
        _, model = fit_forest(x, y, 2)
        wrong_max = max(lower_probability(model, values(case, joint)) for case in train if not positive(case, args.pedal_support))
        threshold = min(1., max(inputs['minimum_threshold'], wrong_max + inputs['negative_margin']))
        metric = dict(candidates=len(validation), fully_held=sum(positive(c) for c in validation), accepted=0,
                      held_recovery_seconds=0., unsupported_added_seconds=0., nonheld_accepted=0)
        accepted = []
        for case in validation:
            probability = lower_probability(model, values(case, joint))
            if probability < threshold:
                continue
            metric['accepted'] += 1
            metric['held_recovery_seconds'] += case['held_seconds']
            metric['unsupported_added_seconds'] += case['unsupported_seconds']
            metric['nonheld_accepted'] += not positive(case, args.pedal_support)
            accepted.append(dict(end_sample=case['end_sample'], midi=case['midi'], probability=probability))
        folds[held_group] = dict(training_rows=len(train), training_positive_rows=int((y == 0).sum()),
                                threshold=threshold, wrong_max=wrong_max, metrics=metric, accepted=accepted, model=model,
                                timing=score_acceptances(held_group, accepted))
        print(held_group, json.dumps({k: v for k, v in folds[held_group].items() if k != 'model'}), flush=True)
    passed = sum(f['metrics']['held_recovery_seconds'] for f in folds.values()) > 0 and all(
        f['metrics']['unsupported_added_seconds'] < 1e-8 and not f['metrics']['nonheld_accepted'] and
        not f['timing']['isolated_additions'] and
        f['timing']['matched_attacks']['after'] >= f['timing']['matched_attacks']['before'] for f in folds.values())
    result = dict(inputs=inputs, folds=folds, decision='prepare_disjoint_calibration' if passed else 'reject',
                  scope='Training-only leave-recording-out screen. No outside instrument controls, fourth-recording calibration, held-out evaluation, native behavior change or model promotion. Passing this screen alone is insufficient for any runtime use.')
    assert digest(path) == inputs['audit_sha256'] and digest(Path(__file__)) == inputs['script_sha256']
    output = ('joint' if args.joint else 'keyboard') + '_confirmation_evaluation' + ('_empirical' if args.empirical_cutoff else '') + ('_pedal' if args.pedal_support else '') + '.json'
    atomic_json(ROOT / 'build' / output, result)
    print('First-hit verifier screen:', result['decision'], flush=True)


if __name__ == '__main__':
    main()
