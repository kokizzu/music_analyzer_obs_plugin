#!/usr/bin/env python3
"""Simulate drum active thresholds from analyzer_drum_samples attribute rows."""

from __future__ import annotations

import argparse
import csv
import pathlib


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
DEFAULT_THRESHOLDS = (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90)


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def percent(hit: int, total: int) -> float:
    return 100.0 * hit / total if total else 0.0


def print_threshold(rows: list[dict[str, str]], threshold: float) -> None:
    print(f"threshold {threshold:.2f}")
    for category in CATEGORIES:
        total = sum(1 for row in rows if row.get("expected") == category)
        hit = sum(
            1
            for row in rows
            if row.get("expected") == category
            and as_float(row.get(f"{category}_level", "")) > threshold
        )
        active = sum(1 for row in rows if as_float(row.get(f"{category}_level", "")) > threshold)
        false = sum(
            1
            for row in rows
            if row.get("expected") != category
            and as_float(row.get(f"{category}_level", "")) > threshold
        )
        print(
            f"  {category}: recall={hit}/{total} {percent(hit, total):.2f}% "
            f"precision={hit}/{active} {percent(hit, active):.2f}% false={false}"
        )


def parse_thresholds(values: list[str]) -> list[float]:
    if not values:
        return list(DEFAULT_THRESHOLDS)
    thresholds: list[float] = []
    for value in values:
        for part in value.split(","):
            part = part.strip()
            if part:
                thresholds.append(float(part))
    return thresholds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", type=pathlib.Path)
    parser.add_argument(
        "--threshold",
        action="append",
        default=[],
        help="threshold value or comma-separated values; defaults to 0.30..0.90",
    )
    args = parser.parse_args()

    rows = read_rows(args.rows)
    print(f"drum active threshold simulation: rows={len(rows)} source={args.rows}")
    for threshold in parse_thresholds(args.threshold):
        print_threshold(rows, threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
