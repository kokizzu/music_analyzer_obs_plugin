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
                "actionable=1 coverage_blocked=34\n",
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
            report = REPORT.render(
                source, [chords], vocal_full_mix, [bach10_0, bach10_1], musicnet, drum, urmp,
                vocalset_full_mix, [maps], None, route_summary, good_sounds_full_mix, hf_drum_outputs,
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
            )

        self.assertIn("| Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Guitar — Visual primary row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Detector-improvement route coverage", report)
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
        self.assertIn("| DCS All DCS vocal windows — Current-note vocal ownership | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| DCS All DCS vocal windows — Visible current-note vocal routing | 0 / 2 (0.0%) | 2 |", report)
        self.assertIn("| DCS SATB range — Soprano — Vocal ownership | 1 / 1 (100.0%) | 0 |", report)
        self.assertIn("| DCS Configuration — DCS_Test — Current-note vocal ownership | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Routes meeting protected and cross-corpus gates | 1 / 160 (0.6%) | 159 |", report)
        self.assertIn("| Routes awaiting additional fixture coverage | 34 / 160 (21.2%) | 126 |", report)
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


if __name__ == "__main__":
    unittest.main()
