#!/usr/bin/env python3
"""Checks for the continuous-piano chord confidence-floor screen."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "audit_piano_chord_display_confidence.py"
SPEC = importlib.util.spec_from_file_location("piano_chord_display_confidence", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class PianoChordDisplayConfidenceTest(unittest.TestCase):
    def test_floor_requires_zero_correct_suppression_in_both_corpora(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            header = "keyboard_chord\tkeyboard_chord_confidence\tchord_hit\n"
            maps = root / "maps.tsv"
            maps.write_text(header + "C\t0.80\t1\nD\t0.45\t0\n", encoding="utf-8")
            maestro = root / "maestro.tsv"
            maestro.write_text(header + "E\t0.80\t1\nF\t0.45\t0\n", encoding="utf-8")
            result = AUDIT.render([maps, maestro], (0.0, 0.50, 0.90))
        self.assertIn("0.50\t0\t2\t2/2", result)
        self.assertIn(
            "piano_chord_display_confidence: best_floor=0.50 supported_corpora=2/2 "
            "common_zero_regression_floors=1",
            result,
        )


if __name__ == "__main__":
    unittest.main()
