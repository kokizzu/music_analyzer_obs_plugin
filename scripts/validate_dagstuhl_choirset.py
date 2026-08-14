#!/usr/bin/env python3
"""Validate the downloaded Dagstuhl ChoirSet archive before it is extracted."""

import argparse
import hashlib
import sys
import zipfile
from pathlib import PurePosixPath


def safe_member(name: str) -> bool:
    """Return whether a ZIP member remains beneath its extraction root."""
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return bool(normalized) and not path.is_absolute() and ".." not in path.parts and not path.drive


def archive_md5(path: str) -> str:
    digest = hashlib.md5()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive(path: str, expected_md5: str) -> int:
    digest = archive_md5(path)
    if expected_md5 and digest.lower() != expected_md5.lower():
        raise ValueError(f"MD5 mismatch: got {digest}, expected {expected_md5}")
    with zipfile.ZipFile(path) as archive:
        files = 0
        for member in archive.infolist():
            if not safe_member(member.filename):
                raise ValueError(f"unsafe archive member: {member.filename}")
            if not member.is_dir():
                files += 1
        if files == 0:
            raise ValueError("archive has no files")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--expected-md5", default="")
    args = parser.parse_args(argv)
    try:
        files = validate_archive(args.archive, args.expected_md5)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"validate_dagstuhl_choirset: {exc}", file=sys.stderr)
        return 1
    print(f"validate_dagstuhl_choirset: valid files={files} archive={args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
