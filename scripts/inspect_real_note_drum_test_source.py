#!/usr/bin/env python3
"""Print the relevant analysis and diagnostic paths for real drum fixtures."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "analyzer_real_drum_samples.cpp"
MARKERS = (
    "analyze_buffer",
    "MUSIC_ANALYZER_REAL_DRUM_VERBOSE",
    "real-drums miss",
    "snapshot.drums",
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    emitted = set()
    for index, line in enumerate(lines):
        if not any(marker in line for marker in MARKERS):
            continue
        start = max(0, index - 7)
        end = min(len(lines), index + 14)
        key = (start, end)
        if key in emitted:
            continue
        emitted.add(key)
        for line_number in range(start, end):
            print(f"{line_number + 1:6} {lines[line_number]}")
        print()


if __name__ == "__main__":
    main()
