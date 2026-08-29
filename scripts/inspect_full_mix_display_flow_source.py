#!/usr/bin/env python3
"""Print full-mix display-mirror call sites with their local assembly flow."""

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source = root / "src" / "analyzer.cpp"
    lines = source.read_text(encoding="utf-8").splitlines()
    matches = [
        (index, "guitar shadow") for index, line in enumerate(lines)
        if "guitar_display_candidate_shadowed_by_" in line and "bool " not in line
    ]
    for index, label in matches:
        start = max(0, index - 48)
        end = min(len(lines), index + 88)
        print(f"--- {source}:{index + 1} {label} ---")
        for line_number in range(start, end):
            print(f"{line_number + 1:6}  {lines[line_number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
