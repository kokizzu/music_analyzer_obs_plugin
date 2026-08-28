#!/usr/bin/env python3
"""Download and extract the compact annotated IDMT bass-line corpus."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import zipfile
import fcntl


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass_single_track")
ARCHIVE = ROOT / "IDMT-SMT-BASS-SINGLE-TRACKS.zip"
PARTIAL = ROOT / "IDMT-SMT-BASS-SINGLE-TRACKS.zip.part"
EXTRACTED = ROOT / "source"
COMPLETE = EXTRACTED / ".complete"
LOCK = ROOT / ".import.lock"
URL = "https://zenodo.org/records/7544099/files/IDMT-SMT-BASS-SINGLE-TRACKS.zip?download=1"


def valid_archive(path: pathlib.Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False


def download(resume: bool) -> None:
    command = ["curl", "-fL"]
    if resume:
        command.extend(["-C", "-"])
    command.extend(["-o", str(PARTIAL), URL])
    subprocess.run(command, check=True)


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w", encoding="ascii") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("IDMT bass import is already running; wait for it to finish")
        if not ARCHIVE.exists() or not valid_archive(ARCHIVE):
            if ARCHIVE.exists():
                ARCHIVE.replace(PARTIAL)
            download(resume=PARTIAL.exists())
            if not valid_archive(PARTIAL):
                # Zenodo redirects occasionally accept a range request yet return
                # a corrupt assembled ZIP. Retry once from a clean local part.
                print("resumed archive invalid; restarting one clean download")
                PARTIAL.unlink(missing_ok=True)
                download(resume=False)
            if not valid_archive(PARTIAL):
                raise SystemExit(f"downloaded archive is invalid: {PARTIAL}")
            PARTIAL.replace(ARCHIVE)
        if COMPLETE.is_file():
            print(f"IDMT bass lines already extracted: {EXTRACTED}")
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
