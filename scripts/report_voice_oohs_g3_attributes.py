#!/usr/bin/env python3
"""Summarize the focused voice-oohs G3 full-mix attribute capture."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = (
    "debug_note", "debug_midi", "debug_owner", "debug_conf", "bass_score", "keyboard_score",
    "guitar_score", "vocal_score", "other_score", "spectral_level", "pitch_confidence",
    "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise", "partial1",
    "partial2", "partial3", "partial4", "partial5", "vocal_label", "vocal_notes",
	"debug_count",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attributes", required=True, type=Path)
    args = parser.parse_args()
    if not args.attributes.is_file():
        print(f"voice_oohs_attributes_exists=false path={args.attributes}")
        return 1
    with args.attributes.open(encoding="utf-8", newline="") as input_file:
        rows = list(csv.DictReader(input_file, delimiter="\t"))
    print(f"voice_oohs_attributes_rows={len(rows)}")
    for index, row in enumerate(rows[:3], start=1):
        values = " ".join(f"{field}={row.get(field, '')}" for field in FIELDS)
        print(f"sample_{index} {values}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
