#!/usr/bin/env python3
"""Diagnose the local compact-IDMT archive without modifying it."""

from __future__ import annotations

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent.parent / "build/InstrumentSamples/idmt_smt_bass_single_track"
ARCHIVES = (
    ROOT / "IDMT-SMT-BASS-SINGLE-TRACKS.zip",
    ROOT / "IDMT-SMT-BASS-SINGLE-TRACKS.zip.part",
)


def main() -> int:
    for path in ARCHIVES:
        if not path.exists():
            print(f"{path}: absent")
            continue
        print(f"{path}: {path.stat().st_size} bytes")
        try:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                print(f"  entries={len(archive.infolist())} first_bad={bad or 'none'}")
        except (OSError, zipfile.BadZipFile) as error:
            print(f"  invalid: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
