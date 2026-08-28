#!/usr/bin/env python3
"""Summarize GuitarSet primary-label misses by expected and detected chord."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "build/guitar_chord_primary_attributes.tsv"


def first_label(labels: str) -> str:
    return labels.split("=", 1)[0] if labels else "--"


def main() -> int:
    if not PATH.is_file():
        raise SystemExit("missing primary attributes; run collect-guitar-chord-primary-attributes first")
    with PATH.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    chord_rows = [row for row in rows if row["expected_chords"]]
    misses = [row for row in chord_rows if row["primary_chord_hit"] != "1"]
    chord_misses = [row for row in chord_rows if row["chord_hit"] != "1"]
    print(f"windows: {len(rows)}, chord windows: {len(chord_rows)}, primary misses: {len(misses)}")
    print(f"actual chord misses: {len(chord_misses)}")
    for row in chord_misses:
        print(
            f"  {row['recording_id']} @{row['center_seconds']} expected={row['expected_chords']} "
            f"guitar={row['guitar_chord']} cells={row['guitar_analysis_cells']}"
        )
    pairs = Counter((row["expected_chords"], first_label(row["guitar_chord"])) for row in misses)
    print("primary miss pairs:")
    for (expected, detected), count in pairs.most_common(80):
        print(f"  {count:3} expected={expected} primary={detected}")
    print("primary misses where expected alias is present:")
    for row in misses:
        expected = set(row["expected_chords"].split("="))
        labels = set(row["guitar_chord"].split("="))
        if expected & labels:
            print(
                f"  {row['recording_id']} @{row['center_seconds']} expected={row['expected_chords']} "
                f"guitar={row['guitar_chord']} cells={row['guitar_analysis_cells']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
