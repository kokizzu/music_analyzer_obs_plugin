#!/usr/bin/env python3
"""Unit tests for the deterministic Pixabay direct-MP3 resolver."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "resolve_pixabay_rimshot_candidate.py"
SPEC = importlib.util.spec_from_file_location("resolve_pixabay_rimshot_candidate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ResolvePixabayRimshotCandidateTest(unittest.TestCase):
    def test_resolves_one_encoded_mp3_when_all_source_labels_match(self) -> None:
        page = (
            "RimShot-f gnuoctathorpe Free for use "
            "https%3A%2F%2Fcdn.pixabay.com%2Fdownload%2Faudio%2F2022%2F01%2F01%2Fa.mp3?x=1"
        )
        self.assertEqual(
            MODULE.resolve_page("https://pixabay.example/rim", ("RimShot-f", "gnuoctathorpe", "Free for use"), page),
            "https://cdn.pixabay.com/download/audio/2022/01/01/a.mp3?x=1",
        )

    def test_rejects_missing_source_label(self) -> None:
        with self.assertRaisesRegex(ValueError, "no longer identifies"):
            MODULE.resolve_page("https://pixabay.example/rim", ("RimShot-f",), "other text")


if __name__ == "__main__":
    unittest.main()
