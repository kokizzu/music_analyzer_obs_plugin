#!/usr/bin/env python3
"""Regression checks for ESMUC Choir Dataset archive inventory."""

from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_esmuc_choir_dataset_archive.py"
SPEC = importlib.util.spec_from_file_location("inspect_esmuc", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "esmuc.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("EsmucChoirDataset/audio/S1.wav", "audio")
            zipped.writestr("EsmucChoirDataset/notes/S1.txt", "notes")
            zipped.writestr("README", "readme")
        files, roots, extensions = INSPECT.inventory(str(archive))
        assert files == ["EsmucChoirDataset/audio/S1.wav", "EsmucChoirDataset/notes/S1.txt", "README"]
        assert roots == {"EsmucChoirDataset": 2, "README": 1}
        assert extensions == {"wav": 1, "txt": 1, "(none)": 1}
    print("test_inspect_esmuc_choir_dataset_archive: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
