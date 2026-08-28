#!/usr/bin/env python3
"""Print the exact verbose per-sample output format used by drum tests."""

from pathlib import Path


def main() -> None:
    lines = Path("tests/analyzer_drum_samples.cpp").read_text(encoding="utf-8").splitlines()
    for current in range(720, min(800, len(lines))):
        print(f"{current + 1:5}: {lines[current]}")


if __name__ == "__main__":
    main()
