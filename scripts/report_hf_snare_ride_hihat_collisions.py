#!/usr/bin/env python3
"""Report snare primary misses that match the final ride/hi-hat recovery."""

import csv
from pathlib import Path


PATH = Path("build/hf_drum_kit_primary_attribute_rows_snare.tsv")


def matches_recovery(row: dict[str, str]) -> bool:
    hihat_level = float(row["hihat_level"])
    ride_level = float(row["ride_level"])
    return (
        hihat_level > 0.30
        and ride_level > 0.30
        and ride_level + 0.025 >= hihat_level
        and float(row["ride_band"]) >= float(row["hihat_band"]) * 1.20
        and float(row["hihat_seg"]) >= 3.20
        and float(row["hihat_seg"]) <= 6.10
        and float(row["rim_level"]) <= 0.805
    )


def main() -> None:
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    misses = [row for row in rows if row["got"] != "snare"]
    collisions = [row for row in misses if matches_recovery(row)]
    print(f"snare_primary_misses={len(misses)} ride_hihat_recovery_collisions={len(collisions)}")
    for row in collisions:
        print(
            f"{row['sample']} got={row['got']} snare={row['snare_level']} "
            f"hihat={row['hihat_level']}/{row['hihat_band']}/{row['hihat_seg']} "
            f"ride={row['ride_level']}/{row['ride_band']}/{row['ride_seg']}"
        )


if __name__ == "__main__":
    main()
