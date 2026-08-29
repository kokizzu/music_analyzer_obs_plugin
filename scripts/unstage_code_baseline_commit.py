#!/usr/bin/env python3
"""Unstage only source-scope files so the baseline commit target can stage them itself."""

from pathlib import Path
import subprocess


ALLOWED_PREFIXES = ("src/", "tests/", "scripts/", "docs/", "android/")
ALLOWED_FILES = {"Makefile", "README.md", "CMakeLists.txt", ".gitignore"}


def source_scope(path: str) -> bool:
    return path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES)


def main() -> None:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=True,
        text=True,
        capture_output=True,
    )
    paths = [path for path in result.stdout.splitlines() if source_scope(path)]
    if not paths:
        print("unstaged=0")
        return
    subprocess.run(["git", "restore", "--staged", "--", *paths], check=True)
    print(f"unstaged={len(paths)}")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
