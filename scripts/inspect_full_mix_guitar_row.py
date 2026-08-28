#!/usr/bin/env python3
"""Print the full-mix guitar display gate and all of its named mirror clauses."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    starts = []
    for index, line in enumerate(lines):
        if "case FullMixDisplayRow::Guitar" in line:
            starts.append(index)
    for start in starts:
        end = min(len(lines), start + 180)
        for number in range(start, end):
            print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
