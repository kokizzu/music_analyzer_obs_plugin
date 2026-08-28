#!/usr/bin/env python3
"""Print the isolated-guitar chord finalization block after candidate selection."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
START = 36280
END = 36520


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print(f"## {SOURCE.relative_to(ROOT)} lines {START}-{END}")
    for index in range(START - 1, min(END, len(lines))):
        print(f"{index + 1:6d}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
