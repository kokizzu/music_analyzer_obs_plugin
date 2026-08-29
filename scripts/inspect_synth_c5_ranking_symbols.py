#!/usr/bin/env python3
"""Locate the synthetic Other note-ranking helpers relevant to C5 diagnostics."""

from pathlib import Path


SYMBOLS = (
    "prefer_strong_visible_lower_other_octave_primary",
    "prefer_probe_supported_lower_synth_primary",
    "promote_source_hinted_other_debug_primaries",
    "boost_measured_other_fundamental_display_level",
    "prefer_debug_supported_lower_other_octave_primary",
    "prefer_visible_lower_octave_primary",
)


def main() -> int:
    lines = Path("src/analyzer.cpp").read_text().splitlines()
    for symbol in SYMBOLS:
        print(f"# {symbol}")
        hits = [index for index, line in enumerate(lines) if symbol in line]
        for index in hits[:2]:
            start = max(0, index - 2)
            end = min(len(lines), index + 24)
            for number in range(start, end):
                print(f"{number + 1}: {lines[number]}")
        if not hits:
            print("not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
