#!/usr/bin/env python3
"""Regression test for the non-extracting BabySlakh archive inspector."""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = REPOSITORY_ROOT / "scripts" / "inspect_babyslakh_archive.py"


def add_member(archive: tarfile.TarFile, name: str) -> None:
    entry = tarfile.TarInfo(name)
    entry.size = 0
    archive.addfile(entry)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive_path = Path(temporary) / "babyslakh.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            add_member(archive, "BabySlakh/train/Track00001/mix.flac")
            add_member(archive, "BabySlakh/train/Track00001/all_src.mid")
            add_member(archive, "BabySlakh/train/Track00001/metadata.yaml")

        completed = subprocess.run(
            [sys.executable, str(INSPECTOR), str(archive_path)],
            check=True,
            capture_output=True,
            text=True,
        )

    rows = dict(line.split("=", 1) for line in completed.stdout.splitlines() if "=" in line)
    assert rows["regular_members"] == "3", rows
    assert rows["audio_members"] == "1", rows
    assert rows["midi_members"] == "1", rows
    assert rows["suffixes"] == ".flac:1,.mid:1,.yaml:1", rows
    print("test_inspect_babyslakh_archive: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
