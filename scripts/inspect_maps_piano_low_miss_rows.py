#!/usr/bin/env python3
"""Print the schema and low-MIDI missed rows from MAPS attribute output."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def midi_set(value: str) -> set[int]:
    if not value or value == "--":
        return set()
    return {int(part) for part in value.split(",")}


def pitch_class_set(value: str) -> set[str]:
    if not value or value == "--":
        return set()
    return set(value.split(","))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_maps_piano_low_miss_rows.py ATTRIBUTE_TSV", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames or []
        print("fields=" + ",".join(fields))
        printed = 0
        for row in reader:
            try:
                expected = midi_set(row.get("expected_midis", ""))
            except ValueError:
                continue
            low_expected = sorted(midi for midi in expected if midi <= 35)
            missing_pcs = pitch_class_set(row.get("expected_pcs", "")) - pitch_class_set(
                row.get("detected_keyboard_pcs", "")
            )
            if not low_expected or not missing_pcs:
                continue
            details = (
                "recording",
                "center_sample",
                "expected_midis",
                "detected_keyboard_midis",
                "keyboard_midi_levels",
                "audio_rms",
                "audio_peak",
            )
            print(
                f"missed_low_midis={','.join(map(str, low_expected))}\t"
                f"missing_pcs={','.join(sorted(missing_pcs))}\t"
                + "\t".join(f"{field}={row.get(field, '')}" for field in details)
            )
            printed += 1
        print(f"low_midi_misses={printed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
