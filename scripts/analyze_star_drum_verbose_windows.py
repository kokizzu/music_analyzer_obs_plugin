#!/usr/bin/env python3
"""Write all prepared STAR drum windows with analyzer debug details."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / "analyzer_egmd"
SAMPLES = ROOT / "build" / "star_drums_preview_samples"
SUMMARY = ROOT / "build" / "star_drums_verbose_windows.log.summary"
LOG = ROOT / "build" / "star_drums_verbose_windows.log"


def main() -> int:
    if not BINARY.is_file() or not SAMPLES.is_dir():
        raise SystemExit("STAR analyzer inputs are missing; run make test-star-drums-samples-parallel first")
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_EGMD_ROOT": str(SAMPLES),
        "MUSIC_ANALYZER_EGMD_REQUIRED": "1",
        "MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS": "4",
        "MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS": "12",
        "MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT": "0",
        "MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT": "100",
        "MUSIC_ANALYZER_EGMD_VERBOSE_WINDOWS": "1",
        "MUSIC_ANALYZER_EGMD_VERBOSE_WINDOW_LIMIT": "4000",
    })
    with SUMMARY.open("w", encoding="utf-8") as stdout, LOG.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run([str(BINARY)], cwd=ROOT, env=environment, stdout=stdout, stderr=stderr)
    print(f"STAR verbose drum windows: {LOG.relative_to(ROOT)}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
