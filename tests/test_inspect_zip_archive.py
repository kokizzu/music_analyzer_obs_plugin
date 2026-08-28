#!/usr/bin/env python3
"""Small fixture test for the generic archive inspector."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_zip_archive.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive_path = Path(temporary) / "fixture.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("aGPTset/audio/player01.wav", b"audio")
            archive.writestr("aGPTset/annotations/player01.csv", "onset,pitch\n0.0,64\n")
        result = subprocess.run(
            ["python3", str(SCRIPT), str(archive_path)], text=True, capture_output=True, check=False
        )
    assert result.returncode == 0, result.stderr
    assert "members=2" in result.stdout
    assert "suffixes=.csv:1, .wav:1" in result.stdout
    assert "annotation_candidates=1" in result.stdout
    assert "annotation_preview=aGPTset/annotations/player01.csv: onset,pitch 0.0,64" in result.stdout
    print("test_inspect_zip_archive: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
