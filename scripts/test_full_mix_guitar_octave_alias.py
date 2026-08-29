#!/usr/bin/env python3
"""Guard a real acoustic-guitar octave harmonic against a piano-row takeover."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "build/full_mix_guitar_attributes_shard_0.tsv"
SAMPLE_ID = "guitar_acoustic_010-051-100"


def note_level(notes: str, note: str) -> float:
    for entry in notes.split(","):
        if not entry.startswith(f"{note}:"):
            continue
        return float(entry.split(":", maxsplit=1)[1])
    return 0.0


def main() -> int:
    with ATTRIBUTES.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["sample_id"] == SAMPLE_ID]
    if not rows:
        raise SystemExit(f"missing regression fixture: {SAMPLE_ID}")
    row = rows[-1]
    if row["visual_first_row"] != "guitar":
        raise SystemExit(
            f"expected visual guitar row, got {row['visual_first_row']} for {SAMPLE_ID}"
        )
    guitar_level = note_level(row["guitar_visual_notes"], "D#3")
    piano_level = note_level(row["piano_visual_notes"], "D#3")
    if guitar_level < 0.89 or piano_level > guitar_level * 0.82 + 0.01:
        raise SystemExit(
            f"expected D#3 guitar priority, got guitar={guitar_level:.2f} piano={piano_level:.2f}"
        )
    print(f"guitar octave-alias regression passed: guitar={guitar_level:.2f} piano={piano_level:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
