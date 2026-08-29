#!/usr/bin/env python3
"""Print only the mixed Other display candidate construction in analyzer.cpp."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "mixed_other_display" not in line:
            continue
        print(f"--- {SOURCE}:{index + 1} ---")
        for current in range(max(0, index - 12), min(len(lines), index + 16)):
            print(f"{current + 1:6d}  {lines[current]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
