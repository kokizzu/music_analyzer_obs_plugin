#!/usr/bin/env python3
"""Print the existing mixed-source vocal display gates for focused review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEEDLES = (
    "measured_low_full_mix_vocal_display_supported",
    "full_mix_vocal_profile_supported",
    "stable_misrouted_vocal_display",
)


def main() -> None:
    path = ROOT / "src" / "analyzer.cpp"
    lines = path.read_text(encoding="utf-8").splitlines()
    for needle in NEEDLES:
        for index, line in enumerate(lines):
            if needle in line:
                start = max(0, index - 2)
                end = min(len(lines), index + 45)
                print(f"--- {path}:{index + 1} {needle} ---")
                for number in range(start, end):
                    print(f"{number + 1:6} {lines[number]}")
                break


if __name__ == "__main__":
    main()
