#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_instrument_owner_patterns.py"

HEADER = [
    "kind",
    "status",
    "family",
    "expected_family",
    "program",
    "program_name",
    "note",
    "midi",
    "path",
    "window_ms",
    "detected_expected_row",
    "detected_anywhere",
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_label",
    "piano_label",
    "guitar_label",
    "vocal_label",
    "other_label",
    "global_chord",
    "keyboard_chord",
    "guitar_chord",
    "other_chord",
    "rms",
    "low",
    "mid",
    "high",
    "raw_expected_peak",
    "raw_expected_ratio",
    "raw_tuned_peak",
    "raw_tuned_ratio",
    "raw_tuned_cent_offset",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_note",
    "raw_local_best_midi",
    "raw_local_best_peak",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
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
    values = {field: "" for field in HEADER}
    values.update(
        {
            "kind": "note",
            "status": "hit",
            "expected_family": "piano",
            "program": "1",
            "program_name": "Program",
            "note": "C4",
            "midi": "60",
            "path": "sample.wav",
            "window_ms": "100",
            "detected_expected_row": "1",
            "detected_anywhere": "1",
            "expected_level": "1.0",
            "bass_level": "0.0",
            "piano_level": "0.8",
            "guitar_level": "0.1",
            "vocal_level": "0.0",
            "other_level": "0.1",
            "amb_level": "0.0",
            "rms": "0.2",
            "low": "0.2",
            "mid": "0.6",
            "high": "0.2",
            "raw_expected_peak": "10.0",
            "raw_expected_ratio": "1.0",
            "raw_tuned_peak": "10.0",
            "raw_tuned_ratio": "1.0",
            "raw_tuned_cent_offset": "0.0",
            "raw_tuned_abs_cent_offset": "0.0",
            "raw_local_best_note": "C4",
            "raw_local_best_midi": "60",
            "raw_local_best_peak": "10.0",
            "raw_expected_rank": "1",
            "raw_prev_ratio": "0.1",
            "raw_next_ratio": "0.1",
            "raw_octave_down_ratio": "0.2",
            "raw_octave_up_ratio": "0.2",
            "debug_note": "C4",
            "debug_midi": "60",
            "debug_owner": "piano",
            "debug_conf": "0.8",
            "keyboard_score": "0.8",
            "guitar_score": "0.1",
            "vocal_score": "0.0",
            "other_score": "0.1",
            "spectral_level": "0.8",
            "pitch_confidence": "0.9",
            "periodicity": "0.8",
            "harmonicity": "0.6",
            "fit_error": "0.1",
            "centroid": "0.2",
            "slope": "0.3",
            "noise": "0.05",
            "partial1": "1.0",
            "partial2": "0.5",
            "partial3": "0.3",
            "partial4": "0.2",
            "partial5": "0.1",
        }
    )
    values.update(overrides)
    return [values[field] for field in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "instrument.tsv"
        rows = [
            row(
                family="guitar",
                expected_family="guitar",
                program_name="Clean Guitar",
                note="E3",
                midi="52",
                path="guitar_1.wav",
                debug_note="E3",
                debug_midi="52",
                debug_owner="piano",
                partial2="0.12",
            ),
            row(
                family="guitar",
                expected_family="guitar",
                program_name="Clean Guitar",
                note="A3",
                midi="57",
                path="guitar_2.wav",
                debug_note="A3",
                debug_midi="57",
                debug_owner="piano",
                partial2="0.14",
            ),
            row(
                family="piano",
                expected_family="piano",
                program_name="Grand Piano",
                note="C4",
                midi="60",
                path="piano_1.wav",
                debug_note="C4",
                debug_midi="60",
                debug_owner="piano",
                partial2="0.62",
            ),
            row(
                family="piano",
                expected_family="piano",
                program_name="Clean Guitar",
                note="E3",
                midi="52",
                path="piano_2.wav",
                debug_note="E3",
                debug_midi="52",
                debug_owner="piano",
                partial2="0.62",
            ),
            row(
                family="vocals",
                expected_family="vocals",
                program_name="Voice",
                note="E4",
                midi="64",
                path="vocal_1.wav",
                debug_note="E4",
                debug_midi="64",
                debug_owner="vocals",
                partial2="0.12",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_miss:guitar->piano",
                "--limit",
                "10",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "3",
                "--beam-width",
                "80",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        example = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_miss:guitar->piano",
                "--condition",
                "debug_owner=piano",
                "--show-examples",
                "1",
                "--max-negative-samples",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    assert (
        "owner_miss:guitar->piano positives=2 samples/2 rows protected_hits=3 samples/3 rows"
        in result.stdout
    ), result.stdout + result.stderr
    assert "AND partial2<=0.14: pos=2/2 rows=2 neg=0/3 rows=0" in result.stdout, result.stdout + result.stderr
    assert "highest-coverage candidate rules" in result.stdout, result.stdout + result.stderr
    assert "explicit rule:" in example.stdout, example.stdout + example.stderr
    assert "debug_owner=piano: pos=2/2 rows=2 neg=2/3 rows=2" in example.stdout, (
        example.stdout + example.stderr
    )
    assert "positive examples:" in example.stdout, example.stdout + example.stderr
    assert "guitar Clean Guitar E3 path=guitar_1.wav target=guitar owner=piano" in example.stdout, (
        example.stdout + example.stderr
    )
    assert "protected-hit examples:" in example.stdout, example.stdout + example.stderr
    assert "piano Grand Piano C4 path=piano_1.wav target=piano owner=piano" in example.stdout, (
        example.stdout + example.stderr
    )
    print("test_find_instrument_owner_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
