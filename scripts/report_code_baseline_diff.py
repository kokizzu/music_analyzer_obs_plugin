#!/usr/bin/env python3
"""Print the tracked source-only diff before a baseline checkpoint."""

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--", "Makefile", "src", "scripts", "tests", "README.md"],
        cwd=ROOT,
        text=True,
        check=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
