#!/usr/bin/env python3
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_cross_corpus_chord_evidence.py"


class CrossCorpusChordEvidenceTest(unittest.TestCase):
    def write_tsv(self, path, chord_column, rows):
        path.write_text(
            "expected_chords\tchord_hit\t" + chord_column + "\n" +
            "\n".join("\t".join(row) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_reports_common_outcomes_for_keyboard_and_guitar(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = pathlib.Path(directory)
            maps = directory / "maps.tsv"
            guitar = directory / "guitar.tsv"
            self.write_tsv(maps, "keyboard_chord", [("C", "1", "C"), ("D", "0", "--"), ("E", "0", "F")])
            self.write_tsv(guitar, "guitar_chord", [("G", "1", "G"), ("A", "0", "--"), ("B", "0", "C")])
            result = subprocess.run(["python3", str(SCRIPT), str(maps), str(guitar)], text=True, capture_output=True, check=True)
        self.assertIn("maps.tsv: hit=1/3 (33.3%) no_label=1/3 (33.3%) wrong_label=1/3 (33.3%)", result.stdout)
        self.assertIn("replicated_miss_no_label: 2/2 (100.0%)", result.stdout)
        self.assertIn("replicated_miss_wrong_label: 2/2 (100.0%)", result.stdout)

    def test_ignores_blank_expected_chord_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = pathlib.Path(directory)
            maps = directory / "maps.tsv"
            guitar = directory / "guitar.tsv"
            # The two-field MAPS row intentionally leaves keyboard_chord blank;
            # DictReader represents that trailing cell as None.
            self.write_tsv(maps, "keyboard_chord", [("", "0"), ("C", "1", "C")])
            self.write_tsv(guitar, "guitar_chord", [("G", "1", "G")])
            result = subprocess.run(
                ["python3", str(SCRIPT), str(maps), str(guitar)],
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertIn("maps.tsv: hit=1/1 (100.0%)", result.stdout)


if __name__ == "__main__":
    unittest.main()
