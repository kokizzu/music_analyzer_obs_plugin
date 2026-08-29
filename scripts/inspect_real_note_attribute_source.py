#!/usr/bin/env python3
"""Print the real-note attribute export declarations used by diagnostics."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "analyzer_real_note_samples.cpp"
MARKERS = ("void print_attribute_header", "void append_attribute_row")


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for marker in MARKERS:
        for index, line in enumerate(lines):
            if marker not in line:
                continue
            print(f"--- {SOURCE}:{index + 1} {marker} ---")
            for number in range(index, min(index + 150, len(lines))):
                print(f"{number + 1:6d}  {lines[number]}")
            break


if __name__ == "__main__":
    main()
