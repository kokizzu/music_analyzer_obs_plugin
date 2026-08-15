#!/usr/bin/env python3
"""Regression checks for fast MAESTRO subset archive validation."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import zipfile


PROJECT = Path(__file__).parents[1]
SCRIPT = PROJECT / "scripts" / "validate_maestro_subset_archive.py"
sys.path.insert(0, str(PROJECT / "scripts"))
SPEC = importlib.util.spec_from_file_location("validate_maestro_subset_archive", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_pair_archive(path: Path):
    with zipfile.ZipFile(path, "w") as zipped:
        zipped.writestr("maestro-v3.0.0/2018/MIDI-Unprocessed_01.midi", b"midi")
        zipped.writestr("maestro-v3.0.0/2018/MIDI-Unprocessed_01.wav", b"wav")


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "maestro.zip"
        write_pair_archive(archive)
        assert MODULE.validate(archive, "OTHER", 1) == 1
        try:
            MODULE.validate(archive, "OTHER", 2)
        except ValueError as error:
            assert "at least 2" in str(error)
        else:
            raise AssertionError("missing pair count should fail")
        invalid = root / "invalid.zip"
        invalid.write_bytes(b"not a ZIP")
        try:
            MODULE.validate(invalid, "OTHER", 1)
        except ValueError as error:
            assert "invalid ZIP structure" in str(error)
        else:
            raise AssertionError("invalid central directory should fail")
    print("test_validate_maestro_subset_archive: 3 checks passed")


if __name__ == "__main__":
    main()
