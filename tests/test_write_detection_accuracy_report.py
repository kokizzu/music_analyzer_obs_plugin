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
        self.assertFalse(
            REPORT.visual_expected_pitch_lit(
                {"expected_midi": "44", "other_visual_notes": "A3:1.00"}, "other"
            )
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
            urmp = Path(temporary) / "urmp.out"
            urmp.write_text(
                "URMP separated-track precision: expected >=90%, got 90/100 (isolated precision 90.00%, recall 75.00%)\n"
                "URMP separated-track exact recall: expected >=70%, got 90/120\n"
                "analyzer_urmp: 0/300 checks passed (4 pieces, 48 windows, 100 track hits/120, 90 provided chord hits/100, 0 summed chord hits/100)\n"
                "analyzer_urmp: coverage: discovered 4 piece dirs, loadable 4, unusable 0, no-candidate 0, selected 48 candidate windows\n"
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
            report = REPORT.render(
                source, [chords], vocal_full_mix, [bach10_0, bach10_1], musicnet, drum, urmp,
                vocalset_full_mix, [maps], None, route_summary, good_sounds_full_mix,
            )

        self.assertIn("| Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Guitar — Visual primary row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Detector-improvement route coverage", report)
        self.assertIn("| Routes with direct zero-regression support | 1 / 160 (0.6%) | 159 |", report)
        self.assertIn("| Routes awaiting additional fixture coverage | 34 / 160 (21.2%) | 126 |", report)
        self.assertIn("## Cached isolated-guitar chord gates", report)
        self.assertIn("| Guitar Chord Mix — exact chord windows | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — primary displayed chord windows | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — expected guitar pitch classes | 6 / 8 (75.0%) | 2 |", report)
        self.assertIn("| Guitar Chord Mix — power-chord exact windows | 0 / 1 (0.0%) | 1 |", report)
        self.assertIn("## Vocadito full-mix vocal routing", report)
        self.assertIn("## MAPS real-piano gate", report)
        self.assertIn("| MAPS real piano — keyboard chord precision | 2 / 4 (50.0%) | 2 false predictions |", report)
        self.assertIn("| Vocadito vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Vocadito vocals — Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("## VocalSet full-mix vocal routing", report)
        self.assertIn("| VocalSet vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| VocalSet vocals — Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("## Good Sounds full-mix acoustic routing", report)
        self.assertIn("| Good Sounds — Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Good Sounds — Other — Expected instrument row | 1 / 2 (50.0%) | 1 |", report)
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
        self.assertIn("| URMP — provided sequence chord windows | 28 / 40 (70.0%) | 12 |", report)
        self.assertIn("## Full drum primary-classification gate", report)
        self.assertIn("| Full drum gate — primary kick | 8 / 10 (80.0%) | 2 |", report)
        self.assertIn("| Full drum gate — primary hihat | 6 / 10 (60.0%) | 4 |", report)


if __name__ == "__main__":
    unittest.main()
