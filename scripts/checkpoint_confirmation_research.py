#!/usr/bin/env python3
"""Verify the rejected first-hit screens and publish only research artifacts."""
import argparse
import ast
import json
import subprocess

from evaluate_guitar_duplicate_model import lower_probability
from evaluate_keyboard_confirmation import values, positive, score_acceptances
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'scripts/evaluate_keyboard_confirmation.py', 'scripts/joint_pitch_reference.py',
         'scripts/capture_joint_pitch.py', 'scripts/checkpoint_confirmation_research.py',
         'tests/test_keyboard_confirmation.py', 'tests/test_joint_pitch_reference.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    audit_path = ROOT / 'build/keyboard_confirmation_audit.json'
    audit = read(audit_path)
    assert all(digest(ROOT / p) == h for p, h in audit['inputs'].items())
    pointer = read(ROOT / 'build/joint_pitch/current.json')
    capture_path = ROOT / pointer['report']
    captured = read(capture_path)
    assert captured['complete'] and digest(capture_path) == pointer['sha256']
    assert captured['inputs']['audit_sha256'] == digest(audit_path)
    assert captured['inputs']['script_sha256'] == digest(ROOT / 'scripts/capture_joint_pitch.py')
    assert captured['inputs']['helper_sha256'] == digest(ROOT / 'scripts/joint_pitch_reference.py')
    assert all(digest(ROOT / p) == h for p, h in captured['inputs']['samples'].items())
    assert digest(capture_path.parent / 'dictionary.json') == captured['dictionary_sha256']
    assert sum(r['frames'] for r in captured['recordings'].values()) == 3600
    assert sum(len(r['cases']) for r in captured['recordings'].values()) == 980
    joint = {(name, c['end_sample'], c['midi']): c for name, r in captured['recordings'].items() for c in r['cases']}
    for name, recording in audit['recordings'].items():
        for case in recording['cases']:
            case['recording'] = name
    count = 0
    for prefix in ('keyboard', 'joint'):
        for empirical in (False, True):
            for pedal in (False, True):
                name = prefix + '_confirmation_evaluation' + ('_empirical' if empirical else '') + ('_pedal' if pedal else '') + '.json'
                report = read(ROOT / 'build' / name)
                assert report['decision'] == 'reject'
                assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/evaluate_keyboard_confirmation.py')
                assert report['inputs']['audit_sha256'] == digest(audit_path)
                assert all(digest(ROOT / p) == h for p, h in report['inputs']['helpers'].items())
                cues = joint if prefix == 'joint' else None
                if cues is not None:
                    assert report['inputs']['joint_sha256'] == digest(capture_path)
                assert report['inputs']['minimum_threshold'] == (0 if empirical else .95)
                for held_group, fold in report['folds'].items():
                    train = [c for n, r in audit['recordings'].items() if n != held_group for c in r['cases']]
                    wrong_max = max(lower_probability(fold['model'], values(c, cues)) for c in train if not positive(c, pedal))
                    assert wrong_max == fold['wrong_max']
                    assert fold['threshold'] == min(1., max(report['inputs']['minimum_threshold'], wrong_max + .01))
                    accepted = []
                    for case in audit['recordings'][held_group]['cases']:
                        probability = lower_probability(fold['model'], values(case, cues))
                        if probability >= fold['threshold']:
                            accepted.append(dict(end_sample=case['end_sample'], midi=case['midi'], probability=probability))
                    assert accepted == fold['accepted']
                    assert score_acceptances(held_group, accepted) == fold['timing']
                count += 1
    assert 'experimental_keyboard_confirmation' not in git('show', 'HEAD:src/analyzer.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified', count, 'rejected recording-disjoint screens and 3600 causal joint-fit windows; runtime unchanged', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    verify()
    if not (args.stage or args.publish):
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    for target in ('test-keyboard-confirmation', 'test-joint-pitch', 'test-routing-duration-score'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    git('add', '--', *PATHS)
    assert set(git('diff', '--cached', '--name-only').splitlines()) <= set(PATHS)
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, text=True, capture_output=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    (ROOT / 'build/confirmation_research_staged.diff').write_text(git('diff', '--cached'))
    print(git('diff', '--cached', '--stat'), flush=True)
    if args.stage:
        return
    print(git('commit', '-m', 'Screen causal first-hit verifiers and joint spectral pitch evidence'), flush=True)
    print(git('push', remote, 'HEAD:' + primary), flush=True)
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
