#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_instrument_owner_patterns.py"
sys.path.insert(0, str(ROOT / "scripts"))

import find_instrument_owner_patterns as patterns

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
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
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
            "raw_fifth_up_ratio": "0.4",
            "raw_second_octave_up_ratio": "0.2",
            "raw_upper_major_third_ratio": "0.1",
            "raw_upper_fifth_ratio": "0.05",
            "raw_third_octave_up_ratio": "0.02",
            "debug_note": "C4",
            "debug_midi": "60",
            "debug_owner": "piano",
            "debug_conf": "0.8",
            "bass_score": "0.0",
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
                detected_expected_row="0",
                expected_level="0.0",
                guitar_level="0.0",
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
                detected_expected_row="0",
                expected_level="0.0",
                guitar_level="0.0",
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
            row(
                family="bass",
                expected_family="bass",
                program_name="Finger Bass",
                note="E2",
                midi="40",
                path="bass_1.wav",
                debug_note="E2",
                debug_midi="40",
                debug_owner="bass",
                debug_conf="0.72",
                bass_score="0.72",
                keyboard_score="0.0",
                guitar_score="0.2",
                vocal_score="0.0",
                other_score="0.0",
            ),
            row(
                family="strings",
                expected_family="strings",
                program_name="Pizzicato Strings",
                note="G2",
                midi="43",
                path="strings_miss_1.wav",
                status="miss",
                detected_expected_row="0",
                detected_anywhere="1",
                expected_level="0.0",
                other_level="0.0",
                raw_expected_ratio="0.91",
                raw_tuned_ratio="0.90",
                raw_tuned_abs_cent_offset="18",
                raw_expected_rank="1",
                debug_note="",
                debug_midi="",
                debug_owner="",
                debug_conf="",
            ),
            row(
                family="strings",
                expected_family="strings",
                program_name="Pizzicato Strings",
                note="G2",
                midi="43",
                path="strings_miss_2.wav",
                status="miss",
                detected_expected_row="0",
                detected_anywhere="1",
                expected_level="0.0",
                other_level="0.0",
                raw_expected_ratio="0.92",
                raw_tuned_ratio="0.91",
                raw_tuned_abs_cent_offset="18",
                raw_expected_rank="1",
                debug_note="",
                debug_midi="",
                debug_owner="",
                debug_conf="",
            ),
            row(
                family="strings",
                expected_family="strings",
                program_name="Pizzicato Strings",
                note="A2",
                midi="45",
                path="strings_hit_1.wav",
                status="hit",
                detected_expected_row="1",
                detected_anywhere="1",
                expected_level="0.7",
                other_level="0.7",
                raw_expected_ratio="0.94",
                raw_tuned_ratio="0.93",
                raw_expected_rank="1",
                debug_note="",
                debug_midi="",
                debug_owner="",
                debug_conf="",
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
                "--top-buckets",
                "4",
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
                "debug_owner_miss:guitar->piano",
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
        cross_family = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_miss:guitar->piano",
                "--limit",
                "3",
                "--negative-mode",
                "not-family",
                "--max-negative-samples",
                "3",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        runtime_fields = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_miss:guitar->piano",
                "--field-preset",
                "full-mix-debug",
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
        profile_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_miss:guitar->piano",
                "--limit",
                "3",
                "--max-negative-samples",
                "0",
                "--profile-fields",
                "3",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        status_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--status-bucket",
                "miss:strings",
                "--limit",
                "10",
                "--min-positive-samples",
                "2",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "3",
                "--beam-width",
                "80",
                "--include-display-fields",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        auto_owner = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--top-buckets",
                "1",
                "--limit",
                "3",
                "--min-positive-samples",
                "2",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        parallel_auto_owner = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--top-buckets",
                "2",
                "--limit",
                "3",
                "--min-positive-samples",
                "1",
                "--max-negative-samples",
                "2",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
                "--jobs",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        serial_auto_owner = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--top-buckets",
                "2",
                "--limit",
                "3",
                "--min-positive-samples",
                "1",
                "--max-negative-samples",
                "2",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
                "--jobs",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        auto_status = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--status-top-buckets",
                "1",
                "--status-bucket-status",
                "miss",
                "--limit",
                "3",
                "--min-positive-samples",
                "2",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        parallel_auto_status = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--status-top-buckets",
                "2",
                "--status-bucket-status",
                "miss",
                "--limit",
                "3",
                "--min-positive-samples",
                "1",
                "--max-negative-samples",
                "1",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
                "--jobs",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        serial_auto_status = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--status-top-buckets",
                "2",
                "--status-bucket-status",
                "miss",
                "--limit",
                "3",
                "--min-positive-samples",
                "1",
                "--max-negative-samples",
                "1",
                "--max-conditions",
                "2",
                "--beam-width",
                "40",
                "--jobs",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        status_reason = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--status-bucket",
                "miss:strings",
                "--condition",
                "miss_reason=ownership",
                "--limit",
                "3",
                "--min-positive-samples",
                "2",
                "--max-negative-samples",
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
        bass_hit = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--bucket",
                "owner_hit:bass->bass",
                "--condition",
                "debug_owner=bass",
                "--show-examples",
                "1",
                "--max-negative-samples",
                "4",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    assert (
        "owner_miss:guitar->piano positives=2 samples/2 rows negatives(owner-hit)=5 samples/5 rows"
        in result.stdout
    ), result.stdout + result.stderr
    assert "AND partial2<=0.14: pos=2/2 rows=2 neg=0/5 rows=0" in result.stdout, result.stdout + result.stderr
    assert "side_rows=0 net_rows=2 gain_per_side=inf" in result.stdout, result.stdout + result.stderr
    assert "highest-coverage candidate rules" in result.stdout, result.stdout + result.stderr
    assert "detected_expected_row" not in result.stdout, result.stdout + result.stderr
    assert "expected_level" not in result.stdout, result.stdout + result.stderr
    assert "explicit rule:" in example.stdout, example.stdout + example.stderr
    assert "debug_owner=piano: pos=2/2 rows=2 neg=2/5 rows=2" in example.stdout, (
        example.stdout + example.stderr
    )
    assert "side_rows=2 net_rows=0 gain_per_side=1.00" in example.stdout, (
        example.stdout + example.stderr
    )
    assert "positive examples:" in example.stdout, example.stdout + example.stderr
    assert "guitar Clean Guitar E3 path=guitar_1.wav status=hit target=guitar" in example.stdout, (
        example.stdout + example.stderr
    )
    assert "protected-hit examples:" in example.stdout, example.stdout + example.stderr
    assert "piano Grand Piano C4 path=piano_1.wav status=hit target=piano" in example.stdout, (
        example.stdout + example.stderr
    )
    assert (
        "owner_miss:guitar->piano positives=2 samples/2 rows negatives(not-family)=7 samples/7 rows"
        in cross_family.stdout
    ), cross_family.stdout + cross_family.stderr
    assert "partial2<=0.14" in runtime_fields.stdout, runtime_fields.stdout + runtime_fields.stderr
    assert "raw_expected" not in runtime_fields.stdout, runtime_fields.stdout + runtime_fields.stderr
    assert "program_name" not in runtime_fields.stdout, runtime_fields.stdout + runtime_fields.stderr
    assert "numeric attribute profile:" in profile_result.stdout, profile_result.stdout + profile_result.stderr
    assert "partial2 <=" in profile_result.stdout, profile_result.stdout + profile_result.stderr
    assert "category attribute profile:" in profile_result.stdout, profile_result.stdout + profile_result.stderr
    assert "program_name=Clean Guitar" in profile_result.stdout, profile_result.stdout + profile_result.stderr
    assert (
        "status:miss:strings positives=2 samples/2 rows negatives(same-family-hit)=1 samples/1 rows"
        in status_result.stdout
    ), status_result.stdout + status_result.stderr
    assert "expected_level<=0: pos=2/2 rows=2 neg=0/1 rows=0" in status_result.stdout, (
        status_result.stdout + status_result.stderr
    )
    assert "side_rows=0 net_rows=2 gain_per_side=inf" in status_result.stdout, (
        status_result.stdout + status_result.stderr
    )
    assert "strings Pizzicato Strings G2 path=strings_miss_1.wav status=miss" in status_result.stdout, (
        status_result.stdout + status_result.stderr
    )
    assert "owner_miss:guitar->piano positives=2 samples/2 rows" in auto_owner.stdout, (
        auto_owner.stdout + auto_owner.stderr
    )
    assert "owner_miss:guitar->other" not in auto_owner.stdout, auto_owner.stdout + auto_owner.stderr
    assert parallel_auto_owner.stdout == serial_auto_owner.stdout
    assert "status:miss:strings positives=2 samples/2 rows" in auto_status.stdout, (
        auto_status.stdout + auto_status.stderr
    )
    assert "status:hit:" not in auto_status.stdout, auto_status.stdout + auto_status.stderr
    assert parallel_auto_status.stdout == serial_auto_status.stdout
    assert "miss_reason=ownership: pos=2/2 rows=2 neg=0/1 rows=0" in status_reason.stdout, (
        status_reason.stdout + status_reason.stderr
    )
    assert "reason=ownership" in status_reason.stdout, status_reason.stdout + status_reason.stderr
    assert "owner_hit:bass->bass positives=1 samples/1 rows" in bass_hit.stdout, (
        bass_hit.stdout + bass_hit.stderr
    )
    assert "bass Finger Bass E2 path=bass_1.wav status=hit target=bass" in bass_hit.stdout, (
        bass_hit.stdout + bass_hit.stderr
    )
    print("test_find_instrument_owner_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
