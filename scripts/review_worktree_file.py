#!/usr/bin/env python3
"""Show the reviewable diff or content preview for one worktree path."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: review_worktree_file.py PATH", file=sys.stderr)
        return 2

    path = sys.argv[1]
    tracked = run("ls-files", "--error-unmatch", "--", path).strip()
    if tracked:
        diff = run("diff", "--unified=3", "--", path)
        if diff:
            print(diff[:50000].rstrip())
        else:
            print(run("show", f"HEAD:{path}")[:50000].rstrip())
        return 0

    file_path = ROOT / path
    if not file_path.is_file():
        print(f"not a tracked or regular untracked file: {path}", file=sys.stderr)
        return 1
    print(f"(untracked file preview: {path})")
    print(file_path.read_text(errors="replace")[:50000].rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
