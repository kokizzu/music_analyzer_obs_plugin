#!/usr/bin/env python3
"""Measure piano fixtures whose first full-mix display row is guitar."""

import csv
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "real_note_piano_ownership.tsv"
FIELDS = (
    "guitar_score", "other_score", "spectral_level", "pitch_confidence", "periodicity",
    "fit_error", "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5",
)


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "0"))
    except ValueError:
        return 0.0


def main() -> int:
    env = os.environ.copy()
    env.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "piano",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(OUTPUT),
    })
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

    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    with OUTPUT.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            by_sample[row["sample_id"]].append(row)
    routed = []
    for sample_id, rows in by_sample.items():
        # first_row is a fixture aggregate repeated on every buffer. Select an
        # actual guitar-winning buffer so the reported attributes describe the
        # duplicate display decision rather than an arbitrary earlier frame.
        first = next((row for row in rows if row.get("buffer_strongest_row") == "guitar"), None)
        if first is not None:
            routed.append(first)
    print(f"piano fixtures={len(by_sample)} first_row_guitar={len(routed)}")
    if not routed:
        return 0
    print("route medians " + " ".join(
        f"{field}={statistics.median(number(row, field) for row in routed):.3f}"
        for field in FIELDS
    ))
    for row in sorted(routed, key=lambda item: item["sample_id"])[:20]:
        print(" ".join(f"{field}={row.get(field, '')}" for field in (
            "sample_id", "source", "expected_note", "expected_midi", "buffer", "debug_owner",
            "debug_conf", *FIELDS,
        )))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
