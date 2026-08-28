#!/usr/bin/env python3
"""Find literal text in a repository path for Make-driven inspection."""

from __future__ import annotations

import sys
from pathlib import Path


SKIP_PARTS = {".git", "build", "__pycache__"}


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("usage: find_repo_text.py ROOT TEXT [MAX_RESULTS]", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    needle = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) == 4 else 100
    found = 0
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        if any(part in SKIP_PARTS for part in path.parts) or not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, start=1):
            if needle not in line:
                continue
            print(f"{path.as_posix()}:{number}:{line}")
            found += 1
            if found >= max_results:
                return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
