#!/usr/bin/env python3
"""Measure a deterministic Other-family shard with per-note ownership attributes."""

from __future__ import annotations

import csv
import os
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build/analyzer_real_note_samples"
ATTRIBUTES = ROOT / "build/full_mix_other_attributes_shard_0.tsv"


def main() -> int:
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "other",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT": "4",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX": "0",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
        }
    )
    subprocess.run([str(BINARY)], cwd=ROOT, env=environment, check=True)

    with ATTRIBUTES.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    samples: dict[str, dict[str, str]] = {}
    for row in rows:
        samples.setdefault(row["sample_id"], row)
    raw = Counter(row["first_row"] for row in samples.values())
    visual = Counter(row["visual_first_row"] for row in samples.values())
    wrong = [
        row
        for row in samples.values()
        if row["first_row"] == "other" and row["visual_first_row"] == "piano"
    ]
    print(f"fixtures={len(samples)} raw={dict(raw)} visual={dict(visual)}")
    print(f"raw-other-visual-piano={len(wrong)}")
    for row in wrong[:12]:
        print(
            f"  {row['sample_id']} {row['expected_note']} "
            f"other={row['other_visual_level']} piano={row['piano_visual_level']} "
            f"debug={row['debug_note']}:{row['debug_owner']} "
            f"scores=k{row['keyboard_score']},g{row['guitar_score']},o{row['other_score']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
