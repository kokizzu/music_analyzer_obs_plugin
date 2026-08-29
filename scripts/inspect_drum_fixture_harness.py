#!/usr/bin/env python3
"""Locate drum-fixture filters and hi-hat assertions in the sample test harness."""

from pathlib import Path


def main() -> int:
    path = Path("tests/analyzer_instrument_samples.cpp")
    lines = path.read_text().splitlines()
    needles = ("DRUM", "hihat", "HiHat", "drum kit", "env_filter", "filter_matches")
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if not any(needle in line for needle in needles):
            continue
        start = max(0, index - 3)
        if start in seen:
            continue
        seen.add(start)
        print(f"# {path}:{index + 1}")
        for number in range(start, min(len(lines), index + 18)):
            print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
