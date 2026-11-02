"""Causal display duration and attack scoring against pedal-aware MIDI.

MIDI annotation support cannot establish whether an acoustic decay is audible.
Reported unsupported duration is deliberately not named acoustic false duration.
"""
import math
from collections import defaultdict

ROWS = ('keys', 'guitar', 'voice', 'bass', 'other', 'ambiguous')


def merge(intervals):
    result = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if result and start <= result[-1][1] + 1e-12:
            result[-1] = (result[-1][0], max(end, result[-1][1]))
        else:
            result.append((start, end))
    return result


def length(intervals):
    return sum(end - start for start, end in intervals)


def intersections(a, b):
    return merge((max(start, other_start), min(end, other_end))
                 for start, end in a for other_start, other_end in b
                 if max(start, other_start) < min(end, other_end))


def score(rows, notes, rate, release_grace=.3, attack_tolerance=.15):
    if not rows or not 8000 <= rate <= 192000:
        raise ValueError('Need nonempty uniformly sampled capture and a supported rate')
    if not math.isfinite(release_grace) or release_grace < 0 or not math.isfinite(attack_tolerance) or attack_tolerance < 0:
        raise ValueError('Invalid timing tolerance')
    hop = int(rate * .05 + .5)
    horizon = int(rows[-1]['end_sample']) / rate
    predictions = {key: defaultdict(list) for key in (*ROWS, 'any_row')}
    foreign = dict(guitar_note_seconds=0., guitar_active_seconds=0., voice_note_seconds=0., voice_active_seconds=0.)
    for index, row in enumerate(rows, 1):
        if int(row['end_sample']) != index * hop:
            raise ValueError('Capture has a missing, duplicated or reordered hop')
        start, end = index * hop / rate, min(horizon, (index + 1) * hop / rate)
        active = {}
        for key in ROWS:
            if key not in row:
                raise ValueError('Missing row: ' + key)
            active[key] = {int(value) for value in row[key].split(',') if value}
            if any(not 0 <= midi <= 127 for midi in active[key]):
                raise ValueError('Invalid predicted MIDI')
        active['any_row'] = set().union(*active.values())
        for key, midis in active.items():
            for midi in midis:
                predictions[key][midi].append((start, end))
        for key in ('guitar', 'voice'):
            foreign[key + '_note_seconds'] += len(active[key]) * (end - start)
            foreign[key + '_active_seconds'] += bool(active[key]) * (end - start)
    key_intervals, allowed = defaultdict(list), defaultdict(list)
    attacks = defaultdict(list)
    censored = 0
    for note in notes:
        if note['channel'] == 9:
            continue
        start, key_end, end = note['start'], note['key_end'], note['end']
        if not all(math.isfinite(value) for value in (start, key_end, end)) or not 0 <= start < key_end <= end or not 0 <= note['midi'] <= 127:
            raise ValueError('Invalid MIDI interval')
        if start >= horizon:
            continue
        key_intervals[note['midi']].append((start, min(key_end, horizon)))
        allowed[note['midi']].append((start, min(end + release_grace, horizon)))
        deadline = min(key_end, start + attack_tolerance)
        if deadline <= horizon:
            attacks[note['midi']].append((start, deadline))
        else:
            censored += 1
    key_intervals = {midi: merge(values) for midi, values in key_intervals.items()}
    allowed = {midi: merge(values) for midi, values in allowed.items()}
    result = dict(frames=len(rows), audio_seconds=horizon, release_grace_seconds=release_grace,
                  attack_tolerance_seconds=attack_tolerance, censored_attacks=censored,
                  scope='Display state starts at each causal analysis endpoint and lasts until the next hop; annotation support is not acoustic audibility')
    for key, by_midi in predictions.items():
        by_midi = {midi: merge(values) for midi, values in by_midi.items()}
        totals = dict(held_note_seconds=0., missing_note_seconds=0., onset_gap_seconds=0.,
                      internal_dropout_seconds=0., early_release_seconds=0., entirely_missing_note_seconds=0.,
                      annotation_unsupported_note_seconds=0., matched_attacks=0, missed_attacks=0,
                      unmatched_predicted_attacks=0, attack_latency_ms=[])
        for midi, expected in key_intervals.items():
            for start, end in expected:
                detected = intersections([(start, end)], by_midi.get(midi, []))
                totals['held_note_seconds'] += end - start
                missing = end - start - length(detected)
                totals['missing_note_seconds'] += missing
                if not detected:
                    totals['entirely_missing_note_seconds'] += end - start
                    continue
                onset, release = detected[0][0] - start, end - detected[-1][1]
                totals['onset_gap_seconds'] += onset
                totals['early_release_seconds'] += release
                totals['internal_dropout_seconds'] += missing - onset - release
        for midi, detected in by_midi.items():
            totals['annotation_unsupported_note_seconds'] += length(detected) - length(intersections(detected, allowed.get(midi, [])))
        for midi in set(attacks) | set(by_midi):
            candidates = [start for start, end in by_midi.get(midi, [])]
            used = set()
            for start, deadline in sorted(attacks.get(midi, [])):
                match = next((i for i, candidate in enumerate(candidates) if i not in used and start - 1e-12 <= candidate <= deadline + 1e-12), None)
                if match is None:
                    totals['missed_attacks'] += 1
                else:
                    used.add(match)
                    totals['matched_attacks'] += 1
                    totals['attack_latency_ms'].append(round((candidates[match] - start) * 1000, 9))
            totals['unmatched_predicted_attacks'] += len(candidates) - len(used)
        result[key] = {name: round(max(0., value), 12) if isinstance(value, float) else value for name, value in totals.items()}
    result['foreign_rows'] = {name: round(value, 12) for name, value in foreign.items()}
    return result
