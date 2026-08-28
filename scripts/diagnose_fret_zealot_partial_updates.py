#!/usr/bin/env python3
"""Print the Fret Zealot LED write and auto-root update paths for diagnosis."""

from pathlib import Path


SOURCE = Path("android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java")
RANGES = ((125, 337),)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for start_line, end_line in RANGES:
        start = max(0, start_line - 1)
        end = min(len(lines), end_line)
        print(f"\n{SOURCE}:{start_line}-{end}")
        for number in range(start, end):
            print(f"{number + 1:5}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
