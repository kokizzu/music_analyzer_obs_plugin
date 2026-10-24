#!/usr/bin/env python3
"""Compare physical onset-scoring hypotheses on captured three-second histories."""
import argparse
import csv
import json
import math
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'build/accuracy_goal_bpm/source-history-baseline-20261014'


def close(value, expected):
    return value > 0 and abs(value - expected) <= 8


def peaks(frames, interval, mode):
    if mode in ('independent-sources', 'balanced-sources'):
        separate = []
        for source in range(4):
            values = [f[source] for f in frames]
            maximum = max(values, default=0)
            floor = max(.045, maximum * .25)
            source_peaks = []
            for index, value in enumerate(values):
                if value < floor or (index and value < values[index-1]) or (index+1 < len(frames) and value < values[index+1]):
                    continue
                body, subdivision = frames[index][4:6]
                quality = max(0, min(1, body / (body+subdivision))) if body+subdivision > 1e-6 else .5
                strength = value / maximum if mode == 'balanced-sources' else value
                peak = [index*interval, strength*(.62+.38*quality), quality, 1 << source]
                if source_peaks and 0 < peak[0]-source_peaks[-1][0] < .16:
                    if peak[1] > source_peaks[-1][1]:
                        source_peaks[-1] = peak
                else:
                    source_peaks.append(peak)
            separate.extend(source_peaks)
        output = []
        for peak in sorted(separate):
            if output and abs(peak[0]-output[-1][0]) < .04:
                output[-1][1] = max(output[-1][1], peak[1])
                output[-1][2] = max(output[-1][2], peak[2])
                output[-1][3] |= peak[3]
            else:
                output.append(peak)
        return output
    strength = []
    for f in frames:
        rhythmic = max(f[:3])
        strength.append(max(rhythmic, f[3]) if f[3] >= .045 and f[3] >= rhythmic * 1.15 else rhythmic)
    output = []
    for index, value in enumerate(strength):
        if value < .045 or (index and value < strength[index-1]) or (index+1 < len(frames) and value < strength[index+1]):
            continue
        time = index * interval
        if mode == 'interpolated' and 0 < index < len(frames)-1:
            previous, following = strength[index-1], strength[index+1]
            denominator = previous - 2 * value + following
            if denominator < -1e-6:
                time += max(-.5, min(.5, .5 * (previous-following) / denominator)) * interval
        body, subdivision = frames[index][4:6]
        quality = max(0, min(1, body / (body+subdivision))) if body+subdivision > 1e-6 else .5
        weighted = value * (.62 + quality * .38)
        mask = sum(1 << source for source in range(4) if frames[index][source] >= value * .72)
        peak = [time, weighted, quality, mask]
        if output and 0 < time-output[-1][0] < .16:
            if weighted > output[-1][1]:
                output[-1] = peak
            else:
                output[-1][2] = max(output[-1][2], quality)
                output[-1][3] |= mask
        else:
            output.append(peak)
    return output


def estimate(items, mode='current', interval=.05):
    if len(items) < 3 or items[-1][0]-items[0][0] < .45:
        return 0
    winner, best = 0, 0
    total = sum(math.sqrt(max(p[1], 0)) for p in items)
    for bpm in range(50, 221):
        period = 60 / bpm
        tolerance = max(.035, min(.085, period * .12))
        if mode == 'quantization-tolerance':
            tolerance = max(tolerance, min(.085, interval * .70))
        score = 0
        phase = [math.sqrt(max(p[1], 0)) for p in items]
        for older, a in enumerate(items):
            best_direct = 0
            for newer in range(older+1, len(items)):
                b = items[newer]
                delta = b[0]-a[0]
                beats = math.floor(delta / period + .5)
                if not 1 <= beats <= 8:
                    continue
                error = abs(delta-beats*period)
                if error > tolerance:
                    continue
                drum = bool(a[3] & 5 and b[3] & 5)
                if mode == 'same-drum-source':
                    drum = bool(a[3] & b[3] & 5)
                bass = bool(a[3] & b[3] & 2)
                tonal = bool(a[3] & b[3] & 8)
                mixed = bool(a[3] & 8 and b[3] & 7 or b[3] & 8 and a[3] & 7)
                source = 1 if drum else .75 if bass else .62 if tonal else .38 if mixed else .18
                body = .68 + .32 * math.sqrt(max(a[2]*b[2], 0))
                match = 1 - error / tolerance
                strength = (a[1]*b[1]) ** (1 if mode == 'strong-body' else .5)
                pair = strength * (1 if beats == 1 else .18) * source * body * match * match
                if mode == 'nearest-direct':
                    best_direct = max(best_direct, pair if beats == 1 else 0)
                else:
                    score += pair
                phase[older] += math.sqrt(max(b[1], 0)) * match
                phase[newer] += math.sqrt(max(a[1], 0)) * match
            if mode == 'nearest-direct':
                score += best_direct
        if len(items) >= 4 and score > 0 and total > 1e-6:
            score *= .45 + .55 * max(0, min(1, max(phase) / total))
        if mode == 'grid-completeness' and score > 0:
            best_coverage = 0
            for anchor in items:
                begin = math.ceil((items[0][0]-anchor[0])/period)
                end = math.floor((items[-1][0]-anchor[0])/period)
                cells = end-begin+1
                if cells < 3:
                    continue
                filled = sum(any(abs(p[0]-(anchor[0]+beat*period)) <= tolerance for p in items)
                             for beat in range(begin, end+1))
                best_coverage = max(best_coverage, filled/cells)
            score *= best_coverage * best_coverage
        if score > best:
            best, winner = score, bpm
    return winner


