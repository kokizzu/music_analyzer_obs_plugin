#!/usr/bin/env python3
"""Print the tom/snare primary-analysis script and matching analyzer arbitration code."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/analyze_tom_snare_primary.py"
SOURCE = ROOT / "src/analyzer.cpp"
TERMS = ("tom_snare_level", "tom_snare_band", "tom_snare_trigger", "tom_snare_shape", "tom_snare_body")


def print_script() -> None:
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    print(f"## {SCRIPT.relative_to(ROOT)}")
    for index, line in enumerate(lines, start=1):
        print(f"{index:6d}: {line}")


def print_source() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if any(term in line for term in TERMS)]
    print(f"## {SOURCE.relative_to(ROOT)} matches={len(matches)}")
    emitted: set[int] = set()
    for match in matches:
        start = max(0, match - 18)
        end = min(len(lines), match + 30)
        visible = [index for index in range(start, end) if index not in emitted]
        if not visible:
            continue
        print(f"-- lines {visible[0] + 1}-{visible[-1] + 1}")
        for index in visible:
            print(f"{index + 1:6d}: {lines[index]}")
            emitted.add(index)


def main() -> int:
    print_script()
    print_source()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
