#!/usr/bin/env python3
"""Regression checks for isolated Guitar visual-row summaries."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "summarize_isolated_guitar_visual.py"
SPEC = importlib.util.spec_from_file_location("summarize_isolated_guitar_visual", MODULE_PATH)
assert SPEC and SPEC.loader
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


class IsolatedGuitarVisualTest(unittest.TestCase):
    def test_counts_exact_expected_notes_per_buffer_and_sample(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            attributes = Path(temporary) / "attributes.tsv"
            attributes.write_text(
                "sample_id\tfamily\texpected_note\tguitar_visual_notes\n"
                "one\tguitar\tE3\tE3:0.7\n"
                "one\tguitar\tE3\t--\n"
                "two\tguitar\tA3\t--\n"
                "ignore\tbass\tE2\tE2:0.9\n",
                encoding="utf-8",
            )
            self.assertEqual(
                SUMMARY.summarize(attributes, "Fixture"),
                "isolated_guitar_visual: source=Fixture buffers=1/3 samples=1/2",
            )


if __name__ == "__main__":
    unittest.main()
