from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_candombe_dataset.py"


class InspectCandombeDatasetTest(unittest.TestCase):
    def test_counts_matching_flac_and_csv_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "candombe"
            (root / "audio").mkdir(parents=True)
            (root / "annotations").mkdir()
            for index in range(35):
                (root / "audio" / f"track-{index:02d}.flac").touch()
                (root / "annotations" / f"track-{index:02d}.csv").write_text("0,1.1\n", encoding="utf-8")
            output = root.parent / "inventory.txt"
            subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--output", str(output)], check=True)
            self.assertIn("direct annotation-name match: 35", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
