#!/usr/bin/env python3
"""Safely extract official IRMAS testing archives outside the repository."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile


def safe_member(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    return not path.is_absolute() and ".." not in path.parts and not stat.S_ISLNK(info.external_attr >> 16)


def extract(archive_path: Path, output: Path) -> int:
    extracted = 0
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            if not safe_member(info):
                raise ValueError(f"{archive_path}: unsafe member {info.filename!r}")
            if info.is_dir():
                continue
            target = output / PurePosixPath(info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.stat().st_size == info.file_size:
                continue
            temporary = target.with_name(f".{target.name}.part")
            with archive.open(info) as source, temporary.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            temporary.replace(target)
            extracted += 1
    return extracted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    extracted = sum(extract(path, output) for path in args.archive)
    (output / ".irmas-extraction-complete").write_text("IRMAS testing archives extracted\n", encoding="utf-8")
    print(f"extract_irmas: extracted={extracted} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
