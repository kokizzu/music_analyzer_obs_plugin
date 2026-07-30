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
    "bass_visual_notes",
    "guitar_visual_notes",
    "piano_visual_notes",
    "vocal_visual_notes",
    "other_visual_notes",
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
            row(
                sample_id="keyboard_multi_debug",
                family="piano",
                source="electronic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="guitar",
                keyboard_score="0.20",
                guitar_score="0.90",
                guitar_notes="E4:0.30",
                piano_notes="E4:0.90",
            ),
            row(
                sample_id="keyboard_multi_debug",
                family="piano",
                source="electronic",
                expected_note="E4",
                expected_midi="64",
                debug_note="E4",
                debug_midi="64",
                debug_owner="piano",
                keyboard_score="0.90",
                guitar_score="0.10",
                guitar_notes="E4:0.30",
                piano_notes="E4:0.90",
            ),
            row(
                sample_id="keyboard_bass_shadow",
                family="piano",
                source="electronic",
                expected_note="C3",
                expected_midi="48",
                debug_note="C3",
                debug_midi="48",
                debug_owner="piano",
                bass_score="0.00",
                keyboard_score="0.80",
                guitar_score="0.10",
                bass_notes="C3:0.40",
                guitar_notes="",
                piano_notes="C3:0.90",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="measured_guitar_bass_shadow",
                family="piano",
                source="electronic",
                expected_note="E3",
                expected_midi="52",
                first_row="guitar",
                debug_note="E3",
                debug_midi="52",
                debug_owner="guitar",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                bass_notes="E3:0.68",
                guitar_notes="E3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="measured_guitar_bass_relaxed_periodicity",
                family="piano",
                source="electronic",
                expected_note="F3",
                expected_midi="53",
                first_row="guitar",
                debug_note="F3",
                debug_midi="53",
                debug_owner="guitar",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                periodicity="0.52",
                bass_notes="F3:0.68",
                guitar_notes="F3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="measured_guitar_bass_relaxed_noise",
                family="piano",
                source="electronic",
                expected_note="F#3",
                expected_midi="54",
                first_row="guitar",
                debug_note="F#3",
                debug_midi="54",
                debug_owner="guitar",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                noise="0.52",
                bass_notes="F#3:0.68",
                guitar_notes="F#3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="measured_guitar_bass_protected",
                family="bass",
                source="electronic",
                expected_note="E3",
                expected_midi="52",
                first_row="bass",
                debug_note="E3",
                debug_midi="52",
                debug_owner="guitar",
                bass_score="0.07",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                bass_notes="E3:0.73",
                guitar_notes="E3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="measured_guitar_bass_noisy_shadow",
                family="piano",
                source="electronic",
                expected_note="G3",
                expected_midi="55",
                first_row="guitar",
                debug_note="G3",
                debug_midi="55",
                debug_owner="guitar",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                noise="0.63",
                bass_notes="G3:0.68",
                guitar_notes="G3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
            ),
            row(
                sample_id="hidden_measured_guitar_bass_shadow",
                family="piano",
                source="electronic",
                expected_note="A3",
                expected_midi="57",
                first_row="guitar",
                debug_note="A3",
                debug_midi="57",
                debug_owner="guitar",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.30",
                vocal_score="0.00",
                other_score="0.00",
                bass_notes="A3:0.68",
                guitar_notes="A3:1.00",
                piano_notes="",
                vocal_notes="",
                other_notes="",
                bass_visual_notes="",
                guitar_visual_notes="A3:1.00",
            ),
            row(
                sample_id="measured_other_vocal_shadow",
                family="other",
                source="acoustic",
                expected_note="C4",
                expected_midi="60",
                first_row="other",
                debug_note="C4",
                debug_midi="60",
                debug_owner="other",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.00",
                vocal_score="0.00",
                other_score="0.82",
                bass_notes="",
                guitar_notes="",
                piano_notes="",
                vocal_notes="C4:0.20",
                other_notes="C4:0.67",
            ),
            row(
                sample_id="measured_other_vocal_protected",
                family="vocals",
                source="acoustic",
                expected_note="D4",
                expected_midi="62",
                first_row="vocals",
                debug_note="D4",
                debug_midi="62",
                debug_owner="other",
                bass_score="0.00",
                keyboard_score="0.00",
                guitar_score="0.00",
                vocal_score="0.00",
                other_score="0.82",
                bass_notes="",
                guitar_notes="",
                piano_notes="",
                vocal_notes="D4:0.30",
                other_notes="D4:0.67",
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
        min_extra_threshold_result = subprocess.run(
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
                "--min-threshold-extra-hits",
                "3",
                "--threshold-limit",
                "2",
                "--shadow-score-thresholds",
                "0.18,0.24",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        alias_threshold_result = subprocess.run(
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
                "--threshold-search",
                "--max-protected",
                "0",
                "--top-routes",
                "1",
                "--shadow-score-thresholds",
                "0.18,0.24",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
                "--show-examples",
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
        guarded_threshold_result = subprocess.run(
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
                "--min-pitch-confidence",
                "0.85",
                "--min-periodicity",
                "0.75",
                "--max-fit-error",
                "0.06",
                "--max-noise",
                "0.06",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        guarded_reject_result = subprocess.run(
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
                "--min-pitch-confidence",
                "0.95",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        owner_mode_result = subprocess.run(
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
                "--threshold-owner-mode",
                "shadow",
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
        all_threshold_result = subprocess.run(
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
                "--threshold-search",
                "--max-protected",
                "0",
                "--threshold-limit",
                "3",
                "--shadow-score-thresholds",
                "0.18,0.24",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        measured_runtime_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "guitar",
                "--target-row",
                "bass",
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
        measured_other_vocal_runtime_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "other",
                "--target-row",
                "vocals",
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
        protected_threshold_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_real_note_display_shadow.py"),
                str(path),
                "--shadow-row",
                "guitar",
                "--target-row",
                "bass",
                "--min-shadow-level",
                "0.10",
                "--min-target-level",
                "0.10",
                "--summary-only",
                "--threshold-search",
                "--max-protected",
                "1",
                "--threshold-limit",
                "1",
                "--shadow-score-thresholds",
                "0.24",
                "--score-ratios",
                "0.50",
                "--level-ratios",
                "0.90",
                "--threshold-protected-examples",
                "1",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

    output = result.stdout
    assert "piano->same-pitch guitar extras rows=3 samples=3" in output, output
    assert "sources piano/electronic=3" in output, output
    assert "piano->same-pitch guitar protected rows=1 samples=1" in output, output
    assert "sources guitar/acoustic=1" in output, output
    assert "target_score=0.80 shadow_score=0.20" in output, output
    assert "piano->same-pitch guitar suppressor simulations" in output, output
    assert "owner_shadow_score2_level" in output, output
    assert "extras=2/3 protected=0/1 precision=100.0% protected_rate=0.0%" in output, output
    source_breakdown_output = source_breakdown_result.stdout
    assert "extras_sources piano/electronic=2" in source_breakdown_output, source_breakdown_output
    assert "protected_sources --" in source_breakdown_output, source_breakdown_output
    summary_output = summary_result.stdout
    assert "piano->same-pitch guitar extras rows=3 samples=3" in summary_output, summary_output
    assert "piano->same-pitch guitar protected rows=1 samples=1" in summary_output, summary_output
    assert "target_level" not in summary_output, summary_output
    assert "example " not in summary_output, summary_output
    threshold_output = threshold_result.stdout
    assert (
        "piano->same-pitch guitar threshold search max_protected=0 min_extra_hits=1"
        in threshold_output
    ), threshold_output
    assert "protected=0/1 extras=2/3 min_shadow_score=0.18 score_ratio=0.50 level_ratio=0.90" in threshold_output, threshold_output
    assert "extra keyboard_note_only_debug@0 src=piano/electronic expected=D4/62" in threshold_output, threshold_output
    min_extra_threshold_output = min_extra_threshold_result.stdout
    assert (
        "piano->same-pitch guitar threshold search max_protected=0 min_extra_hits=3"
        in min_extra_threshold_output
    ), min_extra_threshold_output
    assert "no matching thresholds" in min_extra_threshold_output, min_extra_threshold_output
    alias_threshold_output = alias_threshold_result.stdout
    assert "piano->same-pitch guitar extras rows=3 samples=3" in alias_threshold_output, alias_threshold_output
    assert "piano->same-pitch guitar threshold search max_protected=0" in alias_threshold_output, alias_threshold_output
    assert alias_threshold_output.count("protected=0/1 extras=") == 1, alias_threshold_output
    assert "example keyboard_1@0 src=piano/electronic expected=C4/60" in alias_threshold_output, alias_threshold_output
    target_level_threshold_output = target_level_threshold_result.stdout
    assert (
        "protected=0/1 extras=2/3 min_shadow_score=0.18 score_ratio=0.50 "
        "level_ratio=0.90 target_level_max=0.40"
    ) in target_level_threshold_output, target_level_threshold_output
    guarded_threshold_output = guarded_threshold_result.stdout
    assert (
        "protected=0/1 extras=2/3 min_shadow_score=0.18 score_ratio=0.50 "
        "level_ratio=0.90 min_pitch_confidence=0.85 min_periodicity=0.75 "
        "max_fit_error=0.06 max_noise=0.06"
    ) in guarded_threshold_output, guarded_threshold_output
    guarded_reject_output = guarded_reject_result.stdout
    assert "no matching thresholds" in guarded_reject_output, guarded_reject_output
    owner_mode_output = owner_mode_result.stdout
    assert (
        "protected=0/1 extras=2/3 min_shadow_score=0.18 score_ratio=0.50 "
        "level_ratio=0.90 owner_mode=shadow"
    ) in owner_mode_output, owner_mode_output
    all_rows_output = all_rows_result.stdout
    assert "piano->same-pitch guitar extras rows=3 samples=3" in all_rows_output, all_rows_output
    assert "piano->same-pitch bass extras rows=1 samples=1" in all_rows_output, all_rows_output
    assert "runtime_keyboard_bass_weak" in all_rows_output, all_rows_output
    assert "runtime_keyboard_bass_guarded" in all_rows_output, all_rows_output
    assert "extras=1/1 protected=0/0 precision=100.0%" in all_rows_output, all_rows_output
    assert "guitar->same-pitch piano extras rows=1 samples=1" in all_rows_output, all_rows_output
    assert "piano->same-pitch piano" not in all_rows_output, all_rows_output
    all_threshold_output = all_threshold_result.stdout
    assert "ranked threshold-search opportunities" in all_threshold_output, all_threshold_output
    assert (
        "piano->same-pitch guitar protected=0/1 extras=2/3 "
        "min_shadow_score=0.18 score_ratio=0.50 level_ratio=0.90"
    ) in all_threshold_output, all_threshold_output
    assert (
        "piano->same-pitch bass protected=0/0 extras=1/1 "
        "min_shadow_score=0.18 score_ratio=0.50 level_ratio=0.90"
    ) in all_threshold_output, all_threshold_output
    measured_runtime_output = measured_runtime_result.stdout
    assert "guitar->same-pitch bass extras rows=4 samples=4" in measured_runtime_output, measured_runtime_output
    assert "runtime_guitar_bass_guarded" not in measured_runtime_output, measured_runtime_output
    assert (
        "runtime_guitar_bass_measured extras=3/4 protected=0/1 precision=100.0% protected_rate=0.0%"
    ) in measured_runtime_output, measured_runtime_output
    measured_other_vocal_runtime_output = measured_other_vocal_runtime_result.stdout
    assert (
        "other->same-pitch vocals extras rows=1 samples=1"
    ) in measured_other_vocal_runtime_output, measured_other_vocal_runtime_output
    assert (
        "other->same-pitch vocals protected rows=1 samples=1"
    ) in measured_other_vocal_runtime_output, measured_other_vocal_runtime_output
    assert (
        "runtime_other_vocal_measured extras=1/1 protected=0/1 precision=100.0% protected_rate=0.0%"
    ) in measured_other_vocal_runtime_output, measured_other_vocal_runtime_output
    protected_threshold_output = protected_threshold_result.stdout
    assert "protected=1/1 extras=4/4 min_shadow_score=0.24" in protected_threshold_output, protected_threshold_output
    assert "protected measured_guitar_bass_protected@0" in protected_threshold_output, protected_threshold_output
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
