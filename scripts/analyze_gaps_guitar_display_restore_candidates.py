#!/usr/bin/env python3
"""Find GAPS chord misses with one analysis-supported tone absent from display."""

import argparse
import csv
import re
from collections import Counter


PITCH_CLASSES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
                 "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
ROOT = re.compile(r"^([A-G](?:#)?)")


def classes(value):
    return {PITCH_CLASSES[name] for name in value.split(",") if name in PITCH_CLASSES}


def root(label):
    match = ROOT.match(label)
    return PITCH_CLASSES[match.group(1)] if match else None


def has_root(label, expected_root):
    return any(root(component) == expected_root for component in label.split("="))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes")
    parser.add_argument("--limit", type=int, default=24)
    args = parser.parse_args()

    candidates = []
    by_interval = Counter()
    by_quality = Counter()
    with open(args.attributes, newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["status"] != "chord_miss" or not row["expected_chords"]:
                continue
            expected_root = root(row["expected_chords"].split("/")[0])
            if expected_root is None or not has_root(row["guitar_chord"], expected_root):
                continue
            expected = classes(row["expected_pitch_classes"])
            visible = classes(row["guitar_pitch_classes"])
            analysis = classes(row["guitar_analysis_pitch_classes"])
            missing = expected - visible
            if len(missing) != 1 or not missing <= analysis or expected_root not in visible:
                continue
            interval = next(iter(missing)) - expected_root
            interval %= 12
            by_interval[interval] += 1
            by_quality[row["expected_chord_qualities"]] += 1
            candidates.append((row, interval, next(iter(missing))))

    print(f"candidates {len(candidates)}")
    if by_interval:
        print("missing intervals " + " ".join(
            f"{interval}={count}" for interval, count in sorted(by_interval.items())))
    if by_quality:
        print("qualities " + " ".join(
            f"{quality}={count}" for quality, count in by_quality.most_common()))
    for row, interval, missing in candidates[:args.limit]:
        expected_name = next(name for name, pitch in PITCH_CLASSES.items() if pitch == missing)
        print(
            f"{row['recording_id']}@{row['center_seconds']} expected={row['expected_chords']} "
            f"got={row['guitar_chord']} missing={expected_name}(+{interval}) "
            f"visible={row['guitar_pitch_classes']} analysis={row['guitar_analysis_pitch_classes']}"
        )


if __name__ == "__main__":
    main()
