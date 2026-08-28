#!/usr/bin/env python3
"""Locate the supported verbose/debug controls in the drum fixture runner."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "tests/analyzer_drum_samples.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed_until = -1
    for index, line in enumerate(lines):
        lowered = line.lower()
        if "verbose" not in lowered and "debug" not in lowered and "getenv" not in lowered:
            continue
        start = max(0, index - 3)
        end = min(len(lines), index + 4)
        if start <= printed_until:
            continue
        for current in range(start, end):
            print(f"{current + 1:5}: {lines[current]}")
        print()
        printed_until = end - 1


if __name__ == "__main__":
    main()
