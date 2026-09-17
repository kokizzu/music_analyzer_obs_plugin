#!/usr/bin/env python3
"""Print the standalone live-source selection region for review."""

from pathlib import Path


path = Path(__file__).resolve().parents[1] / "src" / "standalone.cpp"
lines = path.read_text(encoding="utf-8").splitlines()
for number, line in enumerate(lines[590:660], start=591):
    print(f"{number}: {line}")
