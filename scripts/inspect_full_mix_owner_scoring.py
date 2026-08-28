#!/usr/bin/env python3
"""Print the full-mix owner scoring branch around vocal promotion."""

from __future__ import annotations

import pathlib


SOURCE = pathlib.Path("src/analyzer.cpp")
START = 10530
END = 10680


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for number in range(START, min(END, len(lines)) + 1):
        print(f"{number}: {lines[number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
