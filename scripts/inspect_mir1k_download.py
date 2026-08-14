#!/usr/bin/env python3
"""Report the resumable MIR-1K archive download state without modifying it."""

from __future__ import annotations

import argparse
from pathlib import Path


def describe(path: Path, label: str) -> str:
    if not path.is_file():
        return f"{label}=missing"
    return f"{label}=present bytes={path.stat().st_size}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--lock-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    print("inspect_mir1k_download: " + describe(args.archive, "archive"))
    print("inspect_mir1k_download: " + describe(Path(f"{args.archive}.part"), "partial"))
    print(f"inspect_mir1k_download: lock={'held' if args.lock_dir.is_dir() else 'free'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
