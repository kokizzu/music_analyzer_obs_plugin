#!/usr/bin/env python3
"""Print hi-hat/ride arbitration blocks from the analyzer."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for current in range(35150, min(35420, len(lines))):
        print(f"{current + 1:5}: {lines[current]}")


if __name__ == "__main__":
    main()
