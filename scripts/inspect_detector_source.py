#!/usr/bin/env python3
"""Print focused analyzer source contexts for a detector term."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("term")
    parser.add_argument("--context", type=int, default=3)
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"
    lines = source.read_text(encoding="utf-8").splitlines()
    term = args.term.lower()
    emitted: set[int] = set()
    for index, line in enumerate(lines):
        if term not in line.lower():
            continue
        start = max(0, index - args.context)
        end = min(len(lines), index + args.context + 1)
        if any(number in emitted for number in range(start, end)):
            continue
        print(f"--- analyzer.cpp:{start + 1}-{end} ---")
        for number in range(start, end):
            emitted.add(number)
            print(f"{number + 1}: {lines[number]}")


if __name__ == "__main__":
    main()
