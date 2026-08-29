#!/usr/bin/env python3
"""Compare piano fixtures whose expected note is owned as Guitar."""

import csv
import os
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / "analyzer_real_note_samples"
FEATURES = (
    "debug_conf", "keyboard_score", "guitar_score", "vocal_score", "other_score",
    "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error",
    "centroid", "slope", "noise", "partial1", "partial2", "partial3", "partial4",
    "partial5",
)


def fixture_command(shard_index: int) -> tuple[list[str], dict[str, str], Path]:
    attributes = ROOT / f"build/full_mix_piano_guitar_attributes_shard_{shard_index}.tsv"
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "piano",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT": "16",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX": str(shard_index),
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(attributes),
        }
    )
    return [str(BINARY)], environment, attributes


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
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    jobs = [fixture_command(shard_index) for shard_index in (0, 4, 8, 12)]
    processes = [
        subprocess.Popen(command, cwd=ROOT, env=environment, stdout=subprocess.DEVNULL)
        for command, environment, _ in jobs
    ]
    for process in processes:
        if process.wait() != 0:
            raise SystemExit("piano guitar-ownership fixture run failed")
    for _, _, attributes in jobs:
        with attributes.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                grouped[row["sample_id"]].append(row)

    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rows in grouped.values():
        row = expected_note_row(rows)
        if row is not None and row["debug_owner"] == "guitar":
            buckets[row["buffer_visual_strongest_row"]].append(row)

    for visual, rows in sorted(buckets.items()):
        print(f"guitar-owned piano visual-{visual} samples={len(rows)}")
        for feature in FEATURES:
            mean = sum(float(row[feature]) for row in rows) / len(rows)
            print(f"  {feature}={mean:.4f}")
        for row in rows[:32]:
            print(
                f"  row={row['sample_id']} expected={row['expected_note']} "
                f"conf={row['debug_conf']} keyboard={row['keyboard_score']} "
                f"guitar={row['guitar_score']} vocal={row['vocal_score']} "
                f"other={row['other_score']} level={row['spectral_level']} "
                f"pitch={row['pitch_confidence']} period={row['periodicity']} "
                f"harmonicity={row['harmonicity']} fit={row['fit_error']} "
                f"centroid={row['centroid']} slope={row['slope']} noise={row['noise']} "
                f"p2={row['partial2']} p3={row['partial3']} p4={row['partial4']} "
                f"p5={row['partial5']}"
            )
        if len(rows) > 32:
            print(f"  ... {len(rows) - 32} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
