#!/usr/bin/env python3
"""Report visible per-instrument note recall from full-mix attribute exports."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE_PATHS = tuple(
    ROOT / "build" / f"real_note_full_mix_attributes_{index}.tsv" for index in range(8)
)
VISUAL_COLUMNS = {
    "bass": "bass_visual_level",
    "guitar": "guitar_visual_level",
    "piano": "piano_visual_level",
    "vocals": "vocal_visual_level",
    "other": "other_visual_level",
}
VISIBLE_LEVEL = 0.25


def main() -> int:
    details = "--details" in sys.argv
    rows_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in ATTRIBUTE_PATHS:
        if not path.is_file():
            print(f"missing-attributes={path}")
            return 1
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                rows_by_sample[row["sample_id"]].append(row)

    totals: dict[str, int] = defaultdict(int)
    visible: dict[str, int] = defaultdict(int)
    missed_sources: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for rows in rows_by_sample.values():
        family = rows[0]["family"]
        column = VISUAL_COLUMNS.get(family)
        if column is None:
            continue
        totals[family] += 1
        if any(float(row[column] or 0.0) >= VISIBLE_LEVEL for row in rows):
            visible[family] += 1
        else:
            missed_sources[family][rows[0]["source"]] += 1

    for family in ("bass", "guitar", "piano", "vocals", "other"):
        total = totals[family]
        hit = visible[family]
        percent = hit * 100.0 / total if total else 0.0
        print(f"visible-row {family}={hit}/{total} ({percent:.1f}%)")
        if details and missed_sources[family]:
            sources = ",".join(
                f"{source}:{count}" for source, count in sorted(missed_sources[family].items())
            )
            print(f"  visible-miss-sources {sources}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
