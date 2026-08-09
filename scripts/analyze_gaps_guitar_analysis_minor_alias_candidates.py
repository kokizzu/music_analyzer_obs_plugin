#!/usr/bin/env python3
"""Audit analysis-complete minor triads whose fifth is absent from display."""

import argparse
import csv
import re


NOTE_TO_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
PC_TO_NOTE = tuple(NOTE_TO_PC)


def cells(text):
    values = {}
    for entry in (text or "").split(","):
        match = re.match(r"([A-G](?:#)?)(?:-?\d+)?:([0-9.]+)$", entry)
        if match:
            pitch = NOTE_TO_PC[match.group(1)]
            values[pitch] = max(values.get(pitch, 0.0), float(match.group(2)))
    return values


def components(label):
    return set(part for part in (label or "").split("=") if part and part != "--")


def expected_minor(expected, root):
    return f"{PC_TO_NOTE[root]}m" in (expected or "").split("/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv", nargs="?", default="build/gaps_guitar_full_attributes.tsv")
    parser.add_argument("--display-root-floor", type=float, default=0.95)
    parser.add_argument("--display-minor-floor", type=float, default=0.35)
    parser.add_argument("--display-fifth-ceiling", type=float, default=0.10)
    parser.add_argument("--analysis-root-floor", type=float, default=0.95)
    parser.add_argument("--analysis-minor-floor", type=float, default=0.50)
    parser.add_argument("--analysis-fifth-floor", type=float, default=0.35)
    parser.add_argument("--analysis-fifth-ceiling", type=float, default=0.45)
    parser.add_argument("--analysis-major-ceiling", type=float, default=0.25)
    args = parser.parse_args()

    positives, negatives = [], []
    with open(args.tsv, newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            label = components(row.get("guitar_chord"))
            display = cells(row.get("guitar_cells"))
            analysis = cells(row.get("guitar_analysis_cells"))
            for root, name in enumerate(PC_TO_NOTE):
                candidate = f"{name}m"
                minor = (root + 3) % 12
                major = (root + 4) % 12
                fifth = (root + 7) % 12
                if candidate in label:
                    continue
                if display.get(root, 0.0) < args.display_root_floor:
                    continue
                if display.get(minor, 0.0) < args.display_minor_floor:
                    continue
                if display.get(fifth, 0.0) > args.display_fifth_ceiling:
                    continue
                if analysis.get(root, 0.0) < args.analysis_root_floor:
                    continue
                if analysis.get(minor, 0.0) < args.analysis_minor_floor:
                    continue
                if not args.analysis_fifth_floor <= analysis.get(fifth, 0.0) <= args.analysis_fifth_ceiling:
                    continue
                if analysis.get(major, 0.0) > args.analysis_major_ceiling:
                    continue
                item = (row, candidate, display.get(minor, 0.0), analysis.get(fifth, 0.0))
                (positives if expected_minor(row.get("expected_chords"), root) else negatives).append(item)

    print(f"candidates {len(positives) + len(negatives)} positives {len(positives)} false {len(negatives)}")
    for tag, entries in (("positive", positives), ("false", negatives)):
        for row, candidate, minor, fifth in entries:
            print(
                f"{tag} {row['recording_id']}@{row['center_seconds']} expected={row['expected_chords']} "
                f"got={row['guitar_chord']} candidate={candidate} "
                f"display_minor={minor:.3f} analysis_fifth={fifth:.3f}")


if __name__ == "__main__":
    main()
