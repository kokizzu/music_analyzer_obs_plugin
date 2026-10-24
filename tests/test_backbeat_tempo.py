#!/usr/bin/env python3
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_backbeat_tempo import backbeat_candidate


class Tests(unittest.TestCase):
    def test_quarter_kick_and_backbeat_snare(self):
        kick = [(i * .5, 1.) for i in range(6)]
        snare = [(.5, 1.), (1.5, 1.), (2.5, 1.)]
        self.assertEqual(backbeat_candidate(60, kick, snare), 120)

    def test_missing_quarter_support_keeps_native(self):
        snare = [(.5, 1.), (1.5, 1.), (2.5, 1.)]
        self.assertEqual(backbeat_candidate(60, snare, snare), 60)

    def test_irregular_and_weak_backbeat_rejected(self):
        kick = [(i * .5, 1.) for i in range(6)]
        self.assertEqual(backbeat_candidate(60, kick, [(.5, 1.), (1.2, 1.), (2.5, 1.)]), 60)
        self.assertEqual(backbeat_candidate(60, kick, [(.5, .1), (1.5, .1), (2.5, .1)]), 60)


if __name__ == "__main__":
    unittest.main()
