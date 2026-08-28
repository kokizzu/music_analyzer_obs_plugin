#!/usr/bin/env python3
"""Print the Basic Pitch vocal-fusion API and call sites."""

from __future__ import annotations

import pathlib


FILES = (pathlib.Path("src/basic_pitch_vocal_fusion.hpp"), pathlib.Path("src/analyzer.cpp"))
TERMS = ("BasicPitch", "vocal_fusion", "vocal")


def main() -> int:
    for path in FILES:
        print(f"\n== {path} ==")
        lines = path.read_text(encoding="utf-8").splitlines()
        matches = [index for index, line in enumerate(lines) if any(term.lower() in line.lower() for term in TERMS)]
        for index in matches[:18]:
            for number in range(max(0, index - 3), min(len(lines), index + 12)):
                print(f"{number + 1}: {lines[number]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
