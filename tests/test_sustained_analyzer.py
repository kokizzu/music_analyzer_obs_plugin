#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("sustained", Path(__file__).resolve().parents[1] / "scripts/measure_sustained_analyzer.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Tests(unittest.TestCase):
    def rows(self):
        return [dict(end_sample=str(i * 2400), hop_index=str(i), sequence="0", wall_ms=str(ms), cpu_ms="1",
                     rss_kb="1024", chord=chord, guitar="", voice="", drums="")
                for i, (ms, chord) in enumerate([(1, "A"), (60, "B"), (2, "A")], 1)]

    def test_deadline_and_reversal(self):
        result = module.summarize(self.rows(), 48000)
        self.assertEqual(result["deadline_misses"], 1)
        self.assertEqual(result["one_hop_reversals"]["chord"], 1)
        self.assertEqual(result["transitions"]["chord"], 2)

    def test_dropped_hop_rejected(self):
        with self.assertRaises(AssertionError):
            module.summarize(self.rows()[1:], 48000)

    def test_duplicate_hop_rejected(self):
        rows = self.rows()
        rows[1]["hop_index"] = "1"
        with self.assertRaises(AssertionError):
            module.summarize(rows, 48000)

    def test_fractional_sample_hop_matches_cpp_rounding(self):
        rows = self.rows()
        for i, row in enumerate(rows, 1):
            row["end_sample"] = str(i * 1103)
        self.assertEqual(module.summarize(rows, 22050)["frames"], 3)


if __name__ == "__main__":
    unittest.main()
