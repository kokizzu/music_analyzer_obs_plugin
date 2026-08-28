#!/usr/bin/env python3
"""Print the vocal candidate weighting used by the rendered note grid."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if "ownership_weighted_candidate" in line]
    if not matches:
        raise SystemExit("vocal display weighting function not found")
    start = max(0, matches[0] - 2)
    end = min(len(lines), matches[0] + 50)
    for index in range(start, end):
        print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
