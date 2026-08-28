#!/usr/bin/env python3
"""Print the unstaged Fret Zealot controller diff for narrow commit review."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
    "tests/check_fret_zealot_frame_settle.py",
)


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--", *PATHS], cwd=ROOT, text=True, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
