#!/usr/bin/env python3
"""Training-only screen of frozen Guitar verifier extrapolation; no promotion."""
import csv
import json
from itertools import groupby
from pathlib import Path

from evaluate_guitar_duplicate_model import eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from routing_duration_baseline import ROOT, atomic_json, digest
from midi_sustain_reference import read_intervals
from routing_duration_score import score
from evaluate_voice_duplicate import protected_voice


def screen(path, model):
    previous = set()
    result = dict(voice_candidates=0, voice_removed=0, gap_candidates=0, keys_added=0)
    changed = dict(voice=[], keys=[])
    with path.open() as stream:
        for endpoint, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
            rows = list(frame)
            context = frame_context(rows)
            current = {int(value) for value in rows[0]['keys'].split(',') if value}
            for row in rows:
                midi = int(row['midi'])
                if midi < 0:
                    continue
                voice = row['midi'] in row['voice'].split(',') and midi in current
                gap = midi in previous and midi not in current and row['midi'] in row['guitar'].split(',')
                if not (voice or gap):
                    continue
                # Reuse the exact physical eligibility checks, replacing only
                # the display-membership prerequisite for the audited domain.
                probe = dict(row, guitar=row['midi'], keys=row['midi'])
                if not eligible(probe):
                    continue
                accepted = lower_probability(model['model'], features(row) + context) >= model['threshold']
                if voice:
                    result['voice_candidates'] += 1
                    result['voice_removed'] += accepted
                    if accepted:
                        changed['voice'].append((int(endpoint), midi))
                if gap:
                    result['gap_candidates'] += 1
                    result['keys_added'] += accepted
                    if accepted:
                        changed['keys'].append((int(endpoint), midi))
            # Original display only: never let repaired hops extend themselves.
            previous = current
    return result, changed


def main():
    canonical = ROOT / 'models/piano_guitar_verifier.json'
    model = json.loads(canonical.read_text())
    inputs = {str(canonical.relative_to(ROOT)): digest(canonical),
              str(Path(__file__).relative_to(ROOT)): digest(Path(__file__))}
    for name in ('evaluate_guitar_duplicate_model.py', 'evaluate_guitar_music_model.py',
                 'midi_sustain_reference.py', 'routing_duration_score.py', 'evaluate_voice_duplicate.py'):
        inputs['scripts/' + name] = digest(ROOT / 'scripts' / name)
    metrics = {}
    for kind, relative in [('piano', 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'),
                           ('controls', 'build/routing_controls/84b9eb144888ea8d/report.json')]:
        source = ROOT / relative
        report = json.loads(source.read_text())
        assert report['complete']
        inputs[relative] = digest(source)
        selected = {sample['id']: sample for sample in report['inputs'].get('selection', [])}
        for name, recording in report['recordings'].items():
            sample = selected.get(name, {})
            if recording.get('cohort', sample.get('cohort')) != 'training':
                continue
            if kind == 'piano' and name == 'training-4':
                continue  # Preserve the existing calibration recording.
            path = source.parent / (name + '.tsv')
            assert digest(path) == recording['sha256']
            inputs[str(path.relative_to(ROOT))] = digest(path)
            result, changed = screen(path, model)
            if kind == 'piano':
                baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
                baseline = json.loads(baseline_path.read_text())
                inputs[str(baseline_path.relative_to(ROOT))] = digest(baseline_path)
                item = next(value for value in baseline['selection'] if value['id'] == name)
                midi_path = ROOT / item['midi']
                assert digest(midi_path) == item['midi_sha256']
                inputs[str(midi_path.relative_to(ROOT))] = digest(midi_path)
                frames_path = baseline_path.parent / (name + '.tsv')
                assert digest(frames_path) == baseline['recordings'][name]['frames_sha256']
                inputs[str(frames_path.relative_to(ROOT))] = digest(frames_path)
                with frames_path.open() as stream:
                    original = list(csv.DictReader(stream, delimiter='\t'))
                additions = set(changed['keys'])
                repaired = [dict(row, keys=','.join(str(value) for value in sorted(
                    {int(v) for v in row['keys'].split(',') if v} |
                    {midi for endpoint, midi in additions if endpoint == int(row['end_sample'])}))) for row in original]
                notes = read_intervals(midi_path.read_bytes())
                rate = baseline['recordings'][name]['rate']
                before, after = (score(frames, notes, rate)['keys'] for frames in (original, repaired))
                result['held_recovery_seconds'] = before['missing_note_seconds'] - after['missing_note_seconds']
                result['unsupported_added_seconds'] = after['annotation_unsupported_note_seconds'] - before['annotation_unsupported_note_seconds']
            else:
                result.update(held_recovery_seconds=0., unsupported_added_seconds=0.)
            result['protected_voice_losses'] = sum(
                protected_voice(sample, midi)
                for _, midi in changed['voice']) if kind == 'controls' else 0
            # Any Keys addition on an isolated non-Keyboard control is wrong
            # instrument routing, irrespective of its pitch annotation.
            result['wrong_control_keys_added'] = len(changed['keys']) if kind == 'controls' else 0
            metrics[kind + '/' + name] = result
    assert all(digest(ROOT / path) == checksum for path, checksum in inputs.items())
    totals = {kind: {key: sum(value[key] for name, value in metrics.items() if name.startswith(kind + '/'))
                     for key in next(iter(metrics.values()))} for kind in ('piano', 'controls')}
    result = dict(inputs=inputs, recordings=metrics, totals=totals,
                  decision='diagnostic_only_no_runtime_change',
                  scope='Training recordings only; no refit or threshold tuning; frozen Guitar model is outside its trained membership domain. Piano additions require MIDI duration scoring and native replay before acceptance. Controls protect Voice pitches and reject every wrong Keyboard addition.')
    atomic_json(ROOT / 'build/voice_duration_candidate_audit.json', result)
    print(json.dumps(dict(totals=totals, decision=result['decision']), indent=2))


if __name__ == '__main__':
    main()
