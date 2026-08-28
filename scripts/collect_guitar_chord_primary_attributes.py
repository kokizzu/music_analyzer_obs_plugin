#!/usr/bin/env python3
"""Collect structured GuitarSet primary-chord ranking evidence."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "build/guitar_chord_primary_attributes.tsv"


def main() -> int:
    env = os.environ.copy()
    env["MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV"] = str(OUTPUT)
    return subprocess.run(
        ["make", "test-guitar-chord-mix-samples-serial"], cwd=ROOT, env=env, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
