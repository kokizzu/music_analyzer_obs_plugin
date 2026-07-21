#!/usr/bin/env python3
"""Print feature ranges for selected real-note attribute buckets."""

from __future__ import annotations

import csv
import argparse
import collections
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


ROW_FOR_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}

CATEGORY_FIELDS = [
    "expected_note",
    "debug_note",
    "debug_owner",
    "row_label",
    "buffer_strongest_row",
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


def bucket_rows(
    rows: list[dict[str, str]], status: str, family: str, source: str, first_row: str
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("status") == status
        and row.get("family") == family
        and row.get("source") == source
        and row.get("first_row") == first_row
        and row.get("debug_note")
    ]


def bucket_sample_count(rows: list[dict[str, str]], key: tuple[str, str, str, str]) -> int:
    status, family, source, first_row = key
    return len(
        {
            row["sample_id"]
            for row in rows
            if row.get("status") == status
            and row.get("family") == family
            and row.get("source") == source
            and row.get("first_row") == first_row
        }
    )


def compact_counts(rows: list[dict[str, str]], field: str, limit: int = 8) -> str:
    counts = collections.Counter(row.get(field, "") for row in rows if row.get(field, ""))
    if not counts:
        return ""
    return " ".join(f"{key}={value}" for key, value in counts.most_common(limit))


def print_bucket(rows: list[dict[str, str]], status: str, family: str, source: str, first_row: str) -> None:
    rows_for_bucket = bucket_rows(rows, status, family, source, first_row)
    samples = sorted({row["sample_id"] for row in rows_for_bucket})
    print()
    print(
        f"{status}:{family}/{source}->{first_row} rows={len(rows_for_bucket)} "
        f"samples={len(samples)} examples={', '.join(samples[:12])}"
    )
    for field in CATEGORY_FIELDS:
        counts = compact_counts(rows_for_bucket, field)
        if counts:
            print(f"  {field:16s} {counts}")
    for field in FIELDS:
        values = sorted(value for row in rows_for_bucket if (value := as_float(row, field)) is not None)
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


def top_bucket_keys(rows: list[dict[str, str]], top_misses: int) -> list[tuple[str, str, str, str]]:
    counts: collections.Counter[tuple[str, str, str, str]] = collections.Counter()
    for row in rows:
        key = (row.get("status", ""), row.get("family", ""), row.get("source", ""), row.get("first_row", ""))
        if "" in key:
            continue
        counts[key] += 1

    keys: list[tuple[str, str, str, str]] = []
    for key, _row_count in counts.most_common():
        status, family, source, first_row = key
        if status != "ownership_miss":
            continue
        keys.append(key)
        expected_row = ROW_FOR_FAMILY.get(family)
        comparisons = [
            ("hit", family, source, first_row),
            ("hit", family, source, expected_row or first_row),
        ]
        for comparison in comparisons:
            if comparison in counts:
                keys.append(comparison)
        if len({key for key in keys if key[0] == "ownership_miss"}) >= top_misses:
            break

    for bucket in DEFAULT_BUCKETS:
        keys.append(bucket)

    deduped = []
    seen = set()
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        if bucket_sample_count(rows, key) <= 0:
            continue
        deduped.append(key)
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--top-misses",
        type=int,
        default=12,
        help="number of largest ownership-miss buckets to print before fixed comparison buckets",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    rows = load_rows(path)
    for bucket in top_bucket_keys(rows, max(0, args.top_misses)):
        print_bucket(rows, *bucket)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
