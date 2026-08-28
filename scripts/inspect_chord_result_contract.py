#!/usr/bin/env python3
"""Print the chord result fields and label finalization helpers used by display rows."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
HEADER = ROOT / "src/analyzer.hpp"
SYMBOLS = (
    "struct ChordResult",
    "set_instrument_chord",
    "detect_guitar_chord",
    "analysis_simple_triad_supported",
    "restore_guitar",
    "format_chord",
    "ChordTemplate",
)


def print_matches(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    print(f"## {path.relative_to(ROOT)}")
    for symbol in SYMBOLS:
        matches = [index for index, line in enumerate(lines) if re.search(re.escape(symbol), line)]
        print(f"### {symbol} matches={len(matches)}")
        for match in matches[:3]:
            start = max(0, match - 3)
            end = min(len(lines), match + 48)
            print(f"-- lines {start + 1}-{end}")
            for index in range(start, end):
                print(f"{index + 1:6d}: {lines[index]}")


def main() -> int:
    print_matches(HEADER)
    print_matches(SOURCE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
