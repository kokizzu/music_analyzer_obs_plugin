#!/usr/bin/env python3
"""Print MIR-1K Makefile target blocks with their line numbers."""

from __future__ import annotations

import pathlib
import subprocess


PATH = pathlib.Path("Makefile")


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    indexed = subprocess.run(["git", "show", ":Makefile"], check=True, text=True,
                             capture_output=True).stdout
    print("index contains immediate pre-MIR anchor: " +
          ("yes" if "status-real-note-full-mix:" in indexed else "no"))
    print("context:")
    for number in range(9200, min(len(lines), 9320) + 1):
        print(f"{number}: {lines[number - 1]}")
    print("\nMIR-1K target blocks:")
    for index, line in enumerate(lines):
        if "mir1k" not in line.lower():
            continue
        if line.startswith(".PHONY:") or (line and not line.startswith(("\t", " ")) and line.endswith(":")):
            print(f"{index + 1}: {line}")
            cursor = index + 1
            while cursor < len(lines) and (not lines[cursor] or lines[cursor].startswith(("\t", " "))):
                print(f"{cursor + 1}: {lines[cursor]}")
                cursor += 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
