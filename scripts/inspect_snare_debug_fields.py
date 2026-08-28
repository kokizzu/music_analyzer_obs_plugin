#!/usr/bin/env python3
"""List snare diagnostics published by the analyzer snapshot."""

from pathlib import Path


def main() -> None:
    for path in (Path("src/analyzer.hpp"), Path("src/analyzer.cpp")):
        print(f"## {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "drum_debug_snare" in line:
                print(f"{line_number}: {line}")


if __name__ == "__main__":
    main()
