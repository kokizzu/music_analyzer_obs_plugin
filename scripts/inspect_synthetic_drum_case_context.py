#!/usr/bin/env python3
"""Print synthetic drum assertions and their nearby setup in analyzer_cases."""

from pathlib import Path


NEEDLES = (
    "soft drum transient stream",
    "low-body snare transient",
    "kick-backed snare transient",
    "bright snare transient",
    "low-kick one-shot snare sample",
)


def main() -> None:
    lines = Path("tests/analyzer_cases.cpp").read_text(encoding="utf-8").splitlines()
    ranges: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not any(needle in line for needle in NEEDLES):
            continue
        start = max(0, index - 55)
        end = min(len(lines), index + 16)
        if ranges and start <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
        else:
            ranges.append((start, end))
    for start, end in ranges:
        print(f"## {start + 1}-{end}")
        for position in range(start, end):
            print(f"{position + 1}: {lines[position]}")


if __name__ == "__main__":
    main()
