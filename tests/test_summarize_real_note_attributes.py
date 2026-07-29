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
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
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
    "amb_notes",
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
            "raw_expected_peak": "8.0",
            "raw_expected_ratio": "1.0",
            "raw_tuned_peak": "8.5",
            "raw_tuned_ratio": "1.0",
            "raw_tuned_cent_offset": "0",
            "raw_tuned_abs_cent_offset": "0",
            "raw_local_best_note": "C4",
            "raw_local_best_midi": "60",
            "raw_local_best_peak": "8.0",
            "raw_expected_rank": "1",
            "raw_prev_ratio": "0.1",
            "raw_next_ratio": "0.1",
            "raw_octave_down_ratio": "0.2",
            "raw_octave_up_ratio": "0.3",
            "raw_fifth_up_ratio": "0.4",
            "raw_second_octave_up_ratio": "0.2",
            "raw_upper_major_third_ratio": "0.1",
            "raw_upper_fifth_ratio": "0.05",
            "raw_third_octave_up_ratio": "0.02",
            "rms": "0.1",
            "low": "0.2",
            "mid": "0.3",
            "high": "0.4",
        }
    )
    values.update(overrides)
    return [values[name] for name in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(
                status="hit",
                first_row="piano",
                visual_first_row="piano",
                sample_id="keyboard_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C4",
                expected_midi="60",
                buffer="0",
                buffer_strongest_row="guitar",
                buffer_visual_strongest_row="bass",
                debug_note="C4",
                debug_midi="60",
                debug_owner="piano",
                debug_conf="0.80",
                bass_level="0.40",
                guitar_level="0.60",
                piano_level="1.00",
                bass_score="0.01",
                keyboard_score="0.70",
                guitar_score="0.10",
                vocal_score="0.02",
                other_score="0.05",
                pitch_confidence="0.90",
                periodicity="0.85",
                fit_error="0.05",
                noise="0.12",
                partial1="1.0",
                partial2="0.4",
                partial3="0.2",
                partial4="0.1",
                bass_notes="C3:0.40",
                guitar_notes="C4:0.60",
                piano_notes="C4:1.00",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="guitar",
                visual_first_row="guitar",
                sample_id="keyboard_2",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="E2",
                expected_midi="40",
                buffer="0",
                buffer_strongest_row="guitar",
                buffer_visual_strongest_row="other",
                row_grid="0",
                debug_note="E2",
                debug_midi="40",
                debug_owner="guitar",
                debug_conf="0.56",
                guitar_level="0.80",
                piano_level="0.00",
                other_level="0.50",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.56",
                vocal_score="0.00",
                other_score="0.43",
                pitch_confidence="0.70",
                periodicity="0.71",
                fit_error="0.07",
                noise="0.54",
                raw_expected_ratio="0.41",
                raw_tuned_ratio="0.48",
                raw_tuned_cent_offset="18",
                raw_tuned_abs_cent_offset="18",
                raw_local_best_note="F2",
                raw_local_best_midi="41",
                raw_expected_rank="2",
                raw_prev_ratio="0.21",
                raw_next_ratio="1.0",
                raw_octave_down_ratio="0.0",
                raw_octave_up_ratio="0.32",
                partial1="1.0",
                partial2="0.54",
                partial3="0.13",
                partial4="0.17",
                guitar_notes="E2:0.80",
                piano_notes="--",
                other_notes="E3:0.50",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "summarize_real_note_attributes.py"), str(path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        detailed_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "summarize_real_note_attributes.py"),
                str(path),
                "--detail-limit",
                "4",
                "--sample-limit",
                "4",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "samples 2" in result.stdout
    assert "hit=1" in result.stdout
    assert "ownership_miss=1" in result.stdout
    assert "ownership_miss:piano/electronic->guitar=1" in result.stdout
    assert "debug medians ownership_miss:piano/electronic->guitar" in result.stdout
    assert "context medians ownership_miss:piano/electronic->guitar" in result.stdout
    assert "raw_expected_ratio=0.410" in result.stdout
    assert "raw_tuned_abs_cent_offset=18.000" in result.stdout
    assert "extra note-row summary buffers=2 samples=2" in result.stdout
    assert "extra_pitch_buffers=2 extra_pitch_rows=4" in result.stdout
    assert "extra_exact_buffers=2 extra_exact_rows=2" in result.stdout
    assert "top extra pitch source/row piano/electronic->guitar=2" in result.stdout
    assert "piano/electronic->bass=1" in result.stdout
    assert "top extra exact source/row piano/electronic->guitar=2" in result.stdout
    assert "extra note-cell intervals cells=4 same_pitch_class=4 exact=2" in result.stdout
    assert "top extra note-cell delta piano/electronic->guitar:+0=2" in result.stdout
    assert "piano/electronic->bass:-12=1" in result.stdout
    assert "piano/electronic->other:+12=1" in result.stdout
    assert "top extra same-pitch/octave delta piano/electronic->guitar:+0=2" in result.stdout
    assert "strongest-row confusion note buckets rows=2 samples=2" in result.stdout
    assert "piano/electronic C4->guitar=1" in result.stdout
    assert "piano/electronic E2->guitar=1" in result.stdout
    assert "strongest-row confusion routes piano/electronic->guitar=2" in result.stdout
    assert "strongest-row confusion pitch-class routes piano/electronic C->guitar=1" in result.stdout
    assert "piano/electronic E->guitar=1" in result.stdout
    assert "strongest-row confusion route medians" in result.stdout
    assert "piano/electronic->guitar rows=2 samples=2 debug_owners=piano=1 guitar=1" in result.stdout
    assert "expected_row_level=0.500 observed_row_level=0.700" in result.stdout
    assert "expected_row_pitch_level=0.500" in result.stdout
    assert "observed_row_pitch_level=0.700" in result.stdout
    assert "debug_exact_match=1.000 debug_pitch_match=1.000 debug_abs_delta=0.000" in result.stdout
    assert "visual-row confusion note buckets rows=2 samples=2" in result.stdout
    assert "piano/electronic C4->bass=1" in result.stdout
    assert "piano/electronic E2->other=1" in result.stdout
    assert "visual-row confusion routes piano/electronic->bass=1 piano/electronic->other=1" in result.stdout
    assert "visual-row confusion route medians" in result.stdout
    assert "source detail" in detailed_result.stdout
    assert "piano/electronic samples=2 midi=40-60" in detailed_result.stdout
    assert "top extra-row samples" in detailed_result.stdout
    assert "keyboard_1 pitch_buffers=1 exact_buffers=1 rows=bass=1 guitar=1" in detailed_result.stdout
    assert "top extra exact examples" in detailed_result.stdout
    assert (
        "piano/electronic->guitar keyboard_1@0 expected=C4/60 level=0.60"
        in detailed_result.stdout
    )
    assert "strongest-row confusion bucket samples" in detailed_result.stdout
    assert "piano/electronic C4->guitar rows=1 samples=1 keyboard_1" in detailed_result.stdout
    assert "strongest-row confusion bucket medians" in detailed_result.stdout
    assert "visual-row confusion bucket samples" in detailed_result.stdout
    assert "visual-row confusion bucket medians" in detailed_result.stdout
    assert "non-hit pitch buckets" in detailed_result.stdout
    assert "ownership_miss:piano/electronic note=E2->guitar samples=1" in detailed_result.stdout
    assert "non-hit sample attributes" in detailed_result.stdout
    assert "keyboard_2 status=ownership_miss source=piano/electronic expected=E2/40" in detailed_result.stdout
    print("test_summarize_real_note_attributes: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
