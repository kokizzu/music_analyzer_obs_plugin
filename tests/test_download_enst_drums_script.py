#!/usr/bin/env python3
"""Regression checks for the ENST download licence gate (without networking)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_enst_drums.sh"
URL = "https://zenodo.org/record/7831843/files/enstdrums_yourmt3_16k.tar.gz?download=1"
MD5 = "7e28c2a923e4f4162b3d83877cedb5eb"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "enst" / "enstdrums_yourmt3_16k.tar.gz"
        result = subprocess.run(
            ["sh", str(SCRIPT), str(archive), URL, MD5, "0"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 2, result.stderr
        assert "ENST_DRUMS_LICENSE_ACCEPTED=1" in result.stderr
        assert not archive.exists()
        assert not archive.parent.exists()
    print("test_download_enst_drums_script: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
