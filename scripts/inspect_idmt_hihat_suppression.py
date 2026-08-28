#!/usr/bin/env python3
"""Show final hi-hat caps and nearby one-shot arbitration in the analyzer."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
MARKERS = ("cap_drum_level(HiHat", "drum_level_[HiHat] =", "HiHat] >", "HiHat] <=")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    shown: set[int] = set()
    for number, line in enumerate(lines, start=1):
        if not any(marker in line for marker in MARKERS):
            continue
        start = max(1, number - 12)
        end = min(len(lines), number + 12)
        if any(index in shown for index in range(start, end + 1)):
            continue
        print(f"== line {number} ==")
        for index in range(start, end + 1):
            print(f"{index:5}: {lines[index - 1]}")
            shown.add(index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
