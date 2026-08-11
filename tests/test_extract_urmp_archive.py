#!/usr/bin/env python3
"""Regression checks for external URMP ZIP extraction."""

import argparse
import subprocess
import tempfile
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="urmp-extract-") as temporary:
        root = Path(temporary)
        archive_path = root / "urmp.zip"
        destination = root / "external-store" / "urmp" / "extracted"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("Dataset/01_Jupiter/AuMix_01_Jupiter.wav", b"wav")
            archive.writestr("Dataset/01_Jupiter/Notes_01_Jupiter_1.txt", b"0.0\t1.0\t60\n")

        command = ["sh", str(args.script), str(archive_path), str(destination)]
        subprocess.run(command, check=True)
        assert (destination / "Dataset" / "01_Jupiter" / "AuMix_01_Jupiter.wav").is_file()

        # A valid existing external extraction must be harmlessly reusable.
        subprocess.run(command, check=True)

    print("extract_urmp_archive: ok")


if __name__ == "__main__":
    main()
