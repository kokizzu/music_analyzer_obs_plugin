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
    "visual_first_row",
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
    "buffer_visual_strongest_row",
    "bass_score",
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
    "bass_notes",
    "guitar_notes",
    "piano_notes",
    "vocal_notes",
    "other_notes",
    "bass_visual_notes",
    "guitar_visual_notes",
    "piano_visual_notes",
    "vocal_visual_notes",
    "other_visual_notes",
    "debug_note",
    "debug_midi",
    "debug_owner",
    "debug_conf",
]


def row(**overrides: str) -> list[str]:
    values = {name: "" for name in HEADER}
    values.update(
        {
            "status": "hit",
            "detected": "1",
            "detected_anywhere": "1",
            "detected_expected_row": "1",
            "first_row": "vocals",
            "visual_first_row": "piano",
            "family": "vocals",
            "source": "acoustic",
            "expected_note": "C4",
            "expected_midi": "60",
            "buffer": "0",
            "mode": "full_mix",
            "row_label": "C4",
            "row_conf": "1",
            "row_grid": "1",
            "any_grid": "1",
            "buffer_strongest_row": "piano",
            "buffer_visual_strongest_row": "piano",
            "bass_score": "0.00",
            "keyboard_score": "0.15",
            "guitar_score": "0.00",
            "vocal_score": "0.05",
            "other_score": "0.80",
            "spectral_level": "0.92",
            "pitch_confidence": "0.88",
            "periodicity": "0.78",
            "harmonicity": "0.65",
            "fit_error": "0.12",
            "centroid": "0.42",
            "slope": "0.50",
            "noise": "0.18",
            "partial1": "1.00",
            "partial2": "0.55",
            "partial3": "0.80",
            "partial4": "0.20",
            "partial5": "0.10",
            "bass_notes": "",
            "guitar_notes": "",
            "piano_notes": "C4:0.90",
            "vocal_notes": "",
            "other_notes": "C4:0.80",
            "debug_note": "C4",
            "debug_midi": "60",
            "debug_owner": "other",
            "debug_conf": "0.82",
        }
    )
    values.update(overrides)
    for visual_field, note_field in (
        ("bass_visual_notes", "bass_notes"),
        ("guitar_visual_notes", "guitar_notes"),
        ("piano_visual_notes", "piano_notes"),
        ("vocal_visual_notes", "vocal_notes"),
        ("other_visual_notes", "other_notes"),
    ):
        if visual_field not in overrides:
            values[visual_field] = values[note_field]
    return [values[name] for name in HEADER]


def write_tsv(path: pathlib.Path, rows: list[list[str]]) -> None:
    path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        primary = tmp_path / "primary.tsv"
        compare = tmp_path / "compare.tsv"
        write_tsv(
            primary,
            [
                row(sample_id="missing_vocal"),
                row(
                    sample_id="already_visible_vocal",
                    expected_note="D4",
                    expected_midi="62",
                    debug_note="D4",
                    debug_midi="62",
                    vocal_notes="D4:0.55",
                ),
                row(
                    sample_id="wrong_debug_pitch",
                    expected_note="E4",
                    expected_midi="64",
                    debug_note="F4",
                    debug_midi="65",
                ),
            ],
        )
        write_tsv(
            compare,
            [
                row(
                    sample_id="new_false_vocal",
                    family="piano",
                    source="electronic",
                    first_row="piano",
                    expected_note="C4",
                    expected_midi="60",
                    debug_note="C4",
                    debug_midi="60",
                ),
                row(
                    sample_id="already_false_vocal",
                    family="guitar",
                    first_row="guitar",
                    expected_note="E3",
                    expected_midi="52",
                    debug_note="E3",
                    debug_midi="52",
                    vocal_notes="E3:0.40",
                ),
                row(
                    sample_id="condition_rejected",
                    family="other",
                    first_row="other",
                    expected_note="G3",
                    expected_midi="55",
                    debug_note="G3",
                    debug_midi="55",
                    fit_error="0.45",
                ),
            ],
        )

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_vocal_display_fallback.py"),
                str(primary),
                "--compare-path",
                str(compare),
                "--condition",
                "fit_error<0.20",
                "--group-by",
                "debug_owner",
                "--group-by",
                "expected_octave",
                "--examples",
                "3",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        output = result.stdout
        assert "positive_missing_vocal rows=1 samples=1" in output
        assert "already_visible_vocal rows=1 samples=1" in output
        assert "side_effect_non_vocal rows=1 samples=1" in output
        assert "already_false_vocal rows=1 samples=1" in output
        assert "utility net_rows=0 net_samples=0" in output
        assert "missing_vocal" in output
        assert "new_false_vocal" in output

        summary = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_vocal_display_fallback.py"),
                str(primary),
                "--compare-path",
                str(compare),
                "--condition",
                "fit_error<0.20",
                "--summary-only",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        assert "positive examples" not in summary
        assert "positive groups" in summary

    print("test_evaluate_real_note_vocal_display_fallback: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
