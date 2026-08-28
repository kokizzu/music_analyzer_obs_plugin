#!/usr/bin/env python3
"""Show shared full-mix ownership definitions and their final display call sites."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
NEEDLES = (
    "InstrumentKind classify",
    "classify_full_mix",
    "full_mix_display_candidates(",
    "build_full_mix_ownership(",
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    shown: set[int] = set()
    for index, line in enumerate(lines):
        if not any(needle in line for needle in NEEDLES):
            continue
        start = max(0, index - 4)
        if start in shown:
            continue
        shown.add(start)
        end = min(len(lines), index + 28)
        print(f"\n{SOURCE}:{index + 1}")
        for number in range(start, end):
            print(f"{number + 1:5}: {lines[number]}")


if __name__ == "__main__":
    main()
