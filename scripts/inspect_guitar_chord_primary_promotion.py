#!/usr/bin/env python3
"""Print analyzer paths that choose or promote guitar chord display candidates."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
MARKERS = (
    "same_root_extension",
    "primary_chord",
    "promote_chord",
    "guitar_chord",
)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    shown: set[int] = set()
    for number, line in enumerate(lines, start=1):
        if not any(marker in line for marker in MARKERS):
            continue
        start = max(1, number - 10)
        end = min(len(lines), number + 14)
        if any(index in shown for index in range(start, end + 1)):
            continue
        print(f"== line {number} ==")
        for index in range(start, end + 1):
            print(f"{index:5}: {lines[index - 1]}")
            shown.add(index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
