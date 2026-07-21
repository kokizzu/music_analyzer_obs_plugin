#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_guitarset_attributes.py"

HEADER = [
    "status",
    "recording_id",
    "audio_path",
    "center_seconds",
    "sample_rate",
    "instrument",
    "expected_midis",
    "expected_pitch_classes",
    "expected_pitch_class_count",
    "expected_chords",
    "expected_chord_qualities",
    "expected_chord_tone_count",
    "guitar_note_hits",
    "expected_note_count",
    "guitar_false_positive_pitch_classes",
    "cross_row_expected_hits",
    "chord_hit",
    "simple_chord_hit",
    "guitar_chord_hit",
    "global_chord",
    "keyboard_chord",
    "guitar_chord",
    "other_chord",
    "guitar_pitch_classes",
    "guitar_cells",
    "guitar_analysis_pitch_classes",
    "guitar_analysis_cells",
    "guitar_smoothed_pitch_classes",
    "guitar_smoothed_cells",
    "bass_pitch_classes",
    "keyboard_pitch_classes",
    "vocal_pitch_classes",
    "other_pitch_classes",
    "ambiguous_pitch_classes",
    "rms",
    "low",
    "mid",
    "high",
]


def row(**overrides: str) -> list[str]:
    values = {field: "" for field in HEADER}
    values.update(
        {
            "status": "chord_hit",
            "recording_id": "rec1",
            "audio_path": "rec1.wav",
            "center_seconds": "1.25",
            "sample_rate": "48000",
            "instrument": "guitar",
            "expected_midis": "C3,E3,G3",
            "expected_pitch_classes": "C,E,G",
            "expected_pitch_class_count": "3",
            "expected_chords": "C",
            "expected_chord_qualities": "maj",
            "expected_chord_tone_count": "3",
            "guitar_note_hits": "3",
            "expected_note_count": "3",
            "guitar_false_positive_pitch_classes": "0",
            "cross_row_expected_hits": "0",
            "chord_hit": "1",
            "simple_chord_hit": "1",
            "guitar_chord_hit": "1",
            "global_chord": "C",
            "keyboard_chord": "--",
            "guitar_chord": "C",
            "other_chord": "--",
            "guitar_pitch_classes": "C,E,G",
            "guitar_cells": "C3:1.00,E3:0.80,G3:0.70",
            "guitar_analysis_pitch_classes": "C,E,G",
            "guitar_analysis_cells": "C3:1.00,E3:0.80,G3:0.70",
            "guitar_smoothed_pitch_classes": "C,E,G",
            "guitar_smoothed_cells": "C3:1.00,E3:0.80,G3:0.70",
            "bass_pitch_classes": "--",
            "keyboard_pitch_classes": "--",
            "vocal_pitch_classes": "--",
            "other_pitch_classes": "--",
            "ambiguous_pitch_classes": "--",
            "rms": "0.25",
            "low": "0.4",
            "mid": "0.5",
            "high": "0.1",
        }
    )
    values.update(overrides)
    return [values[field] for field in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "guitarset.tsv"
        rows = [
            row(),
            row(
                status="chord_miss",
                recording_id="rec2",
                center_seconds="2.5",
                expected_chords="G",
                expected_chord_qualities="maj",
                guitar_note_hits="2",
                expected_note_count="3",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="G,D",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_smoothed_pitch_classes="G,B,D",
            ),
            row(
                status="no_chord",
                recording_id="rec3",
                expected_midis="A2",
                expected_pitch_classes="A",
                expected_pitch_class_count="1",
                expected_chords="--",
                expected_chord_qualities="--",
                expected_chord_tone_count="0",
                guitar_note_hits="0",
                expected_note_count="1",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="--",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    output = completed.stdout
    assert "summarize_guitarset_attributes: rows 3 recordings 3" in output
    assert "status chord_hit=1 chord_miss=1 no_chord=1" in output
    assert "guitar note recall 5/7 71.43%" in output
    assert "chord exact/global recall 1/2 50.00%" in output
    assert "visible chord-tone coverage 100%=1 50-74%=1" in output
    assert "analysis chord-tone coverage 100%=2" in output
    assert "visible missing chord tones major_third=1" in output
    assert "analysis missing chord tones --" in output
    assert "full-tone chord misses visible/analysis/smoothed 0/1/1" in output
    assert "chord miss examples" in output
    assert "rec2@2.500s expected=G" in output
    assert "weak guitar-note examples" in output
    assert "rec3@1.250s expected=--" in output
    print("test_summarize_guitarset_attributes: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
