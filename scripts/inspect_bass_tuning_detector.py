#!/usr/bin/env python3
"""Print chromatic tuning implementation and bass-specific call sites."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src/analyzer.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines)
               if "chromatic_tuning_probe(" in line]
    emitted: set[int] = set()
    for index in matches:
        print(f"### {index + 1}")
        for number in range(max(0, index - 12), min(len(lines), index + 130)):
            if number in emitted:
                continue
            emitted.add(number)
            print(f"{number + 1:6}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
