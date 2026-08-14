#!/usr/bin/env python3
"""Regression checks for safe, idempotent ESMUC extraction."""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_esmuc_choir_dataset as extractor


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "esmuc.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("README.md", "fixture")
            zipped.writestr("DG_FT_take1_S1.wav", "audio")
        output = root / "extracted"
        assert extractor.extract(archive, output) == 2
        assert extractor.extract(archive, output) == 2
        assert (output / "README.md").is_file()

        stale = root / ".retry.tmp-fixture"
        stale.mkdir()
        (stale / "partial.wav").write_text("partial", encoding="utf-8")
        assert extractor.discard_stale_staging(root / "retry") == 1
        assert not stale.exists()
    print("test_extract_esmuc_choir_dataset: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
