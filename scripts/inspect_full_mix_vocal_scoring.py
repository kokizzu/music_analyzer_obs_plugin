#!/usr/bin/env python3
"""Print the vocal-score branch of the full-mix ownership classifier."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if "scores[2]" in line]
    if not matches:
        raise SystemExit("no vocal score branch found")
    start = max(0, matches[0] - 24)
    end = min(len(lines), matches[-1] + 25)
    for index in range(start, end):
        print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
