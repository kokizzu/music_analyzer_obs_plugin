#!/usr/bin/env python3
"""Validate every member of a ZIP archive and fail on the first corrupt one."""

from __future__ import annotations

import pathlib
import sys
import zipfile


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_zip_archive.py ARCHIVE", file=sys.stderr)
        return 2

    archive = pathlib.Path(argv[1])
    try:
        with zipfile.ZipFile(archive) as contents:
            corrupted = contents.testzip()
    except (OSError, zipfile.BadZipFile) as error:
        print(f"check_zip_archive: {archive}: {error}", file=sys.stderr)
        return 1
    if corrupted:
        print(f"check_zip_archive: {archive}: corrupted member {corrupted}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
