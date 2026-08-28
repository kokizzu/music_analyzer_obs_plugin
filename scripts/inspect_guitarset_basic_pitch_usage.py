#!/usr/bin/env python3
"""Show Basic Pitch enablement and replay settings in the GuitarSet harness."""

from __future__ import annotations

import pathlib


FILES = (pathlib.Path("tests/analyzer_guitarset.cpp"), pathlib.Path("src/analyzer.cpp"), pathlib.Path("src/analyzer.hpp"))
TERMS = ("basic_pitch", "onnx", "model_path", "enable_basic")


def main() -> int:
    for path in FILES:
        print(f"\n== {path} ==")
        lines = path.read_text(encoding="utf-8").splitlines()
        matches = [index for index, line in enumerate(lines) if any(term in line.lower() for term in TERMS)]
        for index in matches[:20]:
            for number in range(max(0, index - 4), min(len(lines), index + 16)):
                print(f"{number + 1}: {lines[number]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
