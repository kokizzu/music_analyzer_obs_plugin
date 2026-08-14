#!/usr/bin/env python3
"""Regression checks for the SCMS archive inventory."""

from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_scms_dataset_archive.py"
SPEC = importlib.util.spec_from_file_location("inspect_scms", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive_path = Path(temporary) / "scms.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("SCMS/audio/example.wav", b"audio")
            archive.writestr("SCMS/annotations/example.csv", b"time,f0\n")
            archive.writestr("README", b"notes")
        result = INSPECT.inspect(archive_path)
        assert result["members"] == 3
        assert result["extensions"][".wav"] == 1
        assert result["extensions"][".csv"] == 1
        output = INSPECT.summary(archive_path)
        assert "members: 3" in output
        assert ".wav: 1 files 5 bytes" in output
    print("test_inspect_scms_dataset_archive: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
