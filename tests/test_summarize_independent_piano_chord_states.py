#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_independent_piano_chord_states.py"
SPEC = importlib.util.spec_from_file_location("independent_piano_states", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class IndependentPianoStatesTest(unittest.TestCase):
    def write(self, path: Path, rows: list[tuple[str, str, str, str, str, str, str]]):
        path.write_text(
            "expected_chords\tchord_hit\tkeyboard_chord\tdetected_chord_pcs\tchord_debug\tmissing_pcs\textra_pcs\n"
            + "\n".join("\t".join(row) for row in rows)
            + "\n",
            encoding="utf-8",
        )

    def test_reports_only_shared_runtime_states(self):
        debug = "clusters=3 templates=0 conflicts=0 selected=1"
        other = "clusters=2 templates=1 conflicts=0 selected=0"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "maps.tsv"
            second = root / "maestro.tsv"
            self.write(first, [("C", "0", "--", "C,E,G", debug, "--", "--"), ("D", "1", "D", "D,F#,A", other, "--", "--")])
            self.write(second, [("C", "0", "--", "C,E,G", debug, "--", "--"), ("E", "0", "F", "E,G#,B", debug, "--", "C")])
            lines = MODULE.render([first, second], 1, 10)
        self.assertEqual(
            lines[0],
            "independent_piano_chord_states: corpora=2 shared_no_label_states=1 complete_pcs_recovery_candidates=1",
        )
        self.assertIn("pcs=3 clusters=3 templates=0 conflicts=0 selected=1", lines[1])
        self.assertIn("maps.tsv:hit/no_label/complete_pcs/wrong=0/1/1/0", lines[1])
        self.assertIn("maestro.tsv:hit/no_label/complete_pcs/wrong=0/1/1/1", lines[1])


if __name__ == "__main__":
    unittest.main()
