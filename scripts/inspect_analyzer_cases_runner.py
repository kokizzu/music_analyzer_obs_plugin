#!/usr/bin/env python3
"""Print the analyzer-case runner entry point before adding a selective mode."""

from pathlib import Path


def main() -> None:
    lines = Path("tests/analyzer_cases.cpp").read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("int main("):
            start = max(0, index - 12)
            end = min(len(lines), index + 180)
            print(f"## {start + 1}-{end}")
            for position in range(start, end):
                print(f"{position + 1}: {lines[position]}")
            return
    raise SystemExit("analyzer_cases main function not found")


if __name__ == "__main__":
    main()
