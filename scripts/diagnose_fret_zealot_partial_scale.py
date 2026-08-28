#!/usr/bin/env python3
"""Print the Fret Zealot root-change and LED reconciliation paths."""

from pathlib import Path


def main() -> int:
    excerpts = {
        Path("tests/check_android_project.py"): ((330, 450),),
    }
    for source, ranges in excerpts.items():
        lines = source.read_text(encoding="utf-8").splitlines()
        for start, end in ranges:
            for line_index in range(start - 1, min(end, len(lines))):
                print(f"{source}:{line_index + 1}: {lines[line_index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
