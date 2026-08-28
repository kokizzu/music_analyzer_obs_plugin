#!/usr/bin/env python3
"""Run the existing real-note analyzer harness on generated MIR-1K fixtures."""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys


FIXTURE_ROOT = pathlib.Path("tests/fixtures/mir1k_clean_vocals")
MIX_FIXTURE_ROOT = pathlib.Path("build/mir1k_vocal_fixtures/vocal_mixes")


def test_binary() -> pathlib.Path:
    candidates = sorted(path for path in pathlib.Path("build").rglob("analyzer_real_note_samples")
                        if path.is_file() and os.access(path, os.X_OK))
    if not candidates:
        raise SystemExit(
            "analyzer_real_note_samples is not built; run the existing real-note test target first")
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-mix", action="store_true")
    parser.add_argument("--attributes", action="store_true")
    parser.add_argument("--mixed-fixtures", action="store_true")
    parser.add_argument("--measure-only", action="store_true")
    args = parser.parse_args()
    fixture_root = MIX_FIXTURE_ROOT if args.mixed_fixtures else FIXTURE_ROOT
    if not (fixture_root / "manifest.tsv").is_file():
        raise SystemExit("MIR-1K fixtures are missing; run make prepare-mir1k-vocal-fixtures first")

    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(fixture_root),
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": "200",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0" if args.measure_only else ("98" if args.full_mix else "0"),
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0" if args.measure_only else ("70" if args.full_mix else "0"),
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0" if args.measure_only else ("8" if args.full_mix else "0"),
    })
    if args.full_mix:
        environment["MUSIC_ANALYZER_REAL_NOTE_FULL_MIX"] = "1"
    if args.attributes:
        attribute_path = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")
        attribute_path.parent.mkdir(parents=True, exist_ok=True)
        environment["MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV"] = str(attribute_path)
    print("mode: " + ("full-mix" if args.full_mix else "vocal-source"))
    print(f"fixture root: {fixture_root}")
    return subprocess.run([str(test_binary())], env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
