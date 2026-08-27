#!/usr/bin/env python3
"""Measure guitar fixtures lost by full-mix ownership arbitration."""

import csv
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "real_note_guitar_ownership.tsv"
BASELINE = ROOT / "build" / "real_note_ownership.tsv"


def value(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0"))
    except ValueError:
        return 0.0


def main() -> int:
    env = os.environ.copy()
    env.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "guitar",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(OUTPUT),
    })
    if "--report" not in sys.argv:
        completed = subprocess.run(
            [str(ROOT / "build" / "analyzer_real_note_samples")],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode:
            return completed.returncode

    with OUTPUT.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["sample_id"]].append(row)

    misses = []
    for sample_id, sample_rows in grouped.items():
        if any(row.get("detected_expected_row") == "1" for row in sample_rows):
            continue
        strongest = max(
            sample_rows,
            key=lambda row: (value(row, "raw_expected_ratio"), value(row, "guitar_score")),
        )
        misses.append(strongest)

    print(f"guitar fixtures={len(grouped)} missed_expected_row={len(misses)}")
    for row in sorted(misses, key=lambda item: item["sample_id"]):
        fields = (
            "sample_id", "source", "expected_note", "expected_midi", "buffer",
            "debug_owner", "debug_conf", "bass_score", "keyboard_score", "guitar_score",
            "other_score", "spectral_level", "pitch_confidence", "periodicity", "fit_error",
            "centroid", "slope", "noise", "partial1", "partial2", "partial3", "partial4", "partial5",
            "raw_expected_ratio", "raw_tuned_abs_cent_offset",
        )
        print(" ".join(f"{field}={row.get(field, '')}" for field in fields))

    if not BASELINE.exists():
        return 0
    with BASELINE.open(encoding="utf-8", newline="") as stream:
        baseline_rows = list(csv.DictReader(stream, delimiter="\t"))
    baseline_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in baseline_rows:
        baseline_by_sample[row["sample_id"]].append(row)
    print("baseline expected-row evidence")
    for current in sorted(misses, key=lambda item: item["sample_id"]):
        candidates = [
            row for row in baseline_by_sample[current["sample_id"]]
            if row.get("detected_expected_row") == "1"
        ]
        if not candidates:
            print(f"sample_id={current['sample_id']} baseline_expected_row=missing")
            continue
        strongest = max(
            candidates,
            key=lambda row: (value(row, "raw_expected_ratio"), value(row, "guitar_score")),
        )
        fields = (
            "sample_id", "buffer", "debug_owner", "debug_conf", "guitar_score",
            "spectral_level", "pitch_confidence", "periodicity", "fit_error", "centroid", "slope", "noise",
            "partial1", "partial2", "partial3", "partial4", "partial5",
            "raw_expected_ratio", "raw_tuned_abs_cent_offset",
        )
        print(" ".join(f"baseline_{field}={strongest.get(field, '')}" for field in fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
