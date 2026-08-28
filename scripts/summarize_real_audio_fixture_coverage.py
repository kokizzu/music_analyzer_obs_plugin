#!/usr/bin/env python3
"""Summarize cached real-audio fixture attributes by corpus and instrument label."""

from collections import Counter
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
KEYWORDS = ("drum", "guitar", "vocal", "choir", "piano", "maestro", "musicnet", "urmp", "bass")


def label(row: dict[str, str]) -> str:
    for field in ("instrument", "expected", "merged_expected", "expected_instrument"):
        value = row.get(field, "").strip()
        if value:
            return value
    return "unlabelled"


def main() -> int:
    paths = [
        path for path in sorted(BUILD.glob("*attributes*.tsv"))
        if ".shard-" not in path.name and any(keyword in path.name.lower() for keyword in KEYWORDS)
    ]
    print(f"attribute_files={len(paths)}")
    for path in paths:
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
        except (OSError, UnicodeError, csv.Error):
            continue
        if not rows:
            continue
        labels = Counter(label(row) for row in rows)
        compact = ",".join(f"{name}:{count}" for name, count in labels.most_common(8))
        print(f"{path.relative_to(ROOT)} rows={len(rows)} labels={compact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
