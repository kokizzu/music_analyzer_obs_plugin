#!/usr/bin/env python3
"""Regression checks for external MusicNet archive extraction."""

import argparse
import subprocess
import tarfile
import tempfile
from pathlib import Path


def add_dir(archive: tarfile.TarFile, name: str) -> None:
    entry = tarfile.TarInfo(name)
    entry.type = tarfile.DIRTYPE
    entry.mode = 0o755
    archive.addfile(entry)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="musicnet-extract-") as temporary:
        root = Path(temporary)
        archive_path = root / "musicnet.tar.gz"
        destination = root / "external-store" / "musicnet"
        with tarfile.open(archive_path, "w:gz") as archive:
            add_dir(archive, "musicnet/")
            add_dir(archive, "musicnet/train_data/")
            add_dir(archive, "musicnet/test_data/")

        command = ["sh", str(args.script), str(archive_path), str(destination)]
        subprocess.run(command, check=True)
        assert (destination / "train_data").is_dir()
        assert (destination / "test_data").is_dir()

        # A valid existing extraction must be harmlessly reusable.
        subprocess.run(command, check=True)

    print("extract_musicnet_archive: ok")


if __name__ == "__main__":
    main()
