#!/usr/bin/env python3
"""Verify named Makefile targets without invoking make's shell database."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: inspect_make_target_name.py TARGET [TARGET ...]")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    lines = makefile.splitlines()
    missing = []
    for target in sys.argv[1:]:
        marker = f"{target}:"
        matches = [index + 1 for index, line in enumerate(lines) if line.startswith(marker)]
        if not matches:
            missing.append(target)
            continue
        print(f"{target}: lines {', '.join(map(str, matches))}")
    if missing:
        raise SystemExit("missing Makefile targets: " + ", ".join(missing))


if __name__ == "__main__":
    main()
