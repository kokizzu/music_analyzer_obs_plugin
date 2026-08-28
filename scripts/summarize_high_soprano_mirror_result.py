#!/usr/bin/env python3
"""Summarize the enabled high-soprano display mirror from cached VocalSet rows."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


PATH = Path("build/vocalset_full_mix_attributes.tsv")


def value(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, ""))
    except ValueError:
        return 0.0


def main() -> int:
    if not PATH.is_file():
        raise SystemExit("missing VocalSet attributes; run make analyze-vocalset-full-mix-attributes")
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    matches = [
        row for row in rows
        if row.get("family") == "vocals" and row.get("debug_owner") == "piano" and
        row.get("debug_midi") in {"77", "78"} and
        value(row, "adjacent_upper_ratio") >= 0.032 and value(row, "noise") >= 0.122 and
        value(row, "pitch_confidence") <= 0.814
    ]
    samples = {row["sample_id"] for row in matches}
    expected = {row["sample_id"] for row in matches if row.get("detected_expected_row") == "1"}
    print(f"high-soprano mirror candidates: rows={len(matches)} samples={len(samples)} expected-row={len(expected)}")
    print("status=" + " ".join(f"{name}={count}" for name, count in
                                sorted(Counter(row.get("status", "") for row in matches).items())))
    print("first-row=" + " ".join(f"{name}={count}" for name, count in
                                   sorted(Counter(row.get("first_row", "") for row in matches).items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
