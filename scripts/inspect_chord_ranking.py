#!/usr/bin/env python3
"""Print the chord candidate scoring and label ordering implementation."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "src/analyzer.cpp"


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("ChordResult detect_chord("))
    depth = 0
    opened = False
    end = start
    for index in range(start, len(lines)):
        depth += lines[index].count("{")
        opened = opened or "{" in lines[index]
        depth -= lines[index].count("}")
        if opened and depth == 0:
            end = index + 1
            break
    for index in range(start, end):
        print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
