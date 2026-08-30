#!/usr/bin/env python3
"""Verify Iowa Steinway fixtures through the normal full-mix Piano row."""

from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BINARY = REPO_ROOT / "build" / "analyzer_real_note_samples"
ROOT = REPO_ROOT / "build" / "iowa_piano_midrange_samples"
ATTRIBUTE_PATH = REPO_ROOT / "build" / "iowa_piano_midrange_attributes.tsv"


def row_count() -> int:
    manifest = ROOT / "manifest.tsv"
    with manifest.open(encoding="utf-8", newline="") as source:
        return sum(1 for _ in csv.DictReader(source, delimiter="\t"))


def expected_row_metric(output: str, total: int) -> tuple[int, int]:
    matches = re.findall(r"expected-row-by-family[^\n]*?piano=(\d+)/(\d+)", output)
    if not matches:
        raise RuntimeError("missing Piano expected-row metric in analyzer output")
    hit, observed_total = map(int, matches[-1])
    if observed_total != total:
        raise RuntimeError(f"unexpected Piano total: {observed_total}, expected {total}")
    return hit, observed_total


def visible_piano_metric(total: int) -> tuple[int, int]:
    with ATTRIBUTE_PATH.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        visible = {
            row["sample_id"]
            for row in rows
            if float(row["piano_visual_level"] or 0.0) >= 0.25
        }
    if len(visible) > total:
        raise RuntimeError(f"unexpected visible Piano total: {len(visible)}, expected at most {total}")
    return len(visible), total


def main() -> int:
    verify = "--verify" in sys.argv
    details = "--details" in sys.argv
    attributes = "--attributes" in sys.argv or verify
    if not BINARY.is_file():
        raise RuntimeError(f"missing analyzer binary: {BINARY}")
    if not (ROOT / "manifest.tsv").is_file():
        print("iowa-piano-fixtures=incomplete manifest=missing expected=108")
        return 1
    total = row_count()
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": str(total),
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
    })
    if details:
        environment.update({
            "MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLES": "1",
            "MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLE_LIMIT": "108",
        })
    if attributes:
        ATTRIBUTE_PATH.unlink(missing_ok=True)
        environment["MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV"] = str(ATTRIBUTE_PATH)
    result = subprocess.run([str(BINARY)], env=environment, text=True, capture_output=True)
    if result.returncode:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"analyzer failed with exit status {result.returncode}")
    if details:
        sys.stdout.write(result.stdout)
    if attributes:
        print(f"attributes={ATTRIBUTE_PATH}")
    expected_hit, observed_total = expected_row_metric(result.stdout, total)
    visual_hit, visual_total = visible_piano_metric(total)
    expected_percent = expected_hit * 100.0 / observed_total if observed_total else 0.0
    visual_percent = visual_hit * 100.0 / visual_total if visual_total else 0.0
    print(f"iowa-piano-midrange expected-row={expected_hit}/{observed_total} ({expected_percent:.1f}%)")
    print(f"iowa-piano-midrange visible-piano-row={visual_hit}/{visual_total} ({visual_percent:.1f}%)")
    if verify and expected_percent < 80.0:
        raise RuntimeError(f"Iowa Piano expected-row recall below 80%: {expected_percent:.1f}%")
    if verify and visual_percent < 75.0:
        raise RuntimeError(f"Iowa Piano visible Piano recall below 75%: {visual_percent:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
