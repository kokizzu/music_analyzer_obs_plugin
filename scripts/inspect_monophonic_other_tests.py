#!/usr/bin/env python3
"""Locate deterministic monophonic-other coverage in analyzer tests."""

from pathlib import Path


SOURCES = (Path("tests/analyzer_cases.cpp"), Path("tests/analyzer_internal.cpp"))
NEEDLES = ("monophonic", "quiet_named", "IsolatedOther", "string track", "brass track")
CONTEXT = 12


def main() -> None:
    for source in SOURCES:
        lines = source.read_text(encoding="utf-8").splitlines()
        emitted: set[int] = set()
        for index, line in enumerate(lines):
            if not any(needle in line for needle in NEEDLES):
                continue
            start = max(0, index - CONTEXT)
            end = min(len(lines), index + CONTEXT + 1)
            if any(position in emitted for position in range(start, end)):
                continue
            emitted.update(range(start, end))
            print(f"--- {source}:{index + 1} ---")
            for position in range(start, end):
                print(f"{position + 1:5}: {lines[position]}")


if __name__ == "__main__":
    main()
