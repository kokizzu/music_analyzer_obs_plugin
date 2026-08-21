#!/usr/bin/env python3
"""Tests for isolated Rimshot result parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_pixabay_rimshot_measurement.py"
SPEC = importlib.util.spec_from_file_location("inspect_pixabay_rimshot_measurement", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PixabayRimshotMeasurementTests(unittest.TestCase):
    def test_reports_detected_but_snare_primary(self) -> None:
        text = (
            "  expected rim   kick=0 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=1\n"
            "  expected rim   kick=0 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=0 ambiguous=0 none=0\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "measurement.log"
            path.write_text(text, encoding="utf-8")
            rendered = "\n".join(MODULE.render(path))
        self.assertEqual(rendered, "pixabay_rimshot_measurement: detected=1/1 primary=0/1 snare_primary=1/1")


if __name__ == "__main__":
    unittest.main()
