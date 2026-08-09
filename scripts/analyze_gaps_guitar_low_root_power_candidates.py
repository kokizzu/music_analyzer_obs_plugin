#!/usr/bin/env python3
"""Audit weak-fifth, third-free power-dyad aliases in expanded GAPS guitar rows."""

import csv
import re


NOTE_TO_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
PC_TO_NOTE = tuple(NOTE_TO_PC)


def cells(text):
    result = {}
    for entry in (text or "").split(","):
        match = re.match(r"([A-G](?:#)?)(?:-?\d+)?:([0-9.]+)$", entry)
        if match:
            pitch_class = NOTE_TO_PC[match.group(1)]
            result[pitch_class] = max(result.get(pitch_class, 0.0), float(match.group(2)))
    return result


def components(text):
    return {part for part in (text or "").split("=") if part and part != "--"}


def main():
    positives = []
    negatives = []
    with open("build/gaps_guitar_full_attributes.tsv", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            label = components(row.get("guitar_chord"))
            display = cells(row.get("guitar_cells"))
            analysis = cells(row.get("guitar_analysis_cells"))
            if len(label) > 2:
                continue
            for root, name in enumerate(PC_TO_NOTE):
                fifth = (root + 7) % 12
                minor_third = (root + 3) % 12
                major_third = (root + 4) % 12
                candidate = f"{name}pow"
                if f"{name}m" not in label or candidate in label:
                    continue
                if not (display.get(root, 0.0) >= 0.95 and
                        0.30 <= display.get(fifth, 0.0) <= 0.50 and
                        display.get(minor_third, 0.0) <= 0.03 and
                        display.get(major_third, 0.0) <= 0.03 and
                        analysis.get(root, 0.0) >= 0.95 and
                        analysis.get(fifth, 0.0) >= 0.30 and
                        analysis.get(minor_third, 0.0) <= 0.03 and
                        analysis.get(major_third, 0.0) <= 0.03):
                    continue
                entry = (row, candidate, display.get(fifth, 0.0), analysis.get(fifth, 0.0))
                (positives if candidate in row.get("expected_chords", "").split("/") else negatives).append(entry)

    print(f"candidates {len(positives) + len(negatives)} positives {len(positives)} false {len(negatives)}")
    for kind, entries in (("positive", positives), ("false", negatives)):
        for row, candidate, display_root, analysis_root in entries:
            print(f"{kind} {row['recording_id']}@{row['center_seconds']} "
                  f"expected={row['expected_chords']} got={row['guitar_chord']} "
                  f"candidate={candidate} display_fifth={display_root:.3f} "
                  f"analysis_fifth={analysis_root:.3f}")


if __name__ == "__main__":
    main()
