#!/usr/bin/env python3
"""Safely extract a verified BabySlakh archive into external sample storage."""

from __future__ import annotations

import argparse
import os
import shutil
import tarfile
from pathlib import Path, PurePosixPath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    return parser.parse_args()


def safe_relative_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe archive member: {name!r}")
    return path


def validate_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    for member in members:
        safe_relative_name(member.name)
        if member.issym() or member.islnk() or member.isdev():
            raise ValueError(f"unsupported archive member type: {member.name!r}")
        if not (member.isdir() or member.isfile()):
            raise ValueError(f"unsupported archive member type: {member.name!r}")
    return members


def main() -> int:
    args = parse_args()
    if not args.archive.is_file():
        raise SystemExit(f"extract_babyslakh_archive: missing archive: {args.archive}")
    destination = args.destination.resolve()
    temporary = destination.with_name(destination.name + ".partial")
    if destination.exists():
        print(f"extract_babyslakh_archive: reused {destination}")
        return 0

    with tarfile.open(args.archive, "r:gz") as archive:
        members = validate_members(archive)
        if temporary.exists():
            shutil.rmtree(temporary)
        temporary.mkdir(parents=True)
        for member in members:
            output = temporary.joinpath(*safe_relative_name(member.name).parts)
            if member.isdir():
                output.mkdir(parents=True, exist_ok=True)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"unreadable archive member: {member.name!r}")
            with source, output.open("wb") as target:
                shutil.copyfileobj(source, target)
            os.chmod(output, member.mode & 0o777)

    temporary.rename(destination)
    print(f"extract_babyslakh_archive: extracted {len(members)} members to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
