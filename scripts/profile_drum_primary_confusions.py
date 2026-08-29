#!/usr/bin/env python3
"""Run one real drum category with unthresholded primary-class diagnostics."""

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATEGORY = "tom"


def main() -> int:
    category = os.environ.get("DRUM_PROFILE_CATEGORY", DEFAULT_CATEGORY).strip().lower()
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_DRUM_SAMPLES_DIR": "build/drum_samples_spread",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY": category,
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES": category,
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY": "1",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT": "240",
    })
    print(f"category={category}")
    return subprocess.run([str(ROOT / "build" / "analyzer_drum_samples")], cwd=ROOT,
                          env=environment, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
