#!/usr/bin/env python3
"""Print the analyzer's drum-score construction and primary arbitration context."""

from pathlib import Path


NEEDLES = (
    "boost_drum_level(Snare",
    "promote_drum_primary(Snare",
    "snare_transient",
    "snare_onset",
    "snare_recovery",
)


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    ranges: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not any(needle in line for needle in NEEDLES):
            continue
        start = max(0, index - 30)
        end = min(len(lines), index + 28)
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
