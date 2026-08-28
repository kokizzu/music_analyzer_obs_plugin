#!/usr/bin/env python3
"""Stop only the analyzer-case runners listed by the paired report target."""

from __future__ import annotations

import os
import signal
import subprocess


def main() -> int:
    result = subprocess.run(
        ["pgrep", "-f", "build/analyzer_cases"], capture_output=True, text=True, check=False
    )
    pids = [int(value) for value in result.stdout.split() if value.isdigit()]
    for pid in pids:
        os.kill(pid, signal.SIGTERM)
        print(f"stopped analyzer_cases pid={pid}")
    if not pids:
        print("analyzer_cases: no running process")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
