#!/usr/bin/env python3
"""Print official Real A2S tenor-index rows that name scale recordings."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    args = parser.parse_args()
    if not args.index.is_file():
        raise SystemExit(f"missing official tenor index: {args.index}")
    with args.index.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    fields = list(rows[0]) if rows else []
    print("fields=" + ",".join(fields))
    selected = [
        row for row in rows
        if "scale" in " ".join(value for value in row.values() if value).lower()
    ]
    for row in selected:
        print(
            " | ".join(
                f"{field}={row.get(field, '')}"
                for field in ("FILENAME", "TEMPO", "MEASURE", "TYPE", "ALTISSIMO", "PERFORMER")
            )
        )
    print(f"scale_rows={len(selected)} total_rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
