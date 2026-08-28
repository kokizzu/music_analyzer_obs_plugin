#!/usr/bin/env python3
"""Commit and push only the staged Fret Zealot final-frame settle fix."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if staged != [EXPECTED]:
        raise RuntimeError(f"refusing to commit mixed staged files: {staged}")
    run(["git", "commit", "-m", "Prevent interleaved Fret Zealot scale frames"])
    run(["git", "push"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
