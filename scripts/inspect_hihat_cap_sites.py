#!/usr/bin/env python3
"""Show compact context for final hi-hat level caps in the analyzer."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "analyzer.cpp"
HEADER = ROOT / "src" / "analyzer.hpp"
CONTEXT = 9


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [
        index for index, line in enumerate(lines)
        if "cap_drum_level(HiHat" in line
    ]
    print(f"hihat_cap_sites={len(matches)}")
    for site, index in enumerate(matches, start=1):
        print(f"\n== cap {site} at analyzer.cpp:{index + 1} ==")
        for number in range(max(0, index - CONTEXT), min(len(lines), index + CONTEXT + 1)):
            print(f"{number + 1:5}: {lines[number]}")
    print("\n== analyzer.hpp drum debug flags ==")
    for number, line in enumerate(HEADER.read_text(encoding="utf-8").splitlines(), start=1):
        if "DrumDebug" in line:
            print(f"{number:5}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
