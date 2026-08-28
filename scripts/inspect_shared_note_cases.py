#!/usr/bin/env python3
"""Print synthetic regression coverage for same-pitch full-mix ownership."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tests" / "analyzer_cases.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for name in ("check_same_note_timbre_split", "check_ambiguous_same_note_full_mix_chord_ownership"):
        start = next(index for index, line in enumerate(lines) if line.startswith(f"void {name}("))
        print(f"## {name}")
        for index in range(start, min(start + 160, len(lines))):
            print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
