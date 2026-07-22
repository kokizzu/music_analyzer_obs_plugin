#!/usr/bin/env python3
"""Inspect generated instrument sample full-mix owner buckets."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import statistics


FIELDS = [
    "midi",
    "expected_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
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
]


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
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


def compact_counter(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def owner_target(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family == "piano":
        return "piano"
    if family == "guitar":
        return "guitar"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth"}:
        return "other"
    if family == "bass":
        return "bass-display"
    return family or "unknown"


def bucket_key(row: dict[str, str]) -> tuple[str, str, str]:
    target = owner_target(row)
    owner = row.get("debug_owner", "") or "none"
    if target == "bass-display":
        status = "bass_debug"
    else:
        status = "owner_hit" if owner == target else "owner_miss"
    return row.get("family", "unknown"), status, owner


def print_bucket(key: tuple[str, str, str], rows: list[dict[str, str]], examples: int) -> None:
    family, status, owner = key
    print()
    print(f"{status}:{family}->{owner} rows={len(rows)}")
    print(f"  programs {compact_counter(collections.Counter(row.get('program_name', '') for row in rows))}")
    print(f"  notes {compact_counter(collections.Counter(row.get('note', '') for row in rows))}")
    print(f"  raw_best {compact_counter(collections.Counter(row.get('raw_local_best_note', '') for row in rows))}")
    for field in FIELDS:
        values = sorted(value for row in rows if (value := as_float(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:26s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )
    for row in rows[:examples]:
        print(
            "  example "
            f"{row.get('family', '')} {row.get('program_name', '')} {row.get('note', '')} "
            f"{row.get('path', '')} owner={row.get('debug_owner', '')} "
            f"scores=k:{row.get('keyboard_score', '')},g:{row.get('guitar_score', '')},"
            f"v:{row.get('vocal_score', '')},o:{row.get('other_score', '')} "
            f"raw={row.get('raw_expected_ratio', '')}/{row.get('raw_tuned_ratio', '')}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--examples", type=int, default=4)
    args = parser.parse_args()

    rows = [
        row
        for row in load_rows(args.path)
        if row.get("kind") == "note" and row.get("debug_note")
    ]
    print(f"inspect_instrument_sample_owner_buckets: note debug rows {len(rows)}")
    counts = collections.Counter(bucket_key(row) for row in rows)
    print("owner buckets " + " ".join(f"{'/'.join(key)}={count}" for key, count in counts.most_common(args.top)))

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        grouped[bucket_key(row)].append(row)

    for key, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[: args.top]:
        print_bucket(key, group, max(0, args.examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
