#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "inspect_29k_samples_drums.py"
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "fixture.zip"
        with zipfile.ZipFile(archive, "w") as source:
            source.writestr("29kSamples/kd/hit.wav", b"RIFF")
            source.writestr("29kSamples/ft/hit.wav", b"RIFF")
            source.writestr("29kSamples/readme.txt", "fixture")
        result = subprocess.run(
            [sys.executable, str(script), str(archive)], text=True, capture_output=True, check=True
        )
    required = ("regular_members=3", "suffixes=.txt:1,.wav:2", "wav_members=2")
    if not all(value in result.stdout for value in required):
        raise SystemExit(f"unexpected inspection output:\n{result.stdout}")
    print("test_inspect_29k_samples_drums: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
