#!/usr/bin/env python3
"""Print the existing full-mix candidate diagnostic implementation."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if "void append_full_mix_debug_candidate" in line)
    for index in range(start, min(len(lines), start + 110)):
        print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
