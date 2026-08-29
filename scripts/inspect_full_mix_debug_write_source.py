#!/usr/bin/env python3
"""Print writes to full-mix debug candidates and nearby ownership flow."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if "full_mix_debug_candidate" not in line:
            continue
        start, end = max(0, index - 12), min(len(lines), index + 22)
        if any(current in seen for current in range(start, end)):
            continue
        print(f"--- {SOURCE}:{index + 1} ---")
        for current in range(start, end):
            seen.add(current)
            print(f"{current + 1:6d}  {lines[current]}")
    for index, line in enumerate(lines):
        if "set_note_grid_from_candidates(snapshot." not in line:
            continue
        print(f"--- {SOURCE}:{index + 1} final grid write ---")
        for current in range(max(0, index - 2), min(len(lines), index + 3)):
            print(f"{current + 1:6d}  {lines[current]}")
    for index, line in enumerate(lines):
        if "snapshot.other_notes" not in line and "snapshot.keyboard_notes" not in line and "snapshot.guitar_notes" not in line:
            continue
        print(f"--- {SOURCE}:{index + 1} rendered row write ---")
        for current in range(max(0, index - 2), min(len(lines), index + 3)):
            print(f"{current + 1:6d}  {lines[current]}")
    for index, line in enumerate(lines):
        if "mixed_other_display" not in line:
            continue
        print(f"--- {SOURCE}:{index + 1} mixed Other candidate flow ---")
        for current in range(max(0, index - 8), min(len(lines), index + 10)):
            print(f"{current + 1:6d}  {lines[current]}")
    start = next(index for index, line in enumerate(lines) if line.startswith("void set_note_grid_from_candidates("))
    depth = 0
    entered = False
    print(f"--- {SOURCE}:{start + 1} set_note_grid_from_candidates ---")
    for index in range(start, len(lines)):
        opens = lines[index].count("{")
        depth += opens - lines[index].count("}")
        entered = entered or opens > 0
        print(f"{index + 1:6d}  {lines[index]}")
        if entered and depth == 0:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
