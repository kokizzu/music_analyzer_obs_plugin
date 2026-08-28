#!/usr/bin/env python3
"""Export full-mix ownership attributes for every real vocal fixture."""

import csv
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/real_note_vocal_attributes.tsv"


def main() -> int:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": "build/real_note_samples",
        "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "vocals",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(OUTPUT),
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
    })
    subprocess.run([str(ROOT / "build/analyzer_real_note_samples")], cwd=ROOT, env=environment, check=True)
    with OUTPUT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = [row for row in rows if row.get("debug_midi") == row.get("expected_midi")]
    best_by_sample: dict[str, dict[str, str]] = {}
    for row in expected:
        sample = row["sample_id"]
        score = float(row["vocal_score"] or 0.0)
        current = best_by_sample.get(sample)
        if current is None or score > float(current["vocal_score"] or 0.0):
            best_by_sample[sample] = row
    print(f"vocal attribute rows: {len(rows)}, expected-pitch rows: {len(expected)}, samples: {len(best_by_sample)}")
    selected = ("sample_id", "expected_note", "buffer", "first_row", "visual_first_row", "row_conf",
                "debug_owner", "debug_conf", "vocal_score", "pitch_confidence", "periodicity", "fit_error",
                "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5",
                "vocal_tone_profile", "vocal_rejected_polyphony")
    print("\t".join(selected))
    for row in best_by_sample.values():
        print("\t".join(row.get(field, "") for field in selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
