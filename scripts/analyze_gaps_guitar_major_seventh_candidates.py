#!/usr/bin/env python3
"""Measure display-suppressed major-seventh aliases in expanded GAPS windows."""

import argparse
import csv
import re
from collections import Counter


PITCH_CLASSES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
                 "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
ROOT = re.compile(r"^([A-G](?:#)?)(.*)$")


def classes(value):
    return {PITCH_CLASSES[name] for name in value.split(",") if name in PITCH_CLASSES}


def levels(value):
    result = {}
    for part in value.split(","):
        name, _, number = part.partition(":")
        if name in PITCH_CLASSES and number:
            result[PITCH_CLASSES[name]] = float(number)
    return result


def parse_root(label):
    match = ROOT.match(label)
    return (PITCH_CLASSES[match.group(1)], match.group(1), match.group(2)) if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes")
    parser.add_argument("--seventh-floor", type=float, default=0.22)
    parser.add_argument("--seventh-ceiling", type=float, default=0.30)
    parser.add_argument(
        "--allow-analysis-absent",
        action="store_true",
        help="also measure raw-supported sevenths that final analysis pruning omitted",
    )
    parser.add_argument(
        "--require-analysis-absent",
        action="store_true",
        help="only measure raw-supported sevenths that final analysis pruning omitted",
    )
    parser.add_argument(
        "--require-single-component",
        action="store_true",
        help="only consider an unambiguous, single-component detected chord",
    )
    parser.add_argument(
        "--detection-seventh-floor",
        type=float,
        default=0.0,
        help="require direct pre-prune guitar detection support for the seventh",
    )
    parser.add_argument("--limit", type=int, default=16)
    args = parser.parse_args()
    if args.allow_analysis_absent and args.require_analysis_absent:
        parser.error("--allow-analysis-absent and --require-analysis-absent are mutually exclusive")

    candidates = []
    false_qualities = Counter()
    with open(args.attributes, newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            expected_root = parse_root(row["expected_chords"].split("/")[0]) if row["expected_chords"] else None
            if expected_root is None:
                continue
            root_pc, root_name, _ = expected_root
            plain_root = False
            has_major7 = False
            for component in row["guitar_chord"].split("="):
                parsed = parse_root(component)
                if parsed is None or parsed[0] != root_pc:
                    continue
                plain_root = plain_root or parsed[2] == ""
                has_major7 = has_major7 or parsed[2] in {"maj7", "maj9"}
            if not plain_root or has_major7:
                continue
            if args.require_single_component and "=" in row["guitar_chord"]:
                continue
            visible = classes(row["guitar_pitch_classes"])
            analysis = classes(row["guitar_analysis_pitch_classes"])
            required = {root_pc, (root_pc + 4) % 12, (root_pc + 7) % 12}
            seventh = (root_pc + 11) % 12
            raw = levels(row["raw_pitch_class_levels"])
            detection = levels(row["guitar_detection_pitch_class_levels"])
            if not required <= visible or seventh in visible:
                continue
            if args.require_analysis_absent and seventh in analysis:
                continue
            if not args.allow_analysis_absent and not args.require_analysis_absent and seventh not in analysis:
                continue
            if raw.get(seventh, 0.0) < args.seventh_floor or raw.get(seventh, 0.0) > args.seventh_ceiling:
                continue
            if detection.get(seventh, 0.0) < args.detection_seventh_floor:
                continue
            positive = row["expected_chord_qualities"] == "maj7"
            if not positive:
                false_qualities[row["expected_chord_qualities"]] += 1
            candidates.append((positive, row, root_name, raw[seventh]))

    positives = sum(positive for positive, *_ in candidates)
    print(f"candidates {len(candidates)} positives {positives} false {len(candidates) - positives}")
    if false_qualities:
        print("false qualities " + " ".join(
            f"{quality or '--'}={count}" for quality, count in false_qualities.most_common()))
    for positive, row, root_name, level in candidates[:args.limit]:
        print(
            f"{'positive' if positive else 'false'} {row['recording_id']}@{row['center_seconds']} "
            f"expected={row['expected_chords']} got={row['guitar_chord']} root={root_name} "
            f"maj7={level:.3f} visible={row['guitar_pitch_classes']} "
            f"analysis={row['guitar_analysis_pitch_classes']} "
            f"analysis7={'yes' if (PITCH_CLASSES.get(root_name, -1) + 11) % 12 in classes(row['guitar_analysis_pitch_classes']) else 'no'} "
            f"detection7={levels(row['guitar_detection_pitch_class_levels']).get((PITCH_CLASSES.get(root_name, -1) + 11) % 12, 0.0):.3f}"
        )


if __name__ == "__main__":
    main()
