#!/usr/bin/env python3
"""Print line-numbered analyzer source context for a detector topic."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="ride_hihat")
    parser.add_argument("--context", type=int, default=12)
    parser.add_argument("--source", type=Path, default=Path("src/analyzer.cpp"))
    args = parser.parse_args()

    lines = args.source.read_text(encoding="utf-8").splitlines()
    topic = args.topic.lower()
    matches = [index for index, line in enumerate(lines) if topic in line.lower()]
    print(f"analyzer_section topic={args.topic} matches={len(matches)} source={args.source}")
    printed: set[int] = set()
    for match in matches:
        start = max(0, match - args.context)
        end = min(len(lines), match + args.context + 1)
        for index in range(start, end):
            if index in printed:
                continue
            printed.add(index)
            print(f"{index + 1}: {lines[index]}")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
