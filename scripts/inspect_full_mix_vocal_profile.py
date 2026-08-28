#!/usr/bin/env python3
"""Print the full-mix vocal profile gate and its helper predicates."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"
NAMES = ("full_mix_vocal_profile_supported", "measured_full_mix_sustained_voice_profile",
         "full_mix_polyphonic_vocal_profile_supported")


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for name in NAMES:
        starts = [index for index, line in enumerate(lines) if name in line and "bool " in line]
        if not starts:
            continue
        start = starts[0]
        print(f"== {name} ==")
        for index in range(start, min(len(lines), start + 90)):
            print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
