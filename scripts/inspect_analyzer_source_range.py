#!/usr/bin/env python3
"""Print a stable numbered range from the analyzer for Makefile-backed debugging."""

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: inspect_analyzer_source_range.py START END")
    start, end = (int(value) for value in sys.argv[1:])
    if start < 1 or end < start:
        raise SystemExit("invalid source range")
    lines = Path("src/analyzer.cpp").read_text().splitlines()
    for number in range(start, min(end, len(lines)) + 1):
        print(f"{number}: {lines[number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
