#!/usr/bin/env python3
"""Locate chord-template scoring and simplification logic in the analyzer."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for index in range(10922, min(len(lines), 11105)):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
