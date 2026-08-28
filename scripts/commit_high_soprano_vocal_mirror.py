#!/usr/bin/env python3
"""Commit and push only the staged high-soprano vocal mirror repair."""

from __future__ import annotations

import subprocess


EXPECTED = [
    "src/analyzer.hpp",
    "src/analyzer.cpp",
    "Makefile",
    "tests/test_high_soprano_vocal_mirror.py",
    "scripts/summarize_high_soprano_mirror_result.py",
]


def main() -> int:
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True,
                            text=True, stdout=subprocess.PIPE).stdout.splitlines()
    if staged != EXPECTED:
        raise RuntimeError(f"refusing mixed commit: {staged}")
    subprocess.run(["git", "commit", "-m", "Enable measured high-soprano vocal recovery"], check=True)
    subprocess.run(["git", "push"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
