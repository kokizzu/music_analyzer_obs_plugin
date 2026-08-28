#!/usr/bin/env python3
"""Print the compact IDMT bass importer configuration source."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "scripts/import_idmt_bass_single_track_archive.py"


def main() -> int:
    if not SOURCE.is_file():
        return 1
    for number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{number:4}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
