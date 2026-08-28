#!/usr/bin/env python3
"""Show worktree status and the paths owned by MIR-1K fixture work."""

from __future__ import annotations

import subprocess


OWNED_PREFIXES = (
    "Makefile",
    "scripts/",
    "tests/fixtures/mir1k_clean_vocals/",
)


def main() -> int:
    result = subprocess.run(["git", "status", "--short"], check=True, text=True, capture_output=True)
    print("worktree status:")
    print(result.stdout.rstrip() or "clean")
    print("\nMIR-1K candidate paths:")
    for line in result.stdout.splitlines():
        path = line[3:]
        if path in OWNED_PREFIXES or path.startswith(OWNED_PREFIXES[1]) or path.startswith(OWNED_PREFIXES[2]):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
