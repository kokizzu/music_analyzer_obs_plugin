#!/usr/bin/env python3
"""Print the Fret Zealot scale scheduling state machine."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java"
RANGES = ((120, 240), (880, 1010))


def main() -> int:
    if not PATH.is_file():
        return 1
    lines = PATH.read_text(encoding="utf-8").splitlines()
    for first, last in RANGES:
        print(f"### {PATH.relative_to(ROOT)}:{first}-{last}")
        for number in range(first - 1, min(last, len(lines))):
            print(f"{number + 1:4}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
