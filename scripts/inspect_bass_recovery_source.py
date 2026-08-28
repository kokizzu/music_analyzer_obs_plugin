#!/usr/bin/env python3
"""Print the focused analyzer regions which route upper-register bass notes."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"
TERMS = ("upper bass", "upper_bass", "bass recovery", "bass_recovery")


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines) if any(term in line.lower() for term in TERMS)]
    if not hits:
        raise SystemExit("no upper-bass recovery markers found")
    for index in hits:
        first = max(0, index - 12)
        last = min(len(lines), index + 24)
        print(f"[{first + 1}-{last}]")
        for line_number in range(first, last):
            print(f"{line_number + 1}: {lines[line_number]}")


if __name__ == "__main__":
    main()
