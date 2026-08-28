#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_gtzan_rhythm_tempo_fixture.py"


class PrepareGtzanRhythmTempoFixtureTest(unittest.TestCase):
    def test_creates_genre_balanced_symlinked_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            audio = root / "audio"
            annotations = root / "annotations" / "jams"
            annotations.mkdir(parents=True)
            for index in range(900):
                genre = "blues" if index % 2 == 0 else "jazz"
                directory = audio / genre
                directory.mkdir(parents=True, exist_ok=True)
                (directory / f"{genre}.{index:05d}.wav").touch()
            beats = [{"time": number * 0.5} for number in range(41)]
            for genre in ("blues", "jazz"):
                (annotations / f"{genre}.0000{0 if genre == 'blues' else 1}.wav.jams").write_text(
                    json.dumps({"annotations": [{"namespace": "beat", "data": beats}]}),
                    encoding="utf-8",
                )
            external_fixture = root / "external-fixture"
            external_fixture.mkdir()
            (external_fixture / "stale.txt").write_text("stale", encoding="utf-8")
            output = root / "fixture"
            output.symlink_to(external_fixture, target_is_directory=True)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--audio-root",
                    str(audio),
                    "--annotations-root",
                    str(root / "annotations"),
                    "--output",
                    str(output),
                    "--limit",
                    "2",
                ],
                check=True,
            )

            with (output / "maestro-v3.0.0.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(2, len(rows))
            self.assertTrue(output.is_symlink())
            self.assertFalse((external_fixture / "stale.txt").exists())
            self.assertTrue((output / rows[0]["audio_filename"]).is_symlink())
            self.assertEqual(b"MThd", (output / rows[0]["midi_filename"]).read_bytes()[:4])


if __name__ == "__main__":
    unittest.main()
