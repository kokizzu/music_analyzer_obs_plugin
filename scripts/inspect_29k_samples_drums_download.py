#!/usr/bin/env python3
"""Report the resumable 29k Drums archive state without touching its data."""

from __future__ import annotations

import sys
from pathlib import Path


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
    if len(sys.argv) != 2:
        print("usage: inspect_29k_samples_drums_download.py ARCHIVE", file=sys.stderr)
        return 2
    archive = Path(sys.argv[1])
    partial = archive.with_name(archive.name + ".part")
    control = partial.with_name(partial.name + ".aria2")
    state, payload = state_for(archive)
    size = payload.stat().st_size if payload else 0
    print(f"29k_samples_drums_download: state={state}")
    print(f"archive={archive}")
    print(f"bytes={size}")
    print(f"resume_control={int(control.exists())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
