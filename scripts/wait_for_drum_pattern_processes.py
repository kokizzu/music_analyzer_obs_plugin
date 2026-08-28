#!/usr/bin/env python3
"""Wait briefly for the drum pattern miner to finish without starting another run."""

from __future__ import annotations

import subprocess
import time


def running() -> bool:
    return subprocess.run(
        ["pgrep", "-f", "build/analyzer_drum_samples"], check=False
    ).returncode == 0


def main() -> int:
    deadline = time.monotonic() + 120.0
    while running() and time.monotonic() < deadline:
        time.sleep(5.0)
    print("drum_pattern_analysis: " + ("running" if running() else "complete"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
