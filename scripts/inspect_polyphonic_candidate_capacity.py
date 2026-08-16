#!/usr/bin/env python3
"""Report whether full-mix candidate capacity truncates labelled polyphony."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def candidate_count(value: str) -> int:
    value = value.strip()
    return 0 if not value or value == "--" else len(value.split())


def active_note_count(value: str) -> int:
    value = value.strip()
    return 0 if not value or value == "--" else len(value.split(","))


def inspect(path: Path, limit: int) -> tuple[int, int, int, int, int, int]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"active_notes", "candidates", "missing_pcs"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing candidate-capacity columns: {', '.join(sorted(missing))}")

    polyphonic = saturated = missing_pitch = saturated_missing = maximum = 0
    for row in rows:
        if active_note_count(row["active_notes"]) < 2:
            continue
        polyphonic += 1
        count = candidate_count(row["candidates"])
        maximum = max(maximum, count)
        full = count >= limit
        missing = row["missing_pcs"].strip() not in {"", "--"}
        saturated += int(full)
        missing_pitch += int(missing)
        saturated_missing += int(full and missing)
    return len(rows), polyphonic, saturated, missing_pitch, saturated_missing, maximum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", nargs="+", type=Path)
    parser.add_argument("--limit", type=int, default=24)
    args = parser.parse_args()
    if args.limit < 1:
        raise ValueError("--limit must be positive")

    print("polyphonic candidate capacity audit")
    print("corpus\trows\tpolyphonic\tsaturated\tmissing-pitch\tsaturated-missing\tmax-candidates")
    corpus_count = saturated_corpora = missing_total = saturated_missing_total = 0
    for path in args.attributes:
        rows, polyphonic, saturated, missing, saturated_missing, maximum = inspect(path, args.limit)
        print(f"{path.stem}\t{rows}\t{polyphonic}\t{saturated}\t{missing}\t{saturated_missing}\t{maximum}")
        corpus_count += 1
        saturated_corpora += int(saturated > 0)
        missing_total += missing
        saturated_missing_total += saturated_missing
    print(
        "polyphonic_candidate_capacity: "
        f"capacity_limited_corpora={saturated_corpora}/{corpus_count} "
        f"missing_pitch_windows={missing_total} "
        f"saturation_explains_missing={saturated_missing_total}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
