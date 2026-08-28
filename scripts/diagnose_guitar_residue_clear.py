#!/usr/bin/env python3
"""Print the final guitar chord cleanup block and its supporting predicates."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
RANGES = ((37525, 37620),)
NEEDLES = (
    "clear_guitar_residue",
    "chord_label_has_guitar_extension_or_alteration",
    "primary_guitar_chord_has_playable_voicing",
)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for start_line, end_line in RANGES:
        print(f"\n{SOURCE}:{start_line}-{end_line}")
        for index in range(start_line - 1, min(end_line, len(lines))):
            print(f"{index + 1:5}: {lines[index]}")
    for index, line in enumerate(lines):
        if not any(needle in line for needle in NEEDLES):
            continue
        print(f"\n{SOURCE}:{index + 1}")
        for number in range(max(0, index - 6), min(len(lines), index + 18)):
            print(f"{number + 1:5}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
