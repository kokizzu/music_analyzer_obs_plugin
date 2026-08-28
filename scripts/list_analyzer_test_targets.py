#!/usr/bin/env python3
"""List analyzer-related Makefile test targets for focused verification."""

from pathlib import Path
import re


TARGET = re.compile(r"^([A-Za-z0-9_.-]+):")


def main() -> None:
    targets = []
    for line in Path("Makefile").read_text(encoding="utf-8").splitlines():
        match = TARGET.match(line)
        if not match:
            continue
        target = match.group(1)
        lowered = target.lower()
        if "test" in lowered and ("analyzer" in lowered or "chord" in lowered or "note" in lowered):
            targets.append(target)
    for target in sorted(set(targets)):
        print(target)


if __name__ == "__main__":
    main()
