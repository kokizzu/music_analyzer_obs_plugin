#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_detector_coverage_candidates.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    summary = """detector_route_summary: candidates=3 low_false=2 shadow=0 near_miss=0 guitar=1 drum=0 positive_net=3 gain_ge_1=3 source_safe_positive_net=3 actionable=0 coverage_blocked=3
  coverage-blocked candidates need more positive samples before detector changes
    coverage_need guitar bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0 observed_samples=4 need_samples=1 +rows=7 side_rows=0 net_rows=7 gain_per_side=inf :: analysis_root<=0 AND smooth_tones<=1
    coverage_need low-false row_confusion:piano/electronic->guitar observed_samples=4 need_samples=1 +rows=4 side_rows=0 net_rows=4 gain_per_side=inf :: centroid>=0.52 AND partial4<=0.018 AND partial4>=0
    coverage_need low-false visual_row_confusion:piano/electronic->other observed_samples=2 need_samples=3 +rows=4 side_rows=0 net_rows=4 gain_per_side=inf :: adjacent_lower_ratio>=0.006 AND adjacent_upper_ratio<=0 AND bass_score<=0
"""
    header = [
        "sample_id",
        "status",
        "family",
        "source",
        "expected_note",
        "expected_midi",
        "first_row",
        "visual_first_row",
        "debug_note",
        "debug_midi",
        "debug_owner",
        "centroid",
        "partial4",
        "adjacent_lower_ratio",
        "adjacent_upper_ratio",
        "bass_score",
        "spectral_level",
        "pitch_confidence",
        "periodicity",
        "fit_error",
    ]
    rows = [
        [
            "organ_1",
            "hit",
            "piano",
            "electronic",
            "E5",
            "76",
            "guitar",
            "guitar",
            "E5",
            "76",
            "guitar",
            "0.550",
            "0.010",
            "0.020",
            "0.100",
            "0.000",
            "0.133",
            "0.055",
            "0.449",
            "2.998",
        ],
        [
            "organ_2",
            "hit",
            "piano",
            "electronic",
            "C5",
            "72",
            "other",
            "other",
            "C8",
            "108",
            "amb",
            "0.100",
            "0.030",
            "0.010",
            "0.000",
            "0.000",
            "0.973",
            "0.409",
            "0.336",
            "0.057",
        ],
        [
            "guitar_1",
            "hit",
            "guitar",
            "acoustic",
            "E3",
            "52",
            "guitar",
            "guitar",
            "E3",
            "52",
            "guitar",
            "0.300",
            "0.030",
            "0.000",
            "0.000",
            "0.000",
            "0.700",
            "0.800",
            "0.900",
            "0.100",
        ],
    ]
    guitar_header = [
        "recording_id",
        "status",
        "quality",
        "expected_label",
        "guitar_match_kind",
        "support",
        "guitar_chord",
        "analysis_root",
        "smooth_tones",
        "rms",
        "low",
        "mid",
        "high",
        "audio_path",
    ]
    guitar_rows = [
        [
            "168_QM1wc",
            "chord_miss",
            "pow",
            "Fpow",
            "different_root",
            "visible1_analysis1_smooth1_rootvis0",
            "Am=Am9=Am7=C=C7=C6",
            "0.000",
            "1.000",
            "0.020",
            "0.200",
            "0.700",
            "0.100",
            "/tmp/168_QM1wc.wav",
        ],
        [
            "168_QM1wc",
            "chord_miss",
            "pow",
            "Fpow",
            "different_root",
            "visible1_analysis1_smooth1_rootvis0",
            "Am=Am9=Am7=C=C7=C6",
            "0.000",
            "1.000",
            "0.021",
            "0.201",
            "0.699",
            "0.100",
            "/tmp/168_QM1wc.wav",
        ],
        [
            "single_note_no_chord",
            "no_chord",
            "--",
            "--",
            "no_display_label",
            "visible0_analysis0_smooth0_rootvis0",
            "--",
            "0.000",
            "0.000",
            "0.010",
            "0.100",
            "0.800",
            "0.100",
            "/tmp/single_note_no_chord.wav",
        ],
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        summary_path = tmp_path / "detector_summary.txt"
        rows_path = tmp_path / "real_note_rows.tsv"
        guitar_rows_path = tmp_path / "guitar_rows.tsv"
        summary_path.write_text(summary, encoding="utf-8")
        rows_path.write_text(
            "\n".join(["\t".join(header)] + ["\t".join(row) for row in rows]) + "\n",
            encoding="utf-8",
        )
        guitar_rows_path.write_text(
            "\n".join(["\t".join(guitar_header)] + ["\t".join(row) for row in guitar_rows]) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(summary_path),
                "--limit",
                "3",
                "--examples",
                "1",
                "--field",
                "centroid",
                "--field",
                "partial4",
                "--field",
                "analysis_root",
                "--field",
                "smooth_tones",
                str(rows_path),
                str(guitar_rows_path),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"coverage candidate inspector failed with {completed.returncode}\n"
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )

    output = completed.stdout
    require(output, "coverage_candidate_inspection: candidates=3 row_paths=2/2 expanded_ready=0")
    require(
        output,
        "coverage_status_summary expanded_ready=0 expanded_partial=0 still_short=3 total_short_by=12",
    )
    require(
        output,
        "nearest_coverage guitar bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0 selected_samples=1 required_samples=5 short_by=4 :: analysis_root<=0 AND smooth_tones<=1",
    )
    require(
        output,
        "coverage_candidate guitar bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0 observed_samples=4 selected_samples=1 selected_rows=2 need_samples=1 expanded_samples=-3 coverage_status=still_short_by=4 :: analysis_root<=0 AND smooth_tones<=1",
    )
    require(output, "groups _coverage_path/status/quality/guitar_match_kind/support")
    require(output, "chord_miss/pow/different_root/visible1_analysis1_smooth1_rootvis0 rows=2 samples=1")
    require(output, "analysis_root: min=0.000 med=0.000 max=0.000")
    require(output, "smooth_tones: min=1.000 med=1.000 max=1.000")
    require(output, "example recording_id=168_QM1wc status=chord_miss expected_label=Fpow")
    require(
        output,
        "coverage_candidate low-false row_confusion:piano/electronic->guitar observed_samples=4 selected_samples=1 selected_rows=1 need_samples=1 expanded_samples=-3 coverage_status=still_short_by=4 :: centroid>=0.52 AND partial4<=0.018 AND partial4>=0",
    )
    require(output, "groups _coverage_path/status/family/source/first_row/visual_first_row")
    require(output, "hit/piano/electronic/guitar/guitar rows=1 samples=1")
    require(output, "centroid: min=0.550 med=0.550 max=0.550")
    require(output, "partial4: min=0.010 med=0.010 max=0.010")
    require(output, "quick_pattern spectral_level_median=0.133")
    require(output, "example sample_id=organ_1 status=hit family=piano source=electronic")
    require(
        output,
        "coverage_candidate low-false visual_row_confusion:piano/electronic->other observed_samples=2 selected_samples=1 selected_rows=1 need_samples=3 expanded_samples=-1 coverage_status=still_short_by=4 :: adjacent_lower_ratio>=0.006 AND adjacent_upper_ratio<=0 AND bass_score<=0",
    )

    ready_summary = """detector_route_summary: candidates=2 low_false=2 shadow=0 near_miss=0 guitar=0 drum=0 positive_net=2 gain_ge_1=2 source_safe_positive_net=2 actionable=0 coverage_blocked=2
  coverage-blocked candidates need more positive samples before detector changes
    coverage_need low-false row_confusion:piano/electronic->other observed_samples=4 need_samples=1 +rows=4 side_rows=0 net_rows=4 gain_per_side=inf :: partial4>=0.8
    coverage_need low-false row_confusion:piano/electronic->guitar observed_samples=2 need_samples=1 +rows=3 side_rows=0 net_rows=3 gain_per_side=inf :: centroid>=0.5
