#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_detector_route_report.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {needle!r} in:\n{text}")


def main() -> int:
    report = """candidate rules are attribute selectors; rerun gates
row_confusion:piano/electronic->amb positives=186 samples/636 rows protected_hits=2209 samples/22357 rows foreign_misses=0 samples/0 rows
  positive sample profile: groups=organ_electronic=120,keyboard_electronic=66 sources=piano/electronic=186
  low-false candidate rules:
    debug_conf<=0.542 AND partial3>=2.46 AND partial5<=0.02: pos=23/186 rows=44 neg=15/2209 rows=29 side_rows=29 net_rows=15 gain_per_side=1.52 pos_groups=organ_electronic=14,keyboard_electronic=9 pos_sources=piano/electronic=23 neg_same_source_rows=27 neg_cross_source_rows=2 foreign_cross_source_rows=0 neg_sources=piano/electronic=27,other/acoustic=2
    debug_conf<=0.542 AND partial3>=2.46 AND slope>=0.655: pos=23/186 rows=44 neg=16/2209 rows=29 side_rows=29 net_rows=15 gain_per_side=1.52 neg_same_source_rows=24 neg_cross_source_rows=5 foreign_cross_source_rows=0 neg_sources=piano/electronic=24,other/acoustic=5
  highest-coverage candidate rules:
    debug_conf<=0.542 AND partial3>=2.46 AND partial5<=0.02: pos=23/186 rows=44 neg=15/2209 rows=29 side_rows=29 net_rows=15 gain_per_side=1.52 pos_groups=organ_electronic=14,keyboard_electronic=9 pos_sources=piano/electronic=23 neg_same_source_rows=27 neg_cross_source_rows=2 foreign_cross_source_rows=0 neg_sources=piano/electronic=27,other/acoustic=2
  nearest over-budget single-condition candidate rules:
    slope>=0.203: pos=20/22 rows=47 neg=202/254 rows=616 foreign_miss=75/93 rows=242 side_rows=858 net_rows=-811 gain_per_side=0.05 neg_same_source_rows=0 neg_cross_source_rows=616 foreign_cross_source_rows=242 neg_sources=vocals/example=45 foreign_sources=vocals/other=19
      positive examples:
        sample expected=D#3 debug=D#3 owner=other
ownership_miss:guitar/electronic->piano positives=3 samples/6 rows protected_hits=120 samples/480 rows foreign_misses=0 samples/0 rows
  positive sample profile: groups=guitar_electronic=2,guitar_synth=1 sources=guitar/electronic=3
  low-false candidate rules:
    adjacent_lower_ratio<=0.698 AND partial3>=1.817: pos=2/3 rows=5 neg=0/120 rows=0 side_rows=0 net_rows=5 gain_per_side=inf pos_groups=guitar_electronic=2 pos_sources=guitar/electronic=2 neg_same_source_rows=0 neg_cross_source_rows=0 foreign_cross_source_rows=0
      positive examples:
        guitar_electronic_001 expected=E3/52 debug=E3/52 owner=piano delta=0 reason=hit first_row=piano strongest=piano scores(b/k/g/v/o)=0/1/0/0/0 spec=0.42 pitch=0.71 per=0.81 fit=0.09 cent=0.01 raw_best=E3/92.4 raw_rank=1 ignored=1
    centroid>=0.4 AND partial5<=0.2: pos=1/3 rows=2 neg=0/120 rows=0 side_rows=0 net_rows=2 gain_per_side=inf neg_same_source_rows=0 neg_cross_source_rows=0 foreign_cross_source_rows=0
      positive examples:
        guitar_electronic_002 expected=F3/53 debug=F3/53 owner=piano delta=0 reason=hit first_row=piano strongest=piano spec=0.52 pitch=0.61
octave_displacement:piano/electronic->-12 positives=61 samples/410 rows protected_hits=0 samples/0 rows foreign_misses=0 samples/0 rows
  positive sample profile: groups=organ_electronic=61 sources=piano/electronic=61
  low-false candidate rules:
    debug_delta<=-12 AND noise<=0.121: pos=61/61 rows=410 neg=0/0 rows=0 side_rows=0 net_rows=410 gain_per_side=inf pos_groups=organ_electronic=61 pos_sources=piano/electronic=61 neg_same_source_rows=0 neg_cross_source_rows=0 foreign_cross_source_rows=0
      positive examples:
        organ_electronic_001 expected=A#4/70 debug=A#3/58 owner=amb delta=-12 reason=hit first_row=amb strongest=amb scores(b/k/g/v/o)=0/0.4/0.6/0/0 spec=1 pitch=0.9 per=0.8 fit=0.05 cent=0.2 raw_best=A#3/624 raw_rank=2
route snare->tom positives=492 rows=492 protected_correct=13126 rows=13126
  +24 rows=24 -5 rows=5 foreign=4 rows=4 new-active=0 rows=0 primary-break=4 rows=4 side_rows=13 net_rows=11 gain_per_side=1.85 :: hihat_band>=24.633 AND tom_level>=0.981
  +21 rows=21 -7 rows=7 foreign=6 rows=6 new-active=1 rows=1 primary-break=6 rows=6 side_rows=20 net_rows=1 gain_per_side=1.05 :: hihat_band>=24.633 AND tom_seg<=225.582
route tom->snare positives=4 rows=4 protected_correct=13126 rows=13126
  +4 rows=4 -0 rows=0 foreign=0 rows=0 new-active=0 rows=0 primary-break=0 rows=0 side_rows=0 net_rows=4 gain_per_side=inf :: snare_kick_level_ratio>=3.362 AND tom_snare_body_ratio>=1.824
bucket chord_miss:7:visible3_analysis3_smooth3_rootvis1 positives=6 positive_rows=9 protected_hits=38
  +3 rows=3 -0 rows=0 :: evidence_source=raw
    030_rpswc@93.498s expected=A#7 guitar=E=Esus2 support=visible3_analysis3_smooth3_rootvis1 raw(root/third/fifth)=0.25/0.10/1.00 analysis=E,F,F#,G#,A,A#,B visible=E,F,F#,G#,A,A#,B
  +5 rows=6 -1 rows=1 :: evidence_class=raw_quality_gap
    031_rpswc@94.100s expected=A#7 guitar=A#7 support=visible3_analysis3_smooth3_rootvis1 raw(root/third/fifth)=1.00/0.70/0.80 analysis=A#,D,F,G# visible=A#,D,F,G#
compact route summary
  routes=2 routes_with_extras=2 safe_simulation_routes=2 safe_simulation_extra_hits=24
  safe_threshold_routes=1 no_safe_threshold_routes=1 safe_threshold_extra_hits=23 safe_threshold_protected_hits=0
  other->same-pitch vocals extras=694/310 protected=11/9 simulation=runtime_other_vocal_measured:23/0 threshold=protected=0/11 extras=23/694 min_shadow_score=0.24 score_ratio=0.15 level_ratio=0.48 net_hits=23 gain_per_protected=inf simulation_net_hits=23 simulation_gain_per_protected=inf guarded=runtime_other_vocal_cpp_guarded:0/0
  piano->same-pitch bass extras=2218/520 protected=487/115 simulation=weak_target_shadow_owned:1/0 threshold=none simulation_net_hits=1 simulation_gain_per_protected=inf
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "16"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

    output = result.stdout
    require(
        output,
        "detector_route_summary: candidates=13 low_false=5 shadow=2 near_miss=1 guitar=2 drum=3 positive_net=12 gain_ge_1=12 source_safe_positive_net=10 actionable=5 coverage_blocked=2",
    )
    require(
        output,
        "blocked-reason summary cross_source_rows=3 low_samples<5=3 diagnostic_octave_displacement=1 low_rows<5=1 missing_quality_tone=1 negative_net=1",
    )
    require(
        output,
        "coverage-blocked candidates need more positive samples before detector changes",
    )
    require(
        output,
        "coverage_need low-false ownership_miss:guitar/electronic->piano observed_samples=2 need_samples=3 +rows=5 side_rows=0 net_rows=5 gain_per_side=inf :: adjacent_lower_ratio<=0.698 AND partial3>=1.817",
    )
    require(
        output,
        "example guitar_electronic_001 expected=E3/52 debug=E3/52 owner=piano delta=0 reason=hit first_row=piano strongest=piano scores(b/k/g/v/o)=0/1/0/0/0 spec=0.42 pitch=0.71 per=0.81 fit=0.09 cent=0.01 raw_best=E3/92.4 raw_rank=1",
    )
    require(output, "  coverage-route clusters")
    require(
        output,
        "coverage_route ownership_miss:guitar/electronic->piano candidates=2 best_observed_samples=2 min_need_samples=3 total_net_rows=7 examples=guitar_electronic_001,guitar_electronic_002 groups=guitar_electronic=2 sources=guitar/electronic=2 bucket_groups=guitar_electronic=2,guitar_synth=1 bucket_sources=guitar/electronic=3",
    )
    require(
        output,
        "low-false row_confusion:piano/electronic->amb +samples=23 +rows=44 -samples=15 -rows=29 foreign_rows=0 side_rows=29 net_rows=15 gain_per_side=1.52 neg_same_source_rows=27 neg_cross_source_rows=2 foreign_cross_source_rows=0 pos_groups=organ_electronic=14,keyboard_electronic=9 pos_sources=piano/electronic=23 neg_sources=piano/electronic=27,other/acoustic=2",
    )
    require(output, "blocked_by=cross_source_rows=2")
    require(
        output,
        "shadow other->same-pitch vocals +rows=23 protected_rows=0 side_rows=0 net_rows=23 gain_per_side=inf :: threshold min_shadow_score=0.24 score_ratio=0.15 level_ratio=0.48; simulation=runtime_other_vocal_measured:23/0; guarded=runtime_other_vocal_cpp_guarded:0/0",
    )
    require(
        output,
        "shadow piano->same-pitch bass +rows=1 protected_rows=0 side_rows=0 net_rows=1 gain_per_side=inf :: simulation weak_target_shadow_owned",
    )
    require(
        output,
        "guitar bucket chord_miss:7:visible3_analysis3_smooth3_rootvis1 +recordings=5 +rows=6 -recordings=1 -rows=1 side_rows=1 net_rows=5 gain_per_side=6.00 :: evidence_class=raw_quality_gap",
    )
    require(
        output,
        "guitar bucket chord_miss:7:visible3_analysis3_smooth3_rootvis1 +recordings=3 +rows=3 -recordings=0 -rows=0 side_rows=0 net_rows=3 gain_per_side=inf blocked_by=missing_quality_tone,low_samples<5 :: evidence_source=raw",
    )
    require(
        output,
        "example 031_rpswc@94.100s expected=A#7 guitar=A#7 support=visible3_analysis3_smooth3_rootvis1 raw(root/third/fifth)=1.00/0.70/0.80 analysis=A#,D,F,G# visible=A#,D,F,G#",
    )
    require(
        output,
        "near-miss row_confusion:piano/electronic->amb +samples=20 +rows=47 -samples=202 -rows=616 foreign_rows=242 side_rows=858 net_rows=-811 gain_per_side=0.05 neg_same_source_rows=0 neg_cross_source_rows=616 foreign_cross_source_rows=242 neg_sources=vocals/example=45 foreign_sources=vocals/other=19",
    )
    require(output, "blocked_by=negative_net,cross_source_rows=858")
    require(
        output,
        "low-false octave_displacement:piano/electronic->-12 +samples=61 +rows=410 -samples=0 -rows=0 foreign_rows=0 side_rows=0 net_rows=410 gain_per_side=inf pos_groups=organ_electronic=61 pos_sources=piano/electronic=61 blocked_by=diagnostic_octave_displacement :: debug_delta<=-12 AND noise<=0.121",
    )
    require(
        output,
        "drum route snare->tom +rows=24 -rows=5 foreign_rows=4 new_active_rows=0 primary_break_rows=4 side_rows=13 net_rows=11 gain_per_side=1.85",
    )
    require(
        output,
        "drum route tom->snare +rows=4 -rows=0 foreign_rows=0 new_active_rows=0 primary_break_rows=0 side_rows=0 net_rows=4 gain_per_side=inf blocked_by=low_rows<5 :: snare_kick_level_ratio>=3.362 AND tom_snare_body_ratio>=1.824",
    )
    if output.index("shadow other->same-pitch vocals") > output.index("drum route snare->tom"):
        raise AssertionError(f"expected highest-net source-safe candidate first:\n{output}")
    if output.index("drum route snare->tom") > output.index("low-false row_confusion"):
        raise AssertionError(f"expected source-safe drum routes before cross-source-risky note routes:\n{output}")
    if output.index("guitar bucket chord_miss") > output.index("low-false row_confusion"):
        raise AssertionError(f"expected source-safe guitar routes before cross-source-risky note routes:\n{output}")
    if output.index("shadow other->same-pitch vocals") > output.index("near-miss row_confusion"):
        raise AssertionError(f"expected positive-net shadow candidates before near-miss routes:\n{output}")
    if output.index("drum route snare->tom") > output.index("near-miss row_confusion"):
        raise AssertionError(f"expected positive-net drum candidates before negative-net near misses:\n{output}")

    weak_row_report = """ownership_miss:guitar/acoustic->bass positives=0 samples/0 rows protected_hits=100 samples/100 rows foreign_misses=0 samples/0 rows
