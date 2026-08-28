#!/usr/bin/env python3
"""Print the chord-result comparator used by mixed display arbitration."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("ChordResult stronger_chord") and index > 20000)
    depth = 0
    entered = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        entered = entered or "{" in line
        print(f"{index + 1:5}: {line}")
        if entered and depth == 0:
            return


if __name__ == "__main__":
    main()
