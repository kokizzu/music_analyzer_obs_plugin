#!/usr/bin/env python3
"""Export and report full-mix ownership for the real guitar fixture subset."""

import csv
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "build" / "real_note_guitar_ownership.tsv"


def main() -> int:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "guitar",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT": "100",
    })
    completed = subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")],
                               cwd=ROOT, env=environment, check=False)
    by_sample = {}
    with ATTRIBUTES.open(encoding="utf-8", newline="") as attributes_file:
        for row in csv.DictReader(attributes_file, delimiter="\t"):
            by_sample.setdefault(row["sample_id"], row)
    missing = [row for row in by_sample.values() if row["detected_expected_row"] == "0"]
    print(f"guitar_fixture_count={len(by_sample)} expected_row_misses={len(missing)}")
    for row in missing:
        print(f"{row['sample_id']} note={row['expected_note']} first={row['first_row']} "
              f"visual={row['visual_first_row']} owner={row['debug_owner']} "
              f"scores=b{row['bass_score']}/k{row['keyboard_score']}/"
              f"g{row['guitar_score']}/v{row['vocal_score']}/o{row['other_score']} "
              f"p={row['pitch_confidence']} per={row['periodicity']} fit={row['fit_error']} "
              f"slope={row['slope']} noise={row['noise']} "
              f"partials={row['partial1']},{row['partial2']},{row['partial3']},"
              f"{row['partial4']},{row['partial5']}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
