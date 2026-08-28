#!/usr/bin/env python3
"""Guard against a low electronic-piano note being mirrored as guitar."""

import csv
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = "keyboard_electronic_001-045-050"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="music-analyzer-piano-shadow-") as directory:
        output = Path(directory) / "attributes.tsv"
        env = os.environ.copy()
        env.update({
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_FILTER": SAMPLE,
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(output),
        })
        completed = subprocess.run(
            [str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT, env=env,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode:
            return completed.returncode
        with output.open(encoding="utf-8", newline="") as stream:
            rows = [
                row for row in csv.DictReader(stream, delimiter="\t")
                if row.get("sample_id") == SAMPLE
            ]
    if not rows:
        raise SystemExit(f"fixture {SAMPLE} did not produce analysis rows")
    first = min(rows, key=lambda row: int(row.get("buffer", "0")))
    if "A2:" in first.get("guitar_notes", ""):
        raise SystemExit("low electronic piano A2 must not be mirrored into the guitar row")
    print("low electronic piano guitar-shadow regression: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
