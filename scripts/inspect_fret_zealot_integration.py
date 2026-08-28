#!/usr/bin/env python3
"""Locate Fret Zealot packet-builder and device-control integration references."""

from __future__ import annotations

from pathlib import Path


TERMS = (
    "build_fret_zealot_major_scale_packet",
    "ExternalDevice::FretZealot",
    "FretZealot",
    "fret_zealot",
)
SKIP_PARTS = {".git", "build", ".cache"}
TEXT_SUFFIXES = {".cpp", ".c", ".h", ".hpp", ".cmake", ".txt", ".py", ".sh", ".md"}


def main() -> int:
    matches: list[tuple[Path, int, str]] = []
    for path in sorted(Path(".").rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "Makefile":
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines):
            if any(term in line for term in TERMS):
                matches.append((path, index, line))

    print(f"fret_zealot_integration matches={len(matches)}")
    for path, index, line in matches:
        print(f"{path}:{index + 1}: {line}")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
