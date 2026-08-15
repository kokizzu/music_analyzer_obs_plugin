#!/usr/bin/env python3
"""Validate one official IRMAS ZIP before it is extracted from InstrumentSamples."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import stat
import zipfile


def safe_member(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    if path.is_absolute() or ".." in path.parts:
        return False
    return not stat.S_ISLNK(info.external_attr >> 16)


def digest(path: Path) -> str:
    value = hashlib.md5()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def validate(path: Path, expected_md5: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing or empty archive: {path}")
    actual = digest(path)
    if actual.lower() != expected_md5.lower():
        raise ValueError(f"{path}: MD5 {actual}, expected {expected_md5}")
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if not members:
            raise ValueError(f"{path}: empty ZIP")
        unsafe = [member.filename for member in members if not safe_member(member)]
        if unsafe:
            raise ValueError(f"{path}: unsafe member {unsafe[0]!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--md5", required=True)
    args = parser.parse_args()
    validate(args.archive, args.md5)
    print(f"validate_irmas_archive: ok {args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