weak_visual_expected_row:piano/electronic->lit_octave@2 positives=7 samples/11 rows protected_hits=100 samples/100 rows foreign_misses=0 samples/0 rows
  positive sample profile: groups=organ_electronic=7 sources=piano/electronic=7
  low-false candidate rules:
    partial4>=2.0 AND noise>=0.3: pos=6/7 rows=8 neg=0/100 rows=0 side_rows=0 net_rows=8 gain_per_side=inf pos_groups=organ_electronic=6 pos_sources=piano/electronic=6 neg_same_source_rows=0 neg_cross_source_rows=0 foreign_cross_source_rows=0
      positive examples:
        organ_electronic_001 expected=C3/48 debug=C3/48 owner=other delta=0 reason=hit first_row=other strongest=other spec=0.52 pitch=0.61
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(weak_row_report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "4"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    weak_row_output = result.stdout
    require(
        weak_row_output,
        "low-false weak_visual_expected_row:piano/electronic->lit_octave@2 +samples=6 +rows=8 -samples=0 -rows=0 foreign_rows=0 side_rows=0 net_rows=8 gain_per_side=inf",
    )
    if "low-false ownership_miss:guitar/acoustic->bass +samples=6" in weak_row_output:
        raise AssertionError(
            "weak-row candidates must not inherit the preceding zero-positive ownership section:\n"
            + weak_row_output
        )

    low_quality_report = """bucket chord_miss:maj:visible2_analysis2_smooth2_rootvis1 positives=5 positive_rows=5 protected_hits=465
  +5 rows=5 -0 rows=0 :: analysis_third<=0 AND display_primary_analysis_fifth<=0
    clips_isolated-chords_A_A_acoustic_guitar_fender_fa_series_1@3.216s expected=A guitar=E=Apow support=visible2_analysis2_smooth2_rootvis1 raw(root/third/fifth)=1.00/0.02/0.42 analysis=E,A visible=E,A
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(low_quality_report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "8"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    low_quality_output = result.stdout
    require(
        low_quality_output,
        "detector_route_summary: candidates=1 low_false=0 shadow=0 near_miss=0 guitar=1 drum=0 positive_net=1 gain_ge_1=1 source_safe_positive_net=1 actionable=0 coverage_blocked=0",
    )
    require(low_quality_output, "blocked-reason summary missing_quality_tone=1")
    require(low_quality_output, "blocked_by=missing_quality_tone")

    extended_quality_report = """bucket chord_miss:maj7:visible3_analysis3_smooth3_rootvis1 positives=9 positive_rows=12 protected_hits=0
  +9 rows=12 -0 rows=0 :: analysis_tones<=3 AND melodic_probe_third>=0.2 AND probe_third<=0.059
    guitar_techs_chords_P1_chords_micamp_drop3_maj7_0021_0297@0.750s expected=F#maj7 guitar=F#=C#=F#pow support=visible3_analysis3_smooth3_rootvis1 raw(root/third/fifth)=0.24/0.03/0.39 analysis=C#,F,F# visible=C#,F,F#
bucket chord_miss:m6/m7b5:visible3_analysis3_smooth3_rootvis1 positives=12 positive_rows=16 protected_hits=0
  +12 rows=16 -0 rows=0 :: analysis_fifth<=0 AND analysis_third<=0
    guitar_techs_chords_P1_chords_directinput_drop3_m7b5_0072_0619@0.750s expected=Gm7b5/A#m6 guitar=C#=C#add9 support=visible3_analysis3_smooth3_rootvis1 raw(root/third/fifth)=0.45/0.20/0.00 analysis=C#,D#,F,G,G# visible=C#,F,G
bucket chord_miss:m:visible0_analysis0_smooth0_rootvis0 positives=36 positive_rows=44 protected_hits=0
  +36 rows=44 -0 rows=0 :: analysis_pc_count<=0
    guitar_techs_chords_P1_chords_directinput_drop3_maj7_0027_0214@0.750s expected=C#m guitar=-- support=visible0_analysis0_smooth0_rootvis0 raw(root/third/fifth)=0.13/1.00/0.38 analysis=-- visible=--
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(extended_quality_report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "8"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    extended_quality_output = result.stdout
    require(
        extended_quality_output,
        "detector_route_summary: candidates=3 low_false=0 shadow=0 near_miss=0 guitar=3 drum=0 positive_net=3 gain_ge_1=3 source_safe_positive_net=3 actionable=0 coverage_blocked=0",
    )
    require(
        extended_quality_output,
        "blocked-reason summary missing_quality_tone=2 missing_note_evidence=1",
    )
    require(extended_quality_output, "chord_miss:maj7")
    require(extended_quality_output, "blocked_by=missing_quality_tone")
    require(extended_quality_output, "chord_miss:m6/m7b5")
    require(extended_quality_output, "chord_miss:m:visible0")
    require(extended_quality_output, "blocked_by=missing_note_evidence")

    power_note_evidence_report = """bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0 positives=4 positive_rows=7 protected_hits=0
  +4 rows=7 -0 rows=0 :: analysis_root<=0
    clips_isolated-chords_Cpow_1@0.750s expected=Cpow guitar=Gpow support=visible1_analysis1_smooth1_rootvis0 raw(root/third/fifth)=0.00/0.00/1.00 analysis=G visible=G
bucket chord_miss:pow:visible2_analysis2_smooth2_rootvis1 positives=4 positive_rows=4 protected_hits=0
  +4 rows=4 -0 rows=0 :: analysis_fifth>=0.32 AND analysis_tones<=2
    clips_isolated-chords_Cpow_2@0.750s expected=Cpow guitar=-- support=visible2_analysis2_smooth2_rootvis1 raw(root/third/fifth)=1.00/0.00/1.00 analysis=C,G visible=C,G
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(power_note_evidence_report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "8"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    power_note_evidence_output = result.stdout
    require(
        power_note_evidence_output,
        "detector_route_summary: candidates=2 low_false=0 shadow=0 near_miss=0 guitar=2 drum=0 positive_net=2 gain_ge_1=2 source_safe_positive_net=2 actionable=0 coverage_blocked=1",
    )
    require(
        power_note_evidence_output,
        "blocked-reason summary low_samples<5=2 missing_note_evidence=1",
    )
    require(
        power_note_evidence_output,
        "coverage_need guitar bucket chord_miss:pow:visible2_analysis2_smooth2_rootvis1 observed_samples=4 need_samples=1",
    )
    if "coverage_need guitar bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0" in power_note_evidence_output:
        raise AssertionError(
            "power-chord routes without root/fifth evidence must not be reported as coverage needs:\n"
            + power_note_evidence_output
        )
    require(
        power_note_evidence_output,
        "bucket chord_miss:pow:visible1_analysis1_smooth1_rootvis0 +recordings=4 +rows=7 -recordings=0 -rows=0 side_rows=0 net_rows=7 gain_per_side=inf blocked_by=missing_note_evidence,low_samples<5 :: analysis_root<=0",
    )

    veto_report = """compact route summary
  routes=1 routes_with_extras=1 safe_simulation_routes=0 safe_simulation_extra_hits=0
  safe_threshold_routes=1 no_safe_threshold_routes=0 safe_threshold_extra_hits=3 safe_threshold_protected_hits=0
  other->same-pitch vocals extras=737/326 protected=25/13 simulation=none threshold=protected=0/25 extras=3/737 min_shadow_score=0.24 score_ratio=0.15 level_ratio=0.35 net_hits=3 gain_per_protected=inf guarded=runtime_other_vocal_cpp_guarded:0/0
compact route summary
  routes=1 routes_with_extras=1 safe_simulation_routes=0 safe_simulation_extra_hits=0
  safe_threshold_routes=0 no_safe_threshold_routes=1 safe_threshold_extra_hits=0 safe_threshold_protected_hits=0
  other->same-pitch vocals extras=737/326 protected=25/13 simulation=none threshold=none guarded=runtime_other_vocal_cpp_guarded:0/0
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(veto_report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "8"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    veto_output = result.stdout
    require(
        veto_output,
        "detector_route_summary: candidates=0 low_false=0 shadow=0 near_miss=0 guitar=0 drum=0 positive_net=0 gain_ge_1=0 source_safe_positive_net=0 actionable=0 coverage_blocked=0",
    )
    require(veto_output, "  --")

    print("test_summarize_detector_route_report: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
