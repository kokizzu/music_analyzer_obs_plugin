#!/usr/bin/env python3
"""Print the full-mix ownership scoring and classifier paths for inspection."""

from pathlib import Path


source = Path("src/analyzer.cpp")
lines = source.read_text(encoding="utf-8").splitlines()
needles = (
    "ownership_scores.fill",
    "ownership_scores[",
    "evidence.owner =",
    "owner = InstrumentKind",
    "max_element(evidence.ownership_scores",
)
for start, end in ((10320, 10530),):
    print(f"--- {start}-{end} ---")
    for number in range(start, min(len(lines), end) + 1):
        print(f"{number}: {lines[number - 1]}")
