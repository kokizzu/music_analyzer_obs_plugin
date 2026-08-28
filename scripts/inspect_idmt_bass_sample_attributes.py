#!/usr/bin/env python3
"""Print all exported detector attributes for one labelled IDMT bass clip."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ATTRIBUTES = ROOT / "build/idmt_bass_single_track_attributes.tsv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", required=True)
    arguments = parser.parse_args()
    rows = [row for row in csv.DictReader(ATTRIBUTES.open(encoding="utf-8"), delimiter="\t")
            if row["sample_id"] == arguments.sample_id]
    if not rows:
        raise SystemExit(f"sample not found: {arguments.sample_id}")
    fields = (
        "status", "sample_id", "expected_note", "expected_midi", "buffer", "row_label", "row_conf",
        "row_grid", "any_grid", "first_row", "bass_notes", "debug_note", "debug_midi", "debug_owner",
        "debug_conf", "raw_expected_ratio", "raw_tuned_ratio", "raw_tuned_cent_offset",
        "raw_expected_rank", "raw_octave_up_ratio", "raw_fifth_up_ratio", "bass_score", "spectral_level",
        "pitch_confidence", "periodicity", "harmonicity", "harmonic_product_score",
    )
    for row in rows:
        print(" ".join(f"{field}={row[field]}" for field in fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
