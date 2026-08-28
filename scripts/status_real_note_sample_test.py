#!/usr/bin/env python3
"""Report whether the long real-note regression runner is still active."""

from __future__ import annotations

import subprocess


def main() -> int:
    result = subprocess.run(
        ["pgrep", "-af", "analyzer_real_note_samples"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("real-note regression: running")
        print(result.stdout, end="")
        return 0
    print("real-note regression: not running")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
