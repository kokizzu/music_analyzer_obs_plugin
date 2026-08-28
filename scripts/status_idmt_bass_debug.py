#!/usr/bin/env python3
"""Report active focused IDMT bass diagnostic processes."""

from __future__ import annotations

import subprocess


def main() -> int:
    result = subprocess.run(
        ["pgrep", "-af", "run_idmt_bass_single_track_measurement.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("IDMT bass diagnostic: running")
        print(result.stdout, end="")
    else:
        print("IDMT bass diagnostic: not running")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
