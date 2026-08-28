#!/usr/bin/env python3
"""Print guitar chord-detection call sites and nearby root-evidence logic."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
NEEDLES = (
    "detect_chord(",
    "promote_supported_plain_guitar_primary",
    "promote_weak_visible_root_later_plain_guitar_primary",
    "const int preferred_root = lowest_note_grid_pitch_class(grid)",
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if not any(needle in line for needle in NEEDLES):
            continue
        start = max(0, index - 12)
        extended = (
            "preferred_root = lowest_note_grid_pitch_class" in line
            or "raw_guitar_label_before_promotion" in line
            or "smoothed_guitar_label_before_promotion" in line
        )
        end = min(len(lines), index + (120 if extended else 28))
        if all(position in seen for position in range(start, end)):
            continue
        seen.update(range(start, end))
        print(f"## {start + 1}-{end}")
        for position in range(start, end):
            print(f"{position + 1}: {lines[position]}")


if __name__ == "__main__":
    main()
