#!/usr/bin/env python3
"""Summarize the dominant labeled MusicNet chord misses from a cached TSV."""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path


def labels(value: str) -> tuple[str, ...]:
    return tuple(label for label in value.split(",") if label and label != "--")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=Path("build/InstrumentSamples/musicnet/musicnet_full_attributes.tsv"))
    parser.add_argument("--limit", type=int, default=16)
    args = parser.parse_args()

    routes: collections.Counter[tuple[str, str]] = collections.Counter()
    exact_pitch_routes: collections.Counter[tuple[str, str]] = collections.Counter()
    missing_shapes: collections.Counter[str] = collections.Counter()
    misses = 0
    with args.path.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"expected_chords", "chord_hit", "global_chord", "missing_pcs", "extra_pcs"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{args.path}: missing columns {', '.join(sorted(missing))}")
        for row in rows:
            expected = labels(row["expected_chords"])
            if not expected or row["chord_hit"] == "1":
                continue
            misses += 1
            rendered = row["global_chord"] or "--"
            for label in expected:
                routes[label, rendered] += 1
                if row["missing_pcs"] in {"", "--"} and row["extra_pcs"] in {"", "--"}:
                    exact_pitch_routes[label, rendered] += 1
            missing_shapes[f"missing={row['missing_pcs'] or '--'} extra={row['extra_pcs'] or '--'}"] += 1

    print(f"MusicNet labeled chord misses: {misses}")
    print("top expected -> rendered routes:")
    for (expected, rendered), count in routes.most_common(max(1, args.limit)):
        print(f"  {count:4d}  {expected} -> {rendered}")
    print("exact-pitch-class routes (label only):")
    for (expected, rendered), count in exact_pitch_routes.most_common(max(1, args.limit)):
        print(f"  {count:4d}  {expected} -> {rendered}")
    print("top pitch-class miss shapes:")
    for shape, count in missing_shapes.most_common(max(1, args.limit)):
        print(f"  {count:4d}  {shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
