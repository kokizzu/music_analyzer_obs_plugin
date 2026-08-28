#!/usr/bin/env python3
"""Print the analyzer-case test runner entrypoint for focused-run support."""

from pathlib import Path


def main() -> None:
    path = Path("tests/analyzer_cases.cpp")
    lines = path.read_text(encoding="utf-8").splitlines()
    start = max(0, len(lines) - 220)
    print(f"== {path}:{start + 1}-{len(lines)} ==")
    for index in range(start, len(lines)):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
