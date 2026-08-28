#!/usr/bin/env python3
"""Print the synthetic complex-timbre regression and its local helpers."""

from pathlib import Path


NEEDLES = ("check_complex_real_timbres_survive_tuning_wobble", "make_complex")


def print_function(lines: list[str], start: int) -> None:
    depth = 0
    entered = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        entered = entered or "{" in line
        print(f"{index + 1:5}: {line}")
        if entered and depth == 0:
            print()
            return


def main() -> None:
    lines = Path("tests/analyzer_cases.cpp").read_text(encoding="utf-8").splitlines()
    printed = set()
    for needle in NEEDLES:
        for index, line in enumerate(lines):
            if needle not in line or index in printed:
                continue
            printed.add(index)
            print_function(lines, index)


if __name__ == "__main__":
    main()
