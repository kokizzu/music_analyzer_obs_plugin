#!/usr/bin/env python3
"""Print the real-note fixture manifest and loader contract for fixture tooling."""

from __future__ import annotations

import pathlib


SOURCE = pathlib.Path("tests/analyzer_real_note_samples.cpp")
TERMS = (
    "manifest.tsv",
    "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT",
    "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV",
    "struct RealNote",
    "expected_index",
    "full_mix",
    "row.family ==",
    "read_manifest",
    "buffers",
    "analyze_buffer",
)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print(f"source: {SOURCE}")
    for term in TERMS:
        print(f"\n[{term}]")
        matches = [index for index, line in enumerate(lines) if term in line]
        for index in matches[:4]:
            start = max(0, index - 4)
            end = min(len(lines), index + 30)
            for number in range(start, end):
                print(f"{number + 1}: {lines[number]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
