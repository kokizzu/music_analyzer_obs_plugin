#!/usr/bin/env python3
"""Print the source-mode setup for the real-note full-mix replay corpus."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "tests/analyzer_real_note_samples.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed_until = -1
    for index, line in enumerate(lines):
        lowered = line.lower()
        if ("full_mix" not in lowered and "source_name" not in lowered and "input_mode" not in lowered
                and "verbose_drum" not in lowered):
            continue
        start = max(0, index - 4)
        end = min(len(lines), index + 5)
        if start <= printed_until:
            continue
        for current in range(start, end):
            print(f"{current + 1:5}: {lines[current]}")
        print()
        printed_until = end - 1


if __name__ == "__main__":
    main()
