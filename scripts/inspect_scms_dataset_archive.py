#!/usr/bin/env python3
"""Inventory the SCMS ZIP without extracting its large audio payload."""

from __future__ import annotations

import argparse
import collections
import zipfile
from pathlib import Path, PurePosixPath


def inspect(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
    roots: collections.Counter[str] = collections.Counter()
    extensions: collections.Counter[str] = collections.Counter()
    sizes: collections.Counter[str] = collections.Counter()
    for member in members:
        parts = PurePosixPath(member.filename).parts
        roots[parts[0] if parts else "--"] += 1
        suffix = Path(member.filename).suffix.lower() or "[none]"
        extensions[suffix] += 1
        sizes[suffix] += member.file_size
    return {
        "members": len(members),
        "roots": roots,
        "extensions": extensions,
        "sizes": sizes,
    }


def summary(path: Path) -> str:
    result = inspect(path)
    lines = [f"scms_archive: {path}", f"members: {result['members']}", "roots:"]
    lines.extend(f"  {key}: {count}" for key, count in sorted(result["roots"].items()))
    lines.append("extensions:")
    for key in sorted(result["extensions"]):
        lines.append(
            f"  {key}: {result['extensions'][key]} files {result['sizes'][key]} bytes"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(summary(args.archive), end="")
    except (OSError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
