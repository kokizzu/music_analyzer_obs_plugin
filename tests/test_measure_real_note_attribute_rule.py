#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run_rule(path: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "measure_real_note_attribute_rule.py"),
            str(path),
            *args,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        compare_path = pathlib.Path(tmp) / "compare_attributes.tsv"
        rows = [
            [
                "sample_id",
                "status",
                "family",
                "source",
                "first_row",
                "buffer_strongest_row",
                "debug_owner",
                "debug_midi",
                "bass_score",
                "keyboard_score",
                "guitar_score",
                "vocal_score",
                "other_score",
                "partial2",
                "partial3",
                "noise",
            ],
            [
                "keyboard_1",
                "hit",
                "piano",
                "electronic",
                "guitar",
                "guitar",
                "guitar",
                "64",
                "0",
                "0.10",
                "0.78",
                "0",
                "0",
                "0.58",
                "0.32",
                "0.01",
            ],
            [
                "keyboard_2",
                "hit",
                "piano",
                "electronic",
                "piano",
                "piano",
                "amb",
                "64",
                "0",
                "0.70",
                "0",
                "0",
                "0",
                "0.10",
                "0.02",
                "0.01",
            ],
            [
                "guitar_1",
                "hit",
                "guitar",
                "electronic",
                "guitar",
                "guitar",
                "guitar",
                "60",
                "0",
                "0",
                "0.80",
                "0",
                "0",
                "0.39",
                "0.05",
                "0.03",
            ],
            [
                "guitar_2",
                "hit",
                "guitar",
                "acoustic",
                "guitar",
                "guitar",
                "guitar",
                "63",
                "0",
                "0",
                "0.80",
                "0",
                "0",
                "0.27",
                "0.01",
                "0.02",
            ],
        ]
        path.write_text("\n".join("\t".join(row) for row in rows) + "\n")
        compare_rows = [
            rows[0],
            [
                "bass_1",
                "hit",
                "bass",
                "electronic",
                "guitar",
                "guitar",
                "guitar",
                "52",
                "0.10",
                "0.20",
                "0.70",
                "0",
                "0",
                "0.45",
                "0.20",
                "0.02",
            ],
            [
                "bass_2",
                "hit",
                "bass",
                "electronic",
                "bass",
                "bass",
                "piano",
                "52",
                "0.70",
                "0.20",
                "0.10",
                "0",
                "0",
                "0.12",
                "0.02",
                "0.01",
            ],
        ]
        compare_path.write_text("\n".join("\t".join(row) for row in compare_rows) + "\n")

        result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--condition",
            "debug_midi:52:64",
            "--condition",
            "partial3>=0.18",
            "--condition",
            "noise<=0.02",
        )
        derived_result = run_rule(
            path,
            "--condition",
            "debug_score_state=scored_amb",
            "--condition",
            "buffer_strongest_row=piano",
            "--condition",
            "partial3<=0.03",
        )
        grouped_result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--group-by",
            "buffer_strongest_row",
            "--group-by",
            "debug_score_state",
        )
        bucketed_result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--numeric-bucket",
            "partial2:0.20",
            "--numeric-bucket",
            "noise:0.02",
            "--group-by",
            "partial2_bucket",
            "--group-by",
            "noise_bucket",
        )
        derived_midi_group_result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--group-by",
            "debug_pitch_class",
            "--group-by",
            "debug_octave",
        )
        compare_result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--primary-condition",
            "family=guitar",
            "--compare-path",
            str(compare_path),
            "--compare-condition",
            "family=bass",
            "--compare-group-by",
            "family",
            "--compare-group-by",
            "first_row",
        )
        default_compare_result = run_rule(
            path,
            "--condition",
            "debug_owner=guitar",
            "--primary-condition",
            "family=piano",
            "--compare-condition",
            "family=guitar",
            "--compare-group-by",
            "family",
        )

    assert "matched rows=1 samples=1" in result.stdout
    assert "examples keyboard_1" in result.stdout
    assert "groups family/source/first_row" in result.stdout
    assert "piano/electronic/guitar rows=1 samples=1" in result.stdout
    assert "guitar/electronic/guitar" not in result.stdout
    assert "matched rows=1 samples=1" in derived_result.stdout
    assert "examples keyboard_2" in derived_result.stdout
    assert "groups buffer_strongest_row/debug_score_state" in grouped_result.stdout
    assert "guitar/scored_owner rows=3 samples=3" in grouped_result.stdout
    assert "family/source/first_row" not in grouped_result.stdout
    assert "groups partial2_bucket/noise_bucket" in bucketed_result.stdout
    assert "0.40-0.60/0.00-0.02 rows=1 samples=1" in bucketed_result.stdout
    assert "0.20-0.40/0.02-0.04 rows=2 samples=2" in bucketed_result.stdout
    assert "groups debug_pitch_class/debug_octave" in derived_midi_group_result.stdout
    assert "E/4 rows=1 samples=1" in derived_midi_group_result.stdout
    assert "C/4 rows=1 samples=1" in derived_midi_group_result.stdout
    assert "D#/4 rows=1 samples=1" in derived_midi_group_result.stdout
    assert "matched rows=2 samples=2" in compare_result.stdout
    assert "matched conditions debug_owner=guitar family=guitar" in compare_result.stdout
    assert f"compare rows=1 samples=1 path={compare_path}" in compare_result.stdout
    assert "compare conditions debug_owner=guitar family=bass" in compare_result.stdout
    assert "compare groups family/first_row" in compare_result.stdout
    assert "bass/guitar rows=1 samples=1" in compare_result.stdout
    assert "matched conditions debug_owner=guitar family=piano" in default_compare_result.stdout
    assert f"compare rows=2 samples=2 path={path}" in default_compare_result.stdout
    assert "compare conditions debug_owner=guitar family=guitar" in default_compare_result.stdout
    assert "compare groups family" in default_compare_result.stdout
    assert "guitar rows=2 samples=2" in default_compare_result.stdout
    print("test_measure_real_note_attribute_rule: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
