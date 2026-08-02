#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_real_note_candidate_rows.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    header = [
        "sample_id",
        "status",
        "family",
        "source",
        "expected_note",
        "expected_midi",
        "first_row",
        "visual_first_row",
        "debug_note",
        "debug_midi",
        "debug_owner",
        "bass_score",
        "keyboard_score",
        "guitar_score",
        "vocal_score",
        "other_score",
        "partial4",
        "noise",
    ]
    rows = [
        [
            "keyboard_1",
            "hit",
            "piano",
            "electronic",
            "E4",
            "64",
            "guitar",
            "guitar",
            "E4",
            "64",
            "guitar",
            "0.00",
            "0.20",
            "0.70",
            "0.00",
            "0.00",
            "0.010",
            "0.020",
        ],
        [
            "keyboard_2",
            "hit",
            "piano",
            "electronic",
            "C4",
            "60",
            "piano",
            "piano",
            "C4",
            "60",
            "piano",
            "0.00",
            "0.75",
            "0.10",
            "0.00",
            "0.00",
            "0.030",
            "0.010",
        ],
        [
            "guitar_1",
            "miss",
            "guitar",
            "acoustic",
            "G3",
            "55",
            "guitar",
            "guitar",
            "G3",
            "55",
            "guitar",
            "0.00",
            "0.00",
            "0.80",
            "0.00",
            "0.00",
            "0.020",
            "0.040",
        ],
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "real_note_rows.tsv"
        path.write_text(
            "\n".join(["\t".join(header)] + ["\t".join(row) for row in rows]) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--condition",
                "status=hit",
                "--condition",
                "family=piano",
                "--condition",
                "debug_pitch_class=E",
                "--condition",
                "guitar_score/keyboard_score>3.0",
                "--condition",
                "partial4<=0.02",
                "--field",
                "guitar_score",
                "--field",
                "keyboard_score",
                "--field",
                "guitar_score/keyboard_score",
                "--group-by",
                "family",
                "--group-by",
                "source",
                "--group-by",
                "first_row",
                "--example-field",
                "sample_id",
                "--example-field",
                "expected_note",
                "--example-field",
                "owner_status",
                str(path),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    output = completed.stdout
    require(output, "rows=3 selected=1 samples=1")
    require(output, "groups family/source/first_row")
    require(output, "piano/electronic/guitar rows=1 samples=1")
    require(output, "guitar_score: min=0.700 med=0.700 max=0.700")
    require(output, "keyboard_score: min=0.200 med=0.200 max=0.200")
    require(output, "guitar_score/keyboard_score: min=3.500 med=3.500 max=3.500")
    require(output, "example sample_id=keyboard_1 expected_note=E4 owner_status=owner_miss")
    print("test_inspect_real_note_candidate_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
