#!/usr/bin/env python3
"""Regression checks for safe, idempotent SCMS ZIP extraction."""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_scms_dataset as extractor


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "scms.zip"
        with zipfile.ZipFile(archive, "w") as packed:
            packed.writestr("SCMS/audio/track.wav", b"audio")
            packed.writestr("SCMS/pitch/track.csv", b"0,440\n")
        output = root / "extracted"
        assert extractor.extract(archive, output) == 2
        assert extractor.extract(archive, output) == 2
        assert (output / extractor.READY_FILE).is_file()

        stale = root / ".retry.tmp-fixture"
        stale.mkdir()
        (stale / "partial.wav").write_text("partial", encoding="utf-8")
        assert extractor.discard_stale_staging(root / "retry") == 1
        assert not stale.exists()

        unsafe_archive = root / "unsafe.zip"
        with zipfile.ZipFile(unsafe_archive, "w") as packed:
            packed.writestr("../outside.wav", b"unsafe")
        try:
            extractor.extract(unsafe_archive, root / "unsafe-extracted")
        except ValueError as error:
            assert "unsafe archive member" in str(error)
        else:
            raise AssertionError("unsafe ZIP member should be rejected")
    print("test_extract_scms_dataset: 7 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
