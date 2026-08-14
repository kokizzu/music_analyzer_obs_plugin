#!/usr/bin/env python3
"""Validate the checksum-pinned Saraga Carnatic Melody Synth archive."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path, PurePosixPath


def digest(path: Path) -> str:
    hasher = hashlib.md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def validate(path: Path, expected_md5: str) -> int:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"missing or empty archive: {path}")
    actual = digest(path)
    if actual.lower() != expected_md5.lower():
        raise ValueError(f"checksum mismatch: expected {expected_md5}, got {actual}")
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if not members:
            raise ValueError("archive has no members")
        for member in members:
            member_path = PurePosixPath(member.filename)
            if member.filename and (member_path.is_absolute() or ".." in member_path.parts):
                raise ValueError(f"unsafe archive member: {member.filename}")
    return len(members)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--expected-md5", required=True)
    args = parser.parse_args(argv)
    try:
        members = validate(args.archive, args.expected_md5)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(f"validate_scms_dataset: valid {args.archive} members={members}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
