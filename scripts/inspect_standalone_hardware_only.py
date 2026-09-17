#!/usr/bin/env python3
"""Print the standalone hardware-only option and execution path."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "standalone.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    needles = ("hardware_only", "hardware_test_root", "hardware.start", "hardware.update")
    indexes = [index for index, line in enumerate(lines) if any(needle in line for needle in needles)]
    printed: set[int] = set()
    for index in indexes:
        start = max(0, index - 8)
        end = min(len(lines), index + 12)
        for line_index in range(start, end):
            if line_index in printed:
                continue
            printed.add(line_index)
            print(f"{line_index + 1}: {lines[line_index]}")
        print("...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
