#!/usr/bin/env python3
"""Regression checks for safe, idempotent MIR-1K extraction."""

from __future__ import annotations

import io
import sys
import tarfile
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_mir1k_dataset as extractor


def add_file(archive: tarfile.TarFile, name: str, value: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    archive.addfile(info, io.BytesIO(value))


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "mir1k.tar.gz"
        with tarfile.open(archive, "w:gz") as packed:
            add_file(packed, "mir1k/audio/track.wav", b"audio")
            add_file(packed, "mir1k/labels/track.json", b"{}")
        output = root / "extracted"
        assert extractor.extract(archive, output) == 2
        assert extractor.extract(archive, output) == 2
        assert (output / extractor.READY_FILE).is_file()

        stale = root / ".retry.tmp-fixture"
        stale.mkdir()
        (stale / "partial.wav").write_text("partial", encoding="utf-8")
        assert extractor.discard_stale_staging(root / "retry") == 1
        assert not stale.exists()
    print("test_extract_mir1k_dataset: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
