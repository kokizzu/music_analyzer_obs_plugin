#!/usr/bin/env python3
"""List analyzer EGMD test environment controls and their source locations."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path("tests/analyzer_egmd.cpp")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "MUSIC_ANALYZER" in line or "getenv" in line:
            print(f"{index + 1}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
