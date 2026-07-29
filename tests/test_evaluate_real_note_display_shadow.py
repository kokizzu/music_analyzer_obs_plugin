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
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "raw_expected_ratio",
    "raw_expected_rank",
    "bass_notes",
    "guitar_notes",
    "piano_notes",
    "vocal_notes",
    "other_notes",
]


def row(**overrides: str) -> list[str]:
    values = {name: "" for name in HEADER}
    values.update(
        {
            "status": "hit",
            "detected": "1",
            "detected_anywhere": "1",
            "detected_expected_row": "1",
            "first_row": "piano",
            "nsynth_family": "",
            "source": "acoustic",
            "buffer": "0",
            "debug_note": "C4",
            "debug_midi": "60",
            "debug_owner": "piano",
            "debug_conf": "0.80",
            "bass_score": "0.00",
            "keyboard_score": "0.70",
            "guitar_score": "0.20",
            "vocal_score": "0.00",
            "other_score": "0.10",
            "spectral_level": "0.75",
            "pitch_confidence": "0.90",
            "periodicity": "0.80",
            "harmonicity": "0.45",
            "fit_error": "0.05",
            "centroid": "0.30",
            "slope": "0.10",
            "noise": "0.05",
            "partial2": "0.40",
            "partial3": "0.20",
            "partial4": "0.10",
            "partial5": "0.05",
            "raw_expected_ratio": "1.00",
            "raw_expected_rank": "1",
            "bass_notes": "",
            "guitar_notes": "C4:0.60",
            "piano_notes": "C4:0.90",
            "vocal_notes": "",
            "other_notes": "",
        }
    )
    values.update(overrides)
    return [values[name] for name in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(
                sample_id="keyboard_1",
                family="piano",
                source="electronic",
                expected_note="C4",
                expected_midi="60",
                debug_owner="guitar",
                keyboard_score="0.20",
                guitar_score="0.80",
            ),
            row(
                sample_id="guitar_1",
                family="guitar",
                expected_note="E3",
                expected_midi="52",
                debug_note="E3",
                debug_midi="52",
                debug_owner="guitar",
                keyboard_score="0.20",
                guitar_score="0.80",
                guitar_notes="E3:0.80",
                piano_notes="E3:0.55",
            ),
            row(
                sample_id="keyboard_note_only_debug",
                family="piano",
                source="electronic",
                expected_note="D4",
                expected_midi="62",
                debug_note="D4",
                debug_midi="",
                debug_owner="piano",
                keyboard_score="0.80",
                guitar_score="0.20",
                guitar_notes="D4:0.30",
                piano_notes="D4:0.90",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "piano",
                "--target-row",
                "guitar",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--examples",
                "1",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        summary_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "piano",
                "--target-row",
                "guitar",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        threshold_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "piano",
                "--target-row",
                "guitar",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
                "--threshold-search",
                "--max-protected",
                "0",
                "--threshold-limit",
                "2",
                "--shadow-score-thresholds",
                "0.18,0.24",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
                "--threshold-examples",
                "1",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        source_breakdown_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "piano",
                "--target-row",
                "guitar",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
                "--source-breakdown",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        target_level_threshold_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "piano",
                "--target-row",
                "guitar",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
                "--threshold-search",
                "--max-protected",
                "0",
                "--threshold-limit",
                "2",
                "--shadow-score-thresholds",
                "0.18",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
                "--target-level-thresholds",
                "0.40",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        all_rows_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "all",
                "--target-row",
                "all",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

    output = result.stdout
    assert "piano->same-pitch guitar extras rows=2 samples=2" in output, output
    assert "sources piano/electronic=2" in output, output
    assert "piano->same-pitch guitar protected rows=1 samples=1" in output, output
    assert "sources guitar/acoustic=1" in output, output
    assert "target_score=0.80 shadow_score=0.20" in output, output
    assert "piano->same-pitch guitar suppressor simulations" in output, output
    assert "owner_shadow_score2_level" in output, output
    assert "extras=1/2 protected=0/1 precision=100.0% protected_rate=0.0%" in output, output
    source_breakdown_output = source_breakdown_result.stdout
    assert "extras_sources piano/electronic=1" in source_breakdown_output, source_breakdown_output
    assert "protected_sources --" in source_breakdown_output, source_breakdown_output
    summary_output = summary_result.stdout
    assert "piano->same-pitch guitar extras rows=2 samples=2" in summary_output, summary_output
    assert "piano->same-pitch guitar protected rows=1 samples=1" in summary_output, summary_output
    assert "target_level" not in summary_output, summary_output
    assert "example " not in summary_output, summary_output
    threshold_output = threshold_result.stdout
    assert "piano->same-pitch guitar threshold search max_protected=0" in threshold_output, threshold_output
    assert "protected=0/1 extras=1/2 min_shadow_score=0.18 score_ratio=0.50 level_ratio=0.90" in threshold_output, threshold_output
    assert "extra keyboard_note_only_debug@0 src=piano/electronic expected=D4/62" in threshold_output, threshold_output
    target_level_threshold_output = target_level_threshold_result.stdout
    assert (
        "protected=0/1 extras=1/2 min_shadow_score=0.18 score_ratio=0.50 "
        "level_ratio=0.90 target_level_max=0.40"
    ) in target_level_threshold_output, target_level_threshold_output
    all_rows_output = all_rows_result.stdout
    assert "piano->same-pitch guitar extras rows=2 samples=2" in all_rows_output, all_rows_output
    assert "guitar->same-pitch piano extras rows=1 samples=1" in all_rows_output, all_rows_output
    assert "piano->same-pitch piano" not in all_rows_output, all_rows_output
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
