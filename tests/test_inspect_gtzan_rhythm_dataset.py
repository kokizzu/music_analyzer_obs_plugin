#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_gtzan_rhythm_dataset.py"


class InspectGtzanRhythmDatasetTest(unittest.TestCase):
    def test_reports_audio_and_annotation_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "gtzan_rhythm"
            audio = root / "audio"
            annotations = root / "annotations"
            audio.mkdir(parents=True)
            annotations.mkdir(parents=True)
            for index in range(900):
                (audio / f"blues.{index:05d}.wav").touch()
            (annotations / "blues.00000.beats").write_text("0.0\n", encoding="utf-8")
            output = Path(temporary) / "inventory.txt"

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("audio files: 900", completed.stdout)
            self.assertIn("annotation files: 1", output.read_text(encoding="utf-8"))
            self.assertIn("audio stems with direct annotation-name match: 1", completed.stdout)

    def test_rejects_incomplete_audio_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "gtzan_rhythm"
            (root / "audio").mkdir(parents=True)
            (root / "annotations").mkdir(parents=True)
            (root / "audio" / "blues.00000.wav").touch()
            (root / "annotations" / "blues.00000.beats").write_text("0.0\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--output", str(Path(temporary) / "out")],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("expected at least 900 audio files", completed.stderr)


if __name__ == "__main__":
    unittest.main()
