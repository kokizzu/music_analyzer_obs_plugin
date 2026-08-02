#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_musicnet_shards.py"


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
    simple_chord_hits: int,
    pitch: tuple[int, int, int],
    simplified_chord: tuple[int, int, int],
    global_chord: tuple[int, int, int],
) -> str:
    return (
        "analyzer_musicnet: 15 checks passed "
        f"(recordings {recordings}/4, windows {windows}, read failures 0, "
        "no-candidate recordings 0, unusable 0, "
        f"note hits {note_hits}/{note_expected}, chord hits {chord_hits}/{chord_checks}, "
        "pitch precision 0.00%, pitch recall 0.00%, F1 0.00%, "
        f"tp/fp/fn {pitch[0]}/{pitch[1]}/{pitch[2]}, "
        f"simple chord hits {simple_chord_hits}/{chord_checks} 0.00%, "
        "simplified global chord precision 0.00%, global chord recall 0.00%, F1 0.00%, "
        f"tp/fp/fn {simplified_chord[0]}/{simplified_chord[1]}/{simplified_chord[2]}, "
        "global chord precision 0.00%, global chord recall 0.00%, F1 0.00%, "
        f"tp/fp/fn {global_chord[0]}/{global_chord[1]}/{global_chord[2]}, "
        "active notes min/avg/max 3/3.00/3, active instruments min/avg/max 3/3.00/3, "
        "pitch classes min/avg/max 3/3.00/3)\n"
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
        "70",
        "--min-chord-recall-percent",
        "0",
        "--min-simple-chord-recall-percent",
        "60",
        "--min-global-chord-precision-percent",
        "0",
        "--min-global-simple-chord-precision-percent",
        "60",
        "--min-global-simple-chord-recall-percent",
        "60",
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
                chord_hits=2,
                chord_checks=8,
                simple_chord_hits=5,
                pitch=(12, 2, 2),
                simplified_chord=(5, 2, 3),
                global_chord=(2, 4, 6),
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
                chord_hits=3,
                chord_checks=8,
                simple_chord_hits=6,
                pitch=(13, 2, 2),
                simplified_chord=(6, 2, 2),
                global_chord=(3, 4, 5),
            ),
        )

        result = run_checker(*base_args(shard_a, shard_b))
        assert result.returncode == 0, result.stderr
        assert "check_musicnet_shards: ok" in result.stdout
        assert "recordings 4/4" in result.stdout
        assert "note hits 25/32" in result.stdout
        assert "simple chord hits 11/16" in result.stdout

        recall_result = run_checker(
            *[
                arg if arg != "70" else "80"
                for arg in base_args(shard_a, shard_b)
            ]
        )
        assert recall_result.returncode == 1
        assert "expected pitch-class recall >= 80%" in recall_result.stderr

        simple_result = run_checker(
            *[
                arg if arg != "60" else "70"
                for arg in base_args(shard_a, shard_b)
            ]
        )
        assert simple_result.returncode == 1
        assert "expected simplified chord recall >= 70%" in simple_result.stderr

        malformed = write_log(root, "bad.out", "analyzer_musicnet: 1 checks passed (recordings 1/1)\n")
        malformed_result = run_checker(
            "--min-recordings",
            "1",
            "--min-windows",
            "1",
            "--min-recall-percent",
            "1",
            "--min-precision-percent",
            "1",
            "--min-chord-recall-percent",
            "0",
            "--min-simple-chord-recall-percent",
            "0",
            "--min-global-chord-precision-percent",
            "0",
            "--min-global-simple-chord-precision-percent",
            "0",
            "--min-global-simple-chord-recall-percent",
            "0",
            "--min-chord-checks",
            "1",
            str(malformed),
        )
        assert malformed_result.returncode == 1
        assert "missing analyzer_musicnet pass summary line" in malformed_result.stderr

    print("test_check_musicnet_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
