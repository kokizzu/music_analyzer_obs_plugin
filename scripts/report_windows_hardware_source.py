#!/usr/bin/env python3
"""Print the Windows hardware paths that require runtime review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RANGES = {
    "src/windows_hardware_control.cpp": ((1, 160), (160, 420), (418, 620), (600, 715)),
    "src/windows_hardware_control.hpp": ((1, 180),),
    "src/fret_control.cpp": ((260, 560),),
}


def main() -> int:
    for relative_path, ranges in RANGES.items():
        lines = (ROOT / relative_path).read_text(encoding="utf-8").splitlines()
        print(f"=== {relative_path} ===")
        for start, end in ranges:
            print(f"--- lines {start}-{end} ---")
            for number in range(start, min(end, len(lines)) + 1):
                print(f"{number}: {lines[number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
