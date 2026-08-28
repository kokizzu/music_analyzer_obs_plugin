#!/usr/bin/env python3
"""Print compact real-note attribute rows for a known sample fixture."""

import csv
from pathlib import Path
import sys


FIELDS = (
    "buffer", "sample_id", "family", "expected_note", "buffer_strongest_row",
    "buffer_visual_strongest_row", "rms", "low", "mid", "high", "onset_strength",
    "decay_rate", "pitch_stability", "simultaneous_onset", "debug_note", "debug_owner",
    "debug_conf", "bass_score", "keyboard_score", "guitar_score", "vocal_score",
    "other_score", "spectral_level", "pitch_confidence", "periodicity", "harmonicity",
    "fit_error", "centroid", "slope", "noise", "partial1", "partial2", "partial3",
    "partial4", "partial5",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: inspect_real_note_sample_attributes.py SAMPLE_ID")
    sample_id = sys.argv[1]
    with Path("build/real_note_full_mix_attributes.tsv").open(encoding="utf-8", newline="") as file:
        rows = [row for row in csv.DictReader(file, delimiter="\t") if row["sample_id"] == sample_id]
    if not rows:
        raise SystemExit(f"sample not found: {sample_id}")
    missing = [field for field in FIELDS if field not in rows[0]]
    if missing:
        raise SystemExit(f"missing TSV fields: {', '.join(missing)}")
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
