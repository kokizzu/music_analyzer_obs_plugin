#!/usr/bin/env python3
"""Print global chord tracking updates and display overrides."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "global_chord_tracking_" not in line:
            continue
        for current in range(max(0, index - 10), min(len(lines), index + 20)):
            print(f"{current + 1:5}: {lines[current]}")
        print()


if __name__ == "__main__":
    main()
