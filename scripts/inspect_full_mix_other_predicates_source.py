#!/usr/bin/env python3
"""Print the targeted Other-row recovery predicates and their call site."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "analyzer.cpp"
NAMES = (
    "keyboard_owned_measured_violin_other_display_supported",
    "guitar_owned_measured_string_other_display_supported",
    "low_acoustic_string_other_display_supported",
    "measured_ambiguous_smooth_violin_octave_supported",
    "full_mix_display_mirror_supported",
)


def print_function(lines: list[str], name: str) -> None:
    start = next((i for i, line in enumerate(lines) if name in line and "(" in line), None)
    if start is None:
        raise SystemExit(f"missing {name}")
    depth = 0
    end = start
    opened = False
    for index in range(start, len(lines)):
        depth += lines[index].count("{")
        if lines[index].count("{"):
            opened = True
        depth -= lines[index].count("}")
        end = index
        if opened and depth == 0:
            break
    print(f"--- {SOURCE}:{start + 1} {name} ---")
    for index in range(start, end + 1):
        print(f"{index + 1:6d}  {lines[index].rstrip()}")


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for name in NAMES:
        print_function(lines, name)


if __name__ == "__main__":
    main()
