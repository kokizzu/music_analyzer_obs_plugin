#!/usr/bin/env python3
"""Print the persisted GAPS guitar attribute schema and representative rows."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/gaps_guitar_attributes.tsv"


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        print("columns=" + ",".join(reader.fieldnames or ()))
        rows = list(reader)
    print(f"rows={len(rows)}")
    for row in rows[:8]:
        print("\t".join(f"{key}={row.get(key, '')}" for key in reader.fieldnames or ()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
