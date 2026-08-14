#!/usr/bin/env python3
"""Validate the public Choral Singing Dataset archive before extraction."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def validate(path: Path, expected_md5: str) -> int:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"missing or empty archive: {path}")
    actual_md5 = digest(path)
    if actual_md5.lower() != expected_md5.lower():
        raise ValueError(f"checksum mismatch: expected {expected_md5}, got {actual_md5}")
    with zipfile.ZipFile(path) as archive:
        bad = [entry.filename for entry in archive.infolist() if Path(entry.filename).is_absolute() or ".." in Path(entry.filename).parts]
        if bad:
            raise ValueError(f"unsafe archive member: {bad[0]}")
        if not archive.infolist():
            raise ValueError("archive has no members")
    return len(archive.infolist())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--expected-md5", required=True)
    args = parser.parse_args(argv)
    try:
        members = validate(args.archive, args.expected_md5)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(f"validate_choral_singing_dataset: valid {args.archive} members={members}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
