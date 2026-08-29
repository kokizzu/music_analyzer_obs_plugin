#!/usr/bin/env python3
"""Print chord-template and ranking code relevant to diminished/suspended labels."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "src" / "analyzer.cpp"
RANGES = ((11165, 11355), (14645, 14730), (26145, 26270))


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    selected: set[int] = set()
    for start, end in RANGES:
        selected.update(range(start - 1, min(len(lines), end)))
    for index in sorted(selected):
        print(f"{index + 1:6d}  {lines[index]}")


if __name__ == "__main__":
    main()
