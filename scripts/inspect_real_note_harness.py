#!/usr/bin/env python3
"""Print the real-note harness controls and per-sample diagnostic format."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/analyzer_real_note_samples.cpp"
KEYWORDS = ("attribute_header", "attribute_lines", "attribute_export", "ATTRIBUTE_TSV")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        if not any(keyword in line for keyword in KEYWORDS):
            continue
        start = max(1, number - 3)
        end = min(len(lines), number + 5)
        print(f"-- {start}-{end} --")
        for context_number in range(start, end + 1):
            print(f"{context_number}: {lines[context_number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
