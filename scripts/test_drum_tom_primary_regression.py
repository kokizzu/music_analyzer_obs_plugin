#!/usr/bin/env python3
"""Require measured toms to win primary arbitration at a useful floor."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_DRUM_SAMPLES_DIR": "build/drum_samples_spread",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY": "tom",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES": "tom",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT": "84",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT": "75",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT": "95",
    })
    result = subprocess.run([str(ROOT / "build" / "analyzer_drum_samples")], cwd=ROOT, env=environment)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
