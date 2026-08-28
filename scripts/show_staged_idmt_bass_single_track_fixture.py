#!/usr/bin/env python3
"""Show the staged compact-IDMT fixture diff for review."""

from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    return subprocess.run(["git", "diff", "--cached", "--stat"], cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
