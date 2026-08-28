#!/usr/bin/env python3
"""Locate full-mix note ownership and row-projection code for review."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "analyzer.cpp"
FUNCTION = "bool shared_guitar_pitch_display_supported"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        if number <= 3200 or FUNCTION not in line:
            continue
        for context_number in range(number, min(number + 180, len(lines)) + 1):
            print(f"{context_number}: {lines[context_number - 1]}")
        return 0
    print(f"missing function: {FUNCTION}", file=sys.stderr)
    return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
