#!/usr/bin/env python3
"""Summarize the downloaded BabySlakh archive without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    return parser.parse_args()


def md5sum(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - compares the publisher's supplied checksum.
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    archive = args.archive
    if not archive.is_file():
        raise SystemExit(f"inspect_babyslakh_archive: missing archive: {archive}")

    suffixes = Counter()
    top_levels = Counter()
    regular_members = 0
    with tarfile.open(archive, "r:gz") as contents:
        for member in contents:
            if not member.isfile():
                continue
            regular_members += 1
            path = Path(member.name)
            suffixes[path.suffix.lower() or "<none>"] += 1
            if path.parts:
                top_levels[path.parts[0]] += 1

    audio_count = sum(suffixes[suffix] for suffix in (".flac", ".wav", ".mp3"))
    midi_count = sum(suffixes[suffix] for suffix in (".mid", ".midi"))
    print(f"archive={archive}")
    print(f"size_bytes={archive.stat().st_size}")
    print(f"md5={md5sum(archive)}")
    print(f"regular_members={regular_members}")
    print(f"audio_members={audio_count}")
    print(f"midi_members={midi_count}")
    print("top_levels=" + ",".join(f"{name}:{count}" for name, count in sorted(top_levels.items())))
    print("suffixes=" + ",".join(f"{name}:{count}" for name, count in sorted(suffixes.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
