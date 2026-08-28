#!/usr/bin/env python3
"""Print final analyzer assignments that populate the other-instrument note grid."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    ranges = [(36515, 36545), (36580, 37030)]
    for name in ("void add_full_mix_display_mirror(", "NoteCandidateList full_mix_display_candidates("):
        for index, line in enumerate(lines):
            if line.startswith(name):
                ranges.append((index + 1, index + 130))
                break
    for first, last in ranges:
        print(f"[{first}-{last}]")
        for line_number in range(first, min(last, len(lines)) + 1):
            print(f"{line_number}: {lines[line_number - 1]}")


if __name__ == "__main__":
    main()
