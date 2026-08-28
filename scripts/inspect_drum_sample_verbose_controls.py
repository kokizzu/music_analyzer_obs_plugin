#!/usr/bin/env python3
"""Print drum-sample test environment controls and primary-miss reporting."""

from pathlib import Path


def main() -> None:
    path = Path("tests/analyzer_drum_samples.cpp")
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = []
    for index, line in enumerate(lines, start=1):
        if "MUSIC_ANALYZER" in line or "getenv" in line or "verbose" in line.lower():
            matches.append((index, line))

    if not matches:
        print("No environment-controlled verbose mode found in analyzer_drum_samples.cpp")
        return

    for index, line in matches:
        print(f"{index:5}: {line}")


if __name__ == "__main__":
    main()
