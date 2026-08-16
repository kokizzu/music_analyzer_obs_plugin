#!/usr/bin/env python3
"""Tests for cross-corpus dominant-seventh extension auditing."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_dominant_seventh_extensions", ROOT / "scripts" / "audit_dominant_seventh_extensions.py"
)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class DominantSeventhAuditTest(unittest.TestCase):
    def test_musicnet_percent_chroma_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "musicnet.tsv"
            path.write_text(
                "expected_chords\tglobal_chord\tchord_hit\tdetected_pcs\traw_chroma\n"
                "E7\tE\t0\tD E G# B\tD:25 E:100 G#:69 B:36\n",
                encoding="utf-8",
            )
            self.assertEqual(AUDIT.audit(path, 0.25), AUDIT.Counts(1, 1, 0))

    def test_guitar_row_counts_a_false_replacement_as_regression(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "guitar.tsv"
            path.write_text(
                "expected_chords\tglobal_chord\tchord_hit\tguitar_pitch_classes\traw_pitch_class_levels\n"
                "E\tE\t1\tD,E,G#,B\tD:0.30 E:1.00 G#:0.70 B:0.40\n",
                encoding="utf-8",
            )
            self.assertEqual(AUDIT.audit(path, 0.25), AUDIT.Counts(1, 0, 1))


if __name__ == "__main__":
    unittest.main()
