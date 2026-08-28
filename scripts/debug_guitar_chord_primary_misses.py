#!/usr/bin/env python3
"""Run the serial GuitarSet corpus with primary-chord mismatch diagnostics."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    env = os.environ.copy()
    env["MUSIC_ANALYZER_GUITARSET_VERBOSE_PRIMARY_CHORD_MISSES"] = "1"
    return subprocess.run(
        ["make", "test-guitar-chord-mix-samples-serial"], cwd=ROOT, env=env, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
