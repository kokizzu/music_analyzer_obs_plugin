#!/usr/bin/env python3
"""Regression checks for SATB raw missing-pitch evidence summaries."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "inspect_satb_missing_pitch_evidence.py"
SPEC = importlib.util.spec_from_file_location("inspect_satb_missing_pitch_evidence", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SatbMissingPitchEvidenceTest(unittest.TestCase):
    def test_summarize_counts_missing_and_extra_raw_chroma(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attributes.tsv"
            path.write_text(
                "missing_pcs\textra_pcs\traw_chroma\n"
                "E B\tF#\tE:18 B:5 F#:30\n"
                "C\tD#\tC:0 D#:10\n",
                encoding="utf-8",
            )
            rendered = "\n".join(AUDIT.summarize("DCS", path))
            self.assertIn("missing_pcs=3 extra_pcs=2", rendered)
            self.assertIn("missing raw-chroma p50=5.0", rendered)
            self.assertIn(">=18:1/3", rendered)
            self.assertIn("extra raw-chroma p50=10.0", rendered)


if __name__ == "__main__":
    unittest.main()
