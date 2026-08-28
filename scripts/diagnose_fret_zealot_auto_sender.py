#!/usr/bin/env python3
"""Show the Android AUTO-root path that submits Fret Zealot scale frames."""

from pathlib import Path


ROOT = Path("android/app/src/main/java")
NEEDLES = ("fretZealot.sendPacket", "lastFretZealotPacket", "AUTO", "isScaleFrameInFlight")


def main() -> int:
    for source in sorted(ROOT.rglob("*.java")):
        lines = source.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not any(needle in line for needle in NEEDLES):
                continue
            print(f"\n{source}:{index + 1}")
            for number in range(max(0, index - 12), min(len(lines), index + 20)):
                print(f"{number + 1:5}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
