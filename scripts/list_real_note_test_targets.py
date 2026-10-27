#!/usr/bin/env python3
"""List existing Makefile targets for real-audio note and chord corpora."""
from makefile_source import read_makefile

from pathlib import Path


TERMS = ("musicnet", "maestro", "guitarset", "urmp", "multtipop", "real-note")


def main() -> None:
    for index, line in enumerate(read_makefile(Path("Makefile"), encoding="utf-8").splitlines(), 1):
        lowered = line.lower()
        if any(term in lowered for term in TERMS):
            print(f"{index:5}: {line}")


if __name__ == "__main__":
    main()
