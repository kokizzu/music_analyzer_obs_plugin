#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_independent_piano_exact_chord_fallback.py"
SPEC = importlib.util.spec_from_file_location("piano_fallback", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ExactChordFallbackAuditTest(unittest.TestCase):
    def write(self, path: Path, rows: list[tuple[str, str, str]]):
        path.write_text(
            "expected_chords\tkeyboard_chord\tdetected_chord_pcs\n" +
            "\n".join("\t".join(row) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_reports_only_replicated_zero_error_fallbacks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, second = root / "maps.tsv", root / "maestro.tsv"
            self.write(first, [("C", "--", "C,E,G"), ("C", "--", "C,E,G"),
                               ("Dm", "--", "D,F,A")])
            self.write(second, [("C", "--", "C,E,G"), ("C", "--", "C,E,G"),
                                ("A", "--", "D,F,A")])
            lines = MODULE.render([first, second], 2)
        self.assertEqual(lines[0], "independent_piano_exact_chord_fallback: corpora=2 shared_runtime_safe=1")
        self.assertEqual(lines[1], "  candidate=C maps.tsv:2/2 maestro.tsv:2/2")


if __name__ == "__main__":
    unittest.main()
