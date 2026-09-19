#!/usr/bin/env python3
"""Print Android Fret Zealot SDK call sites that establish packet field order."""

from pathlib import Path


ROOT = Path("android")
TOKENS = (
    ".set(",
    "set_all(",
    ".clear(",
    "set_across(",
    "set_subset(",
    "fretZealotPixelForStandardTuningString",
)
CONTEXT = 3


def main() -> int:
    for source in sorted(ROOT.rglob("*.java")):
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines):
            if not any(token in line for token in TOKENS):
                continue
            print(f"=== {source}:{index + 1} ===")
            for number in range(max(0, index - CONTEXT), min(len(lines), index + CONTEXT + 1)):
                print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
