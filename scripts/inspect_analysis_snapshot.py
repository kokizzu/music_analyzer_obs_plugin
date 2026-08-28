#!/usr/bin/env python3
"""Print the public snapshot structures used by focused analyzer diagnostics."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.hpp").read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if "struct NoteCell" in line)
    for index in range(start, min(len(lines), start + 150)):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
