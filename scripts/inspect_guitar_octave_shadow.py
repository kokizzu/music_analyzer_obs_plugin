#!/usr/bin/env python3
"""Print the existing guitar octave-shadow attenuation implementation."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
MARKER = "attenuate_lower_non_guitar_pitch_class_guitar_octave_shadows"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for start, line in enumerate(lines):
        if MARKER not in line or not line.lstrip().startswith("void "):
            continue
        for index in range(start, min(len(lines), start + 180)):
            print(f"{index + 1}: {lines[index]}")
        return
    raise SystemExit(f"function not found: {MARKER}")


if __name__ == "__main__":
    main()
