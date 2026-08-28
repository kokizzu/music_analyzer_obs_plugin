#!/usr/bin/env python3
"""Summarize high-fidelity ride primary misses with detector attributes."""

import csv
from collections import Counter
from pathlib import Path


PATH = Path("build/hf_drum_kit_primary_attribute_rows_ride.tsv")


def main() -> None:
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        raise SystemExit("no ride attribute rows")

    print("columns=" + ",".join(rows[0].keys()))
    misses = [row for row in rows if row.get("got") != "ride"]
    print(f"rows={len(rows)} primary_misses={len(misses)}")
    print("primary=" + ", ".join(f"{key}:{value}" for key, value in sorted(Counter(row.get("got", "") for row in misses).items())))
    for row in misses:
        values = [
            row.get(key, "")
            for key in ("sample", "got", "hihat_band", "hihat_trigger", "hihat_threshold", "hihat_level", "ride_band", "ride_trigger", "ride_threshold", "ride_level", "rule_flags")
            if key in row
        ]
        print("\t".join(values))


if __name__ == "__main__":
    main()
