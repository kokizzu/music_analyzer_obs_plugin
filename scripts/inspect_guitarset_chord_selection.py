#!/usr/bin/env python3
"""Locate chord template scoring and extra-tone rejection in the analyzer."""

from pathlib import Path


lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
for start, end in ((16620, 16770), (17080, 17275)):
    print(f"--- {start}-{end} ---")
    for number in range(start, min(len(lines), end) + 1):
        print(f"{number}: {lines[number - 1]}")
