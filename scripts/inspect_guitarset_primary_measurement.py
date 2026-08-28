#!/usr/bin/env python3
"""Locate GuitarSet primary-chord measurement and diagnostic hooks."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "tests/analyzer_guitarset.cpp"
PATTERN = re.compile(r"primary chord|primary_chord|chord hits|guitar_chord", re.IGNORECASE)


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines) if PATTERN.search(line)]
    print(f"## {PATH.relative_to(ROOT)}")
    shown: set[int] = set()
    for hit in hits:
        for index in range(max(0, hit - 18), min(len(lines), hit + 35)):
            if index in shown:
                continue
            shown.add(index)
            print(f"{index + 1}: {lines[index]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
