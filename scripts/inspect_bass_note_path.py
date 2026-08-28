#!/usr/bin/env python3
"""Print source contexts that build and publish isolated-bass note candidates."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src/analyzer.cpp"
TERMS = ("bass_debug_displayed", "bass_note_tracking_", "IsolatedBass")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if any(term in line for term in TERMS)]
    emitted: set[int] = set()
    for index in matches[:32]:
        print(f"### {index + 1}")
        for number in range(max(0, index - 10), min(len(lines), index + 22)):
            if number in emitted:
                continue
            emitted.add(number)
            print(f"{number + 1:6}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
