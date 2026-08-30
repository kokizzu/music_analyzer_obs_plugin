#!/usr/bin/env python3
"""Measure full-mix Vocal detection on annotated MedleyDB excerpts."""

from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BINARY = REPO_ROOT / "build" / "analyzer_real_note_samples"
MIX_ROOT = REPO_ROOT / "build" / "medleydb_vocal_mix_samples"
STEM_ROOT = REPO_ROOT / "build" / "medleydb_vocal_stem_samples"


def row_count(root: Path) -> int:
    with (root / "manifest.tsv").open(encoding="utf-8", newline="") as source:
        return sum(1 for _ in csv.DictReader(source, delimiter="\t"))


def expected_metric(output: str, total: int) -> tuple[int, int]:
    matches = re.findall(r"expected-row-by-family[^\n]*?vocals=(\d+)/(\d+)", output)
    if not matches:
        raise RuntimeError("missing Vocal expected-row metric")
    hit, observed = map(int, matches[-1])
    if observed != total:
        raise RuntimeError(f"unexpected Vocal total: {observed}, expected {total}")
    return hit, observed


def visible_metric(attribute_path: Path, total: int) -> tuple[int, int]:
    with attribute_path.open(encoding="utf-8", newline="") as source:
        visible = {
            row["sample_id"]
            for row in csv.DictReader(source, delimiter="\t")
            if float(row["vocal_visual_level"] or 0.0) >= 0.25
        }
    return len(visible), total


def main() -> int:
    verify = "--verify" in sys.argv
    stem = "--stem" in sys.argv
    root = STEM_ROOT if stem else MIX_ROOT
    attribute_path = REPO_ROOT / "build" / (
        "medleydb_vocal_stem_attributes.tsv" if stem else "medleydb_vocal_mix_attributes.tsv"
    )
    if not BINARY.is_file():
        raise RuntimeError(f"missing analyzer binary: {BINARY}")
    total = row_count(root)
    attribute_path.unlink(missing_ok=True)
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": str(total),
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(root),
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
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(attribute_path),
    })
    result = subprocess.run([str(BINARY)], env=environment, text=True, capture_output=True)
    if result.returncode:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"analyzer failed with exit status {result.returncode}")
    expected_hit, observed = expected_metric(result.stdout, total)
    visible_hit, visible_total = visible_metric(attribute_path, total)
    expected_percent = expected_hit * 100.0 / observed if observed else 0.0
    visible_percent = visible_hit * 100.0 / visible_total if visible_total else 0.0
    name = "medleydb-vocal-stem" if stem else "medleydb-vocal-mix"
    print(f"attributes={attribute_path}")
    print(f"{name} expected-row={expected_hit}/{observed} ({expected_percent:.1f}%)")
    print(f"{name} visible-vocal-row={visible_hit}/{visible_total} ({visible_percent:.1f}%)")
    minimum_percent = 90.0 if stem else 80.0
    if verify and (expected_percent < minimum_percent or visible_percent < minimum_percent):
        raise RuntimeError(f"MedleyDB Vocal recall below {minimum_percent:.0f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
