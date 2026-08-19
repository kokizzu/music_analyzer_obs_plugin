from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_candombe_tempo_fixture.py"


class PrepareCandombeTempoFixtureTest(unittest.TestCase):
    def test_creates_tempo_fixture_from_stable_expert_beats(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "candombe"
            (source / "audio").mkdir(parents=True)
            (source / "annotations").mkdir()
            for index in range(35):
                (source / "audio" / f"track-{index:02d}.flac").write_bytes(b"source")
                (source / "annotations" / f"track-{index:02d}.csv").write_text("\n".join(f"{step * .5:.3f},1.{step % 4 + 1}" for step in range(41)), encoding="utf-8")
            ffmpeg = root / "fake-ffmpeg"
            ffmpeg.write_text("#!/usr/bin/env sh\ncp \"$6\" \"$7\"\n", encoding="utf-8")
            ffmpeg.chmod(0o755)
            output = root / "fixture"
            subprocess.run([sys.executable, str(SCRIPT), "--root", str(source), "--output", str(output), "--ffmpeg", str(ffmpeg)], check=True)
            with (output / "maestro-v3.0.0.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(35, len(rows))
            self.assertEqual(b"MThd", (output / rows[0]["midi_filename"]).read_bytes()[:4])
            self.assertTrue((output / rows[0]["audio_filename"]).is_file())


if __name__ == "__main__":
    unittest.main()
