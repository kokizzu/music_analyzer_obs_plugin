#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_maestro_shards.py"


def write_log(directory: pathlib.Path, name: str, body: str) -> pathlib.Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def summary(
    *,
    recordings: int,
    windows: int,
    note_hits: int,
    note_expected: int,
    chord_hits: int,
    chord_checks: int,
    keyboard_tp: int,
    keyboard_fp: int,
    keyboard_fn: int,
    contaminated: int,
    false_non_keyboard: int,
    chord_tp: int,
    chord_fp: int,
    chord_fn: int,
) -> str:
    return (
        "analyzer_maestro: 12 checks passed "
        f"(recordings {recordings}/4, windows {windows}, read failures 0, "
        "no-candidate recordings 0, unusable 0, "
        f"note hits {note_hits}/{note_expected}, chord hits {chord_hits}/{chord_checks}, "
        "keyboard precision 0.00%, keyboard recall 0.00%, F1 0.00%, "
        f"contamination 0.00% ({contaminated}/{note_expected}), "
        f"false non-keyboard windows 0.00% ({false_non_keyboard}/{windows}), "
        f"ambiguous 0/{note_expected}, row leaks bass/guitar/vocal/other 0/0/0/0, "
        f"tp/fp/fn {keyboard_tp}/{keyboard_fp}/{keyboard_fn}, "
        "keyboard chord precision 0.00%, keyboard chord recall 0.00%, F1 0.00%, "
        f"tp/fp/fn {chord_tp}/{chord_fp}/{chord_fn}, "
        "composition bass/guitar/keyboard/vocal/other/mixed 0/0/0/0/0/0)\n"
    )


def base_args(*logs: pathlib.Path) -> list[str]:
    return [
        "--min-recordings",
        "4",
        "--min-windows",
        "16",
        "--min-recall-percent",
        "70",
        "--min-precision-percent",
        "80",
        "--min-keyboard-recall-percent",
        "80",
        "--max-contamination-percent",
        "5",
        "--max-false-non-keyboard-percent",
        "5",
        "--min-chord-recall-percent",
        "60",
        "--min-chord-precision-percent",
        "80",
        "--min-chord-checks",
        "8",
        *(str(path) for path in logs),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        shard_a = write_log(
            root,
            "a.out",
            summary(
                recordings=2,
                windows=8,
                note_hits=12,
                note_expected=16,
                chord_hits=6,
                chord_checks=8,
                keyboard_tp=12,
                keyboard_fp=2,
                keyboard_fn=2,
                contaminated=0,
                false_non_keyboard=0,
                chord_tp=6,
                chord_fp=1,
                chord_fn=2,
            ),
        )
        shard_b = write_log(
            root,
            "b.out",
            summary(
                recordings=2,
                windows=8,
                note_hits=13,
                note_expected=16,
                chord_hits=6,
                chord_checks=8,
                keyboard_tp=13,
                keyboard_fp=2,
                keyboard_fn=2,
                contaminated=1,
                false_non_keyboard=0,
                chord_tp=6,
                chord_fp=1,
                chord_fn=2,
            ),
        )

        result = run_checker(*base_args(shard_a, shard_b))
        assert result.returncode == 0, result.stderr
        assert "check_maestro_shards: ok" in result.stdout
        assert "recordings 4/4" in result.stdout
        assert "note hits 25/32" in result.stdout
        assert "chord hits 12/16" in result.stdout

        fail_result = run_checker(
            *[
                arg if arg != "70" else "80"
                for arg in base_args(shard_a, shard_b)
            ]
        )
        assert fail_result.returncode == 1
        assert "expected piano pitch-class recall >= 80%" in fail_result.stderr

        chord_fail = write_log(
            root,
            "chord-fail.out",
            summary(
                recordings=4,
                windows=16,
                note_hits=30,
                note_expected=32,
                chord_hits=4,
                chord_checks=16,
                keyboard_tp=30,
                keyboard_fp=2,
                keyboard_fn=2,
                contaminated=0,
                false_non_keyboard=0,
                chord_tp=4,
                chord_fp=8,
                chord_fn=12,
            ),
        )
        chord_result = run_checker(*base_args(chord_fail))
        assert chord_result.returncode == 1
        assert "expected piano chord recall >= 60%" in chord_result.stderr

        malformed = write_log(root, "bad.out", "analyzer_maestro: 1 checks passed (recordings 1/1)\n")
        malformed_result = run_checker(
            "--min-recordings",
            "1",
            "--min-windows",
            "1",
            "--min-recall-percent",
            "1",
            "--min-precision-percent",
            "1",
            "--min-keyboard-recall-percent",
            "1",
            "--max-contamination-percent",
            "100",
            "--max-false-non-keyboard-percent",
            "100",
            "--min-chord-recall-percent",
            "1",
            "--min-chord-precision-percent",
            "1",
            "--min-chord-checks",
            "1",
            str(malformed),
        )
        assert malformed_result.returncode == 1
        assert "missing analyzer_maestro pass summary line" in malformed_result.stderr

    print("test_check_maestro_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
