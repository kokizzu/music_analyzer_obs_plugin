#!/usr/bin/env python3
"""Print the complete shared full-mix display mirror gate."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "analyzer.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for signature in (
        "void add_full_mix_display_mirror(",
        "bool full_mix_display_mirror_supported(",
    ):
        start = next(index for index, line in enumerate(lines) if line.startswith(signature))
        print(f"## {signature}")
        for index in range(start, min(start + 110, len(lines))):
            print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
