#!/usr/bin/env python3
"""Show the exact Fret Zealot batching changes intended for staging."""

from __future__ import annotations

import subprocess


PATHS = (
    "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
    "tests/check_android_project.py",
    "tests/check_fret_zealot_auto_root_guard.py",
)


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--", *PATHS], check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stderr, end="")
        return result.returncode
    print(result.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
