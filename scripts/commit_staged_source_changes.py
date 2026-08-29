#!/usr/bin/env python3
"""Commit an already staged, source-only change set after validating its scope."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {"Makefile", "README.md"}
ALLOWED_PREFIXES = ("android/", "docs/", "scripts/", "src/", "tests/", "third_party/")
MAX_BYTES = 2 * 1024 * 1024


def git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def staged_paths() -> list[str]:
    result = git("diff", "--cached", "--name-only", "-z")
    return [path for path in result.stdout.split("\0") if path]


def validate(paths: list[str]) -> None:
    if not paths:
        raise RuntimeError("no staged files to commit")
    for relative in paths:
        path = ROOT / relative
        if relative not in ROOT_FILES and not relative.startswith(ALLOWED_PREFIXES):
            raise RuntimeError(f"staged file is outside the source-only scope: {relative}")
        if path.is_file() and path.stat().st_size > MAX_BYTES:
            raise RuntimeError(f"staged file exceeds {MAX_BYTES} bytes: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    paths = staged_paths()
    validate(paths)
    print(f"staged_source_files={len(paths)}")
    for relative in paths:
        print(f"+ {relative}")
    result = git("commit", "-m", args.message)
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"commit_staged_source_changes: {error}")
        raise SystemExit(1)
