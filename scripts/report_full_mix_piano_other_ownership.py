#!/usr/bin/env python3
"""Compare piano fixtures whose expected note is owned as Other."""

import csv
import os
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / "analyzer_real_note_samples"
ATTRIBUTES = ROOT / "build" / "full_mix_piano_attributes_shard_0.tsv"
FEATURES = (
    "debug_conf", "keyboard_score", "guitar_score", "other_score", "spectral_level",
    "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope",
    "noise", "partial1", "partial2", "partial3", "partial4", "partial5",
)


def run_fixture() -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "piano",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT": "32",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX": "0",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
        }
    )
    subprocess.run([str(BINARY)], cwd=ROOT, env=environment, check=True)


def expected_note_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    last_buffer = max(float(row["buffer"]) for row in rows)
    matching = [
        row
        for row in rows
        if float(row["buffer"]) == last_buffer and row["debug_midi"] == row["expected_midi"]
    ]
    if not matching:
        return None
    return max(matching, key=lambda row: float(row["debug_conf"]))


def main() -> int:
    run_fixture()
    with ATTRIBUTES.open(encoding="utf-8", newline="") as source:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in csv.DictReader(source, delimiter="\t"):
            grouped[row["sample_id"]].append(row)

    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rows in grouped.values():
        row = expected_note_row(rows)
        if row is not None and row["debug_owner"] == "other":
            buckets[row["buffer_visual_strongest_row"]].append(row)

    for visual, rows in sorted(buckets.items()):
        print(f"other-owned piano visual-{visual} samples={len(rows)}")
        for feature in FEATURES:
            mean = sum(float(row[feature]) for row in rows) / len(rows)
            print(f"  {feature}={mean:.4f}")
        for row in rows:
            print(
                f"  row={row['sample_id']} expected={row['expected_note']} "
                f"conf={row['debug_conf']} other={row['other_score']} "
                f"keyboard={row['keyboard_score']} guitar={row['guitar_score']} "
                f"level={row['spectral_level']} pitch={row['pitch_confidence']} "
                f"period={row['periodicity']} harmonicity={row['harmonicity']} "
                f"fit={row['fit_error']} centroid={row['centroid']} "
                f"slope={row['slope']} noise={row['noise']} "
                f"p2={row['partial2']} p3={row['partial3']} p4={row['partial4']} "
                f"p5={row['partial5']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
