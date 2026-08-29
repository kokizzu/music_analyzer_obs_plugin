#!/usr/bin/env python3
"""Measure full-mix note and ownership recall on external URMP stem fixtures."""

from __future__ import annotations

import csv
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE_ROOT = ROOT / "build" / "urmp_analyzer_cases"
SHARDS = 4


def output_path(index: int) -> Path:
    return ROOT / "build" / f"urmp_analyzer_attributes_{index}.tsv"


def run_shard(sample_root: Path, required_samples: int, output_prefix: str, index: int) -> None:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(sample_root),
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": str(required_samples),
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT": str(SHARDS),
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX": str(index),
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ROOT / "build" / f"{output_prefix}_{index}.tsv"),
    })
    subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                   env=environment, check=True, stdout=subprocess.DEVNULL)


def read_rows(output_prefix: str) -> dict[str, dict[str, str]]:
    samples: dict[str, dict[str, str]] = {}
    for index in range(SHARDS):
        with (ROOT / "build" / f"{output_prefix}_{index}.tsv").open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                sample = samples.setdefault(row["sample_id"], row.copy())
                for field in ("detected", "detected_anywhere", "detected_expected_row"):
                    if row[field] == "1":
                        sample[field] = "1"
    return samples


def ratio(rows: list[dict[str, str]], field: str) -> str:
    hits = sum(row.get(field) == "1" for row in rows)
    return f"{hits}/{len(rows)} ({100 * hits // len(rows) if rows else 0}%)"


def main() -> int:
    started = time.perf_counter()
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--mixtures", action="store_true")
    arguments = parser.parse_args()
    sample_root = ROOT / "build" / ("urmp_mixture_cases" if arguments.mixtures else "urmp_analyzer_cases")
    required_samples = 800 if arguments.mixtures else 1300
    output_prefix = "urmp_mixture_attributes" if arguments.mixtures else "urmp_analyzer_attributes"
    if not (sample_root / "manifest.tsv").is_file():
        print("status=missing fixtures; run make apply-urmp-analyzer-cases first", file=sys.stderr)
        return 1
    with ThreadPoolExecutor(max_workers=SHARDS) as executor:
        list(executor.map(lambda index: run_shard(sample_root, required_samples, output_prefix, index), range(SHARDS)))
    samples = read_rows(output_prefix)
    rows = list(samples.values())
    by_instrument: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_instrument.setdefault(row["source"].removeprefix("urmp-"), []).append(row)
    print(f"urmp-cases={len(rows)}")
    print("any-note=" + ratio(rows, "detected_anywhere"))
    print("expected-row=" + ratio(rows, "detected_expected_row"))
    print("by-instrument:")
    for instrument, group in sorted(by_instrument.items()):
        print(f"  {instrument} any={ratio(group, 'detected_anywhere')} expected-row={ratio(group, 'detected_expected_row')}")
    if arguments.verify:
        expected_hits = sum(row.get("detected_expected_row") == "1" for row in rows)
        failures: list[str] = []
        if len(rows) < required_samples:
            failures.append(f"expected at least {required_samples} URMP cases, got {len(rows)}")
        expected_floor = 80 if arguments.mixtures else 90
        per_instrument_floor = 70 if arguments.mixtures else 75
        if expected_hits * 100 < len(rows) * expected_floor:
            failures.append(f"expected-row recall below {expected_floor}%: {expected_hits}/{len(rows)}")
        for instrument, group in sorted(by_instrument.items()):
            hits = sum(row.get("detected_expected_row") == "1" for row in group)
            if hits * 100 < len(group) * per_instrument_floor:
                failures.append(
                    f"{instrument} expected-row recall below {per_instrument_floor}%: {hits}/{len(group)}"
                )
        if failures:
            print("status=failed " + "; ".join(failures), file=sys.stderr)
            return 1
    print(f"duration-seconds={time.perf_counter() - started:.2f}")
    print("status=ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
