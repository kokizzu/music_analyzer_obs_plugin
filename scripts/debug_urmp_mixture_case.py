#!/usr/bin/env python3
"""Replay one annotated URMP mixture case with analyzer debug output."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ANALYZER = ROOT / "build" / "analyzer_real_note_samples"
FIXTURES = ROOT / "build" / "urmp_mixture_cases"
DEFAULT_CASE = "17_Nocturne_vn_fl_cl_10_01"


def main() -> None:
    if not ANALYZER.is_file():
        raise SystemExit(f"missing analyzer test binary: {ANALYZER}")
    if not FIXTURES.is_dir():
        raise SystemExit(f"missing URMP mixture fixtures: {FIXTURES}")
    case_id = os.environ.get("URMP_MIXTURE_CASE", DEFAULT_CASE)
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(FIXTURES),
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
            "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": case_id,
            "MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES": "1",
        }
    )
    result = subprocess.run([str(ANALYZER)], cwd=ROOT, env=environment, check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
