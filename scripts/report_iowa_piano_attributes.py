#!/usr/bin/env python3
"""Summarize full-mix Iowa Piano attribute exports by visible destination."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE_PATH = ROOT / "build" / "iowa_piano_midrange_attributes.tsv"
FEATURES = (
    "bass_level", "guitar_level", "piano_level", "vocal_level", "other_level",
    "bass_visual_level", "guitar_visual_level", "piano_visual_level",
    "vocal_visual_level", "other_visual_level", "ownership_confidence",
    "bass_score", "keyboard_score", "guitar_score", "vocal_score", "other_score",
    "spectral_level", "pitch_confidence", "periodicity", "harmonicity",
    "fit_error", "centroid", "slope", "noise", "adjacent_lower_ratio", "adjacent_upper_ratio",
    "partial1", "partial2", "partial3", "partial4", "partial5",
)


def number(row: dict[str, str], key: str) -> float | None:
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return None


def representative_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)
    selected: list[dict[str, str]] = []
    for sample_rows in by_sample.values():
        visual_route = sample_rows[0]["visual_first_row"]
        matching = [row for row in sample_rows if row["buffer_visual_strongest_row"] == visual_route]
        selected.append(min(matching or sample_rows, key=lambda row: int(row["buffer"])))
    return selected


def main() -> int:
    if not ATTRIBUTE_PATH.is_file():
        print(f"missing-attributes={ATTRIBUTE_PATH}")
        return 1
    with ATTRIBUTE_PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    selected = representative_rows(rows)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        groups[row["visual_first_row"]].append(row)
    print(f"iowa-piano-attribute-samples={len(selected)} frames={len(rows)}")
    available = tuple(feature for feature in FEATURES if feature in rows[0]) if rows else ()
    for route in sorted(groups):
        group = groups[route]
        values = []
        for feature in available:
            data = [value for row in group if (value := number(row, feature)) is not None]
            if data:
                values.append(f"{feature}={statistics.median(data):.3f}")
        print(f"visual={route} samples={len(group)} {' '.join(values)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
