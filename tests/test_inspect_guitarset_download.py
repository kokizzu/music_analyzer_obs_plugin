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


def run(annotation: Path, audio: Path) -> str:
    return subprocess.check_output(
        [sys.executable, str(SCRIPT), "--annotation", str(annotation), "--audio", str(audio)],
        text=True,
    )


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
        assert "audio=missing" in output
        assert "audio_part=partial" in output

    print("test_inspect_guitarset_download: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
