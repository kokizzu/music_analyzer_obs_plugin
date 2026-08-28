#!/usr/bin/env python3
"""Print the quiet monophonic visual-floor regression function."""

from pathlib import Path


SOURCE = Path("tests/analyzer_internal.cpp")
MARKER = "void check_quiet_monophonic_other_visual_floor"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if MARKER in line)
    depth = 0
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        print(f"{index + 1:5}: {line}")
        if index > start and depth == 0:
            return


if __name__ == "__main__":
    main()
