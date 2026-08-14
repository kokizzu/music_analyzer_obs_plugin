#!/usr/bin/env python3
"""Print a compact, deterministic Choral Singing Dataset archive inventory."""

from __future__ import annotations

import argparse
import collections
import zipfile
from pathlib import PurePosixPath


def inventory(archive_path: str) -> tuple[list[str], collections.Counter[str], collections.Counter[str]]:
    with zipfile.ZipFile(archive_path) as archive:
        files = sorted(entry.filename for entry in archive.infolist() if not entry.is_dir())
    extensions = collections.Counter(
        PurePosixPath(name).suffix.lower().lstrip(".") or "(none)" for name in files
    )
    roots = collections.Counter(PurePosixPath(name).parts[0] for name in files)
    return files, roots, extensions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--contains", default="")
    parser.add_argument("--read", default="")
    args = parser.parse_args(argv)
    if args.read:
        with zipfile.ZipFile(args.archive) as archive:
            with archive.open(args.read) as source:
                print(source.read().decode("utf-8", errors="replace"))
        return 0
    files, roots, extensions = inventory(args.archive)
    print(f"inspect_choral_singing_dataset_archive: files={len(files)}")
    print("roots=" + ", ".join(f"{name}={count}" for name, count in sorted(roots.items())))
    print("extensions=" + ", ".join(f"{name}={count}" for name, count in sorted(extensions.items())))
    selected = [name for name in files if args.contains.lower() in name.lower()]
    for name in selected[: max(0, args.limit)]:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
