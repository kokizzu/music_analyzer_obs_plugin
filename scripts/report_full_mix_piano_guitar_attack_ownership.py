#!/usr/bin/env python3
"""Compare attack-time piano candidates that the full-mix model owns as guitar."""

import csv
import os
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / "analyzer_real_note_samples"
SHARDS = (0, 4, 8, 12)
FEATURES = (
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "onset_strength",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "noise",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
)


def command(shard: int) -> tuple[list[str], dict[str, str], Path]:
    attributes = ROOT / "build" / f"full_mix_piano_guitar_attack_attributes_shard_{shard}.tsv"
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER="piano",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="16",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=str(shard),
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(attributes),
        MUSIC_ANALYZER_REAL_NOTE_ATTACK_ATTRIBUTE_EXPORT="1",
    )
    return [str(BINARY)], environment, attributes


def expected_attack_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    first_buffer = min(float(row["buffer"]) for row in rows)
    for row in rows:
        if float(row["buffer"]) == first_buffer and row["debug_midi"] == row["expected_midi"]:
            return row
    return None


def main() -> int:
    jobs = [command(shard) for shard in SHARDS]
    processes = [
        subprocess.Popen(command_line, cwd=ROOT, env=environment)
        for command_line, environment, _ in jobs
    ]
    for process in processes:
        if process.wait() != 0:
            return process.returncode

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for _, _, attributes in jobs:
        with attributes.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                grouped[row["sample_id"]].append(row)

    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rows in grouped.values():
        row = expected_attack_row(rows)
        if row is not None and row["debug_owner"] == "guitar":
            buckets[row["buffer_visual_strongest_row"]].append(row)

    for visual, rows in sorted(buckets.items()):
        print(f"attack guitar-owned piano visual-{visual} samples={len(rows)}")
        for feature in FEATURES:
            mean = sum(float(row[feature]) for row in rows) / len(rows)
            print(f"  {feature}={mean:.4f}")
        for row in rows[:8]:
            print(
                f"  row={row['sample_id']} expected={row['expected_note']} "
                f"conf={row['debug_conf']} guitar={row['guitar_score']} "
                f"onset={row['onset_strength']} pitch={row['pitch_confidence']} "
                f"noise={row['noise']} visual={row['buffer_visual_strongest_row']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
