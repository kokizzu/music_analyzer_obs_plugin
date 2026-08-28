#!/usr/bin/env python3
"""Print Android project assertions that cover Fret Zealot frame handling."""

from pathlib import Path


SOURCE = Path("tests/check_android_project.py")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "Fret Zealot" not in line and "LEGACY_" not in line:
            continue
        start = max(0, index - 3)
        end = min(len(lines), index + 4)
        print(f"\n{SOURCE}:{index + 1}")
        for number in range(start, end):
            print(f"{number + 1:5}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
