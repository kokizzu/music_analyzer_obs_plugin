#!/usr/bin/env python3
"""Guard the measured GAPS full-mix primary chord display baseline."""

import csv
from pathlib import Path
import sys


def primary_matches_expected(row: dict[str, str]) -> bool:
    primary = row.get("guitar_chord", "--").split("=", 1)[0]
    expected = row.get("expected_chords", "").split("/")
    return primary in expected


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_gaps_guitar_primary_display.py ATTRIBUTES MINIMUM", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    minimum = int(sys.argv[2])
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    hits = sum(primary_matches_expected(row) for row in rows)
    if hits < minimum:
        print(f"GAPS full primary display regressed: {hits}/{len(rows)} < {minimum}", file=sys.stderr)
        return 1
    print(f"GAPS full primary display: {hits}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
