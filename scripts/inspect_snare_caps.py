#!/usr/bin/env python3
"""Show every final snare inactive-cap condition in the analyzer."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "cap_drum_level(Snare, 0.28f)" not in line:
            continue
        start = max(0, index - 34)
        end = min(len(lines), index + 5)
        print(f"## {start + 1}-{end}")
        for position in range(start, end):
            print(f"{position + 1}: {lines[position]}")


if __name__ == "__main__":
    main()
