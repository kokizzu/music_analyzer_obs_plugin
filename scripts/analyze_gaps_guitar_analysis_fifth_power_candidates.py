#!/usr/bin/env python3
"""Audit GAPS power aliases whose fifth survives only in the analysis grid."""

import argparse
import csv
import re
import sys


NOTE_TO_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
PC_TO_NOTE = tuple(NOTE_TO_PC)


def cells(text):
    values = {}
    for entry in (text or "").split(","):
        match = re.match(r"([A-G](?:#)?)(?:-?\d+)?:([0-9.]+)$", entry)
        if match:
            values[NOTE_TO_PC[match.group(1)]] = max(
                values.get(NOTE_TO_PC[match.group(1)], 0.0), float(match.group(2)))
    return values


def label_components(label):
    return set(component for component in (label or "").split("=") if component and component != "--")


def expected_power(expected, root):
    return f"{PC_TO_NOTE[root]}pow" in (expected or "").split("/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv", nargs="?", default="build/gaps_guitar_full_attributes.tsv")
    parser.add_argument("--display-root-floor", type=float, default=0.80)
    parser.add_argument("--display-fifth-ceiling", type=float, default=0.10)
    parser.add_argument("--analysis-root-floor", type=float, default=0.85)
    parser.add_argument("--analysis-fifth-floor", type=float, default=0.18)
    parser.add_argument("--analysis-fifth-ceiling", type=float, default=0.22)
    parser.add_argument("--require-adjacent-minor-aliases", action="store_true")
    args = parser.parse_args()

    positives = []
    negatives = []
    with open(args.tsv, newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            label = label_components(row.get("guitar_chord"))
            display = cells(row.get("guitar_cells"))
            analysis = cells(row.get("guitar_analysis_cells"))
            for root, name in enumerate(PC_TO_NOTE):
                fifth = (root + 7) % 12
                candidate = f"{name}pow"
                if name not in label or candidate in label:
                    continue
                if args.require_adjacent_minor_aliases:
                    lower_minor = f"{PC_TO_NOTE[(root + 9) % 12]}m"
                    upper_minor = f"{PC_TO_NOTE[(root + 4) % 12]}m"
                    if lower_minor not in label or upper_minor not in label:
                        continue
                if display.get(root, 0.0) < args.display_root_floor:
                    continue
                if display.get(fifth, 0.0) > args.display_fifth_ceiling:
                    continue
                if analysis.get(root, 0.0) < args.analysis_root_floor:
                    continue
                analysis_fifth = analysis.get(fifth, 0.0)
                if not args.analysis_fifth_floor <= analysis_fifth <= args.analysis_fifth_ceiling:
                    continue
                item = (row, candidate, display.get(root, 0.0), analysis_fifth)
                (positives if expected_power(row.get("expected_chords"), root) else negatives).append(item)

    print(f"candidates {len(positives) + len(negatives)} positives {len(positives)} false {len(negatives)}")
    for tag, entries in (("positive", positives), ("false", negatives)):
        for row, candidate, root_level, fifth_level in entries:
            print(
                f"{tag} {row['recording_id']}@{row['center_seconds']} "
                f"expected={row['expected_chords']} got={row['guitar_chord']} "
                f"candidate={candidate} display_root={root_level:.3f} "
                f"analysis_fifth={fifth_level:.3f}")


if __name__ == "__main__":
    main()
