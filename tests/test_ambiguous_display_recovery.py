#!/usr/bin/env python3
"""Guard the high-confidence ambiguous shared-display recovery."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
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
    return {parsed for label in NOTE.findall(value or "") if (parsed := midi(label)) is not None}


def main() -> int:
    if not INPUT.exists():
        print(f"missing attributes: {INPUT}", file=sys.stderr)
        return 1
    totals = Counter()
    hits = Counter()
    unresolved_ambiguous = Counter()
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            family = row.get("family", "")
            if family not in {"bass", "guitar", "piano"}:
                continue
            try:
                expected = int(row["expected_midi"])
            except (KeyError, ValueError):
                continue
            totals[family] += 1
            if expected in note_list(row.get(f"{family}_notes", "")):
                hits[family] += 1
            elif expected in note_list(row.get("amb_notes", "")):
                unresolved_ambiguous[family] += 1

    requirements = (
        ("bass", 1000, None),
        ("guitar", 2100, 160),
        ("piano", 7400, 560),
    )
    failures = []
    for family, minimum_hits, maximum_unresolved in requirements:
        if hits[family] < minimum_hits:
            failures.append(f"{family} hits {hits[family]} < {minimum_hits}")
        if maximum_unresolved is not None and unresolved_ambiguous[family] > maximum_unresolved:
            failures.append(
                f"{family} unresolved ambiguous {unresolved_ambiguous[family]} > {maximum_unresolved}"
            )
    print(
        "ambiguous_display_recovery: "
        + ", ".join(
            f"{family}={hits[family]}/{totals[family]} unresolved={unresolved_ambiguous[family]}"
            for family, _, _ in requirements
        )
    )
    if failures:
        print("; ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
