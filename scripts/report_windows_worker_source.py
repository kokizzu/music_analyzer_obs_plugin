#!/usr/bin/env python3
"""Print the Windows hardware worker section for focused review."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")
START = 680
END = 900


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print(f"=== {SOURCE}:{START}-{END} ===")
    for number in range(START - 1, min(END, len(lines))):
        print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
