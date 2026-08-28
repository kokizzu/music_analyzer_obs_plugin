#!/usr/bin/env python3
"""Run the cached GuitarSet corpus with opt-in per-window chord diagnostics."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "guitarset-manifest.tsv"
BINARY = ROOT / "build" / "analyzer_guitarset"
LOG = ROOT / "build" / "guitarset_debug_windows.log"


def main() -> int:
    if not MANIFEST.is_file() or not BINARY.is_file():
        print("run make analyze-guitarset-misses first to prepare GuitarSet diagnostics", file=sys.stderr)
        return 1
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_GUITARSET_MANIFEST": str(MANIFEST),
        "MUSIC_ANALYZER_GUITARSET_REQUIRED": "1",
        "MUSIC_ANALYZER_GUITARSET_USE_ALL": "1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS": "200",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS": "1000",
        "MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT": "8",
        "MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT": "75",
        "MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT": "65",
        "MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT": "75",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS": "1000",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT": "69",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT": "71",
        "MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT": "84",
        "MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT": "52",
        "MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT": "75",
        "MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT": "84",
        "MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT": "65",
        "MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES": "0",
        "MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES": "1",
        "MUSIC_ANALYZER_GUITARSET_VERBOSE_PRIMARY_CHORD_MISSES": "1",
        "MUSIC_ANALYZER_GUITARSET_DEBUG_WINDOWS": "1",
    })
    with LOG.open("w", encoding="utf-8") as log:
        completed = subprocess.run([str(BINARY)], cwd=ROOT, env=environment,
                                   stdout=sys.stdout, stderr=log, check=False)
    print(f"guitarset debug log: {LOG.relative_to(ROOT)}", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
