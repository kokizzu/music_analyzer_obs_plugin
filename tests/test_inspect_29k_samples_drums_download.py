#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def inspect(script: Path, archive: Path) -> str:
    return subprocess.run(
        [sys.executable, str(script), str(archive)], text=True, capture_output=True, check=True
    ).stdout


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "inspect_29k_samples_drums_download.py"
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "fixture.zip"
        absent = inspect(script, archive)
        if "state=absent" not in absent or "bytes=0" not in absent:
            raise SystemExit(f"unexpected absent state:\n{absent}")
        partial = archive.with_name(archive.name + ".part")
        partial.write_bytes(b"partial")
        partial.with_name(partial.name + ".aria2").write_bytes(b"resume")
        resumable = inspect(script, archive)
        if "state=partial" not in resumable or "bytes=7" not in resumable or "resume_control=1" not in resumable:
            raise SystemExit(f"unexpected partial state:\n{resumable}")
        archive.write_bytes(b"archive")
        complete = inspect(script, archive)
        if "state=archive" not in complete or "bytes=7" not in complete:
            raise SystemExit(f"unexpected archive state:\n{complete}")
    print("test_inspect_29k_samples_drums_download: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
