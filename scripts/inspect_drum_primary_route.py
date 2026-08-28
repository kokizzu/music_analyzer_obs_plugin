#!/usr/bin/env python3
"""Inspect samples and feature ranges for one expected-to-primary drum route."""

from __future__ import annotations

import argparse
import csv
import pathlib
import statistics


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summary(values: list[float]) -> str:
    if not values:
        return "--"
    ordered = sorted(values)
    return (
        f"min={ordered[0]:.4g} q25={ordered[len(ordered) // 4]:.4g} "
        f"med={statistics.median(ordered):.4g} q75={ordered[(len(ordered) * 3) // 4]:.4g} "
        f"max={ordered[-1]:.4g}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--primary", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--field", action="append", default=[])
    args = parser.parse_args()

    with args.path.open(newline="", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    matched = [
        row
        for row in rows
        if row.get("expected") == args.expected and row.get("got") == args.primary
    ]
    print(
        f"drum_primary_route expected={args.expected} primary={args.primary} "
        f"rows={len(matched)} source={args.path}"
    )

    fields = args.field or [
        f"{args.expected}_level", f"{args.primary}_level",
        f"{args.expected}_{args.primary}_level_ratio",
        f"{args.expected}_band", f"{args.primary}_band",
        f"{args.expected}_{args.primary}_band_ratio",
        f"{args.expected}_trigger", f"{args.primary}_trigger",
        f"{args.expected}_{args.primary}_trigger_ratio",
        f"{args.expected}_shape_score", f"{args.primary}_shape_score",
        f"{args.expected}_{args.primary}_shape_score_ratio",
    ]
    for field in fields:
        values = [value for row in matched if (value := number(row.get(field, ""))) is not None]
        if values:
            print(f"  {field} {summary(values)}")

    for row in matched[: max(args.limit, 0)]:
        sample = row.get("sample", row.get("path", row.get("audio_path", "--")))
        print(
            "  sample=" + sample +
            " primary_level=" + row.get(f"{args.primary}_level", "--") +
            " expected_level=" + row.get(f"{args.expected}_level", "--") +
            " primary_band=" + row.get(f"{args.primary}_band", "--") +
            " expected_band=" + row.get(f"{args.expected}_band", "--") +
            " primary_trigger=" + row.get(f"{args.primary}_trigger", "--") +
            " expected_trigger=" + row.get(f"{args.expected}_trigger", "--")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
