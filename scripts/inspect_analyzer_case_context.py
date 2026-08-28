#!/usr/bin/env python3
"""Print focused source context for named analyzer-case assertions."""

from pathlib import Path
import sys


SOURCE = Path("tests/analyzer_cases.cpp")
CONTEXT = 55


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: inspect_analyzer_case_context.py TEXT")
    needle = sys.argv[1]
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    found = False
    for index, line in enumerate(lines):
        if needle not in line:
            continue
        found = True
        print(f"== line {index + 1} ==")
        for number in range(max(0, index - CONTEXT), min(len(lines), index + CONTEXT + 1)):
            print(f"{number + 1}: {lines[number]}")
    if not found:
        raise SystemExit(f"not found: {needle}")


if __name__ == "__main__":
    main()
