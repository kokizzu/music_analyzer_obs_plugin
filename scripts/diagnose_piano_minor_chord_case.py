#!/usr/bin/env python3
"""Print the MulTTiPop minor-chord fixture and relevant chord-resolution call sites."""

from pathlib import Path


TESTS = Path("tests/analyzer_cases.cpp")
ANALYZER = Path("src/analyzer.cpp")


def main() -> int:
    test_lines = TESTS.read_text(encoding="utf-8").splitlines()
    print(f"{TESTS}:6990-7140")
    for index in range(6989, 7140):
        print(f"{index + 1:5}: {test_lines[index]}")
    lines = ANALYZER.read_text(encoding="utf-8").splitlines()
    print("\n" + f"{ANALYZER}:35935-35966")
    for index in range(35934, 35966):
        print(f"{index + 1:5}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
