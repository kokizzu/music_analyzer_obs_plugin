#!/usr/bin/env python3
"""Print hi-hat suppression branches from the analyzer for focused diagnosis."""

from pathlib import Path


def main() -> int:
    lines = Path("src/analyzer.cpp").read_text().splitlines()
    for index, line in enumerate(lines):
        lower = line.lower()
        if "hihat" not in lower or "suppress" not in lower:
            continue
        print(f"# analyzer.cpp:{index + 1}")
        for number in range(max(0, index - 8), min(len(lines), index + 22)):
            print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
