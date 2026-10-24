#!/usr/bin/env python3
"""Test physical Kick-quarter/Snare-backbeat agreement in causal 3 s histories."""
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import median

from evaluate_source_tempo_histories import peaks, estimate, close

ROOT = Path(__file__).resolve().parents[1]


def backbeat_candidate(actual, kick, snare):
    if actual <= 0 or len(kick) < 4 or len(snare) < 3:
        return actual
    if min(max(p[1] for p in kick), max(p[1] for p in snare)) < .2:
        return actual
    intervals = [b[0] - a[0] for a, b in zip(snare, snare[1:])]
    spacing = median(intervals)
    if spacing <= 0 or max(abs(value - spacing) for value in intervals) > .075:
        return actual
    candidate = round(120 / spacing)
    if not 50 <= candidate <= 220 or min(abs(candidate - actual * 2), abs(candidate * 2 - actual)) > 4:
        return actual
    period = 60 / candidate
    direct = sum(abs(b[0] - a[0] - period) <= .06 for a, b in zip(kick, kick[1:]))
    aligned = sum(any(abs((p[0] - s[0]) / period - round((p[0] - s[0]) / period)) * period <= .06 for s in snare) for p in kick)
    return candidate if direct >= 3 and aligned / len(kick) >= .8 else actual


def main():
    directory = ROOT / "build/accuracy_goal_bpm/live-cadence-baseline-20261014"
    metrics, inputs, changes = {}, {}, []
    for corpus in ("Ballroom", "FiloBass", "GTZAN-Rhythm"):
        path = directory / (corpus + "-source-history.tsv")
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        recordings = defaultdict(list)
        with path.open() as stream:
            for row in csv.reader(stream, delimiter="\t"):
                recordings[row[0]].append([float(value) for value in row[1:]])
        result = metrics[corpus] = dict(recordings=len(recordings), changes=0, gains=0, correct_losses=0)
        for recording, rows in recordings.items():
            expected, interval, actual = rows[0][:3]
            frames = [row[4:] for row in rows]
            assert estimate(peaks(frames, interval, "current")) == actual
            isolated = []
            for source in (0, 2):
                selected = [[value if index == source or index >= 4 else 0 for index, value in enumerate(frame)] for frame in frames]
                isolated.append(peaks(selected, interval, "current"))
            candidate = backbeat_candidate(actual, *isolated)
            result["changes"] += candidate != actual
            result["gains"] += close(candidate, expected) and not close(actual, expected)
            result["correct_losses"] += close(actual, expected) and not close(candidate, expected)
            if candidate != actual:
                changes.append(dict(corpus=corpus, recording=recording, expected=expected, actual=actual, candidate=candidate))
    report = dict(metrics=metrics, inputs=inputs, changed=changes,
                  decision="candidate" if any(row["gains"] for row in metrics.values()) and not any(row["correct_losses"] for row in metrics.values()) else "reject",
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="Historical causal three-second Kick/Snare screening only; no genre/source/annotation input to selection")
    output = ROOT / "build/next_detection/backbeat_tempo.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
