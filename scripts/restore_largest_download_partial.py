#!/usr/bin/env python3
"""Recover the larger preserved partial archive without discarding either file."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive = args.archive
    partial = archive.with_suffix(archive.suffix + ".part")
    preserved = archive.with_suffix(archive.suffix + ".corrupt")
    restart = archive.with_suffix(archive.suffix + ".part.restart")

    if not preserved.is_file():
        print(f"download_partial_restore: preserved=missing path={preserved}")
        return 0
    if restart.exists():
        raise SystemExit(f"download_partial_restore: refusing to overwrite {restart}")
    preserved_size = preserved.stat().st_size
    partial_size = partial.stat().st_size if partial.is_file() else 0
    if preserved_size <= partial_size:
        print(
            "download_partial_restore: kept_current "
            f"current_bytes={partial_size} preserved_bytes={preserved_size}"
        )
        return 0
    if partial.is_file():
        partial.rename(restart)
    preserved.rename(partial)
    print(
        "download_partial_restore: restored_larger "
        f"partial_bytes={preserved_size} saved_restart_bytes={partial_size}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
