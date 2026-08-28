#!/usr/bin/env python3
"""Report whether the compact-IDMT bass measurement is still running."""

from __future__ import annotations

import subprocess


def main() -> int:
    result = subprocess.run(
        ["pgrep", "-af", "analyzer_real_note_samples|run_idmt_bass_single_track_measurement.py"],
        text=True,
        capture_output=True,
        check=False,
    )
    print(result.stdout.rstrip() or "no active compact IDMT bass measurement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
