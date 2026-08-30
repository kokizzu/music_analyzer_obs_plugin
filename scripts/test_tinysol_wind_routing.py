#!/usr/bin/env python3
"""Regression test for a sustained Alto Sax note routed out of Other."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path("build/real_instrument_expansion_samples")
BINARY = Path("build/analyzer_real_note_samples")
SAMPLE_ID = "tinysol_alto-saxophone_ASax-ord-B4-ff-N"


def main() -> int:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
        "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": SAMPLE_ID,
    })
    completed = subprocess.run([str(BINARY)], env=environment, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    lines = [line for line in (completed.stdout + completed.stderr).splitlines() if line.startswith("debug sample=")]
    if not any(re.search(r"\bother=([^\[]*\bB4\b[^\[]*)\[", line) for line in lines):
        raise RuntimeError("Alto Sax B4 is not recovered in Other")
    print("tinysol-wind-routing: Alto Sax B4 reaches Other")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"tinysol-wind-routing: {error}", file=sys.stderr)
        raise SystemExit(1)
