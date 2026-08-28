#!/usr/bin/env python3
"""Measure real IDMT bass note detection without weakening regression gates."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "build/idmt_bass_single_track_fixture"
BINARY = ROOT / "build/analyzer_real_note_samples"
OUTPUT = ROOT / "build/idmt_bass_single_track_measurement.out"
ATTRIBUTES = ROOT / "build/idmt_bass_single_track_attributes.tsv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-recall", type=float, default=0.0)
    arguments = parser.parse_args()
    if not (FIXTURE / "manifest.tsv").is_file():
        raise SystemExit("missing IDMT bass fixture; run make prepare-idmt-bass-single-track-fixture")
    if not BINARY.is_file():
        raise SystemExit("missing analyzer_real_note_samples binary")
    sample_count = len((FIXTURE / "manifest.tsv").read_text(encoding="utf-8").splitlines()) - 1
    if sample_count <= 0:
        raise SystemExit("IDMT bass fixture has no samples")
    max_failures = 999999
    if arguments.min_recall > 0.0:
        max_failures = int(sample_count * max(0.0, 1.0 - arguments.min_recall / 100.0))
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": str(sample_count),
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(FIXTURE),
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "1",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": str(max_failures),
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
    })
    with OUTPUT.open("w", encoding="utf-8") as output:
        result = subprocess.run([str(BINARY)], cwd=ROOT, env=environment, text=True,
                                stdout=output, stderr=subprocess.STDOUT, check=False)
    print(OUTPUT.read_text(encoding="utf-8"), end="")
    if arguments.min_recall > 0.0:
        print(f"IDMT bass recall gate: >= {arguments.min_recall:.1f}% ({max_failures} failures allowed)")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
