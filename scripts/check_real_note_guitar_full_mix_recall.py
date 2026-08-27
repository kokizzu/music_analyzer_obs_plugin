#!/usr/bin/env python3
"""Require every committed real single-guitar fixture to reach the guitar row."""

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "real_note_guitar_ownership.tsv"


def main() -> int:
    if not OUTPUT.exists():
        print(f"check_real_note_guitar_full_mix_recall: missing {OUTPUT}")
        return 1
    rows_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    with OUTPUT.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            rows_by_sample[row["sample_id"]].append(row)
    total = len(rows_by_sample)
    hits = sum(
        any(row.get("detected_expected_row") == "1" for row in rows)
        for rows in rows_by_sample.values()
    )
    if total != 346 or hits != total:
        print(f"check_real_note_guitar_full_mix_recall: expected guitar=346/346, got {hits}/{total}")
        return 1
    print("check_real_note_guitar_full_mix_recall: guitar=346/346")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
