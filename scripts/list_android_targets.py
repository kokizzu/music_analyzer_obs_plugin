#!/usr/bin/env python3
"""List Makefile targets that build or test the Android application."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
TARGET = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*):")


def main() -> int:
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        match = TARGET.match(line)
        if match and "android" in match.group(1).lower():
            print(match.group(1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
