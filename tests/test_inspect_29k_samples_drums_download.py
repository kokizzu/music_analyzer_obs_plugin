#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def inspect(script: Path, archive: Path, job_log: Path | None = None) -> str:
    command = [sys.executable, str(script), str(archive)]
    if job_log is not None:
        command.append(str(job_log))
    return subprocess.run(
        command, text=True, capture_output=True, check=True
    ).stdout


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "inspect_29k_samples_drums_download.py"
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "fixture.zip"
        absent = inspect(script, archive)
        if "state=absent" not in absent or "logical_bytes=0" not in absent or "aria2_downloaded_bytes=unknown" not in absent:
            raise SystemExit(f"unexpected absent state:\n{absent}")
        partial = archive.with_name(archive.name + ".part")
        partial.write_bytes(b"partial")
        partial.with_name(partial.name + ".aria2").write_bytes(b"resume")
        job_log = Path(temporary) / "job.log"
        job_log.write_bytes(b"\r[#abc 32MiB/897MiB(3%) CN:8 DL:1MiB ETA:1m]\n")
        resumable = inspect(script, archive, job_log)
        if "state=partial" not in resumable or "logical_bytes=7" not in resumable or "aria2_downloaded_bytes=33554432" not in resumable or "aria2_total_bytes=940572672" not in resumable or "resume_control=1" not in resumable:
            raise SystemExit(f"unexpected partial state:\n{resumable}")
        archive.write_bytes(b"archive")
        complete = inspect(script, archive, job_log)
        if "state=archive" not in complete or "logical_bytes=7" not in complete or "aria2_downloaded_bytes=33554432" not in complete:
            raise SystemExit(f"unexpected archive state:\n{complete}")
    print("test_inspect_29k_samples_drums_download: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
