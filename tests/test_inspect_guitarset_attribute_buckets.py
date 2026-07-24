#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_guitarset_attribute_buckets.py"

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
    "guitar_raw_chord",
    "guitar_smoothed_chord",
    "guitar_pitch_classes",
    "guitar_cells",
    "guitar_analysis_pitch_classes",
    "guitar_analysis_cells",
    "guitar_smoothed_pitch_classes",
    "guitar_smoothed_cells",
    "expected_raw_peak",
    "expected_raw_cells",
    "raw_pitch_class_levels",
    "guitar_probe_pitch_class_levels",
    "guitar_melodic_probe_pitch_class_levels",
    "expected_quality_raw_profile",
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
            "guitar_raw_chord": "C",
            "guitar_smoothed_chord": "C",
            "guitar_pitch_classes": "C,E,G",
            "guitar_cells": "C3:1.00,E3:0.80,G3:0.70",
            "guitar_analysis_pitch_classes": "C,E,G",
            "guitar_analysis_cells": "C3:1.00,E3:0.80,G3:0.70",
            "guitar_smoothed_pitch_classes": "C,E,G",
            "guitar_smoothed_cells": "C3:1.00,E3:0.80,G3:0.70",
            "expected_raw_peak": "12.0",
            "expected_raw_cells": "C3:1.000,E3:0.800,G3:0.700",
            "raw_pitch_class_levels": "C:1.000,E:0.800,G:0.700",
            "guitar_probe_pitch_class_levels": "C:1.000,E:0.800,G:0.700",
            "guitar_melodic_probe_pitch_class_levels": "C:1.000,E:0.800,G:0.700",
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
                guitar_cells="G3:0.70,D4:0.40",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_analysis_cells="G3:0.90,B3:0.35,D4:0.55",
                guitar_smoothed_pitch_classes="G,B,D",
                guitar_smoothed_cells="G3:0.82,B3:0.30,D4:0.50",
                expected_raw_peak="10.0",
                expected_raw_cells="G3:1.000,B3:0.380,D4:0.600",
                raw_pitch_class_levels="G:0.900,B:0.200,D:0.500",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "chord_miss:maj:visible2_analysis3_smooth3_rootvis1",
                "--recording-id",
                "rec2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        compact = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--misses-only",
                "--summary-only",
                "--examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        dumped = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--dump-rows",
                "--misses-only",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    output = completed.stdout
    assert "chord_miss:maj:visible2_analysis3_smooth3_rootvis1 rows=1 recordings=1" in output
    assert "visible_missing_tones" in output
    assert "third=1" in output
    assert "analysis_missing_tones" in output
    assert "--=1" in output
    assert "raw_third" in output
    assert "guitar_match_kind" in output
    assert "no_display_label=1" in output
    assert "raw_third_anchor_ratio" in output
    assert "recording rec2: status=chord_miss expected=G" in output
    assert "match=no_display_label" in output
    assert "evidence=analysis_full_tone_label_gap/analysis" in output
    assert "levels raw(root/third/fifth)=0.900/0.200/0.500" in output
    assert "opposite/anchor/margin=0.000/0.222/0.200" in output
    assert "chord_miss:maj:visible2_analysis3_smooth3_rootvis1 rows=1 recordings=1 examples=rec2" in compact.stdout
    assert "chord_hit:maj:all" not in compact.stdout
    assert "raw_third" not in compact.stdout
    assert "evidence_class" in dumped.stdout
    assert "\tanalysis_full_tone_label_gap\tanalysis\t" in dumped.stdout
    assert dumped.stdout.startswith("recording_id\tstatus\texpected_chords\t")
    assert "\nrec2\tchord_miss\tG\tmaj\tmaj\tG\tG\tmaj\tno_display_label\t0\t0\t0" in dumped.stdout
    assert "\nrec1\t" not in dumped.stdout
    print("test_inspect_guitarset_attribute_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
