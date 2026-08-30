#!/usr/bin/env python3
"""Regression test for a low Bass fundamental misclassified as Guitar/Keyboard octaves."""

import os
import re
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BINARY = REPO / "build" / "analyzer_real_note_samples"
SAMPLE_ID = "idmt_bass_lines_004_040_E1_FS_NO"


def main() -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(REPO / "build" / "real_instrument_expansion_samples"),
            "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": SAMPLE_ID,
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "100",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES": "100",
        }
    )
    completed = subprocess.run([str(BINARY)], cwd=REPO, env=environment, text=True, capture_output=True, check=False)
    output = completed.stdout + completed.stderr
    if completed.returncode:
        raise SystemExit(output)
    debug_lines = [line for line in output.splitlines() if line.startswith("debug sample=")]
    if any(re.search(r"\bbass=[^\[]*\bE1\b", line) for line in debug_lines):
        print("idmt-low-bass-octave-stack: E1 recovered")
        return
    raise SystemExit("E1 missing from Bass row\n" + "\n".join(debug_lines))


if __name__ == "__main__":
    main()
