#!/usr/bin/env python3
"""Measure expected-row recall recoverable from the existing ambiguous note grid."""

from __future__ import annotations

import csv
import re
from collections import Counter
from statistics import median
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "build" / "real_note_full_mix_attributes.tsv"
NOTE = re.compile(r"([A-G](?:#)?-?\d+):")
PITCH_CLASS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
               "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi(label: str) -> int | None:
    match = re.fullmatch(r"([A-G](?:#)?)(-?\d+)", label)
    if not match:
        return None
    return (int(match.group(2)) + 1) * 12 + PITCH_CLASS[match.group(1)]


def note_list(value: str) -> set[int]:
    return {value for label in NOTE.findall(value or "") if (value := midi(label)) is not None}


def main() -> int:
    if not INPUT.exists():
        print(f"missing attributes: {INPUT}")
        return 1
    totals = Counter()
    hits = Counter()
    recovered = Counter()
    features: dict[str, dict[str, list[float]]] = {
        family: {name: [] for name in ("keyboard_score", "guitar_score", "vocal_score", "other_score", "spectral_level",
                                        "pitch_confidence", "periodicity", "harmonicity", "noise")}
        for family in ("bass", "guitar", "piano", "vocals", "other")
    }
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            family = row.get("family", "")
            expected = row.get("expected_midi", "")
            try:
                expected_midi = int(expected)
            except ValueError:
                continue
            if family not in {"bass", "guitar", "piano", "vocals", "other"}:
                continue
            totals[family] += 1
            grid_column = "vocal_notes" if family == "vocals" else f"{family}_notes"
            expected_row = note_list(row.get(grid_column, ""))
            if expected_midi in expected_row:
                hits[family] += 1
                continue
            ambiguous = note_list(row.get("amb_notes", ""))
            if expected_midi in ambiguous:
                recovered[family] += 1
                for name, values in features[family].items():
                    try:
                        values.append(float(row.get(name, "")))
                    except ValueError:
                        pass
    print("ambiguous expected-pitch recovery candidates:")
    for family in ("bass", "guitar", "piano", "vocals", "other"):
        total = totals[family]
        count = recovered[family]
        rate = 100.0 * count / total if total else 0.0
        hit_rate = 100.0 * hits[family] / total if total else 0.0
        print(f"  {family}: row_hits={hits[family]}/{total} ({hit_rate:.1f}%), ambiguous_recovery={count}/{total} ({rate:.1f}%)")
        if count:
            print("    medians " + " ".join(
                f"{name}={median(values):.3f}" for name, values in features[family].items() if values
            ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
