#!/usr/bin/env python3
"""Commit and push only the staged ambiguous shared-display recovery change."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = sorted(("Makefile", "src/analyzer.cpp", "tests/test_ambiguous_display_recovery.py"))


def main() -> int:
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.splitlines()
    if sorted(staged) != EXPECTED:
        raise RuntimeError(f"refusing to commit mixed staged files: {staged}")
    subprocess.run(["git", "commit", "-m", "Recover ambiguous keyboard and guitar notes"],
                   cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
