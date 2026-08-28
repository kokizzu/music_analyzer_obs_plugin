#!/usr/bin/env python3
"""Print the Android project assertions relevant to Fret Zealot output."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "tests/check_android_project.py"


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    for index in range(330, min(len(lines), 450)):
        print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
