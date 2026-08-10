#!/usr/bin/env python3
"""Report the resumable GuitarSet archive state without modifying it."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


def describe(name: str, path: Path) -> str:
    if not path.exists():
        return f"guitarset_download: {name}=missing path={path}"
    size = path.stat().st_size
    try:
        with zipfile.ZipFile(path) as archive:
            invalid_member = archive.testzip()
            if invalid_member is not None:
                return (
                    f"guitarset_download: {name}=invalid bytes={size} path={path} "
                    f"member={invalid_member}"
                )
            return f"guitarset_download: {name}=complete bytes={size} path={path}"
    except (OSError, zipfile.BadZipFile):
        return f"guitarset_download: {name}=partial bytes={size} path={path}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation", required=True, type=Path)
    parser.add_argument("--audio", required=True, type=Path)
    args = parser.parse_args()
    print(describe("annotation", args.annotation))
    print(describe("annotation_part", args.annotation.with_suffix(args.annotation.suffix + ".part")))
    print(describe("audio", args.audio))
    print(describe("audio_part", args.audio.with_suffix(args.audio.suffix + ".part")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
