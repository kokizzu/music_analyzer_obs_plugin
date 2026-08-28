#!/usr/bin/env python3
"""Print the primary-drum arbitration helper used by real-sample tests."""

from pathlib import Path


def main() -> None:
    lines = Path("tests/analyzer_drum_samples.cpp").read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if "primary_drum_index" in line and "(" in line)
    depth = 0
    entered_body = False
    for current in range(start, len(lines)):
        line = lines[current]
        depth += line.count("{") - line.count("}")
        entered_body = entered_body or "{" in line
        print(f"{current + 1:5}: {line}")
        if entered_body and depth == 0:
            return


if __name__ == "__main__":
    main()
