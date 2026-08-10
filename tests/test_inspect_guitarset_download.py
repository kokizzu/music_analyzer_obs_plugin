#!/usr/bin/env python3
"""Regression coverage for the non-mutating GuitarSet download inspector."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_guitarset_download.py"
RESTORE = ROOT / "scripts" / "restore_largest_download_partial.py"


def run(annotation: Path, audio: Path) -> str:
    return subprocess.check_output(
        [sys.executable, str(SCRIPT), "--annotation", str(annotation), "--audio", str(audio)],
        text=True,
    )


def restore(archive: Path) -> str:
    return subprocess.check_output([sys.executable, str(RESTORE), str(archive)], text=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        annotation = root / "annotation.zip"
        audio = root / "audio_mono-mic.zip"
        audio_part = audio.with_suffix(".zip.part")
        with zipfile.ZipFile(annotation, "w") as archive:
            archive.writestr("annotation.txt", "ok")
        audio_part.write_bytes(b"incomplete archive")

        output = run(annotation, audio)
        assert "annotation=complete" in output
        assert "annotation_part=missing" in output
        assert "annotation_preserved=missing" in output
        assert "audio=missing" in output
        assert "audio_part=partial" in output
        assert "audio_preserved=missing" in output

        preserved = audio.with_suffix(".zip.corrupt")
        preserved.write_bytes(b"larger interrupted download")
        restore_output = restore(audio)
        assert "restored_larger" in restore_output
        assert audio_part.read_bytes() == b"larger interrupted download"
        assert audio.with_suffix(".zip.part.restart").read_bytes() == b"incomplete archive"

        preserved.write_bytes(b"older")
        second_restore = subprocess.run(
            [sys.executable, str(RESTORE), str(audio)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert second_restore.returncode != 0
        assert "refusing to overwrite" in second_restore.stderr
        assert audio_part.read_bytes() == b"larger interrupted download"
        assert preserved.read_bytes() == b"older"

    print("test_inspect_guitarset_download: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
