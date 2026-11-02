#!/usr/bin/env python3
"""Compare actual primary-native consensus against frozen offline decisions."""
import argparse
import csv
import fcntl
import hashlib
import json
from itertools import groupby
from pathlib import Path
import subprocess

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from evaluate_routing_consensus import confirmed
from evaluate_voice_duplicate import decisions, protected_voice
from routing_duration_baseline import ROOT, atomic_json, digest


def load_build():
    pointer = json.loads((ROOT / 'build/routing_consensus_trial/current.json').read_text())
    path = ROOT / pointer['build']
    assert digest(path) == pointer['sha256']
    build = json.loads(path.read_text())
    assert digest(path.parent / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['assets'].items())
    return path, build


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    build_path, build = load_build()
    sources = [('single', 'build/routing_controls/84b9eb144888ea8d/report.json'),
               ('poly', 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json'),
               ('music', 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json')] if args.controls else [
               ('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json')]
    model_path = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(model_path.read_text())
    inputs = dict(build_sha256=digest(build_path), model_sha256=digest(model_path), controls=args.controls,
                  script_sha256=digest(Path(__file__)), sources={path: digest(ROOT / path) for _, path in sources},
                  helpers={p: digest(ROOT / p) for p in ('scripts/evaluate_routing_consensus.py', 'scripts/evaluate_voice_duplicate.py',
                           'scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_guitar_music_model.py')})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_consensus_pair' / key
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        replay(inputs, sources, model, build_path.parent / 'pair', directory)


def timing(values, rate):
    ordered = sorted(values)
    return dict(p50=ordered[(len(ordered) - 1) // 2], p99=ordered[int((len(ordered) - 1) * .99)],
                maximum=ordered[-1], deadline_misses=sum(value > int(rate * .05 + .5) / rate * 1000 for value in values))


def inspect_frames(path, rate, sample=None, poly=False, expected=None, predicted=None):
    result = dict(windows=0, guitar_removed=0, voice_removed=0, protected_guitar_changes=0, protected_voice_changes=0)
    before_times, after_times = [], []
    with path.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            result['windows'] += 1
            endpoint = row['end_sample']
            assert int(endpoint) == result['windows'] * int(rate * .05 + .5)
            assert row['any_lost'] == row['unrelated_difference'] == '' and row['bpm_changed'] == row['survivor_changed'] == '0'
            if expected is not None:
                assert all(row[key] == expected[endpoint][key] for key in ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
            for kind in ('guitar', 'voice'):
                before, after = ({int(v) for v in row[key].split(',') if v} for key in (kind, 'after_' + kind))
                assert after <= before
                removed = before - after
                if predicted is not None:
                    assert removed == predicted[endpoint][kind], 'Actual native consensus differs from frozen offline decisions'
                result[kind + '_removed'] += len(removed)
                if poly and kind == 'guitar':
                    result['protected_guitar_changes'] += len(removed)
                elif sample and kind == 'guitar' and sample['family'] == 'guitar':
                    result['protected_guitar_changes'] += sample['midi'] in removed
                elif sample and kind == 'voice':
                    result['protected_voice_changes'] += sum(protected_voice(sample, midi) for midi in removed)
            before_times.append(float(row['before_ms']))
            after_times.append(float(row['after_ms']))
    result.update(sha256=digest(path), before_ms=timing(before_times, rate), after_ms=timing(after_times, rate))
    return result


def replay(inputs, sources, model, binary, directory):
    checkpoint = directory / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False, passed=False)
    assert state['inputs'] == inputs
    for kind, relative in sources:
        path = ROOT / relative
        report = json.loads(path.read_text())
        assert report['complete']
        selected = {row['id']: row for row in report['inputs'].get('selection', [])}
        for name, entry in report['recordings'].items():
            capture = path.parent / (name + '.tsv')
            assert digest(capture) == entry['sha256']
            expected, predicted, guitar_hits, voice_hits = {}, {}, {}, {}
            with capture.open() as stream:
                for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                    rows = list(frame)
                    context = frame_context(rows)
                    guitar_predicted = {int(row['midi']) for row in rows if eligible(row) and lower_probability(model['model'], features(row) + context) >= model['threshold']}
                    guitar, guitar_hits = confirmed(guitar_predicted, guitar_hits)
                    voice, voice_hits = confirmed(decisions(rows, model), voice_hits)
                    expected[endpoint], predicted[endpoint] = rows[0], dict(guitar=guitar, voice=voice)
            if kind == 'piano':
                base = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267'
                baseline = json.loads((base / 'report.json').read_text())
                raw, rate = base / (name + '.f32'), baseline['recordings'][name]['rate']
            else:
                raw, rate = path.parent / (name + '.f32'), entry['rate']
            key = kind + '-' + name
            destination = directory / (key + '.tsv')
            if key in state['recordings']:
                assert digest(destination) == state['recordings'][key]['sha256']
            else:
                temporary = destination.with_suffix('.pending.tsv')
                subprocess.run([str(binary), str(raw), str(rate), str(temporary)], check=True, timeout=3600)
                temporary.replace(destination)
            result = inspect_frames(destination, rate, selected.get(name), kind in ('poly', 'music'), expected, predicted)
            assert result['windows'] == len(expected)
            result.update(cohort=kind + '-' + entry.get('cohort', selected.get(name, {}).get('cohort', 'unknown')), raw_sha256=digest(raw))
            state['recordings'][key] = result
            atomic_json(checkpoint, state)
            print(key, 'removed G/V', result['guitar_removed'], result['voice_removed'],
                  'protected changes', result['protected_guitar_changes'], result['protected_voice_changes'], flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256']
    state['complete'] = True
    state['passed'] = not any(row['protected_guitar_changes'] or row['protected_voice_changes'] or row['after_ms']['deadline_misses'] for row in state['recordings'].values())
    if not inputs['controls']:
        state['passed'] &= all(any(row['cohort'] == 'piano-heldout' and row[kind + '_removed'] for row in state['recordings'].values()) for kind in ('guitar', 'voice'))
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), 'passed', state['passed'], flush=True)
    assert state['passed']


if __name__ == '__main__':
    main()
