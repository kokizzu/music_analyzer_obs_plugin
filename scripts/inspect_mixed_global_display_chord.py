#!/usr/bin/env python3
"""Print mixed global display-chord arbitration helpers."""

from pathlib import Path


NAMES = ("detect_mixed_display_global_chord", "prefer_mixed_display_global_chord")


def print_function(lines: list[str], start: int) -> None:
    depth = 0
    entered = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        entered = entered or "{" in line
        print(f"{index + 1:5}: {line}")
        if entered and depth == 0:
            print()
            return


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for name in NAMES:
        start = next(index for index, line in enumerate(lines) if line.startswith("ChordResult " + name))
        print_function(lines, start)


if __name__ == "__main__":
    main()
