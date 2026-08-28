#!/usr/bin/env python3
"""List explicit Android-related Makefile targets for repeatable verification."""

from __future__ import annotations

import re
from pathlib import Path


TARGET = re.compile(r"^([A-Za-z0-9_.-]+):")


def main() -> int:
    targets: list[str] = []
    for line in Path("Makefile").read_text(encoding="utf-8").splitlines():
        match = TARGET.match(line)
        if match and "android" in match.group(1):
            targets.append(match.group(1))
    print("android_make_targets=" + ",".join(targets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
