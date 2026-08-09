#!/usr/bin/env python3
"""Audit analysis-complete major add9 chords missing their final alias."""

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv", nargs="?", default="build/gaps_guitar_full_attributes.tsv")
    parser.add_argument("--root-floor", type=float, default=0.65)
    parser.add_argument("--third-floor", type=float, default=0.40)
    parser.add_argument("--fifth-floor", type=float, default=0.90)
    parser.add_argument("--ninth-floor", type=float, default=0.80)
    args = parser.parse_args()

    positives, negatives = [], []
    with open(args.tsv, newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            label = set(part for part in (row.get("guitar_chord") or "").split("=") if part)
            analysis = cells(row.get("guitar_analysis_cells"))
            expected = set((row.get("expected_chords") or "").split("/"))
            for root, name in enumerate(PC_TO_NOTE):
                candidate = f"{name}add9"
                if name not in label or candidate in label:
                    continue
                root_level = analysis.get(root, 0.0)
                third = analysis.get((root + 4) % 12, 0.0)
                fifth = analysis.get((root + 7) % 12, 0.0)
                ninth = analysis.get((root + 2) % 12, 0.0)
                if root_level < args.root_floor or third < args.third_floor or fifth < args.fifth_floor or ninth < args.ninth_floor:
                    continue
                item = (row, candidate, root_level, third, fifth, ninth)
                (positives if candidate in expected else negatives).append(item)

    print(f"candidates {len(positives) + len(negatives)} positives {len(positives)} false {len(negatives)}")
    for tag, entries in (("positive", positives), ("false", negatives)):
        for row, candidate, root, third, fifth, ninth in entries:
            print(f"{tag} {row['recording_id']}@{row['center_seconds']} expected={row['expected_chords']} "
                  f"got={row['guitar_chord']} candidate={candidate} "
                  f"r={root:.3f} M3={third:.3f} 5={fifth:.3f} 9={ninth:.3f}")


if __name__ == "__main__":
    main()
