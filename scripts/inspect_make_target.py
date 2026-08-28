#!/usr/bin/env python3
"""Print one Makefile target and its recipe for repository diagnostics."""

from pathlib import Path


def main() -> None:
    lines = Path("Makefile").read_text(encoding="utf-8").splitlines()
    for current in range(2835, min(2890, len(lines))):
        print(f"{current + 1:5}: {lines[current]}")


if __name__ == "__main__":
    main()
