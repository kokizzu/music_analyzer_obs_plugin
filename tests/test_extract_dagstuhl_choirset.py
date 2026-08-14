#!/usr/bin/env python3
"""Regression checks for safe, idempotent DCS extraction."""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_dagstuhl_choirset as extractor


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "dcs.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("DagstuhlChoirSet/README.md", "fixture")
            zipped.writestr("DagstuhlChoirSet/audio.wav", "audio")
        output = root / "extracted"
        assert extractor.extract(archive, output) == 2
        assert extractor.extract(archive, output) == 2
        assert (output / "DagstuhlChoirSet" / "README.md").is_file()
    print("test_extract_dagstuhl_choirset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
