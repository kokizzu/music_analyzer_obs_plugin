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
                raw_pitch_class_levels="G:1.000,B:0.380,D:0.600",
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
                raw_pitch_class_levels="D:1.000,F#:0.350,A:0.650",
            ),
            row(
                status="single_note_false_chord",
                recording_id="rec4",
                expected_midis="F4",
                expected_pitch_classes="F",
                expected_pitch_class_count="1",
                expected_chords="--",
                expected_chord_qualities="--",
                expected_chord_tone_count="0",
                guitar_note_hits="1",
                expected_note_count="1",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
                global_chord="--",
                guitar_chord="Fm=Fpow=F",
                guitar_raw_chord="Fm",
                guitar_smoothed_chord="F=Fpow=Fm",
                guitar_pitch_classes="C,F",
                guitar_cells="C6:0.99,F4:1.00",
                guitar_analysis_pitch_classes="C,F,G#",
                guitar_analysis_cells="C6:0.41,F4:1.00,G#4:0.01",
                guitar_smoothed_pitch_classes="C,F",
                guitar_smoothed_cells="C6:0.41,F4:1.00",
                expected_raw_peak="11.0",
                expected_raw_cells="F4:1.000",
                raw_pitch_class_levels="C:0.522,F:1.000,G#:0.010",
                guitar_probe_pitch_class_levels="C:0.993,F:1.000,G#:0.008",
                guitar_melodic_probe_pitch_class_levels="C:0.900,F:1.000,G#:0.007",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n",
            encoding="utf-8",
        )
        protected_path = pathlib.Path(tmpdir) / "protected.tsv"
        protected_rows = [
            row(
                status="chord_hit",
                recording_id="protected_hit",
                expected_chords="F",
                expected_chord_qualities="maj",
                guitar_chord="F",
                guitar_raw_chord="F",
                guitar_smoothed_chord="F",
                guitar_pitch_classes="C,F,A",
                guitar_cells="C4:0.70,F3:1.00,A3:0.80",
                guitar_analysis_pitch_classes="C,F,A",
                guitar_analysis_cells="C4:0.70,F3:1.00,A3:0.80",
                guitar_smoothed_pitch_classes="C,F,A",
                guitar_smoothed_cells="C4:0.70,F3:1.00,A3:0.80",
                raw_pitch_class_levels="C:0.700,F:1.000,A:0.800",
            )
        ]
        protected_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in protected_rows) + "\n",
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
                "--row-examples",
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
        single_note_false = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "single_note_false_chord:any:any",
                "--min-positive-recordings",
                "1",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        protected_single_note_false = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "single_note_false_chord:any:any",
                "--protected-path",
                str(protected_path),
                "--protected-bucket",
                "chord_hit:any:any",
                "--min-positive-recordings",
                "1",
                "--max-negative-recordings",
                "0",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        runtime_single_note_false = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "single_note_false_chord:any:any",
                "--protected-path",
                str(protected_path),
                "--protected-bucket",
                "chord_hit:any:any",
                "--runtime-only",
                "--min-positive-recordings",
                "1",
                "--max-negative-recordings",
                "0",
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
                raw_pitch_class_levels="G:1.000,B:1.000,D:1.000",
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
                raw_pitch_class_levels="G:1.000,B:1.000,D:1.000",
            ),
            row(
                recording_id="hit_low_root",
                expected_chords="G",
                expected_chord_qualities="maj",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
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
                raw_pitch_class_levels="G:0.200,B:1.000,D:1.000",
            ),
            row(
                recording_id="hit_low_third",
                expected_chords="G",
                expected_chord_qualities="maj",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
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
                raw_pitch_class_levels="G:1.000,B:0.200,D:1.000",
            ),
            row(
                recording_id="hit_low_fifth",
                expected_chords="G",
                expected_chord_qualities="maj",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
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
                raw_pitch_class_levels="G:1.000,B:1.000,D:0.200",
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
    assert "chord_hit<=" not in output
    assert "bucket chord_miss:maj:visible2_analysis3_smooth3_rootvis1 positives=2" in auto_completed.stdout
    assert "rec2@2.500s expected=G guitar=--" in auto_completed.stdout
    assert "bucket single_note_false_chord:any:any positives=1" in single_note_false.stdout
    assert "rec4@" in single_note_false.stdout
    assert "expected=-- guitar=Fm=Fpow=F" in single_note_false.stdout
    assert "bucket single_note_false_chord:any:any positives=1" in protected_single_note_false.stdout
    assert "protected_hits=1" in protected_single_note_false.stdout
    assert "rec4@" in protected_single_note_false.stdout
    assert "-0 rows=0" in protected_single_note_false.stdout
    assert "bucket single_note_false_chord:any:any positives=1" in runtime_single_note_false.stdout
    assert "guitar_pc_count<=2" in runtime_single_note_false.stdout
    assert "expected_chord_qualities" not in runtime_single_note_false.stdout
    assert "raw_fifth>=1 AND raw_root>=1 AND raw_third>=1" in multi_condition.stdout
    assert "miss1@1.000s expected=G guitar=--" in multi_condition.stdout
    print("test_find_guitarset_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
