#!/usr/bin/env python3
"""Validate the reproducible MIR-1K/YourMT3 archive before extraction."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path, PurePosixPath


def digest(path: Path) -> str:
    hasher = hashlib.md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def safe_member(member: tarfile.TarInfo) -> bool:
    path = PurePosixPath(member.name)
    return (
        bool(member.name)
        and not path.is_absolute()
        and ".." not in path.parts
        and (member.isdir() or member.isfile())
    )


def validate(path: Path, expected_md5: str) -> int:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"missing or empty archive: {path}")
    actual = digest(path)
    if actual.lower() != expected_md5.lower():
        raise ValueError(f"checksum mismatch: expected {expected_md5}, got {actual}")
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        if not members:
            raise ValueError("archive has no members")
        for member in members:
            if not safe_member(member):
                raise ValueError(f"unsafe archive member: {member.name}")
    return len(members)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--expected-md5", required=True)
    args = parser.parse_args(argv)
    try:
        members = validate(args.archive, args.expected_md5)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.error(str(error))
    print(f"validate_mir1k_dataset: valid {args.archive} members={members}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
