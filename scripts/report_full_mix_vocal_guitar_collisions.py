#!/usr/bin/env python3
"""Report vocal fixtures whose full-mix candidate ownership prefers guitar."""

from __future__ import annotations

import csv
import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "build" / "real_note_samples"
SHARD_COUNT = 4


def output_path(index: int) -> Path:
    return ROOT / "build" / f"full_mix_vocal_guitar_collisions_{index}.tsv"


def snapshot_path(name: str) -> Path:
    return ROOT / "build" / f"full_mix_vocal_guitar_collisions_{name}.tsv"


def run_shard(index: int) -> None:
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=str(SAMPLE_ROOT),
        MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER="vocals",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=str(SHARD_COUNT),
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=str(index),
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(output_path(index)),
    )
    subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                   env=environment, check=True, stdout=subprocess.DEVNULL)


def read_snapshot(name: str) -> dict[str, dict[str, str]]:
    with snapshot_path(name).open(encoding="utf-8", newline="") as stream:
        return {row["sample_id"]: row for row in csv.DictReader(stream, delimiter="\t")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot")
    parser.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    arguments = parser.parse_args()
    if arguments.compare:
        before_name, after_name = arguments.compare
        before = read_snapshot(before_name)
        after = read_snapshot(after_name)
        fields = ("detected_expected_row", "first_row", "visual_first_row", "debug_owner",
                  "debug_conf", "keyboard_score", "guitar_score", "vocal_score")
        changed = [
            sample_id for sample_id in sorted(set(before) | set(after))
            if any(before.get(sample_id, {}).get(field) != after.get(sample_id, {}).get(field)
                   for field in fields)
        ]
        print(f"before={before_name} after={after_name} changed={len(changed)}")
        print("sample_id\texpected_note\t" + "\t".join(
            f"before_{field}\tafter_{field}" for field in fields
        ))
        for sample_id in changed:
            before_row = before.get(sample_id, {})
            after_row = after.get(sample_id, {})
            print(sample_id + "\t" + before_row.get("expected_note", after_row.get("expected_note", "")) + "\t" + "\t".join(
                value
                for field in fields
                for value in (before_row.get(field, ""), after_row.get(field, ""))
            ))
        return 0
    if not SAMPLE_ROOT.is_dir():
        raise SystemExit("missing real-note sample root")
    with ThreadPoolExecutor(max_workers=SHARD_COUNT) as executor:
        list(executor.map(run_shard, range(SHARD_COUNT)))
    rows: dict[str, dict[str, str]] = {}
    for index in range(SHARD_COUNT):
        with output_path(index).open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                rows.setdefault(row["sample_id"], row)
    if arguments.snapshot:
        fields = tuple(next(iter(rows.values())))
        with snapshot_path(arguments.snapshot).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows.values())
    collisions = [row for row in rows.values()
                  if row["first_row"] == "guitar" or row["debug_owner"] == "guitar"]
    print(f"fixtures={len(rows)} guitar-collisions={len(collisions)}")
    fields = ("sample_id", "source", "expected_note", "debug_note", "debug_owner", "debug_conf",
              "detected_expected_row", "first_row", "visual_first_row", "keyboard_score",
              "guitar_score", "vocal_score", "spectral_level", "pitch_confidence", "periodicity",
              "fit_error", "centroid", "slope", "noise", "partial2", "partial3", "partial4",
              "partial5")
    print("\t".join(fields))
    for row in collisions:
        print("\t".join(row.get(field, "") for field in fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
