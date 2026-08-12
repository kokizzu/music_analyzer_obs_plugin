#!/usr/bin/env python3
"""Regression checks for the instrument-family miss inspector."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "inspect_instrument_family_misses.py"
SPEC = importlib.util.spec_from_file_location("inspect_instrument_family_misses", MODULE_PATH)
assert SPEC and SPEC.loader
INSPECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECTOR)


class InspectInstrumentFamilyMissesTest(unittest.TestCase):
    def test_summarize_aggregates_windows_per_sample(self) -> None:
        header = "\t".join(
            ("sample_id", "family", "instrument", "expected_row_hit")
            + tuple(f"{family}_{suffix}" for family in INSPECTOR.FAMILIES for suffix in ("active", "confidence", "label"))
        )
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "attributes.tsv"
            source.write_text(
                "\n".join(
                    (
                        header,
                        "miss\tvocals\tfemale singer\t0\t1\t0.7\tE3\t0\t0.0\t--\t0\t0.0\t--\t1\t0.8\tC4",
                        "miss\tvocals\tfemale singer\t0\t1\t0.9\tG3\t0\t0.0\t--\t0\t0.0\t--\t1\t1.0\tD4",
                        "hit\tother\tflute\t1\t0\t0.0\t--\t0\t0.0\t--\t0\t0.0\t--\t1\t0.3\tA4",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            lines = INSPECTOR.summarize(source)
        self.assertEqual(lines[0], "instrument_family_miss_summary: misses=1/2")
        self.assertEqual(lines[1], "miss routes vocals/female singer:1")
        self.assertIn("sample=vocals/female singer id=miss buffers=2", lines[2])
        self.assertIn("guitar[active=2/2 max=0.900 labels=E3:1,G3:1]", lines[2])
        self.assertIn("other[active=2/2 max=1.000 labels=C4:1,D4:1]", lines[2])


if __name__ == "__main__":
    unittest.main()
