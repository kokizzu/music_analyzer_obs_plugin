#!/usr/bin/env python3
"""Report the resumable 29k Drums archive state without touching its data."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ARIA2_PROGRESS_RE = re.compile(
    rb"\[[^\]]+\s+(\d+)(KiB|MiB|GiB)/(\d+)(KiB|MiB|GiB)\("
)
UNIT_BYTES = {b"KiB": 1024, b"MiB": 1024 * 1024, b"GiB": 1024 * 1024 * 1024}


def state_for(archive: Path) -> tuple[str, Path | None]:
    partial = archive.with_name(archive.name + ".part")
    if archive.is_file() and archive.stat().st_size:
        return "archive", archive
    if partial.is_file() and partial.stat().st_size:
        return "partial", partial
    if partial.with_name(partial.name + ".aria2").exists():
        return "empty-resume", partial
    return "absent", None


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: inspect_29k_samples_drums_download.py ARCHIVE [JOB_LOG]", file=sys.stderr)
        return 2
    archive = Path(sys.argv[1])
    job_log = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    partial = archive.with_name(archive.name + ".part")
    control = partial.with_name(partial.name + ".aria2")
    state, payload = state_for(archive)
    logical_size = payload.stat().st_size if payload else 0
    progress = None
    if job_log is not None and job_log.is_file():
        matches = list(ARIA2_PROGRESS_RE.finditer(job_log.read_bytes()[-65536:]))
        if matches:
            downloaded, downloaded_unit, total, total_unit = matches[-1].groups()
            progress = (int(downloaded) * UNIT_BYTES[downloaded_unit],
                        int(total) * UNIT_BYTES[total_unit])
    print(f"29k_samples_drums_download: state={state}")
    print(f"archive={archive}")
    print(f"logical_bytes={logical_size}")
    if progress is None:
        print("aria2_downloaded_bytes=unknown")
    else:
        print(f"aria2_downloaded_bytes={progress[0]}")
        print(f"aria2_total_bytes={progress[1]}")
    print(f"resume_control={int(control.exists())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
