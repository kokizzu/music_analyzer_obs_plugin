#!/usr/bin/env python3
"""List chord-label parsing and template helpers in the analyzer source."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    for number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        lowered = line.lower()
        if "chord" in lowered and ("parse" in lowered or "template" in lowered):
            print(f"{number}: {line}")


if __name__ == "__main__":
    main()
