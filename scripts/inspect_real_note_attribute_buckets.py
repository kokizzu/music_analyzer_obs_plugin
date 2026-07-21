#!/usr/bin/env python3
"""Print feature ranges for selected real-note attribute buckets."""

from __future__ import annotations

import csv
import pathlib
import statistics
import sys


FIELDS = [
    "expected_midi",
    "debug_midi",
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
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
]

DEFAULT_BUCKETS = [
    ("ownership_miss", "piano", "electronic", "guitar"),
    ("ownership_miss", "piano", "electronic", "bass"),
    ("ownership_miss", "guitar", "acoustic", "vocals"),
    ("ownership_miss", "guitar", "acoustic", "piano"),
    ("ownership_miss", "other", "acoustic", "guitar"),
    ("ownership_miss", "other", "acoustic", "bass"),
    ("hit", "piano", "electronic", "guitar"),
    ("hit", "guitar", "acoustic", "guitar"),
    ("hit", "other", "acoustic", "other"),
]


def as_float(row: dict[str, str], field: str) -> float | None:
    try:
        value = row[field]
    except KeyError:
        return None
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def print_bucket(rows: list[dict[str, str]], status: str, family: str, source: str, first_row: str) -> None:
    bucket_rows = [
        row
        for row in rows
        if row.get("status") == status
        and row.get("family") == family
        and row.get("source") == source
        and row.get("first_row") == first_row
        and row.get("debug_note")
    ]
    samples = sorted({row["sample_id"] for row in bucket_rows})
    print()
    print(
        f"{status}:{family}/{source}->{first_row} rows={len(bucket_rows)} "
        f"samples={len(samples)} examples={', '.join(samples[:12])}"
    )
    for field in FIELDS:
        values = sorted(value for row in bucket_rows if (value := as_float(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:16s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/real_note_full_mix_attributes.tsv")
    rows = load_rows(path)
    for bucket in DEFAULT_BUCKETS:
        print_bucket(rows, *bucket)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
