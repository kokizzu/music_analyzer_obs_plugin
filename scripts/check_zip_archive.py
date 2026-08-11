#!/usr/bin/env python3
"""Validate every member of a ZIP archive and fail on the first corrupt one."""

from __future__ import annotations

import pathlib
import sys
import zipfile


def main(argv: list[str]) -> int:
    list_members = False
    if len(argv) == 3 and argv[1] == "--list":
        list_members = True
        archive = pathlib.Path(argv[2])
    elif len(argv) == 2:
        archive = pathlib.Path(argv[1])
    else:
        print("usage: check_zip_archive.py [--list] ARCHIVE", file=sys.stderr)
        return 2

    try:
        with zipfile.ZipFile(archive) as contents:
            corrupted = contents.testzip()
            if list_members:
                members = [member for member in contents.infolist() if not member.is_dir()]
                suffixes: dict[str, int] = {}
                for member in members:
                    suffix = pathlib.PurePosixPath(member.filename).suffix.lower() or "[no suffix]"
                    suffixes[suffix] = suffixes.get(suffix, 0) + 1
                print(f"check_zip_archive: members={len(members)} archive={archive}")
                print(
                    "check_zip_archive: suffixes="
                    + " ".join(f"{suffix}:{count}" for suffix, count in sorted(suffixes.items()))
                )
                for member in members[:80]:
                    print(member.filename)
                if len(members) > 80:
                    print(f"... {len(members) - 80} more members")
    except (OSError, zipfile.BadZipFile) as error:
        print(f"check_zip_archive: {archive}: {error}", file=sys.stderr)
        return 1
    if corrupted:
        print(f"check_zip_archive: {archive}: corrupted member {corrupted}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
