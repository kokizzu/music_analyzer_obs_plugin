#!/usr/bin/env python3
"""Report the state of the resumable BabySlakh download."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive = args.archive
    state_dir = archive.parent
    part = archive.with_name(archive.name + ".part")

    if archive.is_file():
        print(f"state=downloaded size_bytes={archive.stat().st_size}")
        return 0
    service = subprocess.run(
        ["systemctl", "--user", "is-active", "--quiet", "music-analyzer-babyslakh-download.service"],
        check=False,
    )
    print("state=running" if service.returncode == 0 else "state=not_running")
    print(f"partial_bytes={part.stat().st_size if part.is_file() else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
