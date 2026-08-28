#!/usr/bin/env python3
"""Print where full-mix ownership scores become display-row state."""

from __future__ import annotations

import pathlib


SOURCE = pathlib.Path("src/analyzer.cpp")
TERMS = ("best_same_midi_vocal_shadow_debug", "vocal_shadow", "full_mix_display_mirror_supported")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for term in TERMS:
        print(f"\n== {term} ==")
        matches = [index for index, line in enumerate(lines) if term in line]
        for index in matches[-5:]:
            for number in range(index, min(len(lines), index + 28)):
                print(f"{number + 1}: {lines[number]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
