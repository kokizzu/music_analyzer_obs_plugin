#!/usr/bin/env python3
"""Report whether the compact annotated IDMT bass fixture workflow is wired."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "importer": Path("scripts/import_idmt_bass_single_track_archive.py"),
    "inspector": Path("scripts/inspect_idmt_bass_single_track_layout.py"),
}
TARGETS = (
    "import-idmt-bass-single-track-archive",
    "inspect-idmt-bass-single-track-layout",
)


def main() -> int:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    complete = True
    for label, relative in EXPECTED.items():
        present = (ROOT / relative).is_file()
        print(f"{label}: {'present' if present else 'missing'} ({relative})")
        complete &= present
    for target in TARGETS:
        present = f"{target}:" in makefile
        print(f"target {target}: {'present' if present else 'missing'}")
        complete &= present
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
