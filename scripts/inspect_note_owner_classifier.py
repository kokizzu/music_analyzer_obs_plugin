#!/usr/bin/env python3
"""Print source context for the note instrument-owner scoring and arbitration paths."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
CONTEXT = 340


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed: set[int] = set()
    for index, line in enumerate(lines):
        normalized = line.strip()
        if "scores[0] / total" not in normalized:
            continue
        start = max(0, index - CONTEXT)
        end = min(len(lines), index + CONTEXT + 1)
        if any(number in printed for number in range(start, end)):
            continue
        print(f"== line {index + 1} ==")
        for number in range(start, end):
            printed.add(number)
            print(f"{number + 1}: {lines[number]}")


if __name__ == "__main__":
    main()
