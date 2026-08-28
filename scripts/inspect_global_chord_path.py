#!/usr/bin/env python3
"""Print global-chord detector call sites and nearby root-selection code."""

from pathlib import Path


def main() -> None:
    lines = Path("src/analyzer.cpp").read_text(encoding="utf-8").splitlines()
    for index in range(35845, min(len(lines), 36110)):
        print(f"{index + 1:5}: {lines[index]}")


if __name__ == "__main__":
    main()
