#!/usr/bin/env python3
"""Group full-mix visual-row misses by intended family and source."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE_PATHS = tuple(sorted((ROOT / "build").glob("real_note_full_mix_attributes_*.tsv")))
EXPECTED_ROW = {"bass": "bass", "guitar": "guitar", "piano": "piano", "vocals": "vocals", "other": "other"}


def main() -> None:
    rows: dict[str, dict[str, str]] = {}
    for path in ATTRIBUTE_PATHS:
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                rows.setdefault(row["sample_id"], row)
    if not rows:
        raise SystemExit("missing full-mix attributes; run make report-real-note-full-mix-attributes first")

    eligible = [row for row in rows.values() if row.get("family") in EXPECTED_ROW]
    misses = [
        row for row in eligible
        if row.get("visual_first_row") != EXPECTED_ROW[row["family"]]
    ]
    print(f"visual-row={len(eligible) - len(misses)}/{len(eligible)} misses={len(misses)}")
    for label, counter in (
        ("family", Counter(row["family"] for row in misses)),
        ("family-source", Counter(f"{row['family']}/{row.get('source', '')}" for row in misses)),
        ("route", Counter(f"{row['family']}->{row.get('visual_first_row', '') or 'none'}" for row in misses)),
    ):
        print(label + ":")
        for value, count in counter.most_common(20):
            print(f"  {value}={count}")


if __name__ == "__main__":
    main()
