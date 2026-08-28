#!/usr/bin/env python3
"""Show uncommitted Fret Zealot transport changes without shell composition."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java",
    "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
    "src/fret_control.cpp",
    "src/fret_control.h",
    "tests/fret_control.cpp",
)


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--", *PATHS], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    sys.stdout.write(result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
