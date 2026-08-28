#!/usr/bin/env python3
"""List declared Makefile targets containing an optional case-insensitive term."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TARGET = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.%/-]*):(?:\s|$)")


def main() -> int:
    term = sys.argv[1].lower() if len(sys.argv) > 1 else "gaps"
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        match = TARGET.match(line)
        if match is None:
            continue
        name = match.group(1)
        if not term or term in name.lower():
            print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
