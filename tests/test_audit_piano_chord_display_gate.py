#!/usr/bin/env python3
"""Checks for the protected keyboard-chord display-gate comparison."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "audit_piano_chord_display_gate.py"
SPEC = importlib.util.spec_from_file_location("piano_chord_display_gate", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class PianoChordDisplayGateTest(unittest.TestCase):
    def test_gate_requires_wrong_label_reduction_without_correct_or_flicker_loss(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            header = "recording\tanchor_sample\tframe\tkeyboard_chord\tchord_hit\n"
            baseline = root / "baseline.tsv"
            baseline.write_text(
                header + "a\t1\t0\tC\t1\n" + "a\t1\t1\tD\t0\n" + "a\t1\t2\tC\t1\n",
                encoding="utf-8",
            )
            trial = root / "trial.tsv"
            trial.write_text(
                header + "a\t1\t0\tC\t1\n" + "a\t1\t1\t--\t0\n" + "a\t1\t2\tC\t1\n",
                encoding="utf-8",
            )
            result = AUDIT.render([baseline], [trial], 0.60)
        self.assertEqual(
            result,
            "piano_chord_display_gate: floor=0.60 baseline_correct=2/3 baseline_wrong=1 "
            "baseline_flickers=1 trial_correct=2/3 trial_wrong=0 trial_flickers=1 eligible=1",
        )


if __name__ == "__main__":
    unittest.main()
