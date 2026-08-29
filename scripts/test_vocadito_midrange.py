#!/usr/bin/env python3
"""Measure annotated vocadito D3-F#3 vocal clips in the full-mix analyzer path."""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "build" / "vocadito_midrange_samples"
BINARY = REPO_ROOT / "build" / "analyzer_real_note_samples"


def row_count() -> int:
    manifest = ROOT / "manifest.tsv"
    if not manifest.is_file():
        raise RuntimeError(f"missing fixture manifest: {manifest}")
    with manifest.open(newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file, delimiter="\t"))
    if not rows or any(row.get("family") != "vocals" for row in rows):
        raise RuntimeError("vocadito manifest must contain vocal rows")
    return len(rows)


def metric(output: str, name: str, total: int) -> tuple[int, int]:
    pattern = rf"{re.escape(name)}(?:=| )(\d+)/(\d+)"
    matches = re.findall(pattern, output)
    if not matches:
        raise RuntimeError(f"missing {name} metric in analyzer output")
    hit, observed_total = map(int, matches[-1])
    if observed_total != total:
        raise RuntimeError(f"unexpected {name} total: {observed_total}, expected {total}")
    return hit, observed_total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--minimum-expected-percent", type=int, default=80)
    args = parser.parse_args()
    if not BINARY.is_file():
        raise RuntimeError(f"missing analyzer binary: {BINARY}")
    total = row_count()
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": str(total),
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": str(total),
            "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        }
    )
    result = subprocess.run([str(BINARY)], env=environment, text=True, capture_output=True)
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"analyzer failed with exit status {result.returncode}")
    summaries = [line for line in result.stdout.splitlines() if "by-family" in line]
    print("analyzer-family-summaries=")
    for line in summaries:
        print(line)
    expected_lines = [line for line in result.stdout.splitlines() if "expected-row-by-family" in line]
    if not expected_lines:
        raise RuntimeError("missing expected-row-by-family summary")
    expected_segment = expected_lines[-1].split("expected-row-by-family", 1)[1].split(
        "first-row-by-family", 1
    )[0]
    expected_hit, _ = metric(expected_segment, "vocals", total)
    any_hit, _ = metric(result.stdout, "any-row", total)
    expected_percent = expected_hit * 100.0 / total
    any_percent = any_hit * 100.0 / total
    print(
        f"vocadito-midrange expected-row={expected_hit}/{total} ({expected_percent:.1f}%) "
        f"any-row={any_hit}/{total} ({any_percent:.1f}%)"
    )
    if args.verify and expected_percent < args.minimum_expected_percent:
        raise RuntimeError(
            f"expected-row recall {expected_percent:.1f}% is below {args.minimum_expected_percent}%"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
