#!/usr/bin/env python3
"""Summarize ZIP contents without extracting its payload."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import PurePosixPath
import zipfile


TEXT_SUFFIXES = {".csv", ".tsv", ".json", ".jams", ".txt", ".xml"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()

    with zipfile.ZipFile(args.archive) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        suffixes = Counter(PurePosixPath(member.filename).suffix.lower() or "[none]" for member in members)
        top_levels = Counter(PurePosixPath(member.filename).parts[0] for member in members if member.filename)
        annotations = [member for member in members if PurePosixPath(member.filename).suffix.lower() in TEXT_SUFFIXES]
        print(f"members={len(members)}")
        print(f"compressed_bytes={sum(member.compress_size for member in members)}")
        print(f"uncompressed_bytes={sum(member.file_size for member in members)}")
        print("top_levels=" + ", ".join(f"{name}:{count}" for name, count in sorted(top_levels.items())))
        print("suffixes=" + ", ".join(f"{name}:{count}" for name, count in sorted(suffixes.items())))
        for member in members[:40]:
            print(f"member={member.filename}")
        print(f"annotation_candidates={len(annotations)}")
        for member in annotations[:40]:
            print(f"annotation={member.filename}")
        for member in annotations[:5]:
            try:
                preview = archive.read(member, pwd=None)[:512].decode("utf-8", errors="replace")
            except OSError as exc:
                print(f"annotation_preview_error={member.filename}: {exc}")
                continue
            preview = " ".join(preview.splitlines()[:4])
            print(f"annotation_preview={member.filename}: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
