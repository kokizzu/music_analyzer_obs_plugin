#!/usr/bin/env python3
"""Print real-note manifest/runtime configuration and fixture-prep sources."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = (Path("tests/analyzer_real_note_samples.cpp"), Path("Makefile"))
NEEDLES = ("REAL_NOTE", "manifest", "MUSIC_ANALYZER", "sample_root")


def main() -> int:
    found = False
    for relative in PATHS:
        path = ROOT / relative
        if not path.is_file():
            continue
        found = True
        lines = path.read_text(encoding="utf-8").splitlines()
        matched = [index for index, line in enumerate(lines) if any(needle in line for needle in NEEDLES)]
        if not matched:
            continue
        print(f"### {relative}")
        emitted: set[int] = set()
        for index in matched:
            for number in range(max(0, index - 3), min(len(lines), index + 4)):
                if number in emitted:
                    continue
                emitted.add(number)
                print(f"{number + 1:4}: {lines[number]}")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
