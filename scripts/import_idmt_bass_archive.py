#!/usr/bin/env python3
"""Download and extract the public IDMT-SMT-Bass archive into build/."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import zipfile


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass")
ARCHIVE = ROOT / "IDMT-SMT-BASS.zip"
PARTIAL = ROOT / "IDMT-SMT-BASS.zip.part"
EXTRACTED = ROOT / "source"
COMPLETE = EXTRACTED / ".complete"
URL = "https://zenodo.org/records/7188892/files/IDMT-SMT-BASS.zip?download=1"


def valid_archive(path: pathlib.Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists() or not valid_archive(ARCHIVE):
        if ARCHIVE.exists():
            ARCHIVE.replace(PARTIAL)
        subprocess.run(["curl", "-fL", "-C", "-", "-o", str(PARTIAL), URL], check=True)
        if not valid_archive(PARTIAL):
            raise SystemExit(f"downloaded archive is invalid: {PARTIAL}")
        PARTIAL.replace(ARCHIVE)
    if COMPLETE.is_file():
        print(f"IDMT-SMT-Bass already extracted: {EXTRACTED}")
        return 0
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    EXTRACTED.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive.extractall(EXTRACTED)
    COMPLETE.write_text("complete\n", encoding="ascii")
    print(f"archive bytes: {ARCHIVE.stat().st_size}")
    print(f"extracted: {EXTRACTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
