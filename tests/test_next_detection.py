#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("next_detection", Path(__file__).resolve().parents[1] / "scripts/evaluate_next_detection.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Tests(unittest.TestCase):
    def test_empty_tempo_does_not_invent_estimate(self):
        self.assertEqual(module.tempo_candidate(0, []), 0)
        self.assertEqual(module.tempo_candidate(120, []), 120)

    def test_grid_prefers_filled_beats_over_double_with_empty_cells(self):
        peaks = [(i * .6, 1., 1., 1) for i in range(5)]
        self.assertGreater(module.tempo_grid(peaks, 100), module.tempo_grid(peaks, 200))
        self.assertEqual(module.tempo_candidate(50, peaks), 100)

    def test_amplitude_invariance(self):
        peaks = [(i * .5, .2, 1., 1) for i in range(6)]
        loud = [(t, v * 4, q, s) for t, v, q, s in peaks]
        self.assertAlmostEqual(module.tempo_grid(peaks, 120), module.tempo_grid(loud, 120))

    def test_missing_third_penalty(self):
        chroma = [0.] * 12
        chroma[0] = chroma[3] = chroma[7] = 1.
        self.assertGreater(module.chord_score("Cm", chroma), module.chord_score("C", chroma))
        self.assertEqual(module.chord_template("C/E"), None)

    def test_enharmonic_template(self):
        self.assertEqual(module.chord_template("C#dim"), module.chord_template("Dbdim"))


if __name__ == "__main__":
    unittest.main()