"""
    ready_rows = [
        row[:]
        for row in rows
    ] + [
        [
            "organ_3",
            "hit",
            "piano",
            "electronic",
            "G5",
            "79",
            "guitar",
            "guitar",
            "G5",
            "79",
            "guitar",
            "0.610",
            "0.010",
            "0.000",
            "0.000",
            "0.000",
            "0.433",
            "0.255",
            "0.649",
            "0.198",
        ],
        [
            "organ_4",
            "hit",
            "piano",
            "electronic",
            "A5",
            "81",
            "guitar",
            "guitar",
            "A5",
            "81",
            "guitar",
            "0.720",
            "0.010",
            "0.000",
            "0.000",
            "0.000",
            "0.533",
            "0.355",
            "0.749",
            "0.298",
        ],
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        summary_path = tmp_path / "detector_summary.txt"
        rows_path = tmp_path / "real_note_rows.tsv"
        summary_path.write_text(ready_summary, encoding="utf-8")
        rows_path.write_text(
            "\n".join(["\t".join(header)] + ["\t".join(row) for row in ready_rows]) + "\n",
            encoding="utf-8",
        )
        ready_completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(summary_path),
                "--limit",
                "2",
                "--examples",
                "0",
                str(rows_path),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if ready_completed.returncode != 0:
            raise AssertionError(
                f"coverage ready candidate inspector failed with {ready_completed.returncode}\n"
                f"stdout:\n{ready_completed.stdout}\nstderr:\n{ready_completed.stderr}"
            )
    ready_output = ready_completed.stdout
    require(ready_output, "coverage_candidate_inspection: candidates=2 row_paths=1/1 expanded_ready=1")
    require(
        ready_output,
        "coverage_status_summary expanded_ready=1 expanded_partial=0 still_short=1 total_short_by=5",
    )
    require(
        ready_output,
        "nearest_coverage low-false row_confusion:piano/electronic->other selected_samples=0 required_samples=5 short_by=5 :: partial4>=0.8",
    )
    first_ready_line = next(
        line for line in ready_output.splitlines() if line.startswith("coverage_candidate ")
    )
    if "row_confusion:piano/electronic->guitar" not in first_ready_line:
        raise AssertionError(f"expanded-ready candidate should be listed first:\n{ready_output}")
    require(ready_output, "coverage_status=expanded_ready :: centroid>=0.5")
    require(ready_output, "coverage_status=still_short_by=5 :: partial4>=0.8")
    print("test_inspect_detector_coverage_candidates: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
