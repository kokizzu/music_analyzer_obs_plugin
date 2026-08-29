#!/usr/bin/env python3
"""Compare expected-note features for stable and visually misrouted vocals."""

from __future__ import annotations

import csv
from collections import defaultdict
from statistics import fmean
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "build/full_mix_vocal_attributes_shard_0.tsv"
FIELDS = (
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
)


def main() -> int:
    with ATTRIBUTES.open(encoding="utf-8", newline="") as handle:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in csv.DictReader(handle, delimiter="\t"):
            grouped[row["sample_id"]].append(row)

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rows in grouped.values():
        summary = rows[-1]
        if summary["first_row"] != "vocals":
            continue
        expected_midi = summary["expected_midi"]
        expected_rows = [row for row in rows if row["debug_midi"] == expected_midi]
        if not expected_rows:
            continue
        key = "visual-vocal" if summary["visual_first_row"] == "vocals" else "visually-misrouted"
        groups[key].append(expected_rows[-1])

    for group, rows in sorted(groups.items()):
        print(f"{group} samples={len(rows)}")
        for field in FIELDS:
            values = [float(row[field]) for row in rows]
            print(f"  {field}={fmean(values):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
