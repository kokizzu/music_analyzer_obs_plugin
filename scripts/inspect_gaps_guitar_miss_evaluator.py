#!/usr/bin/env python3
"""Show the current GAPS guitar-miss measurement contract and output fields."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/evaluate_gaps_guitar_misses.py"


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    print(f"## {PATH.relative_to(ROOT)} lines={len(lines)}")
    for index, line in enumerate(lines, start=1):
        print(f"{index:6d}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
