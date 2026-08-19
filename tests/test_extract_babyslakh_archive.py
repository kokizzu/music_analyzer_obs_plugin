#!/usr/bin/env python3
"""Regression test for BabySlakh's safe archive extractor."""

from __future__ import annotations

import io
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = REPOSITORY_ROOT / "scripts" / "extract_babyslakh_archive.py"


def add_file(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    entry = tarfile.TarInfo(name)
    entry.size = len(data)
    archive.addfile(entry, io.BytesIO(data))


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive_path = root / "safe.tar.gz"
        output = root / "out"
        with tarfile.open(archive_path, "w:gz") as archive:
            add_file(archive, "BabySlakh/train/Track00001/all_src.mid", b"MThd")
        subprocess.run([sys.executable, str(EXTRACTOR), str(archive_path), str(output)], check=True)
        assert (output / "BabySlakh/train/Track00001/all_src.mid").read_bytes() == b"MThd"

        unsafe_archive = root / "unsafe.tar.gz"
        with tarfile.open(unsafe_archive, "w:gz") as archive:
            add_file(archive, "../escape", b"no")
        rejected = subprocess.run(
            [sys.executable, str(EXTRACTOR), str(unsafe_archive), str(root / "unsafe")],
            capture_output=True,
            text=True,
        )
        assert rejected.returncode != 0, rejected
        assert "unsafe archive member" in rejected.stderr, rejected
    print("test_extract_babyslakh_archive: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
