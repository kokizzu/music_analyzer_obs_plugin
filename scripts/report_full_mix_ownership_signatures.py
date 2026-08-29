#!/usr/bin/env python3
"""List ownership-related analyzer declarations for focused source inspection."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "tests" / "analyzer_real_note_samples.cpp"
    lines = source.read_text().splitlines()
    start = next(index for index, line in enumerate(lines) if "void print_attribute_header(" in line)
    end = min(len(lines), start + 260)
    print(f"--- {source}:{start + 1}-{end} ---")
    for index in range(start, end):
        print(f"{index + 1:6d}  {lines[index]}")


if __name__ == "__main__":
    main()
