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
                        "\t".join(("expected_chords", "chord_hit", "expected_pitch_class_count", "guitar_note_hits")),
                        "C\t1\t3\t3",
                        "Dm\t0\t3\t2",
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
            report = REPORT.render(source, [chords], vocal_full_mix)

        self.assertIn("| Any detected note | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Primary display row | 1 / 3 (33.3%) | 2 |", report)
        self.assertIn("| Visual primary row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Guitar — Visual primary row | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("## Cached isolated-guitar chord gates", report)
        self.assertIn("| Guitar Chord Mix — exact chord windows | 1 / 2 (50.0%) | 1 |", report)
        self.assertIn("| Guitar Chord Mix — expected guitar pitch classes | 5 / 6 (83.3%) | 1 |", report)
        self.assertIn("## Vocadito full-mix vocal routing", report)
        self.assertIn("| Vocadito vocals — Expected instrument row | 2 / 3 (66.7%) | 1 |", report)
        self.assertIn("| Vocadito vocals — Visual primary row | 2 / 3 (66.7%) | 1 |", report)


if __name__ == "__main__":
    unittest.main()