def direct_body_matches(items, bpm):
    if bpm <= 0:
        return 0
    period = 60/bpm
    tolerance = max(.035, min(.085, period*.12))
    return sum(any(abs(b[0]-a[0]-period) <= tolerance and a[2] >= .65 and b[2] >= .65
                   for b in items[index+1:]) for index, a in enumerate(items))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--events-only', action='store_true')
    args = parser.parse_args()
    checkpoint = json.loads((args.directory / 'checkpoint.json').read_text())
    if len(checkpoint['corpora']) != 3:
        raise SystemExit('Source-history replay has not completed; wait for its live process')
    corpora = {}
    for path in sorted(args.directory.glob('*-source-history.tsv')):
        records = defaultdict(list)
        with path.open() as stream:
            for row in csv.reader(stream, delimiter='\t'):
                records[row[0]].append([float(v) for v in row[1:]])
        corpora[path.name.removesuffix('-source-history.tsv')] = records
        expected_count = checkpoint['corpora'][path.name.removesuffix('-source-history.tsv')]['metrics']['recordings']
        if len(records) != expected_count:
            raise SystemExit('Source-history recording count does not match its completed checkpoint')
    if len(corpora) != 3:
        raise SystemExit('All three source-history corpora are required')
    report = {}
    modes = ('current', 'interpolated', 'same-drum-source', 'nearest-direct', 'strong-body',
             'independent-sources', 'balanced-sources', 'quantization-tolerance', 'grid-completeness')
    if args.events_only:
        modes = ('current', 'precise-events', 'precise-body-events', 'harmonic-event-consensus')
    for mode in modes:
        report[mode] = {}
        for corpus, records in corpora.items():
            counts = {'total': len(records), 'correct': 0, 'half_double': 0, 'other_wrong': 0,
                      'missing': 0, 'improved': 0, 'regressed': 0, 'reproduction_mismatches': 0}
            captured_events = defaultdict(list)
            if mode.startswith('precise-') or mode == 'harmonic-event-consensus':
                with (args.directory / (corpus + '-source-history.tsv.events')).open() as stream:
                    for line in csv.reader(stream, delimiter='\t'):
                        captured_events[line[0]].append([float(v) for v in line[1:]])
            for record_id, rows in records.items():
                expected, interval, actual = rows[0][:3]
                frames = [r[4:] for r in rows]
                value = estimate(peaks(frames, interval, mode), mode, interval)
                if mode.startswith('precise-') or mode == 'harmonic-event-consensus':
                    items = []
                    for expected_event, actual_event, time, strength, body, subdivision in captured_events[record_id]:
                        quality = body/(body+subdivision) if body+subdivision > 1e-6 else .5
                        if mode == 'precise-body-events' and body < max(.045, subdivision * 1.15):
                            continue
                        items.append([time, strength*(.62+.38*quality), quality, 5 if body >= subdivision else 8])
                    value = estimate(items)
                    if mode == 'harmonic-event-consensus':
                        body_items = [p for p in items if p[2] >= .65]
                        body_value = estimate(body_items)
                        harmonic = actual > 0 and value > 0 and min(abs(actual*2-value), abs(actual/2-value)) <= 4
                        if not (harmonic and abs(body_value-value) <= 4 and direct_body_matches(items, value) >= 3):
                            value = actual
                counts['correct'] += close(value, expected)
                counts['missing'] += value <= 0
                counts['half_double'] += value > 0 and not close(value, expected) and (
                    close(value*2, expected) or close(value/2, expected))
                counts['other_wrong'] += value > 0 and not close(value, expected) and not (
                    close(value*2, expected) or close(value/2, expected))
                counts['improved'] += close(value, expected) and not close(actual, expected)
                counts['regressed'] += close(actual, expected) and not close(value, expected)
                counts['reproduction_mismatches'] += mode == 'current' and value != actual
            report[mode][corpus] = counts
            print(mode, corpus, json.dumps(counts), flush=True)
    if any(r['reproduction_mismatches'] for r in report['current'].values()):
        raise SystemExit('Offline scorer disagrees with the runtime baseline; do not use variant results')
    report_name = 'event_scorer_hypotheses.json' if args.events_only else 'scorer_hypotheses.json'
    (args.directory / report_name).write_text(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
