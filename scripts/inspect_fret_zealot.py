#!/usr/bin/env python3
"""Print line-numbered Fret Zealot implementation context for debugging."""

from __future__ import annotations

from pathlib import Path


ROOT = Path("src")
TERMS = ("fret zealot", "fret_zealot", "FretZealot", "FZ")


def main() -> int:
    matches: list[tuple[Path, int]] = []
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".cpp", ".c", ".h", ".hpp"}:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines):
            if any(term.lower() in line.lower() for term in TERMS):
                matches.append((path, index))

    print(f"fret_zealot_context matches={len(matches)}")
    emitted: set[tuple[Path, int]] = set()
    for path, index in matches:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"[{path}]")
        for line_index in range(max(0, index - 5), min(len(lines), index + 8)):
            key = (path, line_index)
            if key in emitted:
                continue
            emitted.add(key)
            print(f"{line_index + 1}: {lines[line_index]}")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
