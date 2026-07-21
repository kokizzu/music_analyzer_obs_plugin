#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]

HEADER = [
    "status",
    "detected",
    "detected_anywhere",
    "detected_expected_row",
    "first_row",
    "sample_id",
    "family",
    "nsynth_family",
    "source",
    "expected_note",
    "expected_midi",
    "buffer",
    "mode",
    "row_label",
    "row_conf",
    "row_grid",
    "any_grid",
    "buffer_strongest_row",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "global_chord",
    "keyboard_chord",
    "guitar_chord",
    "other_chord",
    "rms",
    "low",
    "mid",
    "high",
    "kick",
    "snare",
    "hihat",
    "crash",
    "tom",
    "ride",
    "rim",
    "debug_note",
    "debug_midi",
    "debug_owner",
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


def row(**overrides: str) -> list[str]:
    values = {name: "" for name in HEADER}
    values.update(
        {
            "detected": "1",
            "detected_anywhere": "1",
            "detected_expected_row": "1",
            "mode": "full_mix",
            "row_conf": "1",
            "row_grid": "1",
            "any_grid": "1",
            "buffer_strongest_row": "piano",
            "debug_note": "F#4",
            "debug_midi": "66",
            "debug_owner": "piano",
            "debug_conf": "1",
            "keyboard_score": "1",
            "guitar_score": "0",
            "vocal_score": "0",
            "other_score": "0",
            "spectral_level": "1",
            "pitch_confidence": "0.95",
            "periodicity": "0.78",
            "harmonicity": "0.3",
            "fit_error": "0.04",
            "centroid": "0.12",
            "slope": "0.08",
            "noise": "0.01",
            "partial1": "1",
            "partial2": "0.12",
            "partial3": "0.02",
            "partial4": "0.07",
            "partial5": "0.01",
        }
    )
    values.update(overrides)
    return [values[name] for name in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_1",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="F#4",
                expected_midi="66",
                partial2="0.12",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_2",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                partial2="0.14",
            ),
            row(
                status="hit",
                first_row="piano",
                sample_id="keyboard_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                partial2="0.62",
            ),
            row(
                status="hit",
                first_row="guitar",
                sample_id="keyboard_2",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                debug_owner="guitar",
                keyboard_score="0",
                guitar_score="1",
                partial2="0.13",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "12",
                "--max-negative-samples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        example_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
                "--condition",
                "debug_owner=piano",
                "--show-examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        multi_path = pathlib.Path(tmp) / "multi_attributes.tsv"
        multi_rows = [
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_1",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="F#4",
                expected_midi="66",
                partial2="0.12",
                pitch_confidence="0.95",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_2",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                partial2="0.13",
                pitch_confidence="0.96",
            ),
            row(
                status="hit",
                first_row="piano",
                sample_id="keyboard_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                partial2="0.12",
                pitch_confidence="0.40",
            ),
            row(
                status="hit",
                first_row="piano",
                sample_id="keyboard_2",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                partial2="0.62",
                pitch_confidence="0.96",
            ),
            row(
                status="hit",
                first_row="guitar",
                sample_id="keyboard_3",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C5",
                expected_midi="72",
                debug_note="C5",
                debug_midi="72",
                debug_owner="guitar",
                partial2="0.12",
                pitch_confidence="0.96",
            ),
        ]
        multi_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in multi_rows) + "\n"
        )
        multi_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(multi_path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "20",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "3",
                "--beam-width",
                "80",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "ownership_miss:guitar/acoustic->piano positives=2 samples/2 rows" in result.stdout
    assert "debug_owner=piano AND partial2<=0.14: pos=2/2 rows=2 neg=0/2 rows=0" in result.stdout
    assert "highest-coverage candidate rules" in result.stdout
    assert "explicit rule:" in example_result.stdout
    assert "debug_owner=piano: pos=2/2 rows=2 neg=1/2 rows=1" in example_result.stdout
    assert "positive examples:" in example_result.stdout
    assert "guitar_1 expected=F#4/66 debug=F#4/66 owner=piano" in example_result.stdout
    assert "protected-hit examples:" in example_result.stdout
    assert "keyboard_1 expected=F#4/66 debug=F#4/66 owner=piano" in example_result.stdout
    assert (
        "debug_midi<=69 AND partial2<=0.13 AND pitch_confidence>=0.95: "
        "pos=2/2 rows=2 neg=0/3 rows=0"
    ) in multi_result.stdout
    print("test_find_real_note_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
