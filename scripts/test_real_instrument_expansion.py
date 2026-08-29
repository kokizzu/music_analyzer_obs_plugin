#!/usr/bin/env python3
"""Run the new external real-instrument corpus as a measured regression suite."""

from __future__ import annotations

import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "build" / "real_instrument_expansion_samples"
BINARY = REPO / "build" / "analyzer_real_note_samples"
SHARD_COUNT = 16
FAMILIES = ("bass", "guitar", "piano", "other")


def run_shard(index: int, base_environment: dict[str, str]) -> tuple[int, int, str]:
    environment = base_environment.copy()
    environment["MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT"] = str(SHARD_COUNT)
    environment["MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX"] = str(index)
    completed = subprocess.run(
        [str(BINARY)], cwd=REPO, env=environment, check=False, text=True, capture_output=True
    )
    return index, completed.returncode, completed.stdout + completed.stderr


def family_counts(output: str, marker: str) -> dict[str, tuple[int, int]]:
    line = next((line for line in reversed(output.splitlines()) if marker in line), "")
    segment = line.split(marker, 1)[1]
    if marker == "expected-row-by-family":
        segment = segment.split("first-row-by-family", 1)[0]
    counts = {name: (int(hit), int(total)) for name, hit, total in re.findall(r"(bass|guitar|piano|other)=(\d+)/(\d+)", segment)}
    if set(counts) != set(FAMILIES):
        raise RuntimeError(f"missing {marker} summary: {line or '[none]'}")
    return counts


def main() -> None:
    if not ROOT.is_dir() or not (ROOT / "manifest.tsv").is_file():
        raise SystemExit("missing expansion manifest; run make apply-real-instrument-expansion-fixtures first")
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
            "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
			"MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "80",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "75",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT": "80",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT": "75",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT": "90",
			"MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT": "85",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT": "0",
			"MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT": "0",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "1",
        }
    )
    with ThreadPoolExecutor(max_workers=SHARD_COUNT) as executor:
        results = list(executor.map(lambda index: run_shard(index, environment), range(SHARD_COUNT)))
    expected_totals = {family: [0, 0] for family in FAMILIES}
    first_totals = {family: [0, 0] for family in FAMILIES}
    failed = False
    for index, return_code, output in results:
        expected = family_counts(output, "expected-row-by-family")
        first = family_counts(output, "first-row-by-family")
        for family in FAMILIES:
            expected_totals[family][0] += expected[family][0]
            expected_totals[family][1] += expected[family][1]
            first_totals[family][0] += first[family][0]
            first_totals[family][1] += first[family][1]
        if return_code:
            print(f"--- failing shard {index} (exit {return_code}) ---")
            print(output, end="" if output.endswith("\n") else "\n")
        failed = failed or return_code != 0
    print("real-instrument expected-row=" + " ".join(
        f"{family}={hit}/{total} ({100 * hit // total}%)"
        for family, (hit, total) in expected_totals.items()
    ))
    print("real-instrument first-row=" + " ".join(
        f"{family}={hit}/{total} ({100 * hit // total}%)"
        for family, (hit, total) in first_totals.items()
    ))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
