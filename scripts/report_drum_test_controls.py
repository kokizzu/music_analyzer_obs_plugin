#!/usr/bin/env python3
"""List drum-test environment controls declared by the real-sample harness."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "analyzer_drum_samples.cpp"


def main() -> int:
    controls = sorted(set(re.findall(r'"(MUSIC_ANALYZER_DRUM_[A-Z0-9_]+)"',
                                     SOURCE.read_text(encoding="utf-8"))))
    for control in controls:
        print(control)
    return 0


if __name__ == "__main__":
    sys.exit(main())
