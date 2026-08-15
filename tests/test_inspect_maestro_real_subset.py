#!/usr/bin/env python3
"""Regression check for the non-mutating MAESTRO subset inspector."""

from __future__ import annotations

import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_maestro_real_subset.py"


class InspectMaestroRealSubsetTests(unittest.TestCase):
    def test_counts_only_complete_wav_midi_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (root / "maestro-v3.0.0.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["audio_filename", "midi_filename"])
                writer.writeheader()
                writer.writerow({"audio_filename": "a.wav", "midi_filename": "a.mid"})
                writer.writerow({"audio_filename": "b.wav", "midi_filename": "b.mid"})
            (root / ".maps_piano_signature").write_text("ready", encoding="utf-8")
            (root / "a.wav").touch()
            (root / "a.mid").touch()
            (root / "b.wav").touch()
            result = subprocess.run(["python3", str(SCRIPT), str(root)], check=True, text=True, capture_output=True)
        self.assertIn("metadata_rows=2 paired_files=1/2 signature=present", result.stdout)


if __name__ == "__main__":
    unittest.main()
