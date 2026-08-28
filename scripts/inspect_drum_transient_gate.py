#!/usr/bin/env python3
"""Print the drum-transient decision feeding final real-mix drum gates."""

from pathlib import Path


def main() -> None:
    path = Path("src/analyzer.cpp")
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "const bool drum_transient" not in line:
            continue
        print(f"== {path}:{index + 1} ==")
        for current in range(max(0, index - 20), min(len(lines), index + 36)):
            print(f"{current + 1:5}: {lines[current]}")


if __name__ == "__main__":
    main()
