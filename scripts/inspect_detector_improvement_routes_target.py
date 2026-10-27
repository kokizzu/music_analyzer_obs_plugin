#!/usr/bin/env python3
"""Show the Makefile definition for detector-improvement-routes targets."""
from makefile_source import read_makefile

from pathlib import Path


def main() -> None:
    lines = read_makefile(Path("Makefile"), encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "detector-improvement-routes" not in line and "analyze-detector-improvement-routes" not in line:
            continue
        start = max(0, index - 4)
        end = min(len(lines), index + 16)
        print(f"--- Makefile:{index + 1} ---")
        for position in range(start, end):
            print(f"{position + 1:5}: {lines[position]}")


if __name__ == "__main__":
    main()
