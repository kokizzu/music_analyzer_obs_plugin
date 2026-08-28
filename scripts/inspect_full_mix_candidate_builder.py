#!/usr/bin/env python3
"""Print the native full-mix candidate construction and per-row selection paths."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
SYMBOLS = (
    "build_full_mix_ownership",
    "full_mix_display_candidates",
    "add_full_mix_display_mirror",
    "prune_shadowed_full_mix_guitar_display_candidates",
    "set_instrument_note_set_from_candidates",
)
CONTEXT = 70


def find_definitions(lines: list[str], symbol: str) -> list[int]:
    pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")
    return [index for index, line in enumerate(lines) if pattern.search(line)]


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for symbol in SYMBOLS:
        matches = find_definitions(lines, symbol)
        print(f"## {symbol} matches={len(matches)}")
        for match in matches[:4]:
            start = max(0, match - 4)
            end = min(len(lines), match + CONTEXT)
            print(f"-- lines {start + 1}-{end}")
            for index in range(start, end):
                print(f"{index + 1:6d}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
