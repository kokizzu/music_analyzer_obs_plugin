#!/usr/bin/env python3
"""Print global chroma write sites used by full-mix chord detection."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for index in range(10620, min(len(lines), 10810)):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
