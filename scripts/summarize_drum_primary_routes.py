#!/usr/bin/env python3
"""Summarize expected-to-primary routes in drum detector diagnostic TSV data."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = reader.fieldnames or []

    expected_field = next((name for name in ("expected", "expected_primary", "category") if name in fields), "")
    primary_field = next((name for name in ("primary", "got", "detected_primary", "actual") if name in fields), "")
    print(f"drum_primary_routes source={args.input} rows={len(rows)}")
    print("fields=" + ",".join(fields))
    if not expected_field or not primary_field:
        print("route fields unavailable")
        return 1

    routes = Counter((row.get(expected_field, ""), row.get(primary_field, "")) for row in rows)
    print(f"expected_field={expected_field} primary_field={primary_field}")
    for (expected, primary), count in routes.most_common(args.limit):
        print(f"{expected}->{primary} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
