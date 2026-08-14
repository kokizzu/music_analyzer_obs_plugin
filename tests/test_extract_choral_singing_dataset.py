#!/usr/bin/env python3
"""Regression checks for safe, idempotent CSD extraction."""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_choral_singing_dataset as extractor


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "csd.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("ChoralSingingDataset/README.txt", "fixture")
            zipped.writestr("ChoralSingingDataset/audio.wav", "audio")
        output = root / "extracted"
        assert extractor.extract(archive, output) == 2
        assert extractor.extract(archive, output) == 2
        assert (output / "ChoralSingingDataset" / "README.txt").is_file()
    print("test_extract_choral_singing_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
