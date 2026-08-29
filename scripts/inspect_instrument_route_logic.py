#!/usr/bin/env python3
"""Print the current mixed-source primary-owner classifier."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "analyzer.cpp"
FUNCTION = "InstrumentKind choose_full_mix_owner("


def function_region(lines: list[str]) -> tuple[int, int]:
    start = next((index for index, line in enumerate(lines) if FUNCTION in line), -1)
    if start < 0:
        raise RuntimeError(f"function not found: {FUNCTION}")

    depth = 0
    opened = False
    for index in range(start, len(lines)):
        depth += lines[index].count("{")
        depth -= lines[index].count("}")
        opened = opened or "{" in lines[index]
        if opened and depth == 0:
            return start, index
    raise RuntimeError(f"function is not closed: {FUNCTION}")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start, end = function_region(lines)
    print(f"function={FUNCTION.rstrip('(')} region={start + 1}-{end + 1}")
    for index in range(start, end + 1):
        print(f"{SOURCE.relative_to(ROOT)}:{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
