#!/usr/bin/env python3
"""Print the initial hi-hat event and activation logic."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"
START = 31380
END = 31613


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for number in range(START - 1, END):
        print(f"{number + 1}: {lines[number]}")


if __name__ == "__main__":
    main()
