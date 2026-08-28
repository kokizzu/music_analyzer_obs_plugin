#!/usr/bin/env python3
"""Locate full-mix debug output controls in the real-note fixture test."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "tests/analyzer_real_note_samples.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines)
            if "debug_candidate" in line or "FULL_MIX" in line or "VERBOSE" in line]
    printed: set[int] = set()
    for hit in hits:
        for index in range(max(0, hit - 4), min(len(lines), hit + 8)):
            if index not in printed:
                print(f"{index + 1}: {lines[index]}")
                printed.add(index)


if __name__ == "__main__":
    main()
