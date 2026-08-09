#!/usr/bin/env python3
"""Measure weak-third power-alias opportunities in expanded GAPS guitar windows."""

import argparse
import csv
import re
from collections import Counter


PITCH_CLASSES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
                 "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
ROOT = re.compile(r"^([A-G](?:#)?)(.*)$")


def levels(value):
    result = {}
    for part in value.split(","):
        name, _, number = part.partition(":")
        if name in PITCH_CLASSES and number:
            result[PITCH_CLASSES[name]] = float(number)
    return result


def root_name(label):
    match = ROOT.match(label)
    return match.group(1) if match else None


def has_plain_root(label, root):
    return any(component == root for component in label.split("="))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes")
    parser.add_argument("--third-floor", type=float, default=0.0)
    parser.add_argument("--third-ceiling", type=float, default=0.30)
    parser.add_argument("--root-floor", type=float, default=0.65)
    parser.add_argument("--fifth-floor", type=float, default=0.65)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    candidates = []
    false_qualities = Counter()
    with open(args.attributes, newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            expected = row["expected_chords"]
            detected = row["guitar_chord"]
            if not expected or detected in {"", "--"}:
                continue
            root = root_name(expected.split("/")[0])
            if root is None or not has_plain_root(detected, root):
                continue
            if f"{root}pow" in detected.split("="):
                continue
            root_pc = PITCH_CLASSES[root]
            fifth_pc = (root_pc + 7) % 12
            minor_third_pc = (root_pc + 3) % 12
            major_third_pc = (root_pc + 4) % 12
            visible = {PITCH_CLASSES[name] for name in row["guitar_pitch_classes"].split(",")
                       if name in PITCH_CLASSES}
            raw = levels(row["raw_pitch_class_levels"])
            if root_pc not in visible or fifth_pc not in visible:
                continue
            if raw.get(root_pc, 0.0) < args.root_floor or raw.get(fifth_pc, 0.0) < args.fifth_floor:
                continue
            third = max(raw.get(minor_third_pc, 0.0), raw.get(major_third_pc, 0.0))
            if minor_third_pc not in visible and major_third_pc not in visible:
                continue
            if third < args.third_floor or third > args.third_ceiling:
                continue
            quality = row["expected_chord_qualities"]
            is_positive = quality == "pow"
            if not is_positive:
                false_qualities[quality] += 1
            candidates.append((is_positive, row, root, raw.get(minor_third_pc, 0.0),
                               raw.get(major_third_pc, 0.0), raw.get(fifth_pc, 0.0)))

    positives = sum(positive for positive, *_ in candidates)
    print(f"candidates {len(candidates)} positives {positives} false {len(candidates) - positives}")
    if false_qualities:
        print("false qualities " + " ".join(
            f"{quality or '--'}={count}" for quality, count in false_qualities.most_common()))
    for positive, row, root, minor, major, fifth in candidates[:args.limit]:
        print(
            f"{'positive' if positive else 'false'} {row['recording_id']}@{row['center_seconds']} "
            f"expected={row['expected_chords']} got={row['guitar_chord']} root={root} "
            f"m3={minor:.3f} M3={major:.3f} fifth={fifth:.3f} visible={row['guitar_pitch_classes']}"
        )


if __name__ == "__main__":
    main()
