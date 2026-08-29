#!/usr/bin/env python3
"""Summarize current full-mix vocal-row misses from generated attributes."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE_PATHS = tuple(sorted((ROOT / "build").glob("real_note_full_mix_attributes_*.tsv")))


def main() -> None:
    rows: dict[str, dict[str, str]] = {}
    for path in ATTRIBUTE_PATHS:
        if not path.is_file():
            raise SystemExit("missing full-mix attributes; run make test-real-note-samples-full-mix first")
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                rows.setdefault(row["sample_id"], row)

    vocals = [row for row in rows.values() if row.get("family") == "vocals"]
    if not vocals:
        raise SystemExit("no vocal rows in full-mix attributes")
    expected = vocals
    misses = [row for row in expected if row.get("detected_expected_row") != "1"]
    print(f"vocals expected-row={len(expected) - len(misses)}/{len(vocals)} misses={len(misses)}")
    for label, counter in (
        ("visual-route", Counter(row.get("visual_first_row", "") for row in misses)),
        ("owner", Counter(row.get("debug_owner", "") for row in misses)),
        ("source", Counter(row.get("source", "") for row in misses)),
    ):
        values = ", ".join(f"{key or 'none'}={count}" for key, count in counter.most_common())
        print(f"{label}: {values or 'none'}")
    for row in misses[:12]:
        print(
            "miss "
            f"id={row.get('sample_id')} midi={row.get('expected_midi')} "
            f"source={row.get('source')} owner={row.get('debug_owner')} "
            f"visual={row.get('visual_first_row')} pitch={row.get('pitch_confidence')} "
            f"periodicity={row.get('periodicity')} noise={row.get('noise')}"
        )


if __name__ == "__main__":
    main()
