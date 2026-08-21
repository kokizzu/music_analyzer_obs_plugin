#!/usr/bin/env python3
"""Tests for the strict Beat This interval-count gate audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_beat_this_continuous_interval_gate.py"
SPEC = importlib.util.spec_from_file_location("audit_beat_this_continuous_interval_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def row(intervals: int, status: str) -> str:
    return f"Beat This rolling tempo diag\tid=1\toutput=1\tintervals={intervals}\tstatus={status}\n"


class ContinuousIntervalGateTests(unittest.TestCase):
    def test_finds_the_broadest_zero_wrong_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ballroom = root / "ballroom.log"
            filobass = root / "filobass.log"
            ballroom.write_text(row(8, "miss") + row(12, "hit") + row(13, "hit"), encoding="utf-8")
            filobass.write_text(row(9, "miss") + row(12, "hit") + row(14, "hit"), encoding="utf-8")
            rendered = "\n".join(MODULE.render(ballroom, filobass, 2))
        self.assertIn("minimum_intervals=12", rendered)
        self.assertIn("ballroom_correct=2/2", rendered)
        self.assertIn("filobass_correct=2/2", rendered)
        self.assertIn("eligible=1", rendered)

    def test_rejects_a_gate_without_enough_safe_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ballroom = root / "ballroom.log"
            filobass = root / "filobass.log"
            ballroom.write_text(row(12, "hit"), encoding="utf-8")
            filobass.write_text(row(12, "miss"), encoding="utf-8")
            rendered = "\n".join(MODULE.render(ballroom, filobass, 1))
        self.assertIn("minimum_intervals=-1", rendered)
        self.assertIn("eligible=0", rendered)


if __name__ == "__main__":
    unittest.main()
