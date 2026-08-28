#!/usr/bin/env python3
"""Print diminished-alias construction and its analyzer call sites."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
MARKER = "append_strict_symmetric_dim7_aliases"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if MARKER in line and line.lstrip().startswith("void "):
            print("== definition ==")
            for number in range(index, min(len(lines), index + 160)):
                print(f"{number + 1}: {lines[number]}")
            break
    print("== call sites ==")
    for index, line in enumerate(lines):
        if MARKER in line and not line.lstrip().startswith("void "):
            print(f"{index + 1}: {line}")


if __name__ == "__main__":
    main()
