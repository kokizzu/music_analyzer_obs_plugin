#!/usr/bin/env python3
"""Print the full-mix owner classifier and its immediate callers for review."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"


def print_block(lines: list[str], name: str) -> None:
    start = next(index for index, line in enumerate(lines) if name in line and "(" in line)
    depth = 0
    entered = False
    end = start
    for index in range(start, len(lines)):
        opens = lines[index].count("{")
        depth += opens - lines[index].count("}")
        entered = entered or opens > 0
        if entered and depth == 0:
            end = index
            break
    print(f"--- {SOURCE}:{start + 1} {name} ---")
    for index in range(start, end + 1):
        print(f"{index + 1:6d}  {lines[index]}")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for name in ("choose_full_mix_owner", "boost_existing_measured_violin_other_visual_notes",
                 "boost_existing_measured_acoustic_string_other_visual_notes",
                 "full_mix_display_candidates", "add_full_mix_display_mirror"):
        try:
            print_block(lines, name)
        except StopIteration:
            continue
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
