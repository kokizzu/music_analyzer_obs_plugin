#!/usr/bin/env python3
"""Regression checks for MIR-1K archive validation."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import tarfile
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_mir1k_dataset.py"
SPEC = importlib.util.spec_from_file_location("validate_mir1k", SCRIPT)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


def write_archive(path: Path, member: str) -> str:
    with tarfile.open(path, "w:gz") as archive:
        data = b"fixture"
        info = tarfile.TarInfo(member)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "mir1k.tar.gz"
        digest = write_archive(archive, "mir1k/track.wav")
        assert VALIDATE.validate(archive, digest) == 1
        try:
            VALIDATE.validate(archive, "0" * 32)
        except ValueError as error:
            assert "checksum" in str(error)
        else:
            raise AssertionError("expected checksum failure")
        unsafe = root / "unsafe.tar.gz"
        unsafe_digest = write_archive(unsafe, "../escape.wav")
        try:
            VALIDATE.validate(unsafe, unsafe_digest)
        except ValueError as error:
            assert "unsafe" in str(error)
        else:
            raise AssertionError("expected traversal failure")
    print("test_validate_mir1k_dataset: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
