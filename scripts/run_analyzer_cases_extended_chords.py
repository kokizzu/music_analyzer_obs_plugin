#!/usr/bin/env python3
"""Build and run the focused extended-chord regression group."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    subprocess.run(["make", "build/analyzer_cases"], cwd=ROOT, check=True)
    environment = os.environ.copy()
    environment["MUSIC_ANALYZER_CASE_GROUP"] = "extended-chords"
    return subprocess.run([str(ROOT / "build/analyzer_cases")], cwd=ROOT, env=environment).returncode


if __name__ == "__main__":
    raise SystemExit(main())
