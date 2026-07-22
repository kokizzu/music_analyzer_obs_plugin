#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

from test_inspect_guitarset_attribute_buckets import HEADER, ROOT, row


SCRIPT = ROOT / "scripts" / "find_guitarset_attribute_patterns.py"


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
            ),
            row(
                status="chord_miss",
                recording_id="rec3",
                center_seconds="3.0",
                expected_chords="D",
                expected_chord_qualities="maj",
                guitar_note_hits="2",
                expected_note_count="3",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="D,A",
                guitar_cells="D3:0.75,A3:0.50",
                guitar_analysis_pitch_classes="D,F#,A",
                guitar_analysis_cells="D3:0.95,F#3:0.32,A3:0.60",
                guitar_smoothed_pitch_classes="D,F#,A",
                guitar_smoothed_cells="D3:0.90,F#3:0.30,A3:0.57",
                expected_raw_peak="9.0",
                expected_raw_cells="D3:1.000,F#3:0.350,A3:0.650",
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
                "--min-positive-recordings",
                "2",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        auto_completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--top-buckets",
                "1",
                "--min-positive-recordings",
                "2",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        multi_condition_rows = [
            row(
                status="chord_miss",
                recording_id="miss1",
                center_seconds="1.0",
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
                expected_raw_cells="G3:1.000,B3:1.000,D4:1.000",
            ),
            row(
                status="chord_miss",
                recording_id="miss2",
                center_seconds="1.5",
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
                expected_raw_cells="G3:1.000,B3:1.000,D4:1.000",
            ),
            row(
                recording_id="hit_low_root",
                expected_chords="G",
                expected_chord_qualities="maj",
                guitar_note_hits="2",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="G,D",
                guitar_cells="G3:0.70,D4:0.40",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_analysis_cells="G3:0.90,B3:0.35,D4:0.55",
                guitar_smoothed_pitch_classes="G,B,D",
                guitar_smoothed_cells="G3:0.82,B3:0.30,D4:0.50",
                expected_raw_peak="10.0",
                expected_raw_cells="G3:0.200,B3:1.000,D4:1.000",
            ),
            row(
                recording_id="hit_low_third",
                expected_chords="G",
                expected_chord_qualities="maj",
                guitar_note_hits="2",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="G,D",
                guitar_cells="G3:0.70,D4:0.40",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_analysis_cells="G3:0.90,B3:0.35,D4:0.55",
                guitar_smoothed_pitch_classes="G,B,D",
                guitar_smoothed_cells="G3:0.82,B3:0.30,D4:0.50",
                expected_raw_peak="10.0",
                expected_raw_cells="G3:1.000,B3:0.200,D4:1.000",
            ),
            row(
                recording_id="hit_low_fifth",
                expected_chords="G",
                expected_chord_qualities="maj",
                guitar_note_hits="2",
                global_chord="--",
                guitar_chord="--",
                guitar_pitch_classes="G,D",
                guitar_cells="G3:0.70,D4:0.40",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_analysis_cells="G3:0.90,B3:0.35,D4:0.55",
                guitar_smoothed_pitch_classes="G,B,D",
                guitar_smoothed_cells="G3:0.82,B3:0.30,D4:0.50",
                expected_raw_peak="10.0",
                expected_raw_cells="G3:1.000,B3:1.000,D4:0.200",
            ),
        ]
        multi_path = pathlib.Path(tmpdir) / "multi.tsv"
        multi_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in multi_condition_rows) + "\n",
            encoding="utf-8",
        )
        multi_condition = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(multi_path),
                "--bucket",
                "chord_miss:maj:visible2_analysis3_smooth3_rootvis1",
                "--min-positive-recordings",
                "2",
                "--max-negative-recordings",
                "0",
                "--max-conditions",
                "3",
                "--limit",
                "20",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    output = completed.stdout
    assert "bucket chord_miss:maj:visible2_analysis3_smooth3_rootvis1 positives=2" in output
    assert "+2 rows=2 -0 rows=0" in output
    assert "support=visible2_analysis3_smooth3_rootvis1" in output
    assert "rec2@2.500s expected=G guitar=--" in output
    assert "bucket chord_miss:maj:visible2_analysis3_smooth3_rootvis1 positives=2" in auto_completed.stdout
    assert "rec2@2.500s expected=G guitar=--" in auto_completed.stdout
    assert "raw_fifth>=1 AND raw_root>=1 AND raw_third>=1" in multi_condition.stdout
    assert "miss1@1.000s expected=G guitar=--" in multi_condition.stdout
    print("test_find_guitarset_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
