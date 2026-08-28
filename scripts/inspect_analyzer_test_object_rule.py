#!/usr/bin/env python3
"""Print Makefile rules that build or consume analyzer_test.o."""

from pathlib import Path


def main() -> None:
    path = Path("Makefile")
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines) if "analyzer_test.o" in line]
    if not hits:
        raise SystemExit("No analyzer_test.o Makefile rule found.")
    seen: set[int] = set()
    for index in hits:
        seen.update(range(max(0, index - 3), min(len(lines), index + 5)))
    for index in sorted(seen):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
