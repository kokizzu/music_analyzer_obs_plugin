#!/usr/bin/env python3
"""Regression checks for MIR-1K archive inventory."""

from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_mir1k_dataset_archive.py"
SPEC = importlib.util.spec_from_file_location("inspect_mir1k", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def add_file(archive: tarfile.TarFile, name: str) -> None:
    info = tarfile.TarInfo(name)
    info.size = 1
    archive.addfile(info, io.BytesIO(b"x"))


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "mir1k.tar.gz"
        with tarfile.open(archive, "w:gz") as packed:
            add_file(packed, "mir1k/audio/track.wav")
            add_file(packed, "mir1k/labels/track.json")
        files, roots, extensions = INSPECT.inventory(str(archive))
        assert files == ["mir1k/audio/track.wav", "mir1k/labels/track.json"]
        assert roots == {"mir1k": 2}
        assert extensions == {"json": 1, "wav": 1}
    print("test_inspect_mir1k_dataset_archive: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
