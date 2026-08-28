#!/usr/bin/env python3
"""Print full-mix ownership diagnostics for one manifest sample id."""

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: debug_real_note_sample.py [SAMPLE_ID]", file=sys.stderr)
        return 2
    sample_id = sys.argv[1] if len(sys.argv) == 2 else "keyboard_electronic_001-045-050"
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": sample_id,
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT": "100",
    })
    return subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")],
                          cwd=ROOT, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
