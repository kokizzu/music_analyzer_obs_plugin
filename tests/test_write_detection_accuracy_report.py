#!/usr/bin/env python3
"""Regression checks for the tracked accuracy dashboard generator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "write_detection_accuracy_report.py"
SPEC = importlib.util.spec_from_file_location("write_detection_accuracy_report", MODULE_PATH)
assert SPEC and SPEC.loader
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


HEADER = "\t".join(("sample_id", "family", "detected", "detected_expected_row", "first_row", "visual_first_row"))


class DetectionAccuracyReportTest(unittest.TestCase):
    def test_mdb_rim_coverage_parses_class_specific_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "mdb_rim_coverage.txt"
            audit.write_text("mdb_rim_coverage: detected=0/1\n", encoding="utf-8")
            self.assertEqual(REPORT.mdb_rim_coverage(audit), (0, 1))

    def test_fsd50k_rim_metadata_audit_accepts_zero_label_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "fsd50k_rim_metadata.txt"
            audit.write_text(
                "fsd50k_rim_metadata: rimshot_labelled_rows=0 pure_rimshot_candidates=0 permissive_cc_candidates=0 dev=0 eval=0\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.fsd50k_rim_metadata_audit(audit), (0, 0, 0))

    def test_visual_expected_pitch_lit_matches_pitch_class_at_threshold(self) -> None:
        self.assertTrue(
            REPORT.visual_expected_pitch_lit(
                {"expected_midi": "44", "other_visual_notes": "G#3:0.25"}, "other"
            )
        )
        self.assertFalse(
            REPORT.visual_expected_pitch_lit(
                {"expected_midi": "44", "other_visual_notes": "G#3:0.24"}, "other"
            )
        )

    def test_expected_exact_note_detected_requires_the_annotated_octave(self) -> None:
        rows = [{"expected_midi": "50", "other_notes": "D4:1.00,A4:1.00"}]
        self.assertFalse(REPORT.expected_exact_note_detected(rows, "other"))
        rows[0]["other_notes"] = "D3:0.20,D4:1.00,A4:1.00"
        self.assertTrue(REPORT.expected_exact_note_detected(rows, "other"))
        self.assertFalse(
            REPORT.visual_expected_pitch_lit(
                {"expected_midi": "44", "other_visual_notes": "A3:1.00"}, "other"
            )
        )

    def test_load_samples_accepts_long_generated_evidence_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "attributes.tsv"
            source.write_text(
                HEADER + "\n" + f"{'s' * 140000}\tvocals\t1\t1\tvocals\tvocals\n",
                encoding="utf-8",
            )
            self.assertEqual(len(REPORT.load_samples(source)), 1)

    def test_electronic_piano_guitar_audit_requires_two_independent_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "electronic_piano_guitar_route_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "matched rows=15 samples=10",
                        "compare rows=0 samples=0 path=maps.tsv",
                        "compare rows=2 samples=2 path=maestro.tsv",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.electronic_piano_guitar_route_audit(audit), (10, 1, 2))

    def test_scms_vocal_other_audit_counts_three_independent_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "scms_vocal_other_route_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "matched rows=6 samples=5",
                        "compare rows=0 samples=0 path=vocadito.tsv",
                        "compare rows=2 samples=1 path=vocalset.tsv",
                        "compare rows=0 samples=0 path=mir1k.tsv",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.scms_vocal_other_route_audit(audit), (5, 1, 3))

    def test_tenor_sax_piano_audit_requires_independent_recurrence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "tenor_sax_piano_route_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "matched rows=5 samples=3",
                        "compare rows=0 samples=0 path=iowa.tsv",
                        "compare rows=0 samples=0 path=tinysol.tsv",
                        "compare rows=0 samples=0 path=real-a2s.tsv",
                        "compare rows=0 samples=0 path=urmp.tsv",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.tenor_sax_piano_route_audit(audit), (3, 0, 4))

    def test_urmp_good_sounds_shared_sax_audit_records_zero_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "urmp_good_sounds_sax_shared_patterns.txt"
            audit.write_text("shared_sax_candidates=0\n", encoding="utf-8")
            self.assertEqual(REPORT.urmp_good_sounds_sax_shared_pattern_audit(audit), 0)

    def test_cross_corpus_octave_audit_records_zero_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "octave_correction_cross_corpus_audit.txt"
            audit.write_text("shared_octave_correction_candidates=0\n", encoding="utf-8")
            self.assertEqual(REPORT.octave_correction_cross_corpus_audit(audit), 0)

    def test_dominant_seventh_audit_requires_independent_zero_regression_support(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "dominant_seventh_extension_audit.txt"
            audit.write_text(
                "dominant_seventh_extension: supported_corpora=0/4 regressions=3\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.dominant_seventh_extension_audit(audit), (0, 4, 3))

    def test_guitarset_attributes_report_pitch_and_chord_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            attributes = Path(temporary) / "guitarset_attributes.tsv"
            attributes.write_text(
                "guitar_note_hits\texpected_note_count\texpected_chords\tchord_hit\n"
                "3\t4\tC\t1\n"
                "2\t3\tDm\t0\n"
                "1\t1\t--\t0\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.guitarset_attribute_audit(attributes), (6, 8, 1, 2))

    def test_same_root_guitar_quality_audit_requires_cross_corpus_support(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "same_root_guitar_quality_audit.txt"
            audit.write_text(
                "same_root_guitar_quality: best_floor=0.040 supported_corpora=0/4 regressions=169 common_zero_regression=0\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.same_root_guitar_quality_audit(audit), (0.04, 0, 4, 169, 0))

    def test_owner_classifier_loco_audit_requires_all_held_out_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "owner_classifier_loco_audit.txt"
            audit.write_text(
                "owner_classifier_loco: improved_corpora=1/2 current=10672/33568 model=12030/33568\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.owner_classifier_loco_audit(audit), (1, 2, 10672, 12030, 33568))

    def test_owner_score_calibration_loco_audit_requires_all_held_out_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "owner_score_calibration_loco_audit.txt"
            audit.write_text(
                "owner_score_calibration_loco: improved_corpora=5/9 current=12807/61501 model=12211/61501\n",
                encoding="utf-8",
            )
            self.assertEqual(
                REPORT.owner_score_calibration_loco_audit(audit),
                (5, 9, 12807, 12211, 61501),
            )

    def test_beat_this_tempo_rows_use_the_offline_error_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            diagnostic = Path(temporary) / "beat_this.log"
            diagnostic.write_text(
                "Beat This tempo diag\tid=1\texpected=120.00\traw=120.00\terror=0.00\n"
                "Beat This tempo diag\tid=2\texpected=90.00\traw=180.00\terror=90.00\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.beat_this_tempo_diagnostic_counts(diagnostic), (1, 2))

    def test_permissive_tracker_rows_apply_the_certainty_floor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            diagnostic = Path(temporary) / "btt.log"
            diagnostic.write_text(
                "BTT tempo diag\tid=1\texpected=120.00\traw=120.00\tconfidence=0.80\terror=0.00\n"
                "BTT tempo diag\tid=2\texpected=90.00\traw=180.00\tconfidence=0.80\terror=90.00\n"
                "BTT tempo diag\tid=3\texpected=100.00\traw=100.00\tconfidence=0.40\terror=0.00\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.permissive_tracker_tempo_counts(diagnostic), (2, 3))
            self.assertEqual(REPORT.permissive_tracker_tempo_counts(diagnostic, 0.75), (1, 2))

    def test_polyphonic_candidate_capacity_audit_tracks_saturation_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "polyphonic_candidate_capacity_audit.txt"
            audit.write_text(
                "polyphonic_candidate_capacity: capacity_limited_corpora=0/3 "
                "missing_pitch_windows=427 saturation_explains_missing=0\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.polyphonic_candidate_capacity_audit(audit), (0, 3, 427, 0))

    def test_29k_drum_measurement_parses_tom_and_ride_primary_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            measurement = Path(temporary) / "29k.log"
            measurement.write_text(
                "analyzer_drum_samples: ok (usable 12, tom recall 4/6 primary 3/6 precision 4/7 false 3, ride recall 5/6 primary 4/6 precision 5/8 false 3)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                REPORT.samples29k_drum_counts(measurement),
                {"tom": (4, 6, 3), "ride": (5, 6, 4)},
            )

    def test_29k_primary_attribute_rows_require_the_expected_tsv_header(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            attributes = Path(temporary) / "29k-primary.tsv"
            attributes.write_text("sample\texpected\tgot\tenergy_low\n", encoding="utf-8")
            self.assertEqual(REPORT.samples29k_primary_attributes_ready(attributes), 1)
            attributes.write_text("expected\tgot\n", encoding="utf-8")
            self.assertEqual(REPORT.samples29k_primary_attributes_ready(attributes), 0)
            self.assertEqual(REPORT.samples29k_primary_attributes_ready(None), 0)

    def test_drum_recovery_candidate_audit_requires_cross_real_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "recovery.txt"
            audit.write_text(
                "drum_recovery_candidate_audit: corpora=2 missed_events=70 "
                "cross_real_zero_false_candidates=3\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.drum_recovery_candidate_audit(audit), (2, 70, 3))

    def test_violin_guitar_audit_requires_two_independent_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "violin_guitar_route_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "matched rows=4 samples=4",
                        "compare rows=0 samples=0 path=iowa.tsv",
                        "compare rows=0 samples=0 path=kraisler.tsv",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(REPORT.violin_guitar_route_audit(audit), (4, 0, 2))

    def test_guitar_primary_display_audit_requires_both_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "guitar_chord_primary_display_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "source=Guitar_Chord_Mix",
                        "guitar_chord: primary=400/511 later=85 miss=26",
                        "same_root_extension_primary_runtime_safe_rules:",
                        "  --",
                        "comparison=GAPS_full",
                        "guitar_chord: primary=176/540 later=185 miss=179",
                        "same_root_extension_primary_runtime_safe_rules:",
                        "  +12 protected_false=0 neutral=5 :: suffix=7",
                        "  +8 protected_false=0 neutral=3 :: suffix=7",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(
                REPORT.guitar_chord_primary_display_audit(audit),
                ((400, 511, 26), (176, 540, 179), 0, 2),
            )

    def test_guitar_tone_recovery_audit_tracks_all_three_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = Path(temporary) / "guitar_chord_tone_recovery_audit.txt"
            audit.write_text(
                "\n".join(
                    (
                        "tone=minor-third",
                        "gaps.tsv: candidates=0 recoveries=0 false=0",
                        "mix.tsv: candidates=1 recoveries=1 false=0",
                        "techs.tsv: candidates=0 recoveries=0 false=0",
                        "tone=major-third",
                        "gaps.tsv: candidates=1 recoveries=1 false=0",
                        "mix.tsv: candidates=2 recoveries=2 false=0",
                        "techs.tsv: candidates=6 recoveries=0 false=6",
                        "tone=minor-fifth",
                        "gaps.tsv: candidates=0 recoveries=0 false=0",
                        "mix.tsv: candidates=0 recoveries=0 false=0",
                        "techs.tsv: candidates=0 recoveries=0 false=0",
                        "tone=major-fifth",
                        "gaps.tsv: candidates=0 recoveries=0 false=0",
                        "mix.tsv: candidates=0 recoveries=0 false=0",
                        "techs.tsv: candidates=0 recoveries=0 false=0",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(
                REPORT.guitar_chord_tone_recovery_audit(audit),
                {
                    "minor-third": (1, 0, 3),
                    "major-third": (2, 6, 3),
                    "minor-fifth": (0, 0, 3),
                    "major-fifth": (0, 0, 3),
                },
            )

    def test_render_reports_global_and_family_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "attributes.tsv"
            source.write_text(
                "\n".join(
                    (
                        HEADER,
                        "a\tpiano\t1\t1\tpiano\tpiano",
                        "b\tguitar\t1\t1\tpiano\tguitar",
                        "c\tguitar\t0\t0\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            chords = Path(temporary) / "guitar_chord_mix_attributes.tsv"
            chords.write_text(
                "\n".join(
                    (
                        "\t".join(("expected_chords", "chord_hit", "guitar_chord", "expected_pitch_class_count", "guitar_note_hits")),
                        "C\t1\tC\t3\t3",
                        "Dm\t0\tD\t3\t2",
                        "Apow\t0\tA\t2\t1",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            vocal_full_mix = Path(temporary) / "vocadito_full_mix_attributes.tsv"
            vocal_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "v1\tvocals\t1\t1\tvocals\tvocals",
                        "v2\tvocals\t1\t1\tpiano\tvocals",
                        "v3\tvocals\t1\t0\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            vocalset_full_mix = Path(temporary) / "vocalset_full_mix_attributes.tsv"
            vocalset_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "vs1\tvocals\t1\t1\tvocals\tvocals",
                        "vs2\tvocals\t1\t1\tpiano\tvocals",
                        "vs3\tvocals\t0\t0\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            good_sounds_full_mix = Path(temporary) / "good_sounds_full_mix_attributes.tsv"
            good_sounds_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "gs1\tbass\t1\t1\tbass\tbass",
                        "gs2\tother\t1\t1\tpiano\tother",
                        "gs3\tother\t0\t0\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            irmas_labelled = Path(temporary) / "irmas_labelled_attributes.tsv"
            irmas_labelled.write_text(
                "sample_id\tfamily\tdetected\tdetected_expected_row\tfirst_row\tvisual_first_row"
                "\trow_grid\tbuffer_strongest_row\tbuffer_visual_strongest_row\n"
                "irmas-piano\tpiano\t1\t1\tpiano\tpiano\t1\tpiano\tpiano\n"
                "irmas-guitar\tguitar\t1\t0\tpiano\tguitar\t0\tpiano\tguitar\n",
                encoding="utf-8",
            )
            medley_solos_attributes = Path(temporary) / "medley_solos_attributes.tsv"
            medley_solos_attributes.write_text(
                "\n".join(
                    (
                        "\t".join(("sample_id", "family", "instrument", "expected_row_hit")),
                        "m1\tother\tclarinet\t0",
                        "m1\tother\tclarinet\t1",
                        "m2\tvocals\tfemale singer\t0",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            focused_vocalset_clean_vowel = Path(temporary) / "vocalset_clean_vowel_attributes.tsv"
            focused_vocalset_clean_vowel.write_text(
                "\n".join(
                    (
                        HEADER,
                        "c5\tvocals\t1\t1\tvocals\tvocals",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            pitch_shifted_violin = Path(temporary) / "pitch_shifted_violin_attributes.tsv"
            pitch_shifted_violin.write_text(
                "\n".join(
                    (
                        HEADER,
                        "pv1\tother\t1\t1\tother\tother",
                        "pv2\tother\t1\t1\tpiano\tother",
                        "pv3\tother\t0\t0\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            iowa_orchestra_full = Path(temporary) / "iowa_orchestra_full_attributes.tsv"
            iowa_orchestra_full.write_text(
                "\n".join(
                    (
                        "\t".join((
                            "sample_id", "family", "detected", "detected_expected_row",
                            "first_row", "visual_first_row", "expected_midi", "bass_notes",
                            "guitar_notes", "piano_notes", "vocal_notes", "other_notes",
                        )),
                        "io1\tother\t1\t1\tother\tother\t60\t\t\t\t\tC4:1.00",
                        "io2\tbass\t1\t1\tbass\tbass\t36\tC2:1.00\t\t\t\t",
                        "io3\tother\t1\t1\tother\tother\t50\t\t\t\t\tD4:1.00",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            iowa_sax_full_mix = Path(temporary) / "iowa_sax_full_mix_attributes.tsv"
            iowa_sax_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "is1\tother\t1\t1\tother\tother",
                        "is2\tother\t1\t1\tguitar\tother",
                        "is3\tother\t1\t1\tguitar\tguitar",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            iowa_piano_full_mix = Path(temporary) / "iowa_piano_full_mix_attributes.tsv"
            iowa_piano_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "ip1\tpiano\t1\t1\tpiano\tpiano",
                        "ip2\tpiano\t1\t1\tguitar\tpiano",
                        "ip3\tpiano\t1\t1\tguitar\tguitar",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            tinysol_wind_exact = Path(temporary) / "tinysol_wind_exact_attributes.tsv"
            tinysol_wind_exact.write_text(
                "\n".join(
                    (
                        "\t".join((
                            "sample_id", "family", "source", "detected", "detected_expected_row",
                            "first_row", "visual_first_row", "expected_midi", "other_notes",
                        )),
                        "two1\tother\toboe\t1\t1\tother\tother\t72\tC5:1.00",
                        "tt1\tother\ttrombone\t1\t1\tother\tother\t40\tE2:1.00",
                        "tt2\tother\ttrombone\t1\t1\tother\tother\t53\tF2:1.00",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            tinysol_sax_full_mix = Path(temporary) / "tinysol_sax_full_mix_attributes.tsv"
            tinysol_sax_full_mix.write_text(
                "\n".join(
                    (
                        HEADER,
                        "ts1\tother\t1\t1\tother\tother",
                        "ts2\tother\t1\t1\tpiano\tpiano",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            real_a2s_tenor_scale = Path(temporary) / "real_a2s_tenor_scale_attributes.tsv"
            real_a2s_tenor_scale.write_text(
                "\n".join(
                    (
                        "\t".join((
                            "sample_id", "family", "detected", "detected_expected_row",
                            "first_row", "visual_first_row", "expected_midi", "other_notes",
                        )),
                        "a2s1\tother\t1\t1\tother\tother\t53\tF3:1.00",
                        "a2s2\tother\t1\t0\tpiano\tpiano\t55\t",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            urmp_sax_exact = Path(temporary) / "urmp_sax_exact_attributes.tsv"
            urmp_sax_exact.write_text(
                "\n".join(
                    (
                        "\t".join((
                            "sample_id", "family", "detected", "detected_expected_row",
                            "first_row", "visual_first_row", "expected_midi", "other_notes",
                        )),
                        "urmp1\tother\t1\t1\tother\tother\t60\tC4:1.00",
                        "urmp2\tother\t1\t1\tother\tother\t62\tC4:1.00",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            urmp_sax_full_mix = Path(temporary) / "urmp_sax_full_mix_attributes.tsv"
            urmp_sax_full_mix.write_text(
                "\n".join(
                    (
                        "\t".join((
                            "sample_id", "family", "detected", "detected_expected_row",
                            "first_row", "visual_first_row", "expected_midi", "other_notes",
                        )),
                        "urmpfm1\tother\t1\t1\tother\tother\t60\tC4:1.00",
                        "urmpfm2\tother\t1\t0\tpiano\tpiano\t62\tD4:1.00",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            bach10_0 = Path(temporary) / "bach10_0.out"
            bach10_0.write_text(
                "analyzer_musicnet: 20 checks passed (recordings 3/10, windows 12, note hits "
                "45/48, chord hits 9/12, simple chord hits 9/12 75.00%)\n",
                encoding="utf-8",
            )
            bach10_1 = Path(temporary) / "bach10_1.out"
            bach10_1.write_text(
                "analyzer_musicnet: 20 checks passed (recordings 2/10, windows 8, note hits "
                "29/32, chord hits 5/8, simple chord hits 7/8 87.50%)\n",
                encoding="utf-8",
            )
            musicnet = Path(temporary) / "musicnet.out"
            musicnet.write_text(
                "analyzer_musicnet: 5/20 checks failed (recordings 20/330, windows 80, note hits "
                "210/300, chord hits 40/80, simple chord hits 52/80 65.00%)\n",
                encoding="utf-8",
            )
            maps = Path(temporary) / "maps.out"
            maps.write_text(
                "analyzer_maestro: 12 checks passed (recordings 2/80, windows 4, read failures 0, "
                "no-candidate recordings 0, unusable 0, note hits 9/12, chord hits 2/4, "
                "keyboard precision 75.00%, keyboard recall 75.00%, F1 75.00%, contamination 0.00% (0/12), "
                "false non-keyboard windows 0.00% (0/4), ambiguous 0/12, row leaks bass/guitar/vocal/other 0/0/0/0, "
                "tp/fp/fn 9/3/3, keyboard chord precision 50.00%, keyboard chord recall 50.00%, F1 50.00%, "
                "tp/fp/fn 2/2/2, active notes min/avg/max 2/3.00/4, pitch classes min/avg/max 2/3.00/4)\n",
                encoding="utf-8",
            )
            maps_attributes = Path(temporary) / "maps_attributes.tsv"
            maps_attributes.write_text(
                "\n".join(
                    (
                        "expected_chords\tchord_hit\tmissing_pcs\tkeyboard_chord",
                        "C\t0\t\t--",
                        "Dm\t0\tF\tD",
                        "E\t1\t\tE",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            drum = Path(temporary) / "drum_full_gate.out"
            drum.write_text(
                "analyzer_drum_samples: primary matrix\n"
                "  expected kick  kick=8 snare=1 hihat=0 crash=0 tom=1 ride=0 rim=0 ambiguous=0 none=0\n"
                "  expected snare kick=1 snare=7 hihat=0 crash=0 tom=2 ride=0 rim=0 ambiguous=0 none=0\n"
                "  expected hihat kick=0 snare=1 hihat=6 crash=1 tom=0 ride=1 rim=0 ambiguous=0 none=1\n"
                "  expected crash kick=0 snare=0 hihat=1 crash=5 tom=0 ride=2 rim=0 ambiguous=1 none=1\n"
                "  expected tom   kick=2 snare=1 hihat=0 crash=0 tom=7 ride=0 rim=0 ambiguous=0 none=0\n"
                "  expected ride  kick=0 snare=0 hihat=2 crash=1 tom=0 ride=6 rim=0 ambiguous=0 none=1\n"
                "  expected rim   kick=0 snare=2 hihat=1 crash=0 tom=1 ride=0 rim=5 ambiguous=1 none=0\n",
                encoding="utf-8",
            )
            hf_drum_outputs = []
            for expected in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim"):
                shard = Path(temporary) / f"hf_{expected}.out"
                competing = "snare" if expected != "snare" else "kick"
                shard.write_text(
                    "analyzer_drum_samples: primary matrix\n"
                    f"  expected {expected}  {expected}=8 {competing}=1 ambiguous=1 none=0\n",
                    encoding="utf-8",
                )
                hf_drum_outputs.append(shard)
            star_drums = Path(temporary) / "star_drums_misses.log.summary"
            star_drums.write_text(
                "analyzer_egmd: 23 checks passed (recordings 4/4, windows 16, read failures 0, "
                "no-candidate recordings 0, unusable 0, drum hits 39/56, drum precision 76.47%, "
                "drum recall 69.64%, F1 72.90%, false-positive windows 62.50% (10/16), "
                "recall by category kick:12/12-0, tp/fp/fn 39/12/17, hits min/avg/max 3/3.75/5)\n",
                encoding="utf-8",
            )
            mdb_drums = Path(temporary) / "mdb_drums_misses.log.summary"
            mdb_drums.write_text(
                "analyzer_egmd: 99 checks passed (recordings 23/23, windows 92, read failures 0, "
                "no-candidate recordings 0, unusable 0, drum hits 192/192, drum precision 70.85%, "
                "drum recall 100.00%, F1 82.94%, false-positive windows 55.43% (51/92), "
                "recall by category kick:55/55-0, tp/fp/fn 192/79/0, hits min/avg/max 1/2.14/3)\n",
                encoding="utf-8",
            )
            babyslakh_drums = Path(temporary) / "babyslakh_drums.log"
            babyslakh_drums.write_text(
                "analyzer_egmd: 41 checks passed (recordings 20/20, windows 80, read failures 0, "
                "no-candidate recordings 0, unusable 0, drum hits 101/140, drum precision 60.84%, "
                "drum recall 72.14%, F1 65.75%, false-positive windows 40.00% (32/80), "
                "recall by category kick:30/40-0, tp/fp/fn 101/65/39, hits min/avg/max 1/2.14/4)\n",
                encoding="utf-8",
            )
            babyslakh_archive = Path(temporary) / "babyslakh.tar.gz"
            babyslakh_archive.write_bytes(b"verified fixture")
            babyslakh_extraction = Path(temporary) / "babyslakh-extracted"
            babyslakh_extraction.mkdir()
            babyslakh_manifest = Path(temporary) / "babyslakh-e-gmd-v1.0.0.csv"
            babyslakh_manifest.write_text(
                "id,audio_filename,midi_filename\n" +
                "".join(f"Track{index:05d},audio/{index}.wav,midi/{index}.mid\n" for index in range(20)),
                encoding="utf-8",
            )
            urmp = Path(temporary) / "urmp.out"
            urmp.write_text(
                "URMP separated-track precision: expected >=90%, got 90/100 (isolated precision 90.00%, recall 75.00%)\n"
                "URMP separated-track exact recall: expected >=70%, got 90/120\n"
                "analyzer_urmp: 0/300 checks passed (4 pieces, 48 windows, 100 track hits/120, 90 provided chord hits/100, 0 summed chord hits/100)\n"
                "analyzer_urmp: coverage: discovered 4 piece dirs, loadable 4, unusable 0, no-candidate 0, selected 48 candidate windows\n"
                "analyzer_urmp: sax isolated metrics: isolated precision 90.00%, recall 75.00%, F1 81.82%, contamination 0.00%, octave-error 0.00%, ambiguous 0/12, by-row other tp/fp/fn 9/1/3, confusion none\n"
                "analyzer_urmp: chord metrics: provided global chord precision 90.00%, recall 75.00%, F1 81.82%, tp/fp/fn 30/3/10; summed global chord precision 90.00%, recall 75.00%, F1 81.82%, tp/fp/fn 30/3/10; provided stream global chord precision 90.00%, recall 80.00%, F1 84.21%, tp/fp/fn 32/3/8; summed stream global chord precision 90.00%, recall 80.00%, F1 84.21%, tp/fp/fn 32/3/8; provided sequence global chord precision 90.00%, recall 70.00%, F1 78.26%, tp/fp/fn 28/3/12\n",
                encoding="utf-8",
            )
            route_summary = Path(temporary) / "routes.txt"
            route_summary.write_text(
                "detector_route_summary: candidates=160 low_false=48 shadow=1 near_miss=68 "
                "guitar=35 drum=8 positive_net=78 gain_ge_1=78 source_safe_positive_net=68 "
                "actionable=1 coverage_blocked=34 independent_corpus_blocked=82\n",
                encoding="utf-8",
            )
            dcs_measurement = Path(temporary) / "dagstuhl_choirset_measurement.tsv"
            dcs_measurement.write_text(
                "\n".join((
                    "group\tmetric\taccurate\ttotal",
                    "All DCS chord windows\tExact chord accuracy\t1\t2",
                    "All DCS vocal windows\tCurrent-note vocal ownership\t1\t2",
                    "All DCS vocal windows\tVisible current-note vocal routing\t0\t2",
                    "All SATB notes\tPitch-class recall\t3\t4",
                    "SATB range — Soprano\tVocal ownership\t1\t1",
                    "Configuration — DCS_Test\tCurrent-note vocal ownership\t1\t2",
                )) + "\n",
                encoding="utf-8",
            )
            dcs_validation = Path(temporary) / "dagstuhl_validation.txt"
            dcs_inspection = Path(temporary) / "dagstuhl_inventory.txt"
            dcs_extraction = Path(temporary) / "DagstuhlChoirSet" / "README.md"
            dcs_manifest = Path(temporary) / "dagstuhl_manifest.json"
            dcs_extraction.parent.mkdir()
            for path in (dcs_validation, dcs_inspection, dcs_extraction, dcs_manifest):
                path.write_text("fixture\n", encoding="utf-8")
            piano_state_evidence = Path(temporary) / "independent_piano_states.txt"
            piano_state_evidence.write_text(
                "independent_piano_chord_states: corpora=2 shared_no_label_states=5 complete_pcs_recovery_candidates=1\n",
                encoding="utf-8",
            )
            piano_chord_stability = Path(temporary) / "independent_piano_chord_stability.txt"
            piano_chord_stability.write_text(
                "piano_chord_state_audit: combined sequences=2 frames=10 correct=4/10 "
                "no_label=3 wrong=3 transient_losses=1\n",
                encoding="utf-8",
            )
            piano_exact_fallback = Path(temporary) / "independent_piano_exact_chord_fallback.txt"
            piano_exact_fallback.write_text(
                "independent_piano_exact_chord_fallback: corpora=2 shared_runtime_safe=0\n",
                encoding="utf-8",
            )
            exact_note_cross_corpus = Path(temporary) / "vocal_exact_note_cross_corpus.tsv"
            exact_note_cross_corpus.write_text(
                "corpus\texact_vocal\texact_foreign\tpitch_class_only\tno_pitch_class\ttotal\n"
                "fixture\t1\t2\t3\t4\t10\n",
                encoding="utf-8",
            )
            scms_extraction = Path(temporary) / ".scms-extraction-complete"
            scms_manifest = Path(temporary) / "scms_manifest.tsv"
            scms_measurement = Path(temporary) / "scms_measurement.out"
            for path in (scms_extraction, scms_manifest, scms_measurement):
                path.write_text("fixture\n", encoding="utf-8")
            kraisler_archive = Path(temporary) / "KRAISLER.zip"
            kraisler_archive.write_text("fixture\n", encoding="utf-8")
            kraisler_extraction = Path(temporary) / "kraisler-extracted"
            kraisler_extraction.mkdir()
            kraisler_manifest = Path(temporary) / "kraisler-manifest.json"
            kraisler_manifest.write_text("fixture\n", encoding="utf-8")
            harmonic_product_audit = Path(temporary) / "harmonic_product_octave_audit.txt"
            harmonic_product_audit.write_text(
                "harmonic_product_octave: common_zero_regression_thresholds=0/6 corpora=3\n",
                encoding="utf-8",
            )
            quality_classifier_audit = Path(temporary) / "owner_classifier_quality_loco_audit.txt"
            quality_classifier_audit.write_text(
                "owner_classifier_loco: improved_corpora=8/9 current=10/20 model=14/20\n",
                encoding="utf-8",
            )
            drum_classifier_audit = Path(temporary) / "drum_primary_loco_audit.txt"
            drum_classifier_audit.write_text(
                "drum_primary_loco: improved_corpora=0/3 current=20/30 model=10/30 "
                "target_delta=tom=-5 ride=-3 rim=-2\n",
                encoding="utf-8",
            )
            drum_false_positive_cap_audit = Path(temporary) / "drum_false_positive_cap_audit.txt"
            drum_false_positive_cap_audit.write_text(
                "drum_false_positive_cap_audit: real_candidates=53 cross_real_candidates=2 "
                "protected_runtime_safe=0/2\n",
                encoding="utf-8",
            )
            mdb_full_mix_false_positive_cap_audit = Path(temporary) / "mdb_full_mix_false_positive_cap_audit.txt"
            mdb_full_mix_false_positive_cap_audit.write_text(
                "drum_false_positive_cap_audit: real_candidates=101 cross_real_candidates=101 "
                "protected_runtime_safe=0/101\n",
                encoding="utf-8",
            )
            mdb_full_mix_competing_active_context_audit = Path(temporary) / "mdb_full_mix_competing_active_context_audit.txt"
            mdb_full_mix_competing_active_context_audit.write_text(
                "drum_competing_active_context_audit: real_candidates=19 protected_runtime_safe=6/19 "
                "runtime_replayed=6/6 runtime_gain=0/6\n",
                encoding="utf-8",
            )
            drum_false_positive_context_audit = Path(temporary) / "drum_false_positive_context_audit.txt"
            drum_false_positive_context_audit.write_text(
                "drum_false_positive_context_audit: primitives=102 cross_real_contexts=2 "
                "protected_runtime_safe=1/2\n",
                encoding="utf-8",
            )
            drum_recovery_candidate_audit = Path(temporary) / "drum_recovery_candidate_audit.txt"
            drum_recovery_candidate_audit.write_text(
                "drum_recovery_candidate_audit: corpora=2 missed_events=70 "
                "cross_real_zero_false_candidates=3\n",
                encoding="utf-8",
            )
            chord_primary_component_audit = Path(temporary) / "chord_primary_component_audit.txt"
            chord_primary_component_audit.write_text(
                "chord_primary_component_audit: any_hit=17/20 primary_hit=15/20 alias_rescued=2 "
                "dim7_primary_hit=17/20 dim7_promotions=2 dim7_regressions=0\n",
                encoding="utf-8",
            )
            urmp_bass_timing = Path(temporary) / "urmp_bass_timing_audit.tsv"
            urmp_bass_timing.write_text(
                "piece\tnotes\taudio_aligned_notes\tscore_midi\texplicit_beat_grid\tqualifies_as_tempo_truth\ttiming_files\n"
                "35\tNotes_04_db.txt\t1\t1\t0\t0\t\n",
                encoding="utf-8",
            )
            idmt_bass_timing = Path(temporary) / "idmt_bass_lines_tempo_metadata.tsv"
            idmt_bass_timing.write_text(
                "track_id\tparameter\tvalue\ttiming_or_pattern_field\n"
                "001\tinstrument\tBass\t\n"
                "002\tinstrument\tBass\t\n",
                encoding="utf-8",
            )
            filobass_bpm = Path(temporary) / "filobass_bpm_diagnostics.log"
            filobass_bpm.write_text(
                "MAESTRO tempo diag\tid=1\texpected=120.00\tgot=120.00\tstatus=hit\tcandidates=160(s=1,align=10/20/30/40) 120(s=1,align=10/70/30/40)\n"
                "MAESTRO tempo diag\tid=2\texpected=100.00\tgot=0.00\tstatus=no-estimate\tcandidates=100(s=1,align=10/50/30/40,kb=50) 160(s=1,align=10/20/30/40,kb=20)\n",
                encoding="utf-8",
            )
            filobass_onsets = Path(temporary) / "filobass_bass_onset_diagnostics.tsv"
            filobass_onsets.write_text(
                "id\texpected_bpm\ttop_bpm\ttop_or_double_hit\texpected_rank\ttop_score\texpected_score\n"
                "one\t120\t120\t1\t1\t1\t1\n"
                "two\t100\t50\t1\t3\t1\t0.8\n",
                encoding="utf-8",
            )
            beat_this_ballroom = Path(temporary) / "beat_this_ballroom.log"
            beat_this_ballroom.write_text(
                "Beat This tempo diag\tid=1\texpected=120.00\traw=120.00\terror=0.00\tstatus=hit\n",
                encoding="utf-8",
            )
            beat_this_filobass = Path(temporary) / "beat_this_filobass.log"
            beat_this_filobass.write_text(
                "Beat This tempo diag\tid=1\texpected=100.00\traw=100.00\terror=0.00\tstatus=hit\n",
                encoding="utf-8",
            )
            three_tracker_consensus = Path(temporary) / "three_tracker_consensus.log"
            three_tracker_consensus.write_text(
                "three-tracker consensus sweep: corpora=3 rows=3\n"
                "three-tracker consensus viable: correct=2/2 newly_revealed=1 phase_max=0.60 btt_gate=0.00 agreement=8.00\n",
                encoding="utf-8",
            )
            high_three_tracker_consensus = Path(temporary) / "high_three_tracker_consensus.log"
            high_three_tracker_consensus.write_text(
                "three-tracker consensus sweep: corpora=1 rows=3 min_expected=150.00\n"
                "three-tracker consensus viable: none\n",
                encoding="utf-8",
            )
            piano_chord_confirm3 = Path(temporary) / "piano_chord_confirm3.txt"
            piano_chord_confirm3.write_text(
                "piano_chord_confirmation_audit: baseline_correct=96/530 baseline_wrong=243 "
                "baseline_flickers=0 trial_correct=95/530 trial_wrong=244 trial_flickers=0 "
                "retained_confirm_frames=2 eligible=0\n",
                encoding="utf-8",
            )
            piano_chord_tone018 = Path(temporary) / "piano_chord_tone018.txt"
            piano_chord_tone018.write_text(
                "piano_chord_confirmation_audit: baseline_correct=96/530 baseline_wrong=243 "
                "baseline_flickers=0 trial_correct=99/530 trial_wrong=245 trial_flickers=0 "
                "retained_confirm_frames=2 eligible=0\n",
                encoding="utf-8",
            )
            beat_this_rolling_ballroom = Path(temporary) / "beat_this_rolling_ballroom.log"
            beat_this_rolling_ballroom.write_text(
                "Beat This rolling tempo diag\tid=1\texpected=120.00\traw=120.00\twindow_seconds=20.000\twall_seconds=3.000\terror=0.00\tstatus=hit\n",
                encoding="utf-8",
            )
            beat_this_rolling_filobass = Path(temporary) / "beat_this_rolling_filobass.log"
            beat_this_rolling_filobass.write_text(
                "Beat This rolling tempo diag\tid=1\texpected=100.00\traw=200.00\twindow_seconds=20.000\twall_seconds=21.000\terror=100.00\tstatus=miss\n",
                encoding="utf-8",
            )
            beat_this_continuous_ballroom = Path(temporary) / "beat_this_continuous_ballroom.log"
            beat_this_continuous_ballroom.write_text(
                "Beat This rolling tempo diag\tid=1\toutput=1\texpected=120.00\traw=120.00\twindow_seconds=20.000\twall_seconds=3.000\terror=0.00\tstatus=hit\n",
                encoding="utf-8",
            )
            beat_this_continuous_filobass = Path(temporary) / "beat_this_continuous_filobass.log"
            beat_this_continuous_filobass.write_text(
                "Beat This rolling tempo diag\tid=1\toutput=1\texpected=100.00\traw=200.00\twindow_seconds=20.000\twall_seconds=21.000\terror=100.00\tstatus=miss\n",
                encoding="utf-8",
            )
            ballroom_annotations = Path(temporary) / "ballroom-annotations"
            (ballroom_annotations / ".git").mkdir(parents=True)
            report = REPORT.render(
                source, [chords], vocal_full_mix, [bach10_0, bach10_1], musicnet, drum, urmp,
                vocalset_full_mix, [maps], None, route_summary, good_sounds_full_mix, irmas_labelled,
                hf_drum_outputs,
                maps_attributes, medley_solos_attributes, focused_vocalset_clean_vowel,
                pitch_shifted_violin,
                iowa_orchestra_full_input=iowa_orchestra_full,
                tinysol_wind_exact_input=tinysol_wind_exact,
                iowa_sax_full_mix_input=iowa_sax_full_mix,
                iowa_piano_full_mix_input=iowa_piano_full_mix,
                tinysol_sax_full_mix_input=tinysol_sax_full_mix,
                real_a2s_tenor_scale_input=real_a2s_tenor_scale,
                urmp_sax_exact_input=urmp_sax_exact,
                urmp_sax_full_mix_input=urmp_sax_full_mix,
                star_drums_gate_output=star_drums,
                mdb_drums_gate_output=mdb_drums,
                babyslakh_drums_gate_output=babyslakh_drums,
                babyslakh_archive=babyslakh_archive,
                babyslakh_extraction=babyslakh_extraction,
                babyslakh_manifest=babyslakh_manifest,
                dagstuhl_choirset_input=dcs_measurement,
                dagstuhl_choirset_validation=dcs_validation,
                dagstuhl_choirset_inspection=dcs_inspection,
                dagstuhl_choirset_extraction=dcs_extraction,
                dagstuhl_choirset_manifest=dcs_manifest,
                mir1k_dataset_archive=Path(temporary) / "missing-mir1k.tar.gz",
                mir1k_dataset_extraction=Path(temporary) / "missing-mir1k-extraction",
                mir1k_full_mix_input=vocal_full_mix,
                scms_dataset_extraction=scms_extraction,
                scms_dataset_manifest=scms_manifest,
                scms_dataset_measurement=scms_measurement,
                scms_full_mix_input=vocal_full_mix,
                vocal_exact_note_cross_corpus_input=exact_note_cross_corpus,
                maestro_real_measurement=maps,
                maestro_real_manifest=source,
                maestro_real_attribute_input=maps_attributes,
                independent_piano_chord_state_evidence_input=piano_state_evidence,
                independent_piano_chord_stability_evidence_input=piano_chord_stability,
                independent_piano_exact_chord_fallback_audit_input=piano_exact_fallback,
                piano_chord_confirm3_audit_input=piano_chord_confirm3,
                piano_chord_tone018_audit_input=piano_chord_tone018,
                kraisler_archive=kraisler_archive,
                kraisler_extraction=kraisler_extraction,
                kraisler_manifest=kraisler_manifest,
                kraisler_measurement=dcs_measurement,
                harmonic_product_octave_audit_input=harmonic_product_audit,
                owner_classifier_quality_loco_audit_input=quality_classifier_audit,
                drum_primary_loco_audit_input=drum_classifier_audit,
                drum_false_positive_cap_audit_input=drum_false_positive_cap_audit,
                mdb_full_mix_false_positive_cap_audit_input=mdb_full_mix_false_positive_cap_audit,
                mdb_full_mix_competing_active_context_audit_input=mdb_full_mix_competing_active_context_audit,
                drum_false_positive_context_audit_input=drum_false_positive_context_audit,
                drum_recovery_candidate_audit_input=drum_recovery_candidate_audit,
                chord_primary_component_audit_input=chord_primary_component_audit,
                urmp_bass_timing_audit_input=urmp_bass_timing,
                idmt_bass_tempo_metadata_input=idmt_bass_timing,
                filobass_bpm_input=filobass_bpm,
                filobass_onset_diagnostic_input=filobass_onsets,
                beat_this_ballroom_bpm_input=beat_this_ballroom,
                beat_this_filobass_bpm_input=beat_this_filobass,
                beat_this_rolling_ballroom_bpm_input=beat_this_rolling_ballroom,
                beat_this_rolling_filobass_bpm_input=beat_this_rolling_filobass,
                beat_this_continuous_ballroom_bpm_input=beat_this_continuous_ballroom,
                beat_this_continuous_filobass_bpm_input=beat_this_continuous_filobass,
                three_tempo_tracker_consensus_input=three_tracker_consensus,
                high_tempo_three_tracker_consensus_input=high_three_tracker_consensus,
                ballroom_annotations=ballroom_annotations,
            )

        self.assertIn("| Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Guitar — Visual primary row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Detector-improvement route coverage", report)
        self.assertIn(
            "| Retrieve versioned Ballroom beat/bar annotations | 1 / 1 (100.0%) | 0 |",
            report,
        )
        self.assertIn("## Harmonic-product octave-correction audit", report)
        self.assertIn("| Zero-regression harmonic-product thresholds across all SATB corpora | 0 / 6 (0.0%) | 6 |", report)
        self.assertIn("## Extended owner-classifier leave-one-corpus-out audit", report)
        self.assertIn("| LOCO corpora improved over current owner | 8 / 9 (88.9%) | 1 |", report)
        self.assertIn("## Drum-primary leave-one-corpus-out classifier audit", report)
        self.assertIn("## Real-drum Tom/Ride/Rim coverage checklist", report)
        self.assertIn("## Continuous independent-piano chord-state replay", report)
        self.assertIn("| Three-frame replacement confirmation | 95 / 530 (17.9%) | 244 | 0 |", report)
        self.assertIn("| Lower 0.18 pitch-class presence | 99 / 530 (18.7%) | 245 | 0 |", report)
        self.assertIn("| Annotated stable chord-state frames with the expected keyboard chord | 4 / 10 (40.0%) | 6 |", report)
        self.assertIn("### Independent-piano exact fallback audit", report)
        self.assertIn("| Cross-piano runtime-safe exact pitch-class fallback available | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn(
            "| Checksum-verified 29k Drums archive inspected for Tom/Ride labels | 0 / 1 (0.0%) | 1 |",
            report,
        )
        self.assertIn("| Measure independent 29k Drums Tom/Ride baseline | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("| Independently replicate Rim on real acoustic recordings | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("ENST-Drums has suitable labelled classes and a public prepared archive", report)
        self.assertIn("| Aggregate classifier accuracy | 10 / 30 (33.3%) | 20 |", report)
        self.assertIn("## Cross-real drum false-positive cap audit", report)
        self.assertIn("| Cross-real candidates safe on protected one-shot primaries | 0 / 2 (0.0%) | 2 |", report)
        self.assertIn("## MDB full-mix drum false-positive cap audit", report)
        self.assertIn("| MDB caps safe on protected one-shot primaries | 0 / 101 (0.0%) | 101 |", report)
        self.assertIn("## Cross-real competing-drum context audit", report)
        self.assertIn("| Remaining contexts safe for an isolated runtime experiment | 6 / 19 (31.6%) | 13 |", report)
        self.assertIn("| Protected-safe contexts replayed through runtime detector | 6 / 6 (100.0%) | 0 |", report)
        self.assertIn("| Replayed contexts with a verified runtime gain | 0 / 6 (0.0%) | 6 |", report)
        self.assertIn("| Further source-scoped context work available | 0 / 6 (0.0%) | 6 |", report)
        self.assertIn("## Two-feature cross-real drum false-positive context audit", report)
        self.assertIn("| Protected one-shot runtime-safe contexts | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Early Snare onset | 139→140 / 28→28 | 39→40 / 0→0 | 140→140 / 38→39 |", report)
        self.assertIn("| Low-transient HiHat | 139→140 / 28→28 | 39→39 / 0→0 | 140→140 / 38→38 |", report)
        self.assertIn("| Zero-false cross-real recovery shapes replayed through runtime gates | 3 / 3 (100.0%) | 0 |", report)
        self.assertIn("| Recovery shapes with a verified overall runtime gain | 0 / 3 (0.0%) | 3 |", report)
        self.assertIn("## Canonical-first chord display audit", report)
        self.assertIn("| Correct chords rescued only by a later alias | 2 / 17 (11.8%) | 15 |", report)
        self.assertIn("| Correct chords after same-root dim7 promotion | 17 / 20 (85.0%) | 3 |", report)
        self.assertIn("| Same-root dim7 runtime display eligible | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("## URMP double-bass timing-ground-truth audit", report)
        self.assertIn("| URMP double-bass stems qualifying as tempo truth | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("## Rejected three-corpus keys-to-vocal routing trial", report)
        self.assertIn(
            "| Protected full-mix first-row accuracy during trial | 771 / 2212 (34.9%) | 1441 |",
            report,
        )
        self.assertIn("## Choral Singing Dataset (CSD) coverage-gap checklist", report)
        self.assertIn("## MIR-1K vocal-with-accompaniment coverage-gap checklist", report)
        self.assertIn("Store validated MIR-1K archive in InstrumentSamples | 0 / 1 (0.0%)", report)
        self.assertIn("## Saraga-Carnatic-Melody-Synth (SCMS) coverage-gap checklist", report)
        self.assertIn("Store validated SCMS archive in InstrumentSamples | 0 / 1 (0.0%)", report)
        self.assertIn("Extract SCMS safely in InstrumentSamples | 1 / 1 (100.0%) | 0", report)
        self.assertIn("Prepare labelled vocal-plus-accompaniment windows | 1 / 1 (100.0%) | 0", report)
        self.assertIn("Measure current-note exact-MIDI and pitch-class recall | 1 / 1 (100.0%) | 0", report)
        self.assertIn("## SCMS full-mix vocal routing", report)
        self.assertIn("| SCMS vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("Run DCS/CSD/ESMUC/MIR-1K/cached-vocal ownership audit", report)
        self.assertIn("Audit exact-MIDI vocal failures across all six corpora | 1 / 1 (100.0%)", report)
        self.assertIn(
            "Re-audit ownership rules across choir, solo-vocal, and MIR-1K corpora | 0 / 1 (0.0%)",
            report,
        )
        self.assertIn("## MIR-1K full-mix vocal routing", report)
        self.assertIn("## Cross-corpus vocal exact-MIDI evidence", report)
        self.assertIn("| fixture — pitch class only (wrong octave) | 3 / 10 (30.0%) | 7 |", report)
        self.assertIn("| MIR-1K vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("## Dagstuhl ChoirSet (DCS) real-audio measurement", report)
        self.assertIn("| Store DCS archive in InstrumentSamples | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Extract DCS safely in InstrumentSamples | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Inspect real DCS audio and annotations | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Import DCS sources and labels | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Prepare external MAESTRO paired-audio subset | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Measure MAESTRO note and chord outcomes | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| MAESTRO external piano — expected pitch classes |", report)
        self.assertIn("## Independent piano chord-outcome evidence", report)
        self.assertIn("| No-label states with complete pitch-class recovery in every corpus | 1 / 5 (20.0%) | 4 |", report)
        self.assertIn("| MAPS |", report)
        self.assertIn("| MAESTRO |", report)
        self.assertIn("## KRAISLER independent piano–violin coverage checklist", report)
        self.assertIn("## IDMT real-bass timing-ground-truth audit", report)
        self.assertIn("## Beat This! offline real-tempo diagnostic", report)
        self.assertIn("| Ballroom offline stable-segment BPM within 8 BPM | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| FiloBass offline stable-segment BPM within 8 BPM | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("### Three-tracker offline consensus safety audit", report)
        self.assertIn("| Correct offline three-tracker consensus candidates | 2 / 2 (100.0%) | 0 wrong candidates |", report)
        self.assertIn("| Audited rows eligible for offline three-tracker consensus | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("### High-tempo three-tracker offline veto audit", report)
        self.assertIn("| Correct high-tempo three-tracker consensus candidates | 0 / 0 (0.0%) | 0 wrong candidates |", report)
        self.assertIn("| High-tempo annotated rows eligible for consensus | 0 / 3 (0.0%) | 3 |", report)
        self.assertIn("| Benchmark Beat This! on independent real-tempo corpora | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Audit phase/BTT/Beat This! offline agreement | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("### Beat This! bounded rolling-window replay", report)
        self.assertIn("### Beat This! continuous causal replay", report)
        self.assertIn("| Ballroom continuous causal BPM within 8 BPM | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| FiloBass continuous causal BPM within 8 BPM | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("| Ballroom rolling BPM within 8 BPM | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| FiloBass rolling BPM within 8 BPM | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("| FiloBass rolling windows processed within their audio duration | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("| Replay bounded trailing Beat This! windows on real-tempo corpora | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Demonstrate bounded causal Beat This! live use | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("## FiloBass real bass-led annotated-tempo diagnostic", report)
        self.assertIn("### FiloBass raw bass-attack feasibility diagnostic", report)
        self.assertIn("### FiloBass source-grid energy feasibility diagnostic", report)
        self.assertIn("| Labelled BPM exported through harness-only probe | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Present labelled candidate has higher bass grid-energy | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Reviewed BPM ranked first by raw bass attacks | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Reviewed BPM matches raw bass attacks at direct or double tempo | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Reviewed BPM ranked in top five by raw bass attacks | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Displayable BPM at confidence ≥ 0.60 | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Tracks with corpus-supplied tempo, beat, or pattern metadata | 0 / 2 (0.0%) | 2 |", report)
        self.assertIn("| IDMT real-bass timing metadata qualifies as beat truth | 0 / 2 (0.0%) | 2 |", report)
        self.assertIn("| Independent real bass-led beat-labelled validation measured | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Reject MUSDB18/BeatNet+ as an authoritative bass BPM benchmark | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Assess raw bass-attack BPM evidence | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Preserve simultaneous kick+bass downbeat evidence | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Reject bass-dominant RMS attack phase feature | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Reject combined bass/coincidence candidate reweighting | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Retain calibrated BPM display-confidence gate | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Retrieve license-compatible advanced beat tracker | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Benchmark permissive beat tracker on both real tempo corpora | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Permissive tracker raw BPM — Ballroom | 41 / 64 (64.1%) | 23 |", report)
        self.assertIn("| Permissive tracker at 0.75 certainty — FiloBass | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Permissive tracker at 0.80 certainty — Ballroom | 11 / 11 (100.0%) | 0 |", report)
        self.assertIn("| Repair continuous PCM feed to permissive tracker | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Enable strict live permissive-tracker fallback | 3 / 3 (100.0%) | 0 |", report)
        self.assertIn("| Benchmark constrained high-tempo beat tracker | 2 / 2 (100.0%) | 0 |", report)
        self.assertIn("| Reject concurrent high-tempo tracker fallback | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Reject high-tempo-only tracker setting | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Demonstrate a bass-attack feature improves real bass BPM | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("| Validate external KRAISLER archive | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Complete protected KRAISLER cross-corpus rule audit | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("### KRAISLER real piano–violin measurement", report)
        self.assertIn("| DCS All DCS vocal windows — Current-note vocal ownership | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| DCS All DCS vocal windows — Visible current-note vocal routing | 0 / 2 (0.0%) | 2 |", report)
        self.assertIn("| DCS SATB range — Soprano — Vocal ownership | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| DCS Configuration — DCS_Test — Current-note vocal ownership | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Routes meeting protected and cross-corpus gates | 1 / 160 (0.6%) | 159 |", report)
        self.assertIn("| Routes awaiting additional fixture coverage | 34 / 160 (21.2%) | 126 |", report)
        self.assertIn("| Routes lacking independent-corpus replication | 82 / 160 (51.2%) | 78 |", report)
        self.assertIn("## IRMAS independent instrument-routing coverage", report)
        self.assertIn("| IRMAS — Strongest raw routing row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Cached isolated-guitar chord gates", report)
        self.assertIn("## TinySOL isolated wind and brass exact-note coverage", report)
        self.assertIn("| TinySOL — Oboe — exact expected MIDI note | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| TinySOL — Trombone — exact expected MIDI note | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Guitar Chord Mix — exact chord windows | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — primary displayed chord windows | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — expected guitar pitch classes | 6 / 8 (75.0%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — power-chord exact windows | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("## Vocadito full-mix vocal routing", report)
        self.assertIn("## MAPS real-piano gate", report)
        self.assertIn("| MAPS real piano — keyboard chord precision | 2 / 4 (50.0%) | 2 false predictions |", report)
        self.assertIn("## MAPS chord-miss evidence", report)
        self.assertIn("| Expected pitch classes are all present | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| No keyboard chord label | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Vocadito vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Vocadito vocals — Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("## VocalSet full-mix vocal routing", report)
        self.assertIn("| VocalSet vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| VocalSet vocals — Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("### Focused clean-vowel regression", report)
        self.assertIn("| VocalSet clean C5 vowel — Expected instrument row | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("## Good Sounds full-mix acoustic routing", report)
        self.assertIn("all 1,318 usable labelled recordings are already in this fixture", report)
        self.assertIn("| Good Sounds — Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Good Sounds — Other — Expected instrument row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Controlled octave-down violin fixture", report)
        self.assertIn("| Pitch-shifted violin — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("## Iowa orchestra isolated-note coverage", report)
        self.assertIn("| Iowa orchestra — Exact expected MIDI note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Iowa orchestra — Bass — exact expected MIDI note | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("## Iowa saxophone full-mix routing", report)
        self.assertIn("| Iowa saxophones — Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("## Iowa piano full-mix routing", report)
        self.assertIn("| Iowa piano — Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("## TinySOL alto-saxophone full-mix routing", report)
        self.assertIn("| TinySOL alto saxophone — Primary display row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Real A2S tenor-saxophone score-aligned probes", report)
        self.assertIn("| Real A2S tenor saxophone — Exact expected MIDI note | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## URMP isolated saxophone exact-note coverage", report)
        self.assertIn("| URMP saxophones — Exact expected MIDI note | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## URMP saxophone full-mix-mode routing", report)
        self.assertIn("| URMP saxophones — Expected instrument row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Medley Solos instrument routing", report)
        self.assertIn("| Medley Solos — Expected instrument row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Medley Solos — Instrument Clarinet expected row | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Medley Solos — Instrument Female Singer expected row | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("## Bach10-mf0-synth multitrack stress gate", report)
        self.assertIn("| Bach10-mf0-synth — expected note slots | 74 / 80 (92.5%) | 6 |", report)
        self.assertIn("| Bach10-mf0-synth — exact chord windows | 14 / 20 (70.0%) | 6 |", report)
        self.assertIn("| Bach10-mf0-synth — simplified chord windows | 16 / 20 (80.0%) | 4 |", report)
        self.assertIn("## MusicNet real-mixture gate", report)
        self.assertIn(
            "| MusicNet real mixes — recordings with eligible chord windows | 20 / 330 (6.1%) | 310 |",
            report,
        )
        self.assertIn("| MusicNet real mixes — expected pitch classes | 210 / 300 (70.0%) | 90 |", report)
        self.assertIn("## URMP real multitrack gate", report)
        self.assertIn("| URMP — isolated-track exact notes | 90 / 120 (75.0%) | 30 |", report)
        self.assertIn("| URMP — isolated-track precision | 90 / 100 (90.0%) | 10 false notes |", report)
        self.assertIn("| URMP — saxophone isolated exact notes | 9 / 12 (75.0%) | 3 |", report)
        self.assertIn("| URMP — provided sequence chord windows | 28 / 40 (70.0%) | 12 |", report)
        self.assertIn("## Full drum primary-classification gate", report)
        self.assertIn("| Full drum gate — primary kick | 8 / 10 (80.0%) | 2 |", report)
        self.assertIn("| Full drum gate — primary hihat | 6 / 10 (60.0%) | 4 |", report)
        self.assertIn("## High-fidelity drum-kit primary-classification gate", report)
        self.assertIn("| High-fidelity drum kit — primary rim | 8 / 10 (80.0%) | 2 |", report)
        self.assertIn("## STAR Drums preview multitrack gate", report)
        self.assertIn("| STAR Drums preview — annotated drum events detected | 39 / 56 (69.6%) | 17 |", report)
        self.assertIn("| STAR Drums preview — detected-drum precision | 39 / 51 (76.5%) | 12 false predictions |", report)
        self.assertIn("| STAR Drums preview — windows without a false drum | 6 / 16 (37.5%) | 10 false-positive windows |", report)
        self.assertIn("## MDB Drums multitrack gate", report)
        self.assertIn("| MDB Drums — annotated drum events detected | 192 / 192 (100.0%) | 0 |", report)
        self.assertIn("| MDB Drums — detected-drum precision | 192 / 271 (70.8%) | 79 false predictions |", report)
        self.assertIn("| MDB Drums — windows without a false drum | 41 / 92 (44.6%) | 51 false-positive windows |", report)
        self.assertIn("## BabySlakh rendered full-mix drum baseline", report)
        self.assertIn("| BabySlakh rendered mixes — annotated drum events detected | 101 / 140 (72.1%) | 39 |", report)
        self.assertIn("| BabySlakh rendered mixes — detected-drum precision | 101 / 166 (60.8%) | 65 false predictions |", report)
        self.assertIn("| BabySlakh rendered mixes — windows without a false drum | 48 / 80 (60.0%) | 32 false-positive windows |", report)
        self.assertIn("## BabySlakh drum-validation checklist", report)
        self.assertIn("| Store checksum-verified archive in InstrumentSamples | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Extract archive safely in InstrumentSamples | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| Inspect and prepare all published drum full mixes | 20 / 20 (100.0%) | 0 |", report)
        self.assertIn("| Measure rendered full-mix drum baseline | 1 / 1 (100.0%) | 0 |", report)


if __name__ == "__main__":
    unittest.main()
