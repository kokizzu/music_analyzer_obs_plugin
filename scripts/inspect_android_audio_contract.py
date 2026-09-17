#!/usr/bin/env python3
"""Print audio lifecycle assertions from the Android project contract test."""

from pathlib import Path


def main() -> int:
    path = Path("tests/check_android_project.py")
    lines = path.read_text(encoding="utf-8").splitlines()
    for number in range(200, min(345, len(lines)) + 1):
        print(f"{number}: {lines[number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
