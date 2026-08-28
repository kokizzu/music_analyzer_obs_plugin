#!/usr/bin/env python3
"""Locate chord alias aggregation and visible-label ordering paths."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "src/analyzer.cpp"
PATTERN = re.compile(r"(alias|merge|append|stronger).*(chord|label)|(chord|label).*(alias|merge|append|stronger)", re.I)


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines) if PATTERN.search(line)]
    shown: set[int] = set()
    for hit in hits:
        start = max(0, hit - 7)
        end = min(len(lines), hit + 15)
        print(f"\n## line {hit + 1}")
        for index in range(start, end):
            if index in shown:
                continue
            shown.add(index)
            print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
