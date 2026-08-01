#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import find_real_note_attribute_patterns as patterns

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
    "bass_visual_level",
    "guitar_visual_level",
    "piano_visual_level",
    "vocal_visual_level",
    "other_visual_level",
    "amb_visual_level",
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
            "buffer_strongest_row": "piano",
            "raw_expected_peak": "8.0",
            "raw_expected_ratio": "1.0",
            "raw_tuned_peak": "8.5",
            "raw_tuned_ratio": "1.0",
            "raw_tuned_cent_offset": "0",
            "raw_tuned_abs_cent_offset": "0",
            "raw_local_best_note": "F#4",
            "raw_local_best_midi": "66",
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
    assert not patterns.constraints_compatible(
        (patterns.numeric_pattern("centroid", "<=", 0.04).constraint,),
        patterns.numeric_pattern("centroid", ">=", 0.04).constraint,
    )
    assert patterns.constraints_compatible(
        (patterns.numeric_pattern("centroid", ">=", 0.03).constraint,),
        patterns.numeric_pattern("centroid", "<=", 0.04).constraint,
    )
    assert not patterns.constraints_compatible(
        (patterns.numeric_pattern("debug_midi", "<=", 46).constraint,),
        patterns.numeric_pattern("debug_midi", "<=", 57).constraint,
    )
    assert not patterns.constraints_compatible(
        (patterns.category_pattern("debug_owner", "guitar").constraint,),
        patterns.category_pattern("debug_owner", "piano").constraint,
    )
    assert patterns.derive_real_note_row({})["debug_score_state"] == "no_debug"
    assert (
        patterns.derive_real_note_row(
            {"debug_note": "C4", "debug_midi": "60", "debug_owner": "amb"}
        )["debug_score_state"]
        == "unscored_amb"
    )
    assert (
        patterns.derive_real_note_row(
            {"debug_note": "C4", "debug_midi": "60", "debug_owner": "amb", "guitar_score": "0.2"}
        )["debug_score_state"]
        == "scored_amb"
    )
    assert (
        patterns.derive_real_note_row(
            {"debug_note": "E2", "debug_midi": "40", "debug_owner": "bass", "bass_score": "0.4"}
        )["debug_score_state"]
        == "scored_owner"
    )
    visual_row = patterns.derive_real_note_row(
        {
            "family": "piano",
            "expected_midi": "60",
            "buffer_visual_strongest_row": "guitar",
            "piano_visual_notes": "C4:0.50",
            "guitar_visual_notes": "C4:0.90",
        }
    )
    assert visual_row["expected_row_visual_exact_level"] == "0.500"
    assert visual_row["expected_row_visual_pitch_level"] == "0.500"
    assert visual_row["visual_strongest_row_exact_level"] == "0.900"
    assert visual_row["visual_strongest_row_pitch_level"] == "0.900"
    assert visual_row["expected_visual_exact_row_count"] == "2"
    assert "expected_row_visual_exact_level" in patterns.ROW_CONTEXT_NUMERIC_FIELDS
    assert "visual_strongest_row_pitch_level" in patterns.ROW_CONTEXT_NUMERIC_FIELDS

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
        extra_protected_path = pathlib.Path(tmp) / "extra_protected_attributes.tsv"
        extra_protected_rows = [
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="extra_keyboard_protected",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                debug_note="F#4",
                debug_midi="66",
                debug_owner="piano",
                partial2="0.13",
            )
        ]
        extra_protected_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in extra_protected_rows) + "\n"
        )
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
        near_miss_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "0",
                "--show-near-misses",
                "2",
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
                "--row-examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        range_result = subprocess.run(
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
                "debug_midi:66:69",
                "--condition",
                "debug_owner=piano",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        extra_protected_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "3",
                "--extra-protected-path",
                str(extra_protected_path),
                "--row-examples",
                "1",
                "--condition",
                "debug_midi:66:69",
                "--condition",
                "debug_owner=piano",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        reason_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "0",
                "--condition",
                "miss_reason=ownership",
                "--row-examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        score_state_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "3",
                "--condition",
                "debug_score_state=scored_owner",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        profile_result = subprocess.run(
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
                "--profile-fields",
                "3",
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
        auto_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(path),
                "--top-buckets",
                "1",
                "--limit",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        hit_path = pathlib.Path(tmp) / "hit_attributes.tsv"
        hit_rows = [
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="piano_wrong_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                debug_owner="guitar",
                keyboard_score="0",
                guitar_score="1",
            ),
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="piano_wrong_2",
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
            ),
            row(
                status="hit",
                first_row="piano",
                sample_id="piano_right",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C5",
                expected_midi="72",
            ),
            row(
                status="hit",
                first_row="guitar",
                sample_id="guitar_right",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="guitar",
                keyboard_score="0",
                guitar_score="1",
            ),
        ]
        hit_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in hit_rows) + "\n"
        )
        hit_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(hit_path),
                "--bucket",
                "hit:piano/electronic->guitar",
                "--condition",
                "debug_owner=guitar",
                "--limit",
                "2",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        row_confusion_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(hit_path),
                "--top-buckets",
                "1",
                "--bucket-status",
                "row_confusion",
                "--include-row-context",
                "--condition",
                "debug_owner=guitar",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        parallel_path = pathlib.Path(tmp) / "parallel_attributes.tsv"
        parallel_rows = [
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="piano_wrong_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                debug_owner="guitar",
                keyboard_score="0",
                guitar_score="1",
            ),
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="piano_wrong_2",
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
            ),
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="other_wrong_1",
                family="other",
                nsynth_family="string",
                source="acoustic",
                expected_note="C4",
                expected_midi="60",
                debug_note="C4",
                debug_midi="60",
                debug_owner="piano",
                other_score="0",
                keyboard_score="1",
            ),
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="other_wrong_2",
                family="other",
                nsynth_family="string",
                source="acoustic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="piano",
                other_score="0",
                keyboard_score="1",
            ),
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="piano_right",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C5",
                expected_midi="72",
            ),
            row(
                status="hit",
                first_row="other",
                buffer_strongest_row="other",
                sample_id="other_right",
                family="other",
                nsynth_family="string",
                source="acoustic",
                expected_note="G4",
                expected_midi="67",
                debug_note="G4",
                debug_midi="67",
                debug_owner="other",
            ),
        ]
        parallel_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in parallel_rows) + "\n"
        )
        parallel_args = [
            sys.executable,
            str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
            str(parallel_path),
            "--top-buckets",
            "2",
            "--bucket-status",
            "row_confusion",
            "--limit",
            "2",
            "--min-positive-samples",
            "1",
            "--max-negative-samples",
            "4",
            "--show-examples",
            "1",
        ]
        serial_bucket_result = subprocess.run(
            [*parallel_args, "--jobs", "1"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        parallel_bucket_result = subprocess.run(
            [*parallel_args, "--jobs", "2"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        visual_rows = [
            row(
                status="hit",
                first_row="piano",
                visual_first_row="guitar",
                buffer_strongest_row="piano",
                buffer_visual_strongest_row="guitar",
                sample_id="keyboard_visual_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="F#4",
                expected_midi="66",
                debug_note="F#4",
                debug_midi="66",
                debug_owner="guitar",
                guitar_visual_level="0.95",
                piano_visual_level="0.35",
            ),
            row(
                status="hit",
                first_row="piano",
                visual_first_row="guitar",
                buffer_strongest_row="piano",
                buffer_visual_strongest_row="guitar",
                sample_id="keyboard_visual_2",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                debug_owner="guitar",
                guitar_visual_level="0.90",
                piano_visual_level="0.40",
            ),
            row(
                status="hit",
                first_row="piano",
                visual_first_row="piano",
                buffer_strongest_row="piano",
                buffer_visual_strongest_row="piano",
                sample_id="keyboard_visual_right",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C4",
                expected_midi="60",
                debug_note="C4",
                debug_midi="60",
                debug_owner="piano",
                guitar_visual_level="0.10",
                piano_visual_level="0.90",
            ),
            row(
                status="hit",
                first_row="guitar",
                visual_first_row="guitar",
                buffer_strongest_row="guitar",
                buffer_visual_strongest_row="guitar",
                sample_id="guitar_visual_right",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="guitar",
                guitar_visual_level="0.90",
                piano_visual_level="0.10",
            ),
        ]
        visual_path = pathlib.Path(tmp) / "visual_attributes.tsv"
        visual_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in visual_rows) + "\n"
        )
        visual_row_confusion_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(visual_path),
                "--top-buckets",
                "1",
                "--bucket-status",
                "visual_row_confusion",
                "--include-row-context",
                "--condition",
                "buffer_visual_strongest_row=guitar",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        visual_row_scoped_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(visual_path),
                "--top-buckets",
                "1",
                "--bucket-status",
                "visual_row_confusion",
                "--protected-scope",
                "same-source-correct-row",
                "--include-row-context",
                "--condition",
                "buffer_visual_strongest_row=guitar",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        octave_path = pathlib.Path(tmp) / "octave_attributes.tsv"
        octave_rows = [
            row(
                status="hit",
                first_row="bass",
                buffer_strongest_row="bass",
                sample_id="bass_octave_1",
                family="bass",
                source="electronic",
                expected_note="E1",
                expected_midi="28",
                debug_note="E2",
                debug_midi="40",
                debug_owner="bass",
            ),
            row(
                status="hit",
                first_row="bass",
                buffer_strongest_row="bass",
                sample_id="bass_octave_2",
                family="bass",
                source="electronic",
                expected_note="A1",
                expected_midi="33",
                debug_note="A2",
                debug_midi="45",
                debug_owner="bass",
            ),
            row(
                status="hit",
                first_row="bass",
                buffer_strongest_row="bass",
                sample_id="bass_right",
                family="bass",
                source="electronic",
                expected_note="D2",
                expected_midi="38",
                debug_note="D2",
                debug_midi="38",
                debug_owner="bass",
            ),
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="guitar_right",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="E2",
                expected_midi="40",
                debug_note="E2",
                debug_midi="40",
                debug_owner="guitar",
            ),
        ]
        octave_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in octave_rows) + "\n"
        )
        octave_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(octave_path),
                "--top-buckets",
                "1",
                "--bucket-status",
                "octave_displacement",
                "--condition",
                "debug_delta=12",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        placement_path = pathlib.Path(tmp) / "placement_attributes.tsv"
        placement_rows = [
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="guitar_hidden_1",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="F#4",
                expected_midi="66",
                debug_note="F#4",
                debug_midi="66",
                piano_notes="F#4:1.00",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="guitar_hidden_2",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                piano_notes="A4:0.90",
            ),
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="guitar_visible",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="C4",
                expected_midi="60",
                debug_note="C4",
                debug_midi="60",
                guitar_notes="C4:1.00",
            ),
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="piano_visible",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                piano_notes="E4:1.00",
            ),
        ]
        placement_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in placement_rows) + "\n"
        )
        placement_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(placement_path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--include-row-context",
                "--condition",
                "expected_row_exact_level<=0",
                "--limit",
                "1",
                "--max-negative-samples",
                "0",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        foreign_path = pathlib.Path(tmp) / "foreign_attributes.tsv"
        foreign_rows = [
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_foreign_1",
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
                sample_id="guitar_foreign_2",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                partial2="0.13",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="bass_foreign",
                family="bass",
                nsynth_family="bass",
                source="electronic",
                expected_note="E2",
                expected_midi="40",
                debug_note="E2",
                debug_midi="40",
                partial2="0.12",
            ),
            row(
                status="hit",
                first_row="piano",
                sample_id="piano_protected",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C4",
                expected_midi="60",
                debug_note="C4",
                debug_midi="60",
                partial2="0.12",
            ),
        ]
        foreign_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in foreign_rows) + "\n"
        )
        foreign_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(foreign_path),
                "--bucket",
                "ownership_miss:guitar/acoustic->piano",
                "--condition",
                "debug_owner=piano",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
                "--row-examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        wildcard_path = pathlib.Path(tmp) / "wildcard_attributes.tsv"
        wildcard_rows = [
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="piano",
                sample_id="guitar_acoustic_hidden",
                family="guitar",
                nsynth_family="guitar",
                source="acoustic",
                expected_note="F#4",
                expected_midi="66",
                debug_note="F#4",
                debug_midi="66",
                debug_owner="piano",
                partial2="0.12",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="other",
                sample_id="guitar_electric_hidden",
                family="guitar",
                nsynth_family="guitar",
                source="electric",
                expected_note="A4",
                expected_midi="69",
                debug_note="A4",
                debug_midi="69",
                debug_owner="other",
                partial2="0.13",
            ),
            row(
                status="hit",
                first_row="guitar",
                buffer_strongest_row="guitar",
                sample_id="guitar_protected",
                family="guitar",
                nsynth_family="guitar",
                source="electric",
                expected_note="C4",
                expected_midi="60",
                debug_note="C4",
                debug_midi="60",
                debug_owner="guitar",
                partial2="0.62",
            ),
            row(
                status="hit",
                first_row="piano",
                buffer_strongest_row="piano",
                sample_id="piano_protected",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="piano",
                partial2="0.12",
            ),
        ]
        wildcard_path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in wildcard_rows) + "\n"
        )
        wildcard_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(wildcard_path),
                "--bucket",
                "ownership_miss:guitar/*->*",
                "--condition",
                "miss_reason=ownership",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        wildcard_scoped_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "find_real_note_attribute_patterns.py"),
                str(wildcard_path),
                "--bucket",
                "ownership_miss:guitar/*->*",
                "--protected-scope",
                "same-source",
                "--condition",
                "miss_reason=ownership",
                "--limit",
                "1",
                "--max-negative-samples",
                "2",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "ownership_miss:guitar/acoustic->piano positives=2 samples/2 rows" in result.stdout
    assert "debug_owner=piano AND partial2<=0.14: pos=2/2 rows=2 neg=0/2 rows=0" in result.stdout
    assert "side_rows=0 net_rows=2 gain_per_side=inf" in result.stdout
    assert "highest-coverage candidate rules" in result.stdout
    assert "nearest over-budget single-condition candidate rules:" in near_miss_result.stdout
    assert "pos=2/2 rows=2 neg=1/2 rows=1" in near_miss_result.stdout
    assert "side_rows=1 net_rows=1 gain_per_side=2.00" in near_miss_result.stdout
    assert "explicit rule:" in example_result.stdout
    assert "debug_owner=piano: pos=2/2 rows=2 neg=1/2 rows=1" in example_result.stdout
    assert "positive examples:" in example_result.stdout
    assert "guitar_1 expected=F#4/66 debug=F#4/66 owner=piano" in example_result.stdout
    assert "reason=ownership" in example_result.stdout
    assert "protected-hit examples:" in example_result.stdout
    assert "keyboard_1 expected=F#4/66 debug=F#4/66 owner=piano" in example_result.stdout
    assert (
        "66<=debug_midi<=69 AND debug_owner=piano: pos=2/2 rows=2 neg=1/2 rows=1"
    ) in range_result.stdout
    assert (
        "66<=debug_midi<=69 AND debug_owner=piano: pos=2/2 rows=2 neg=2/3 rows=2"
    ) in extra_protected_result.stdout
    assert "extra_keyboard_protected expected=F#4/66 debug=F#4/66 owner=piano" in (
        extra_protected_result.stdout
    )
    assert "miss_reason=ownership: pos=2/2 rows=2 neg=0/2 rows=0" in reason_result.stdout
    assert "debug_score_state=scored_owner: pos=2/2 rows=2" in score_state_result.stdout
    assert "numeric attribute profile:" in profile_result.stdout
    assert "partial2 <= sep=0.750 pos=0.13 [0.12..0.14] protected=0.375 [0.13..0.62]" in profile_result.stdout
    assert "category attribute profile:" in profile_result.stdout
    assert "debug_owner=piano enrich=0.500 pos=2/2 protected=1/2" in profile_result.stdout
    assert (
        "debug_midi<=69 AND partial2<=0.13 AND pitch_confidence>=0.95: "
        "pos=2/2 rows=2 neg=0/3 rows=0"
    ) in multi_result.stdout, multi_result.stdout + multi_result.stderr
    assert "ownership_miss:guitar/acoustic->piano positives=2 samples/2 rows" in auto_result.stdout
    assert (
        "hit:piano/electronic->guitar positives=2 samples/2 rows "
        "protected_hits=2 samples/2 rows"
    ) in hit_result.stdout
    assert "debug_owner=guitar: pos=2/2 rows=2 neg=1/2 rows=1" in hit_result.stdout
    assert (
        "row_confusion:piano/electronic->guitar positives=2 samples/2 rows "
        "protected_hits=2 samples/2 rows"
    ) in row_confusion_result.stdout
    assert "debug_owner=guitar: pos=2/2 rows=2 neg=1/2 rows=1" in row_confusion_result.stdout
    assert serial_bucket_result.stdout == parallel_bucket_result.stdout
    assert "row_confusion:piano/electronic->guitar" in parallel_bucket_result.stdout
    assert "row_confusion:other/acoustic->piano" in parallel_bucket_result.stdout
    assert (
        "visual_row_confusion:piano/electronic->guitar positives=2 samples/2 rows "
        "protected_hits=2 samples/2 rows"
    ) in visual_row_confusion_result.stdout
    assert (
        "buffer_visual_strongest_row=guitar: pos=2/2 rows=2 neg=1/2 rows=1"
    ) in visual_row_confusion_result.stdout
    assert (
        "visual_row_confusion:piano/electronic->guitar positives=2 samples/2 rows "
        "protected_hits=1 samples/1 rows"
    ) in visual_row_scoped_result.stdout
    assert (
        "buffer_visual_strongest_row=guitar: pos=2/2 rows=2 neg=0/1 rows=0"
    ) in visual_row_scoped_result.stdout
    assert (
        "octave_displacement:bass/electronic->+12 positives=2 samples/2 rows "
        "protected_hits=2 samples/2 rows"
    ) in octave_result.stdout
    assert "debug_delta=12: pos=2/2 rows=2 neg=0/2 rows=0" in octave_result.stdout
    assert "expected_row_exact_level<=0: pos=2/2 rows=2 neg=0/2 rows=0" in placement_result.stdout
    assert (
        "ownership_miss:guitar/acoustic->piano positives=2 samples/2 rows "
        "protected_hits=1 samples/1 rows foreign_misses=1 samples/1 rows"
    ) in foreign_result.stdout
    assert (
        "debug_owner=piano: pos=2/2 rows=2 neg=1/1 rows=1 "
        "foreign_miss=1/1 rows=1"
    ) in foreign_result.stdout
    assert "side_rows=2 net_rows=0 gain_per_side=1.00" in foreign_result.stdout
    assert "foreign-miss examples:" in foreign_result.stdout
    assert "bass_foreign expected=E2/40 debug=E2/40 owner=piano" in foreign_result.stdout
    assert (
        "ownership_miss:guitar/*->* positives=2 samples/2 rows protected_hits=2 samples/2 rows"
    ) in wildcard_result.stdout
    assert "miss_reason=ownership: pos=2/2 rows=2 neg=0/2 rows=0" in wildcard_result.stdout
    assert (
        "ownership_miss:guitar/*->* positives=2 samples/2 rows protected_hits=1 samples/1 rows"
    ) in wildcard_scoped_result.stdout
    assert "miss_reason=ownership: pos=2/2 rows=2 neg=0/1 rows=0" in wildcard_scoped_result.stdout
    print("test_find_real_note_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
