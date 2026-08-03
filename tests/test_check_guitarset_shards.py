#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_guitarset_shards.py"


def write_log(path: pathlib.Path, excerpts: int, windows: int, note_hits: int, note_total: int,
              chord_hits: int, chord_total: int, guitar_tp: int, guitar_fp: int, guitar_fn: int,
              chord_tp: int, chord_fp: int, chord_fn: int,
              primary_chord_hits: int | None = None) -> None:
    if primary_chord_hits is None:
        primary_chord_hits = chord_hits
    path.write_text(
        "analyzer_guitarset: 74 checks passed "
        f"(excerpts {excerpts}/40, windows {windows}, read failures 0, no-candidate excerpts 0, "
        f"unusable 0, note hits {note_hits}/{note_total}, chord hits {chord_hits}/{chord_total}, "
        f"primary chord hits {primary_chord_hits}/{chord_total}, "
        f"major/minor chord hits {chord_hits}/{chord_total}, other chord hits 0/0, "
        "guitar precision 70.00%, guitar recall 75.00%, F1 72.00%, contamination 0.00%, "
        "false vocal windows 0.00%, ambiguous 0/100, row leaks bass/keys/vocal/other 0/0/0/0, "
        f"tp/fp/fn {guitar_tp}/{guitar_fp}/{guitar_fn}, "
        "guitar chord precision 68.00%, guitar chord recall 65.00%, F1 66.00%, "
        f"tp/fp/fn {chord_tp}/{chord_fp}/{chord_fn}, "
        f"chord quality hits maj {chord_hits}/{chord_total}, "
        f"simple chord hits {chord_hits}/{chord_total} 65.00%, "
        f"simple major/minor hits {chord_hits}/{chord_total} 65.00%, simple other hits 0/0 0.00%, "
        "active notes min/avg/max 2/3.90/6, pitch classes min/avg/max 2/3.37/4)\n"
    )


def run_checker(paths: list[pathlib.Path], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(path) for path in paths), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_aggregates_shards_before_thresholds() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        first = root / "first.out"
        second = root / "second.out"
        write_log(first, 10, 60, 60, 100, 30, 60, 55, 45, 15, 30, 25, 30)
        write_log(second, 10, 60, 95, 100, 45, 60, 95, 10, 5, 45, 10, 15)
        result = run_checker(
            [first, second],
            "--required-excerpts", "20",
            "--required-windows", "120",
            "--min-recall-percent", "75",
            "--min-precision-percent", "70",
            "--min-guitar-recall-percent", "85",
            "--min-chord-checks", "120",
            "--min-chord-recall-percent", "60",
            "--min-chord-precision-percent", "60",
            "--min-primary-chord-hits", "75",
            "--min-major-minor-chord-recall-percent", "60",
            "--min-simple-chord-recall-percent", "60",
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        if "check_guitarset_shards: ok" not in result.stdout:
            raise AssertionError(result.stdout)


def test_fails_aggregate_precision() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        only = root / "only.out"
        write_log(only, 20, 120, 100, 120, 80, 120, 10, 90, 10, 80, 10, 40)
        result = run_checker(
            [only],
            "--required-excerpts", "20",
            "--required-windows", "120",
            "--min-precision-percent", "70",
            "--min-guitar-recall-percent", "0",
            "--min-recall-percent", "0",
            "--min-chord-checks", "0",
        )
        if result.returncode == 0:
            raise AssertionError("expected aggregate precision failure")
        if "guitar precision" not in result.stderr:
            raise AssertionError(result.stderr)


def test_single_note_gate_skips_chord_recall() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        only = root / "only.out"
        write_log(only, 20, 120, 120, 120, 0, 0, 120, 0, 0, 0, 10, 0)
        result = run_checker(
            [only],
            "--required-excerpts", "20",
            "--required-windows", "120",
            "--min-recall-percent", "100",
            "--min-precision-percent", "100",
            "--min-guitar-recall-percent", "100",
            "--min-chord-checks", "0",
            "--min-chord-recall-percent", "99",
            "--max-single-note-chord-false-percent", "20",
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)


def test_fails_primary_chord_hits() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        only = root / "only.out"
        write_log(only, 20, 120, 120, 120, 100, 120, 120, 0, 0, 100, 0, 20,
                  primary_chord_hits=70)
        result = run_checker(
            [only],
            "--required-excerpts", "20",
            "--required-windows", "120",
            "--min-recall-percent", "100",
            "--min-precision-percent", "100",
            "--min-guitar-recall-percent", "100",
            "--min-chord-checks", "120",
            "--min-chord-recall-percent", "80",
            "--min-chord-precision-percent", "80",
            "--min-primary-chord-hits", "90",
        )
        if result.returncode == 0:
            raise AssertionError("expected primary chord hit failure")
        if "primary chord hits" not in result.stderr:
            raise AssertionError(result.stderr)


def main() -> int:
    test_aggregates_shards_before_thresholds()
    test_fails_aggregate_precision()
    test_single_note_gate_skips_chord_recall()
    test_fails_primary_chord_hits()
    print("test_check_guitarset_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
