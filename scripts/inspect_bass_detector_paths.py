#!/usr/bin/env python3
"""Locate isolated-bass tracking and octave-selection paths for fixture diagnosis."""

from pathlib import Path


SYMBOLS = (
    "tracked_bass_midi_",
    "bass_spectral_midi",
    "bass_periodic_midi",
    "isolated_bass",
    "prefer_supported_lower_octave_candidates",
    "choose_isolated_bass_note",
    "dominant_bass_note(",
)


def main() -> int:
    lines = Path("src/analyzer.cpp").read_text().splitlines()
    for symbol in SYMBOLS:
        print(f"# {symbol}")
        hits = [index for index, line in enumerate(lines) if symbol in line]
        for index in hits[:3]:
            print(f"## analyzer.cpp:{index + 1}")
            for number in range(max(0, index - 4), min(len(lines), index + 22)):
                print(f"{number + 1}: {lines[number]}")
        if not hits:
            print("not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
