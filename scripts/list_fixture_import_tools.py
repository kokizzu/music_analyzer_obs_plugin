#!/usr/bin/env python3
"""List repository fixture scripts relevant to real-audio imports."""

from pathlib import Path


terms = ("sample", "fixture", "urmp", "guitar", "drum", "maestro", "dataset", "real_note")
for path in sorted(Path("scripts").glob("*")):
    if not path.is_file():
        continue
    name = path.name.lower()
    if any(term in name for term in terms):
        print(path)

targets = (
    "inspect-full-mix-ownership-classifier:",
    "list-fixture-import-tools:",
    "report-guitarset-miss-process:",
    "inspect-guitarset-chord-selection:",
    "report-piano-guitar-owner-aliases:",
    "report-same-pitch-guitar-owner-separation:",
)
makefile = Path("Makefile").read_text(encoding="utf-8").splitlines()
for number, line in enumerate(makefile, start=1):
    if line in targets:
        print(f"MAKE {number}: {line}")
