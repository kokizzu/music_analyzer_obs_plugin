#!/usr/bin/env python3
"""Evaluate a narrow ride-band tie-break against protected hi-hat samples."""

import csv
from pathlib import Path


INPUTS = {
    "ride": Path("build/hf_drum_kit_primary_attribute_rows_ride.tsv"),
    "hihat": Path("build/hf_drum_kit_primary_attribute_rows_hihat.tsv"),
}


def qualifies(row: dict[str, str], min_band_ratio: float) -> bool:
    hihat_level = float(row["hihat_level"])
    ride_level = float(row["ride_level"])
    return (
        hihat_level > 0.30
        and ride_level > 0.30
        and ride_level + 0.025 >= hihat_level
        and float(row["ride_band"]) >= float(row["hihat_band"]) * min_band_ratio
        and float(row["hihat_seg"]) >= 3.20
        and float(row["hihat_seg"]) <= 6.10
        and float(row["rim_level"]) <= 0.805
    )


def main() -> None:
    rows_by_expected = {}
    for expected, path in INPUTS.items():
        with path.open(encoding="utf-8", newline="") as source:
            rows_by_expected[expected] = list(csv.DictReader(source, delimiter="\t"))

    for ratio in (1.0, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5):
        ride_rows = rows_by_expected["ride"]
        hihat_rows = rows_by_expected["hihat"]
        corrected = [row for row in ride_rows if qualifies(row, ratio) and row["got"] != "ride"]
        harmed = [row for row in hihat_rows if qualifies(row, ratio) and row["got"] == "hihat"]
        print(f"ratio={ratio:.2f} corrected_ride_misses={len(corrected)} harmed_hihat_hits={len(harmed)}")

    ratio = 1.2
    print("ratio=1.20 collision details")
    for expected, rows in rows_by_expected.items():
        selected = [
            row
            for row in rows
            if qualifies(row, ratio)
            and ((expected == "ride" and row["got"] != "ride") or (expected == "hihat" and row["got"] == "hihat"))
        ]
        for row in selected:
            print(
                f"  {expected} {row['sample']} got={row['got']} "
                f"low={row['energy_low']} mid={row['energy_mid']} high={row['energy_high']} "
                f"hihat={row['hihat_level']}/{row['hihat_band']}/{row['hihat_seg']} "
                f"ride={row['ride_level']}/{row['ride_band']}/{row['ride_seg']} "
                f"rim={row['rim_level']}/{row['rim_band']} "
                f"crash={row['crash_level']}/{row['crash_band']} flags={row['rule_flags']}"
            )

    print("current ride recovery candidates")
    for row in rows_by_expected["ride"]:
        if qualifies(row, 1.2):
            print(
                f"  {row['sample']} got={row['got']} rim={row['rim_level']} "
                f"hihat={row['hihat_level']}/{row['hihat_seg']} "
                f"ride={row['ride_level']}/{row['ride_seg']}"
            )


if __name__ == "__main__":
    main()
