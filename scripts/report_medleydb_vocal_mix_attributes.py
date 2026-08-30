#!/usr/bin/env python3
"""Report the remaining MedleyDB Vocal mix visibility misses from analyzer attributes."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEATURES = (
    "vocal_visual_level", "vocal_level", "keyboard_score", "guitar_score", "vocal_score",
    "other_score", "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid",
    "slope", "noise", "partial1", "partial2", "partial3", "partial4", "partial5",
)


def number(row: dict[str, str], field: str) -> float:
    return float(row[field] or 0.0)


def main() -> int:
    stem = "--stem" in sys.argv
    attribute_path = ROOT / "build" / (
        "medleydb_vocal_stem_attributes.tsv" if stem else "medleydb_vocal_mix_attributes.tsv"
    )
    name = "medleydb-vocal-stem" if stem else "medleydb-vocal-mix"
    if not attribute_path.is_file():
        print(f"missing-attributes={attribute_path}")
        return 1
    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    with attribute_path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            by_sample[row["sample_id"]].append(row)
    misses = 0
    for sample_id, rows in sorted(by_sample.items()):
        visible = any(number(row, "vocal_visual_level") >= 0.25 for row in rows)
        if visible:
            continue
        misses += 1
        row = max(rows, key=lambda candidate: number(candidate, "vocal_visual_level"))
        values = " ".join(f"{feature}={number(row, feature):.3f}" for feature in FEATURES)
        print(f"miss={sample_id} expected={row['expected_note']} first={row['visual_first_row']} {values}")
    print(f"{name}-visible-misses={misses}/{len(by_sample)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
