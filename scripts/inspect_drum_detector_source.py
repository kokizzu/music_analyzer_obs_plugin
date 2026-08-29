#!/usr/bin/env python3
"""Print drum activation and hi-hat threshold code for fixture-driven review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
def main() -> None:
    path = ROOT / "src" / "analyzer.cpp"
    lines = path.read_text(encoding="utf-8").splitlines()
    printed: set[int] = set()
    for index, line in enumerate(lines):
        if "Snare" not in line or not any(token in line for token in ("cap_drum_level", "boost_drum_level", "promote_drum_primary")):
            continue
        for number in range(max(0, index - 12), min(len(lines), index + 4)):
            if number in printed:
                continue
            printed.add(number)
            print(f"{number + 1:6} {lines[number]}")


if __name__ == "__main__":
    main()
