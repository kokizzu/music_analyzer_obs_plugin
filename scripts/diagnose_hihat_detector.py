#!/usr/bin/env python3
"""Print the hi-hat classifier gates used for regression investigation."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def print_range(lines: list[str], heading: str, start: int, end: int) -> None:
    print(f"== {heading} ==")
    for index in range(start - 1, min(end, len(lines))):
        print(f"{index + 1:5}: {lines[index]}")
    print()


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print_range(lines, "drum detection gate", 31279, 31325)
    print_range(lines, "early hi-hat recovery", 32089, 32108)
    print_range(lines, "hi-hat trigger path", 31404, 31418)
    print_range(lines, "final real-mix hi-hat recovery", 35288, 35395)
    print("== hi-hat post-processing calls ==")
    for index, line in enumerate(lines):
        if "drum_level(HiHat" not in line:
            continue
        for current in range(max(0, index - 2), min(len(lines), index + 2)):
            print(f"{current + 1:5}: {lines[current]}")
        print()


if __name__ == "__main__":
    main()
