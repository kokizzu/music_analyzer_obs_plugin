#!/usr/bin/env python3
"""Print the deterministic CAGED root-independence regression."""

from pathlib import Path


def main() -> None:
    lines = Path("tests/analyzer_cases.cpp").read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if "check_guitar_caged_mix_root_independence" in line)
    depth = 0
    entered = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        entered = entered or "{" in line
        print(f"{index + 1:5}: {line}")
        if entered and depth == 0:
            return


if __name__ == "__main__":
    main()
